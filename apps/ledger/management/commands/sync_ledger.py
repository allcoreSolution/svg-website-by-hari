from django.core.management.base import BaseCommand
from django.db import models
from apps.candidates.models import Applicant
from apps.placements.models import Placement
from apps.ledger.services import ensure_commission_for_joined


class Command(BaseCommand):
    help = "Backfill ledger commissions for all already-joined candidates and placements."

    def handle(self, *args, **options):
        joined_statuses = ['Joined', 'Placed', 'Candidate Joined', 'Hired', 'Offered & Joined', 'Completed']

        created_count = 0
        skipped_count = 0
        salary_missing_count = 0

        self.stdout.write("Starting ledger sync for joined candidates...")

        # 1. Sync from Placements
        placements = Placement.objects.all()
        for pl in placements:
            try:
                comm = ensure_commission_for_joined(placement=pl, created_by='SyncCommand')
                if comm.status == 'SALARY_MISSING':
                    salary_missing_count += 1
                else:
                    created_count += 1
            except Exception as e:
                skipped_count += 1
                self.stderr.write(f"Error syncing placement ID {pl.id}: {e}")

        # 2. Sync from Applicants with joined status (if not already synced via placement)
        joined_applicants = Applicant.objects.filter(
            models.Q(status__in=joined_statuses) |
            models.Q(approval_status='Joined')
        ).distinct()

        for app in joined_applicants:
            try:
                comm = ensure_commission_for_joined(applicant=app, created_by='SyncCommand')
                if comm.status == 'SALARY_MISSING':
                    salary_missing_count += 1
                else:
                    created_count += 1
            except Exception as e:
                skipped_count += 1
                self.stderr.write(f"Error syncing applicant ID {app.id}: {e}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Ledger sync complete! Processed records: Created/Updated: {created_count}, "
                f"Salary Missing: {salary_missing_count}, Skipped/Error: {skipped_count}"
            )
        )
