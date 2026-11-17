import os
import sys
import re
import threading
import logging
import time
import html
from smtplib import SMTPAuthenticationError, SMTPRecipientsRefused, SMTPDataError, SMTPResponseException
from django.utils import timezone
from django.utils.html import escape
from django.core.mail import get_connection, EmailMultiAlternatives
from django.core.validators import validate_email, ValidationError
from django.conf import settings
from django.core.cache import cache
from django.db import connections
from django.db.models import Q

from apps.accounts.models import CandidateAccount, EmployerAccount
from apps.candidates.constants import SHORTLISTED_STATUSES, SELECTED_STATUSES
from apps.communication.models import BulkMessage, MessageRecipient
from apps.communication.providers import get_sms_provider, get_whatsapp_provider
from apps.communication.sanitizer import sanitize_html, html_to_plain_text
from apps.enquiries.models import log_activity

logger = logging.getLogger(__name__)

ALLOWED_ATTACHMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}


def mask_sensitive_info(text):
    if not text:
        return ""
    password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
    if password and password in str(text):
        text = str(text).replace(password, '******')
    return str(text)


def is_quota_or_limit_error(exc):
    """
    Detects Gmail quota/limit error responses (550 5.4.5, 421/452 rate limits, daily sending limit text).
    """
    err_str = str(exc).lower()
    quota_keywords = [
        "5.4.5",
        "daily user sending limit",
        "rate limit",
        "quota",
        "sending limit",
        "too many messages",
        "user_limit_exceeded"
    ]
    if any(k in err_str for k in quota_keywords):
        return True
    code = getattr(exc, 'smtp_code', None) or getattr(exc, 'code', None)
    if code in [550, 421, 452] and any(k in err_str for k in quota_keywords):
        return True
    return False


def validate_attachment_file(file_obj):
    """
    Validates single attachment file: extension, max size (default 5 MB), and content magic bytes.
    """
    if not file_obj:
        return True

    max_mb = getattr(settings, 'COMM_MAX_ATTACHMENT_MB', 5)
    max_bytes = max_mb * 1024 * 1024

    if file_obj.size > max_bytes:
        raise ValidationError(f"Attachment exceeds maximum allowed size of {max_mb} MB.")

    file_name = file_obj.name.lower()
    ext = file_name.rsplit('.', 1)[-1] if '.' in file_name else ''
    if ext not in ALLOWED_ATTACHMENT_EXTENSIONS:
        raise ValidationError(f"File format (.{ext}) is not allowed. Allowed formats: PDF, DOC, DOCX, JPG, PNG.")

    # Read first 16 bytes for magic signature sniffing
    pos = file_obj.tell() if hasattr(file_obj, 'tell') else 0
    header = file_obj.read(16)
    if hasattr(file_obj, 'seek'):
        file_obj.seek(pos)

    is_valid_magic = False
    if ext == 'pdf' and header.startswith(b'%PDF'):
        is_valid_magic = True
    elif ext in ['jpg', 'jpeg'] and header.startswith(b'\xff\xd8\xff'):
        is_valid_magic = True
    elif ext == 'png' and header.startswith(b'\x89PNG\r\n\x1a\n'):
        is_valid_magic = True
    elif ext == 'doc' and header.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
        is_valid_magic = True
    elif ext == 'docx' and header.startswith(b'PK\x03\x04'):
        is_valid_magic = True

    if not is_valid_magic:
        raise ValidationError("File content does not match the file extension.")

    return True


def resolve_recipients(audience_type, candidate_filter='', include_pending=False, employer_ids=None, specific_candidate_ids=None, job_id=None, company_id=None):
    """
    Resolves targets (CandidateAccount or EmployerAccount objects) based on audience type and filters.
    Single source of truth using SHORTLISTED_STATUSES and SELECTED_STATUSES constants.
    """
    if audience_type == 'candidate':
        # If specific candidates are picked, they override other candidate filters
        if specific_candidate_ids:
            if isinstance(specific_candidate_ids, str):
                specific_candidate_ids = [int(i.strip()) for i in specific_candidate_ids.split(',') if i.strip().isdigit()]
            return list(CandidateAccount.objects.filter(id__in=specific_candidate_ids).order_by('full_name'))

        if include_pending:
            qs = CandidateAccount.objects.filter(approval_status__in=['approved', 'pending'])
        else:
            qs = CandidateAccount.objects.filter(approval_status='approved')

        if candidate_filter == 'shortlisted':
            qs = qs.filter(
                applications__status__in=SHORTLISTED_STATUSES,
                applications__approval_status='Approved'
            )
        elif candidate_filter == 'selected':
            qs = qs.filter(
                applications__status__in=SELECTED_STATUSES,
                applications__approval_status='Approved'
            )

        if job_id:
            try:
                qs = qs.filter(applications__job_id=int(job_id))
            except (ValueError, TypeError):
                pass

        if company_id:
            try:
                qs = qs.filter(applications__job__company_id=int(company_id))
            except (ValueError, TypeError):
                pass

        return list(qs.distinct().order_by('full_name'))

    elif audience_type == 'employer':
        if candidate_filter == 'pending':
            qs = EmployerAccount.objects.filter(status='PENDING')
        else:
            qs = EmployerAccount.objects.filter(status='APPROVED')

        if employer_ids:
            if isinstance(employer_ids, str):
                employer_ids = [int(i.strip()) for i in employer_ids.split(',') if i.strip().isdigit()]
            qs = qs.filter(id__in=employer_ids)
        return list(qs.order_by('company_name'))

    return []


def render_placeholders(text, recipient, is_html=False):
    """
    Replaces {{name}}, {{email}}, {{company_name}}, {{job_title}}, {{status}} placeholders.
    If is_html=True, placeholder values are HTML-escaped before substitution.
    Unknown placeholders are safely removed.
    """
    if not text:
        return ""

    if isinstance(recipient, CandidateAccount):
        raw_name = recipient.full_name or "Candidate"
        raw_email = recipient.email or ""
        raw_company_name = getattr(recipient, 'current_company', None) or "Sky Vision Partner"
        if hasattr(recipient, '_prefetched_objects_cache') and 'applications' in recipient._prefetched_objects_cache:
            apps_list = list(recipient.applications.all())
            latest_app = max(apps_list, key=lambda a: a.id) if apps_list else None
        else:
            latest_app = recipient.applications.order_by('-id').first() if recipient.pk else None
        raw_job_title = latest_app.job_title if latest_app else "Candidate"
        raw_status = latest_app.status if latest_app else (recipient.approval_status.title() if recipient.approval_status else "Registered")
    elif isinstance(recipient, EmployerAccount):
        raw_name = recipient.contact_name or "Employer"
        raw_email = recipient.email or ""
        raw_company_name = recipient.company_name or "Partner Organization"
        raw_job_title = "Employer Partner"
        raw_status = recipient.status.title() if recipient.status else "Active"
    else:
        raw_name = getattr(recipient, 'name', None) or "User"
        raw_email = getattr(recipient, 'email', None) or ""
        raw_company_name = "Sky Vision Group"
        raw_job_title = "Associate"
        raw_status = "Active"

    if is_html:
        name = escape(raw_name)
        email_val = escape(raw_email)
        company_name = escape(raw_company_name)
        job_title = escape(raw_job_title)
        status_val = escape(raw_status)
    else:
        name = raw_name
        email_val = raw_email
        company_name = raw_company_name
        job_title = raw_job_title
        status_val = raw_status

    rendered = str(text)
    rendered = rendered.replace('{{name}}', name)
    rendered = rendered.replace('{{email}}', email_val)
    rendered = rendered.replace('{{company_name}}', company_name)
    rendered = rendered.replace('{{job_title}}', job_title)
    rendered = rendered.replace('{{status}}', status_val)

    # Clean up any leftover unknown placeholders like {{something_else}}
    rendered = re.sub(r'\{\{[a-zA-Z0-9_]+\}\}', '', rendered)
    return rendered


def get_daily_sent_email_count():
    """
    Returns count of email recipients delivered successfully today across all BulkMessages.
    """
    today = timezone.now().date()
    return MessageRecipient.objects.filter(
        channel='email',
        delivery_status='Sent',
        sent_at__date=today
    ).count()


def create_recipient_snapshots(bulk_message):
    """
    Resolves targets and creates MessageRecipient rows up front in 'Pending' status.
    Channels are truly selectable (Email, Dashboard, or both).
    """
    targets = resolve_recipients(
        bulk_message.audience_type,
        candidate_filter=bulk_message.candidate_filter,
        include_pending=getattr(bulk_message, 'include_pending', False),
        employer_ids=bulk_message.employer_ids,
        specific_candidate_ids=getattr(bulk_message, 'candidate_ids', None),
        job_id=getattr(bulk_message, 'job_id', None),
        company_id=getattr(bulk_message, 'company_id', None)
    )

    enable_sms_wa = getattr(settings, 'COMM_ENABLE_SMS_WHATSAPP', False)

    channels = [c for c in (bulk_message.channels or []) if c in ['dashboard', 'email', 'sms', 'whatsapp']]
    if not channels:
        channels = ['dashboard']

    if not enable_sms_wa:
        channels = [c for c in channels if c not in ['sms', 'whatsapp']]

    new_recipients = []
    seen_keys = set()

    for target in targets:
        is_candidate = isinstance(target, CandidateAccount)
        cand_acc = target if is_candidate else None
        emp_acc = target if not is_candidate else None

        for ch in channels:
            key = (bulk_message.id, cand_acc.id if cand_acc else None, emp_acc.id if emp_acc else None, ch)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            new_recipients.append(
                MessageRecipient(
                    bulk_message=bulk_message,
                    candidate_account=cand_acc,
                    employer_account=emp_acc,
                    channel=ch,
                    delivery_status='Pending',
                    error=''
                )
            )

    if new_recipients:
        MessageRecipient.objects.bulk_create(new_recipients, ignore_conflicts=True, batch_size=1000)

    created_recipients = list(bulk_message.recipients.all())
    recompute_bulk_message_status(bulk_message)
    return created_recipients


def build_branded_email_html(body_html, portal_url, site_url, attachment_name=None):
    """
    Constructs a professional table-based HTML email with SVG logo, CTA, and footer.
    """
    logo_url = f"{site_url}/static/images/logo/logo.png"

    attachment_badge_html = ""
    if attachment_name:
        attachment_badge_html = f"""
        <div style="margin-top: 18px; padding: 10px 14px; background-color: #f1f5f9; border-radius: 8px; border: 1px dashed #cbd5e1; font-size: 13px; color: #475569;">
            📎 <strong>Attachment:</strong> {escape(attachment_name)} (attached to this email)
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sky Vision Group</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #1e293b; background-color: #f8fafc; margin: 0; padding: 24px;">
    <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 620px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); overflow: hidden;">
        <!-- Header -->
        <tr>
            <td style="background-color: #0b1727; padding: 20px 28px; border-bottom: 3px solid #00d2d3;">
                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                    <tr>
                        <td align="left" valign="middle">
                            <span style="font-size: 19px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px;">SKY VISION GROUP</span>
                            <div style="font-size: 11px; color: #00d2d3; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-top: 2px;">Consultancy &amp; Human Resources</div>
                        </td>
                        <td align="right" valign="middle">
                            <img src="{logo_url}" alt="Sky Vision Group" width="46" height="46" style="border-radius: 6px; display: block; border: 0;" onerror="this.style.display='none';">
                        </td>
                    </tr>
                </table>
            </td>
        </tr>

        <!-- Main Body -->
        <tr>
            <td style="padding: 32px 28px; font-size: 15px; color: #334155; line-height: 1.75;">
                {body_html}
                {attachment_badge_html}

                <!-- CTA Button -->
                <table role="presentation" border="0" cellpadding="0" cellspacing="0" style="margin-top: 28px; margin-bottom: 8px;">
                    <tr>
                        <td align="center" style="border-radius: 8px; background-color: #2563eb;">
                            <a href="{portal_url}" target="_blank" style="font-size: 14px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 8px; display: inline-block; font-weight: 600;">
                                Open your Dashboard &rarr;
                            </a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>

        <!-- Footer -->
        <tr>
            <td style="background-color: #f8fafc; padding: 22px 28px; border-top: 1px solid #e2e8f0; font-size: 12px; color: #64748b; line-height: 1.6;">
                <p style="margin: 0 0 6px 0; font-weight: 600; color: #475569;">Sky Vision Group Consultancy</p>
                <p style="margin: 0 0 10px 0;">Official Recruitment, Staffing &amp; Corporate Training Solutions</p>
                <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 10px 0;">
                <p style="margin: 0; font-size: 11px; color: #94a3b8;">
                    You received this official notification as a registered member of Sky Vision Group.
                    You can manage email notifications in your portal profile settings.
                </p>
            </td>
        </tr>
    </table>
</body>
</html>"""


def send_single_email(connection, recipient_account, raw_subject, raw_body, attachment_file=None):
    """
    Sends a single email with connection reuse, subject newline stripping (capped at 150 chars),
    safe-HTML body rendering, clean plain-text fallback, optional attachment, and Reply-To header.
    """
    email_addr = getattr(recipient_account, 'email', '').strip()
    if not email_addr:
        raise ValidationError("Missing email address")

    validate_email(email_addr)

    is_candidate = isinstance(recipient_account, CandidateAccount)

    # 1. Subject formatting
    rendered_subject = render_placeholders(raw_subject, recipient_account, is_html=False)
    subj = rendered_subject.replace('\n', ' ').replace('\r', ' ').strip()
    if len(subj) > 150:
        subj = subj[:147] + "..."

    # 2. Body formatting (Safe HTML + Clean Plain Text)
    # Sanitize raw body first, then replace placeholders with escaped values
    sanitized_body = sanitize_html(raw_body)
    html_body_content = render_placeholders(sanitized_body, recipient_account, is_html=True)
    plain_body_content = render_placeholders(html_to_plain_text(sanitized_body), recipient_account, is_html=False)

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@skyvisiongroup.in')
    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
    portal_path = "/candidate/messages/" if is_candidate else "/employer/messages/"
    portal_url = f"{site_url}{portal_path}"

    plain_text = f"{plain_body_content}\n\n---\nSent via Sky Vision Group.\nYou can also view this message in your Portal Inbox: {portal_url}"

    attachment_name = os.path.basename(attachment_file.name) if attachment_file and hasattr(attachment_file, 'name') else None
    html_text = build_branded_email_html(html_body_content, portal_url, site_url, attachment_name=attachment_name)

    headers = {}
    reply_to = getattr(settings, 'COMM_REPLY_TO', '').strip()
    if reply_to:
        headers['Reply-To'] = reply_to

    msg = EmailMultiAlternatives(
        subject=subj,
        body=plain_text,
        from_email=from_email,
        to=[email_addr],
        headers=headers,
        connection=connection
    )
    msg.attach_alternative(html_text, "text/html")

    # Attach file if present
    if attachment_file:
        try:
            if hasattr(attachment_file, 'read'):
                pos = attachment_file.tell() if hasattr(attachment_file, 'tell') else 0
                content = attachment_file.read()
                if hasattr(attachment_file, 'seek'):
                    attachment_file.seek(pos)
                filename = os.path.basename(attachment_file.name)
                msg.attach(filename, content)
            elif hasattr(attachment_file, 'path') and os.path.exists(attachment_file.path):
                msg.attach_file(attachment_file.path)
        except Exception as attach_err:
            logger.warning(f"Failed to attach file to email: {attach_err}")

    msg.send()


def send_test_email(to_email, subject, body, recipient_name="Admin"):
    """
    Sends a test email to a specified address to verify SMTP setup.
    """
    try:
        email_addr = to_email.strip()
        if not email_addr:
            return False, "Test email address cannot be empty."

        validate_email(email_addr)

        dummy_cand = CandidateAccount(full_name=recipient_name, email=email_addr)
        conn = get_connection(timeout=getattr(settings, 'EMAIL_TIMEOUT', 20))
        conn.open()
        try:
            send_single_email(conn, dummy_cand, subject, body)
        finally:
            conn.close()

        backend_name = getattr(settings, 'EMAIL_BACKEND', '')
        if 'console' in backend_name.lower():
            return True, f"[Test Mode] Email simulated in terminal console. Real email was NOT sent because EMAIL_BACKEND is console. Please restart Django server after configuring .env."

        return True, f"Test email successfully sent to {email_addr} (Check Inbox & Spam folder)"

    except SMTPAuthenticationError:
        return False, "Gmail Authentication Failed: Check EMAIL_HOST_USER and App Password in .env."
    except ValidationError as ve:
        return False, f"Invalid email format: {str(ve)}"
    except Exception as e:
        return False, f"Email delivery error: {mask_sensitive_info(str(e))}"


def recompute_bulk_message_status(bulk_message):
    """
    Recomputes total_recipients, sent_count, failed_count, skipped_count, pending_count, and status.
    """
    all_recipients = bulk_message.recipients.all()
    total_count = all_recipients.count()
    sent_count = all_recipients.filter(delivery_status='Sent').count()
    failed_count = all_recipients.filter(delivery_status='Failed').count()
    skipped_count = all_recipients.filter(delivery_status='Skipped').count()
    pending_count = all_recipients.filter(delivery_status='Pending').count()

    bulk_message.total_recipients = total_count
    bulk_message.sent_count = sent_count
    bulk_message.failed_count = failed_count
    bulk_message.skipped_count = skipped_count
    bulk_message.pending_count = pending_count

    if bulk_message.status == 'Draft':
        pass
    elif bulk_message.is_stopped or bulk_message.status == 'Stopped':
        bulk_message.status = 'Stopped'
    elif bulk_message.status == 'Interrupted':
        bulk_message.status = 'Interrupted'
    elif pending_count == 0:
        if sent_count > 0 and failed_count == 0:
            bulk_message.status = 'Sent'
        elif sent_count > 0 and failed_count > 0:
            bulk_message.status = 'Partial'
        elif sent_count == 0 and failed_count > 0:
            bulk_message.status = 'Failed'
        elif bulk_message.stop_reason:
            bulk_message.status = 'Failed'
        elif total_count == 0:
            bulk_message.status = 'Failed'
        else:
            bulk_message.status = 'Sent'
    else:  # pending_count > 0
        if sent_count > 0:
            bulk_message.status = 'Partial'
        elif failed_count > 0 or bulk_message.stop_reason:
            bulk_message.status = 'Failed'
        else:
            bulk_message.status = 'Partial'

    bulk_message.save(update_fields=['total_recipients', 'sent_count', 'failed_count', 'skipped_count', 'pending_count', 'status'])
    cache.delete('comm_failed_delivery_count')


def check_stale_sending_messages():
    """
    Detects BulkMessages stuck in 'Sending' status with no activity for > 10 min and marks them 'Interrupted'.
    """
    stale_minutes = getattr(settings, 'COMM_STALE_SENDING_MINUTES', 10)
    cutoff = timezone.now() - timezone.timedelta(minutes=stale_minutes)

    stale_bm = BulkMessage.objects.filter(
        status='Sending'
    ).filter(
        Q(last_activity_at__lt=cutoff) | Q(last_activity_at__isnull=True, created_at__lt=cutoff)
    )

    interrupted_count = 0
    for bm in stale_bm:
        bm.status = 'Interrupted'
        bm.stop_reason = f"Execution interrupted (no activity for > {stale_minutes} minutes). Can be resumed via Retry / Resume."
        bm.save(update_fields=['status', 'stop_reason'])
        interrupted_count += 1

    return interrupted_count


def process_bulk_message_send(bulk_message_id, actor_name="Admin"):
    """
    Main worker execution loop for dispatching a BulkMessage with snapshot delivery,
    quota stop detection, deduplication, opt-out gating, transient error retries,
    heartbeat updates, atomic concurrency locking, and stop flag responsiveness.
    """
    lock_acquired = False
    try:
        # Atomic lock / state transition: only proceed if message is not already actively Sending
        updated = BulkMessage.objects.filter(
            id=bulk_message_id
        ).exclude(status='Sending').update(
            status='Sending',
            stop_reason='',
            is_stopped=False,
            last_activity_at=timezone.now()
        )
        if not updated:
            if not BulkMessage.objects.filter(id=bulk_message_id).exists():
                logger.error(f"BulkMessage {bulk_message_id} not found.")
                return
            logger.warning(f"BulkMessage {bulk_message_id} is already in 'Sending' status. Skipping concurrent execution.")
            return

        lock_acquired = True
        bulk_msg = BulkMessage.objects.get(id=bulk_message_id)

        if not bulk_msg.recipients.exists():
            create_recipient_snapshots(bulk_msg)

        pending_recipients = bulk_msg.recipients.filter(delivery_status='Pending')

        # 1. PROCESS DASHBOARD INBOX CHANNEL (Instant local delivery)
        dash_recipients = pending_recipients.filter(channel='dashboard')
        if dash_recipients.exists():
            if BulkMessage.objects.filter(id=bulk_msg.id, is_stopped=True).exists():
                bulk_msg.status = 'Stopped'
                bulk_msg.stop_reason = 'Stopped by admin'
                bulk_msg.save(update_fields=['status', 'stop_reason'])
                return

            dash_recipients.update(delivery_status='Sent', sent_at=timezone.now(), error='')

        # 2. PROCESS EMAIL CHANNEL
        email_recipients = pending_recipients.filter(channel='email').select_related(
            'candidate_account', 'employer_account'
        ).prefetch_related(
            'candidate_account__applications'
        )
        if email_recipients.exists():
            daily_limit = getattr(settings, 'COMM_EMAIL_DAILY_LIMIT', 400)
            daily_sent = get_daily_sent_email_count()

            batch_size = getattr(settings, 'COMM_EMAIL_BATCH_SIZE', 20)
            delay_sec = getattr(settings, 'COMM_EMAIL_DELAY_SECONDS', 1.0)
            timeout_sec = getattr(settings, 'EMAIL_TIMEOUT', 20)

            conn = get_connection(timeout=timeout_sec)
            auth_failed_halt = False
            quota_halt = False
            stopped_by_admin = False

            email_list = list(email_recipients)
            total_emails = len(email_list)
            seen_emails_in_run = set()

            for i in range(0, total_emails, batch_size):
                if auth_failed_halt or quota_halt or stopped_by_admin:
                    break

                # Check stop flag between batches
                if BulkMessage.objects.filter(id=bulk_msg.id, is_stopped=True).exists():
                    stopped_by_admin = True
                    bulk_msg.status = 'Stopped'
                    bulk_msg.stop_reason = 'Stopped by admin'
                    bulk_msg.save(update_fields=['status', 'stop_reason'])
                    break

                batch = email_list[i:i + batch_size]
                try:
                    conn.open()
                except SMTPAuthenticationError:
                    auth_failed_halt = True
                    bulk_msg.stop_reason = 'Gmail login failed. Check EMAIL_HOST_USER / App Password.'
                    bulk_msg.save(update_fields=['stop_reason'])
                    for mr in email_list[i:]:
                        mr.delivery_status = 'Failed'
                        mr.error = 'Gmail authentication failed'
                        mr.save(update_fields=['delivery_status', 'error'])
                    break
                except Exception as conn_err:
                    if is_quota_or_limit_error(conn_err):
                        quota_halt = True
                        bulk_msg.stop_reason = f"Gmail sending quota limit reached: {mask_sensitive_info(str(conn_err))}. Remaining emails can be sent tomorrow via Retry."
                        bulk_msg.save(update_fields=['stop_reason'])
                        break
                    logger.warning(f"Connection open error: {conn_err}")

                for mr in batch:
                    # Check stop flag per recipient
                    if BulkMessage.objects.filter(id=bulk_msg.id, is_stopped=True).exists():
                        stopped_by_admin = True
                        bulk_msg.status = 'Stopped'
                        bulk_msg.stop_reason = 'Stopped by admin'
                        bulk_msg.save(update_fields=['status', 'stop_reason'])
                        break

                    if daily_sent >= daily_limit:
                        quota_halt = True
                        bulk_msg.stop_reason = f"Gmail daily limit reached ({daily_limit}/day). Remaining emails can be sent tomorrow via Retry."
                        bulk_msg.save(update_fields=['stop_reason'])
                        break

                    target = mr.candidate_account or mr.employer_account
                    if not target:
                        mr.delivery_status = 'Skipped'
                        mr.error = 'Recipient target account missing'
                        mr.save(update_fields=['delivery_status', 'error'])
                        continue

                    # Opt-out check
                    if not getattr(target, 'email_notifications_enabled', True):
                        mr.delivery_status = 'Skipped'
                        mr.error = 'Recipient opted out of email notifications'
                        mr.save(update_fields=['delivery_status', 'error'])
                        continue

                    email_addr = getattr(target, 'email', '').strip().lower()
                    if not email_addr:
                        mr.delivery_status = 'Skipped'
                        mr.error = 'Missing email address'
                        mr.save(update_fields=['delivery_status', 'error'])
                        continue

                    if email_addr in seen_emails_in_run:
                        mr.delivery_status = 'Skipped'
                        mr.error = 'Duplicate email in this run'
                        mr.save(update_fields=['delivery_status', 'error'])
                        continue

                    seen_emails_in_run.add(email_addr)

                    # Send email with short retry loop for transient network glitches
                    success = False
                    last_error = None

                    for attempt in range(3):
                        try:
                            send_single_email(
                                conn,
                                target,
                                bulk_msg.subject,
                                bulk_msg.body,
                                attachment_file=bulk_msg.attachment
                            )
                            success = True
                            break
                        except SMTPAuthenticationError as auth_err:
                            auth_failed_halt = True
                            mr.delivery_status = 'Failed'
                            mr.error = 'Gmail authentication failed'
                            mr.save(update_fields=['delivery_status', 'error'])
                            bulk_msg.stop_reason = 'Gmail login failed. Check EMAIL_HOST_USER / App Password.'
                            bulk_msg.save(update_fields=['stop_reason'])
                            break
                        except SMTPRecipientsRefused:
                            mr.delivery_status = 'Failed'
                            mr.error = 'Recipient email address refused by mail server'
                            mr.save(update_fields=['delivery_status', 'error'])
                            break
                        except ValidationError as ve:
                            mr.delivery_status = 'Failed'
                            mr.error = f"Invalid email format: {str(ve)}"
                            mr.save(update_fields=['delivery_status', 'error'])
                            break
                        except Exception as exc:
                            if is_quota_or_limit_error(exc):
                                quota_halt = True
                                bulk_msg.stop_reason = f"Gmail quota/sending limit hit: {mask_sensitive_info(str(exc))}. Remaining emails kept Pending for Retry."
                                bulk_msg.save(update_fields=['stop_reason'])
                                break
                            last_error = exc
                            if attempt < 2:
                                time.sleep(0.5)

                    if auth_failed_halt or quota_halt or stopped_by_admin:
                        break

                    if success:
                        mr.delivery_status = 'Sent'
                        mr.sent_at = timezone.now()
                        mr.error = ''
                        mr.save(update_fields=['delivery_status', 'sent_at', 'error'])
                        daily_sent += 1
                    elif mr.delivery_status != 'Failed':
                        mr.delivery_status = 'Failed'
                        mr.error = mask_sensitive_info(str(last_error))
                        mr.save(update_fields=['delivery_status', 'error'])

                # Update heartbeat
                bulk_msg.last_activity_at = timezone.now()
                bulk_msg.save(update_fields=['last_activity_at'])

                try:
                    conn.close()
                except Exception:
                    pass

                if not auth_failed_halt and not quota_halt and not stopped_by_admin and (i + batch_size < total_emails):
                    time.sleep(delay_sec)

        # 3. PROCESS SMS & WHATSAPP CHANNELS (If enabled)
        enable_sms_wa = getattr(settings, 'COMM_ENABLE_SMS_WHATSAPP', False)

        sms_recipients = pending_recipients.filter(channel='sms')
        if sms_recipients.exists():
            if enable_sms_wa:
                sms_provider = get_sms_provider()
                for mr in sms_recipients:
                    target = mr.candidate_account or mr.employer_account
                    rendered_subj = render_placeholders(bulk_msg.subject, target)
                    rendered_body = render_placeholders(bulk_msg.body, target)
                    ok, err = sms_provider.send(target, rendered_body, rendered_subj)
                    if ok:
                        mr.delivery_status = 'Sent'
                        mr.sent_at = timezone.now()
                        mr.error = ''
                    else:
                        mr.delivery_status = 'Failed'
                        mr.error = err or 'SMS delivery failed'
                    mr.save()
            else:
                sms_recipients.update(delivery_status='Failed', error='SMS channel disabled in system settings')

        wa_recipients = pending_recipients.filter(channel='whatsapp')
        if wa_recipients.exists():
            if enable_sms_wa:
                wa_provider = get_whatsapp_provider()
                for mr in wa_recipients:
                    target = mr.candidate_account or mr.employer_account
                    rendered_subj = render_placeholders(bulk_msg.subject, target)
                    rendered_body = render_placeholders(bulk_msg.body, target)
                    ok, err = wa_provider.send(target, rendered_body, rendered_subj)
                    if ok:
                        mr.delivery_status = 'Sent'
                        mr.sent_at = timezone.now()
                        mr.error = ''
                    else:
                        mr.delivery_status = 'Failed'
                        mr.error = err or 'WhatsApp delivery failed'
                    mr.save()
            else:
                wa_recipients.update(delivery_status='Failed', error='WhatsApp channel disabled in system settings')

        log_activity(
            action_type="Bulk Message Sent",
            title=f"Bulk Message '{bulk_msg.title}' processed",
            description=f"Audience: {bulk_msg.audience_type} ({bulk_msg.candidate_filter})",
            actor=actor_name
        )

    except Exception as fatal_e:
        logger.exception(f"Worker crashed processing BulkMessage {bulk_message_id}: {fatal_e}")
        try:
            bm = BulkMessage.objects.get(id=bulk_message_id)
            bm.stop_reason = mask_sensitive_info(f"Worker crashed: {str(fatal_e)}")
            bm.save(update_fields=['stop_reason'])
        except Exception:
            pass

    finally:
        if lock_acquired:
            try:
                bm = BulkMessage.objects.get(id=bulk_message_id)
                recompute_bulk_message_status(bm)
            except Exception:
                pass
        connections.close_all()


def queue_bulk_message_send(bulk_message_id, actor_name="Admin", sync=False):
    """
    Enqueues or synchronously processes bulk message send execution.
    Only honors async thread when not running unit tests.
    """
    is_test = 'test' in sys.argv or any('test' in arg for arg in sys.argv)
    should_sync = sync or is_test

    if should_sync:
        process_bulk_message_send(bulk_message_id, actor_name=actor_name)
    else:
        thread = threading.Thread(
            target=process_bulk_message_send,
            args=(bulk_message_id,),
            kwargs={'actor_name': actor_name}
        )
        thread.daemon = True
        thread.start()
