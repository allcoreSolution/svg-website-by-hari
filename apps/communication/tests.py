import os
from unittest.mock import patch
from smtplib import SMTPAuthenticationError, SMTPDataError
from django.test import TestCase, Client, override_settings
from django.core import mail
from django.conf import settings
from django.utils import timezone
from django.db import IntegrityError, transaction

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.core.management import call_command

from apps.accounts.models import AdminUser, CandidateAccount, EmployerAccount, Role
from apps.candidates.models import Applicant
from apps.jobs.models import Job
from apps.communication.models import BulkMessage, MessageRecipient, MessageTemplate
from apps.communication.sanitizer import sanitize_html, html_to_plain_text
from apps.communication.services import (
    resolve_recipients,
    process_bulk_message_send,
    queue_bulk_message_send,
    create_recipient_snapshots,
    send_test_email,
    get_daily_sent_email_count,
    render_placeholders,
    check_stale_sending_messages,
    validate_attachment_file
)


class BulkCommunicationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        MessageRecipient.objects.all().delete()
        BulkMessage.objects.all().delete()

        # Admin User
        self.super_role, _ = Role.objects.get_or_create(name="Super Admin", defaults={"is_super": True, "is_system": True})
        self.admin = AdminUser.objects.create(email="admin@skyvision.com", is_active=True, role=self.super_role)
        self.admin.set_password("admin123")
        self.admin.save()

        # Approved Candidates
        self.cand_app1 = CandidateAccount.objects.create(
            full_name="Candidate One",
            email="cand1@example.com",
            phone="9876543210",
            current_company="Alpha Corp",
            approval_status="approved",
            is_approved=True
        )
        self.cand_app2 = CandidateAccount.objects.create(
            full_name="Candidate Two",
            email="cand2@example.com",
            phone="9876543211",
            current_company="Beta LLC",
            approval_status="approved",
            is_approved=True
        )

        # Pending Candidate
        self.cand_pending = CandidateAccount.objects.create(
            full_name="Candidate Pending",
            email="pending@example.com",
            phone="9876543212",
            approval_status="pending",
            is_approved=False
        )

        # Approved Employers
        self.emp1 = EmployerAccount.objects.create(
            company_name="Tech Corp",
            contact_name="Alice Employer",
            email="alice@techcorp.com",
            phone="9998887771",
            status="APPROVED"
        )
        self.emp2 = EmployerAccount.objects.create(
            company_name="Biz Solutions",
            contact_name="Bob Employer",
            email="bob@biz.com",
            phone="9998887772",
            status="APPROVED"
        )

        # Pending Employer
        self.emp_pending = EmployerAccount.objects.create(
            company_name="Pending Corp",
            contact_name="Charlie Employer",
            email="charlie@pending.com",
            phone="9998887773",
            status="PENDING"
        )

        # Job & Applicant setup for Shortlisted / Selected filters
        self.job = Job.objects.create(
            employer=self.emp1,
            title="Software Developer",
            status="ACTIVE"
        )

        # App 1 -> Shortlisted
        self.app_shortlisted = Applicant.objects.create(
            candidate_account=self.cand_app1,
            job=self.job,
            employer=self.emp1,
            full_name=self.cand_app1.full_name,
            email=self.cand_app1.email,
            phone=self.cand_app1.phone,
            job_title=self.job.title,
            status="Shortlisted",
            approval_status="Approved"
        )

        # App 2 -> Selected
        self.app_selected = Applicant.objects.create(
            candidate_account=self.cand_app2,
            job=self.job,
            employer=self.emp1,
            full_name=self.cand_app2.full_name,
            email=self.cand_app2.email,
            phone=self.cand_app2.phone,
            job_title=self.job.title,
            status="Selected",
            approval_status="Approved"
        )

    def login_admin(self):
        session = self.client.session
        session['admin_id'] = self.admin.id
        session['admin_email'] = self.admin.email
        session.save()

    def login_candidate(self, candidate):
        session = self.client.session
        session['candidate_id'] = candidate.id
        session['candidate_email'] = candidate.email
        session.save()

    def login_employer(self, employer):
        session = self.client.session
        session['employer_id'] = employer.id
        session['employer_email'] = employer.email
        session.save()

    # --------------------------------------------------------------------------
    # Existing Baseline Tests
    # --------------------------------------------------------------------------

    def test_registered_filter_approved_only(self):
        recipients = resolve_recipients("candidate", candidate_filter="registered")
        self.assertIn(self.cand_app1, recipients)
        self.assertIn(self.cand_app2, recipients)
        self.assertNotIn(self.cand_pending, recipients)

    def test_shortlisted_and_selected_filters(self):
        shortlisted = resolve_recipients("candidate", candidate_filter="shortlisted")
        self.assertIn(self.cand_app1, shortlisted)
        self.assertNotIn(self.cand_app2, shortlisted)

        selected = resolve_recipients("candidate", candidate_filter="selected")
        self.assertIn(self.cand_app2, selected)
        self.assertNotIn(self.cand_app1, selected)

    def test_employer_audience_filter(self):
        employers = resolve_recipients("employer")
        self.assertIn(self.emp1, employers)
        self.assertIn(self.emp2, employers)
        self.assertNotIn(self.emp_pending, employers)

    def test_portal_inbox_isolation(self):
        msg_cand = BulkMessage.objects.create(
            title="Candidate Announcement",
            subject="Subj",
            body="Hello {{name}}",
            audience_type="candidate",
            candidate_filter="registered",
            channels=["dashboard"]
        )
        queue_bulk_message_send(msg_cand.id, sync=True)

        msg_emp = BulkMessage.objects.create(
            title="Employer Announcement",
            subject="Subj",
            body="Hello {{name}}",
            audience_type="employer",
            channels=["dashboard"]
        )
        queue_bulk_message_send(msg_emp.id, sync=True)

        self.login_candidate(self.cand_app1)
        res_cand = self.client.get("/candidate/messages/")
        self.assertContains(res_cand, "Candidate Announcement")
        self.assertNotContains(res_cand, "Employer Announcement")

        self.login_employer(self.emp1)
        res_emp = self.client.get("/employer/messages/")
        self.assertContains(res_emp, "Employer Announcement")
        self.assertNotContains(res_emp, "Candidate Announcement")

    def test_strict_privacy_candidate_idor(self):
        msg = BulkMessage.objects.create(
            title="Private Message for Cand 1",
            subject="Subj",
            body="Secret text",
            audience_type="candidate",
            channels=["dashboard"]
        )
        rec1 = MessageRecipient.objects.create(
            bulk_message=msg,
            candidate_account=self.cand_app1,
            channel="dashboard",
            delivery_status="Sent"
        )

        self.login_candidate(self.cand_app2)
        res_unauthorized = self.client.post(f"/api/candidate/messages/{rec1.id}/read/")
        self.assertEqual(res_unauthorized.status_code, 404)

        self.login_candidate(self.cand_app1)
        res_authorized = self.client.post(f"/api/candidate/messages/{rec1.id}/read/")
        self.assertEqual(res_authorized.status_code, 200)

    def test_mark_read_updates_unread_count(self):
        msg = BulkMessage.objects.create(
            title="Test Notice",
            subject="Subj",
            body="Content",
            audience_type="candidate",
            channels=["dashboard"]
        )
        rec = MessageRecipient.objects.create(
            bulk_message=msg,
            candidate_account=self.cand_app1,
            channel="dashboard",
            delivery_status="Sent",
            is_read=False
        )

        self.login_candidate(self.cand_app1)

        res_before = self.client.get("/api/candidate/messages/unread-count/")
        self.assertEqual(res_before.json()['unread_count'], 1)

        self.client.post(f"/api/candidate/messages/{rec.id}/read/")

        res_after = self.client.get("/api/candidate/messages/unread-count/")
        self.assertEqual(res_after.json()['unread_count'], 0)

    @override_settings(
        EMAIL_HOST_USER="admin@gmail.com",
        EMAIL_HOST_PASSWORD="app-password-1234",
        EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
    )
    def test_gmail_configured_smtp_backend(self):
        self.assertEqual(settings.EMAIL_BACKEND, "django.core.mail.backends.smtp.EmailBackend")
        self.assertTrue(bool(settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD))

    @override_settings(
        EMAIL_HOST_USER="",
        EMAIL_HOST_PASSWORD="",
        EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend"
    )
    def test_console_backend_fallback_when_credentials_empty(self):
        self.assertEqual(settings.EMAIL_BACKEND, "django.core.mail.backends.console.EmailBackend")
        self.assertFalse(bool(settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD))

    @override_settings(EMAIL_HOST_USER="", EMAIL_HOST_PASSWORD="")
    def test_dashboard_notification_delivered_without_email_credentials(self):
        msg = BulkMessage.objects.create(
            title="Dashboard Only Test",
            subject="Test Subj",
            body="Hello {{name}}",
            audience_type="candidate",
            candidate_filter="registered",
            channels=["dashboard"]
        )
        queue_bulk_message_send(msg.id, sync=True)

        msg.refresh_from_db()
        self.assertEqual(msg.status, "Sent")
        self.assertGreater(msg.sent_count, 0)
        self.assertEqual(msg.failed_count, 0)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_single_recipient_per_email(self):
        mail.outbox = []
        msg = BulkMessage.objects.create(
            title="Multi Recipient Test",
            subject="Personalized Broadcast",
            body="Hello {{name}}",
            audience_type="candidate",
            candidate_filter="registered",
            channels=["email"]
        )
        queue_bulk_message_send(msg.id, sync=True)

        self.assertGreater(len(mail.outbox), 0)
        for sent_mail in mail.outbox:
            self.assertEqual(len(sent_mail.to), 1)
            self.assertEqual(len(sent_mail.cc), 0)
            self.assertEqual(len(sent_mail.bcc), 0)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', SITE_URL='http://127.0.0.1:8000')
    def test_html_and_plain_text_bodies(self):
        mail.outbox = []
        msg = BulkMessage.objects.create(
            title="HTML Body Test",
            subject="Test Subject",
            body="Main email content line 1\nMain email content line 2",
            audience_type="candidate",
            candidate_filter="registered",
            channels=["email"]
        )
        queue_bulk_message_send(msg.id, sync=True)

        self.assertGreater(len(mail.outbox), 0)
        sent = mail.outbox[0]
        self.assertIn("Main email content line 1", sent.body)
        self.assertIn("/candidate/messages/", sent.body)

        self.assertEqual(len(sent.alternatives), 1)
        html_alt, mimetype = sent.alternatives[0]
        self.assertEqual(mimetype, "text/html")
        self.assertIn("Main email content line 1", html_alt)
        self.assertIn("/candidate/messages/", html_alt)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_placeholder_replacement(self):
        mail.outbox = []
        msg = BulkMessage.objects.create(
            title="Placeholder Test",
            subject="Notice for {{name}}",
            body="Hello {{name}}, welcome to {{company_name}} for role {{job_title}}.",
            audience_type="candidate",
            candidate_filter="shortlisted",
            channels=["email"]
        )
        queue_bulk_message_send(msg.id, sync=True)

        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertEqual(sent.to, [self.cand_app1.email])
        self.assertIn("Candidate One", sent.subject)
        self.assertIn("Candidate One", sent.body)
        self.assertIn("Alpha Corp", sent.body)
        self.assertIn("Software Developer", sent.body)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_header_injection_prevention(self):
        mail.outbox = []
        long_subject_with_newlines = "Header Injection Test \nBcc: hacker@evil.com\r\n" + ("A" * 200)

        msg = BulkMessage.objects.create(
            title="Injection Test",
            subject=long_subject_with_newlines,
            body="Test body",
            audience_type="candidate",
            candidate_filter="shortlisted",
            channels=["email"]
        )
        queue_bulk_message_send(msg.id, sync=True)

        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertNotIn("\n", sent.subject)
        self.assertNotIn("\r", sent.subject)
        self.assertLessEqual(len(sent.subject), 150)

    @override_settings(COMM_EMAIL_DAILY_LIMIT=2, EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_daily_limit_enforcement(self):
        mail.outbox = []
        prev_msg = BulkMessage.objects.create(title="Prev", subject="S", body="B", audience_type="candidate", channels=["email"])
        MessageRecipient.objects.create(bulk_message=prev_msg, candidate_account=self.cand_app1, channel="email", delivery_status="Sent", sent_at=timezone.now())
        MessageRecipient.objects.create(bulk_message=prev_msg, candidate_account=self.cand_app2, channel="email", delivery_status="Sent", sent_at=timezone.now())

        msg = BulkMessage.objects.create(
            title="Daily Limit Test",
            subject="Subj",
            body="Body text",
            audience_type="candidate",
            candidate_filter="registered",
            channels=["email"]
        )
        queue_bulk_message_send(msg.id, sync=True)

        msg.refresh_from_db()
        self.assertIn("limit", msg.stop_reason.lower())

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
    @patch('django.core.mail.backends.smtp.EmailBackend.open', side_effect=SMTPAuthenticationError(535, b"Auth failed"))
    def test_smtp_authentication_failure_halts_queue(self, mock_open):
        msg = BulkMessage.objects.create(
            title="Auth Failure Test",
            subject="Subj",
            body="Body text",
            audience_type="candidate",
            candidate_filter="registered",
            channels=["dashboard", "email"]
        )
        queue_bulk_message_send(msg.id, sync=True)

        msg.refresh_from_db()
        self.assertIn("Gmail login failed", msg.stop_reason)

        dash_sent = msg.recipients.filter(channel='dashboard', delivery_status='Sent').count()
        self.assertGreater(dash_sent, 0)

    @override_settings(COMM_ENABLE_SMS_WHATSAPP=False)
    def test_channel_gating_sms_whatsapp(self):
        msg = BulkMessage.objects.create(
            title="Channel Gating Test",
            subject="Subj",
            body="Body text",
            audience_type="candidate",
            candidate_filter="registered",
            channels=["dashboard", "email", "sms", "whatsapp"]
        )

        create_recipient_snapshots(msg)
        channels = list(msg.recipients.values_list('channel', flat=True).distinct())

        self.assertIn("dashboard", channels)
        self.assertIn("email", channels)
        self.assertNotIn("sms", channels)
        self.assertNotIn("whatsapp", channels)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_snapshot_recipient_retry_isolation(self):
        msg = BulkMessage.objects.create(
            title="Retry Test",
            subject="Subj",
            body="Body text",
            audience_type="candidate",
            candidate_filter="registered",
            channels=["dashboard", "email"]
        )

        snapshots = create_recipient_snapshots(msg)
        initial_count = len(snapshots)

        email_rec1 = msg.recipients.get(candidate_account=self.cand_app1, channel='email')
        email_rec1.delivery_status = 'Failed'
        email_rec1.error = 'Temporary connection error'
        email_rec1.save()

        email_rec2 = msg.recipients.get(candidate_account=self.cand_app2, channel='email')
        email_rec2.delivery_status = 'Sent'
        email_rec2.save()

        msg.recipients.filter(delivery_status='Failed').update(delivery_status='Pending', error='')

        process_bulk_message_send(msg.id)

        self.assertEqual(msg.recipients.count(), initial_count)
        email_rec1.refresh_from_db()
        self.assertEqual(email_rec1.delivery_status, 'Sent')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_test_email_api_endpoint(self):
        self.login_admin()
        res = self.client.post(
            "/admin-panel/communication/send-test/",
            data={'to_email': 'admin@skyvision.com', 'subject': 'Test', 'body': 'Test Body'},
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['status'], 'success')

        res_invalid = self.client.post(
            "/admin-panel/communication/send-test/",
            data={'to_email': 'not-an-email', 'subject': 'Test', 'body': 'Test Body'},
            content_type="application/json"
        )
        self.assertEqual(res_invalid.status_code, 400)
        self.assertEqual(res_invalid.json()['status'], 'error')

    # --------------------------------------------------------------------------
    # Hardening Tests (a through j)
    # --------------------------------------------------------------------------

    def test_draft_employer_ids_persistence_and_validation(self):
        self.login_admin()
        res_invalid = self.client.post(
            "/admin-panel/communication/send/",
            data={
                "title": "Invalid Emp Test",
                "subject": "S",
                "body": "B",
                "audience_type": "employer",
                "employer_ids": [99999],
                "channels": ["email"],
                "action": "send"
            },
            content_type="application/json"
        )
        self.assertEqual(res_invalid.status_code, 400)
        self.assertIn("Selected employer(s) no longer valid", res_invalid.json()['message'])

        draft_msg = BulkMessage.objects.create(
            title="Draft for Emp 1",
            subject="Subj",
            body="Content",
            audience_type="employer",
            employer_ids=[self.emp1.id],
            channels=["dashboard", "email"],
            status="Draft"
        )

        res_send = self.client.post(f"/admin-panel/communication/history/{draft_msg.id}/send-draft/")
        self.assertEqual(res_send.status_code, 200)

        draft_msg.refresh_from_db()
        recipients = list(draft_msg.recipients.values_list('employer_account_id', flat=True))
        self.assertIn(self.emp1.id, recipients)
        self.assertNotIn(self.emp2.id, recipients)

    @override_settings(COMM_EMAIL_DAILY_LIMIT=1, EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_daily_cap_pending_status_and_retry(self):
        mail.outbox = []
        msg = BulkMessage.objects.create(
            title="Cap Pending Test",
            subject="Subj",
            body="Body",
            audience_type="candidate",
            candidate_filter="registered",
            channels=["dashboard", "email"]
        )
        create_recipient_snapshots(msg)
        process_bulk_message_send(msg.id)

        msg.refresh_from_db()
        self.assertEqual(msg.status, "Partial")
        # 2 dashboard sent + 1 email sent = 3 total sent
        self.assertEqual(msg.sent_count, 3)
        self.assertEqual(msg.pending_count, 1)

        pending_row = msg.recipients.get(delivery_status='Pending')
        self.assertEqual(pending_row.delivery_status, 'Pending')

        with override_settings(COMM_EMAIL_DAILY_LIMIT=100):
            process_bulk_message_send(msg.id)
            msg.refresh_from_db()
            self.assertEqual(msg.status, "Sent")
            self.assertEqual(msg.sent_count, 4)
            self.assertEqual(msg.pending_count, 0)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
    @patch('django.core.mail.backends.smtp.EmailBackend.open', side_effect=SMTPDataError(550, b"5.4.5 Daily user sending limit exceeded"))
    def test_quota_error_550_545_stops_run_remaining_pending(self, mock_send):
        msg = BulkMessage.objects.create(
            title="Quota 550 Test",
            subject="Subj",
            body="Body",
            audience_type="candidate",
            candidate_filter="registered",
            channels=["dashboard", "email"]
        )
        process_bulk_message_send(msg.id)

        msg.refresh_from_db()
        self.assertIn("limit", msg.stop_reason.lower())
        self.assertEqual(msg.recipients.filter(channel='dashboard', delivery_status='Sent').count(), 2)
        self.assertGreater(msg.recipients.filter(channel='email', delivery_status='Pending').count(), 0)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_retry_pending_rows_and_sending_409_conflict(self):
        self.login_admin()
        msg = BulkMessage.objects.create(
            title="Retry Pending Test",
            subject="Subj",
            body="Body",
            audience_type="candidate",
            candidate_filter="registered",
            channels=["email"],
            status="Draft"
        )
        create_recipient_snapshots(msg)

        BulkMessage.objects.filter(id=msg.id).update(status="Sending")
        res_409 = self.client.post(f"/admin-panel/communication/history/{msg.id}/retry/")
        self.assertEqual(res_409.status_code, 409)

        BulkMessage.objects.filter(id=msg.id).update(status="Partial")
        rec1 = msg.recipients.all()[0]
        rec1.delivery_status = 'Sent'
        rec1.save()

        mail.outbox = []
        res_retry = self.client.post(f"/admin-panel/communication/history/{msg.id}/retry/")
        self.assertEqual(res_retry.status_code, 200)

        rec1.refresh_from_db()
        self.assertEqual(rec1.delivery_status, 'Sent')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_duplicate_email_in_one_run(self):
        emp_same_email = EmployerAccount.objects.create(
            company_name="Dup Email Corp",
            contact_name="Dup Contact",
            email=self.cand_app1.email,
            phone="9998881234",
            status="APPROVED"
        )
        msg = BulkMessage.objects.create(
            title="Dedupe Test",
            subject="Subj",
            body="Body",
            audience_type="candidate",
            channels=["email"]
        )
        rec1 = MessageRecipient.objects.create(
            bulk_message=msg, candidate_account=self.cand_app1, channel="email", delivery_status="Pending"
        )
        rec2 = MessageRecipient.objects.create(
            bulk_message=msg, employer_account=emp_same_email, channel="email", delivery_status="Pending"
        )

        process_bulk_message_send(msg.id)

        rec1.refresh_from_db()
        rec2.refresh_from_db()

        statuses = [rec1.delivery_status, rec2.delivery_status]
        errors = [rec1.error, rec2.error]
        self.assertIn("Skipped", statuses)
        self.assertIn("Duplicate email in this run", errors)

    def test_mark_read_post_only_and_ownership(self):
        msg = BulkMessage.objects.create(title="T", subject="S", body="B", audience_type="candidate", channels=["dashboard"])
        rec = MessageRecipient.objects.create(bulk_message=msg, candidate_account=self.cand_app1, channel="dashboard", delivery_status="Sent")

        self.login_candidate(self.cand_app1)
        res_get = self.client.get(f"/api/candidate/messages/{rec.id}/read/")
        self.assertEqual(res_get.status_code, 405)

        self.login_candidate(self.cand_app2)
        res_other = self.client.post(f"/api/candidate/messages/{rec.id}/read/")
        self.assertEqual(res_other.status_code, 404)

        self.login_candidate(self.cand_app1)
        res_owner = self.client.post(f"/api/candidate/messages/{rec.id}/read/")
        self.assertEqual(res_owner.status_code, 200)

    def test_mark_all_read_isolation(self):
        msg = BulkMessage.objects.create(title="T", subject="S", body="B", audience_type="candidate", channels=["dashboard", "email"])
        rec_dash = MessageRecipient.objects.create(bulk_message=msg, candidate_account=self.cand_app1, channel="dashboard", delivery_status="Sent", is_read=False)
        rec_email = MessageRecipient.objects.create(bulk_message=msg, candidate_account=self.cand_app1, channel="email", delivery_status="Sent", is_read=False)
        rec_pending = MessageRecipient.objects.create(bulk_message=msg, candidate_account=self.cand_app2, channel="dashboard", delivery_status="Pending", is_read=False)

        self.login_candidate(self.cand_app1)
        self.client.post("/api/candidate/messages/mark-all-read/")

        rec_dash.refresh_from_db()
        rec_email.refresh_from_db()
        rec_pending.refresh_from_db()

        self.assertTrue(rec_dash.is_read)
        self.assertFalse(rec_email.is_read)
        self.assertFalse(rec_pending.is_read)

    def test_db_constraints_on_message_recipient(self):
        msg = BulkMessage.objects.create(title="Constraint Test", subject="S", body="B", audience_type="candidate", channels=["dashboard"])

        MessageRecipient.objects.create(bulk_message=msg, candidate_account=self.cand_app1, channel="dashboard")

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                MessageRecipient.objects.create(bulk_message=msg, candidate_account=self.cand_app1, channel="dashboard")

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                MessageRecipient.objects.create(bulk_message=msg, channel="dashboard")

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                MessageRecipient.objects.create(bulk_message=msg, candidate_account=self.cand_app1, employer_account=self.emp1, channel="dashboard")

    @patch('apps.communication.services.resolve_recipients', side_effect=RuntimeError("Simulated worker crash"))
    def test_worker_crash_recomputes_status(self, mock_resolve):
        msg = BulkMessage.objects.create(title="Crash Test", subject="S", body="B", audience_type="candidate", candidate_filter="registered", channels=["email"])

        process_bulk_message_send(msg.id)

        msg.refresh_from_db()
        self.assertNotEqual(msg.status, "Sending")
        self.assertIn(msg.status, ["Failed", "Partial"])
        self.assertIn("Worker crashed", msg.stop_reason)

    def test_sidebar_badge_context_processor(self):
        self.login_admin()
        msg = BulkMessage.objects.create(title="Failed Test", subject="S", body="B", audience_type="candidate", channels=["email"])
        MessageRecipient.objects.create(bulk_message=msg, candidate_account=self.cand_app1, channel="email", delivery_status="Failed", error="Test error")

        from django.core.cache import cache
        cache.delete('comm_failed_delivery_count')

        res = self.client.get("/admin-panel/dashboard/")
        self.assertEqual(res.status_code, 200)
        self.assertIn('failed_delivery_count', res.context)
        self.assertGreaterEqual(res.context['failed_delivery_count'], 1)

    # --------------------------------------------------------------------------
    # Regression & Comprehensive Feature Tests
    # --------------------------------------------------------------------------

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_regression_compose_filter_shortlisted_and_selected(self):
        self.login_admin()

        # 1. Shortlisted Filter
        res_shortlisted = self.client.post(
            "/admin-panel/communication/send/",
            data={
                "title": "Shortlisted Broadcast",
                "subject": "Interview Update",
                "body": "Congratulations {{name}}",
                "audience_type": "candidate",
                "candidate_filter": "shortlisted",
                "channels": ["email"],
                "action": "send"
            },
            content_type="application/json"
        )
        self.assertEqual(res_shortlisted.status_code, 200)
        msg_id_1 = res_shortlisted.json().get('message_id')
        msg_1 = BulkMessage.objects.get(id=msg_id_1)
        recipients_1 = list(msg_1.recipients.values_list('candidate_account_id', flat=True))
        self.assertIn(self.cand_app1.id, recipients_1)
        self.assertNotIn(self.cand_app2.id, recipients_1)

        # 2. Selected Filter
        res_selected = self.client.post(
            "/admin-panel/communication/send/",
            data={
                "title": "Selected Broadcast",
                "subject": "Offer Release",
                "body": "Congratulations on your selection {{name}}",
                "audience_type": "candidate",
                "candidate_filter": "selected",
                "channels": ["email"],
                "action": "send"
            },
            content_type="application/json"
        )
        self.assertEqual(res_selected.status_code, 200)
        msg_id_2 = res_selected.json().get('message_id')
        msg_2 = BulkMessage.objects.get(id=msg_id_2)
        recipients_2 = list(msg_2.recipients.values_list('candidate_account_id', flat=True))
        self.assertIn(self.cand_app2.id, recipients_2)
        self.assertNotIn(self.cand_app1.id, recipients_2)

    def test_candidate_include_pending_toggle(self):
        self.login_admin()

        res_without = self.client.post(
            "/admin-panel/communication/preview-recipients/",
            data={
                "audience_type": "candidate",
                "candidate_filter": "registered",
                "include_pending": False
            },
            content_type="application/json"
        )
        self.assertEqual(res_without.status_code, 200)
        self.assertEqual(res_without.json()['count'], 2)

        res_with = self.client.post(
            "/admin-panel/communication/preview-recipients/",
            data={
                "audience_type": "candidate",
                "candidate_filter": "registered",
                "include_pending": True
            },
            content_type="application/json"
        )
        self.assertEqual(res_with.status_code, 200)
        self.assertEqual(res_with.json()['count'], 3)

    def test_applicant_approval_status_gate(self):
        # Applicant shortlisted but approval_status='Pending'
        cand_unapproved_app = CandidateAccount.objects.create(
            full_name="Unapproved Shortlist",
            email="unapproved@example.com",
            phone="9876543299",
            approval_status="approved",
            is_approved=True
        )
        Applicant.objects.create(
            candidate_account=cand_unapproved_app,
            job=self.job,
            employer=self.emp1,
            full_name=cand_unapproved_app.full_name,
            email=cand_unapproved_app.email,
            phone=cand_unapproved_app.phone,
            job_title=self.job.title,
            status="Shortlisted",
            approval_status="Pending"
        )

        shortlisted = resolve_recipients("candidate", candidate_filter="shortlisted")
        self.assertIn(self.cand_app1, shortlisted)
        self.assertNotIn(cand_unapproved_app, shortlisted)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_channels_selection_and_validation(self):
        self.login_admin()

        # Reject empty channels
        res_no_ch = self.client.post(
            "/admin-panel/communication/send/",
            data={
                "title": "No Channel Test",
                "subject": "Subject",
                "body": "Body",
                "audience_type": "candidate",
                "candidate_filter": "registered",
                "channels": [],
                "action": "send"
            },
            content_type="application/json"
        )
        self.assertEqual(res_no_ch.status_code, 400)
        self.assertIn("at least one delivery channel", res_no_ch.json()['message'])

        # Email only
        res_email = self.client.post(
            "/admin-panel/communication/send/",
            data={
                "title": "Email Only Test",
                "subject": "Subject",
                "body": "Body",
                "audience_type": "candidate",
                "candidate_filter": "registered",
                "channels": ["email"],
                "action": "send"
            },
            content_type="application/json"
        )
        self.assertEqual(res_email.status_code, 200)
        msg_email = BulkMessage.objects.get(id=res_email.json()['message_id'])
        self.assertTrue(msg_email.recipients.filter(channel='email').exists())
        self.assertFalse(msg_email.recipients.filter(channel='dashboard').exists())

        # Dashboard only
        res_dash = self.client.post(
            "/admin-panel/communication/send/",
            data={
                "title": "Dash Only Test",
                "subject": "Subject",
                "body": "Body",
                "audience_type": "candidate",
                "candidate_filter": "registered",
                "channels": ["dashboard"],
                "action": "send"
            },
            content_type="application/json"
        )
        self.assertEqual(res_dash.status_code, 200)
        msg_dash = BulkMessage.objects.get(id=res_dash.json()['message_id'])
        self.assertTrue(msg_dash.recipients.filter(channel='dashboard').exists())
        self.assertFalse(msg_email.recipients.filter(channel='dashboard').exists())

    def test_html_sanitization_pipeline(self):
        dirty_html = (
            "<p>Safe text with <b>bold</b> and <i>italic</i> and "
            "<a href='https://skyvisiongroup.in' onclick='malicious()'>Our Site</a></p>"
            "<script>alert('xss');</script>"
            "<iframe src='http://evil.com'></iframe>"
        )
        clean_html = sanitize_html(dirty_html)
        self.assertIn("<b>bold</b>", clean_html)
        self.assertIn("<i>italic</i>", clean_html)
        self.assertIn("href=\"https://skyvisiongroup.in\"", clean_html)
        self.assertNotIn("onclick", clean_html)
        self.assertNotIn("<script>", clean_html)
        self.assertNotIn("<iframe>", clean_html)

        plain_text = html_to_plain_text(clean_html)
        self.assertIn("Safe text with bold and italic and Our Site", plain_text)
        self.assertNotIn("<p>", plain_text)
        self.assertNotIn("<b>", plain_text)

    def test_placeholder_html_escaping(self):
        malicious_cand = CandidateAccount.objects.create(
            full_name="Evil <script>alert(1)</script> & Co",
            email="evil@example.com",
            phone="9988776655",
            approval_status="approved",
            current_company="A & B Partners"
        )

        # HTML context should escape
        html_out = render_placeholders("Hello {{name}} from {{company_name}} {{unknown_tag}}", malicious_cand, is_html=True)
        self.assertIn("Evil &lt;script&gt;alert(1)&lt;/script&gt; &amp; Co", html_out)
        self.assertIn("A &amp; B Partners", html_out)
        self.assertNotIn("{{unknown_tag}}", html_out)

        # Plain-text context should remain unescaped
        plain_out = render_placeholders("Hello {{name}} from {{company_name}}", malicious_cand, is_html=False)
        self.assertIn("Evil <script>alert(1)</script> & Co", plain_out)
        self.assertIn("A & B Partners", plain_out)

    def test_attachment_validation(self):
        # 1. Disallowed extension
        bad_ext = SimpleUploadedFile("payload.exe", b"MZexecutabledata", content_type="application/octet-stream")
        with self.assertRaises(ValidationError) as cm:
            validate_attachment_file(bad_ext)
        self.assertIn("not allowed", str(cm.exception))

        # 2. File size > 5 MB
        huge_file = SimpleUploadedFile("large.pdf", b"%PDF" + (b"0" * (6 * 1024 * 1024)), content_type="application/pdf")
        with self.assertRaises(ValidationError) as cm:
            validate_attachment_file(huge_file)
        self.assertIn("exceeds maximum allowed size", str(cm.exception))

        # 3. Magic byte mismatch
        fake_pdf = SimpleUploadedFile("fake.pdf", b"Not actually a PDF file", content_type="application/pdf")
        with self.assertRaises(ValidationError) as cm:
            validate_attachment_file(fake_pdf)
        self.assertIn("content does not match", str(cm.exception))

        # 4. Valid PDF file
        valid_pdf = SimpleUploadedFile("document.pdf", b"%PDF-1.4\n1 0 obj\n<<\n>>\nendobj\ntrailer\n<<\n>>\n%%EOF", content_type="application/pdf")
        self.assertTrue(validate_attachment_file(valid_pdf))

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_opt_out_skipped_delivery(self):
        self.cand_app1.email_notifications_enabled = False
        self.cand_app1.save()

        msg = BulkMessage.objects.create(
            title="Opt-Out Test",
            subject="Subj",
            body="Body",
            audience_type="candidate",
            candidate_filter="shortlisted",
            channels=["email", "dashboard"]
        )
        create_recipient_snapshots(msg)
        process_bulk_message_send(msg.id)

        rec_email = msg.recipients.get(channel='email', candidate_account=self.cand_app1)
        self.assertEqual(rec_email.delivery_status, 'Skipped')
        self.assertIn("opted out", rec_email.error.lower())

        rec_dash = msg.recipients.get(channel='dashboard', candidate_account=self.cand_app1)
        self.assertEqual(rec_dash.delivery_status, 'Sent')

    def test_stop_sending_action(self):
        self.login_admin()
        msg = BulkMessage.objects.create(
            title="Stop Test",
            subject="Subj",
            body="Body",
            audience_type="candidate",
            channels=["email"],
            status="Sending",
            is_stopped=False
        )

        res = self.client.post(f"/admin-panel/communication/history/{msg.id}/stop/")
        self.assertEqual(res.status_code, 200)

        msg.refresh_from_db()
        self.assertTrue(msg.is_stopped)
        self.assertEqual(msg.status, "Stopped")
        self.assertIn("Stopped by admin", msg.stop_reason)

    def test_stale_sending_recovery(self):
        fifteen_mins_ago = timezone.now() - timezone.timedelta(minutes=15)
        msg = BulkMessage.objects.create(
            title="Stale Test",
            subject="Subj",
            body="Body",
            audience_type="candidate",
            channels=["email"],
            status="Sending",
            last_activity_at=fifteen_mins_ago
        )
        # Force updated created_at
        BulkMessage.objects.filter(id=msg.id).update(created_at=fifteen_mins_ago, last_activity_at=fifteen_mins_ago)

        interrupted = check_stale_sending_messages()
        self.assertGreaterEqual(interrupted, 1)

        msg.refresh_from_db()
        self.assertEqual(msg.status, "Interrupted")
        self.assertIn("interrupted", msg.stop_reason.lower())

    def test_process_bulk_messages_management_command(self):
        msg = BulkMessage.objects.create(
            title="Command Test",
            subject="Subj",
            body="Body",
            audience_type="candidate",
            candidate_filter="registered",
            channels=["dashboard"],
            status="Draft"
        )
        create_recipient_snapshots(msg)

        call_command('process_bulk_messages')
        msg.refresh_from_db()
        self.assertEqual(msg.status, "Draft")  # Drafts are not auto-processed without --all or pending status

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_idempotency_token_prevents_duplicate(self):
        self.login_admin()

        payload = {
            "title": "Idempotent Msg",
            "subject": "Subj",
            "body": "Body",
            "audience_type": "candidate",
            "candidate_filter": "shortlisted",
            "channels": ["dashboard"],
            "idempotency_key": "unique-idemp-token-xyz-123",
            "action": "send"
        }

        res1 = self.client.post("/admin-panel/communication/send/", data=payload, content_type="application/json")
        self.assertEqual(res1.status_code, 200)
        msg_id_1 = res1.json()['message_id']

        res2 = self.client.post("/admin-panel/communication/send/", data=payload, content_type="application/json")
        self.assertEqual(res2.status_code, 200)
        msg_id_2 = res2.json()['message_id']

        self.assertEqual(msg_id_1, msg_id_2)
        self.assertEqual(BulkMessage.objects.filter(idempotency_key="unique-idemp-token-xyz-123").count(), 1)

    def test_message_templates_crud_and_seeding(self):
        self.login_admin()

        # Verify seeded templates from migration
        self.assertGreaterEqual(MessageTemplate.objects.count(), 7)

        # Create
        res_create = self.client.post(
            "/admin-panel/communication/templates/save/",
            data={
                "name": "Custom Test Template",
                "audience_type": "candidate",
                "subject": "Greetings {{name}}",
                "body": "<b>Welcome!</b>",
                "is_active": True
            },
            content_type="application/json"
        )
        self.assertEqual(res_create.status_code, 200)
        tpl_id = res_create.json()['id']

        # Fetch JSON
        res_get = self.client.get(f"/admin-panel/communication/templates/{tpl_id}/json/")
        self.assertEqual(res_get.status_code, 200)
        self.assertEqual(res_get.json()['template']['name'], "Custom Test Template")

        # Update
        res_update = self.client.post(
            "/admin-panel/communication/templates/save/",
            data={
                "id": tpl_id,
                "name": "Updated Test Template",
                "audience_type": "employer",
                "subject": "Greetings {{company_name}}",
                "body": "<b>Updated</b>",
                "is_active": False
            },
            content_type="application/json"
        )
        self.assertEqual(res_update.status_code, 200)
        tpl = MessageTemplate.objects.get(id=tpl_id)
        self.assertEqual(tpl.name, "Updated Test Template")
        self.assertEqual(tpl.audience_type, "employer")
        self.assertFalse(tpl.is_active)

        # Delete
        res_del = self.client.post(f"/admin-panel/communication/templates/{tpl_id}/delete/")
        self.assertEqual(res_del.status_code, 200)
        self.assertFalse(MessageTemplate.objects.filter(id=tpl_id).exists())

    def test_live_status_polling_and_csv_export(self):
        self.login_admin()

        msg = BulkMessage.objects.create(
            title="Polling & CSV Test",
            subject="Subj",
            body="Body",
            audience_type="candidate",
            candidate_filter="registered",
            channels=["dashboard"]
        )
        create_recipient_snapshots(msg)
        process_bulk_message_send(msg.id)

        # Live status polling
        res_poll = self.client.get(f"/admin-panel/communication/history/{msg.id}/status/")
        self.assertEqual(res_poll.status_code, 200)
        data = res_poll.json()
        self.assertEqual(data['status'], 'Sent')
        self.assertTrue(data['is_complete'])
        self.assertEqual(data['sent_count'], 2)

        # CSV export
        res_csv = self.client.get(f"/admin-panel/communication/history/{msg.id}/export-csv/")
        self.assertEqual(res_csv.status_code, 200)
        self.assertEqual(res_csv['Content-Type'], 'text/csv')
        self.assertIn(f"broadcast_{msg.id}_recipients.csv", res_csv['Content-Disposition'])
        content = res_csv.content.decode('utf-8')
        self.assertIn("Candidate One", content)
        self.assertIn("Candidate Two", content)

    def test_delivery_settings_view(self):
        self.login_admin()
        res = self.client.get("/admin-panel/communication/settings/")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Active SMTP Parameters")
        self.assertContains(res, "Send Test Email")

    def test_non_admin_redirected(self):
        # Without logging in as admin
        client = Client()
        res_compose = client.get("/admin-panel/communication/compose/")
        self.assertEqual(res_compose.status_code, 302)

        res_history = client.get("/admin-panel/communication/history/")
        self.assertEqual(res_history.status_code, 302)

        res_settings = client.get("/admin-panel/communication/settings/")
        self.assertEqual(res_settings.status_code, 302)

    # --------------------------------------------------------------------------
    # Hardened End-to-End Scenarios (Part B)
    # --------------------------------------------------------------------------

    def test_interview_status_excluded_from_shortlisted(self):
        # Application with status 'Interview' must NOT be in shortlisted
        cand_interview = CandidateAccount.objects.create(
            full_name="Interview Candidate",
            email="interview@example.com",
            phone="9876543277",
            approval_status="approved",
            is_approved=True
        )
        Applicant.objects.create(
            candidate_account=cand_interview,
            job=self.job,
            employer=self.emp1,
            full_name=cand_interview.full_name,
            email=cand_interview.email,
            phone=cand_interview.phone,
            job_title=self.job.title,
            status="Interview",
            approval_status="Approved"
        )
        shortlisted = resolve_recipients("candidate", candidate_filter="shortlisted")
        self.assertIn(self.cand_app1, shortlisted)
        self.assertNotIn(cand_interview, shortlisted)

    def test_shortlisted_only_excluded_from_selected(self):
        # Candidate who is only Shortlisted must NOT be in selected
        selected = resolve_recipients("candidate", candidate_filter="selected")
        self.assertIn(self.cand_app2, selected)
        self.assertNotIn(self.cand_app1, selected)

    def test_candidate_with_multiple_applications_distinct(self):
        # Candidate with two applications: 1 Shortlisted, 1 Rejected -> appears ONCE
        cand_multi = CandidateAccount.objects.create(
            full_name="Multi App Candidate",
            email="multi@example.com",
            phone="9876543266",
            approval_status="approved",
            is_approved=True
        )
        job2 = Job.objects.create(employer=self.emp1, title="Backend Engineer", status="ACTIVE")
        Applicant.objects.create(
            candidate_account=cand_multi,
            job=self.job,
            employer=self.emp1,
            full_name=cand_multi.full_name,
            email=cand_multi.email,
            phone=cand_multi.phone,
            job_title=self.job.title,
            status="Shortlisted",
            approval_status="Approved"
        )
        Applicant.objects.create(
            candidate_account=cand_multi,
            job=job2,
            employer=self.emp1,
            full_name=cand_multi.full_name,
            email=cand_multi.email,
            phone=cand_multi.phone,
            job_title=job2.title,
            status="Rejected",
            approval_status="Approved"
        )
        shortlisted = resolve_recipients("candidate", candidate_filter="shortlisted")
        matching = [c for c in shortlisted if c.id == cand_multi.id]
        self.assertEqual(len(matching), 1)

    def test_employer_status_exclusions(self):
        # Suspended and pending employers excluded from approved
        emp_suspended = EmployerAccount.objects.create(
            company_name="Suspended Corp",
            contact_name="Sus Contact",
            email="sus@corp.com",
            phone="9998887799",
            status="SUSPENDED"
        )
        employers = resolve_recipients("employer")
        self.assertIn(self.emp1, employers)
        self.assertIn(self.emp2, employers)
        self.assertNotIn(self.emp_pending, employers)
        self.assertNotIn(emp_suspended, employers)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_candidate_and_employer_sharing_same_email_dedup(self):
        shared_email = "shared_contact@example.com"
        cand_shared = CandidateAccount.objects.create(
            full_name="Shared Candidate",
            email=shared_email,
            phone="9876543111",
            approval_status="approved",
            is_approved=True
        )
        emp_shared = EmployerAccount.objects.create(
            company_name="Shared Partner",
            contact_name="Shared Employer",
            email=shared_email,
            phone="9998887111",
            status="APPROVED"
        )
        msg = BulkMessage.objects.create(
            title="Shared Email Broadcast",
            subject="Notice",
            body="Hello {{name}}",
            audience_type="candidate",
            channels=["email"]
        )
        # Manually create snapshots for both candidate and employer under same broadcast
        rec1 = MessageRecipient.objects.create(
            bulk_message=msg, candidate_account=cand_shared, channel="email", delivery_status="Pending"
        )
        rec2 = MessageRecipient.objects.create(
            bulk_message=msg, employer_account=emp_shared, channel="email", delivery_status="Pending"
        )
        mail.outbox = []
        process_bulk_message_send(msg.id)

        rec1.refresh_from_db()
        rec2.refresh_from_db()
        # Exactly one is Sent, the duplicate is Skipped
        statuses = {rec1.delivery_status, rec2.delivery_status}
        self.assertIn('Sent', statuses)
        self.assertIn('Skipped', statuses)
        self.assertEqual(len(mail.outbox), 1)

    def test_attachment_deleted_from_disk_no_crash(self):
        self.login_admin()
        dummy_file = SimpleUploadedFile("temp_file.pdf", b"%PDF-1.4\ncontent", content_type="application/pdf")
        msg = BulkMessage.objects.create(
            title="Deleted File Broadcast",
            subject="Subj",
            body="Body",
            audience_type="candidate",
            channels=["dashboard"],
            attachment=dummy_file
        )
        # Delete file from disk
        if msg.attachment and os.path.exists(msg.attachment.path):
            os.remove(msg.attachment.path)

        res_history = self.client.get("/admin-panel/communication/history/")
        self.assertEqual(res_history.status_code, 200)

        res_detail = self.client.get(f"/admin-panel/communication/history/{msg.id}/")
        self.assertEqual(res_detail.status_code, 200)

    def test_sanitizer_advanced_xss_vectors(self):
        # 1. Image onerror
        self.assertNotIn("onerror", sanitize_html('<img src=x onerror=alert(1)>'))
        self.assertNotIn("<img", sanitize_html('<img src=x onerror=alert(1)>'))

        # 2. SVG onload
        self.assertNotIn("onload", sanitize_html('<svg onload=alert(1)>text</svg>'))
        self.assertNotIn("<svg", sanitize_html('<svg onload=alert(1)>text</svg>'))

        # 3. Data URL in link
        data_link = '<a href="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==">Click</a>'
        self.assertNotIn("data:", sanitize_html(data_link))

        # 4. Uppercase tags
        upper_dirty = '<SCRIPT>alert(1)</SCRIPT><STRONG>Safe Bold</STRONG>'
        clean = sanitize_html(upper_dirty)
        self.assertNotIn("<SCRIPT", clean)
        self.assertIn("<strong>Safe Bold</strong>", clean)

        # 5. Broken/malformed tags
        broken = '<<<script>>alert(1)<<</script>><b>Valid Bold</b>'
        clean_broken = sanitize_html(broken)
        self.assertNotIn("<script>", clean_broken)
        self.assertIn("<b>Valid Bold</b>", clean_broken)

    def test_concurrent_worker_execution_lock(self):
        msg = BulkMessage.objects.create(
            title="Lock Test",
            subject="Subj",
            body="Body",
            audience_type="candidate",
            channels=["dashboard"],
            status="Sending"
        )
        # Calling process_bulk_message_send while status is already 'Sending' should safely abort
        process_bulk_message_send(msg.id)
        msg.refresh_from_db()
        self.assertEqual(msg.status, "Sending")

    def test_management_command_check_email_setup(self):
        from io import StringIO
        out = StringIO()
        call_command('check_email_setup', stdout=out)
        output = out.getvalue()
        self.assertIn("EMAIL_BACKEND", output)
        self.assertIn("EMAIL_HOST_PASSWORD :", output)
        self.assertNotIn("password123", output)  # Real passwords never in output

    def test_management_command_send_test_email(self):
        from io import StringIO
        out = StringIO()
        with override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            call_command('send_test_email', to='testrecipient@example.com', stdout=out)
            output = out.getvalue()
            self.assertIn("Test email successfully sent", output)

    def test_compose_candidate_category_emails_and_removed_filters(self):
        self.login_admin()
        res_page = self.client.get("/admin-panel/communication/compose/")
        self.assertEqual(res_page.status_code, 200)
        self.assertNotContains(res_page, "Filter by Job Posting:")
        self.assertNotContains(res_page, "Filter by Company:")
        self.assertContains(res_page, 'id="specificCandidateSelect"')

        # 1. Register Candidate -> returns both approved candidates
        res_reg = self.client.post(
            "/admin-panel/communication/preview-recipients/",
            data={"audience_type": "candidate", "candidate_filter": "registered"},
            content_type="application/json"
        )
        self.assertEqual(res_reg.status_code, 200)
        reg_emails = [c['email'] for c in res_reg.json()['candidates']]
        self.assertIn(self.cand_app1.email, reg_emails)
        self.assertIn(self.cand_app2.email, reg_emails)

        # 2. Shortlisted Candidate -> returns only shortlisted candidate email
        res_short = self.client.post(
            "/admin-panel/communication/preview-recipients/",
            data={"audience_type": "candidate", "candidate_filter": "shortlisted"},
            content_type="application/json"
        )
        self.assertEqual(res_short.status_code, 200)
        short_emails = [c['email'] for c in res_short.json()['candidates']]
        self.assertEqual(short_emails, [self.cand_app1.email])

        # 3. Selected Candidate -> returns only selected candidate email
        res_sel = self.client.post(
            "/admin-panel/communication/preview-recipients/",
            data={"audience_type": "candidate", "candidate_filter": "selected"},
            content_type="application/json"
        )
        self.assertEqual(res_sel.status_code, 200)
        sel_emails = [c['email'] for c in res_sel.json()['candidates']]
        self.assertEqual(sel_emails, [self.cand_app2.email])
