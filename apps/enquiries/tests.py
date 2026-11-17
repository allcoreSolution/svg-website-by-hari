import json
import csv
import io
from django.test import TestCase, Client
from django.conf import settings
from apps.accounts.models import AdminUser
from apps.enquiries.models import ContactEnquiry, EnquiryRead, SubmissionThrottle, FollowUp, ActivityLog
from apps.companies.models import CompanyEnquiry
from apps.internships.models import InternshipEnquiry
from apps.enquiries.constants import bucket_of, classify_enquiry_type, BUSINESS_SERVICES, CANDIDATE_SERVICES

class EnquiriesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Create an admin user and log in session
        self.admin = AdminUser.objects.create(
            email="admin@test.com",
            password_hash="pbkdf2_sha256$hashed",
            is_active=True
        )
        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()

    # ==========================================
    # 1. PUBLIC CONTACT FORM TESTS
    # ==========================================
    def test_public_contact_success(self):
        response = self.client.post(
            '/api/contact/',
            data=json.dumps({
                "name": "Test User",
                "email": "testuser@example.com",
                "phone": "9876543210",
                "service": "Recruitment",
                "message": "We need help with recruitment."
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(ContactEnquiry.objects.filter(email="testuser@example.com").exists())

    def test_public_contact_validation_errors(self):
        # Invalid email
        res1 = self.client.post('/api/contact/', data=json.dumps({
            "name": "User", "email": "bademail", "phone": "9876543210"
        }), content_type='application/json')
        self.assertEqual(res1.status_code, 400)

        # Invalid phone
        res2 = self.client.post('/api/contact/', data=json.dumps({
            "name": "User", "email": "user@example.com", "phone": "123"
        }), content_type='application/json')
        self.assertEqual(res2.status_code, 400)

    def test_public_contact_honeypot(self):
        res = self.client.post('/api/contact/', data=json.dumps({
            "name": "Spam Bot",
            "email": "bot@spam.com",
            "phone": "9876543210",
            "website_url": "http://spam.com"
        }), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        # Should NOT create ContactEnquiry record in DB
        self.assertFalse(ContactEnquiry.objects.filter(email="bot@spam.com").exists())

    def test_public_contact_payload_size_limit(self):
        large_message = "A" * 25000  # > 20KB
        res = self.client.post('/api/contact/', data=json.dumps({
            "name": "User",
            "email": "user@example.com",
            "phone": "9876543210",
            "message": large_message
        }), content_type='application/json')
        self.assertEqual(res.status_code, 413)

    def test_public_contact_duplicate_guard(self):
        payload = {
            "name": "Dup User",
            "email": "dup@example.com",
            "phone": "9876543210",
            "message": "Exact duplicate message text"
        }
        res1 = self.client.post('/api/contact/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res1.status_code, 200)

        res2 = self.client.post('/api/contact/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res2.status_code, 400)
        self.assertIn("Duplicate", res2.json()["message"])

    def test_public_contact_spam_heuristics(self):
        payload = {
            "name": "Crypto Investor",
            "email": "crypto@spam.com",
            "phone": "9876543210",
            "service": "General Inquiry",
            "message": "Check out this bitcoin investment opportunity!"
        }
        res = self.client.post('/api/contact/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        obj = ContactEnquiry.objects.get(email="crypto@spam.com")
        self.assertEqual(obj.status, "Spam")

    # ==========================================
    # 2. CLASSIFICATION ENGINE & BUCKETS
    # ==========================================
    def test_classification_engine(self):
        self.assertEqual(classify_enquiry_type("Recruitment"), "General")
        self.assertEqual(classify_enquiry_type("Manpower Supply"), "General")
        self.assertEqual(classify_enquiry_type("Job Application"), "Candidate")
        self.assertEqual(classify_enquiry_type("Internship"), "General")
        self.assertEqual(classify_enquiry_type("Other", "I am looking for a job position"), "Candidate")
        self.assertEqual(classify_enquiry_type("Other", "We want to hire staff for our office"), "General")

    def test_status_buckets(self):
        self.assertEqual(bucket_of("contact", "New"), "open")
        self.assertEqual(bucket_of("contact", "Pending"), "open")
        self.assertEqual(bucket_of("contact", "Contacted"), "in_progress")
        self.assertEqual(bucket_of("contact", "Under Review"), "in_progress")
        self.assertEqual(bucket_of("contact", "Resolved"), "resolved")
        self.assertEqual(bucket_of("company", "Approved"), "resolved")
        self.assertEqual(bucket_of("internship", "Converted"), "resolved")
        self.assertEqual(bucket_of("contact", "Spam"), "closed")
        self.assertEqual(bucket_of("contact", "Rejected"), "closed")

    # ==========================================
    # 3. ADMIN REST API TESTS
    # ==========================================
    def test_unified_enquiries_list_api(self):
        # Create test records
        ContactEnquiry.objects.create(name="Gen 1", email="g1@test.com", phone="999", service="Recruitment", enquiry_type="General")
        ContactEnquiry.objects.create(name="Cand 1", email="c1@test.com", phone="888", service="Job Application", enquiry_type="Candidate")
        CompanyEnquiry.objects.create(recruiter_name="Rec 1", company_name="Comp 1", email="comp@test.com", phone="777")
        InternshipEnquiry.objects.create(full_name="Intern 1", email="int@test.com", phone="666", course_stream="CS")

        res = self.client.get('/api/enquiries')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["count"], 4)

        # Test filtering by type=candidate
        res_cand = self.client.get('/api/enquiries?type=candidate')
        self.assertEqual(res_cand.json()["count"], 1)

    def test_mark_read_and_unread(self):
        c = ContactEnquiry.objects.create(name="Read Test", email="read@test.com", phone="999")
        
        # Mark read
        res_read = self.client.post('/api/enquiry/mark-read', data=json.dumps({"type": "contact", "id": c.id}), content_type='application/json')
        self.assertEqual(res_read.status_code, 200)
        self.assertTrue(EnquiryRead.objects.filter(enquiry_type="contact", enquiry_id=c.id).exists())

        # Mark unread
        res_unread = self.client.post('/api/enquiry/mark-unread', data=json.dumps({"type": "contact", "id": c.id}), content_type='application/json')
        self.assertEqual(res_unread.status_code, 200)
        self.assertFalse(EnquiryRead.objects.filter(enquiry_type="contact", enquiry_id=c.id).exists())

    def test_bulk_status_update(self):
        c1 = ContactEnquiry.objects.create(name="C1", email="c1@t.com", phone="111")
        c2 = ContactEnquiry.objects.create(name="C2", email="c2@t.com", phone="222")

        res = self.client.post('/api/enquiry/bulk-status', data=json.dumps({
            "items": [{"type": "contact", "id": c1.id}, {"type": "contact", "id": c2.id}],
            "status": "Resolved"
        }), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        c1.refresh_from_db()
        c2.refresh_from_db()
        self.assertEqual(c1.status, "Resolved")
        self.assertEqual(c2.status, "Resolved")

    def test_mark_spam_and_restore(self):
        c = ContactEnquiry.objects.create(name="Spam Test", email="sp@t.com", phone="333")

        res_spam = self.client.post('/api/enquiry/mark-spam', data=json.dumps({"type": "contact", "id": c.id}), content_type='application/json')
        self.assertEqual(res_spam.status_code, 200)
        c.refresh_from_db()
        self.assertEqual(c.status, "Spam")

        res_restore = self.client.post('/api/enquiry/restore', data=json.dumps({"type": "contact", "id": c.id}), content_type='application/json')
        self.assertEqual(res_restore.status_code, 200)
        c.refresh_from_db()
        self.assertEqual(c.status, "New")

    def test_counts_api(self):
        ContactEnquiry.objects.create(name="C", email="c@t.com", phone="1", enquiry_type="General")
        CompanyEnquiry.objects.create(recruiter_name="R", company_name="Co", email="co@t.com", phone="2")

        res = self.client.get('/api/enquiry/counts')
        self.assertEqual(res.status_code, 200)
        metrics = res.json()["metrics"]
        self.assertEqual(metrics["total"], 2)

    def test_csv_export_sanitization(self):
        ContactEnquiry.objects.create(
            name="=DDE('cmd';'calc')",  # Formula injection payload
            email="formula@test.com",
            phone="9999999999",
            service="Recruitment"
        )
        res = self.client.get('/api/enquiry/export.csv')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'text/csv')
        content = res.content.decode('utf-8')
        # Check formula is neutralized with leading quote `'=`
        self.assertIn("'=DDE('cmd';'calc')", content)

    # ==========================================
    # 4. SIGNAL CLEANUP TESTS
    # ==========================================
    def test_signal_cleanup_on_delete(self):
        c = ContactEnquiry.objects.create(name="Delete Test", email="del@test.com", phone="111")
        EnquiryRead.objects.create(enquiry_type="contact", enquiry_id=c.id, read_by="admin")
        self.assertTrue(EnquiryRead.objects.filter(enquiry_type="contact", enquiry_id=c.id).exists())

        c.delete()
        self.assertFalse(EnquiryRead.objects.filter(enquiry_type="contact", enquiry_id=c.id).exists())

    # ==========================================
    # 5. DASHBOARD SECTIONS 200 OK TESTS
    # ==========================================
    def test_dashboard_enquiries_sections(self):
        sections = [
            'all', 'general', 'candidate', 'company',
            'internship', 'unread', 'resolved'
        ]
        for sec in sections:
            res = self.client.get(f'/admin-panel/enquiries/{sec}/')
            self.assertEqual(res.status_code, 200, f"Failed for section {sec}")
