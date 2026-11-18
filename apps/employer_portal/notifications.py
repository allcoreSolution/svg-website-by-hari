import logging
import html
import threading
from django.core.mail import EmailMultiAlternatives
from django.core.cache import cache
from django.conf import settings
from apps.enquiries.models import log_activity

logger = logging.getLogger(__name__)

def _send_email_async(msg):
    def _runner():
        try:
            msg.send(fail_silently=True)
        except Exception as e:
            logger.warning(f"Async email sending error: {e}")
    threading.Thread(target=_runner, daemon=True).start()


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


def notify_employer_registered(employer):
    """Email sent to employer upon registration."""
    if not employer or not employer.email:
        return False

    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
    subject = "Employer Registration Received - Pending Admin Approval | Sky Vision Consultancy"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Sky Vision Group <info@skyvisiongroup.in>')

    plain_message = (
        f"Dear {employer.contact_name},\n\n"
        f"Thank you for registering {employer.company_name} on Sky Vision Group of Consultancy.\n\n"
        f"Your registration has been received and is currently PENDING ADMIN APPROVAL.\n\n"
        f"Our administration team is reviewing your company details. Once approved, you will receive "
        f"an email notification with your portal login link so you can continue, post job vacancies, and review candidate applications.\n\n"
        f"Registered Details:\n"
        f"- Company: {employer.company_name}\n"
        f"- Contact: {employer.contact_name}\n"
        f"- Email: {employer.email}\n\n"
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
        Thank you for registering, {html.escape(employer.contact_name)}!
    </h2>
    
    <p style="margin: 0 0 14px 0; font-size: 15px; color: #334155;">
        We have received the registration for <strong>{html.escape(employer.company_name)}</strong> on Sky Vision Group of Consultancy.
    </p>
    
    <p style="margin: 0 0 20px 0; font-size: 14px; color: #475569;">
        Your employer account is currently <strong>pending admin approval</strong>. Our team is verifying your registration details. As soon as your account is approved, you will receive an approval email with your direct link to log in and continue.
    </p>

    <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; margin: 20px 0; padding: 16px 20px;">
        <tr>
            <td colspan="2" style="padding-bottom: 10px; font-weight: 700; font-size: 13px; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #e2e8f0;">
                Submitted Details
            </td>
        </tr>
        <tr>
            <td style="padding: 10px 0 4px 0; font-size: 13px; color: #64748b; width: 140px;">Company Name:</td>
            <td style="padding: 10px 0 4px 0; font-size: 13px; font-weight: 600; color: #0f172a;">{html.escape(employer.company_name)}</td>
        </tr>
        <tr>
            <td style="padding: 4px 0; font-size: 13px; color: #64748b;">Contact Person:</td>
            <td style="padding: 4px 0; font-size: 13px; font-weight: 600; color: #0f172a;">{html.escape(employer.contact_name)}</td>
        </tr>
        <tr>
            <td style="padding: 4px 0; font-size: 13px; color: #64748b;">Registered Email:</td>
            <td style="padding: 4px 0; font-size: 13px; font-weight: 600; color: #0f172a;">{html.escape(employer.email)}</td>
        </tr>
        <tr>
            <td style="padding: 4px 0; font-size: 13px; color: #64748b;">Current Status:</td>
            <td style="padding: 4px 0; font-size: 13px; font-weight: 700; color: #d97706;">Pending Admin Approval</td>
        </tr>
    </table>
    """

    html_message = _wrap_email_html("Employer Registration Pending Review", content_html, site_url)

    try:
        msg = EmailMultiAlternatives(subject=subject, body=plain_message, from_email=from_email, to=[employer.email])
        msg.attach_alternative(html_message, "text/html")
        _send_email_async(msg)
        logger.info(f"Queued employer registration confirmation to {employer.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send employer registration email to {employer.email}: {e}")
        return False


def notify_employer_approved(employer):
    """Email sent to employer when approved by admin."""
    if not employer or not employer.email:
        return False

    # Prevent duplicate approval emails within 60 seconds
    emp_id = getattr(employer, 'id', None)
    if emp_id:
        cache_key = f"employer_approval_email_sent_{emp_id}"
        if cache.get(cache_key):
            logger.info(f"Duplicate approval email suppressed for employer {emp_id} ({employer.email})")
            return True
        cache.set(cache_key, True, timeout=60)

    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
    login_url = f"{site_url}/employer/login/"
    subject = "Registration Approved - Continue to Sky Vision Portal"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Sky Vision Group <info@skyvisiongroup.in>')

    plain_message = (
        f"Dear {employer.contact_name},\n\n"
        f"Congratulations! Your employer registration for '{employer.company_name}' has been APPROVED by the Sky Vision admin team.\n\n"
        f"Your account is now fully active. You can now log in and continue to access your employer portal to post job requirements, review candidate applications, and hire talent.\n\n"
        f"--- Account Details ---\n"
        f"Company Name: {employer.company_name}\n"
        f"Contact Person: {employer.contact_name}\n"
        f"Registered Email: {employer.email}\n"
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
        Welcome, {html.escape(employer.contact_name)}!
    </h2>
    
    <p style="margin: 0 0 14px 0; font-size: 15px; color: #334155;">
        Great news! Your employer registration for <strong>{html.escape(employer.company_name)}</strong> has been <strong>approved</strong> by the Sky Vision admin team.
    </p>
    
    <p style="margin: 0 0 20px 0; font-size: 14px; color: #475569;">
        Your account is now active. You can now log in and continue to access your employer portal to post job vacancies, manage applicants, and hire talent.
    </p>

    <!-- Details Box -->
    <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; margin: 20px 0; padding: 16px 20px;">
        <tr>
            <td colspan="2" style="padding-bottom: 10px; font-weight: 700; font-size: 13px; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #e2e8f0;">
                Account Details
            </td>
        </tr>
        <tr>
            <td style="padding: 10px 0 4px 0; font-size: 13px; color: #64748b; width: 140px;">Company Name:</td>
            <td style="padding: 10px 0 4px 0; font-size: 13px; font-weight: 600; color: #0f172a;">{html.escape(employer.company_name)}</td>
        </tr>
        <tr>
            <td style="padding: 4px 0; font-size: 13px; color: #64748b;">Contact Person:</td>
            <td style="padding: 4px 0; font-size: 13px; font-weight: 600; color: #0f172a;">{html.escape(employer.contact_name)}</td>
        </tr>
        <tr>
            <td style="padding: 4px 0; font-size: 13px; color: #64748b;">Registered Email:</td>
            <td style="padding: 4px 0; font-size: 13px; font-weight: 600; color: #0f172a;">{html.escape(employer.email)}</td>
        </tr>
        {f'<tr><td style="padding: 4px 0; font-size: 13px; color: #64748b;">Phone:</td><td style="padding: 4px 0; font-size: 13px; font-weight: 600; color: #0f172a;">{html.escape(employer.phone)}</td></tr>' if employer.phone else ''}
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
        <li>Post new job vacancies and requirement criteria</li>
        <li>Browse pre-screened and qualified candidate profiles</li>
        <li>Review applications and schedule interviews directly</li>
    </ul>

    <p style="margin: 0; font-size: 12px; color: #94a3b8;">
        Direct link: <a href="{login_url}" style="color: #2563eb; text-decoration: underline;">{login_url}</a>
    </p>
    """

    html_message = _wrap_email_html("Employer Registration Approved", content_html, site_url)

    try:
        msg = EmailMultiAlternatives(subject=subject, body=plain_message, from_email=from_email, to=[employer.email])
        msg.attach_alternative(html_message, "text/html")
        _send_email_async(msg)
        logger.info(f"Successfully sent employer approval email to {employer.email}")
        log_activity(
            action_type="Email Sent",
            title=f"Approval email sent to employer '{employer.company_name}'",
            description=f"Registration approval email sent to {employer.email}."
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send employer approval email to {employer.email}: {e}")
        return False


def notify_employer_rejected(employer, reason=""):
    """Email sent to employer when rejected by admin."""
    if not employer or not employer.email:
        return False

    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
    subject = "Employer Registration Status - Sky Vision Group of Consultancy"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Sky Vision Group <info@skyvisiongroup.in>')
    reason_text = f"\nReason: {reason}\n" if reason else ""

    plain_message = (
        f"Dear {employer.contact_name},\n\n"
        f"We regret to inform you that your employer registration request for '{employer.company_name}' was not approved at this time.{reason_text}\n"
        f"If you believe this is an error or wish to provide updated verification details, please contact our support team.\n\n"
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
        Dear {html.escape(employer.contact_name)},
    </h2>
    
    <p style="margin: 0 0 14px 0; font-size: 15px; color: #334155;">
        We regret to inform you that your employer registration request for <strong>{html.escape(employer.company_name)}</strong> was not approved at this time.
    </p>

    {reason_box}

    <p style="margin: 16px 0; font-size: 14px; color: #475569;">
        If you believe this decision was made in error or if you would like to provide updated documentation or verification details, please feel free to reach out to our support desk.
    </p>
    """

    html_message = _wrap_email_html("Employer Registration Status", content_html, site_url)

    try:
        msg = EmailMultiAlternatives(subject=subject, body=plain_message, from_email=from_email, to=[employer.email])
        msg.attach_alternative(html_message, "text/html")
        _send_email_async(msg)
        logger.info(f"Sent employer rejection email to {employer.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send employer rejection email to {employer.email}: {e}")
        return False


def notify_employer_suspended(employer, reason=""):
    """Email sent to employer when account is suspended/revoked."""
    if not employer or not employer.email:
        return False

    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
    subject = "Employer Account Notice - Sky Vision Group of Consultancy"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Sky Vision Group <info@skyvisiongroup.in>')
    reason_text = f"\nReason: {reason}\n" if reason else ""

    plain_message = (
        f"Dear {employer.contact_name},\n\n"
        f"Your employer account access for '{employer.company_name}' has been suspended by administration.{reason_text}\n"
        f"Any active job listings have been temporarily hidden. Please contact Sky Vision administration if you have questions.\n\n"
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
            Account Suspended
        </span>
    </div>
    
    <h2 style="color: #0f172a; font-size: 20px; font-weight: 700; margin: 0 0 14px 0;">
        Dear {html.escape(employer.contact_name)},
    </h2>
    
    <p style="margin: 0 0 14px 0; font-size: 15px; color: #334155;">
        Your employer account access for <strong>{html.escape(employer.company_name)}</strong> has been suspended by administration.
    </p>

    {reason_box}

    <p style="margin: 16px 0; font-size: 14px; color: #475569;">
        Any active job postings associated with your account have been temporarily hidden. Please contact Sky Vision administration to discuss account reactivation.
    </p>
    """

    html_message = _wrap_email_html("Employer Account Notice", content_html, site_url)

    try:
        msg = EmailMultiAlternatives(subject=subject, body=plain_message, from_email=from_email, to=[employer.email])
        msg.attach_alternative(html_message, "text/html")
        _send_email_async(msg)
        logger.info(f"Sent employer suspension email to {employer.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send employer suspension email to {employer.email}: {e}")
        return False


def notify_job_status_change(job, old_status, new_status, reason=""):
    """Email sent to employer when job approval status changes."""
    if not job or not job.employer or not job.employer.email:
        return False

    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
    subject = f"Job Posting Update: {job.title} - {new_status}"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Sky Vision Group <info@skyvisiongroup.in>')
    reason_text = f"\nDetails: {reason}\n" if reason else ""

    plain_message = (
        f"Dear {job.employer.contact_name},\n\n"
        f"The status of your job posting for '{job.title}' has been updated to: {new_status}.{reason_text}\n"
        f"You can view and manage your job listings at:\n"
        f"{site_url}/employer/jobs/\n\n"
        f"Best regards,\n"
        f"Sky Vision Team\n"
        f"{site_url}"
    )

    reason_box = f"""
    <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px; margin: 16px 0; font-size: 13px; color: #334155;">
        <strong>Details:</strong> {html.escape(reason)}
    </div>
    """ if reason else ""

    content_html = f"""
    <h2 style="color: #0f172a; font-size: 20px; font-weight: 700; margin: 0 0 14px 0;">
        Dear {html.escape(job.employer.contact_name)},
    </h2>
    
    <p style="margin: 0 0 14px 0; font-size: 15px; color: #334155;">
        The status of your job posting for <strong>{html.escape(job.title)}</strong> has been updated to: <span style="font-weight: 700; color: #2563eb;">{html.escape(new_status)}</span>.
    </p>

    {reason_box}

    <p style="margin: 20px 0;">
        <a href="{site_url}/employer/jobs/" target="_blank" style="display: inline-block; padding: 11px 22px; font-size: 14px; font-weight: 600; color: #ffffff; background-color: #2563eb; text-decoration: none; border-radius: 6px;">
            View Job Listings &rarr;
        </a>
    </p>
    """

    html_message = _wrap_email_html("Job Posting Status Update", content_html, site_url)

    try:
        msg = EmailMultiAlternatives(subject=subject, body=plain_message, from_email=from_email, to=[job.employer.email])
        msg.attach_alternative(html_message, "text/html")
        _send_email_async(msg)
        logger.info(f"Sent job status update email to {job.employer.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send job status update email for {job.title}: {e}")
        return False

