from django.core.management.base import BaseCommand
from apps.companies.models import CompanyEnquiry, Company, CompanyContact, CompanyRequirement
from apps.jobs.models import Job

class Command(BaseCommand):
    help = "Idempotently convert existing CompanyEnquiry records into Company, CompanyContact, and CompanyRequirement records."

    def handle(self, *args, **options):
        enquiries = CompanyEnquiry.objects.all()
        created_companies_count = 0
        created_contacts_count = 0
        created_reqs_count = 0

        for enquiry in enquiries:
            company, comp_created = Company.objects.get_or_create(
                name=enquiry.company_name,
                defaults={
                    "email": enquiry.email,
                    "phone": enquiry.phone,
                    "address": enquiry.address or "",
                    "source_enquiry": enquiry,
                    "status": "Active",
                }
            )
            if comp_created:
                created_companies_count += 1

            contact, contact_created = CompanyContact.objects.get_or_create(
                company=company,
                name=enquiry.recruiter_name,
                defaults={
                    "designation": enquiry.designation or "",
                    "email": enquiry.email or "",
                    "phone": enquiry.phone or "",
                    "is_primary": True,
                }
            )
            if contact_created:
                created_contacts_count += 1

            if enquiry.job_title:
                title = enquiry.job_title
                job_obj = Job.objects.filter(title__iexact=title, category__icontains=enquiry.company_name).first()
                req, req_created = CompanyRequirement.objects.get_or_create(
                    company=company,
                    source_enquiry=enquiry,
                    title=title,
                    defaults={
                        "contact": contact,
                        "job": job_obj,
                        "department": enquiry.department or "",
                        "job_type": enquiry.job_type or "Full Time",
                        "location": enquiry.address or "Lucknow, UP",
                        "vacancies": enquiry.vacancies or "1",
                        "experience_req": enquiry.experience_req or "",
                        "salary_range": enquiry.salary_range or "",
                        "description": enquiry.message or "",
                        "requirements": enquiry.requirements or "",
                        "deadline": enquiry.application_deadline or "30 Days",
                        "status": "Active" if enquiry.status in ["Approved", "Active", "Selected"] else "Active",
                    }
                )
                if req_created:
                    created_reqs_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Data migration complete. Companies created: {created_companies_count}, "
                f"Contacts created: {created_contacts_count}, Requirements created: {created_reqs_count}"
            )
        )
