from django.core.management.base import BaseCommand
from django.db import transaction
from apps.candidates.models import Applicant
from apps.accounts.models import EmployerAccount


class Command(BaseCommand):
    help = "Fix applicant ownership, sync employer/company from job, and report visibility status."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Simulate changes without saving to the database.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        if dry_run:
            self.stdout.write(self.style.WARNING("--- RUNNING IN DRY-RUN MODE (No changes will be saved) ---"))
        else:
            self.stdout.write(self.style.SUCCESS("--- RUNNING IN LIVE FIX MODE ---"))

        mismatched_count = 0
        fixed_count = 0
        no_employer_jobs = []
        invisible_approved = []
        now_visible_approved = []

        all_applicants = Applicant.objects.select_related('job', 'job__employer', 'job__company', 'employer', 'company').all()

        for applicant in all_applicants:
            job = applicant.job
            old_emp = applicant.employer
            old_comp = applicant.company

            # 1. Applicants whose job has no employer
            if not job:
                no_employer_jobs.append(f"Applicant #{applicant.id} ({applicant.full_name}): No job linked.")
            elif not job.employer:
                no_employer_jobs.append(f"Applicant #{applicant.id} ({applicant.full_name}): Job #{job.id} '{job.title}' has no owner employer.")

            # 2. Check mismatch between applicant.employer/company and job.employer/company
            if job and job.employer:
                target_employer = job.employer
                target_company = job.company or target_employer.company

                if old_emp != target_employer or old_comp != target_company:
                    mismatched_count += 1
                    self.stdout.write(
                        f"Mismatch on Applicant #{applicant.id} ({applicant.full_name}): "
                        f"Current Employer = {old_emp.company_name if old_emp else 'None'} (ID #{old_emp.id if old_emp else 'N/A'}), "
                        f"Target Employer = {target_employer.company_name} (ID #{target_employer.id})"
                    )

                    if not dry_run:
                        applicant.employer = target_employer
                        applicant.company = target_company
                        applicant.save(update_fields=['employer', 'company'])
                        fixed_count += 1

            # 3. Assess visibility changes for Approved applicants under new rules
            # Under new rules, visible to employer E iff approval_status == 'Approved' and applicant.job.employer_id == E.id (or shares_company_data opt-in)
            if applicant.approval_status == 'Approved':
                if not job or not job.employer:
                    invisible_approved.append(
                        f"Applicant #{applicant.id} ({applicant.full_name}): Approved but job has no employer -> INVISIBLE to all employers."
                    )
                else:
                    now_visible_approved.append(
                        f"Applicant #{applicant.id} ({applicant.full_name}): Approved -> Visible strictly to Employer #{job.employer.id} ({job.employer.company_name})."
                    )

        self.stdout.write("\n=== SUMMARY REPORT ===")
        self.stdout.write(f"Total Applicants Processed: {all_applicants.count()}")
        self.stdout.write(f"Mismatched Applicants Found: {mismatched_count}")
        if not dry_run:
            self.stdout.write(f"Mismatched Applicants Fixed: {fixed_count}")

        self.stdout.write("\n--- Applicants Whose Job Has No Owner Employer ---")
        if no_employer_jobs:
            for line in no_employer_jobs:
                self.stdout.write(self.style.WARNING(f"  • {line}"))
        else:
            self.stdout.write("  None found.")

        self.stdout.write("\n--- Approved Applicants Visibility Under New Rules ---")
        self.stdout.write(f"Approved applicants visible strictly to job owner: {len(now_visible_approved)}")
        self.stdout.write(f"Approved applicants invisible due to missing job owner: {len(invisible_approved)}")

        if invisible_approved:
            for line in invisible_approved:
                self.stdout.write(self.style.WARNING(f"  • {line}"))

        if dry_run:
            self.stdout.write(self.style.WARNING("\nDry-run complete. No database changes were executed."))
        else:
            self.stdout.write(self.style.SUCCESS("\nFix complete. Database updated successfully."))
