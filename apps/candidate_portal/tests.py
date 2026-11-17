from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import AdminUser, CandidateAccount, EmployerAccount
from apps.candidates.models import Applicant, Interview
from apps.jobs.models import Job
from apps.candidate_portal.models import ApplicationStatusHistory, CandidateSavedJob
from apps.candidates.status_helpers import set_applicant_status


class CandidatePortalTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create Admin
        self.admin = AdminUser.objects.create(
            email="admin@skyvision.com",
            is_active=True
        )
        self.admin.set_password("adminpass123")
        self.admin.save()

        # Create Employer
        self.emp = EmployerAccount.objects.create(
            company_name="Test Corp",
            contact_name="Test Employer",
            email="employer@test.com",
            phone="9876543219",
            status="APPROVED"
        )

        # Create Approved Candidate Account (Candidate A)
        self.cand_a = CandidateAccount.objects.create(
            email="cand_a@test.com",
            full_name="Candidate A",
            phone="9876543210",
            city="Lucknow",
            is_approved=True,
            approval_status="approved"
        )
        self.cand_a.set_password("candpass123")
        self.cand_a.save()

        # Create Candidate B (Approved)
        self.cand_b = CandidateAccount.objects.create(
            email="cand_b@test.com",
            full_name="Candidate B",
            phone="9876543211",
            city="Kanpur",
            is_approved=True,
            approval_status="approved"
        )
        self.cand_b.set_password("candpass123")
        self.cand_b.save()

        # Create Job
        self.job = Job.objects.create(
            employer=self.emp,
            title="Python Developer",
            location="Lucknow",
            employment_type="Full Time",
            status="LIVE"
        )

    def test_01_candidate_registration_pending_approval(self):
        """Test candidate registration creates pending account."""
        resp = self.client.post('/api/candidate/register/', {
            "full_name": "New Registrant",
            "email": "newreg@test.com",
            "phone": "9988776655",
            "password": "password123",
            "confirm_password": "password123",
            "city": "Lucknow"
        })
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data["status"], "success")

        cand = CandidateAccount.objects.get(email="newreg@test.com")
        self.assertFalse(cand.is_approved)
        self.assertEqual(cand.approval_status, "pending")

    def test_02_login_blocking_pending_or_rejected(self):
        """Test login is blocked if account is pending or rejected."""
        # 1. Pending account
        pending_cand = CandidateAccount.objects.create(
            email="pending@test.com",
            full_name="Pending Candidate",
            phone="9123456789",
            is_approved=False,
            approval_status="pending"
        )
        pending_cand.set_password("password123")
        pending_cand.save()

        resp = self.client.post('/api/candidate/login/', {
            "email": "pending@test.com",
            "password": "password123"
        })
        self.assertEqual(resp.status_code, 403)

        # 2. Rejected account
        rejected_cand = CandidateAccount.objects.create(
            email="rejected@test.com",
            full_name="Rejected Candidate",
            phone="9123456788",
            is_approved=False,
            approval_status="rejected",
            rejection_reason="Invalid credentials document"
        )
        rejected_cand.set_password("password123")
        rejected_cand.save()

        resp = self.client.post('/api/candidate/login/', {
            "email": "rejected@test.com",
            "password": "password123"
        })
        self.assertEqual(resp.status_code, 403)
        self.assertIn("rejected", resp.json()["message"].lower())

    def test_03_login_success_approved(self):
        """Test approved candidate can login successfully."""
        resp = self.client.post('/api/candidate/login/', {
            "email": "cand_a@test.com",
            "password": "candpass123"
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "success")
        self.assertEqual(self.client.session.get("candidate_id"), self.cand_a.id)

    def test_04_admin_approval_and_rejection(self):
        """Test admin approval and rejection endpoints."""
        # Login as Admin
        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()

        new_cand = CandidateAccount.objects.create(
            email="to_approve@test.com",
            full_name="To Approve",
            phone="9000000001",
            is_approved=False,
            approval_status="pending"
        )

        # Admin approves
        resp = self.client.post(f'/api/admin/candidate-registrations/{new_cand.id}/approve/')
        self.assertEqual(resp.status_code, 200)
        new_cand.refresh_from_db()
        self.assertTrue(new_cand.is_approved)
        self.assertEqual(new_cand.approval_status, "approved")

        from django.core import mail
        self.assertGreaterEqual(len(mail.outbox), 1)
        approval_email = mail.outbox[-1]
        self.assertIn(new_cand.email, approval_email.to)
        self.assertIn("Registration Approved", approval_email.subject)
        self.assertIn("/candidate/login/", approval_email.body)

        # Calling approve a second time should NOT send a duplicate email
        outbox_len_before = len(mail.outbox)
        resp_dup = self.client.post(f'/api/admin/candidate-registrations/{new_cand.id}/approve/')
        self.assertEqual(resp_dup.status_code, 200)
        self.assertIn("already approved", resp_dup.json()["message"])
        self.assertEqual(len(mail.outbox), outbox_len_before)

        # Admin rejects
        resp = self.client.post(f'/api/admin/candidate-registrations/{new_cand.id}/reject/', {
            "reason": "Test rejection"
        }, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        new_cand.refresh_from_db()
        self.assertFalse(new_cand.is_approved)
        self.assertEqual(new_cand.approval_status, "rejected")

    def test_05_job_apply_requires_login_and_auto_prefill(self):
        """Test applying for jobs requires login, auto pre-fills data, and sets Application Received status."""
        # 1. Unauthenticated guest apply fails
        resp = self.client.post('/api/apply/', {
            "job_id": self.job.id,
            "job_title": self.job.title
        })
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json()["status"], "login_required")

        # 2. Login as Candidate A
        session = self.client.session
        session['candidate_id'] = self.cand_a.id
        session.save()

        # Apply as Candidate A
        resp = self.client.post('/api/apply/', {
            "job_id": self.job.id,
            "job_title": self.job.title
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "success")

        app = Applicant.objects.get(candidate_account=self.cand_a, job=self.job)
        self.assertEqual(app.full_name, self.cand_a.full_name)
        self.assertEqual(app.email, self.cand_a.email)
        self.assertIn(app.status, ["Application Submitted", "Application Received"])

        # Status History recorded
        history = ApplicationStatusHistory.objects.filter(applicant=app)
        self.assertTrue(history.exists())

        # 3. Duplicate application blocked
        resp_dup = self.client.post('/api/apply/', {
            "job_id": self.job.id,
            "job_title": self.job.title
        })
        self.assertEqual(resp_dup.status_code, 400)
        self.assertIn("already applied", resp_dup.json()["message"].lower())

    def test_06_idor_protection(self):
        """Test candidate A cannot view Candidate B's applications or interviews."""
        # Create application for Candidate B
        app_b = Applicant.objects.create(
            candidate_account=self.cand_b,
            job=self.job,
            full_name=self.cand_b.full_name,
            email=self.cand_b.email,
            phone=self.cand_b.phone,
            job_title=self.job.title,
            status="Application Received"
        )

        # Login as Candidate A
        session = self.client.session
        session['candidate_id'] = self.cand_a.id
        session.save()

        resp = self.client.get('/api/candidate/applied-jobs/')
        self.assertEqual(resp.status_code, 200)
        apps_data = resp.json()["applications"]

        # Ensure Candidate A does NOT see Candidate B's application
        app_ids_returned = [item["application"]["id"] for item in apps_data]
        self.assertNotIn(app_b.id, app_ids_returned)

    def test_07_newly_registered_candidate_sees_zero_applications(self):
        """Verify newly registered candidate dashboard starts with 0 applied jobs and cannot see other candidates' applications even with same contact info."""
        # Pre-existing application belonging to Candidate B
        app_old = Applicant.objects.create(
            candidate_account=self.cand_b,
            job=self.job,
            full_name="Old Applicant",
            email="shared_email@test.com",
            phone="9998887776",
            job_title="Senior Developer",
            status="Joined"
        )

        # Register fresh Candidate C
        cand_c = CandidateAccount.objects.create(
            email="shared_email@test.com",
            full_name="New Candidate C",
            phone="9998887776",
            is_approved=True,
            approval_status="approved"
        )

        # Login as Candidate C
        session = self.client.session
        session['candidate_id'] = cand_c.id
        session.save()

        # Check dashboard stats: must be 0
        resp_stats = self.client.get('/api/candidate/dashboard-stats/')
        self.assertEqual(resp_stats.status_code, 200)
        data = resp_stats.json()
        self.assertEqual(data["stats"]["applied_jobs"], 0)
        self.assertEqual(data["stats"]["interviews"], 0)
        self.assertEqual(data["stats"]["offers"], 0)
        self.assertEqual(len(data["recent_applications"]), 0)

        # Check applied jobs list: must be empty
        resp_apps = self.client.get('/api/candidate/applied-jobs/')
        self.assertEqual(resp_apps.status_code, 200)
        self.assertEqual(len(resp_apps.json()["applications"]), 0)

        # Candidate C applies for job
        resp_apply = self.client.post('/api/apply/', {
            "job_id": self.job.id,
            "job_title": self.job.title
        })
        self.assertEqual(resp_apply.status_code, 200)

        # Now dashboard stats should reflect exactly 1 application
        resp_stats2 = self.client.get('/api/candidate/dashboard-stats/')
        data2 = resp_stats2.json()
        self.assertEqual(data2["stats"]["applied_jobs"], 1)
        self.assertEqual(len(data2["recent_applications"]), 1)
        self.assertEqual(data2["recent_applications"][0]["job_title"], self.job.title)

