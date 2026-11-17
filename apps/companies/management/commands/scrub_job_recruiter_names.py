from django.core.management.base import BaseCommand
from apps.jobs.models import Job
from apps.companies.views import scrub_recruiter_details_from_job

class Command(BaseCommand):
    help = "Sanitize public job listings by removing recruiter names and raw company contact tags."

    def handle(self, *args, **options):
        jobs = Job.objects.all()
        scrubbed_count = 0
        for job in jobs:
            old_cat = job.category
            old_desc = job.description
            scrub_recruiter_details_from_job(job)
            if job.category != old_cat or job.description != old_desc:
                scrubbed_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully scrubbed recruiter details from {scrubbed_count} job listings."))
