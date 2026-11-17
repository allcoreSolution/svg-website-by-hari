import logging
import html
from django.core.mail import EmailMultiAlternatives
from django.core.cache import cache
from django.conf import settings
from apps.enquiries.models import log_activity

logger = logging.getLogger(__name__)


def _wrap_email_html(title, content_html, site_url):
    """Wraps body content in a responsive, branded Sky Vision HTML email template."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
</head>
<body style="margin: 0; padding: 24px 12px; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b;">
    <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
        <!-- Header -->
        <tr>
            <td style="background-color: #0b1727; padding: 24px 30px; border-bottom: 3px solid #00d2d3;">
                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                    <tr>
                        <td align="left" valign="middle">
                            <span style="font-size: 20px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px;">SKY VISION GROUP</span>
                            <div style="font-size: 11px; color: #00d2d3; font-weight: 600; text-transform: uppercase; letter-spacing: 1.2px; margin-top: 3px;">Consultancy &amp; Human Resources</div>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        <!-- Content -->
        <tr>
            <td style="padding: 32px 30px; font-size: 14px; line-height: 1.65; color: #334155;">
                {content_html}
            </td>
        </tr>
        <!-- Footer -->
        <tr>
            <td style="background-color: #f8fafc; padding: 20px 30px; border-top: 1px solid #e2e8f0; font-size: 12px; color: #64748b; line-height: 1.6;">
                <p style="margin: 0 0 4px 0; font-weight: 700; color: #334155;">Sky Vision Group of Consultancy</p>
                <p style="margin: 0 0 8px 0;">Official Recruitment, Staffing &amp; Corporate Training Solutions</p>
                <p style="margin: 0; font-size: 11px; color: #94a3b8;">
                    This is an official automated notification. If you have questions, please contact our support team at <a href="mailto:{getattr(settings, 'EMAIL_HOST_USER', 'support@skyvisiongroup.in')}" style="color: #2563eb; text-decoration: none;">{getattr(settings, 'EMAIL_HOST_USER', 'support@skyvisiongroup.in')}</a> or visit <a href="{site_url}" style="color: #2563eb; text-decoration: none;">{site_url}</a>.
                </p>
            </td>
        </tr>
    </table>
</body>
</html>"""


def notify_candidate_registered(candidate):
    """Email sent to candidate upon registration."""
    if not candidate or not candidate.email:
        return False

    # Prevent duplicate registration emails within 60 seconds
    cand_id = getattr(candidate, 'id', None)
    if cand_id:
        cache_key = f"candidate_registered_email_sent_{cand_id}"
        if cache.get(cache_key):
            logger.info(f"Duplicate registration email suppressed for candidate {cand_id} ({candidate.email})")
            return True
        cache.set(cache_key, True, timeout=60)

    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
    subject = "Candidate Registration Received - Pending Admin Approval | Sky Vision Consultancy"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Sky Vision Group <info@skyvisiongroup.in>')

    plain_message = (
        f"Dear {candidate.full_name},\n\n"
        f"Thank you for registering with Sky Vision Group of Consultancy.\n\n"
        f"Your candidate registration has been received and is currently PENDING ADMIN APPROVAL.\n\n"
        f"Once our administration team reviews and approves your account, you will receive an approval "
        f"email with your direct login link to start applying for jobs and tracking interview invitations.\n\n"
        f"Registered Details:\n"
        f"- Full Name: {candidate.full_name}\n"
        f"- Email: {candidate.email}\n"
        f"- Qualification: {candidate.qualification or 'Not specified'}\n\n"
        f"Best regards,\n"
        f"Sky Vision Team\n"
        f"{site_url}"
    )

    content_html = f"""
    <div style="margin-bottom: 20px;">
        <span style="background-color: #fef3c7; color: #b45309; border: 1px solid #fde68a; padding: 5px 14px; border-radius: 9999px; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; display: inline-block;">
            ⏳ Registration Under Review
        </span>
    </div>
    
    <h2 style="color: #0f172a; font-size: 20px; font-weight: 700; margin: 0 0 14px 0;">
        Thank you for registering, {html.escape(candidate.full_name)}!
    </h2>
    
    <p style="margin: 0 0 14px 0; font-size: 15px; color: #334155;">
        Your candidate registration has been received by Sky Vision Group of Consultancy.
    </p>
    
    <p style="margin: 0 0 20px 0; font-size: 14px; color: #475569;">
        Your account is currently <strong>pending admin approval</strong>. Once our administration team verifies your profile, you will receive an approval email notification and will be able to log in to apply for jobs and track your applications.
    </p>

    <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; margin: 20px 0; padding: 16px 20px;">
        <tr>
            <td colspan="2" style="padding-bottom: 10px; font-weight: 700; font-size: 13px; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #e2e8f0;">
                Submitted Details
            </td>
        </tr>
        <tr>
            <td style="padding: 10px 0 4px 0; font-size: 13px; color: #64748b; width: 140px;">Candidate Name:</td>
            <td style="padding: 10px 0 4px 0; font-size: 13px; font-weight: 600; color: #0f172a;">{html.escape(candidate.full_name)}</td>
        </tr>
        <tr>
            <td style="padding: 4px 0; font-size: 13px; color: #64748b;">Registered Email:</td>
            <td style="padding: 4px 0; font-size: 13px; font-weight: 600; color: #0f172a;">{html.escape(candidate.email)}</td>
        </tr>
        {f'<tr><td style="padding: 4px 0; font-size: 13px; color: #64748b;">Phone:</td><td style="padding: 4px 0; font-size: 13px; font-weight: 600; color: #0f172a;">{html.escape(candidate.phone)}</td></tr>' if candidate.phone else ''}
        {f'<tr><td style="padding: 4px 0; font-size: 13px; color: #64748b;">Qualification:</td><td style="padding: 4px 0; font-size: 13px; font-weight: 600; color: #0f172a;">{html.escape(candidate.qualification)}</td></tr>' if candidate.qualification else ''}
        <tr>
            <td style="padding: 4px 0; font-size: 13px; color: #64748b;">Current Status:</td>
            <td style="padding: 4px 0; font-size: 13px; font-weight: 700; color: #d97706;">Pending Admin Approval</td>
        </tr>
    </table>
    """

    html_message = _wrap_email_html("Candidate Registration Pending Review", content_html, site_url)

    try:
        msg = EmailMultiAlternatives(subject=subject, body=plain_message, from_email=from_email, to=[candidate.email])
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Sent candidate registration confirmation to {candidate.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send candidate registration email to {candidate.email}: {e}")
        return False


def notify_candidate_approved(candidate):
    """Email sent to candidate when approved by admin."""
    if not candidate or not candidate.email:
        return False

    # Prevent duplicate emails from being sent to the same candidate within 60 seconds
    cand_id = getattr(candidate, 'id', None)
    if cand_id:
        cache_key = f"candidate_approval_email_sent_{cand_id}"
        if cache.get(cache_key):
            logger.info(f"Duplicate approval email suppressed for candidate {cand_id} ({candidate.email})")
            return True
        cache.set(cache_key, True, timeout=60)

    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
    login_url = f"{site_url}/candidate/login/"
    subject = "Registration Approved - Continue to Sky Vision Portal"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Sky Vision Group <info@skyvisiongroup.in>')

    plain_message = (
        f"Dear {candidate.full_name},\n\n"
        f"Congratulations! Your candidate registration has been APPROVED by the Sky Vision admin team.\n\n"
        f"Your account is now fully active. You can now log in and continue to access your candidate portal to explore verified job openings, apply directly, and track interview invitations.\n\n"
        f"--- Account Details ---\n"
        f"Full Name: {candidate.full_name}\n"
        f"Registered Email: {candidate.email}\n"
        f"Qualification: {candidate.qualification or 'Registered Candidate'}\n"
        f"Account Status: Approved & Active\n\n"
        f"Click the link below to log in and continue:\n"
        f"{login_url}\n\n"
        f"Best regards,\n"
        f"Sky Vision Group of Consultancy\n"
        f"{site_url}"
    )

    content_html = f"""
    <div style="margin-bottom: 20px;">
        <span style="background-color: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; padding: 5px 14px; border-radius: 9999px; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; display: inline-block;">
            ✔ Registration Approved
        </span>
    </div>
    
    <h2 style="color: #0f172a; font-size: 20px; font-weight: 700; margin: 0 0 14px 0;">
        Welcome, {html.escape(candidate.full_name)}!
    </h2>
    
    <p style="margin: 0 0 14px 0; font-size: 15px; color: #334155;">
        Great news! Your candidate registration has been <strong>approved</strong> by the Sky Vision admin team.
    </p>
    
    <p style="margin: 0 0 20px 0; font-size: 14px; color: #475569;">
        Your account is now fully active. You can now log in and continue to access your candidate portal to explore verified job openings, apply directly, and track interview invitations.
    </p>

    <!-- Details Box -->
    <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; margin: 20px 0; padding: 16px 20px;">
        <tr>
            <td colspan="2" style="padding-bottom: 10px; font-weight: 700; font-size: 13px; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #e2e8f0;">
                Account Details
            </td>
        </tr>
        <tr>
            <td style="padding: 10px 0 4px 0; font-size: 13px; color: #64748b; width: 140px;">Candidate Name:</td>
            <td style="padding: 10px 0 4px 0; font-size: 13px; font-weight: 600; color: #0f172a;">{html.escape(candidate.full_name)}</td>
        </tr>
        <tr>
            <td style="padding: 4px 0; font-size: 13px; color: #64748b;">Registered Email:</td>
            <td style="padding: 4px 0; font-size: 13px; font-weight: 600; color: #0f172a;">{html.escape(candidate.email)}</td>
        </tr>
        {f'<tr><td style="padding: 4px 0; font-size: 13px; color: #64748b;">Phone:</td><td style="padding: 4px 0; font-size: 13px; font-weight: 600; color: #0f172a;">{html.escape(candidate.phone)}</td></tr>' if candidate.phone else ''}
        {f'<tr><td style="padding: 4px 0; font-size: 13px; color: #64748b;">Qualification:</td><td style="padding: 4px 0; font-size: 13px; font-weight: 600; color: #0f172a;">{html.escape(candidate.qualification)}</td></tr>' if candidate.qualification else ''}
        <tr>
            <td style="padding: 4px 0; font-size: 13px; color: #64748b;">Account Status:</td>
            <td style="padding: 4px 0; font-size: 13px; font-weight: 700; color: #16a34a;">Approved &amp; Active</td>
        </tr>
    </table>

    <!-- CTA Button -->
    <table role="presentation" border="0" cellpadding="0" cellspacing="0" style="margin: 26px 0 24px 0;">
        <tr>
            <td align="center" style="border-radius: 8px; background-color: #2563eb;">
                <a href="{login_url}" target="_blank" style="display: inline-block; padding: 13px 28px; font-size: 15px; font-weight: 700; color: #ffffff; text-decoration: none; border-radius: 8px; letter-spacing: 0.3px;">
                    Login to Continue &rarr;
                </a>
            </td>
        </tr>
    </table>

    <p style="margin: 0 0 6px 0; font-size: 13px; font-weight: 600; color: #334155;">What you can do next:</p>
    <ul style="margin: 0 0 20px 0; padding-left: 20px; font-size: 13px; color: #64748b; line-height: 1.6;">
        <li>Complete your profile and upload your updated CV/resume</li>
        <li>Browse and apply for verified corporate job openings</li>
        <li>Receive interview updates and direct tracking status</li>
    </ul>

    <p style="margin: 0; font-size: 12px; color: #94a3b8;">
        Direct link: <a href="{login_url}" style="color: #2563eb; text-decoration: underline;">{login_url}</a>
    </p>
    """

    html_message = _wrap_email_html("Candidate Registration Approved", content_html, site_url)

    try:
        msg = EmailMultiAlternatives(subject=subject, body=plain_message, from_email=from_email, to=[candidate.email])
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Successfully sent candidate approval email to {candidate.email}")
        log_activity(
            action_type="Email Sent",
            title=f"Approval email sent to candidate '{candidate.full_name}'",
            description=f"Registration approval email sent to {candidate.email}."
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send candidate approval email to {candidate.email}: {e}")
        return False


def notify_candidate_rejected(candidate, reason=""):
    """Email sent to candidate when rejected by admin."""
    if not candidate or not candidate.email:
        return False

    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
    subject = "Candidate Registration Status - Sky Vision Group of Consultancy"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Sky Vision Group <info@skyvisiongroup.in>')
    reason_text = f"\nReason: {reason}\n" if reason else ""

    plain_message = (
        f"Dear {candidate.full_name},\n\n"
        f"We regret to inform you that your registration request with Sky Vision Group of Consultancy was not approved at this time.{reason_text}\n"
        f"If you believe this is an error or have questions, please contact our support team.\n\n"
        f"Best regards,\n"
        f"Sky Vision Team\n"
        f"{site_url}"
    )

    reason_box = f"""
    <div style="background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 12px 16px; margin: 16px 0; font-size: 13px; color: #991b1b;">
        <strong>Reason provided:</strong> {html.escape(reason)}
    </div>
    """ if reason else ""

    content_html = f"""
    <div style="margin-bottom: 20px;">
        <span style="background-color: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; padding: 5px 14px; border-radius: 9999px; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; display: inline-block;">
            Registration Not Approved
        </span>
    </div>
    
    <h2 style="color: #0f172a; font-size: 20px; font-weight: 700; margin: 0 0 14px 0;">
        Dear {html.escape(candidate.full_name)},
    </h2>
    
    <p style="margin: 0 0 14px 0; font-size: 15px; color: #334155;">
        We regret to inform you that your candidate registration request was not approved at this time.
    </p>

    {reason_box}

    <p style="margin: 16px 0; font-size: 14px; color: #475569;">
        If you have questions or believe this was an error, please contact our support team for further assistance.
    </p>
    """

    html_message = _wrap_email_html("Candidate Registration Status", content_html, site_url)

    try:
        msg = EmailMultiAlternatives(subject=subject, body=plain_message, from_email=from_email, to=[candidate.email])
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Sent candidate rejection email to {candidate.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send candidate rejection email to {candidate.email}: {e}")
        return False


def notify_applicant_status_change(applicant, old_status, new_status, notes=""):
    """Email sent to candidate when their job application status changes."""
    if not applicant or not applicant.email:
        return False

    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
    subject = f"Application Status Update: {applicant.job_title} - {new_status}"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Sky Vision Group <info@skyvisiongroup.in>')
    notes_text = f"\nNotes: {notes}\n" if notes else ""
    portal_url = f"{site_url}/candidate/applied-jobs/"

    plain_message = (
        f"Dear {applicant.full_name},\n\n"
        f"Your application status for the role '{applicant.job_title}' has been updated to: {new_status}.\n"
        f"{notes_text}\n"
        f"You can track your application progress in your Candidate Dashboard:\n"
        f"{portal_url}\n\n"
        f"Best regards,\n"
        f"Sky Vision Team\n"
        f"{site_url}"
    )

    notes_box = f"""
    <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px; margin: 16px 0; font-size: 13px; color: #334155;">
        <strong>Notes from recruiter:</strong> {html.escape(notes)}
    </div>
    """ if notes else ""

    content_html = f"""
    <h2 style="color: #0f172a; font-size: 20px; font-weight: 700; margin: 0 0 14px 0;">
        Dear {html.escape(applicant.full_name)},
    </h2>
    
    <p style="margin: 0 0 14px 0; font-size: 15px; color: #334155;">
        Your application status for the role <strong>{html.escape(applicant.job_title)}</strong> has been updated to: <span style="font-weight: 700; color: #2563eb;">{html.escape(new_status)}</span>.
    </p>

    {notes_box}

    <p style="margin: 20px 0;">
        <a href="{portal_url}" target="_blank" style="display: inline-block; padding: 11px 22px; font-size: 14px; font-weight: 600; color: #ffffff; background-color: #2563eb; text-decoration: none; border-radius: 6px;">
            View Applied Jobs &rarr;
        </a>
    </p>
    """

    html_message = _wrap_email_html("Application Status Update", content_html, site_url)

    try:
        msg = EmailMultiAlternatives(subject=subject, body=plain_message, from_email=from_email, to=[applicant.email])
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Sent applicant status update email to {applicant.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send application status update email to {applicant.email}: {e}")
        return False


def notify_interview_scheduled(interview):
    """Email sent to candidate when an interview is scheduled or rescheduled."""
    if not interview or not interview.candidate_email:
        return False

    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
    subject = f"Interview Scheduled: {interview.job_title or 'Job Application'}"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Sky Vision Group <info@skyvisiongroup.in>')
    location_info = f"\nLocation/Link: {interview.location_or_link}" if interview.location_or_link else ""

    plain_message = (
        f"Dear {interview.candidate_name},\n\n"
        f"An interview has been scheduled for your application ({interview.job_title or 'Job Application'}).\n\n"
        f"Interview Details:\n"
        f"- Date: {interview.interview_date}\n"
        f"- Time: {interview.interview_time}\n"
        f"- Mode: {interview.interview_mode}{location_info}\n\n"
        f"Please make sure to log in to your candidate portal for updates.\n\n"
        f"Best regards,\n"
        f"Sky Vision Team\n"
        f"{site_url}"
    )

    content_html = f"""
    <h2 style="color: #0f172a; font-size: 20px; font-weight: 700; margin: 0 0 14px 0;">
        Dear {html.escape(interview.candidate_name)},
    </h2>
    
    <p style="margin: 0 0 14px 0; font-size: 15px; color: #334155;">
        An interview has been scheduled for your application for <strong>{html.escape(interview.job_title or 'Job Application')}</strong>.
    </p>

    <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; margin: 20px 0; padding: 16px 20px;">
        <tr>
            <td style="padding: 6px 0; font-size: 13px; color: #64748b; width: 140px;">📅 Date:</td>
            <td style="padding: 6px 0; font-size: 13px; font-weight: 600; color: #0f172a;">{interview.interview_date}</td>
        </tr>
        <tr>
            <td style="padding: 6px 0; font-size: 13px; color: #64748b;">⏰ Time:</td>
            <td style="padding: 6px 0; font-size: 13px; font-weight: 600; color: #0f172a;">{interview.interview_time}</td>
        </tr>
        <tr>
            <td style="padding: 6px 0; font-size: 13px; color: #64748b;">📍 Mode:</td>
            <td style="padding: 6px 0; font-size: 13px; font-weight: 600; color: #0f172a;">{html.escape(str(interview.interview_mode))}</td>
        </tr>
        {f'<tr><td style="padding: 6px 0; font-size: 13px; color: #64748b;">🔗 Venue/Link:</td><td style="padding: 6px 0; font-size: 13px; font-weight: 600; color: #0f172a;">{html.escape(str(interview.location_or_link))}</td></tr>' if interview.location_or_link else ''}
    </table>

    <p style="margin: 20px 0;">
        <a href="{site_url}/candidate/applied-jobs/" target="_blank" style="display: inline-block; padding: 11px 22px; font-size: 14px; font-weight: 600; color: #ffffff; background-color: #2563eb; text-decoration: none; border-radius: 6px;">
            Open Candidate Portal &rarr;
        </a>
    </p>
    """

    html_message = _wrap_email_html("Interview Scheduled", content_html, site_url)

    try:
        msg = EmailMultiAlternatives(subject=subject, body=plain_message, from_email=from_email, to=[interview.candidate_email])
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Sent interview scheduled email to {interview.candidate_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send interview scheduled email to {interview.candidate_email}: {e}")
        return False

