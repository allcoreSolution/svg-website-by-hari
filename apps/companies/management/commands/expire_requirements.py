from django.core.management.base import BaseCommand
from apps.companies.views import sync_expired_requirements

class Command(BaseCommand):
    help = "Sync company requirements status to Expired if application deadline date has passed."

    def handle(self, *args, **options):
        expired_count = sync_expired_requirements()
        self.stdout.write(self.style.SUCCESS(f"Successfully updated {expired_count} expired requirements."))
