import socket
from smtplib import SMTPAuthenticationError, SMTPException
from django.core.management.base import BaseCommand
from django.core.mail import get_connection
from django.conf import settings
from apps.communication.services import mask_sensitive_info


class Command(BaseCommand):
    help = "Verifies SMTP connectivity and credentials without sending an email."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== Sky Vision Group - Email Setup Verification ==="))

        backend = getattr(settings, 'EMAIL_BACKEND', '')
        host = getattr(settings, 'EMAIL_HOST', '')
        port = getattr(settings, 'EMAIL_PORT', 587)
        use_tls = getattr(settings, 'EMAIL_USE_TLS', True)
        user = getattr(settings, 'EMAIL_HOST_USER', '')
        has_password = bool(getattr(settings, 'EMAIL_HOST_PASSWORD', ''))
        site_url = getattr(settings, 'SITE_URL', '')
        is_debug = getattr(settings, 'DEBUG', False)
        timeout = getattr(settings, 'EMAIL_TIMEOUT', 20)

        # 1. Print configuration summary (Password ALWAYS masked)
        self.stdout.write(f"EMAIL_BACKEND       : {backend}")
        self.stdout.write(f"EMAIL_HOST          : {host}")
        self.stdout.write(f"EMAIL_PORT          : {port}")
        self.stdout.write(f"EMAIL_USE_TLS       : {use_tls}")
        self.stdout.write(f"EMAIL_HOST_USER     : {user if user else '(not set)'}")
        self.stdout.write(f"EMAIL_HOST_PASSWORD : {'******' if has_password else '(not set)'}")
        self.stdout.write(f"DEFAULT_FROM_EMAIL  : {getattr(settings, 'DEFAULT_FROM_EMAIL', '')}")
        self.stdout.write(f"COMM_REPLY_TO       : {getattr(settings, 'COMM_REPLY_TO', '') or '(not set)'}")
        self.stdout.write(f"SITE_URL            : {site_url}")
        self.stdout.write(f"DEBUG               : {is_debug}")
        self.stdout.write("")

        # 2. Check SITE_URL for production
        if not is_debug and ('127.0.0.1' in site_url or 'localhost' in site_url):
            self.stdout.write(self.style.WARNING(
                f"[WARNING] SITE_URL is set to a local address ({site_url}) while DEBUG=False!\n"
                f"          Portal links and images in outbound emails will point to localhost.\n"
                f"          Update SITE_URL in .env to your live production domain (e.g. https://skyvisiongroup.in).\n"
            ))

        # 3. Check credentials presence
        if not user or not has_password:
            self.stdout.write(self.style.WARNING(
                "[NOTICE] Running in Test/Console Mode: EMAIL_HOST_USER and/or EMAIL_HOST_PASSWORD is not set in .env.\n"
                "         Outgoing emails will be written to stdout/console rather than dispatched over SMTP.\n"
                "         To configure real sending, follow instructions in SETUP_GMAIL.md.\n"
            ))
            return

        if backend != 'django.core.mail.backends.smtp.EmailBackend':
            self.stdout.write(self.style.WARNING(
                f"[WARNING] EMAIL_BACKEND is '{backend}' instead of django.core.mail.backends.smtp.EmailBackend.\n"
            ))

        # 4. Attempt real SMTP handshake & authentication (WITHOUT sending email)
        self.stdout.write("Testing SMTP handshake and credentials...")
        try:
            conn = get_connection(
                backend='django.core.mail.backends.smtp.EmailBackend',
                fail_silently=False,
                timeout=timeout
            )
            conn.open()
            conn.close()

            self.stdout.write(self.style.SUCCESS(
                f"\n[OK] SMTP Connection & Authentication SUCCESSFUL!\n"
                f"     Host        : {host}:{port}\n"
                f"     User        : {user}\n"
                f"     Encryption  : STARTTLS\n"
                f"     Status      : Gmail SMTP credentials verified and ready for outbound sending."
            ))
        except SMTPAuthenticationError as auth_err:
            self.stdout.write(self.style.ERROR(
                f"\n[ERROR] SMTP Authentication Failed (535 5.7.8): Username and password not accepted.\n"
                f"        Details : {mask_sensitive_info(str(auth_err))}\n"
                f"        Fix     : 1. Ensure 2-Step Verification is enabled in your Google Account.\n"
                f"                  2. Generate a dedicated 16-character App Password at https://myaccount.google.com/apppasswords.\n"
                f"                  3. Set EMAIL_HOST_PASSWORD=<16-char-code> in skyvision/.env."
            ))
        except (socket.timeout, TimeoutError) as t_err:
            self.stdout.write(self.style.ERROR(
                f"\n[ERROR] SMTP Connection Timed Out after {timeout} seconds.\n"
                f"        Details : {mask_sensitive_info(str(t_err))}\n"
                f"        Fix     : Check server outbound network connectivity to {host}:{port}. Ensure firewall is not blocking port {port}."
            ))
        except ConnectionRefusedError as cr_err:
            self.stdout.write(self.style.ERROR(
                f"\n[ERROR] SMTP Connection Refused.\n"
                f"        Details : {mask_sensitive_info(str(cr_err))}\n"
                f"        Fix     : Server rejected connection on {host}:{port}. Verify EMAIL_HOST and EMAIL_PORT settings."
            ))
        except SMTPException as smtp_err:
            self.stdout.write(self.style.ERROR(
                f"\n[ERROR] SMTP Protocol Error.\n"
                f"        Details : {mask_sensitive_info(str(smtp_err))}"
            ))
        except Exception as exc:
            self.stdout.write(self.style.ERROR(
                f"\n[ERROR] Unexpected error connecting to mail server.\n"
                f"        Details : {mask_sensitive_info(str(exc))}"
            ))
