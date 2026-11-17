import json
from django.test import TestCase, Client
from apps.accounts.models import AdminUser, CandidateAccount, EmployerAccount
from apps.jobs.models import Job

class RegistrationApprovalModuleTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = AdminUser.objects.create(email="admin_reg@test.com", password_hash="hash")
        
        # Log in admin
        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()

        # Create sample candidates
        self.cand_pending = CandidateAccount.objects.create(
            email="cand_pending@test.com",
            full_name="Pending Candidate",
            phone="9998887771",
            is_approved=False,
            approval_status="pending"
        )
        self.cand_approved = CandidateAccount.objects.create(
            email="cand_app@test.com",
            full_name="Approved Candidate",
            phone="9998887772",
            is_approved=True,
            approval_status="approved"
        )

        # Create sample employers
        self.emp_pending = EmployerAccount.objects.create(
            company_name="Pending Corp",
            contact_name="HR Lead",
            email="emp_pending@test.com",
            phone="9998887773",
            status="PENDING"
        )
        self.emp_approved = EmployerAccount.objects.create(
            company_name="Approved Corp",
            contact_name="CEO",
            email="emp_app@test.com",
            phone="9998887774",
            status="APPROVED"
        )

    def test_registration_module_views(self):
        """Test HTML module views for Registration & Approval."""
        resp = self.client.get('/admin-panel/registrations/')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/admin-panel/registrations/candidates/')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/admin-panel/registrations/employers/')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/admin-panel/registrations/rejected/')
        self.assertEqual(resp.status_code, 200)

    def test_api_admin_registrations_summary(self):
        """Test summary counts endpoint."""
        resp = self.client.get('/api/admin/registrations/summary/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['status'], 'success')
        counts = data['counts']
        self.assertEqual(counts['total'], 4)
        self.assertEqual(counts['pending'], 2)
        self.assertEqual(counts['approved'], 2)

    def test_api_admin_registrations_list(self):
        """Test unified registrations JSON list endpoint with filters."""
        resp = self.client.get('/api/admin/registrations/?type=all&status=pending')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['total_count'], 2)

        resp = self.client.get('/api/admin/registrations/?type=candidate')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['total_count'], 2)

    def test_bulk_registrations_action(self):
        """Test bulk approve/reject for candidates and employers."""
        payload = {
            "action": "approve",
            "items": [
                {"type": "candidate", "id": self.cand_pending.id},
                {"type": "employer", "id": self.emp_pending.id}
            ]
        }
        resp = self.client.post(
            '/api/admin/registrations/bulk-action/',
            json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['count'], 2)

        self.cand_pending.refresh_from_db()
        self.assertEqual(self.cand_pending.approval_status, 'approved')
        self.assertTrue(self.cand_pending.is_approved)

        self.emp_pending.refresh_from_db()
        self.assertEqual(self.emp_pending.status, 'APPROVED')

    def test_candidate_gate_unapproved_cannot_apply(self):
        """Test that an unapproved candidate cannot apply for jobs."""
        job = Job.objects.create(title="Backend Dev", employer=self.emp_approved, status="Active")
        cand_client = Client()
        session = cand_client.session
        session['candidate_id'] = self.cand_pending.id
        session.save()

        resp = cand_client.post('/api/apply', {'job_id': job.id, 'job_title': job.title})
        self.assertEqual(resp.status_code, 403)
        self.assertIn("pending admin approval", resp.json()['message'])

    def test_employer_gate_unapproved_locked(self):
        """Test that an unapproved employer cannot access employer pages."""
        emp_client = Client()
        session = emp_client.session
        session['employer_id'] = self.emp_pending.id
        session.save()

        resp = emp_client.get('/employer/dashboard/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/employer/pending/', resp.url)
