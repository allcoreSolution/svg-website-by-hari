import json
import re
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.utils import timezone

from .models import CompanyEnquiry, Company, CompanyContact, CompanyRequirement
from .validators import (
    validate_email, validate_phone, validate_website,
    validate_gstin, validate_vacancies, validate_deadline
)
from apps.accounts.auth_helpers import admin_required
from apps.enquiries.models import log_activity
from apps.jobs.models import Job


# ==========================================
# SECURITY & UTILITY HELPERS
# ==========================================

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip or '127.0.0.1'


def is_rate_limited(ip, key_prefix="rate_limit", max_requests=5, window_seconds=3600):
    cache_key = f"{key_prefix}_{ip}"
    request_count = cache.get(cache_key, 0)
    if request_count >= max_requests:
        return True
    cache.set(cache_key, request_count + 1, window_seconds)
    return False


def scrub_recruiter_details_from_job(job_obj, company_name=None):
    """Removes recruiter names and raw company contact tags from public job listings."""
    if not job_obj:
        return

    # Scrub category
    category = job_obj.category or ""
    if "(" in category and ")" in category:
        category = re.sub(r'\s*\([^)]*\)', '', category).strip()
    if not category or category.lower() == "company":
        category = company_name or "Sky Vision Partner"
    job_obj.category = category

    # Scrub description of recruiter info
    desc = job_obj.description or ""
    desc = re.sub(r'Recruiter:\s*[^.]*\.?', '', desc, flags=re.IGNORECASE).strip()
    job_obj.description = desc
    job_obj.save()


def sync_expired_requirements():
    """Syncs requirement status to Expired if application deadline has passed."""
    active_reqs = CompanyRequirement.objects.filter(status="Active")
    today = timezone.now().date()
    expired_count = 0

    for req in active_reqs:
        if req.deadline and re.match(r'^\d{4}-\d{2}-\d{2}$', req.deadline.strip()):
            try:
                deadline_date = datetime.strptime(req.deadline.strip(), "%Y-%m-%d").date()
                if deadline_date < today:
                    req.status = "Expired"
                    req.save()
                    expired_count += 1
                    if req.job and req.job.status == "Active":
                        req.job.status = "Closed"
                        req.job.save()
            except ValueError:
                pass
    return expired_count


# ==========================================
# PUBLIC COMPANY ENQUIRY ENDPOINT
# ==========================================

@require_http_methods(["POST"])
def create_company_enquiry(request):
    """Public hiring requirement submission for recruiters & employers."""
    # Honeypot Anti-Spam Check
    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST

    honeypot = (data.get("website_url") or data.get("company_website_url") or "").strip()
    if honeypot:
        # Silently discard spam submission
        return JsonResponse({
            "status": "success",
            "message": "Thank you! Your hiring requirement has been submitted. Our corporate team will get in touch shortly."
        })

    # Rate Limiting
    ip = get_client_ip(request)
    if is_rate_limited(ip, key_prefix="company_enquiry", max_requests=5, window_seconds=3600):
        return JsonResponse({
            "status": "error",
            "message": "Too many enquiry submissions from your IP address. Please try again later."
        }, status=429)

    recruiter_name = (data.get("recruiter_name") or data.get("name") or "").strip()
    company_name = (data.get("company_name") or "").strip()
    phone = (data.get("phone") or data.get("mobile") or "").strip()
    email = (data.get("email") or data.get("recruiter_email") or "").strip()

    if not (recruiter_name and company_name and phone and email):
        return JsonResponse({"status": "error", "message": "Recruiter name, company name, phone, and email are required."}, status=400)

    val_ok, msg = validate_email(email)
    if not val_ok: return JsonResponse({"status": "error", "message": msg}, status=400)

    val_ok, msg = validate_phone(phone)
    if not val_ok: return JsonResponse({"status": "error", "message": msg}, status=400)

    vacancies = str(data.get("vacancies", "1")).strip()
    val_ok, msg = validate_vacancies(vacancies)
    if not val_ok: return JsonResponse({"status": "error", "message": msg}, status=400)

    enquiry = CompanyEnquiry.objects.create(
        recruiter_name=recruiter_name,
        designation=(data.get("designation") or "").strip(),
        company_name=company_name,
        phone=phone,
        email=email,
        address=(data.get("address") or data.get("location") or "").strip(),
        job_title=(data.get("job_title") or "").strip(),
        department=(data.get("department") or "").strip(),
        job_type=(data.get("job_type") or "Full Time").strip(),
        application_deadline=(data.get("application_deadline") or "30 Days").strip(),
        vacancies=vacancies,
        experience_req=(data.get("experience_req") or data.get("experience") or "").strip(),
        salary_range=(data.get("salary_range") or "").strip(),
        requirements=(data.get("requirements") or "").strip(),
        message=(data.get("message") or "").strip(),
        status="New",  # Force New status to prevent escalation
        notes=""      # Force empty notes
    )

    log_activity(
        "company",
        "Company enquiry received",
        f"{company_name} ({recruiter_name}) posted hiring requirement for {enquiry.job_title or 'staff'} ({enquiry.vacancies} vacancies)"
    )

    return JsonResponse({
        "status": "success",
        "message": "Thank you! Your hiring requirement has been submitted. Our corporate team will get in touch shortly."
    })


# ==========================================
# ADMIN COMPANY ENQUIRIES ENDPOINTS
# ==========================================

@require_http_methods(["GET"])
@admin_required
def get_company_enquiries(request):
    q = request.GET.get("q", "").strip().lower()
    status_filter = request.GET.get("status", "").strip()

    queryset = CompanyEnquiry.objects.all().order_by('-id')
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    results = []
    for e in queryset:
        if q:
            match = (
                q in e.company_name.lower() or
                q in e.recruiter_name.lower() or
                q in e.email.lower() or
                q in (e.job_title or "").lower()
            )
            if not match:
                continue
        results.append(e.to_dict())

    return JsonResponse(results, safe=False)


@admin_required
def company_enquiry_detail(request, id):
    try:
        enquiry = CompanyEnquiry.objects.get(id=id)
    except CompanyEnquiry.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Company enquiry not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(enquiry.to_dict())

    elif request.method == "PUT":
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        if "recruiter_name" in data: enquiry.recruiter_name = data["recruiter_name"]
        if "designation" in data: enquiry.designation = data["designation"]
        if "company_name" in data: enquiry.company_name = data["company_name"]
        if "phone" in data: enquiry.phone = data["phone"]
        if "email" in data: enquiry.email = data["email"]
        if "address" in data: enquiry.address = data["address"]
        if "job_title" in data: enquiry.job_title = data["job_title"]
        if "department" in data: enquiry.department = data["department"]
        if "job_type" in data: enquiry.job_type = data["job_type"]
        if "application_deadline" in data: enquiry.application_deadline = data["application_deadline"]
        if "vacancies" in data: enquiry.vacancies = str(data["vacancies"])
        if "experience_req" in data: enquiry.experience_req = data["experience_req"]
        if "salary_range" in data: enquiry.salary_range = data["salary_range"]
        if "requirements" in data: enquiry.requirements = data["requirements"]
        if "message" in data: enquiry.message = data["message"]
        if "status" in data: enquiry.status = data["status"]
        if "notes" in data: enquiry.notes = data["notes"]
        enquiry.save()

        log_activity("company", "Company enquiry updated", f"Enquiry #{enquiry.id} ({enquiry.company_name}) updated by Admin")
        return JsonResponse({"status": "success", "message": f"Company enquiry '{enquiry.company_name}' updated successfully.", "enquiry": enquiry.to_dict()})

    elif request.method == "DELETE":
        company_name = enquiry.company_name
        enquiry.delete()
        log_activity("company", "Company enquiry deleted", f"Enquiry for {company_name} deleted")
        return JsonResponse({"status": "success", "message": "Company enquiry deleted successfully."})

    return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)


# ==========================================
# ADMIN COMPANIES CRUD ENDPOINTS
# ==========================================

@admin_required
def companies_api(request):
    sync_expired_requirements()
    if request.method == "GET":
        q = request.GET.get("q", "").strip().lower()
        status_filter = request.GET.get("status", "").strip()

        queryset = Company.objects.all().order_by('-id')
        if status_filter:
            queryset = queryset.filter(status__iexact=status_filter)

        results = []
        for c in queryset:
            if q:
                match = (
                    q in c.name.lower() or
                    q in c.email.lower() or
                    q in c.phone.lower() or
                    q in (c.city or "").lower() or
                    q in (c.industry or "").lower() or
                    q in (c.gst_number or "").lower()
                )
                if not match:
                    continue
            results.append(c.to_dict())
        return JsonResponse(results, safe=False)

    elif request.method == "POST":
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        name = (data.get("name") or data.get("company_name") or "").strip()
        email = (data.get("email") or "").strip()
        phone = (data.get("phone") or "").strip()

        if not (name and email and phone):
            return JsonResponse({"status": "error", "message": "Company name, email, and phone are required."}, status=400)

        val_ok, msg = validate_email(email)
        if not val_ok: return JsonResponse({"status": "error", "message": msg}, status=400)

        val_ok, msg = validate_phone(phone)
        if not val_ok: return JsonResponse({"status": "error", "message": msg}, status=400)

        if data.get("website"):
            val_ok, msg = validate_website(data.get("website"))
            if not val_ok: return JsonResponse({"status": "error", "message": msg}, status=400)

        if data.get("gst_number"):
            val_ok, msg = validate_gstin(data.get("gst_number"))
            if not val_ok: return JsonResponse({"status": "error", "message": msg}, status=400)

        company = Company.objects.create(
            name=name,
            industry=(data.get("industry") or "").strip(),
            website=(data.get("website") or "").strip(),
            email=email,
            phone=phone,
            address=(data.get("address") or "").strip(),
            city=(data.get("city") or "Lucknow").strip(),
            state=(data.get("state") or "Uttar Pradesh").strip(),
            gst_number=(data.get("gst_number") or "").strip(),
            status=(data.get("status") or "Active").strip(),
            notes=(data.get("notes") or "").strip()
        )

        # Create primary contact if contact details provided
        contact_name = (data.get("contact_name") or data.get("recruiter_name") or name + " Contact").strip()
        primary_contact = CompanyContact.objects.create(
            company=company,
            name=contact_name,
            designation=(data.get("designation") or "HR Manager").strip(),
            email=email,
            phone=phone,
            is_primary=True
        )

        # Create initial requirement if title provided
        initial_title = (data.get("job_title") or data.get("requirement_title") or "").strip()
        if initial_title:
            CompanyRequirement.objects.create(
                company=company,
                contact=primary_contact,
                title=initial_title,
                department=(data.get("department") or "").strip(),
                job_type=(data.get("job_type") or "Full Time").strip(),
                location=(data.get("location") or company.address or "Lucknow, UP").strip(),
                vacancies=str(data.get("vacancies", "1")).strip(),
                experience_req=(data.get("experience_req") or "").strip(),
                salary_range=(data.get("salary_range") or "").strip(),
                description=(data.get("description") or "").strip(),
                requirements=(data.get("requirements") or "").strip(),
                deadline=(data.get("deadline") or "30 Days").strip(),
                status="Active"
            )

        log_activity("company", "Company Created", f"Company '{company.name}' created by Admin")
        return JsonResponse({"status": "success", "message": f"Company '{company.name}' created successfully.", "company": company.to_dict()}, status=201)

    return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)


@admin_required
def company_detail_api(request, id):
    try:
        company = Company.objects.get(id=id)
    except Company.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Company not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(company.to_dict())

    elif request.method == "PUT":
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        if "name" in data: company.name = data["name"].strip()
        if "industry" in data: company.industry = data["industry"].strip()
        if "website" in data: company.website = data["website"].strip()
        if "email" in data: company.email = data["email"].strip()
        if "phone" in data: company.phone = data["phone"].strip()
        if "address" in data: company.address = data["address"].strip()
        if "city" in data: company.city = data["city"].strip()
        if "state" in data: company.state = data["state"].strip()
        if "gst_number" in data: company.gst_number = data["gst_number"].strip()
        if "status" in data: company.status = data["status"].strip()
        if "notes" in data: company.notes = data["notes"].strip()

        company.save()
        log_activity("company", "Company Updated", f"Company '{company.name}' updated by Admin")
        return JsonResponse({"status": "success", "message": f"Company '{company.name}' updated successfully.", "company": company.to_dict()})

    elif request.method == "DELETE":
        name = company.name
        company.delete()
        log_activity("company", "Company Deleted", f"Company '{name}' deleted by Admin")
        return JsonResponse({"status": "success", "message": "Company deleted successfully."})

    return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)


# ==========================================
# ADMIN COMPANY CONTACTS CRUD ENDPOINTS
# ==========================================

@admin_required
def company_contacts_api(request):
    if request.method == "GET":
        company_id = request.GET.get("company_id")
        q = request.GET.get("q", "").strip().lower()

        queryset = CompanyContact.objects.all().order_by('-id')
        if company_id:
            try: queryset = queryset.filter(company_id=int(company_id))
            except ValueError: pass

        results = []
        for c in queryset:
            if q:
                match = (
                    q in c.name.lower() or
                    q in (c.email or "").lower() or
                    q in (c.phone or "").lower() or
                    q in (c.designation or "").lower() or
                    q in (c.company.name.lower() if c.company else "")
                )
                if not match:
                    continue
            results.append(c.to_dict())
        return JsonResponse(results, safe=False)

    elif request.method == "POST":
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        company_id = data.get("company_id")
        name = (data.get("name") or "").strip()

        if not (company_id and name):
            return JsonResponse({"status": "error", "message": "Company ID and contact name are required."}, status=400)

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Associated company not found."}, status=404)

        contact = CompanyContact.objects.create(
            company=company,
            name=name,
            designation=(data.get("designation") or "").strip(),
            email=(data.get("email") or "").strip(),
            phone=(data.get("phone") or "").strip(),
            is_primary=bool(data.get("is_primary", False)),
            notes=(data.get("notes") or "").strip()
        )

        log_activity("company", "Company Contact Created", f"Contact '{contact.name}' created for {company.name}")
        return JsonResponse({"status": "success", "message": "Contact added successfully.", "contact": contact.to_dict()}, status=201)

    return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)


@admin_required
def company_contact_detail_api(request, id):
    try:
        contact = CompanyContact.objects.get(id=id)
    except CompanyContact.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Company contact not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(contact.to_dict())

    elif request.method == "PUT":
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        if "name" in data: contact.name = data["name"].strip()
        if "designation" in data: contact.designation = data["designation"].strip()
        if "email" in data: contact.email = data["email"].strip()
        if "phone" in data: contact.phone = data["phone"].strip()
        if "is_primary" in data: contact.is_primary = bool(data["is_primary"])
        if "notes" in data: contact.notes = data["notes"].strip()

        contact.save()
        log_activity("company", "Company Contact Updated", f"Contact '{contact.name}' updated")
        return JsonResponse({"status": "success", "message": "Contact updated successfully.", "contact": contact.to_dict()})

    elif request.method == "DELETE":
        name = contact.name
        contact.delete()
        log_activity("company", "Company Contact Deleted", f"Contact '{name}' deleted")
        return JsonResponse({"status": "success", "message": "Contact deleted successfully."})

    return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)


@admin_required
@require_http_methods(["POST"])
def set_primary_contact_api(request, id):
    try:
        contact = CompanyContact.objects.get(id=id)
    except CompanyContact.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Contact not found."}, status=404)

    contact.is_primary = True
    contact.save()
    return JsonResponse({"status": "success", "message": f"'{contact.name}' set as primary contact for {contact.company.name}."})


# ==========================================
# ADMIN COMPANY REQUIREMENTS CRUD ENDPOINTS
# ==========================================

@admin_required
def company_requirements_api(request):
    sync_expired_requirements()
    if request.method == "GET":
        company_id = request.GET.get("company_id")
        status_filter = request.GET.get("status", "").strip()
        q = request.GET.get("q", "").strip().lower()

        queryset = CompanyRequirement.objects.all().order_by('-id')
        if company_id:
            try: queryset = queryset.filter(company_id=int(company_id))
            except ValueError: pass
        if status_filter:
            queryset = queryset.filter(status__iexact=status_filter)

        results = []
        for r in queryset:
            if q:
                match = (
                    q in r.title.lower() or
                    q in (r.department or "").lower() or
                    q in (r.company.name.lower() if r.company else "") or
                    q in (r.location or "").lower()
                )
                if not match:
                    continue
            results.append(r.to_dict())
        return JsonResponse(results, safe=False)

    elif request.method == "POST":
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        company_id = data.get("company_id")
        title = (data.get("title") or "").strip()

        if not (company_id and title):
            return JsonResponse({"status": "error", "message": "Company ID and requirement title are required."}, status=400)

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Company not found."}, status=404)

        contact = None
        if data.get("contact_id"):
            contact = CompanyContact.objects.filter(id=data["contact_id"]).first()
        if not contact:
            contact = company.contacts.filter(is_primary=True).first() or company.contacts.first()

        vacancies = str(data.get("vacancies", "1")).strip()
        val_ok, msg = validate_vacancies(vacancies)
        if not val_ok: return JsonResponse({"status": "error", "message": msg}, status=400)

        deadline = (data.get("deadline") or "30 Days").strip()
        val_ok, msg = validate_deadline(deadline)
        if not val_ok: return JsonResponse({"status": "error", "message": msg}, status=400)

        req = CompanyRequirement.objects.create(
            company=company,
            contact=contact,
            title=title,
            department=(data.get("department") or "").strip(),
            job_type=(data.get("job_type") or "Full Time").strip(),
            location=(data.get("location") or company.address or "Lucknow, UP").strip(),
            vacancies=vacancies,
            experience_req=(data.get("experience_req") or "").strip(),
            salary_range=(data.get("salary_range") or "").strip(),
            description=(data.get("description") or "").strip(),
            requirements=(data.get("requirements") or "").strip(),
            deadline=deadline,
            status="Active",
            notes=(data.get("notes") or "").strip()
        )

        log_activity("company", "Company Requirement Created", f"Requirement '{req.title}' created for {company.name}")
        return JsonResponse({"status": "success", "message": "Company requirement added successfully.", "requirement": req.to_dict()}, status=201)

    return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)


@admin_required
def company_requirement_detail_api(request, id):
    try:
        req = CompanyRequirement.objects.get(id=id)
    except CompanyRequirement.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Company requirement not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(req.to_dict())

    elif request.method == "PUT":
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        if "title" in data: req.title = data["title"].strip()
        if "department" in data: req.department = data["department"].strip()
        if "job_type" in data: req.job_type = data["job_type"].strip()
        if "location" in data: req.location = data["location"].strip()
        if "vacancies" in data: req.vacancies = str(data["vacancies"]).strip()
        if "experience_req" in data: req.experience_req = data["experience_req"].strip()
        if "salary_range" in data: req.salary_range = data["salary_range"].strip()
        if "description" in data: req.description = data["description"].strip()
        if "requirements" in data: req.requirements = data["requirements"].strip()
        if "deadline" in data: req.deadline = data["deadline"].strip()
        if "status" in data: req.status = data["status"].strip()
        if "notes" in data: req.notes = data["notes"].strip()

        req.save()

        # Update linked job if exists
        if req.job:
            req.job.title = req.title
            req.job.department = req.department or "General"
            req.job.location = req.location or "Lucknow, UP"
            req.job.employment_type = req.job_type or "Full Time"
            req.job.experience = req.experience_req or "0-2 Years"
            req.job.salary = req.salary_range or "Best in Industry"
            req.job.vacancies = req.vacancies
            req.job.save()

        log_activity("company", "Requirement Updated", f"Requirement '{req.title}' updated")
        return JsonResponse({"status": "success", "message": "Requirement updated successfully.", "requirement": req.to_dict()})

    elif request.method == "DELETE":
        title = req.title
        req.delete()
        log_activity("company", "Requirement Deleted", f"Requirement '{title}' deleted")
        return JsonResponse({"status": "success", "message": "Requirement deleted successfully."})

    return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)


@admin_required
@require_http_methods(["POST"])
def publish_company_requirement_api(request, id):
    try:
        req = CompanyRequirement.objects.get(id=id)
    except CompanyRequirement.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Requirement not found."}, status=404)

    if req.job:
        req.job.status = "Active"
        req.job.save()
        req.status = "Active"
        req.save()
        return JsonResponse({"status": "success", "message": f"Requirement '{req.title}' is already published as Job #{req.job.id}.", "job": req.job.to_dict()})

    # Create new public Job opening
    clean_category = req.company.name if req.company else "Sky Vision Partner"
    job = Job.objects.create(
        title=req.title,
        category=clean_category,
        department=req.department or "General",
        location=req.location or req.company.address or "Lucknow, UP",
        employment_type=req.job_type or "Full Time",
        experience=req.experience_req or "0-2 Years",
        salary=req.salary_range or "Best in Industry",
        vacancies=str(req.vacancies or "1"),
        description=req.description or f"Position at {clean_category}.",
        requirements=req.requirements or req.experience_req or "Relevant qualifications and skills.",
        status=Job.STATUS_LIVE
    )

    scrub_recruiter_details_from_job(job, req.company.name if req.company else None)

    req.job = job
    req.status = "Active"
    req.save()

    log_activity("job", "Job Published from Requirement", f"Published job '{job.title}' for {req.company.name}")
    return JsonResponse({"status": "success", "message": f"Requirement '{req.title}' published successfully as public Job opening!", "job": job.to_dict(), "requirement": req.to_dict()})


@admin_required
@require_http_methods(["POST"])
def close_company_requirement_api(request, id):
    try:
        req = CompanyRequirement.objects.get(id=id)
    except CompanyRequirement.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Requirement not found."}, status=404)

    req.status = "Closed"
    req.save()

    if req.job:
        req.job.status = "Closed"
        req.job.save()

    log_activity("company", "Requirement Closed", f"Requirement '{req.title}' closed")
    return JsonResponse({"status": "success", "message": f"Requirement '{req.title}' has been closed.", "requirement": req.to_dict()})


@admin_required
@require_http_methods(["POST"])
def reopen_company_requirement_api(request, id):
    try:
        req = CompanyRequirement.objects.get(id=id)
    except CompanyRequirement.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Requirement not found."}, status=404)

    req.status = "Active"
    req.save()

    if req.job:
        req.job.status = "Active"
        req.job.save()

    log_activity("company", "Requirement Reopened", f"Requirement '{req.title}' reopened")
    return JsonResponse({"status": "success", "message": f"Requirement '{req.title}' has been reopened as Active.", "requirement": req.to_dict()})


@admin_required
@require_http_methods(["POST"])
def reject_company_requirement_api(request, id):
    try:
        req = CompanyRequirement.objects.get(id=id)
    except CompanyRequirement.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Requirement not found."}, status=404)

    req.status = "Closed"
    req.notes = f"Rejected by Admin on {datetime.now().strftime('%Y-%m-%d %H:%M')}. {req.notes}".strip()
    req.save()

    if req.job:
        req.job.status = "Closed"
        req.job.save()

    log_activity("company", "Requirement Rejected", f"Requirement '{req.title}' rejected by Admin")
    return JsonResponse({"status": "success", "message": f"Requirement '{req.title}' rejected.", "requirement": req.to_dict()})


# ==========================================
# ADMIN JOB OPENINGS CRUD ENDPOINTS
# ==========================================

@admin_required
def admin_jobs_api(request):
    if request.method == "GET":
        status_filter = request.GET.get("status", "").strip()
        q = request.GET.get("q", "").strip().lower()

        queryset = Job.objects.all().order_by('-id')
        if status_filter:
            queryset = queryset.filter(status__iexact=status_filter)

        results = []
        for j in queryset:
            if q:
                match = (
                    q in j.title.lower() or
                    q in (j.category or "").lower() or
                    q in (j.department or "").lower() or
                    q in (j.location or "").lower()
                )
                if not match:
                    continue
            results.append(j.to_dict())
        return JsonResponse(results, safe=False)

    elif request.method == "POST":
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        title = (data.get("title") or "").strip()
        if not title:
            return JsonResponse({"status": "error", "message": "Job title is required."}, status=400)

        job = Job.objects.create(
            title=title,
            category=(data.get("category") or "General").strip(),
            department=(data.get("department") or "General").strip(),
            location=(data.get("location") or "Lucknow, UP").strip(),
            employment_type=(data.get("employment_type") or "Full Time").strip(),
            experience=(data.get("experience") or "0-2 Years").strip(),
            salary=(data.get("salary") or "Best in Industry").strip(),
            vacancies=str(data.get("vacancies", "1")).strip(),
            description=(data.get("description") or "").strip(),
            requirements=(data.get("requirements") or "").strip(),
            status=Job.STATUS_LIVE if (data.get("status") or "LIVE").strip().upper() in ["ACTIVE", "LIVE"] else (data.get("status") or Job.STATUS_LIVE).strip()
        )

        scrub_recruiter_details_from_job(job)

        log_activity("job", "Job Opening Created", f"Job '{job.title}' created by Admin")
        return JsonResponse({"status": "success", "message": f"Job opening '{job.title}' created successfully.", "job": job.to_dict()}, status=201)

    return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)


@admin_required
def admin_job_detail_api(request, id):
    try:
        job = Job.objects.get(id=id)
    except Job.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Job opening not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(job.to_dict())

    elif request.method == "PUT":
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        if "title" in data: job.title = data["title"].strip()
        if "category" in data: job.category = data["category"].strip()
        if "department" in data: job.department = data["department"].strip()
        if "location" in data: job.location = data["location"].strip()
        if "employment_type" in data: job.employment_type = data["employment_type"].strip()
        if "experience" in data: job.experience = data["experience"].strip()
        if "salary" in data: job.salary = data["salary"].strip()
        if "vacancies" in data: job.vacancies = str(data["vacancies"]).strip()
        if "description" in data: job.description = data["description"].strip()
        if "requirements" in data: job.requirements = data["requirements"].strip()
        if "status" in data: job.status = data["status"].strip()

        job.save()
        scrub_recruiter_details_from_job(job)

        log_activity("job", "Job Opening Updated", f"Job '{job.title}' updated by Admin")
        return JsonResponse({"status": "success", "message": f"Job opening '{job.title}' updated successfully.", "job": job.to_dict()})

    elif request.method == "DELETE":
        title = job.title
        job.delete()
        log_activity("job", "Job Opening Deleted", f"Job '{title}' deleted by Admin")
        return JsonResponse({"status": "success", "message": "Job opening deleted successfully."})

    return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)


# ==========================================
# ENQUIRY CONVERSION WORKFLOW ENDPOINTS
# ==========================================

@admin_required
@require_http_methods(["POST"])
def convert_company_enquiry_api(request, id):
    try:
        enquiry = CompanyEnquiry.objects.get(id=id)
    except CompanyEnquiry.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Company enquiry not found."}, status=404)

    company_name_clean = (enquiry.company_name or "").strip()
    recruiter_name_clean = (enquiry.recruiter_name or "").strip()

    company = Company.objects.filter(name__iexact=company_name_clean).first()
    if not company:
        company = Company.objects.create(
            name=company_name_clean,
            email=(enquiry.email or "").strip(),
            phone=(enquiry.phone or "").strip(),
            address=(enquiry.address or "").strip(),
            source_enquiry=enquiry,
            status="Active"
        )
    else:
        if not company.source_enquiry:
            company.source_enquiry = enquiry
            company.save()

    contact = CompanyContact.objects.filter(company=company, name__iexact=recruiter_name_clean).first()
    if not contact:
        contact = CompanyContact.objects.create(
            company=company,
            name=recruiter_name_clean or (company.name + " Contact"),
            designation=(enquiry.designation or "Recruiter").strip(),
            email=(enquiry.email or "").strip(),
            phone=(enquiry.phone or "").strip(),
            is_primary=True
        )

    req = None
    if enquiry.job_title:
        title = enquiry.job_title.strip()
        req = CompanyRequirement.objects.filter(company=company, source_enquiry=enquiry).first()
        if not req:
            req = CompanyRequirement.objects.create(
                company=company,
                contact=contact,
                source_enquiry=enquiry,
                title=title,
                department=(enquiry.department or "").strip(),
                job_type=(enquiry.job_type or "Full Time").strip(),
                location=(enquiry.address or "Lucknow, UP").strip(),
                vacancies=str(enquiry.vacancies or "1").strip(),
                experience_req=(enquiry.experience_req or "").strip(),
                salary_range=(enquiry.salary_range or "").strip(),
                description=(enquiry.message or "").strip(),
                requirements=(enquiry.requirements or "").strip(),
                deadline=(enquiry.application_deadline or "30 Days").strip(),
                status="Active"
            )

    enquiry.status = "Converted"
    enquiry.save()

    log_activity("company", "Company Enquiry Converted", f"Enquiry #{enquiry.id} ({company.name}) converted to Company #{company.id}")
    return JsonResponse({
        "status": "success",
        "message": f"Enquiry converted successfully! Company '{company.name}' created.",
        "company": company.to_dict(),
        "contact": contact.to_dict(),
        "requirement": req.to_dict() if req else None
    })


@admin_required
@require_http_methods(["POST"])
def approve_publish_company_enquiry_api(request, id):
    try:
        enquiry = CompanyEnquiry.objects.get(id=id)
    except CompanyEnquiry.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Company enquiry not found."}, status=404)

    company_name_clean = (enquiry.company_name or "").strip()
    recruiter_name_clean = (enquiry.recruiter_name or "").strip()

    # 1. Convert/Fetch Company & Contact
    company = Company.objects.filter(name__iexact=company_name_clean).first()
    if not company:
        company = Company.objects.create(
            name=company_name_clean,
            email=(enquiry.email or "").strip(),
            phone=(enquiry.phone or "").strip(),
            address=(enquiry.address or "").strip(),
            source_enquiry=enquiry,
            status="Active"
        )
    else:
        if not company.source_enquiry:
            company.source_enquiry = enquiry
            company.save()

    contact = CompanyContact.objects.filter(company=company, name__iexact=recruiter_name_clean).first()
    if not contact:
        contact = CompanyContact.objects.create(
            company=company,
            name=recruiter_name_clean or (company.name + " Contact"),
            designation=(enquiry.designation or "Recruiter").strip(),
            email=(enquiry.email or "").strip(),
            phone=(enquiry.phone or "").strip(),
            is_primary=True
        )

    title = (enquiry.job_title or f"Position at {company.name}").strip()
    req = CompanyRequirement.objects.filter(company=company, source_enquiry=enquiry).first()
    if not req:
        req = CompanyRequirement.objects.create(
            company=company,
            contact=contact,
            source_enquiry=enquiry,
            title=title,
            department=(enquiry.department or "").strip(),
            job_type=(enquiry.job_type or "Full Time").strip(),
            location=(enquiry.address or "Lucknow, UP").strip(),
            vacancies=str(enquiry.vacancies or "1").strip(),
            experience_req=(enquiry.experience_req or "").strip(),
            salary_range=(enquiry.salary_range or "").strip(),
            description=(enquiry.message or "").strip(),
            requirements=(enquiry.requirements or "").strip(),
            deadline=(enquiry.application_deadline or "30 Days").strip(),
            status="Active"
        )

    # 2. Publish scrubbed Job
    job = req.job
    if not job:
        job = Job.objects.create(
            title=title,
            category=company.name,
            department=req.department or "General",
            location=req.location or "Lucknow, UP",
            employment_type=req.job_type or "Full Time",
            experience=req.experience_req or "0-2 Years",
            salary=req.salary_range or "Best in Industry",
            vacancies=str(req.vacancies or "1"),
            description=req.description or f"Hiring requirement for {title} at {company.name}.",
            requirements=req.requirements or "Relevant qualifications and skills.",
            status=Job.STATUS_LIVE
        )
        scrub_recruiter_details_from_job(job, company.name)
        req.job = job
        req.save()
    else:
        job.status = Job.STATUS_LIVE
        job.save()

    enquiry.status = "Approved"
    enquiry.save()

    log_activity("job", "Company Enquiry Approved & Published", f"Approved enquiry for {company.name} -> Published job '{job.title}'")
    return JsonResponse({
        "status": "success",
        "message": f"Approved & published job '{job.title}' for company '{company.name}' successfully!",
        "company": company.to_dict(),
        "requirement": req.to_dict(),
        "job": job.to_dict()
    })

