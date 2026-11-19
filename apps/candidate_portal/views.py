import json
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from apps.accounts.models import CandidateAccount
from apps.accounts.auth_helpers import (
    candidate_required, admin_required, save_resume_file,
    get_client_ip, is_rate_limited, record_attempt, signer
)
from apps.candidates.models import Applicant, Interview
from apps.candidates.validators import EMAIL_REGEX, PHONE_REGEX
from apps.candidates.constants import CANDIDATE_PROGRESS_STEPS, get_candidate_step, get_badge_class
from apps.jobs.models import Job
from apps.internships.models import InternshipApplication, Internship
from apps.placements.models import JobOffer, Placement
from .models import ApplicationStatusHistory, CandidateSavedJob
from .notifications import (
    notify_candidate_registered, notify_candidate_approved, notify_candidate_rejected
)
from apps.enquiries.models import log_activity


# ==========================================
# PUBLIC CANDIDATE AUTH VIEWS & APIS
# ==========================================

@ensure_csrf_cookie
def candidate_register_view(request):
    if request.session.get('candidate_id'):
        return redirect('/candidate/dashboard/')
    if request.session.get('employer_id'):
        return redirect('/employer/dashboard/')
    return render(request, 'candidate_portal/register.html')


@ensure_csrf_cookie
def candidate_login_view(request):
    if request.session.get('candidate_id'):
        return redirect('/candidate/dashboard/')
    if request.session.get('employer_id'):
        return redirect('/employer/dashboard/')
    next_url = request.GET.get('next', '')
    return render(request, 'candidate_portal/login.html', {'next': next_url})


@ensure_csrf_cookie
def candidate_forgot_password_view(request):
    return render(request, 'candidate_portal/forgot_password.html')


@ensure_csrf_cookie
def candidate_reset_password_view(request):
    token = request.GET.get('token', '')
    return render(request, 'candidate_portal/reset_password.html', {'token': token})


@require_http_methods(["POST"])
def api_candidate_register(request):
    """Candidate self-registration. Sets account to pending admin approval."""
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
            file_obj = None
        else:
            data = request.POST.dict()
            file_obj = request.FILES.get('resume')

        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''
        confirm_password = data.get('confirm_password') or ''
        full_name = (data.get('full_name') or '').strip()
        phone = (data.get('phone') or '').strip()

        if not full_name:
            return JsonResponse({"status": "error", "message": "Full name is required."}, status=400)
        if not email or not EMAIL_REGEX.match(email):
            return JsonResponse({"status": "error", "message": "Valid email address is required."}, status=400)
        if not phone or not PHONE_REGEX.match(phone):
            return JsonResponse({"status": "error", "message": "Valid phone number is required (min 10 digits)."}, status=400)
        if not password or len(password) < 6:
            return JsonResponse({"status": "error", "message": "Password must be at least 6 characters."}, status=400)
        if confirm_password and password != confirm_password:
            return JsonResponse({"status": "error", "message": "Passwords do not match."}, status=400)

        if CandidateAccount.objects.filter(email=email).exists():
            return JsonResponse({"status": "error", "message": "An account with this email already exists."}, status=400)

        resume_filename = ""
        if file_obj:
            try:
                resume_filename = save_resume_file(file_obj)
            except ValueError as ve:
                return JsonResponse({"status": "error", "message": str(ve)}, status=400)

        exp_raw = data.get('experience')
        exp_val = 0
        if exp_raw is not None and str(exp_raw).strip() != '':
            try:
                exp_val = int(exp_raw)
            except (ValueError, TypeError):
                exp_val = 0

        candidate = CandidateAccount(
            email=email,
            full_name=full_name,
            phone=phone,
            city=(data.get('city') or '').strip(),
            state=(data.get('state') or '').strip(),
            qualification=(data.get('qualification') or '').strip(),
            experience=exp_val,
            skills=(data.get('skills') or '').strip(),
            current_company=(data.get('current_company') or '').strip(),
            current_salary=(data.get('current_salary') or '').strip(),
            expected_salary=(data.get('expected_salary') or '').strip(),
            availability=(data.get('availability') or '').strip(),
            resume=resume_filename,
            is_approved=False,
            approval_status='pending'
        )
        candidate.set_password(password)
        candidate.save()

        # Send notification
        notify_candidate_registered(candidate)

        # Do not auto-login pending candidate; approval is required first
        request.session.pop('candidate_id', None)
        request.session.pop('employer_id', None)

        return JsonResponse({
            "status": "success",
            "message": "Registration successful! Your account is pending admin approval.",
            "redirect_url": "/candidate/login/"
        }, status=201)

    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Server error: {str(e)}"}, status=500)


@require_http_methods(["POST"])
def api_candidate_login(request):
    """Candidate login. Allows registered candidates to log in and apply for jobs."""
    try:
        ip = get_client_ip(request)
        if is_rate_limited(f"cand_login_{ip}", limit=10, window=900):
            return JsonResponse({"status": "error", "message": "Too many failed attempts. Please try again in 15 minutes."}, status=429)

        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST.dict()

        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''
        next_url = data.get('next') or '/candidate/dashboard/'

        if not email or not password:
            return JsonResponse({"status": "error", "message": "Email and password are required."}, status=400)

        record_attempt(f"cand_login_{ip}")

        try:
            candidate = CandidateAccount.objects.get(email=email)
        except CandidateAccount.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Invalid email or password."}, status=400)

        if not candidate.verify_password(password):
            return JsonResponse({"status": "error", "message": "Invalid email or password."}, status=400)

        if candidate.approval_status == 'rejected':
            reason_str = f" Reason: {candidate.rejection_reason}" if candidate.rejection_reason else ""
            return JsonResponse({
                "status": "error",
                "message": f"Your account registration was rejected by the admin.{reason_str}"
            }, status=403)

        if not candidate.is_approved or candidate.approval_status == 'pending':
            return JsonResponse({
                "status": "error",
                "message": "Your account registration is pending admin approval. You will be able to log in once approved."
            }, status=403)

        # Successful login: set candidate session and pop any existing employer session
        request.session.pop('employer_id', None)
        request.session['candidate_id'] = candidate.id
        request.session.cycle_key()

        return JsonResponse({
            "status": "success",
            "message": "Login successful.",
            "redirect_url": next_url,
            "candidate": candidate.to_dict()
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Server error: {str(e)}"}, status=500)


def api_candidate_logout(request):
    request.session.flush()
    if request.path.startswith('/api/'):
        return JsonResponse({"status": "success", "message": "Logged out successfully."})
    return redirect('/')


@require_http_methods(["POST"])
def api_candidate_forgot_password(request):
    try:
        data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST.dict()
        email = (data.get('email') or '').strip().lower()

        if not email:
            return JsonResponse({"status": "error", "message": "Email address is required."}, status=400)

        try:
            candidate = CandidateAccount.objects.get(email=email)
            token = signer.sign(candidate.email)
            reset_url = f"{settings.SITE_URL}/candidate/reset-password/?token={token}"
            
            subject = "Password Reset - Sky Vision Candidate Portal"
            message = (
                f"Hello {candidate.full_name},\n\n"
                f"You requested a password reset for your Sky Vision Candidate Account.\n"
                f"Click the link below to reset your password (link expires in 30 minutes):\n"
                f"{reset_url}\n\n"
                f"If you did not request this, please ignore this email."
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[candidate.email],
                fail_silently=True
            )
        except CandidateAccount.DoesNotExist:
            pass # Silent fail to prevent email enumeration

        return JsonResponse({
            "status": "success",
            "message": "If an account with that email exists, a password reset link has been sent."
        })
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@require_http_methods(["POST"])
def api_candidate_reset_password(request):
    try:
        data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST.dict()
        token = data.get('token')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if not token or not new_password:
            return JsonResponse({"status": "error", "message": "Token and new password are required."}, status=400)
        if len(new_password) < 6:
            return JsonResponse({"status": "error", "message": "Password must be at least 6 characters."}, status=400)
        if confirm_password and new_password != confirm_password:
            return JsonResponse({"status": "error", "message": "Passwords do not match."}, status=400)

        try:
            email = signer.unsign(token, max_age=1800) # 30 minutes
        except (BadSignature, SignatureExpired):
            return JsonResponse({"status": "error", "message": "Invalid or expired password reset link. Please request a new link."}, status=400)

        candidate = CandidateAccount.objects.get(email=email)
        candidate.set_password(new_password)
        candidate.save()

        return JsonResponse({"status": "success", "message": "Password reset successful. You can now log in with your new password."})

    except CandidateAccount.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Candidate account not found."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# ==========================================
# CANDIDATE PORTAL PROTECTED VIEWS & APIS
# ==========================================

@ensure_csrf_cookie
@candidate_required
def candidate_dashboard_view(request):
    candidate = request.candidate_user
    
    # Query live jobs (posted by admin or approved employers)
    live_jobs_qs = Job.objects.filter(status__in=Job.LIVE_STATUSES).select_related('company', 'employer').order_by('-id')

    # Get applied job IDs for this candidate
    applied_job_ids = set(
        Applicant.objects.filter(candidate_account=candidate, job__isnull=False).values_list('job_id', flat=True)
    )

    # Get saved job IDs for this candidate
    saved_job_ids = set(
        CandidateSavedJob.objects.filter(candidate_account=candidate, job__isnull=False).values_list('job_id', flat=True)
    )

    jobs_data = []
    for j in live_jobs_qs:
        company_display = ""
        if j.company and j.company.name:
            company_display = j.company.name
        elif j.employer and j.employer.company_name:
            company_display = j.employer.company_name
        else:
            company_display = "Sky Vision Partner"

        jobs_data.append({
            "id": j.id,
            "title": j.title,
            "company_name": company_display,
            "location": j.location or "Lucknow, Uttar Pradesh",
            "employment_type": j.employment_type or "Full Time",
            "experience": j.experience or "Fresher / Experienced",
            "salary": j.salary or "Best in Industry",
            "vacancies": j.vacancies or "1",
            "qualification": j.qualification or "Any Graduate / Relevant Skills",
            "description": j.description or "",
            "requirements": j.requirements or "",
            "deadline": j.deadline or "",
            "created_at": j.created_at.strftime("%d %b %Y") if j.created_at else "",
            "is_applied": j.id in applied_job_ids,
            "is_saved": j.id in saved_job_ids,
        })

    # Candidate stats
    app_count = Applicant.objects.filter(candidate_account=candidate).count()
    app_ids = list(Applicant.objects.filter(candidate_account=candidate).values_list('id', flat=True))
    interview_count = Interview.objects.filter(applicant_id__in=app_ids).count()
    offer_count = JobOffer.objects.filter(applicant_id__in=app_ids).count()
    saved_count = len(saved_job_ids)

    from apps.communication.models import MessageRecipient
    recent_messages = MessageRecipient.objects.filter(
        candidate_account=candidate,
        channel='dashboard',
        delivery_status='Sent'
    ).select_related('bulk_message').order_by('-id')[:5]

    return render(request, 'candidate_portal/dashboard.html', {
        'candidate': candidate,
        'jobs': jobs_data,
        'jobs_json': json.dumps(jobs_data),
        'applied_job_ids': list(applied_job_ids),
        'saved_job_ids': list(saved_job_ids),
        'stats': {
            'applied': app_count,
            'interviews': interview_count,
            'offers': offer_count,
            'saved': saved_count
        },
        'recent_messages': recent_messages
    })


@candidate_required
def api_candidate_jobs(request):
    """Returns live jobs with filter by query / location and candidate-specific applied/saved flags."""
    candidate = request.candidate_user
    q = (request.GET.get('q') or '').strip().lower()
    loc = (request.GET.get('location') or '').strip().lower()

    qs = Job.objects.filter(status__in=Job.LIVE_STATUSES).select_related('company', 'employer').order_by('-id')

    if q:
        qs = qs.filter(
            models.Q(title__icontains=q) |
            models.Q(category__icontains=q) |
            models.Q(department__icontains=q) |
            models.Q(description__icontains=q) |
            models.Q(company__name__icontains=q) |
            models.Q(employer__company_name__icontains=q)
        )

    if loc:
        loc_parts = [p.strip() for p in loc.split(',') if p.strip()]
        loc_filter = models.Q()
        for lp in loc_parts:
            loc_filter |= models.Q(location__icontains=lp)
        qs = qs.filter(loc_filter)

    applied_job_ids = set(
        Applicant.objects.filter(candidate_account=candidate, job__isnull=False).values_list('job_id', flat=True)
    )
    saved_job_ids = set(
        CandidateSavedJob.objects.filter(candidate_account=candidate, job__isnull=False).values_list('job_id', flat=True)
    )

    jobs_data = []
    for j in qs:
        company_display = ""
        if j.company and j.company.name:
            company_display = j.company.name
        elif j.employer and j.employer.company_name:
            company_display = j.employer.company_name
        else:
            company_display = "Sky Vision Partner"

        jobs_data.append({
            "id": j.id,
            "title": j.title,
            "company_name": company_display,
            "location": j.location or "Lucknow, Uttar Pradesh",
            "employment_type": j.employment_type or "Full Time",
            "experience": j.experience or "Fresher / Experienced",
            "salary": j.salary or "Best in Industry",
            "vacancies": j.vacancies or "1",
            "qualification": j.qualification or "Any Graduate / Relevant Skills",
            "description": j.description or "",
            "requirements": j.requirements or "",
            "deadline": j.deadline or "",
            "created_at": j.created_at.strftime("%d %b %Y") if j.created_at else "",
            "is_applied": j.id in applied_job_ids,
            "is_saved": j.id in saved_job_ids,
        })

    return JsonResponse({
        "status": "success",
        "jobs": jobs_data,
        "count": len(jobs_data)
    })


@candidate_required
@require_http_methods(["POST"])
def api_candidate_apply_job(request):
    """Directly applies to a job from the candidate dashboard."""
    try:
        candidate = request.candidate_user

        if not candidate.is_approved or candidate.approval_status != 'approved':
            return JsonResponse({
                "status": "error",
                "message": "Your account is pending admin approval. You cannot apply for jobs until approved."
            }, status=403)

        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
            file_obj = None
        else:
            data = request.POST.dict()
            file_obj = request.FILES.get('resume')

        job_id = data.get('job_id')
        if not job_id:
            return JsonResponse({"status": "error", "message": "Job ID is required."}, status=400)

        job = Job.objects.filter(id=job_id).select_related('company', 'employer').first()
        if not job:
            return JsonResponse({"status": "error", "message": "The selected job does not exist."}, status=404)

        if job.status not in Job.LIVE_STATUSES:
            return JsonResponse({"status": "error", "message": "This job posting is not active."}, status=400)

        # Check duplicate application
        if Applicant.objects.filter(candidate_account=candidate, job=job).exists():
            return JsonResponse({
                "status": "error",
                "message": "You have already applied for this job."
            }, status=400)

        # Resume handling
        resume_filename = candidate.resume or ""
        if file_obj:
            try:
                resume_filename = save_resume_file(file_obj)
            except ValueError as ve:
                return JsonResponse({"status": "error", "message": str(ve)}, status=400)

        if not resume_filename:
            return JsonResponse({
                "status": "error",
                "message": "Please upload a resume in your profile or with your application to apply."
            }, status=400)

        target_employer = job.employer
        target_company = job.company or (target_employer.company if target_employer else None)

        applicant = Applicant.objects.create(
            candidate_account=candidate,
            job=job,
            employer=target_employer,
            company=target_company,
            full_name=candidate.full_name,
            email=candidate.email,
            phone=candidate.phone,
            city=candidate.city or job.location or "Lucknow",
            state=candidate.state or "Uttar Pradesh",
            job_title=job.title,
            qualification=candidate.qualification or job.qualification or "",
            experience=candidate.experience or 0,
            skills=candidate.skills or "",
            current_company=candidate.current_company or "",
            current_salary=candidate.current_salary or "",
            expected_salary=candidate.expected_salary or "",
            availability=candidate.availability or "Immediate Joiner",
            cover_letter=(data.get('cover_letter') or '').strip(),
            resume=resume_filename,
            status="Application Submitted",
            approval_status="Pending",
            flow_step=2
        )

        from apps.candidates.status_helpers import set_applicant_status
        set_applicant_status(
            applicant,
            "Application Submitted",
            changed_by="candidate",
            notes="Application submitted by candidate via Candidate Dashboard. Awaiting Super Admin approval."
        )

        return JsonResponse({
            "status": "success",
            "message": "Application submitted successfully! Your application is under review.",
            "applicant_id": applicant.id,
            "job_id": job.id
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Server error: {str(e)}"}, status=500)

@ensure_csrf_cookie
@candidate_required
def candidate_profile_view(request):
    return render(request, 'candidate_portal/profile.html', {'candidate': request.candidate_user})

@ensure_csrf_cookie
@candidate_required
def candidate_applied_jobs_view(request):
    return render(request, 'candidate_portal/applied_jobs.html', {'candidate': request.candidate_user})

@ensure_csrf_cookie
@candidate_required
def candidate_saved_jobs_view(request):
    return render(request, 'candidate_portal/saved_jobs.html', {'candidate': request.candidate_user})

@candidate_required
def candidate_interviews_view(request):
    return render(request, 'candidate_portal/interviews.html', {'candidate': request.candidate_user})

@candidate_required
def candidate_offers_view(request):
    return render(request, 'candidate_portal/offers.html', {'candidate': request.candidate_user})

@candidate_required
def candidate_documents_view(request):
    return render(request, 'candidate_portal/documents.html', {'candidate': request.candidate_user})


@candidate_required
def candidate_internships_view(request):
    candidate = request.candidate_user
    intern_filter = (
        models.Q(email__iexact=candidate.email) & models.Q(phone=candidate.phone)
    ) if (candidate.email and candidate.phone) else models.Q(email__iexact=candidate.email)

    internships = list(
        InternshipApplication.objects.filter(intern_filter)
        .select_related('internship', 'internship__provider')
        .order_by('-id')
    )

    pending_count = sum(1 for a in internships if (a.status or '').strip() in ['Pending', 'New', ''])
    shortlisted_count = sum(1 for a in internships if (a.status or '').strip() == 'Shortlisted')
    selected_count = sum(1 for a in internships if (a.status or '').strip() == 'Selected')
    rejected_count = sum(1 for a in internships if (a.status or '').strip() == 'Rejected')

    return render(request, 'candidate_portal/internships.html', {
        'candidate': candidate,
        'internships': internships,
        'internships_count': len(internships),
        'pending_count': pending_count,
        'shortlisted_count': shortlisted_count,
        'selected_count': selected_count,
        'rejected_count': rejected_count,
    })


@candidate_required
def api_candidate_me(request):
    return JsonResponse({
        "status": "success",
        "candidate": request.candidate_user.to_dict()
    })


@candidate_required
@require_http_methods(["POST"])
def api_candidate_profile_update(request):
    try:
        candidate = request.candidate_user
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
            file_obj = None
        else:
            data = request.POST.dict()
            file_obj = request.FILES.get('resume')

        if 'full_name' in data:
            name_val = data['full_name'].strip()
            if name_val:
                candidate.full_name = name_val
        if 'phone' in data:
            phone_val = data['phone'].strip()
            if phone_val and PHONE_REGEX.match(phone_val):
                candidate.phone = phone_val
        if 'city' in data:
            candidate.city = data['city'].strip()
        if 'state' in data:
            candidate.state = data['state'].strip()
        if 'qualification' in data:
            candidate.qualification = data['qualification'].strip()
        if 'experience' in data:
            try:
                candidate.experience = int(data['experience'])
            except (ValueError, TypeError):
                pass
        if 'skills' in data:
            candidate.skills = data['skills'].strip()
        if 'current_company' in data:
            candidate.current_company = data['current_company'].strip()
        if 'current_salary' in data:
            candidate.current_salary = data['current_salary'].strip()
        if 'expected_salary' in data:
            candidate.expected_salary = data['expected_salary'].strip()
        if 'availability' in data:
            candidate.availability = data['availability'].strip()
        if 'email_notifications_enabled' in data:
            val = data['email_notifications_enabled']
            candidate.email_notifications_enabled = str(val).lower() in ['true', '1', 'yes', 'on']

        if file_obj:
            try:
                candidate.resume = save_resume_file(file_obj)
            except ValueError as ve:
                return JsonResponse({"status": "error", "message": str(ve)}, status=400)

        candidate.save()

        return JsonResponse({
            "status": "success",
            "message": "Profile updated successfully.",
            "candidate": candidate.to_dict()
        })
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@candidate_required
def api_candidate_dashboard_stats(request):
    """Returns dashboard counts and recent applications for logged-in candidate."""
    candidate = request.candidate_user
    
    # Strictly filter by candidate_account to ensure complete candidate isolation
    applications = Applicant.objects.filter(candidate_account=candidate).distinct()

    app_ids = list(applications.values_list('id', flat=True))
    app_count = applications.count()
    
    interviews = Interview.objects.filter(applicant_id__in=app_ids)
    interview_count = interviews.count()

    offers = JobOffer.objects.filter(applicant_id__in=app_ids)
    offer_count = offers.count()

    saved_count = CandidateSavedJob.objects.filter(candidate_account=candidate).count()
    intern_filter = (
        models.Q(email__iexact=candidate.email) & models.Q(phone=candidate.phone)
    ) if (candidate.email and candidate.phone) else models.Q(email__iexact=candidate.email)
    internship_count = InternshipApplication.objects.filter(intern_filter).count()

    recent_apps = []
    for app in applications.order_by('-id')[:5]:
        status_val = app.status if (app.status and app.status.strip()) else "Application Submitted"
        step_idx = get_candidate_step(status_val)
        recent_apps.append({
            "id": app.id,
            "job_title": app.job_title or "Job Opening",
            "status": status_val,
            "step_index": step_idx,
            "badge_class": get_badge_class(status_val),
            "applied_on": app.applied_on.strftime("%Y-%m-%d") if app.applied_on else ""
        })

    return JsonResponse({
        "status": "success",
        "stats": {
            "applied_jobs": app_count,
            "interviews": interview_count,
            "offers": offer_count,
            "saved_jobs": saved_count,
            "internships": internship_count,
        },
        "recent_applications": recent_apps
    })


@candidate_required
def api_candidate_internships(request):
    """Lists all internship applications for the logged-in candidate with status tracking."""
    candidate = request.candidate_user
    intern_filter = (
        models.Q(email__iexact=candidate.email) & models.Q(phone=candidate.phone)
    ) if (candidate.email and candidate.phone) else models.Q(email__iexact=candidate.email)
    internships = InternshipApplication.objects.filter(intern_filter).select_related('internship', 'internship__provider').order_by('-id')

    result = []
    for a in internships:
        st = (a.status or "Pending").strip()
        if st in ["Pending", "New"]:
            step_idx = 1
            badge_class = "warning"
            status_label = "Application Under Review"
        elif st == "Shortlisted":
            step_idx = 2
            badge_class = "primary"
            status_label = "Profile Shortlisted"
        elif st == "Selected":
            step_idx = 3
            badge_class = "success"
            status_label = "Selected for Internship"
        elif st == "Rejected":
            step_idx = 0
            badge_class = "danger"
            status_label = "Not Selected"
        else:
            step_idx = 1
            badge_class = "info"
            status_label = st

        result.append({
            "id": a.id,
            "internship_id": a.internship_id,
            "title": a.internship.title if a.internship else "Internship Track",
            "provider_name": a.internship.provider.name if (a.internship and a.internship.provider) else "Sky Vision Consultancy",
            "location": a.internship.location if a.internship else "Lucknow, UP",
            "mode": a.internship.mode if a.internship else "Work From Home / Remote",
            "duration": a.internship.duration if a.internship else "3 Months",
            "stipend": a.internship.stipend if a.internship else "Performance Based",
            "college": a.college,
            "course_stream": a.course_stream,
            "skills": a.skills,
            "message": a.message,
            "notes": a.notes,
            "status": st,
            "status_label": status_label,
            "badge_class": badge_class,
            "step_index": step_idx,
            "resume_url": f"/api/admin/files/download/{a.resume}" if a.resume else "",
            "created_at": a.created_at.strftime("%d %b %Y, %I:%M %p") if a.created_at else "",
        })

    return JsonResponse({
        "status": "success",
        "internships": result,
        "count": len(result)
    })


@candidate_required
def api_candidate_applied_jobs(request):
    """Lists all job applications for the logged-in candidate with status tracking timeline (IDOR safe)."""
    candidate = request.candidate_user
    applications = Applicant.objects.filter(
        candidate_account=candidate
    ).select_related('job', 'job__employer', 'job__company').order_by('-id').distinct()

    result = []
    for app in applications:
        # Build timeline history
        history_qs = ApplicationStatusHistory.objects.filter(applicant=app).order_by('created_at')
        history_list = [h.to_dict() for h in history_qs]

        # Get job details if FK exists
        job_data = None
        if app.job:
            job_data = app.job.to_dict()

        status_val = app.status if (app.status and app.status.strip()) else "Application Submitted"
        step_idx = get_candidate_step(status_val)

        # Step 5: Interview
        interview_info = None
        iv = Interview.objects.filter(applicant=app).order_by('-id').first()
        if iv:
            interview_info = {
                "id": iv.id,
                "date": iv.interview_date.strftime("%Y-%m-%d") if iv.interview_date else "",
                "time": iv.interview_time.strftime("%H:%M") if iv.interview_time else "",
                "mode": iv.interview_mode or "",
                "location_or_link": iv.location_or_link or "",
                "status": iv.status or ""
            }

        # Step 6: Offer Released
        offer_info = None
        off = JobOffer.objects.filter(applicant=app).order_by('-id').first()
        if off:
            offer_info = {
                "id": off.id,
                "designation": off.designation or "",
                "offered_ctc": off.offered_ctc or "",
                "joining_date": off.joining_date or "",
                "status": off.status or ""
            }

        # Step 7: Placement / Joined
        placement_info = None
        pl = Placement.objects.filter(applicant=app).order_by('-id').first()
        if pl:
            placement_info = {
                "id": pl.id,
                "position": pl.position or "",
                "package": pl.package or "",
                "joining_date": pl.joining_date or "",
                "status": pl.status or ""
            }

        app_dict = app.to_dict()
        app_dict["status"] = status_val
        app_dict["interview"] = interview_info
        app_dict["offer"] = offer_info
        app_dict["placement"] = placement_info

        result.append({
            "application": app_dict,
            "job": job_data,
            "current_step": step_idx,
            "badge_class": get_badge_class(status_val),
            "steps": CANDIDATE_PROGRESS_STEPS,
            "history": history_list,
            "interview": interview_info,
            "offer": offer_info,
            "placement": placement_info
        })

    return JsonResponse({
        "status": "success",
        "applications": result
    })


@candidate_required
def api_candidate_saved_jobs(request):
    """GET list of saved jobs or POST toggle save/unsave a job (IDOR safe)."""
    candidate = request.candidate_user
    
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST.dict()
            job_id = data.get('job_id')
            job_title = (data.get('job_title') or '').strip()

            if not job_id and not job_title:
                return JsonResponse({"status": "error", "message": "Job ID or Job Title is required."}, status=400)

            job = None
            if job_id:
                job = Job.objects.filter(id=job_id).first()

            if not job and job_title:
                job = Job.objects.filter(title__iexact=job_title).first()
                if not job:
                    job = Job.objects.create(
                        title=job_title,
                        category="General",
                        location="Lucknow, UP",
                        employment_type="Full Time",
                        salary="Best in Industry",
                        status=Job.STATUS_LIVE
                    )

            if not job:
                return JsonResponse({"status": "error", "message": "Job not found."}, status=404)

            saved_item = CandidateSavedJob.objects.filter(candidate_account=candidate, job=job).first()

            if saved_item:
                saved_item.delete()
                return JsonResponse({"status": "success", "action": "unsaved", "message": "Job removed from saved jobs."})
            else:
                CandidateSavedJob.objects.create(candidate_account=candidate, job=job)
                return JsonResponse({"status": "success", "action": "saved", "message": "Job saved successfully."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    # GET request
    saved_qs = CandidateSavedJob.objects.filter(candidate_account=candidate).select_related('job', 'job__company', 'job__employer')
    jobs_list = []
    for item in saved_qs:
        if item.job:
            jdict = item.job.to_dict()
            jdict['saved_at'] = item.created_at.strftime("%Y-%m-%d")
            jobs_list.append(jdict)

    return JsonResponse({"status": "success", "jobs": jobs_list})


@candidate_required
def api_candidate_interviews(request):
    """Lists interviews for the logged-in candidate (IDOR safe)."""
    candidate = request.candidate_user
    app_ids = list(Applicant.objects.filter(candidate_account=candidate).values_list('id', flat=True))

    interviews = Interview.objects.filter(
        applicant_id__in=app_ids
    ).order_by('-interview_date', '-interview_time')

    result = [i.to_dict() for i in interviews]
    return JsonResponse({"status": "success", "interviews": result})


@candidate_required
def api_candidate_offers(request):
    """Lists Job Offers & Placements for the logged-in candidate (IDOR safe)."""
    candidate = request.candidate_user
    app_ids = list(Applicant.objects.filter(
        candidate_account=candidate
    ).values_list('id', flat=True))

    offers = JobOffer.objects.filter(
        applicant_id__in=app_ids
    ).distinct().order_by('-id')

    placements = Placement.objects.filter(
        applicant_id__in=app_ids
    ).distinct().order_by('-id')

    return JsonResponse({
        "status": "success",
        "job_offers": [o.to_dict() for o in offers],
        "offers": [o.to_dict() for o in offers],
        "placements": [p.to_dict() for p in placements]
    })


@candidate_required
def api_candidate_accept_offer(request, offer_id):
    """Candidate accepts an offer letter and confirms joining."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    candidate = request.candidate_user
    app_ids = list(Applicant.objects.filter(
        candidate_account=candidate
    ).values_list('id', flat=True))

    offer = JobOffer.objects.filter(
        id=offer_id,
        applicant_id__in=app_ids
    ).first()

    if not offer:
        return JsonResponse({"status": "error", "message": "Offer letter not found or unauthorized."}, status=404)

    offer.status = 'Accepted'
    offer.save(update_fields=['status'])

    # Create / Update Placement
    placement, created = Placement.objects.get_or_create(
        applicant=offer.applicant,
        defaults={
            'candidate_name': offer.candidate_name,
            'company_name': offer.company_name,
            'position': offer.designation,
            'package': offer.offered_ctc,
            'placement_date': timezone.now().strftime("%Y-%m-%d"),
            'joining_date': offer.joining_date or timezone.now().strftime("%Y-%m-%d"),
            'status': 'Joined',
            'notes': f"Candidate accepted offer and confirmed joining. {offer.notes or ''}"
        }
    )
    if not created:
        placement.status = 'Joined'
        if offer.offered_ctc:
            placement.package = offer.offered_ctc
        if offer.joining_date:
            placement.joining_date = offer.joining_date
        placement.save()

    if offer.applicant:
        from apps.candidates.status_helpers import set_applicant_status
        set_applicant_status(
            offer.applicant,
            'Joined',
            changed_by='candidate',
            notes='Candidate accepted offer letter and confirmed joining.',
            force_override=True
        )

    log_activity(
        "candidate",
        "Offer Accepted & Joined",
        f"Candidate {candidate.full_name} accepted offer from {offer.company_name} and confirmed joining."
    )

    return JsonResponse({
        "status": "success",
        "message": f"Congratulations! You have accepted the offer from {offer.company_name} and confirmed joining.",
        "offer": offer.to_dict(),
        "placement": placement.to_dict()
    })


# ==========================================
# ADMIN CANDIDATE APPROVAL MANAGEMENT (Phase 2)
# ==========================================

@admin_required
def admin_candidate_registrations_view(request):
    from apps.dashboard.views import admin_module_generic_view
    return admin_module_generic_view(request, 'candidates_registrations')


@admin_required
def api_admin_candidate_registrations(request):
    """Returns candidate registration list for admin approval with status filtering."""
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '').strip()

    qs = CandidateAccount.objects.all().order_by('-id')

    if status_filter != 'all':
        qs = qs.filter(approval_status=status_filter)

    if search_query:
        qs = qs.filter(
            models.Q(full_name__icontains=search_query) |
            models.Q(email__icontains=search_query) |
            models.Q(phone__icontains=search_query)
        )

    candidates_list = [c.to_dict() for c in qs]
    return JsonResponse({
        "status": "success",
        "candidates": candidates_list,
        "count": len(candidates_list)
    })


@admin_required
@require_http_methods(["POST"])
def api_admin_approve_candidate(request, candidate_id):
    """Admin approves candidate registration."""
    try:
        from django.db import transaction
        with transaction.atomic():
            candidate = CandidateAccount.objects.select_for_update().get(id=candidate_id)

            # If already approved, return success without resending duplicate emails
            if candidate.is_approved and candidate.approval_status == 'approved':
                return JsonResponse({
                    "status": "success",
                    "message": f"Candidate '{candidate.full_name}' is already approved.",
                    "candidate": candidate.to_dict()
                })

            candidate.is_approved = True
            candidate.approval_status = 'approved'
            candidate.rejection_reason = ""
            candidate.save()

        # Send approval notification email (safe against duplicates)
        email_sent = notify_candidate_approved(candidate)
        log_activity(
            action_type="Candidate Approved",
            title=f"Candidate '{candidate.full_name}' approved.",
            description=f"Admin approved candidate '{candidate.full_name}' ({candidate.email}). Approval email dispatched: {'Yes' if email_sent else 'Failed'}."
        )

        return JsonResponse({
            "status": "success",
            "message": f"Candidate '{candidate.full_name}' approved successfully. Approval notification email sent to {candidate.email}.",
            "candidate": candidate.to_dict()
        })
    except CandidateAccount.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Candidate not found."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@admin_required
@require_http_methods(["POST"])
def api_admin_reject_candidate(request, candidate_id):
    """Admin rejects candidate registration with reason."""
    try:
        candidate = get_object_or_404(CandidateAccount, id=candidate_id)
        data = json.loads(request.body.decode('utf-8')) if request.body else request.POST.dict()
        reason = (data.get('reason') or '').strip()

        candidate.is_approved = False
        candidate.approval_status = 'rejected'
        candidate.rejection_reason = reason
        candidate.save()

        # Send rejection notification email
        notify_candidate_rejected(candidate, reason=reason)

        return JsonResponse({
            "status": "success",
            "message": f"Candidate '{candidate.full_name}' registration rejected.",
            "candidate": candidate.to_dict()
        })
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@admin_required
@require_http_methods(["GET", "PUT", "DELETE"])
def api_admin_candidate_registration_detail(request, candidate_id):
    """View, update or delete a candidate registration record."""
    candidate = get_object_or_404(CandidateAccount, id=candidate_id)
    if request.method == "GET":
        return JsonResponse({"status": "success", "candidate": candidate.to_dict()})
    elif request.method == "DELETE":
        name = candidate.full_name
        candidate.delete()
        return JsonResponse({"status": "success", "message": f"Candidate registration for '{name}' deleted successfully."})
    elif request.method == "PUT":
        try:
            data = json.loads(request.body.decode('utf-8')) if request.body else request.POST.dict()
        except Exception:
            data = request.POST.dict()
        if 'name' in data or 'full_name' in data:
            candidate.full_name = data.get('full_name') or data.get('name')
        if 'email' in data: candidate.email = data['email']
        if 'phone' in data: candidate.phone = data['phone']
        if 'city' in data: candidate.city = data['city']
        if 'qualification' in data: candidate.qualification = data['qualification']
        candidate.save()
        return JsonResponse({"status": "success", "message": "Candidate registration updated.", "candidate": candidate.to_dict()})

