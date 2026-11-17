from django.core.management.base import BaseCommand, CommandError
from apps.communication.services import send_test_email


class Command(BaseCommand):
    help = "Dispatches a branded test email to verify real outbound SMTP deliverability."

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            required=True,
            help="Recipient email address to send the test message to."
        )
        parser.add_argument(
            '--subject',
            type=str,
            default="Sky Vision Group — SMTP Delivery Test",
            help="Subject line of the test email."
        )
        parser.add_argument(
            '--body',
            type=str,
            default="This is a live transactional test email from Sky Vision Group Consultancy verifying outbound deliverability, HTML email formatting, and button links.",
            help="Body content of the test email."
        )

    def handle(self, *args, **options):
        to_email = options['to'].strip()
        subject = options['subject'].strip()
        body = options['body'].strip()

        self.stdout.write(self.style.MIGRATE_HEADING("=== Sending Test Email ==="))
        self.stdout.write(f"To      : {to_email}")
        self.stdout.write(f"Subject : {subject}")
        self.stdout.write("Dispatching email...")

        success, message = send_test_email(to_email, subject, body, recipient_name="Administrator")

        if success:
            self.stdout.write(self.style.SUCCESS(f"\n[OK] {message}"))
            self.stdout.write("Please check the recipient's Inbox (and Spam/Junk folder if sending to an external address).")
        else:
            self.stdout.write(self.style.ERROR(f"\n[FAILED] {message}"))
            raise CommandError(f"Test email dispatch failed: {message}")
