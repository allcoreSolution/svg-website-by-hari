import json
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings

from django.db import models, IntegrityError
from apps.accounts.models import EmployerAccount, AdminUser
from apps.accounts.auth_helpers import employer_required, save_employer_document_file, is_rate_limited, record_attempt, get_client_ip
from apps.companies.models import Company, CompanyContact, CompanyRequirement
from apps.jobs.models import Job
from apps.candidates.models import Applicant, Interview
from apps.placements.models import Placement, JobOffer
from apps.enquiries.models import log_activity
from apps.candidate_portal.notifications import notify_applicant_status_change, notify_interview_scheduled
from .notifications import notify_employer_registered, notify_employer_approved, notify_employer_rejected, notify_employer_suspended, notify_job_status_change


# ==========================================
# PUBLIC EMPLOYER AUTH & STATUS VIEWS
# ==========================================

def employer_hire_talent_view(request):
    """Smart router for 'Hire Talent' hero button."""
    employer_id = request.session.get('employer_id')
    if not employer_id:
        return redirect('/employer/login/')
    
    try:
        employer = EmployerAccount.objects.get(id=employer_id)
        if employer.status == 'APPROVED':
            return redirect('/employer/dashboard/')
        else:
            return redirect('/employer/pending/')
    except EmployerAccount.DoesNotExist:
        request.session.pop('employer_id', None)
        return redirect('/employer/login/')


@ensure_csrf_cookie
def employer_register_view(request):
    """Employer registration view (public)."""
    if request.session.get('employer_id'):
        return redirect('/employer/hire-talent/')
    if request.session.get('candidate_id'):
        return redirect('/candidate/dashboard/')

    if request.method == 'POST':
        company_name = request.POST.get('company_name', '').strip()
        contact_name = request.POST.get('contact_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        industry = request.POST.get('industry', '').strip()
        company_size = request.POST.get('company_size', '').strip()
        city = request.POST.get('city', '').strip() or 'Lucknow'
        state = request.POST.get('state', '').strip() or 'Uttar Pradesh'
        website = request.POST.get('website', '').strip()
        gst_number = request.POST.get('gst_number', '').strip()
        address = request.POST.get('address', '').strip()
        doc_file = request.FILES.get('document')

        # Basic validations
        errors = {}
        if not company_name:
            errors['company_name'] = 'Company name is required.'
        if not contact_name:
            errors['contact_name'] = 'Contact person name is required.'
        if not email or '@' not in email:
            errors['email'] = 'A valid email address is required.'

        # Check existing registration by email or phone
        existing_email = EmployerAccount.objects.filter(email__iexact=email).first() if email else None
        existing_phone = EmployerAccount.objects.filter(phone=phone).first() if phone else None

        if existing_email and existing_phone:
            if existing_email.id == existing_phone.id:
                errors['already_registered'] = f"Employer account for '{existing_email.company_name}' ({existing_email.email}) is already registered with this email and mobile number! Please log in."
            else:
                errors['already_registered'] = f"Email address '{email}' is registered to '{existing_email.company_name}', and mobile number '{phone}' is registered to '{existing_phone.company_name}'. Please log in or update your details."
        elif existing_email:
            errors['already_registered'] = f"Employer account for '{existing_email.company_name}' with email '{email}' is already registered! Please enter your password to log in."
        elif existing_phone:
            errors['already_registered'] = f"Mobile number '{phone}' is already registered to employer account '{existing_phone.company_name}' ({existing_phone.email}). Please log in or use a different mobile number."
        
        if not phone or len(phone) < 10:
            errors['phone'] = 'A valid 10-digit phone number is required.'
        if not password or len(password) < 6:
            errors['password'] = 'Password must be at least 6 characters long.'

        stored_doc = ""
        if doc_file:
            try:
                stored_doc = save_employer_document_file(doc_file) or ""
            except ValueError as ve:
                errors['document'] = str(ve)

        if errors:
            return render(request, 'employer_portal/register.html', {
                'errors': errors,
                'form_data': request.POST,
                'page_title': 'Employer Registration'
            })

        # Create or find associated Company
        company, _ = Company.objects.get_or_create(
            name=company_name,
            defaults={
                'industry': industry,
                'website': website,
                'email': email,
                'phone': phone,
                'address': address,
                'city': city,
                'state': state,
                'gst_number': gst_number,
                'status': 'Active'
            }
        )

        # Create EmployerAccount & primary contact
        try:
            employer = EmployerAccount(
                company=company,
                company_name=company_name,
                contact_name=contact_name,
                email=email,
                phone=phone,
                industry=industry,
                company_size=company_size,
                city=city,
                state=state,
                website=website,
                gst_number=gst_number,
                address=address,
                document=stored_doc,
                status='PENDING'
            )
            employer.set_password(password)
            employer.save()

            # Create CompanyContact primary contact record
            CompanyContact.objects.create(
                company=company,
                name=contact_name,
                designation='Employer Contact',
                email=email,
                phone=phone,
                is_primary=True,
                notes='Auto-created from Employer Portal Registration'
            )
        except IntegrityError:
            errors['already_registered'] = f"An account with email '{email}' or phone '{phone}' is already registered! Please log in or use different details."
            return render(request, 'employer_portal/register.html', {
                'errors': errors,
                'form_data': request.POST,
                'page_title': 'Employer Registration'
            })

        # Log activity & notify employer
        log_activity(
            action_type="Employer Registered",
            title=f"Employer '{company_name}' registered.",
            description=f"New employer registration submitted for '{company_name}' ({contact_name}, {email})."
        )
        notify_employer_registered(employer)

        # Store employer ID in session and clear candidate session
        request.session.pop('candidate_id', None)
        request.session['employer_id'] = employer.id
        return redirect('/employer/pending/')

    return render(request, 'employer_portal/register.html', {'page_title': 'Employer Registration'})


@ensure_csrf_cookie
def employer_login_view(request):
    """Employer login view."""
    next_url = request.GET.get('next', '/employer/dashboard/')
    if request.session.get('employer_id'):
        return redirect('/employer/hire-talent/')
    if request.session.get('candidate_id'):
        return redirect('/candidate/dashboard/')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        client_ip = get_client_ip(request)
        if is_rate_limited(f"emp_login_{client_ip}", limit=10, window=300):
            return render(request, 'employer_portal/login.html', {
                'error': 'Too many failed login attempts. Please try again in 5 minutes.',
                'email': email,
                'next': next_url,
                'page_title': 'Employer Login'
            })

        try:
            employer = EmployerAccount.objects.get(email=email)
            if not employer.verify_password(password):
                record_attempt(f"emp_login_{client_ip}")
                return render(request, 'employer_portal/login.html', {
                    'error': 'Invalid email or password.',
                    'email': email,
                    'next': next_url,
                    'page_title': 'Employer Login'
                })

            if employer.status == 'PENDING':
                request.session.pop('candidate_id', None)
                request.session['employer_id'] = employer.id
                return render(request, 'employer_portal/login.html', {
                    'warning': 'Your employer account registration is pending admin approval. You can track status on the review page.',
                    'email': email,
                    'is_pending': True,
                    'next': next_url,
                    'page_title': 'Employer Login'
                })
            elif employer.status in ['REJECTED', 'SUSPENDED']:
                request.session.pop('candidate_id', None)
                request.session['employer_id'] = employer.id
                return redirect('/employer/pending/')

            # Approved -> Login Success
            request.session.pop('candidate_id', None)
            request.session['employer_id'] = employer.id
            log_activity(
                action_type="Employer Login",
                title=f"Employer '{employer.company_name}' logged in.",
                description=f"Employer '{employer.company_name}' logged in successfully."
            )
            return redirect(next_url)

        except EmployerAccount.DoesNotExist:
            record_attempt(f"emp_login_{client_ip}")
            return render(request, 'employer_portal/login.html', {
                'error': 'Invalid email or password.',
                'email': email,
                'next': next_url,
                'page_title': 'Employer Login'
            })

    email_get = request.GET.get('email', '').strip()
    return render(request, 'employer_portal/login.html', {'email': email_get, 'next': next_url, 'page_title': 'Employer Login'})


def employer_logout_view(request):
    """Employer logout view."""
    request.session.flush()
    return redirect('/')


def employer_pending_view(request):
    """Pending/Status review page for employers."""
    employer_id = request.session.get('employer_id')
    if not employer_id:
        return redirect('/employer/login/')

    try:
        employer = EmployerAccount.objects.get(id=employer_id)
        if employer.status == 'APPROVED':
            return redirect('/employer/dashboard/')
        return render(request, 'employer_portal/pending.html', {
            'employer': employer,
            'page_title': 'Registration Status — Sky Vision Employer'
        })
    except EmployerAccount.DoesNotExist:
        request.session.pop('employer_id', None)
        return redirect('/employer/login/')


# ==========================================
# EMPLOYER DASHBOARD & JOBS VIEWS (PROTECTED)
# ==========================================

@employer_required
def employer_dashboard_view(request):
    """Employer Dashboard main page."""
    employer = request.employer_user

    job_filter = models.Q(employer=employer)
    if getattr(employer, 'shares_company_data', False) and getattr(employer, 'company', None):
        job_filter |= models.Q(company=employer.company)
    assigned_job_ids = Applicant.objects.visible_to_employer(employer).values_list('job_id', flat=True)
    employer_jobs = Job.objects.filter(job_filter | models.Q(id__in=assigned_job_ids)).distinct()
    active_jobs_count = employer_jobs.filter(status__in=Job.LIVE_STATUSES).count()
    pending_jobs_count = employer_jobs.filter(status='PENDING_APPROVAL').count()
    
    # Applicants for this employer's jobs (only Approved applications)
    applicants_qs = Applicant.objects.visible_to_employer(employer).select_related('job', 'job__employer', 'candidate_account')
    total_applicants_count = applicants_qs.count()
    shortlisted_count = applicants_qs.filter(status__iexact='shortlisted').count()
    
    # Interviews & Placements for this employer's jobs
    interviews_count = Interview.objects.filter(applicant__in=applicants_qs, status__in=['Scheduled', 'Rescheduled', 'Completed']).count()
    hired_count = Placement.objects.filter(applicant__in=applicants_qs).count()

    recent_applicants = applicants_qs.order_by('-id')[:6]
    recent_jobs = employer_jobs.order_by('-id')[:5]

    from apps.communication.models import MessageRecipient
    recent_messages = MessageRecipient.objects.filter(
        employer_account=employer,
        channel='dashboard',
        delivery_status='Sent'
    ).select_related('bulk_message').order_by('-id')[:5]

    context = {
        'employer': employer,
        'active_jobs_count': active_jobs_count,
        'pending_jobs_count': pending_jobs_count,
        'total_applicants_count': total_applicants_count,
        'shortlisted_count': shortlisted_count,
        'interviews_count': interviews_count,
        'hired_count': hired_count,
        'recent_applicants': recent_applicants,
        'recent_jobs': recent_jobs,
        'recent_messages': recent_messages,
        'active_page': 'dashboard',
        'page_title': 'Employer Dashboard — Sky Vision'
    }
    return render(request, 'employer_portal/dashboard.html', context)


@employer_required
def employer_jobs_list_view(request):
    """Employer jobs listing page."""
    employer = request.employer_user
    status_filter = request.GET.get('status', 'all').upper()
    search = request.GET.get('search', '').strip()

    job_filter = models.Q(employer=employer)
    if getattr(employer, 'shares_company_data', False) and getattr(employer, 'company', None):
        job_filter |= models.Q(company=employer.company)
    assigned_job_ids = Applicant.objects.visible_to_employer(employer).values_list('job_id', flat=True)
    jobs_qs = Job.objects.filter(job_filter | models.Q(id__in=assigned_job_ids)).distinct().order_by('-id')
    if status_filter != 'ALL':
        if status_filter in ['LIVE', 'ACTIVE']:
            jobs_qs = jobs_qs.filter(status__in=Job.LIVE_STATUSES)
        else:
            jobs_qs = jobs_qs.filter(status=status_filter)

    if search:
        jobs_qs = jobs_qs.filter(title__icontains=search)

    context = {
        'employer': employer,
        'jobs': jobs_qs,
        'status_filter': status_filter.lower(),
        'search': search,
        'active_page': 'jobs',
        'page_title': 'My Job Postings — Employer Portal'
    }
    return render(request, 'employer_portal/jobs_list.html', context)


@employer_required
def employer_job_create_view(request):
    """Post a new Job / Requirement."""
    employer = request.employer_user

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category = request.POST.get('category', '').strip() or 'General'
        department = request.POST.get('department', '').strip() or 'General'
        location = request.POST.get('location', '').strip() or f"{employer.city}, {employer.state}"
        employment_type = request.POST.get('employment_type', '').strip() or 'Full Time'
        experience = request.POST.get('experience', '').strip()
        salary = request.POST.get('salary', '').strip()
        vacancies = request.POST.get('vacancies', '1').strip() or '1'
        qualification = request.POST.get('qualification', '').strip()
        description = request.POST.get('description', '').strip()
        requirements = request.POST.get('requirements', '').strip()
        deadline = request.POST.get('deadline', '').strip()

        errors = {}
        if not title:
            errors['title'] = 'Job title is required.'
        if not description:
            errors['description'] = 'Job description is required.'

        form_data = {
            'title': title,
            'category': category,
            'department': department,
            'location': location,
            'employment_type': employment_type,
            'experience': experience,
            'salary': salary,
            'vacancies': vacancies,
            'qualification': qualification,
            'description': description,
            'requirements': requirements,
            'deadline': deadline,
        }

        if errors:
            return render(request, 'employer_portal/job_form.html', {
                'employer': employer,
                'errors': errors,
                'form_data': form_data,
                'active_page': 'jobs',
                'page_title': 'Post New Job'
            })

        # Save Job as PENDING_APPROVAL
        job = Job.objects.create(
            employer=employer,
            company=employer.company,
            title=title,
            category=category,
            department=department,
            location=location,
            employment_type=employment_type,
            experience=experience,
            salary=salary,
            vacancies=vacancies,
            qualification=qualification,
            description=description,
            requirements=requirements,
            deadline=deadline,
            status='PENDING_APPROVAL'
        )

        # Mirror in CompanyRequirement
        if employer.company:
            CompanyRequirement.objects.create(
                company=employer.company,
                job=job,
                title=title,
                department=department,
                job_type=employment_type,
                location=location,
                vacancies=vacancies,
                experience_req=experience,
                salary_range=salary,
                qualification=qualification,
                description=description,
                requirements=requirements,
                deadline=deadline,
                status='Pending Approval',
                notes=f"Posted by Employer: {employer.contact_name} ({employer.email})"
            )

        log_activity(
            action_type="Job Posted by Employer",
            title=f"Job '{title}' posted.",
            description=f"Employer '{employer.company_name}' submitted new job '{title}' for approval."
        )

        return redirect('/employer/jobs/')

    default_location = f"{employer.city}, {employer.state}" if (employer and employer.city) else "Lucknow, UP"
    form_data = {
        'title': '',
        'category': '',
        'department': '',
        'location': default_location,
        'employment_type': 'Full Time',
        'experience': '',
        'salary': '',
        'vacancies': '1',
        'qualification': '',
        'deadline': '30 Days',
        'description': '',
        'requirements': ''
    }
    return render(request, 'employer_portal/job_form.html', {
        'employer': employer,
        'job': None,
        'form_data': form_data,
        'active_page': 'jobs',
        'page_title': 'Post New Job'
    })


@employer_required
def employer_job_detail_view(request, job_id):
    """View single job posting details and candidates for it."""
    employer = request.employer_user
    job_filter = models.Q(employer=employer)
    if getattr(employer, 'shares_company_data', False) and getattr(employer, 'company', None):
        job_filter |= models.Q(company=employer.company)
    job = get_object_or_404(Job, job_filter, id=job_id)

    applicants = Applicant.objects.visible_to_employer(employer).filter(job=job).select_related('job', 'job__employer', 'candidate_account').order_by('-id')

    context = {
        'employer': employer,
        'job': job,
        'applicants': applicants,
        'applicants_count': applicants.count(),
        'active_page': 'jobs',
        'page_title': f"{job.title} — Employer Details"
    }
    return render(request, 'employer_portal/job_detail.html', context)


@employer_required
def employer_job_edit_view(request, job_id):
    """Edit an existing job posting."""
    employer = request.employer_user
    job_filter = models.Q(employer=employer)
    if getattr(employer, 'shares_company_data', False) and getattr(employer, 'company', None):
        job_filter |= models.Q(company=employer.company)
    job = get_object_or_404(Job, job_filter, id=job_id)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category = request.POST.get('category', '').strip() or 'General'
        department = request.POST.get('department', '').strip() or 'General'
        location = request.POST.get('location', '').strip() or job.location
        employment_type = request.POST.get('employment_type', '').strip() or 'Full Time'
        experience = request.POST.get('experience', '').strip()
        salary = request.POST.get('salary', '').strip()
        vacancies = request.POST.get('vacancies', '1').strip() or '1'
        qualification = request.POST.get('qualification', '').strip()
        description = request.POST.get('description', '').strip()
        requirements = request.POST.get('requirements', '').strip()
        deadline = request.POST.get('deadline', '').strip()

        form_data = {
            'title': title,
            'category': category,
            'department': department,
            'location': location,
            'employment_type': employment_type,
            'experience': experience,
            'salary': salary,
            'vacancies': vacancies,
            'qualification': qualification,
            'description': description,
            'requirements': requirements,
            'deadline': deadline,
        }

        if not title or not description:
            return render(request, 'employer_portal/job_form.html', {
                'employer': employer,
                'job': job,
                'form_data': form_data,
                'error': 'Title and description are required.',
                'active_page': 'jobs',
                'page_title': f"Edit {job.title}"
            })

        job.title = title
        job.category = category
        job.department = department
        job.location = location
        job.employment_type = employment_type
        job.experience = experience
        job.salary = salary
        job.vacancies = vacancies
        job.qualification = qualification
        job.description = description
        job.requirements = requirements
        job.deadline = deadline
        job.save()

        # Sync requirement if exists
        req = CompanyRequirement.objects.filter(job=job).first()
        if req:
            req.title = title
            req.department = department
            req.job_type = employment_type
            req.location = location
            req.vacancies = vacancies
            req.experience_req = experience
            req.salary_range = salary
            req.qualification = qualification
            req.description = description
            req.requirements = requirements
            req.deadline = deadline
            req.save()

        return redirect(f"/employer/jobs/{job.id}/")

    form_data = {
        'title': job.title,
        'category': job.category,
        'department': job.department,
        'location': job.location,
        'employment_type': job.employment_type,
        'experience': job.experience,
        'salary': job.salary,
        'vacancies': job.vacancies,
        'qualification': job.qualification or '',
        'description': job.description,
        'requirements': job.requirements,
        'deadline': job.deadline,
    }
    return render(request, 'employer_portal/job_form.html', {
        'employer': employer,
        'job': job,
        'form_data': form_data,
        'active_page': 'jobs',
        'page_title': f"Edit {job.title}"
    })


@employer_required
def employer_job_close_view(request, job_id):
    """Close an active job posting."""
    employer = request.employer_user
    job_filter = models.Q(employer=employer)
    if getattr(employer, 'shares_company_data', False) and getattr(employer, 'company', None):
        job_filter |= models.Q(company=employer.company)
    job = get_object_or_404(Job, job_filter, id=job_id)
    if request.method == 'POST':
        job.status = 'CLOSED'
        job.save()
        req = CompanyRequirement.objects.filter(job=job).first()
        if req:
            req.status = 'Closed'
            req.save()
        return redirect('/employer/jobs/')
    return redirect(f"/employer/jobs/{job.id}/")


# ==========================================
# APPLICANTS & HIRING PIPELINE VIEWS
# ==========================================

@employer_required
def employer_applicants_list_view(request):
    """Applicants management board across all employer jobs (only Approved applications)."""
    employer = request.employer_user
    job_filter = models.Q(employer=employer)
    if getattr(employer, 'shares_company_data', False) and getattr(employer, 'company', None):
        job_filter |= models.Q(company=employer.company)
    assigned_job_ids = Applicant.objects.visible_to_employer(employer).values_list('job_id', flat=True)
    employer_jobs = Job.objects.filter(job_filter | models.Q(id__in=assigned_job_ids)).distinct()

    selected_job_id = request.GET.get('job_id')
    stage_filter = request.GET.get('stage', 'all').lower()
    search = request.GET.get('search', '').strip()

    applicants_qs = Applicant.objects.visible_to_employer(employer).select_related('job', 'job__employer', 'candidate_account').order_by('-id')

    if selected_job_id:
        try:
            applicants_qs = applicants_qs.filter(job_id=int(selected_job_id))
        except (ValueError, TypeError):
            pass

    if stage_filter != 'all':
        if stage_filter == 'applied':
            applicants_qs = applicants_qs.filter(status__in=['New', 'Applied', 'Pending', 'Employer Reviews'])
        elif stage_filter == 'shortlisted':
            applicants_qs = applicants_qs.filter(status__iexact='shortlisted')
        elif stage_filter == 'interview':
            applicants_qs = applicants_qs.filter(status__icontains='interview')
        elif stage_filter == 'selected':
            applicants_qs = applicants_qs.filter(status__iexact='selected')
        elif stage_filter == 'offered':
            applicants_qs = applicants_qs.filter(status__icontains='offer')
        elif stage_filter == 'hired' or stage_filter == 'joined':
            applicants_qs = applicants_qs.filter(status__in=['Joined', 'Hired', 'Placed'])
        elif stage_filter == 'rejected':
            applicants_qs = applicants_qs.filter(status__iexact='rejected')

    if search:
        applicants_qs = applicants_qs.filter(
            full_name__icontains=search
        ) | applicants_qs.filter(
            email__icontains=search
        ) | applicants_qs.filter(
            job_title__icontains=search
        )

    context = {
        'employer': employer,
        'jobs': employer_jobs,
        'applicants': applicants_qs,
        'selected_job_id': selected_job_id or '',
        'stage_filter': stage_filter,
        'search': search,
        'active_page': 'applicants',
        'page_title': 'Applicants Pipeline — Employer Portal'
    }
    return render(request, 'employer_portal/applicants_list.html', context)


@employer_required
@require_http_methods(["POST"])
def employer_applicant_status_api(request, applicant_id):
    """Update applicant pipeline status (Shortlisted, Interview Scheduled, Offer Released, Joined, Rejected)."""
    employer = request.employer_user
    
    # IDOR Protection & R1/R3 Approval rule: applicant must be visible to this employer
    applicant = get_object_or_404(Applicant.objects.visible_to_employer(employer), id=applicant_id)

    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.POST
    else:
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

    if 'approval_status' in data:
        return JsonResponse({'status': 'error', 'message': 'Employers cannot modify application approval status.'}, status=403)

    new_status = data.get('status', '').strip()
    notes = data.get('notes', '').strip()
    
    if not new_status:
        return JsonResponse({'status': 'error', 'message': 'New status is required.'}, status=400)

    if new_status.lower() in ['approved', 'pending']:
        return JsonResponse({'status': 'error', 'message': 'Employers cannot modify application approval status.'}, status=403)

    from apps.candidates.status_helpers import set_applicant_status
    from django.db import transaction

    with transaction.atomic():
        try:
            target_status = new_status
            if new_status.lower() in ['interview', 'interview scheduled']:
                iv_date = data.get('interview_date')
                iv_time = data.get('interview_time', '11:00')
                iv_mode = data.get('interview_mode', 'In-Person Office Interview')
                iv_link = data.get('location_or_link', f"{employer.company_name} Office, {employer.city}")

                if iv_date:
                    try:
                        date_obj = datetime.strptime(iv_date, "%Y-%m-%d").date()
                        time_obj = datetime.strptime(iv_time, "%H:%M").time() if len(iv_time) == 5 else datetime.strptime("11:00", "%H:%M").time()
                        interview = Interview.objects.create(
                            candidate_type='applicant',
                            applicant=applicant,
                            candidate_id=applicant.id,
                            candidate_name=applicant.full_name,
                            candidate_email=applicant.email,
                            candidate_phone=applicant.phone,
                            job_title=applicant.job_title,
                            interview_date=date_obj,
                            interview_time=time_obj,
                            interview_mode=iv_mode,
                            location_or_link=iv_link,
                            status='Scheduled',
                            interviewer_notes=notes
                        )
                        notify_interview_scheduled(interview)
                    except Exception:
                        pass
                target_status = "Interview Scheduled"

            elif new_status.lower() in ['selected', 'select', 'candidate selected']:
                target_status = "Selected"
                Interview.objects.filter(applicant=applicant, status__in=['Scheduled', 'Rescheduled']).update(
                    status='Completed', result='Selected'
                )

            elif new_status.lower() in ['offered', 'job offered', 'offer released']:
                designation = data.get('designation', applicant.job_title)
                offered_ctc = data.get('offered_ctc', '')
                joining_date = data.get('joining_date', '')
                offer_date = timezone.now().strftime("%Y-%m-%d")

                # Candidate cleared interview when offer is released
                Interview.objects.filter(applicant=applicant, status__in=['Scheduled', 'Rescheduled']).update(
                    status='Completed', result='Selected'
                )

                # Handle optional offer letter file upload
                doc_filename = ""
                offer_file = request.FILES.get('document') or request.FILES.get('offer_document') or request.FILES.get('offer_letter_file')
                if offer_file:
                    try:
                        from apps.accounts.auth_helpers import save_offer_letter_file
                        doc_filename = save_offer_letter_file(offer_file) or ""
                    except Exception as e:
                        return JsonResponse({'status': 'error', 'message': f'Offer letter upload error: {str(e)}'}, status=400)

                JobOffer.objects.create(
                    applicant=applicant,
                    candidate_name=applicant.full_name,
                    company_name=employer.company_name,
                    designation=designation,
                    offered_ctc=offered_ctc,
                    offer_date=offer_date,
                    joining_date=joining_date,
                    status='Offer Sent',
                    notes=notes,
                    document=doc_filename
                )
                target_status = "Offer Released"

            elif new_status.lower() in ['hired', 'joined', 'candidate joined']:
                ctc = data.get('package', data.get('offered_ctc', ''))
                joining_date = data.get('joining_date', '')
                placement_date = timezone.now().strftime("%Y-%m-%d")

                placement, created = Placement.objects.get_or_create(
                    applicant=applicant,
                    defaults={
                        'candidate_name': applicant.full_name,
                        'company_name': employer.company_name,
                        'position': applicant.job_title,
                        'package': ctc,
                        'placement_date': placement_date,
                        'joining_date': joining_date,
                        'status': 'Joined',
                        'notes': f"Hired by Employer '{employer.company_name}'. {notes}"
                    }
                )
                if not created:
                    placement.status = 'Joined'
                    if ctc:
                        placement.package = ctc
                    if joining_date:
                        placement.joining_date = joining_date
                    placement.save()

                JobOffer.objects.filter(applicant=applicant).update(status='Accepted')
                target_status = "Joined"

            set_applicant_status(
                applicant,
                target_status,
                changed_by=f"employer ({employer.company_name})",
                notes=notes,
                force_override=True
            )

        except ValueError as ve:
            return JsonResponse({'status': 'error', 'message': str(ve)}, status=400)

    return JsonResponse({
        'status': 'success',
        'message': f"Applicant status updated to '{applicant.status}'.",
        'applicant_id': applicant.id,
        'new_status': applicant.status,
        'flow_step': applicant.flow_step
    })


@employer_required
def employer_interviews_list_view(request):
    """List scheduled interviews for this employer's jobs with status filter and search."""
    employer = request.employer_user
    base_qs = Interview.objects.filter(applicant__in=Applicant.objects.visible_to_employer(employer)).select_related('applicant', 'applicant__job', 'applicant__candidate_account')

    status_filter = request.GET.get('status', 'all').strip().lower()
    search = request.GET.get('search', '').strip()

    filtered_qs = base_qs
    if status_filter == 'scheduled':
        filtered_qs = filtered_qs.filter(status__in=['Scheduled', 'Rescheduled'])
    elif status_filter == 'completed':
        filtered_qs = filtered_qs.filter(status='Completed')
    elif status_filter == 'cancelled':
        filtered_qs = filtered_qs.filter(status='Cancelled')

    if search:
        filtered_qs = filtered_qs.filter(
            models.Q(candidate_name__icontains=search) |
            models.Q(candidate_email__icontains=search) |
            models.Q(job_title__icontains=search)
        )

    interviews = filtered_qs.order_by('-interview_date', '-interview_time')

    total_count = base_qs.count()
    scheduled_count = base_qs.filter(status__in=['Scheduled', 'Rescheduled']).count()
    completed_count = base_qs.filter(status='Completed').count()
    cancelled_count = base_qs.filter(status='Cancelled').count()

    context = {
        'employer': employer,
        'interviews': interviews,
        'status_filter': status_filter,
        'search': search,
        'total_count': total_count,
        'scheduled_count': scheduled_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
        'active_page': 'interviews',
        'page_title': 'Interviews — Employer Portal'
    }
    return render(request, 'employer_portal/interviews_list.html', context)


@employer_required
@require_http_methods(["POST"])
def employer_interview_action_api(request, interview_id):
    """Update scheduled interview: reschedule, select, offer, reject, or cancel."""
    employer = request.employer_user
    interview = get_object_or_404(Interview, id=interview_id)

    visible_applicants = Applicant.objects.visible_to_employer(employer)
    is_authorized = (interview.applicant and interview.applicant in visible_applicants) or bool(request.session.get('admin_id'))
    if not is_authorized:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized to modify this interview.'}, status=403)

    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.POST
    else:
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

    action = data.get('action', '').strip().lower()
    from apps.candidates.status_helpers import set_applicant_status
    from django.db import transaction

    with transaction.atomic():
        if action == 'reschedule':
            new_date = data.get('interview_date')
            new_time = data.get('interview_time', '11:00')
            new_mode = data.get('interview_mode', interview.interview_mode)
            new_loc = data.get('location_or_link', interview.location_or_link)
            notes = data.get('interviewer_notes') or data.get('notes', '')

            if not new_date:
                return JsonResponse({'status': 'error', 'message': 'Interview date is required for rescheduling.'}, status=400)

            try:
                interview.interview_date = datetime.strptime(new_date, "%Y-%m-%d").date()
                if new_time and len(new_time) == 5:
                    interview.interview_time = datetime.strptime(new_time, "%H:%M").time()
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'Invalid date/time format: {str(e)}'}, status=400)

            interview.interview_mode = new_mode
            interview.location_or_link = new_loc
            if notes:
                interview.interviewer_notes = notes
            interview.status = 'Rescheduled'
            interview.save()

            if interview.applicant:
                notify_interview_scheduled(interview)

            return JsonResponse({'status': 'success', 'message': 'Interview successfully rescheduled!'})

        elif action in ['select', 'mark_selected', 'passed']:
            interview.status = 'Completed'
            interview.result = 'Selected'
            interview.save()
            if interview.applicant:
                set_applicant_status(interview.applicant, 'Selected', changed_by=f"employer ({employer.company_name})", notes="Selected after interview", force_override=True)
            return JsonResponse({'status': 'success', 'message': 'Candidate marked as Selected!'})

        elif action in ['reject', 'mark_rejected']:
            interview.status = 'Completed'
            interview.result = 'Rejected'
            interview.save()
            if interview.applicant:
                set_applicant_status(interview.applicant, 'Rejected', changed_by=f"employer ({employer.company_name})", notes="Rejected after interview", force_override=True)
            return JsonResponse({'status': 'success', 'message': 'Candidate marked as Rejected.'})

        elif action in ['cancel', 'cancelled']:
            reason = data.get('cancel_reason') or data.get('notes', 'Interview cancelled by employer')
            interview.status = 'Cancelled'
            interview.cancel_reason = reason
            interview.save()
            return JsonResponse({'status': 'success', 'message': 'Interview cancelled.'})

        elif action in ['offer', 'send_offer']:
            if not interview.applicant:
                return JsonResponse({'status': 'error', 'message': 'No applicant profile linked to extend formal offer.'}, status=400)

            designation = data.get('designation', interview.job_title)
            offered_ctc = data.get('offered_ctc', '')
            joining_date = data.get('joining_date', '')
            notes = data.get('notes', '')
            offer_date = timezone.now().strftime("%Y-%m-%d")

            interview.status = 'Completed'
            interview.result = 'Selected'
            interview.save()

            doc_filename = ""
            offer_file = request.FILES.get('document') or request.FILES.get('offer_document')
            if offer_file:
                try:
                    from apps.accounts.auth_helpers import save_offer_letter_file
                    doc_filename = save_offer_letter_file(offer_file) or ""
                except Exception as e:
                    return JsonResponse({'status': 'error', 'message': f'Offer letter upload error: {str(e)}'}, status=400)

            JobOffer.objects.create(
                applicant=interview.applicant,
                candidate_name=interview.candidate_name,
                company_name=employer.company_name,
                designation=designation,
                offered_ctc=offered_ctc,
                offer_date=offer_date,
                joining_date=joining_date,
                status='Offer Sent',
                notes=notes,
                document=doc_filename
            )

            set_applicant_status(interview.applicant, 'Offer Released', changed_by=f"employer ({employer.company_name})", notes=notes, force_override=True)
            return JsonResponse({'status': 'success', 'message': 'Job offer successfully sent to candidate!'})

        else:
            return JsonResponse({'status': 'error', 'message': f'Unknown action: {action}'}, status=400)



@employer_required
def employer_offers_list_view(request):
    """List job offers sent by this employer."""
    employer = request.employer_user
    offers = JobOffer.objects.filter(applicant__in=Applicant.objects.visible_to_employer(employer)).select_related('applicant', 'applicant__job', 'applicant__candidate_account').order_by('-id')

    context = {
        'employer': employer,
        'offers': offers,
        'active_page': 'offers',
        'page_title': 'Job Offers — Employer Portal'
    }
    return render(request, 'employer_portal/offers_list.html', context)


@employer_required
def employer_hired_list_view(request):
    """List hired placements for this employer."""
    employer = request.employer_user
    placements = Placement.objects.filter(applicant__in=Applicant.objects.visible_to_employer(employer)).select_related('applicant', 'applicant__job', 'applicant__candidate_account').order_by('-id')

    context = {
        'employer': employer,
        'placements': placements,
        'active_page': 'hired',
        'page_title': 'Hired Candidates — Employer Portal'
    }
    return render(request, 'employer_portal/hired_list.html', context)

    context = {
        'employer': employer,
        'placements': placements,
        'active_page': 'hired',
        'page_title': 'Hired Candidates — Employer Portal'
    }
    return render(request, 'employer_portal/hired_list.html', context)


@employer_required
def employer_profile_view(request):
    """Manage company profile and password."""
    employer = request.employer_user

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_profile':
            employer.contact_name = request.POST.get('contact_name', employer.contact_name).strip()
            employer.phone = request.POST.get('phone', employer.phone).strip()
            employer.industry = request.POST.get('industry', employer.industry).strip()
            employer.company_size = request.POST.get('company_size', employer.company_size).strip()
            employer.city = request.POST.get('city', employer.city).strip()
            employer.state = request.POST.get('state', employer.state).strip()
            employer.website = request.POST.get('website', employer.website).strip()
            employer.address = request.POST.get('address', employer.address).strip()
            employer.email_notifications_enabled = 'email_notifications_enabled' in request.POST

            doc_file = request.FILES.get('document')
            if doc_file:
                try:
                    stored_doc = save_employer_document_file(doc_file)
                    if stored_doc:
                        employer.document = stored_doc
                except ValueError as ve:
                    return render(request, 'employer_portal/profile.html', {
                        'employer': employer,
                        'error': str(ve),
                        'active_page': 'profile',
                        'page_title': 'Company Profile'
                    })

            employer.save()

            if employer.company:
                comp = employer.company
                comp.name = employer.company_name
                comp.phone = employer.phone
                comp.city = employer.city
                comp.state = employer.state
                comp.website = employer.website
                comp.address = employer.address
                comp.save()

            return render(request, 'employer_portal/profile.html', {
                'employer': employer,
                'success': 'Profile details updated successfully.',
                'active_page': 'profile',
                'page_title': 'Company Profile'
            })

        elif action == 'change_password':
            current_pass = request.POST.get('current_password', '')
            new_pass = request.POST.get('new_password', '')
            confirm_pass = request.POST.get('confirm_password', '')

            if not employer.verify_password(current_pass):
                return render(request, 'employer_portal/profile.html', {
                    'employer': employer,
                    'error': 'Current password is incorrect.',
                    'active_page': 'profile',
                    'page_title': 'Company Profile'
                })
            if len(new_pass) < 6:
                return render(request, 'employer_portal/profile.html', {
                    'employer': employer,
                    'error': 'New password must be at least 6 characters.',
                    'active_page': 'profile',
                    'page_title': 'Company Profile'
                })
            if new_pass != confirm_pass:
                return render(request, 'employer_portal/profile.html', {
                    'employer': employer,
                    'error': 'New password and confirmation do not match.',
                    'active_page': 'profile',
                    'page_title': 'Company Profile'
                })

            employer.set_password(new_pass)
            employer.save()
            return render(request, 'employer_portal/profile.html', {
                'employer': employer,
                'success': 'Password changed successfully.',
                'active_page': 'profile',
                'page_title': 'Company Profile'
            })

    jobs_count = Job.objects.filter(models.Q(employer=employer) | (models.Q(company=employer.company) if getattr(employer, 'company', None) else models.Q(id=0))).count()
    applicants_count = Applicant.objects.visible_to_employer(employer).count()
    hired_count = Placement.objects.filter(models.Q(applicant__in=Applicant.objects.visible_to_employer(employer))).count()

    context = {
        'employer': employer,
        'jobs_count': jobs_count,
        'applicants_count': applicants_count,
        'hired_count': hired_count,
        'active_page': 'profile',
        'page_title': 'Company Profile — Employer Portal'
    }
    return render(request, 'employer_portal/profile.html', context)


# ==========================================
# ADMIN EMPLOYER & JOB APPROVAL APIS
# ==========================================

from apps.accounts.auth_helpers import admin_required

@admin_required
def api_admin_employer_registrations(request):
    """List employer registrations for admin approval."""
    status_filter = request.GET.get('status', 'all').upper()
    search = request.GET.get('search', '').strip()

    qs = EmployerAccount.objects.all().order_by('-id')
    if status_filter != 'ALL':
        qs = qs.filter(status=status_filter)

    if search:
        qs = qs.filter(
            company_name__icontains=search
        ) | qs.filter(
            contact_name__icontains=search
        ) | qs.filter(
            email__icontains=search
        ) | qs.filter(
            phone__icontains=search
        )

    employers_list = [e.to_dict() for e in qs]
    return JsonResponse({
        'status': 'success',
        'employers': employers_list,
        'count': len(employers_list),
        'pending_count': EmployerAccount.objects.filter(status='PENDING').count(),
        'approved_count': EmployerAccount.objects.filter(status='APPROVED').count(),
        'rejected_count': EmployerAccount.objects.filter(status='REJECTED').count(),
        'suspended_count': EmployerAccount.objects.filter(status='SUSPENDED').count()
    })


@admin_required
@require_http_methods(["POST"])
def api_admin_approve_employer(request, employer_id):
    """Approve an employer registration."""
    try:
        from django.db import transaction
        with transaction.atomic():
            employer = EmployerAccount.objects.select_for_update().get(id=employer_id)

            if employer.status == 'APPROVED':
                return JsonResponse({
                    'status': 'success',
                    'message': f"Employer '{employer.company_name}' is already approved.",
                    'employer': employer.to_dict()
                })

            employer.status = 'APPROVED'
            employer.rejection_reason = ""
            employer.approved_at = timezone.now()
            if getattr(request, 'admin_user', None):
                employer.approved_by = request.admin_user
            employer.save()

            if employer.company:
                employer.company.status = 'Active'
                employer.company.save()

        email_sent = notify_employer_approved(employer)
        log_activity(
            action_type="Employer Approved",
            title=f"Employer '{employer.company_name}' approved.",
            description=f"Admin approved employer '{employer.company_name}' ({employer.email}). Approval email dispatched: {'Yes' if email_sent else 'Failed'}."
        )

        return JsonResponse({
            'status': 'success',
            'message': f"Employer '{employer.company_name}' approved successfully. Approval notification email sent to {employer.email}.",
            'employer': employer.to_dict()
        })
    except EmployerAccount.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Employer account not found."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@admin_required
@require_http_methods(["POST"])
def api_admin_reject_employer(request, employer_id):
    """Reject an employer registration with reason."""
    employer = get_object_or_404(EmployerAccount, id=employer_id)
    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST

    reason = (data.get('reason') or '').strip()
    employer.status = 'REJECTED'
    employer.rejection_reason = reason
    employer.save()

    notify_employer_rejected(employer, reason)
    log_activity(
        action_type="Employer Rejected",
        title=f"Employer '{employer.company_name}' rejected.",
        description=f"Admin rejected employer '{employer.company_name}'. Reason: {reason}"
    )

    return JsonResponse({
        'status': 'success',
        'message': f"Employer '{employer.company_name}' registration rejected.",
        'employer': employer.to_dict()
    })


@admin_required
@require_http_methods(["POST"])
def api_admin_suspend_employer(request, employer_id):
    """Suspend/Revoke an approved employer account."""
    employer = get_object_or_404(EmployerAccount, id=employer_id)
    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST

    reason = (data.get('reason') or '').strip()
    employer.status = 'SUSPENDED'
    employer.rejection_reason = reason
    employer.save()

    # Hide all live jobs posted by this employer
    Job.objects.filter(employer=employer, status__in=Job.LIVE_STATUSES).update(status=Job.STATUS_CLOSED)

    notify_employer_suspended(employer, reason)
    log_activity(
        action_type="Employer Suspended",
        title=f"Employer '{employer.company_name}' suspended.",
        description=f"Admin suspended employer '{employer.company_name}'. Reason: {reason}"
    )

    return JsonResponse({
        'status': 'success',
        'message': f"Employer '{employer.company_name}' access suspended.",
        'employer': employer.to_dict()
    })


@admin_required
@require_http_methods(["GET", "PUT", "DELETE"])
def api_admin_employer_registration_detail(request, employer_id):
    """Fetch, update, or delete single employer registration record."""
    employer = get_object_or_404(EmployerAccount, id=employer_id)
    if request.method == "GET":
        return JsonResponse({'status': 'success', 'employer': employer.to_dict()})
    elif request.method == "DELETE":
        company_name = employer.company_name
        employer.delete()
        log_activity(
            action_type="Employer Account Deleted",
            title=f"Employer '{company_name}' deleted.",
            description=f"Admin deleted employer account for '{company_name}'."
        )
        return JsonResponse({'status': 'success', 'message': f"Employer account '{company_name}' deleted."})
    elif request.method == "PUT":
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST
        if 'name' in data or 'company_name' in data:
            employer.company_name = data.get('company_name') or data.get('name')
        if 'contact_name' in data:
            employer.contact_name = data['contact_name']
        if 'email' in data:
            employer.email = data['email']
        if 'phone' in data:
            employer.phone = data['phone']
        if 'status' in data:
            st = str(data['status']).upper()
            if st in ['PENDING', 'APPROVED', 'REJECTED', 'SUSPENDED']:
                employer.status = st
        employer.save()
        return JsonResponse({'status': 'success', 'message': f"Employer '{employer.company_name}' updated.", 'employer': employer.to_dict()})


@admin_required
def api_admin_job_approvals(request):
    """List employer job postings requiring admin review."""
    status_filter = request.GET.get('status', 'all').upper()
    search = request.GET.get('search', '').strip()

    qs = Job.objects.exclude(employer__isnull=True).order_by('-id')
    if status_filter != 'ALL':
        if status_filter == 'PENDING':
            qs = qs.filter(status='PENDING_APPROVAL')
        elif status_filter in ['LIVE', 'ACTIVE']:
            qs = qs.filter(status__in=Job.LIVE_STATUSES)
        else:
            qs = qs.filter(status=status_filter)

    if search:
        qs = qs.filter(title__icontains=search) | qs.filter(employer__company_name__icontains=search)

    jobs_list = [j.to_dict() for j in qs]
    return JsonResponse({
        'status': 'success',
        'jobs': jobs_list,
        'count': len(jobs_list),
        'pending_count': Job.objects.exclude(employer__isnull=True).filter(status='PENDING_APPROVAL').count(),
        'live_count': Job.objects.exclude(employer__isnull=True).filter(status__in=Job.LIVE_STATUSES).count(),
        'rejected_count': Job.objects.exclude(employer__isnull=True).filter(status='REJECTED').count()
    })


@admin_required
@require_http_methods(["POST"])
def api_admin_approve_job(request, job_id):
    """Approve a pending job posting to make it LIVE on the site."""
    job = get_object_or_404(Job, id=job_id)
    old_status = job.status
    job.status = 'LIVE'
    job.rejection_reason = ""
    job.approved_at = timezone.now()
    if getattr(request, 'admin_user', None):
        job.approved_by = request.admin_user
    job.save()

    # Mirror status update in requirement
    req = CompanyRequirement.objects.filter(job=job).first()
    if req:
        req.status = 'Active'
        req.save()
    elif job.company:
        try:
            CompanyRequirement.objects.create(
                company=job.company,
                job=job,
                title=job.title,
                department=job.department or job.category,
                job_type=job.employment_type,
                location=job.location,
                vacancies=job.vacancies,
                experience_req=job.experience,
                salary_range=job.salary,
                qualification=job.qualification,
                description=job.description,
                requirements=job.requirements,
                deadline=job.deadline or '30 Days',
                status='Active'
            )
        except Exception:
            pass

    notify_job_status_change(job, old_status, Job.STATUS_LIVE)
    log_activity(
        action_type="Job Approved",
        title=f"Job '{job.title}' approved.",
        description=f"Admin approved job '{job.title}' for employer '{job.employer.company_name if job.employer else (job.company.name if job.company else 'N/A')}'."
    )

    return JsonResponse({
        'status': 'success',
        'message': f"Job '{job.title}' is now Approved and LIVE on the website!",
        'job': job.to_dict()
    })


@admin_required
@require_http_methods(["POST"])
def api_admin_reject_job(request, job_id):
    """Reject a job posting with reason."""
    job = get_object_or_404(Job, id=job_id)
    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST

    reason = (data.get('reason') or '').strip()
    job.status = 'REJECTED'
    job.rejection_reason = reason
    job.save()

    req = CompanyRequirement.objects.filter(job=job).first()
    if req:
        req.status = 'Rejected'
        req.save()

    notify_job_status_change(job, 'PENDING_APPROVAL', 'REJECTED', reason)
    log_activity(
        action_type="Job Rejected",
        title=f"Job '{job.title}' rejected.",
        description=f"Admin rejected job '{job.title}'. Reason: {reason}"
    )

    return JsonResponse({
        'status': 'success',
        'message': f"Job '{job.title}' rejected.",
        'job': job.to_dict()
    })

