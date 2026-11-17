import json
import os
from django.test import TestCase, Client
from django.utils import timezone
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.accounts.models import AdminUser, Role, RolePermission, AdminLoginLog, StaffMember
from apps.candidates.models import Applicant, Resume
from apps.placements.models import JobOffer
from apps.companies.models import Company
from apps.jobs.models import JobCategory, Job
from apps.ledger.models import LedgerEntry

class CompleteRoleAndPermissionSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Seed Roles
        self.super_role, _ = Role.objects.get_or_create(
            name="Super Admin",
            defaults={"description": "Full Access", "is_super": True, "is_system": True, "is_active": True}
        )
        self.viewer_role, _ = Role.objects.get_or_create(
            name="Viewer",
            defaults={"description": "Read-only access", "is_super": False, "is_system": True, "is_active": True}
        )
        self.accountant_role, _ = Role.objects.get_or_create(
            name="Accountant",
            defaults={"description": "Finance & Ledger", "is_super": False, "is_system": True, "is_active": True}
        )
        self.hr_role, _ = Role.objects.get_or_create(
            name="HR Manager",
            defaults={"description": "HR & Staff", "is_super": False, "is_system": True, "is_active": True}
        )
        self.archived_role, _ = Role.objects.get_or_create(
            name="Old Archived Role",
            defaults={"description": "Deprecated", "is_super": False, "is_system": False, "is_active": False}
        )

        # Viewer permissions (read-only)
        for code in ["dashboard.view", "candidates.view", "job_postings.view", "applications.view", "offer_letters.view", "staff.view"]:
            RolePermission.objects.get_or_create(role=self.viewer_role, code=code)

        # Accountant permissions (ledger & finance)
        for code in ["dashboard.view", "ledger.view", "ledger.add", "ledger.edit", "ledger.export", "payments.view", "payments.add", "invoices.view"]:
            RolePermission.objects.get_or_create(role=self.accountant_role, code=code)

        # HR Manager permissions (staff + view_salary)
        for code in ["dashboard.view", "staff.view", "staff.add", "staff.edit", "staff.view_salary", "candidates.view", "interviews.view", "interviews.add"]:
            RolePermission.objects.get_or_create(role=self.hr_role, code=code)

        # Create Admin Users
        self.super_admin = AdminUser.objects.create(
            email="super_test@skyvision.com",
            full_name="Super Admin User",
            role=self.super_role,
            is_active=True
        )
        self.super_admin.set_password("pass123")
        self.super_admin.save()

        self.viewer_admin = AdminUser.objects.create(
            email="viewer_test@skyvision.com",
            full_name="Viewer User",
            role=self.viewer_role,
            is_active=True
        )
        self.viewer_admin.set_password("pass123")
        self.viewer_admin.save()

        self.accountant_admin = AdminUser.objects.create(
            email="accountant_test@skyvision.com",
            full_name="Accountant User",
            role=self.accountant_role,
            is_active=True
        )
        self.accountant_admin.set_password("pass123")
        self.accountant_admin.save()

        self.hr_admin = AdminUser.objects.create(
            email="hr_test@skyvision.com",
            full_name="HR Manager User",
            role=self.hr_role,
            is_active=True
        )
        self.hr_admin.set_password("pass123")
        self.hr_admin.save()

        self.no_role_admin = AdminUser.objects.create(
            email="norole_test@skyvision.com",
            full_name="Unassigned User",
            role=None,
            is_active=True
        )
        self.no_role_admin.set_password("pass123")
        self.no_role_admin.save()

        self.archived_role_admin = AdminUser.objects.create(
            email="archived_role_test@skyvision.com",
            full_name="Archived Role User",
            role=self.archived_role,
            is_active=True
        )
        self.archived_role_admin.set_password("pass123")
        self.archived_role_admin.save()

        # Seed sample StaffMember with confidential financial details
        self.staff_member = StaffMember.objects.create(
            full_name="Ramesh Sharma",
            email="ramesh@skyvision.com",
            phone="9876543210",
            department="IT",
            designation="Developer",
            monthly_salary=50000.00,
            total_paid=40000.00,
            advance_salary=5000.00,
            pending_salary=5000.00,
            bank_name="HDFC Bank",
            bank_account_no="50100234567890",
            ifsc_code="HDFC0001234",
            pan_number="ABCDE1234F",
            aadhaar_number="1234-5678-9012",
            status="Active"
        )

        # Seed sample Applicant, Resume, JobOffer
        self.applicant = Applicant.objects.create(
            full_name="Sample Candidate",
            email="candidate@example.com",
            phone="9123456789",
            job_title="Python Dev",
            status="applied"
        )
        self.resume = Resume.objects.create(
            full_name="Sample Candidate Resume",
            mobile="9123456789",
            email="candidate@example.com",
            resume="uploads/resumes/test_candidate_resume.pdf"
        )
        self.company = Company.objects.create(
            name="Sample Corp Ltd",
            email="corp@example.com"
        )
        self.job_offer = JobOffer.objects.create(
            applicant=self.applicant,
            candidate_name="Sample Candidate",
            company_name="Sample Corp Ltd",
            designation="Software Engineer",
            offered_ctc=600000.00,
            status="Offered"
        )

        # Create dummy protected resume file on disk
        test_resume_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', 'resumes')
        os.makedirs(test_resume_dir, exist_ok=True)
        self.dummy_resume_path = os.path.join(test_resume_dir, 'test_resume_file.pdf')
        with open(self.dummy_resume_path, 'wb') as f:
            f.write(b"%PDF-1.4 dummy resume content")

    def tearDown(self):
        if os.path.exists(self.dummy_resume_path):
            try:
                os.remove(self.dummy_resume_path)
            except Exception:
                pass

    def login_as(self, admin_user):
        session = self.client.session
        session['admin_id'] = admin_user.id
        session.save()

    # -------------------------------------------------------------
    # 1. Viewer Tests (Forbidden on Write/Delete, Allowed on Read)
    # -------------------------------------------------------------
    def test_viewer_can_read_applicants(self):
        """Viewer can read /api/applicants (200 OK)."""
        self.login_as(self.viewer_admin)
        response = self.client.get("/api/applicants")
        self.assertEqual(response.status_code, 200)

    def test_viewer_forbidden_on_post_applicants(self):
        """Viewer gets 403 on POST /api/admin/applicants."""
        self.login_as(self.viewer_admin)
        response = self.client.post(
            "/api/admin/applicants",
            data=json.dumps({"name": "Test New", "email": "new@test.com"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

    def test_viewer_forbidden_on_delete_resume(self):
        """Viewer gets 403 on DELETE /api/resume/<id>."""
        self.login_as(self.viewer_admin)
        response = self.client.delete(f"/api/resume/{self.resume.id}")
        self.assertEqual(response.status_code, 403)

    def test_viewer_forbidden_on_delete_job_offer(self):
        """Viewer gets 403 on DELETE /api/job-offer/<id>."""
        self.login_as(self.viewer_admin)
        response = self.client.delete(f"/api/job-offer/{self.job_offer.id}")
        self.assertEqual(response.status_code, 403)

    # -------------------------------------------------------------
    # 2. Accountant Tests
    # -------------------------------------------------------------
    def test_accountant_can_use_ledger_apis(self):
        """Accountant can access ledger list, payments, and export APIs (200 OK)."""
        self.login_as(self.accountant_admin)
        # 1. Ledger list
        resp1 = self.client.get("/api/admin/ledger/")
        self.assertEqual(resp1.status_code, 200)

        # 2. Ledger payments
        resp2 = self.client.get("/api/admin/ledger/payments/")
        self.assertEqual(resp2.status_code, 200)

        # 3. Ledger export CSV
        resp3 = self.client.get("/api/admin/ledger/export/")
        self.assertEqual(resp3.status_code, 200)

    def test_accountant_forbidden_on_roles_and_candidates_add(self):
        """Accountant cannot modify roles or create candidates."""
        self.login_as(self.accountant_admin)
        resp1 = self.client.get("/admin-panel/users/roles/")
        self.assertEqual(resp1.status_code, 403)

        resp2 = self.client.post(
            "/api/admin/applicants",
            data=json.dumps({"name": "Bad"}),
            content_type="application/json"
        )
        self.assertEqual(resp2.status_code, 403)

    # -------------------------------------------------------------
    # 3. HR Manager & Staff Detail Tests
    # -------------------------------------------------------------
    def test_hr_can_open_staff_detail_with_salary(self):
        """HR Manager with staff.view_salary can open staff detail and see unmasked salary."""
        self.login_as(self.hr_admin)
        response = self.client.get(f"/api/admin/staff/{self.staff_member.id}/detail/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "success")
        staff = data.get("staff", {})
        # Salary and bank should be visible for HR Manager
        self.assertEqual(staff.get("monthly_salary"), 50000.00)
        self.assertEqual(staff.get("bank_name"), "HDFC Bank")
        self.assertEqual(staff.get("pan_number"), "ABCDE1234F")

    # -------------------------------------------------------------
    # 4. Confidential Masking Tests (Without staff.view_salary)
    # -------------------------------------------------------------
    def test_salary_and_bank_masked_for_user_without_salary_permission(self):
        """Viewer (without staff.view_salary) sees salary, bank, PAN, Aadhaar masked with bullets."""
        self.login_as(self.viewer_admin)
        response = self.client.get(f"/api/admin/staff/{self.staff_member.id}/detail/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        staff = data.get("staff", {})

        # Masked values verification
        self.assertEqual(staff.get("monthly_salary"), 0.0)
        self.assertEqual(staff.get("monthly_salary_fmt"), "••••••")
        self.assertEqual(staff.get("total_paid_fmt"), "••••••")
        self.assertEqual(staff.get("bank_name"), "••••••")
        self.assertEqual(staff.get("bank_account_no"), "••••••••")
        self.assertEqual(staff.get("pan_number"), "••••••••")
        self.assertEqual(staff.get("aadhaar_number"), "••••••••")
        self.assertEqual(staff.get("payments"), [])

    def test_payment_recording_blocked_without_salary_permission(self):
        """User without staff.view_salary cannot record salary/advance payment (403 Forbidden)."""
        self.login_as(self.viewer_admin)
        response = self.client.post(
            f"/api/admin/staff/{self.staff_member.id}/record-payment/",
            data=json.dumps({"amount": 5000, "payment_type": "salary"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

    # -------------------------------------------------------------
    # 5. Anonymous Public Forms (Must Keep Working)
    # -------------------------------------------------------------
    def test_anonymous_can_submit_contact_form(self):
        """Anonymous user can submit public contact form POST /api/contact."""
        payload = {
            "name": "Public Inquirer",
            "email": "inquirer@example.com",
            "mobile": "9988776655",
            "subject": "General Inquiry",
            "message": "Hello, I want to inquire about placement services."
        }
        response = self.client.post("/api/contact", data=json.dumps(payload), content_type="application/json")
        # Should not be redirected to /admin-panel/login or return 401/403 admin error
        self.assertNotIn(response.status_code, [401, 403, 302])

    def test_anonymous_can_submit_job_application(self):
        """Anonymous user hits public candidate apply endpoint without admin block."""
        payload = {
            "full_name": "Public Candidate",
            "email": "candidate_pub@example.com",
            "phone": "9876543210",
            "job_title": "Backend Engineer"
        }
        response = self.client.post("/api/apply", data=payload)
        # It responds with candidate portal status ('login_required' to /candidate/login/), NOT admin middleware 401 redirect
        data = response.json()
        self.assertEqual(data.get("redirect_url"), "/candidate/login/")

    def test_anonymous_can_submit_quick_resume(self):
        """Anonymous user can submit public quick resume upload POST /api/upload-resume."""
        test_file = SimpleUploadedFile("my_resume.pdf", b"%PDF-1.4 sample content", content_type="application/pdf")
        payload = {
            "full_name": "Quick Applicant",
            "mobile": "9876543210",
            "email": "quick@example.com",
            "qualification": "B.Tech",
            "experience": "2",
            "applying_for": "Software Engineer",
            "resume": test_file
        }
        response = self.client.post("/api/upload-resume", data=payload)
        # Should be processed publicly without admin authentication block
        self.assertNotIn(response.status_code, [401, 403, 302])

    def test_anonymous_can_submit_company_enquiry(self):
        """Anonymous user can submit public company enquiry POST /api/company-enquiry."""
        payload = {
            "company_name": "Acme Industries",
            "contact_person": "Jane Doe",
            "email": "hr@acme.com",
            "phone": "9811223344",
            "requirements": "Need 5 Java Developers"
        }
        response = self.client.post("/api/company-enquiry", data=payload)
        self.assertNotIn(response.status_code, [401, 403, 302])

    # -------------------------------------------------------------
    # 6. Protected Media Document Tests
    # -------------------------------------------------------------
    def test_anonymous_cannot_fetch_resumes(self):
        """Anonymous user is blocked (403 Forbidden) when requesting /media/uploads/resumes/..."""
        response = self.client.get("/media/uploads/resumes/test_resume_file.pdf")
        self.assertEqual(response.status_code, 403)
        self.assertIn(b"Access denied", response.content)

    def test_super_admin_can_fetch_protected_resumes(self):
        """Super Admin can access /media/uploads/resumes/... (200 OK)."""
        self.login_as(self.super_admin)
        response = self.client.get("/media/uploads/resumes/test_resume_file.pdf")
        self.assertEqual(response.status_code, 200)
        content = b"".join(response.streaming_content)
        self.assertEqual(content, b"%PDF-1.4 dummy resume content")

    def test_authorized_hr_can_fetch_protected_resumes(self):
        """HR Manager with candidates.view can fetch protected resumes (200 OK)."""
        self.login_as(self.hr_admin)
        response = self.client.get("/media/uploads/resumes/test_resume_file.pdf")
        self.assertEqual(response.status_code, 200)

    # -------------------------------------------------------------
    # 7. No Role Assigned / Archived Role Tests
    # -------------------------------------------------------------
    def test_user_with_no_role_gets_no_role_assigned_page(self):
        """Admin with role=None gets 403 and 'No Active Role Assigned' page."""
        self.login_as(self.no_role_admin)
        response = self.client.get("/admin-panel/dashboard/")
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "No Active Role Assigned", status_code=403)

    def test_user_with_no_role_api_gets_no_role_assigned_json(self):
        """Admin with role=None calling API gets 403 JSON with NO_ROLE_ASSIGNED."""
        self.login_as(self.no_role_admin)
        response = self.client.get("/api/applicants")
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data.get("code"), "NO_ROLE_ASSIGNED")

    def test_user_with_archived_role_gets_no_role_assigned_page(self):
        """Admin with an archived/inactive role gets 403 'No Active Role Assigned' page."""
        self.login_as(self.archived_role_admin)
        response = self.client.get("/admin-panel/dashboard/")
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "No Active Role Assigned", status_code=403)

    # -------------------------------------------------------------
    # 8. AdminLoginLog in admin_login_view Tests
    # -------------------------------------------------------------
    def test_admin_login_view_records_success_log(self):
        """Form POST to /admin-panel/login/ records success in AdminLoginLog."""
        AdminLoginLog.objects.all().delete()
        response = self.client.post("/admin-panel/login/", data={
            "email": "super_test@skyvision.com",
            "password": "pass123"
        })
        self.assertEqual(response.status_code, 302)
        log = AdminLoginLog.objects.filter(email="super_test@skyvision.com", status="success").first()
        self.assertIsNotNone(log)

    def test_admin_login_view_records_failed_log(self):
        """Form POST to /admin-panel/login/ with bad password records failed in AdminLoginLog."""
        AdminLoginLog.objects.all().delete()
        response = self.client.post("/admin-panel/login/", data={
            "email": "super_test@skyvision.com",
            "password": "wrong_password"
        })
        self.assertEqual(response.status_code, 400)
        log = AdminLoginLog.objects.filter(email="super_test@skyvision.com", status="failed").first()
        self.assertIsNotNone(log)
