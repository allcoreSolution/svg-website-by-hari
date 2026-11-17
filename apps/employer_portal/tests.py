import json
from django.test import TestCase, Client
from django.utils import timezone
from apps.accounts.models import AdminUser, EmployerAccount, CandidateAccount
from apps.companies.models import Company, CompanyRequirement
from apps.jobs.models import Job
from apps.candidates.models import Applicant, Interview
from apps.placements.models import Placement, JobOffer


class EmployerPortalTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create Admin
        self.admin = AdminUser.objects.create(email='admin@skyvision.com')
        self.admin.set_password('admin123')
        self.admin.save()

        # Create Employer A
        self.employer_a = EmployerAccount.objects.create(
            company_name='Alpha Tech',
            contact_name='Alice Manager',
            email='alice@alphatech.com',
            phone='9876543210',
            status='APPROVED'
        )
        self.employer_a.set_password('pass123')
        self.employer_a.save()

        # Create Employer B
        self.employer_b = EmployerAccount.objects.create(
            company_name='Beta Solutions',
            contact_name='Bob Recruiter',
            email='bob@betasolutions.com',
            phone='9876543211',
            status='APPROVED'
        )
        self.employer_b.set_password('pass123')
        self.employer_b.save()

        # Create Pending Employer
        self.employer_pending = EmployerAccount.objects.create(
            company_name='Pending Startup',
            contact_name='Charlie Founder',
            email='charlie@pending.com',
            phone='9876543212',
            status='PENDING'
        )
        self.employer_pending.set_password('pass123')
        self.employer_pending.save()

        # Job for Employer A
        self.job_a = Job.objects.create(
            employer=self.employer_a,
            title='Python Backend Engineer',
            location='Lucknow',
            status='LIVE'
        )

        # Job for Employer B
        self.job_b = Job.objects.create(
            employer=self.employer_b,
            title='Frontend React Developer',
            location='Kanpur',
            status='LIVE'
        )

        # Candidate & Applicant for Job A
        self.cand = CandidateAccount.objects.create(
            email='candidate@gmail.com',
            full_name='Test Candidate',
            phone='9998887776',
            is_approved=True,
            approval_status='approved'
        )
        self.applicant = Applicant.objects.create(
            candidate_account=self.cand,
            job=self.job_a,
            full_name='Test Candidate',
            email='candidate@gmail.com',
            phone='9998887776',
            job_title='Python Backend Engineer',
            status='Employer Reviews',
            approval_status='Approved',
            flow_step=3
        )

    def test_employer_registration(self):
        """Test public employer registration creates PENDING account."""
        resp = self.client.post('/employer/register/', {
            'company_name': 'Gamma Corp',
            'contact_name': 'David HR',
            'email': 'david@gammacorp.com',
            'phone': '9876500000',
            'password': 'password123',
            'industry': 'IT & Software',
            'city': 'Lucknow'
        })
        self.assertEqual(resp.status_code, 302)
        emp = EmployerAccount.objects.get(email='david@gammacorp.com')
        self.assertEqual(emp.status, 'PENDING')
        self.assertEqual(emp.company_name, 'Gamma Corp')

    def test_pending_employer_cannot_login_dashboard(self):
        """Pending employer login shows review message and blocks dashboard."""
        resp = self.client.post('/employer/login/', {
            'email': 'charlie@pending.com',
            'password': 'pass123'
        })
        self.assertContains(resp, 'pending admin approval')
        
        # Accessing dashboard should redirect to pending page
        resp_dash = self.client.get('/employer/dashboard/')
        self.assertEqual(resp_dash.status_code, 302)
        self.assertIn('/employer/pending/', resp_dash.url)

    def test_admin_approve_employer(self):
        """Admin can approve pending employer."""
        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()

        resp = self.client.post(f'/api/admin/employer-registrations/{self.employer_pending.id}/approve/')
        self.assertEqual(resp.status_code, 200)
        
        self.employer_pending.refresh_from_db()
        self.assertEqual(self.employer_pending.status, 'APPROVED')

        from django.core import mail
        self.assertGreaterEqual(len(mail.outbox), 1)
        approval_email = mail.outbox[-1]
        self.assertIn(self.employer_pending.email, approval_email.to)
        self.assertIn("Registration Approved", approval_email.subject)
        self.assertIn("/employer/login/", approval_email.body)

    def test_employer_post_job_pending_approval(self):
        """Employer posts job which starts as PENDING_APPROVAL."""
        session = self.client.session
        session['employer_id'] = self.employer_a.id
        session.save()

        resp = self.client.post('/employer/jobs/new/', {
            'title': 'Senior DevOps Engineer',
            'description': 'Manage AWS and Docker clusters.',
            'location': 'Lucknow',
            'vacancies': '2'
        })
        self.assertEqual(resp.status_code, 302)

        job = Job.objects.get(title='Senior DevOps Engineer')
        self.assertEqual(job.status, 'PENDING_APPROVAL')
        self.assertEqual(job.employer, self.employer_a)

    def test_admin_approve_job(self):
        """Admin approves job to make it LIVE on site."""
        new_job = Job.objects.create(
            employer=self.employer_a,
            title='UI/UX Designer',
            description='Design web apps',
            status='PENDING_APPROVAL'
        )

        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()

        resp = self.client.post(f'/api/admin/job-approvals/{new_job.id}/approve/')
        self.assertEqual(resp.status_code, 200)

        new_job.refresh_from_db()
        self.assertEqual(new_job.status, 'LIVE')

    def test_employer_hiring_pipeline_and_placement(self):
        """Employer marks candidate Hired -> Placement record created automatically."""
        self.applicant.status = 'Offer Released'
        self.applicant.flow_step = 6
        self.applicant.save()

        session = self.client.session
        session['employer_id'] = self.employer_a.id
        session.save()

        resp = self.client.post(f'/employer/applicants/{self.applicant.id}/status/', json.dumps({
            'status': 'Hired',
            'package': '6.5 LPA',
            'joining_date': '2026-11-01',
            'notes': 'Selected after technical round.'
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        self.applicant.refresh_from_db()
        self.assertEqual(self.applicant.status, 'Joined')

        placement = Placement.objects.filter(applicant=self.applicant).first()
        self.assertIsNotNone(placement)
        self.assertEqual(placement.package, '6.5 LPA')
        self.assertEqual(placement.company_name, 'Alpha Tech')

    def test_idor_protection(self):
        """Employer B cannot modify applicant applying for Employer A's job."""
        session = self.client.session
        session['employer_id'] = self.employer_b.id  # Logged in as Employer B
        session.save()

        resp = self.client.post(f'/employer/applicants/{self.applicant.id}/status/', json.dumps({
            'status': 'Shortlisted'
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 404)  # 404 Not Found due to IDOR queryset filter

    def test_admin_registrations_tab_counts(self):
        """Admin approval API returns accurate pending counts."""
        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()

        resp_emp = self.client.get('/api/admin/employer-registrations/')
        self.assertEqual(resp_emp.status_code, 200)
        data_emp = json.loads(resp_emp.content)
        self.assertGreaterEqual(data_emp['pending_count'], 1)

        resp_job = self.client.get('/api/admin/job-approvals/')
        self.assertEqual(resp_job.status_code, 200)
        data_job = json.loads(resp_job.content)
        self.assertIn('pending_count', data_job)

    def test_scenario_1_apply_creates_pending_not_visible_to_employer_a(self):
        """1. Employer A posts job J; candidate C applies -> Applicant is Pending; employer A does NOT see C."""
        job_j = Job.objects.create(employer=self.employer_a, title='DevOps Lead', status='LIVE')
        cand_c = CandidateAccount.objects.create(email='c@example.com', full_name='Cand C', phone='9990001111', is_approved=True, approval_status='approved')
        session = self.client.session
        session['candidate_id'] = cand_c.id
        session.save()
        res = self.client.post('/api/apply', {'job_id': job_j.id})
        self.assertEqual(res.status_code, 200)

        app = Applicant.objects.get(candidate_account=cand_c, job=job_j)
        self.assertEqual(app.approval_status, 'Pending')

        session['employer_id'] = self.employer_a.id
        session.pop('candidate_id', None)
        session.save()

        visible = Applicant.objects.visible_to_employer(self.employer_a)
        self.assertNotIn(app, visible)
        res_list = self.client.get('/employer/applicants/')
        self.assertNotIn('Cand C', res_list.content.decode())

    def test_scenario_2_admin_approves_visible_to_a_not_b(self):
        """2. Admin approves -> employer A sees C; employer B (different company) does NOT see C in list, detail URL, status API, resume download, interviews, offers, placements."""
        job_j = Job.objects.create(employer=self.employer_a, title='Backend Dev', status='LIVE')
        cand_c = CandidateAccount.objects.create(email='c2@example.com', full_name='Cand C2', phone='9990002222', is_approved=True, approval_status='approved', resume='c2_resume.pdf')
        app = Applicant.objects.create(
            candidate_account=cand_c,
            job=job_j,
            employer=self.employer_a,
            company=self.employer_a.company,
            full_name='Cand C2',
            email='c2@example.com',
            phone='9990002222',
            status='Application Submitted',
            approval_status='Pending',
            resume='c2_resume.pdf'
        )
        iv = Interview.objects.create(applicant=app, candidate_name='Cand C2', interview_date=timezone.now().date(), interview_time=timezone.now().time(), status='Scheduled')
        offer = JobOffer.objects.create(applicant=app, candidate_name='Cand C2', company_name='Alpha Tech', status='Offer Sent', document='offer_c2.pdf')
        placement = Placement.objects.create(applicant=app, candidate_name='Cand C2', company_name='Alpha Tech', status='Joined')

        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()
        res_app = self.client.post(f'/api/admin/applications/{app.id}/approve/')
        self.assertEqual(res_app.status_code, 200)

        app.refresh_from_db()
        self.assertEqual(app.approval_status, 'Approved')

        # Employer A sees C
        session['employer_id'] = self.employer_a.id
        session.pop('admin_id', None)
        session.save()
        self.assertIn(app, Applicant.objects.visible_to_employer(self.employer_a))

        # Employer B (different company) does NOT see C
        session['employer_id'] = self.employer_b.id
        session.save()
        self.assertNotIn(app, Applicant.objects.visible_to_employer(self.employer_b))

        # Check list page
        res_b_list = self.client.get('/employer/applicants/')
        self.assertNotIn('Cand C2', res_b_list.content.decode())

        # Status API
        res_b_status = self.client.post(f'/employer/applicants/{app.id}/status/', json.dumps({'status': 'Shortlisted'}), content_type='application/json')
        self.assertEqual(res_b_status.status_code, 404)

        # Resume download IDOR check
        res_b_down = self.client.get('/api/admin/files/download/c2_resume.pdf')
        self.assertEqual(res_b_down.status_code, 404)

        # Interviews list
        res_b_iv = self.client.get('/employer/interviews/')
        self.assertNotIn('Cand C2', res_b_iv.content.decode())

        # Offers list
        res_b_off = self.client.get('/employer/offers/')
        self.assertNotIn('Cand C2', res_b_off.content.decode())

        # Placements list
        res_b_place = self.client.get('/employer/hired/')
        self.assertNotIn('Cand C2', res_b_place.content.decode())

    def test_scenario_3_two_employers_same_company_name(self):
        """3. Two employers with the same company_name do not see each other's applicants."""
        emp_a2 = EmployerAccount.objects.create(company_name='Alpha Tech', contact_name='Alice 2', email='alice2@alphatech.com', phone='9876543299', status='APPROVED', shares_company_data=False)
        job_a2 = Job.objects.create(employer=emp_a2, title='Java Dev', status='LIVE')
        app_a2 = Applicant.objects.create(
            job=job_a2,
            employer=emp_a2,
            full_name='Applicant of A2',
            email='a2_app@example.com',
            status='Employer Reviews',
            approval_status='Approved'
        )
        self.assertNotIn(app_a2, Applicant.objects.visible_to_employer(self.employer_a))

    def test_scenario_4_admin_rejects(self):
        """4. Admin rejects -> nobody sees it; candidate sees "Rejected" with reason."""
        job = Job.objects.create(employer=self.employer_a, title='Tester', status='LIVE')
        cand = CandidateAccount.objects.create(email='test_rej@example.com', full_name='Rej Cand', phone='9991112223', is_approved=True, approval_status='approved')
        app = Applicant.objects.create(candidate_account=cand, job=job, employer=self.employer_a, full_name='Rej Cand', status='New', approval_status='Pending')

        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()
        res = self.client.post(f'/api/admin/applications/{app.id}/reject/', json.dumps({'reason': 'Qualifications mismatch'}), content_type='application/json')
        self.assertEqual(res.status_code, 200)

        app.refresh_from_db()
        self.assertEqual(app.approval_status, 'Rejected')
        self.assertEqual(app.rejection_reason, 'Qualifications mismatch')

        # Employer does not see it
        self.assertNotIn(app, Applicant.objects.visible_to_employer(self.employer_a))

        # Candidate sees "Rejected" with reason in applied-jobs API
        session['candidate_id'] = cand.id
        session.pop('admin_id', None)
        session.save()
        res_cand = self.client.get('/api/candidate/applied-jobs/')
        self.assertEqual(res_cand.status_code, 200)
        data = res_cand.json()
        self.assertEqual(data['applications'][0]['application']['approval_status'], 'Rejected')
        self.assertEqual(data['applications'][0]['application']['rejection_reason'], 'Qualifications mismatch')

    def test_scenario_5_shortlisted_but_pending_not_visible(self):
        """5. Applicant with status="Shortlisted" or flow_step>=4 but approval_status="Pending" is NOT visible to the employer."""
        app = Applicant.objects.create(
            job=self.job_a,
            employer=self.employer_a,
            full_name='Sneaky Shortlisted',
            status='Shortlisted',
            approval_status='Pending',
            flow_step=4
        )
        self.assertNotIn(app, Applicant.objects.visible_to_employer(self.employer_a))

    def test_scenario_6_approving_job_without_employer_returns_400(self):
        """6. Approving an applicant whose job has no employer returns 400 and changes nothing."""
        job_no_emp = Job.objects.create(title='Orphan Job', status='LIVE')
        app = Applicant.objects.create(job=job_no_emp, full_name='Orphan Applicant', status='New', approval_status='Pending')

        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()
        res = self.client.post(f'/api/admin/applications/{app.id}/approve/')
        self.assertEqual(res.status_code, 400)

        app.refresh_from_db()
        self.assertEqual(app.approval_status, 'Pending')

    def test_scenario_7_admin_cannot_route_approval_to_different_employer(self):
        """7. Admin cannot route approval to another employer via employer_id."""
        job = Job.objects.create(employer=self.employer_a, title='Node Dev', status='LIVE')
        app = Applicant.objects.create(job=job, employer=self.employer_a, full_name='App Node', status='New', approval_status='Pending')

        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()

        # Passing conflicting employer_id returns 400
        res = self.client.post(f'/api/admin/applications/{app.id}/approve/', json.dumps({'employer_id': self.employer_b.id}), content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertIn("Cannot route approval to a different employer", res.json()["message"])

        # Approval without conflicting employer_id succeeds and retains job owner employer
        res_ok = self.client.post(f'/api/admin/applications/{app.id}/approve/')
        self.assertEqual(res_ok.status_code, 200)

        app.refresh_from_db()
        self.assertEqual(app.approval_status, 'Approved')
        self.assertEqual(app.employer, self.employer_a)

    def test_scenario_8_apply_non_live_or_no_owner_or_duplicate_fails(self):
        """8. Applying to a non-live job or a job without owner fails; duplicate apply fails."""
        cand = CandidateAccount.objects.create(email='app_test@example.com', full_name='App Test', phone='9992223334', is_approved=True, approval_status='approved')
        session = self.client.session
        session['candidate_id'] = cand.id
        session.save()

        # Non-live job
        job_closed = Job.objects.create(employer=self.employer_a, title='Closed Job', status='CLOSED')
        res_closed = self.client.post('/api/apply', {'job_id': job_closed.id})
        self.assertEqual(res_closed.status_code, 400)

        # Job without owner
        job_no_owner = Job.objects.create(title='No Owner Job', status='LIVE')
        res_no_owner = self.client.post('/api/apply', {'job_id': job_no_owner.id})
        self.assertEqual(res_no_owner.status_code, 400)

        # Valid apply
        res_ok = self.client.post('/api/apply', {'job_id': self.job_a.id})
        self.assertEqual(res_ok.status_code, 200)

        # Duplicate apply
        res_dup = self.client.post('/api/apply', {'job_id': self.job_a.id})
        self.assertEqual(res_dup.status_code, 400)

    def test_scenario_9_employer_cannot_modify_approval_status(self):
        """9. Employer cannot modify approval_status."""
        session = self.client.session
        session['employer_id'] = self.employer_a.id
        session.save()

        res_mod = self.client.post(f'/employer/applicants/{self.applicant.id}/status/', json.dumps({
            'approval_status': 'Pending'
        }), content_type='application/json')
        self.assertEqual(res_mod.status_code, 403)

        self.applicant.refresh_from_db()
        self.assertEqual(self.applicant.approval_status, 'Approved')

