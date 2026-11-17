from django.core.management.base import BaseCommand
from django.utils import timezone
import datetime
from apps.enquiries.models import SubmissionThrottle

class Command(BaseCommand):
    help = "Purge submission throttles older than 7 days"

    def handle(self, *args, **options):
        cutoff = timezone.now() - datetime.timedelta(days=7)
        deleted_count, _ = SubmissionThrottle.objects.filter(timestamp__lt=cutoff).delete()
        self.stdout.write(self.style.SUCCESS(f"Successfully purged {deleted_count} expired submission throttles."))
