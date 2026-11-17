import json
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from .models import Applicant, Resume, Interview
from .validators import validate_candidate_data, validate_interview_data
from apps.accounts.auth_helpers import admin_required, save_resume_file, delete_resume_file
from apps.enquiries.models import log_activity


@require_http_methods(["POST"])
def apply_job(request):
    """Job application API. Requires candidate login and approval."""
    try:
        data = request.POST if request.POST else (json.loads(request.body) if request.body else {})
    except Exception:
        data = request.POST

    job_title = str(data.get("job_title") or data.get("title") or "").strip()
    internship_id = data.get("internship_id") or data.get("internship")
    is_internship = data.get("is_internship")
    job_id = data.get("job_id")

    # If it's an internship application, route strictly to internship API (never save to general applicants)
    if "intern" in job_title.lower() or internship_id or is_internship:
        from apps.internships.views import public_internship_apply_api
        return public_internship_apply_api(request)

    if job_id:
        from apps.jobs.models import Job
        job_check = Job.objects.filter(id=job_id).first()
        if job_check and "intern" in (job_check.title or "").lower():
            from apps.internships.views import public_internship_apply_api
            return public_internship_apply_api(request)

    # 1. Require candidate authentication
    candidate_id = request.session.get('candidate_id')
    if not candidate_id:
        return JsonResponse({
            "status": "login_required",
            "message": "Please log in or register a candidate account to apply for jobs.",
            "redirect_url": "/candidate/login/"
        }, status=401)

    from apps.accounts.models import CandidateAccount
    try:
        candidate_account = CandidateAccount.objects.get(id=candidate_id)
        if candidate_account.approval_status == 'rejected':
            return JsonResponse({
                "status": "error",
                "message": "Your candidate account was rejected by admin. Please contact support."
            }, status=403)
        if not candidate_account.is_approved or candidate_account.approval_status != 'approved':
            return JsonResponse({
                "status": "error",
                "message": "Your account is pending admin approval. You cannot apply for jobs until approved."
            }, status=403)
    except CandidateAccount.DoesNotExist:
        request.session.pop('candidate_id', None)
        return JsonResponse({
            "status": "login_required",
            "message": "Please log in as a candidate to apply.",
            "redirect_url": "/candidate/login/"
        }, status=401)

    # 2. Get Job object and validate
    job_id = data.get("job_id")
    target_job = None
    from apps.jobs.models import Job
    if job_id:
        try:
            target_job = Job.objects.filter(id=int(job_id)).first()
        except (ValueError, TypeError):
            pass
    if not target_job and job_title:
        target_job = Job.objects.filter(title__iexact=job_title.strip()).first()

    if not target_job:
        return JsonResponse({
            "status": "error",
            "message": "The job position you are applying for does not exist."
        }, status=400)

    if target_job.status not in Job.LIVE_STATUSES:
        return JsonResponse({
            "status": "error",
            "message": "This job posting is not currently live or active."
        }, status=400)

    if not target_job.employer:
        return JsonResponse({
            "status": "error",
            "message": "This job posting does not have an assigned owner employer."
        }, status=400)

    # 3. Prevent duplicate applications (same candidate_account + job)
    if Applicant.objects.filter(candidate_account=candidate_account, job=target_job).exists():
        return JsonResponse({
            "status": "error",
            "message": "You have already applied for this job position."
        }, status=400)

    # Handle resume file if uploaded in form, otherwise fall back to candidate account resume
    resume_file = request.FILES.get("resume")
    stored_filename = ""
    if resume_file:
        try:
            stored_filename = save_resume_file(resume_file) or ""
        except ValueError as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    else:
        stored_filename = candidate_account.resume or ""

    # Auto pre-fill fields from logged-in candidate account if not provided
    full_name = (data.get("full_name") or data.get("name") or candidate_account.full_name or "").strip()
    email = (data.get("email") or candidate_account.email or "").strip()
    phone = (data.get("phone") or data.get("mobile") or candidate_account.phone or "").strip()
    city = (data.get("city") or candidate_account.city or "").strip()
    state = (data.get("state") or candidate_account.state or "").strip()
    qualification = (data.get("qualification") or candidate_account.qualification or "").strip()
    skills = (data.get("skills") or candidate_account.skills or "").strip()
    current_company = (data.get("current_company") or candidate_account.current_company or "").strip()
    current_salary = (data.get("current_salary") or candidate_account.current_salary or "").strip()
    expected_salary = (data.get("expected_salary") or candidate_account.expected_salary or "").strip()
    availability = (data.get("availability") or candidate_account.availability or "").strip()

    try:
        experience = int(data.get("experience") or candidate_account.experience or 0)
    except (ValueError, TypeError):
        experience = 0

    applied_title = target_job.title or job_title or "General Applicant"
    target_employer = target_job.employer
    target_company = target_job.company or target_employer.company

    applicant = Applicant.objects.create(
        candidate_account=candidate_account,
        job=target_job,
        employer=target_employer,
        company=target_company,
        full_name=full_name,
        email=email,
        phone=phone,
        city=city,
        state=state,
        job_title=applied_title,
        qualification=qualification,
        experience=experience,
        skills=skills,
        current_company=current_company,
        current_salary=current_salary,
        expected_salary=expected_salary,
        availability=availability,
        cover_letter=(data.get("cover_letter") or "").strip(),
        resume=stored_filename,
        status="Application Submitted",
        approval_status="Pending",
        flow_step=2
    )

    from apps.candidates.status_helpers import set_applicant_status
    set_applicant_status(applicant, "Application Submitted", changed_by="candidate", notes="Application submitted by candidate online. Awaiting Super Admin approval.")

    log_activity(
        "candidate",
        "New candidate job application",
        f"{full_name} applied for {applied_title} ({phone}) - Pending Admin Approval"
    )

    return JsonResponse({
        "status": "success",
        "message": "Your application has been submitted successfully! You can track your application status in your Candidate Portal.",
        "applicant_id": applicant.id
    })


@require_http_methods(["POST"])
def upload_quick_resume(request):
    """Quick resume upload API from careers modal."""
    resume_file = request.FILES.get("resume")
    stored_filename = ""
    if resume_file:
        try:
            stored_filename = save_resume_file(resume_file) or ""
        except ValueError as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    form = request.POST
    is_valid, error_resp = validate_candidate_data(form)
    if not is_valid:
        return JsonResponse(error_resp, status=400)

    full_name = (form.get("full_name") or form.get("name") or "").strip()
    mobile = (form.get("mobile") or form.get("phone") or "").strip()
    email = (form.get("email") or "").strip()

    resume_obj = Resume.objects.filter(email__iexact=email, mobile=mobile, status__in=["New", "Pending"]).order_by('-id').first()
    if resume_obj:
        resume_obj.full_name = full_name
        if stored_filename:
            resume_obj.resume = stored_filename
        resume_obj.save()
    else:
        resume_obj = Resume.objects.create(
            full_name=full_name,
            mobile=mobile,
            email=email,
            city=form.get("city", ""),
            qualification=form.get("qualification", ""),
            experience=form.get("experience", ""),
            applying_for=form.get("applying_for", ""),
            message=form.get("message", ""),
            resume=stored_filename,
            status="New"
        )

    log_activity(
        "document",
        "New resume uploaded",
        f"{full_name} uploaded resume for {resume_obj.applying_for or 'General Profile'}"
    )

    return JsonResponse({
        "status": "success",
        "message": "Resume uploaded successfully! We will review your profile shortly."
    })


@require_http_methods(["GET"])
@admin_required
def get_applicants(request):
    q = request.GET.get("q", "").strip().lower()
    status_filter = request.GET.get("status", "").strip()

    queryset = Applicant.objects.exclude(job_title__icontains="intern").order_by('-id')
    if status_filter:
        queryset = queryset.filter(status__iexact=status_filter)

    results = []
    for a in queryset:
        if q:
            match = (
                q in a.full_name.lower() or
                q in a.email.lower() or
                q in a.phone.lower() or
                q in a.job_title.lower()
            )
            if not match:
                continue
        results.append(a.to_dict())

    return JsonResponse(results, safe=False)


@require_http_methods(["POST"])
@admin_required
def admin_create_applicant(request):
    """Admin endpoint to create a candidate."""
    if request.FILES.get("resume"):
        data = request.POST.copy()
        try:
            stored_file = save_resume_file(request.FILES["resume"])
            data["resume"] = stored_file
        except ValueError as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    else:
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

    is_valid, error_resp = validate_candidate_data(data)
    if not is_valid:
        return JsonResponse(error_resp, status=400)

    full_name = (data.get("full_name") or data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or data.get("mobile") or "").strip()

    try:
        experience = int(data.get("experience") or 0)
    except (ValueError, TypeError):
        experience = 0

    target_job = None
    if data.get("job_id"):
        try:
            target_job = Job.objects.filter(id=int(data.get("job_id"))).first()
        except (ValueError, TypeError):
            pass

    target_job = None
    if data.get("job_id"):
        try:
            target_job = Job.objects.filter(id=int(data.get("job_id"))).first()
        except (ValueError, TypeError):
            pass

    target_employer = target_job.employer if (target_job and target_job.employer) else None
    target_company = target_job.company if (target_job and target_job.company) else (target_employer.company if target_employer else None)

    req_approval = str(data.get("approval_status") or "").strip()
    if req_approval == "Approved" and target_employer:
        init_approval_status = "Approved"
        init_flow_step = 4
        admin_user = AdminUser.objects.filter(id=request.session.get('admin_id')).first()
        admin_username = getattr(admin_user, 'email', 'Super Admin') if admin_user else "Super Admin"
        approved_at_val = timezone.now()
        approved_by_val = admin_username
    else:
        init_approval_status = "Pending"
        init_flow_step = 2
        approved_at_val = None
        approved_by_val = ""

    target_candidate_acc = None
    if email:
        target_candidate_acc = CandidateAccount.objects.filter(email__iexact=email).first()
    if not target_candidate_acc and phone:
        target_candidate_acc = CandidateAccount.objects.filter(phone=phone).first()

    applicant = Applicant.objects.create(
        candidate_account=target_candidate_acc,
        job=target_job,
        employer=target_employer,
        company=target_company,
        full_name=full_name,
        email=email,
        phone=phone,
        city=data.get("city", ""),
        state=data.get("state", ""),
        job_title=data.get("job_title", (target_job.title if target_job else "Candidate")),
        qualification=data.get("qualification", ""),
        experience=experience,
        skills=data.get("skills", ""),
        current_company=data.get("current_company", ""),
        current_salary=data.get("current_salary", ""),
        expected_salary=data.get("expected_salary", ""),
        availability=data.get("availability", ""),
        cover_letter=data.get("cover_letter", ""),
        resume=data.get("resume", "") or "",
        status=data.get("status", "Application Submitted"),
        approval_status=init_approval_status,
        approved_at=approved_at_val,
        approved_by=approved_by_val,
        flow_step=init_flow_step,
        notes=data.get("notes", "")
    )

    log_activity("candidate", "Job seeker added by Admin", f"{full_name} added ({applicant.job_title})")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.META.get('HTTP_ACCEPT', ''):
        return JsonResponse({"status": "success", "message": "Candidate added successfully!", "applicant": applicant.to_dict()})
    
    return redirect('/admin-panel/candidates/all/')


@admin_required
def applicant_detail(request, id):
    referer = request.headers.get('Referer', '') or request.META.get('HTTP_REFERER', '')

    # 1. Check if caller originated from Placements page
    if 'placements' in referer:
        from apps.placements.models import Placement
        p = Placement.objects.filter(id=id).first()
        if p:
            if request.method == "DELETE":
                c_name = p.candidate_name
                app = p.applicant
                p.delete()
                if app and app.status in ['Joined', 'Placed']:
                    from apps.candidates.status_helpers import set_applicant_status
                    set_applicant_status(app, 'Selected', changed_by='admin', notes='Placement record deleted by admin.', force_override=True)
                log_activity("placement", "Placement record deleted", f"Placement for {c_name} deleted")
                return JsonResponse({"status": "success", "message": f"Placement record for '{c_name}' deleted successfully."})
            elif request.method == "GET":
                return JsonResponse({"status": "success", "placement": p.to_dict()})

    # 2. Check if caller originated from Job Offers page
    if 'offers' in referer or 'job-offers' in referer:
        from apps.placements.models import JobOffer
        o = JobOffer.objects.filter(id=id).first()
        if o:
            if request.method == "DELETE":
                c_name = o.candidate_name
                app = o.applicant
                o.delete()
                if app and app.status in ['Offer Released', 'Offer Sent']:
                    from apps.candidates.status_helpers import set_applicant_status
                    set_applicant_status(app, 'Selected', changed_by='admin', notes='Job offer deleted by admin.', force_override=True)
                return JsonResponse({"status": "success", "message": f"Job offer for '{c_name}' deleted successfully."})
            elif request.method == "GET":
                return JsonResponse({"status": "success", "offer": o.to_dict()})

    # 3. Standard Applicant Lookup
    applicant = Applicant.objects.filter(id=id).first()

    # 4. Fallback if Applicant not found with this ID
    if not applicant:
        if request.method == "DELETE":
            from apps.placements.models import Placement, JobOffer
            from apps.accounts.models import CandidateAccount
            
            p = Placement.objects.filter(id=id).first()
            if p:
                c_name = p.candidate_name
                app = p.applicant
                p.delete()
                if app and app.status in ['Joined', 'Placed']:
                    from apps.candidates.status_helpers import set_applicant_status
                    set_applicant_status(app, 'Selected', changed_by='admin', notes='Placement record deleted by admin.', force_override=True)
                log_activity("placement", "Placement record deleted", f"Placement for {c_name} deleted")
                return JsonResponse({"status": "success", "message": f"Placement record for '{c_name}' deleted successfully."})

            o = JobOffer.objects.filter(id=id).first()
            if o:
                c_name = o.candidate_name
                app = o.applicant
                o.delete()
                if app and app.status in ['Offer Released', 'Offer Sent']:
                    from apps.candidates.status_helpers import set_applicant_status
                    set_applicant_status(app, 'Selected', changed_by='admin', notes='Job offer deleted by admin.', force_override=True)
                return JsonResponse({"status": "success", "message": f"Job offer for '{c_name}' deleted successfully."})

            ca = CandidateAccount.objects.filter(id=id).first()
            if ca:
                c_name = ca.full_name
                ca.delete()
                return JsonResponse({"status": "success", "message": f"Candidate registration for '{c_name}' deleted successfully."})

            r = Resume.objects.filter(id=id).first()
            if r:
                c_name = r.full_name
                delete_resume_file(r)
                r.delete()
                return JsonResponse({"status": "success", "message": f"Resume record for '{c_name}' deleted successfully."})

        elif request.method == "GET":
            from apps.placements.models import Placement, JobOffer
            p = Placement.objects.filter(id=id).first()
            if p: return JsonResponse({"status": "success", "placement": p.to_dict()})
            o = JobOffer.objects.filter(id=id).first()
            if o: return JsonResponse({"status": "success", "offer": o.to_dict()})

        return JsonResponse({"status": "error", "message": "Applicant not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(applicant.to_dict())

    elif request.method in ["PUT", "POST"]:
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        old_status = applicant.status or "Application Submitted"
        new_status = data.get("status")
        if "full_name" in data: applicant.full_name = data["full_name"]
        if "email" in data: applicant.email = data["email"]
        if "phone" in data: applicant.phone = data["phone"]
        if "city" in data: applicant.city = data["city"]
        if "state" in data: applicant.state = data["state"]
        if "job_title" in data: applicant.job_title = data["job_title"]
        if "qualification" in data: applicant.qualification = data["qualification"]
        if "experience" in data:
            try: applicant.experience = int(data["experience"])
            except (ValueError, TypeError): pass
        if "skills" in data: applicant.skills = data["skills"]
        if "current_company" in data: applicant.current_company = data["current_company"]
        if "current_salary" in data: applicant.current_salary = data["current_salary"]
        if "expected_salary" in data: applicant.expected_salary = data["expected_salary"]
        if "availability" in data: applicant.availability = data["availability"]
        if "cover_letter" in data: applicant.cover_letter = data["cover_letter"]
        if "notes" in data: applicant.notes = data["notes"]

        applicant.save()

        if new_status:
            from apps.candidates.status_helpers import set_applicant_status
            set_applicant_status(applicant, new_status, changed_by="admin", notes=data.get("notes") or f"Updated by Admin to {new_status}")
            if old_status != new_status:
                log_activity("candidate", "Applicant status changed", f"Candidate {applicant.full_name} status updated from '{old_status}' to '{new_status}'")

        return JsonResponse({"status": "success", "message": "Applicant updated successfully.", "applicant": applicant.to_dict()})

    elif request.method == "DELETE":
        if applicant.resume:
            delete_resume_file(applicant.resume)
        name = applicant.full_name
        applicant.delete()
        log_activity("candidate", "Candidate deleted", f"{name} record deleted by Admin")
        return JsonResponse({"status": "success", "message": "Applicant deleted successfully."})

    return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)


@require_http_methods(["GET"])
@admin_required
def get_resumes(request):
    resumes = Resume.objects.all().order_by('-id')
    return JsonResponse([r.to_dict() for r in resumes], safe=False)


@admin_required
def resume_detail(request, id):
    try:
        resume = Resume.objects.get(id=id)
    except Resume.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Resume not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(resume.to_dict())

    elif request.method in ["PUT", "POST"]:
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        old_status = resume.status
        if "full_name" in data: resume.full_name = data["full_name"]
        if "mobile" in data: resume.mobile = data["mobile"]
        if "email" in data: resume.email = data["email"]
        if "city" in data: resume.city = data["city"]
        if "applying_for" in data: resume.applying_for = data["applying_for"]
        if "status" in data: resume.status = data["status"]
        if "notes" in data: resume.notes = data["notes"]

        resume.save()
        if old_status != resume.status:
            log_activity("candidate", "Resume status changed", f"Resume candidate {resume.full_name} status updated from '{old_status}' to '{resume.status}'")

        return JsonResponse({"status": "success", "message": "Resume record updated.", "resume": resume.to_dict()})

    elif request.method == "DELETE":
        if resume.resume:
            delete_resume_file(resume.resume)
        resume.delete()
        log_activity("candidate", "Resume deleted", f"Resume record for {resume.full_name} deleted")
        return JsonResponse({"status": "success", "message": "Resume deleted successfully."})

    return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)


def send_honest_interview_email(candidate_name, candidate_email, job_role, interview_date_str, interview_time_str, interview_mode, location_or_link, notes):
    """Sends email invitation honestly based on SMTP configuration."""
    if not candidate_email:
        return False, "No email address provided for candidate."

    email_backend = getattr(settings, 'EMAIL_BACKEND', '')
    email_host = getattr(settings, 'EMAIL_HOST', '')
    email_host_user = getattr(settings, 'EMAIL_HOST_USER', '')

    is_smtp_configured = bool(email_host and email_host_user and 'console' not in email_backend.lower())

    if not is_smtp_configured:
        return False, "Email delivery bypassed: SMTP server credentials (EMAIL_HOST_USER) are not configured in settings."

    subject = f"Interview Invitation — Sky Vision Group of Consultancy ({job_role})"
    message_body = f"""Dear {candidate_name},

We are pleased to invite you for an interview for the position of '{job_role}' at Sky Vision Group of Consultancy.

Interview Details:
- Date: {interview_date_str}
- Time: {interview_time_str}
- Mode: {interview_mode}
{f'- Venue/Link: {location_or_link}' if location_or_link else ''}
{f'- Notes/Instructions: {notes}' if notes else ''}

Please confirm your availability by replying to this email.

Best regards,
Recruitment Team
Sky Vision Group of Consultancy
"""
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff;">
      <h2 style="color: #4650d6; margin-top: 0;">Interview Invitation</h2>
      <p>Dear <strong>{candidate_name}</strong>,</p>
      <p>We are pleased to invite you for an interview for <strong>{job_role}</strong> at Sky Vision Group of Consultancy.</p>
      
      <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 10px; padding: 16px; margin: 20px 0;">
        <p style="margin: 6px 0;">📅 <strong>Date:</strong> {interview_date_str}</p>
        <p style="margin: 6px 0;">⏰ <strong>Time:</strong> {interview_time_str}</p>
        <p style="margin: 6px 0;">📍 <strong>Mode:</strong> {interview_mode}</p>
        {f'<p style="margin: 6px 0;">🔗 <strong>Venue / Link:</strong> {location_or_link}</p>' if location_or_link else ''}
        {f'<p style="margin: 6px 0;">📝 <strong>Instructions:</strong> {notes}</p>' if notes else ''}
      </div>

      <p>Please reply to this email to confirm your availability.</p>
      <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">
      <p style="font-size: 13px; color: #64748b; margin: 0;">Sky Vision Group of Consultancy</p>
    </div>
    """

    try:
        from django.core.mail import EmailMultiAlternatives
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or email_host_user
        msg = EmailMultiAlternatives(subject, message_body, from_email, [candidate_email])
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)
        return True, None
    except Exception as e:
        return False, str(e)


@admin_required
def admin_schedule_interview(request):
    """Schedules an interview, updates candidate status, creates Interview record, and sends email honestly."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)

    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST

    raw_id = data.get("raw_id") or data.get("candidate_id")
    model_type = str(data.get("model") or data.get("candidate_type") or "applicant").strip().lower()

    if not raw_id:
        return JsonResponse({"status": "error", "message": "Candidate ID is required."}, status=400)

    try:
        valid_id = int(raw_id)
    except (ValueError, TypeError):
        return JsonResponse({"status": "error", "message": f"Invalid candidate ID '{raw_id}'."}, status=400)

    # Validate interview date & time and slot collision
    is_valid, error_resp, parsed_date, parsed_time = validate_interview_data(data)
    if not is_valid:
        return JsonResponse(error_resp, status=400)

    interview_mode = str(data.get("interview_mode") or "In-Person Office Interview").strip()
    location_or_link = str(data.get("location_or_link") or data.get("location") or "").strip()
    notes = str(data.get("notes") or "").strip()

    candidate_name = ""
    candidate_email = ""
    candidate_phone = ""
    job_role = ""
    applicant_obj = None
    resume_obj = None

    if model_type == "resume":
        try:
            resume_obj = Resume.objects.get(id=valid_id)
            resume_obj.status = "Interview"
            if notes:
                resume_obj.notes = f"Interview Scheduled on {parsed_date} at {parsed_time.strftime('%H:%M')} ({interview_mode}). {notes}"
            resume_obj.save()
            candidate_name = resume_obj.full_name
            candidate_email = resume_obj.email
            candidate_phone = resume_obj.mobile
            job_role = resume_obj.applying_for or "Candidate Profile"
        except Resume.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Resume record not found."}, status=404)

    elif model_type == "internship":
        try:
            from apps.internships.models import InternshipEnquiry
            int_obj = InternshipEnquiry.objects.get(id=valid_id)
            int_obj.status = "Interview"
            if notes:
                int_obj.notes = f"Interview Scheduled on {parsed_date} at {parsed_time.strftime('%H:%M')} ({interview_mode}). {notes}"
            int_obj.save()
            candidate_name = int_obj.full_name
            candidate_email = int_obj.email
            candidate_phone = int_obj.phone
            job_role = f"Internship ({int_obj.course_stream or 'General'})"
        except Exception:
            return JsonResponse({"status": "error", "message": "Internship record not found."}, status=404)

    elif model_type in ["candidate_account", "candidate", "candidateaccount"]:
        try:
            from apps.accounts.models import CandidateAccount
            cand_obj = CandidateAccount.objects.get(id=valid_id)
            was_already_approved = cand_obj.is_approved
            cand_obj.is_approved = True
            cand_obj.approval_status = 'approved'
            cand_obj.save()
            if not was_already_approved:
                from apps.candidate_portal.notifications import notify_candidate_approved
                notify_candidate_approved(cand_obj)
            candidate_name = cand_obj.full_name
            candidate_email = cand_obj.email
            candidate_phone = cand_obj.phone
            job_role = cand_obj.qualification or "Registered Candidate"
        except CandidateAccount.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Candidate Account record not found."}, status=404)

    else: # applicant
        try:
            applicant_obj = Applicant.objects.get(id=valid_id)
            candidate_name = applicant_obj.full_name
            candidate_email = applicant_obj.email
            candidate_phone = applicant_obj.phone
            job_role = applicant_obj.job_title or "Job Seeker"
            from apps.candidates.status_helpers import set_applicant_status
            set_applicant_status(
                applicant_obj,
                "Interview",
                changed_by="admin",
                notes=f"Interview Scheduled on {parsed_date} at {parsed_time.strftime('%H:%M')} ({interview_mode}). {notes}",
                force_override=True
            )
        except Applicant.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Applicant record not found."}, status=404)

    # Create Interview database record
    interview = Interview.objects.create(
        candidate_type=model_type,
        applicant=applicant_obj,
        resume=resume_obj,
        candidate_id=valid_id,
        candidate_name=candidate_name,
        candidate_email=candidate_email,
        candidate_phone=candidate_phone,
        job_title=job_role,
        interview_date=parsed_date,
        interview_time=parsed_time,
        interview_mode=interview_mode,
        location_or_link=location_or_link,
        status="Scheduled",
        interviewer_notes=notes
    )

    # Send email
    email_sent, email_err = send_honest_interview_email(
        candidate_name=candidate_name,
        candidate_email=candidate_email,
        job_role=job_role,
        interview_date_str=parsed_date.strftime("%d %b %Y"),
        interview_time_str=parsed_time.strftime("%I:%M %p"),
        interview_mode=interview_mode,
        location_or_link=location_or_link,
        notes=notes
    )

    log_activity(
        "candidate",
        "Interview Scheduled",
        f"Scheduled interview for {candidate_name} on {parsed_date} at {parsed_time.strftime('%H:%M')} ({candidate_email})"
    )

    msg_text = f"✓ Interview scheduled successfully for '{candidate_name}'!"
    if email_sent:
        msg_text += f" Invitation email sent to {candidate_email}."
    elif candidate_email:
        msg_text += f" Note: {email_err}"

    return JsonResponse({
        "status": "success",
        "message": msg_text,
        "interview": interview.to_dict(),
        "email_sent": email_sent,
        "email_error": email_err
    })


@require_http_methods(["GET"])
@admin_required
def get_interviews(request):
    """List interviews with filters."""
    status_filter = request.GET.get("status", "").strip()
    when_filter = request.GET.get("when", "").strip().lower()
    q = request.GET.get("q", "").strip().lower()
    from_date = request.GET.get("from", "").strip()
    to_date = request.GET.get("to", "").strip()

    qs = Interview.objects.all().order_by('-interview_date', '-interview_time')

    if status_filter:
        qs = qs.filter(status__iexact=status_filter)

    today = timezone.now().date()
    if when_filter == 'upcoming':
        qs = qs.filter(status__in=['Scheduled', 'Rescheduled'], interview_date__gte=today)
    elif when_filter == 'completed':
        qs = qs.filter(status='Completed')
    elif when_filter == 'cancelled':
        qs = qs.filter(status='Cancelled')
    elif when_filter == 'today':
        qs = qs.filter(interview_date=today)
    elif when_filter == 'overdue':
        qs = qs.filter(status__in=['Scheduled', 'Rescheduled'], interview_date__lt=today)

    if from_date:
        try:
            fd = datetime.strptime(from_date, "%Y-%m-%d").date()
            qs = qs.filter(interview_date__gte=fd)
        except ValueError:
            pass

    if to_date:
        try:
            td = datetime.strptime(to_date, "%Y-%m-%d").date()
            qs = qs.filter(interview_date__lte=td)
        except ValueError:
            pass

    results = []
    for iv in qs:
        dict_rep = iv.to_dict()
        if q:
            match = (
                q in iv.candidate_name.lower() or
                q in iv.candidate_email.lower() or
                q in iv.job_title.lower() or
                q in iv.interview_mode.lower()
            )
            if not match:
                continue
        results.append(dict_rep)

    return JsonResponse(results, safe=False)


@admin_required
def interview_detail(request, id):
    """GET, PUT, or DELETE an interview record."""
    try:
        interview = Interview.objects.get(id=id)
    except Interview.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Interview record not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(interview.to_dict())

    elif request.method == "PUT":
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        date_changed = "interview_date" in data or "interview_time" in data
        if date_changed:
            val_data = {
                "interview_date": data.get("interview_date", interview.interview_date.strftime("%Y-%m-%d")),
                "interview_time": data.get("interview_time", interview.interview_time.strftime("%H:%M"))
            }
            is_valid, error_resp, parsed_d, parsed_t = validate_interview_data(val_data, current_interview_id=interview.id)
            if not is_valid:
                return JsonResponse(error_resp, status=400)
            interview.interview_date = parsed_d
            interview.interview_time = parsed_t

        if "interview_mode" in data: interview.interview_mode = data["interview_mode"]
        if "location_or_link" in data: interview.location_or_link = data["location_or_link"]
        if "status" in data: interview.status = data["status"]
        if "result" in data: interview.result = data["result"]
        if "feedback" in data: interview.feedback = data["feedback"]
        if "cancel_reason" in data: interview.cancel_reason = data["cancel_reason"]
        if "interviewer_notes" in data: interview.interviewer_notes = data["interviewer_notes"]

        interview.save()
        log_activity("candidate", "Interview updated", f"Interview updated for {interview.candidate_name}")
        return JsonResponse({"status": "success", "message": "Interview updated successfully.", "interview": interview.to_dict()})

    elif request.method == "DELETE":
        name = interview.candidate_name
        interview.delete()
        log_activity("candidate", "Interview deleted", f"Interview deleted for {name}")
        return JsonResponse({"status": "success", "message": "Interview deleted successfully."})

    return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)


@admin_required
def reschedule_interview(request, id):
    """Reschedule an existing interview."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)

    try:
        interview = Interview.objects.get(id=id)
    except Interview.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Interview not found."}, status=404)

    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST

    is_valid, error_resp, parsed_d, parsed_t = validate_interview_data(data, current_interview_id=interview.id)
    if not is_valid:
        return JsonResponse(error_resp, status=400)

    interview.interview_date = parsed_d
    interview.interview_time = parsed_t
    if data.get("interview_mode"):
        interview.interview_mode = str(data["interview_mode"]).strip()
    if "location_or_link" in data:
        interview.location_or_link = str(data["location_or_link"]).strip()
    if data.get("notes"):
        interview.interviewer_notes = str(data["notes"]).strip()
    
    interview.status = "Rescheduled"
    interview.save()

    # Sync candidate status
    obj = interview.get_candidate_object()
    if obj:
        if isinstance(obj, Applicant):
            from apps.candidates.status_helpers import set_applicant_status
            set_applicant_status(
                obj,
                "Interview Scheduled",
                changed_by="admin",
                notes=f"Interview rescheduled to {parsed_d} at {parsed_t}",
                force_override=True
            )
        else:
            obj.status = "Interview"
            obj.save()

    email_sent, email_err = send_honest_interview_email(
        candidate_name=interview.candidate_name,
        candidate_email=interview.candidate_email,
        job_role=interview.job_title,
        interview_date_str=parsed_d.strftime("%d %b %Y"),
        interview_time_str=parsed_t.strftime("%I:%M %p"),
        interview_mode=interview.interview_mode,
        location_or_link=interview.location_or_link,
        notes=f"RESCHEDULED: {interview.interviewer_notes}"
    )

    log_activity(
        "candidate",
        "Interview Rescheduled",
        f"Interview rescheduled for {interview.candidate_name} to {parsed_d} at {parsed_t}"
    )

    msg_text = f"Interview rescheduled to {parsed_d.strftime('%d %b %Y')} at {parsed_t.strftime('%I:%M %p')}."
    if email_sent:
        msg_text += " Confirmation email sent to candidate."
    elif interview.candidate_email:
        msg_text += f" Note: {email_err}"

    return JsonResponse({
        "status": "success",
        "message": msg_text,
        "interview": interview.to_dict(),
        "email_sent": email_sent
    })


@admin_required
def complete_interview(request, id):
    """Mark an interview as completed with result and feedback."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)

    try:
        interview = Interview.objects.get(id=id)
    except Interview.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Interview not found."}, status=404)

    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST

    result = str(data.get("result") or "").strip()
    feedback = str(data.get("feedback") or "").strip()
    notes = str(data.get("interviewer_notes") or "").strip()

    if not result:
        return JsonResponse({"status": "error", "message": "Interview result selection is required."}, status=400)

    interview.status = "Completed"
    interview.result = result
    interview.feedback = feedback
    if notes:
        interview.interviewer_notes = notes
    interview.save()

    # Sync candidate status if result is Selected, Rejected, Shortlisted, etc.
    obj = interview.get_candidate_object()
    if not obj and interview.applicant:
        obj = interview.applicant
    if not obj and interview.candidate_type == 'applicant' and interview.candidate_id:
        obj = Applicant.objects.filter(id=interview.candidate_id).first()

    if obj:
        from apps.candidates.status_helpers import set_applicant_status
        target_status = result
        if result.lower() in ['selected', 'passed', 'cleared']:
            target_status = 'Selected'
        elif result.lower() in ['rejected', 'failed']:
            target_status = 'Rejected'
        elif result.lower() in ['shortlisted']:
            target_status = 'Shortlisted'
        elif result.lower() in ['placed', 'joined']:
            target_status = 'Joined'

        if isinstance(obj, Applicant):
            set_applicant_status(
                obj,
                target_status,
                changed_by='admin',
                notes=feedback or f"Interview marked as {result} by Admin",
                force_override=True
            )
        else:
            obj.status = target_status
            obj.save()

    log_activity(
        "candidate",
        "Interview Completed",
        f"Interview completed for {interview.candidate_name}. Result: {result}"
    )

    return JsonResponse({
        "status": "success",
        "message": f"Interview for '{interview.candidate_name}' marked as Completed ({result}).",
        "interview": interview.to_dict()
    })


@admin_required
def cancel_interview(request, id):
    """Cancel an interview."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)

    try:
        interview = Interview.objects.get(id=id)
    except Interview.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Interview not found."}, status=404)

    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST

    cancel_reason = str(data.get("cancel_reason") or data.get("reason") or "").strip()

    interview.status = "Cancelled"
    if cancel_reason:
        interview.cancel_reason = cancel_reason
    interview.save()

    log_activity(
        "candidate",
        "Interview Cancelled",
        f"Interview cancelled for {interview.candidate_name}. Reason: {cancel_reason or 'None provided'}"
    )

    return JsonResponse({
        "status": "success",
        "message": f"Interview for '{interview.candidate_name}' has been cancelled.",
        "interview": interview.to_dict()
    })
