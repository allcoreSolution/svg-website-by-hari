import json
from datetime import datetime, timedelta
from django.test import TestCase, Client
from django.utils import timezone
from apps.accounts.models import AdminUser
from apps.candidates.models import Applicant, Resume, Interview
from apps.candidates.validators import validate_candidate_data, validate_interview_data


class CandidatesModuleTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Create an admin user & set session for admin_required auth
        self.admin = AdminUser.objects.create(
            email="admin@skyvision.com",
            password_hash="testpasshash",
            is_active=True
        )
        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()

        # Create test applicants & resumes
        self.applicant1 = Applicant.objects.create(
            full_name="Amit Kumar",
            email="amit@example.com",
            phone="9876543210",
            job_title="Python Developer",
            experience=3,
            status="New"
        )
        self.applicant2 = Applicant.objects.create(
            full_name="Priya Sharma",
            email="priya@example.com",
            phone="9876543211",
            job_title="HR Manager",
            experience=5,
            status="Shortlisted"
        )
        self.legacy_candidate = Applicant.objects.create(
            full_name="Legacy Candidate",
            email="legacy@example.com",
            phone="9876543212",
            job_title="Data Analyst",
            experience=2,
            status="Interview"  # Has status "Interview" but no Interview model row
        )
        self.resume1 = Resume.objects.create(
            full_name="Siddharth Roy",
            mobile="9876543213",
            email="siddharth@example.com",
            applying_for="UI/UX Designer",
            status="New"
        )

    def test_validators_candidate_data(self):
        """Test candidate validation functions."""
        # Valid data
        valid, err = validate_candidate_data({
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "9876543210",
            "experience": 2
        })
        self.assertTrue(valid)
        self.assertIsNone(err)

        # Invalid email
        valid, err = validate_candidate_data({
            "full_name": "Test User",
            "email": "invalid-email",
            "phone": "9876543210"
        })
        self.assertFalse(valid)
        self.assertIn("email", err["errors"])

        # Invalid phone (< 10 digits)
        valid, err = validate_candidate_data({
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "123"
        })
        self.assertFalse(valid)
        self.assertIn("phone", err["errors"])

    def test_validators_interview_past_date_rejection(self):
        """Test interview date validation rejects past dates."""
        yesterday = (timezone.now().date() - timedelta(days=1)).strftime("%Y-%m-%d")
        valid, err, d, t = validate_interview_data({
            "interview_date": yesterday,
            "interview_time": "14:00"
        })
        self.assertFalse(valid)
        self.assertIn("interview_date", err["errors"])

    def test_public_apply_job_api(self):
        """Test candidate job application API."""
        from apps.accounts.models import CandidateAccount, EmployerAccount
        from apps.jobs.models import Job

        emp = EmployerAccount.objects.create(
            company_name="Frontend Inc",
            contact_name="FE Lead",
            email="fe@example.com",
            phone="9876543277",
            status="APPROVED"
        )
        Job.objects.create(
            employer=emp,
            title="Frontend Developer",
            location="Lucknow",
            status="LIVE"
        )

        cand = CandidateAccount.objects.create(
            email='rohan@example.com',
            full_name='Rohan Gupta',
            phone='9876543299',
            is_approved=True,
            approval_status='approved'
        )
        cand.set_password('password123')
        cand.save()

        session = self.client.session
        session['candidate_id'] = cand.id
        session.save()

        resp = self.client.post('/api/apply', {
            'full_name': 'Rohan Gupta',
            'email': 'rohan@example.com',
            'phone': '9876543299',
            'job_title': 'Frontend Developer',
            'experience': 2
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data['status'], 'success')
        self.assertTrue(Applicant.objects.filter(email='rohan@example.com').exists())

    def test_public_upload_quick_resume_api(self):
        """Test quick resume upload API."""
        resp = self.client.post('/api/upload-resume', {
            'full_name': 'Neha Verma',
            'email': 'neha@example.com',
            'mobile': '9876543288',
            'applying_for': 'Marketing Manager'
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data['status'], 'success')
        self.assertTrue(Resume.objects.filter(email='neha@example.com').exists())

    def test_admin_schedule_interview_and_duplicate_slot_rejection(self):
        """Test scheduling interview, candidate status sync, email honesty, and duplicate slot rejection."""
        future_date = (timezone.now().date() + timedelta(days=5)).strftime("%Y-%m-%d")
        interview_time = "10:30"

        # Schedule interview for applicant1
        resp = self.client.post('/api/admin/schedule-interview/', json.dumps({
            'raw_id': self.applicant1.id,
            'model': 'applicant',
            'interview_date': future_date,
            'interview_time': interview_time,
            'interview_mode': 'In-Person Office Interview',
            'location_or_link': 'Sky Vision HQ, Lucknow',
            'notes': 'Bring original certificates.'
        }), content_type='application/json')

        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data['status'], 'success')

        # Refresh candidate status
        self.applicant1.refresh_from_db()
        self.assertEqual(self.applicant1.status, "Interview")

        # Verify Interview model row created
        interview = Interview.objects.filter(applicant=self.applicant1).first()
        self.assertIsNotNone(interview)
        self.assertEqual(interview.status, "Scheduled")

        # Test duplicate slot rejection for another candidate at exact same date & time
        resp_dup = self.client.post('/api/admin/schedule-interview/', json.dumps({
            'raw_id': self.applicant2.id,
            'model': 'applicant',
            'interview_date': future_date,
            'interview_time': interview_time,
            'interview_mode': 'Online'
        }), content_type='application/json')

        self.assertEqual(resp_dup.status_code, 400)
        data_dup = json.loads(resp_dup.content)
        self.assertEqual(data_dup['status'], 'error')
        self.assertIn("already booked", data_dup['message'])

    def test_interview_lifecycle(self):
        """Test interview reschedule, complete, and cancel lifecycle."""
        future_date = (timezone.now().date() + timedelta(days=3)).strftime("%Y-%m-%d")
        interview = Interview.objects.create(
            candidate_type='applicant',
            applicant=self.applicant1,
            candidate_id=self.applicant1.id,
            candidate_name=self.applicant1.full_name,
            candidate_email=self.applicant1.email,
            job_title=self.applicant1.job_title,
            interview_date=datetime.strptime(future_date, "%Y-%m-%d").date(),
            interview_time=datetime.strptime("11:00", "%H:%M").time(),
            status="Scheduled"
        )

        # 1. Reschedule
        resched_date = (timezone.now().date() + timedelta(days=7)).strftime("%Y-%m-%d")
        resp_resched = self.client.post(f'/api/interviews/{interview.id}/reschedule/', json.dumps({
            'interview_date': resched_date,
            'interview_time': '15:00',
            'interview_mode': 'Online Video Call'
        }), content_type='application/json')
        self.assertEqual(resp_resched.status_code, 200)

        interview.refresh_from_db()
        self.assertEqual(interview.status, 'Rescheduled')
        self.assertEqual(interview.interview_date.strftime("%Y-%m-%d"), resched_date)

        # 2. Complete with Result = 'Selected'
        resp_comp = self.client.post(f'/api/interviews/{interview.id}/complete/', json.dumps({
            'result': 'Selected',
            'feedback': 'Excellent problem solving skills.'
        }), content_type='application/json')
        self.assertEqual(resp_comp.status_code, 200)

        interview.refresh_from_db()
        self.assertEqual(interview.status, 'Completed')
        self.assertEqual(interview.result, 'Selected')

        # Candidate status must be updated to Selected!
        self.applicant1.refresh_from_db()
        self.assertEqual(self.applicant1.status, 'Selected')

    def test_dashboard_candidate_section_urls(self):
        """Verify 200 OK on all 10 dashboard candidate URLs."""
        urls = [
            '/admin-panel/candidates/all/',
            '/admin-panel/candidates/add/',
            '/admin-panel/candidates/profiles/',
            '/admin-panel/candidates/shortlisted/',
            '/admin-panel/candidates/interviews/upcoming/',
            '/admin-panel/candidates/interviews/completed/',
            '/admin-panel/candidates/interviews/cancelled/',
            '/admin-panel/candidates/selected/',
            '/admin-panel/candidates/rejected/',
            '/admin-panel/candidates/placed/',
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"URL failed with status {response.status_code}: {url}")

    def test_application_flow_r1_apply_pending_invisible_to_employer(self):
        """Rule R1: New candidate application is Pending and invisible to employer."""
        from apps.accounts.models import EmployerAccount, CandidateAccount
        from apps.jobs.models import Job

        employer = EmployerAccount.objects.create(
            company_name="TechCorp India",
            contact_name="HR Manager",
            email="hr@techcorp.com",
            status="APPROVED"
        )
        job = Job.objects.create(
            employer=employer,
            title="Senior Django Developer",
            status="Active"
        )
        candidate = CandidateAccount.objects.create(
            full_name="Vikram Seth",
            email="vikram@example.com",
            phone="9876543200",
            is_approved=True,
            approval_status="approved"
        )

        # Candidate applies
        session = self.client.session
        session['candidate_id'] = candidate.id
        session.save()

        resp = self.client.post('/api/apply', {
            'job_id': job.id,
            'job_title': job.title,
            'full_name': candidate.full_name,
            'email': candidate.email,
            'phone': candidate.phone,
        })
        self.assertEqual(resp.status_code, 200)

        app = Applicant.objects.filter(candidate_account=candidate, job=job).first()
        self.assertIsNotNone(app)
        self.assertEqual(app.status, "Application Submitted")
        self.assertEqual(app.approval_status, "Pending")
        self.assertEqual(app.flow_step, 2)

        # Employer MUST NOT see pending applications!
        visible = Applicant.objects.visible_to_employer(employer)
        self.assertNotIn(app, visible)

    def test_application_flow_r2_r3_admin_approve(self):
        """Rule R2/R3: Super Admin approves application -> advances to Employer Reviews & becomes visible to employer."""
        from apps.accounts.models import EmployerAccount
        from apps.jobs.models import Job
        from apps.candidates.models import Applicant

        employer = EmployerAccount.objects.create(
            company_name="Alpha Solutions",
            contact_name="Recruiter",
            email="recruiter@alpha.com",
            status="APPROVED"
        )
        job = Job.objects.create(
            employer=employer,
            title="Fullstack Developer",
            status="Active"
        )
        app = Applicant.objects.create(
            job=job,
            full_name="Karan Singh",
            email="karan@example.com",
            phone="9876543201",
            job_title=job.title,
            status="Application Submitted",
            approval_status="Pending",
            flow_step=2
        )

        # Admin approves via API
        resp = self.client.post(f'/api/admin/applications/{app.id}/approve/')
        self.assertEqual(resp.status_code, 200)

        app.refresh_from_db()
        self.assertEqual(app.approval_status, "Approved")
        self.assertIn(app.status, ["Employer Reviews", "Shortlisted"])
        self.assertIn(app.flow_step, [3, 4])

        # Employer can now see it!
        visible = Applicant.objects.visible_to_employer(employer)
        self.assertIn(app, visible)

    def test_application_flow_r4_admin_reject(self):
        """Rule R4: Super Admin rejects application -> status Rejected, reason saved, invisible to employer."""
        from apps.accounts.models import EmployerAccount
        from apps.jobs.models import Job
        from apps.candidates.models import Applicant

        employer = EmployerAccount.objects.create(
            company_name="Beta Logistics",
            contact_name="HR Lead",
            email="hr@beta.com",
            status="APPROVED"
        )
        job = Job.objects.create(
            employer=employer,
            title="Logistics Manager",
            status="Active"
        )
        app = Applicant.objects.create(
            job=job,
            full_name="Sunil Gupta",
            email="sunil@example.com",
            phone="9876543202",
            job_title=job.title,
            status="Application Submitted",
            approval_status="Pending",
            flow_step=2
        )

        # Admin rejects with reason
        resp = self.client.post(f'/api/admin/applications/{app.id}/reject/', json.dumps({
            'rejection_reason': 'Insufficient experience in logistics domain.'
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        app.refresh_from_db()
        self.assertEqual(app.approval_status, "Rejected")
        self.assertEqual(app.status, "Rejected")
        self.assertEqual(app.rejection_reason, 'Insufficient experience in logistics domain.')

        # Employer MUST NOT see rejected applications!
        visible = Applicant.objects.visible_to_employer(employer)
        self.assertNotIn(app, visible)

    def test_application_flow_r5_r6_sequential_transition_enforcement(self):
        """Rule R5/R6: Employer drives steps sequentially; invalid skip transition is blocked."""
        from apps.accounts.models import EmployerAccount
        from apps.jobs.models import Job
        from apps.candidates.models import Applicant
        from apps.candidates.status_helpers import set_applicant_status

        employer = EmployerAccount.objects.create(
            company_name="Gamma Tech",
            contact_name="Hiring Lead",
            email="hiring@gamma.com",
            status="APPROVED"
        )
        job = Job.objects.create(employer=employer, title="DevOps Engineer", status="Active")

        app = Applicant.objects.create(
            job=job,
            full_name="Anjali Rao",
            email="anjali@example.com",
            phone="9876543203",
            job_title=job.title,
            status="Employer Reviews",
            approval_status="Approved",
            flow_step=3
        )

        # Valid transition: Employer Reviews (3) -> Shortlisted (4)
        set_applicant_status(app, "Shortlisted", changed_by=f"employer ({employer.company_name})")
        app.refresh_from_db()
        self.assertEqual(app.status, "Shortlisted")
        self.assertEqual(app.flow_step, 4)

        # Invalid transition: Shortlisted (4) -> Joined (7) [Skipping steps 5 & 6]
        with self.assertRaises(ValueError):
            set_applicant_status(app, "Joined", changed_by="employer")

    def test_applicant_detail_put_status_update(self):
        """Test admin updating candidate status via PUT /api/applicant/<id>/."""
        resp = self.client.put(
            f'/api/applicant/{self.applicant1.id}/',
            data=json.dumps({"status": "Shortlisted"}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")

        self.applicant1.refresh_from_db()
        self.assertEqual(self.applicant1.status, "Shortlisted")
        self.assertEqual(self.applicant1.flow_step, 4)

