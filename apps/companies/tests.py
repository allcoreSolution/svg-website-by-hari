import json
from datetime import datetime, timedelta
from django.test import TestCase, Client
from django.core.management import call_command
from django.contrib.sessions.backends.db import SessionStore

from apps.companies.models import CompanyEnquiry, Company, CompanyContact, CompanyRequirement
from apps.jobs.models import Job
from apps.accounts.models import AdminUser


class CompaniesModuleTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = AdminUser.objects.create(email="admin@test.com", password_hash="dummy", is_active=True)
        session = self.client.session
        session['admin_id'] = self.admin.id
        session['admin_username'] = 'admin'
        session.save()

    # -------------------------------------------------------------
    # 1. PUBLIC ENQUIRY SECURITY & HARDENING TESTS
    # -------------------------------------------------------------
    def test_create_company_enquiry_public_hardening(self):
        payload = {
            "recruiter_name": "John Doe",
            "company_name": "Test Global Tech",
            "phone": "9876543210",
            "email": "hr@testglobaltech.com",
            "job_title": "Software Engineer",
            "vacancies": "5",
            "status": "Approved", # Attempting status injection
            "notes": "Malicious internal note" # Attempting notes injection
        }
        res = self.client.post('/api/company-enquiry', json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        
        enquiry = CompanyEnquiry.objects.get(email="hr@testglobaltech.com")
        self.assertEqual(enquiry.status, "New") # Must force New status
        self.assertEqual(enquiry.notes, "") # Must force empty notes

    def test_create_company_enquiry_honeypot(self):
        payload = {
            "recruiter_name": "Spammer",
            "company_name": "Spam Corp",
            "phone": "9876543210",
            "email": "spam@spam.com",
            "website_url": "http://spam-link.com" # Honeypot field filled
        }
        res = self.client.post('/api/company-enquiry', json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertFalse(CompanyEnquiry.objects.filter(company_name="Spam Corp").exists())

    def test_create_company_enquiry_validation_failure(self):
        # Invalid email
        res = self.client.post('/api/company-enquiry', json.dumps({
            "recruiter_name": "John", "company_name": "Acme", "phone": "9876543210", "email": "invalid-email"
        }), content_type='application/json')
        self.assertEqual(res.status_code, 400)

        # Invalid phone
        res = self.client.post('/api/company-enquiry', json.dumps({
            "recruiter_name": "John", "company_name": "Acme", "phone": "123", "email": "john@acme.com"
        }), content_type='application/json')
        self.assertEqual(res.status_code, 400)

    # -------------------------------------------------------------
    # 2. MANAGEMENT COMMAND TESTS
    # -------------------------------------------------------------
    def test_scrub_job_recruiter_names_command(self):
        job = Job.objects.create(
            title="Senior Developer",
            category="Acme Corp (John Recruiter)",
            description="Recruiter: John Recruiter. Hiring for senior dev.",
            status="Active"
        )
        call_command('scrub_job_recruiter_names')
        job.refresh_from_db()
        self.assertNotIn("John Recruiter", job.category)
        self.assertNotIn("Recruiter: John Recruiter", job.description)

    def test_expire_requirements_command(self):
        comp = Company.objects.create(name="Tech Corp", email="info@tech.com", phone="9876543210")
        past_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        req = CompanyRequirement.objects.create(
            company=comp, title="Expired Role", deadline=past_date, status="Active"
        )
        call_command('expire_requirements')
        req.refresh_from_db()
        self.assertEqual(req.status, "Expired")

    # -------------------------------------------------------------
    # 3. ADMIN APIS CRUD & WORKFLOW TESTS
    # -------------------------------------------------------------
    def test_admin_companies_crud(self):
        # Create company
        res = self.client.post('/api/companies/', json.dumps({
            "name": "Nova Systems",
            "email": "hr@novasystems.com",
            "phone": "9876543210",
            "industry": "IT Services",
            "city": "Lucknow"
        }), content_type='application/json')
        self.assertEqual(res.status_code, 201)
        comp_id = res.json()['company']['id']

        # Get companies list
        res = self.client.get('/api/companies/')
        self.assertEqual(res.status_code, 200)

        # Update company
        res = self.client.put(f'/api/companies/{comp_id}/', json.dumps({"industry": "Cloud Computing"}), content_type='application/json')
        self.assertEqual(res.status_code, 200)

        # Delete company
        res = self.client.delete(f'/api/companies/{comp_id}/')
        self.assertEqual(res.status_code, 200)

    def test_company_enquiry_conversion_workflow(self):
        enquiry = CompanyEnquiry.objects.create(
            recruiter_name="Sarah Connor",
            company_name="Cyberdyne Systems",
            phone="9876543210",
            email="sarah@cyberdyne.com",
            job_title="AI Research Engineer",
            status="New"
        )

        # Approve and auto-publish
        res = self.client.post(f'/api/company-enquiry/{enquiry.id}/approve-publish/')
        self.assertEqual(res.status_code, 200)
        enquiry.refresh_from_db()
        self.assertEqual(enquiry.status, "Approved")
        self.assertTrue(Job.objects.filter(title="AI Research Engineer").exists())

    # -------------------------------------------------------------
    # 4. ADMIN DASHBOARD SECTION URLS (200 OK CHECKS)
    # -------------------------------------------------------------
    def test_all_companies_section_urls(self):
        urls = [
            '/admin-panel/companies/all/',
            '/admin-panel/companies/add/',
            '/admin-panel/companies/enquiries/',
            '/admin-panel/companies/requirements/all/',
            '/admin-panel/companies/requirements/active/',
            '/admin-panel/companies/requirements/closed/',
            '/admin-panel/companies/requirements/expired/',
            '/admin-panel/companies/job-openings/',
            '/admin-panel/companies/contacts/'
        ]
        for url in urls:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200, f"URL {url} returned status code {res.status_code}")
