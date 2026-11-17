from django.core.management.base import BaseCommand
from apps.candidates.models import Applicant
from apps.internships.models import Internship, InternshipApplication


class Command(BaseCommand):
    help = "Move existing Applicant rows whose job_title contains 'intern' into InternshipApplication."

    def add_arguments(self, parser):
        parser.add_argument(
            '--commit',
            action='store_true',
            help='Commit changes to the database (default is dry-run).',
        )
        parser.add_argument(
            '--delete-originals',
            action='store_true',
            help='Delete original Applicant rows after copying (only takes effect if --commit is passed).',
        )

    def handle(self, *args, **options):
        commit = options['commit']
        delete_originals = options['delete_originals']

        applicants = Applicant.objects.filter(job_title__icontains='intern')
        total_found = applicants.count()

        self.stdout.write(f"Found {total_found} Applicant row(s) with 'intern' in job_title.")

        if not commit:
            self.stdout.write(self.style.WARNING("DRY-RUN MODE: No changes will be written to database. Pass --commit to apply."))

        general_internship = None
        if commit and total_found > 0:
            general_internship, _ = Internship.objects.get_or_create(
                title="General Internship Programme",
                defaults={
                    "description": "General Internship Application",
                    "mode": "Onsite",
                    "duration": "3 Months",
                    "seats": 10,
                    "status": "Open"
                }
            )

        copied_count = 0
        skipped_count = 0

        for applicant in applicants:
            email = (applicant.email or "").strip()
            phone = (applicant.phone or "").strip()

            self.stdout.write(f" - [{applicant.id}] {applicant.full_name} ({email} | {phone}) - Title: '{applicant.job_title}'")

            if commit:
                # Check for existing duplicate in InternshipApplication
                existing = InternshipApplication.objects.filter(
                    internship=general_internship,
                    email__iexact=email,
                    phone=phone
                ).first()

                if existing:
                    self.stdout.write(self.style.WARNING(f"   -> Skipped (already exists as InternshipApplication #{existing.id})"))
                    skipped_count += 1
                else:
                    app = InternshipApplication.objects.create(
                        internship=general_internship,
                        full_name=applicant.full_name,
                        email=email,
                        phone=phone,
                        college="",
                        course_stream=applicant.qualification or "Internship",
                        skills=applicant.skills or "",
                        message=applicant.cover_letter or "",
                        resume=applicant.resume or "",
                        status="Pending"
                    )
                    copied_count += 1
                    self.stdout.write(self.style.SUCCESS(f"   -> Copied to InternshipApplication #{app.id}"))
            else:
                copied_count += 1

        if commit:
            self.stdout.write(self.style.SUCCESS(f"Finished: {copied_count} copied, {skipped_count} skipped."))
            if delete_originals:
                applicants.delete()
                self.stdout.write(self.style.SUCCESS(f"Deleted {total_found} original Applicant row(s)."))
        else:
            self.stdout.write(self.style.WARNING(f"Dry-run finished: Would copy {copied_count} row(s). Pass --commit to execute."))
