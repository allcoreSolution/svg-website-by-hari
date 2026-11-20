import os







import json







import datetime







from django.db import models







from django.utils import timezone







from django.shortcuts import render, redirect







from django.http import JsonResponse, FileResponse, Http404







from django.views.decorators.csrf import ensure_csrf_cookie







from django.views.decorators.http import require_http_methods







from django.conf import settings







from apps.accounts.auth_helpers import admin_required







from apps.accounts.models import AdminUser, CandidateAccount, EmployerAccount







from apps.candidates.models import Applicant, Resume, Interview







from apps.candidates.status_helpers import set_applicant_status







from apps.companies.models import CompanyEnquiry, Company, CompanyContact, CompanyRequirement







from apps.jobs.models import Job, JobCategory







from apps.companies.views import sync_expired_requirements







from apps.internships.models import InternshipEnquiry, InternshipProvider, Internship, InternshipApplication







from apps.enquiries.models import ContactEnquiry, FollowUp, ActivityLog, EnquiryRead, log_activity







from apps.enquiries.constants import bucket_of







from apps.placements.models import Placement, JobOffer















MODULE_SECTIONS = {







    # Registration & Approval Module







    'registrations_all': {'module_key': 'registrations', 'module_title': 'Registration & Approval', 'section_name': 'All Registrations', 'icon': 'ti-user-check'},







    'registrations_candidates': {'module_key': 'registrations', 'module_title': 'Registration & Approval', 'section_name': 'Candidate Registrations', 'icon': 'ti-users'},







    'registrations_employers': {'module_key': 'registrations', 'module_title': 'Registration & Approval', 'section_name': 'Employer Registrations', 'icon': 'ti-building'},







    'registrations_rejected': {'module_key': 'registrations', 'module_title': 'Registration & Approval', 'section_name': 'Rejected / Suspended Registrations', 'icon': 'ti-user-x'},















    # Job Applications Approval Module







    'job_applications_all': {'module_key': 'candidates', 'module_title': 'Job Management', 'section_name': 'Application Approvals', 'icon': 'ti-file-check'},







    'job_applications_pending': {'module_key': 'candidates', 'module_title': 'Job Management', 'section_name': 'Pending Application Approvals', 'icon': 'ti-clock'},







    # Candidates







    'candidates_all': {'module_key': 'candidates', 'module_title': 'Candidates', 'section_name': 'All Candidates', 'icon': 'ti-users'},







    'candidates_registrations': {'module_key': 'candidates', 'module_title': 'Candidates', 'section_name': 'Candidate Registrations', 'icon': 'ti-user-check'},







    'candidates_add': {'module_key': 'candidates', 'module_title': 'Candidates', 'section_name': 'Add Candidate', 'icon': 'ti-user-plus'},







    'candidates_profiles': {'module_key': 'candidates', 'module_title': 'Candidates', 'section_name': 'Candidate Profiles', 'icon': 'ti-id'},







    'candidates_shortlisted': {'module_key': 'candidates', 'module_title': 'Candidates', 'section_name': 'Shortlisted Candidates', 'icon': 'ti-star'},







    'interviews_upcoming': {'module_key': 'candidates', 'module_title': 'Candidates', 'section_name': 'Upcoming Interviews', 'icon': 'ti-calendar-event'},







    'interviews_completed': {'module_key': 'candidates', 'module_title': 'Candidates', 'section_name': 'Completed Interviews', 'icon': 'ti-circle-check'},







    'interviews_cancelled': {'module_key': 'candidates', 'module_title': 'Candidates', 'section_name': 'Cancelled Interviews', 'icon': 'ti-circle-x'},







    'candidates_selected': {'module_key': 'candidates', 'module_title': 'Candidates', 'section_name': 'Selected Candidates', 'icon': 'ti-user-check'},







    'candidates_rejected': {'module_key': 'candidates', 'module_title': 'Candidates', 'section_name': 'Rejected Candidates', 'icon': 'ti-user-x'},







    'candidates_placed': {'module_key': 'candidates', 'module_title': 'Candidates', 'section_name': 'Placed Candidates', 'icon': 'ti-award'},















    # Companies







    'companies_all': {'module_key': 'companies', 'module_title': 'Companies', 'section_name': 'All Companies', 'icon': 'ti-building'},







    'companies_add': {'module_key': 'companies', 'module_title': 'Companies', 'section_name': 'Add Company', 'icon': 'ti-building-plus'},







    'companies_enquiries': {'module_key': 'companies', 'module_title': 'Companies', 'section_name': 'Company Enquiries', 'icon': 'ti-mail-fast'},







    'requirements_all': {'module_key': 'companies', 'module_title': 'Companies', 'section_name': 'All Company Requirements', 'icon': 'ti-clipboard-list'},







    'requirements_active': {'module_key': 'companies', 'module_title': 'Companies', 'section_name': 'Active Requirements', 'icon': 'ti-clipboard-check'},







    'requirements_closed': {'module_key': 'companies', 'module_title': 'Companies', 'section_name': 'Closed Requirements', 'icon': 'ti-clipboard-off'},







    'requirements_expired': {'module_key': 'companies', 'module_title': 'Companies', 'section_name': 'Expired Requirements', 'icon': 'ti-clipboard-x'},







    'job_openings': {'module_key': 'jobs', 'module_title': 'Job Management', 'section_name': 'Job Postings', 'icon': 'ti-briefcase'},







    'company_contacts': {'module_key': 'companies', 'module_title': 'Companies', 'section_name': 'Company Contacts', 'icon': 'ti-address-book'},















    # Internships







    'internships_all': {'module_key': 'internships', 'module_title': 'Internships', 'section_name': 'All Internships', 'icon': 'ti-school'},







    'internships_add': {'module_key': 'internships', 'module_title': 'Internships', 'section_name': 'Add Internship', 'icon': 'ti-circle-plus'},







    'internships_enquiries': {'module_key': 'internships', 'module_title': 'Internships', 'section_name': 'Internship Enquiries', 'icon': 'ti-help'},







    'internship_apps_all': {'module_key': 'internships', 'module_title': 'Internships', 'section_name': 'All Internship Applications', 'icon': 'ti-file-description'},







    'internship_apps_pending': {'module_key': 'internships', 'module_title': 'Internships', 'section_name': 'Pending Applications', 'icon': 'ti-clock'},







    'internship_apps_shortlisted': {'module_key': 'internships', 'module_title': 'Internships', 'section_name': 'Shortlisted Applications', 'icon': 'ti-thumb-up'},







    'internship_apps_selected': {'module_key': 'internships', 'module_title': 'Internships', 'section_name': 'Selected Applications', 'icon': 'ti-check'},







    'internship_apps_rejected': {'module_key': 'internships', 'module_title': 'Internships', 'section_name': 'Rejected Applications', 'icon': 'ti-x'},







    'internships_active': {'module_key': 'internships', 'module_title': 'Internships', 'section_name': 'Active Internships', 'icon': 'ti-player-play'},







    'internships_completed': {'module_key': 'internships', 'module_title': 'Internships', 'section_name': 'Completed Internships', 'icon': 'ti-certificate'},







    'internship_providers': {'module_key': 'internships', 'module_title': 'Internships', 'section_name': 'Internship Providers', 'icon': 'ti-building-community'},















    # Enquiries







    'enquiries_all': {'module_key': 'enquiries', 'module_title': 'Enquiries', 'section_name': 'All Enquiries', 'icon': 'ti-message-2'},







    'enquiries_general': {'module_key': 'enquiries', 'module_title': 'Enquiries', 'section_name': 'General Enquiries', 'icon': 'ti-message-dots'},







    'enquiries_company': {'module_key': 'enquiries', 'module_title': 'Enquiries', 'section_name': 'Company Enquiries', 'icon': 'ti-building'},







    'enquiries_internship': {'module_key': 'enquiries', 'module_title': 'Enquiries', 'section_name': 'Internship Enquiries', 'icon': 'ti-school'},







    'enquiries_candidate': {'module_key': 'enquiries', 'module_title': 'Enquiries', 'section_name': 'Candidate Enquiries', 'icon': 'ti-user-search'},







    'enquiries_unread': {'module_key': 'enquiries', 'module_title': 'Enquiries', 'section_name': 'Unread Enquiries', 'icon': 'ti-mail-unread'},







    'enquiries_resolved': {'module_key': 'enquiries', 'module_title': 'Enquiries', 'section_name': 'Resolved Enquiries', 'icon': 'ti-circle-check'},















    # Placements







    'placements_all': {'module_key': 'placements', 'module_title': 'Placements', 'section_name': 'All Placements', 'icon': 'ti-award'},







    'placements_active': {'module_key': 'placements', 'module_title': 'Placements', 'section_name': 'Active Placements', 'icon': 'ti-flame'},







    'placements_completed': {'module_key': 'placements', 'module_title': 'Placements', 'section_name': 'Completed Placements', 'icon': 'ti-badge-check'},







    'placements_pending_joining': {'module_key': 'placements', 'module_title': 'Placements', 'section_name': 'Pending Joining', 'icon': 'ti-hourglass'},







    'placements_joined': {'module_key': 'placements', 'module_title': 'Placements', 'section_name': 'Joined Candidates', 'icon': 'ti-user-check'},







    'placements_history': {'module_key': 'placements', 'module_title': 'Placements', 'section_name': 'Placement History', 'icon': 'ti-history'},







    'placements_reports': {'module_key': 'placements', 'module_title': 'Placements', 'section_name': 'Placement Reports', 'icon': 'ti-report-analytics'},















    # Job Offers







    'offers_all': {'module_key': 'offers', 'module_title': 'Job Offers', 'section_name': 'All Job Offers', 'icon': 'ti-file-certificate'},







    'offers_create': {'module_key': 'offers', 'module_title': 'Job Offers', 'section_name': 'Create Job Offer', 'icon': 'ti-file-plus'},







    'offers_pending': {'module_key': 'offers', 'module_title': 'Job Offers', 'section_name': 'Pending Offers', 'icon': 'ti-file-time'},







    'offers_accepted': {'module_key': 'offers', 'module_title': 'Job Offers', 'section_name': 'Accepted Offers', 'icon': 'ti-file-check'},







    'offers_rejected': {'module_key': 'offers', 'module_title': 'Job Offers', 'section_name': 'Rejected Offers', 'icon': 'ti-file-x'},







    'offers_expired': {'module_key': 'offers', 'module_title': 'Job Offers', 'section_name': 'Expired Offers', 'icon': 'ti-file-off'},







    'offers_history': {'module_key': 'offers', 'module_title': 'Job Offers', 'section_name': 'Offer History', 'icon': 'ti-timeline'},















    # Documents







    'documents_all': {'module_key': 'documents', 'module_title': 'Documents', 'section_name': 'All Documents', 'icon': 'ti-files'},







    'documents_candidate': {'module_key': 'documents', 'module_title': 'Documents', 'section_name': 'Candidate Documents', 'icon': 'ti-file-user'},







    'documents_company': {'module_key': 'documents', 'module_title': 'Documents', 'section_name': 'Company Documents', 'icon': 'ti-file-info'},







    'documents_internship': {'module_key': 'documents', 'module_title': 'Documents', 'section_name': 'Internship Documents', 'icon': 'ti-file-code'},







    'documents_offer_letters': {'module_key': 'documents', 'module_title': 'Documents', 'section_name': 'Offer Letters', 'icon': 'ti-file-text'},







    'documents_joining': {'module_key': 'documents', 'module_title': 'Documents', 'section_name': 'Joining Documents', 'icon': 'ti-file-check'},







    'verification_pending': {'module_key': 'documents', 'module_title': 'Documents', 'section_name': 'Pending Verification', 'icon': 'ti-shield-search'},







    'verification_verified': {'module_key': 'documents', 'module_title': 'Documents', 'section_name': 'Verified Documents', 'icon': 'ti-shield-check'},







    'verification_rejected': {'module_key': 'documents', 'module_title': 'Documents', 'section_name': 'Rejected Documents', 'icon': 'ti-shield-x'},















    # Follow-ups







    'followups_all': {'module_key': 'followups', 'module_title': 'Follow-ups', 'section_name': 'All Follow-ups', 'icon': 'ti-calendar-time'},







    'followups_today': {'module_key': 'followups', 'module_title': 'Follow-ups', 'section_name': "Today's Follow-ups", 'icon': 'ti-calendar-due'},







    'followups_upcoming': {'module_key': 'followups', 'module_title': 'Follow-ups', 'section_name': 'Upcoming Follow-ups', 'icon': 'ti-calendar-event'},







    'followups_overdue': {'module_key': 'followups', 'module_title': 'Follow-ups', 'section_name': 'Overdue Follow-ups', 'icon': 'ti-calendar-off'},







    'followups_candidate': {'module_key': 'followups', 'module_title': 'Follow-ups', 'section_name': 'Candidate Follow-ups', 'icon': 'ti-user-exclamation'},







    'followups_company': {'module_key': 'followups', 'module_title': 'Follow-ups', 'section_name': 'Company Follow-ups', 'icon': 'ti-building-cog'},







    'followups_internship': {'module_key': 'followups', 'module_title': 'Follow-ups', 'section_name': 'Internship Follow-ups', 'icon': 'ti-school-bell'},







    'followups_completed': {'module_key': 'followups', 'module_title': 'Follow-ups', 'section_name': 'Completed Follow-ups', 'icon': 'ti-checkup-list'},















    # Users & Roles







    'users_all': {'module_key': 'users', 'module_title': 'Users & Roles', 'section_name': 'All Users', 'icon': 'ti-users-group'},







    'users_add': {'module_key': 'users', 'module_title': 'Users & Roles', 'section_name': 'Add User', 'icon': 'ti-user-plus'},







    'users_admin': {'module_key': 'users', 'module_title': 'Users & Roles', 'section_name': 'Admin Users', 'icon': 'ti-user-shield'},







    'users_staff': {'module_key': 'users', 'module_title': 'Users & Roles', 'section_name': 'Staff Users', 'icon': 'ti-user-cog'},







    'users_candidates': {'module_key': 'users', 'module_title': 'Users & Roles', 'section_name': 'Candidate Users', 'icon': 'ti-user-search'},







    'users_roles': {'module_key': 'users', 'module_title': 'Users & Roles', 'section_name': 'User Roles', 'icon': 'ti-id-badge-2'},







    'users_permissions': {'module_key': 'users', 'module_title': 'Users & Roles', 'section_name': 'Permissions', 'icon': 'ti-lock-access'},







    'users_login_activity': {'module_key': 'users', 'module_title': 'Users & Roles', 'section_name': 'Login Activity', 'icon': 'ti-login'},















    # Notifications







    'notifications_all': {'module_key': 'notifications', 'module_title': 'Notifications', 'section_name': 'All Notifications', 'icon': 'ti-bell'},







    'notifications_send': {'module_key': 'notifications', 'module_title': 'Notifications', 'section_name': 'Send Notification', 'icon': 'ti-bell-plus'},







    'notifications_email': {'module_key': 'notifications', 'module_title': 'Notifications', 'section_name': 'Email Notifications', 'icon': 'ti-mail-notification'},







    'notifications_system': {'module_key': 'notifications', 'module_title': 'Notifications', 'section_name': 'System Notifications', 'icon': 'ti-bell-ringing'},







    'notifications_candidate': {'module_key': 'notifications', 'module_title': 'Notifications', 'section_name': 'Candidate Notifications', 'icon': 'ti-user-check'},







    'notifications_company': {'module_key': 'notifications', 'module_title': 'Notifications', 'section_name': 'Company Notifications', 'icon': 'ti-building'},







    'notifications_history': {'module_key': 'notifications', 'module_title': 'Notifications', 'section_name': 'Notification History', 'icon': 'ti-history'},















    # Reports & Analytics







    'reports_candidate': {'module_key': 'reports', 'module_title': 'Reports & Analytics', 'section_name': 'Candidate Reports', 'icon': 'ti-report'},







    'reports_company': {'module_key': 'reports', 'module_title': 'Reports & Analytics', 'section_name': 'Company Reports', 'icon': 'ti-report-analytics'},







    'reports_internship': {'module_key': 'reports', 'module_title': 'Reports & Analytics', 'section_name': 'Internship Reports', 'icon': 'ti-report-medical'},







    'reports_placement': {'module_key': 'reports', 'module_title': 'Reports & Analytics', 'section_name': 'Placement Reports', 'icon': 'ti-report-money'},







    'reports_job_offer': {'module_key': 'reports', 'module_title': 'Reports & Analytics', 'section_name': 'Job Offer Reports', 'icon': 'ti-file-analytics'},







    'reports_funnel': {'module_key': 'reports', 'module_title': 'Reports & Analytics', 'section_name': 'Recruitment Funnel', 'icon': 'ti-filter'},







    'reports_export': {'module_key': 'reports', 'module_title': 'Reports & Analytics', 'section_name': 'Export Reports', 'icon': 'ti-file-export'},















    # Activity & Logs







    'logs_admin': {'module_key': 'logs', 'module_title': 'Activity & Logs', 'section_name': 'Admin Activity Logs', 'icon': 'ti-history'},







    'logs_user': {'module_key': 'logs', 'module_title': 'Activity & Logs', 'section_name': 'User Activity Logs', 'icon': 'ti-user-check'},







    'logs_login': {'module_key': 'logs', 'module_title': 'Activity & Logs', 'section_name': 'Login Logs', 'icon': 'ti-login'},







    'logs_system': {'module_key': 'logs', 'module_title': 'Activity & Logs', 'section_name': 'System Logs', 'icon': 'ti-cpu'},







    'logs_audit': {'module_key': 'logs', 'module_title': 'Activity & Logs', 'section_name': 'Audit Logs', 'icon': 'ti-shield-lock'},















    # Settings







    'settings_general': {'module_key': 'settings', 'module_title': 'Settings', 'section_name': 'General Settings', 'icon': 'ti-settings'},







    'settings_profile': {'module_key': 'settings', 'module_title': 'Settings', 'section_name': 'Profile Settings', 'icon': 'ti-user-circle'},







    'settings_website': {'module_key': 'settings', 'module_title': 'Settings', 'section_name': 'Website Settings', 'icon': 'ti-world'},







    'settings_email': {'module_key': 'settings', 'module_title': 'Settings', 'section_name': 'Email Settings', 'icon': 'ti-mail-cog'},







    'settings_notification': {'module_key': 'settings', 'module_title': 'Settings', 'section_name': 'Notification Settings', 'icon': 'ti-bell-cog'},







    'settings_security': {'module_key': 'settings', 'module_title': 'Settings', 'section_name': 'Security Settings', 'icon': 'ti-shield-lock'},







    'settings_password': {'module_key': 'settings', 'module_title': 'Settings', 'section_name': 'Password & Authentication', 'icon': 'ti-key'},







    'settings_roles': {'module_key': 'settings', 'module_title': 'Settings', 'section_name': 'Role & Permission Settings', 'icon': 'ti-user-search'},







    'settings_documents': {'module_key': 'settings', 'module_title': 'Settings', 'section_name': 'Document Settings', 'icon': 'ti-file-code'},







    'settings_backup': {'module_key': 'settings', 'module_title': 'Settings', 'section_name': 'Backup & Restore', 'icon': 'ti-database-import'},







    'settings_system': {'module_key': 'settings', 'module_title': 'Settings', 'section_name': 'System Settings', 'icon': 'ti-cpu'},







}















def admin_root_redirect(request):







    admin_id = request.session.get('admin_id')







    if admin_id:







        return redirect('/admin-panel/dashboard/')







    return redirect('/admin-panel/login/')















@ensure_csrf_cookie







def admin_login_view(request):
    """Admin login view with logging to AdminLoginLog and session management."""
    admin_id = request.session.get('admin_id')
    if admin_id and request.method == 'GET':
        return redirect('/admin-panel/dashboard/')

    if request.method == 'POST':
        import json
        from apps.accounts.models import AdminUser, AdminLoginLog
        from apps.accounts.auth_helpers import get_client_ip, is_rate_limited
        from django.utils import timezone
        from apps.enquiries.models import log_activity
        from django.http import JsonResponse

        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json'

        try:
            data = json.loads(request.body) if request.body and request.content_type == 'application/json' else request.POST
        except Exception:
            data = request.POST

        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''
        ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        if is_rate_limited(f"login:{ip}", limit=5, window=900):
            if is_ajax:
                return JsonResponse({"status": "error", "message": "Too many attempts. Try again in 15 minutes."}, status=429)
            return render(request, 'dashboard/login.html', {'error': 'Too many attempts. Try again in 15 minutes.'}, status=429)

        try:
            admin = AdminUser.objects.select_related('role').get(email=email, is_active=True)
            if admin.verify_password(password):
                request.session.flush()
                request.session['admin_id'] = admin.id
                request.session['admin_email'] = admin.email
                request.session.set_expiry(8 * 3600)

                admin.last_login_at = timezone.now()
                admin.last_login_ip = ip
                admin.save(update_fields=['last_login_at', 'last_login_ip'])

                AdminLoginLog.objects.create(
                    email=email,
                    ip_address=ip,
                    status='success',
                    user_agent=user_agent
                )
                log_activity("admin_login", f"Admin {email} logged in successfully.")

                if is_ajax:
                    return JsonResponse({"status": "success", "redirect": "/admin-panel/dashboard/"})
                next_url = request.GET.get('next') or request.POST.get('next') or '/admin-panel/dashboard/'
                return redirect(next_url)
            else:
                AdminLoginLog.objects.create(
                    email=email,
                    ip_address=ip,
                    status='failed',
                    user_agent=user_agent
                )
                if is_ajax:
                    return JsonResponse({"status": "error", "message": "Invalid email or password."}, status=400)
                return render(request, 'dashboard/login.html', {'error': 'Invalid email or password.'}, status=400)
        except AdminUser.DoesNotExist:
            AdminLoginLog.objects.create(
                email=email,
                ip_address=ip,
                status='failed',
                user_agent=user_agent
            )
            if is_ajax:
                return JsonResponse({"status": "error", "message": "Invalid email or password."}, status=400)
            return render(request, 'dashboard/login.html', {'error': 'Invalid email or password.'}, status=400)

    return render(request, 'dashboard/login.html')

def admin_dashboard_view(request):







    admin_id = request.session.get('admin_id')







    if not admin_id:







        return redirect('/admin-panel/login/')















    admin_user = AdminUser.objects.filter(id=admin_id).first()















    # Database Metrics (Exact real DB values)







    total_candidates_db = CandidateAccount.objects.count()







    candidates_pending_db = CandidateAccount.objects.filter(approval_status='pending').count()















    total_employers_db = EmployerAccount.objects.count()







    employers_pending_db = EmployerAccount.objects.filter(status='PENDING').count()















    total_agencies_db = InternshipProvider.objects.count()







    total_internship_apps_db = InternshipApplication.objects.count()







    internships_pending_db = InternshipApplication.objects.filter(models.Q(status__iexact='Pending') | models.Q(status__iexact='New')).count()







    agencies_pending_db = internships_pending_db















    jobs_live_db = Job.objects.filter(status__in=Job.LIVE_STATUSES).count()







    jobs_pending_db = Job.objects.filter(status__in=Job.PENDING_STATUSES).count()







    jobs_draft_db = Job.objects.filter(status=Job.STATUS_DRAFT).count()







    jobs_expired_db = Job.objects.filter(status__in=Job.CLOSED_STATUSES).count()















    total_apps_db = Applicant.objects.count()







    total_hired_db = Placement.objects.filter(status__icontains='Joined').count() + Applicant.objects.filter(status__icontains='Joined').count()







    total_shortlisted_db = Applicant.objects.filter(status__icontains='Shortlisted').count()







    total_interviews_db = Interview.objects.count()







    total_offers_db = JobOffer.objects.count()







    total_staff_db = AdminUser.objects.count()















    # Application Status Breakdown







    app_applied = Applicant.objects.filter(models.Q(status__icontains='Received') | models.Q(status__icontains='Applied') | models.Q(status='New')).count()







    app_shortlisted = total_shortlisted_db







    app_interview = total_interviews_db







    app_offered = total_offers_db







    app_rejected = Applicant.objects.filter(status__icontains='Reject').count()















    # Lists for Tables







    recent_apps_qs = list(Applicant.objects.select_related('job').order_by('-id')[:5])







    latest_jobs_qs = list(Job.objects.order_by('-id')[:5])







    upcoming_interviews_qs = list(Interview.objects.order_by('interview_date', 'interview_time')[:5])







    recent_notifications_qs = list(ActivityLog.objects.order_by('-id')[:5])







    top_employers_qs = list(EmployerAccount.objects.all().order_by('-id')[:5])















    context = {







        'admin_user': admin_user,







        







        # Primary Top KPI Cards (Real DB values)







        'total_candidates': total_candidates_db,







        'candidates_pending_approval': candidates_pending_db,







        'total_employers': total_employers_db,







        'employers_pending_approval': employers_pending_db,







        'total_agencies': total_agencies_db,







        'total_internship_apps': total_internship_apps_db,







        'internships_pending_approval': internships_pending_db,







        'agencies_pending_approval': agencies_pending_db,







        'jobs_live': jobs_live_db,







        'jobs_pending_approval': jobs_pending_db,







        'jobs_draft': jobs_draft_db,







        'jobs_expired': jobs_expired_db,







        'total_applications': total_apps_db,







        'total_hired_this_month': total_hired_db,















        # Bottom KPIs (Real DB values)







        'total_joined': total_hired_db,







        'total_shortlisted': total_shortlisted_db,







        'total_interviews': total_interviews_db,







        'total_offers': total_offers_db,







        'total_active_jobs': jobs_live_db,







        'total_expired_jobs': jobs_expired_db,







        'total_agencies_live': total_agencies_db,







        'total_staff_users': total_staff_db,















        # Application Breakdown







        'app_applied': app_applied,







        'app_shortlisted': app_shortlisted,







        'app_interview': app_interview,







        'app_offered': app_offered,







        'app_rejected': app_rejected,















        # Table data lists







        'recent_applications': recent_apps_qs,







        'latest_jobs': latest_jobs_qs,







        'upcoming_interviews': upcoming_interviews_qs,







        'recent_notifications': recent_notifications_qs,







        'top_employers': top_employers_qs,







    }







    return render(request, 'dashboard/dashboard.html', context)















def _get_status_class(status):







    st = str(status or '').strip().lower()







    if st in ['approved', 'active', 'selected', 'verified', 'joined', 'placed', 'accepted', 'completed', 'resolved', 'fulfilled']:







        return 'active'







    elif st in ['new', 'pending', 'upcoming', 'shortlisted', 'under review', 'contacted', 'offer sent', 'unread']:







        return 'shortlisted'







    elif st in ['rejected', 'cancelled', 'expired', 'closed']:







        return 'rejected'







    return 'info'















SECTION_TO_ACTIVE_MENU = {







    'job_applications_all': 'applications',







    'job_applications_pending': 'applications',







    'candidates_all': 'candidates',







    'candidates_registrations': 'candidates',







    'candidates_add': 'candidates',







    'candidates_profiles': 'candidates',







    'candidates_shortlisted': 'shortlisted',







    'interviews_upcoming': 'interviews',







    'interviews_completed': 'interviews',







    'interviews_cancelled': 'interviews',







    'candidates_selected': 'selections',







    'candidates_rejected': 'candidates',







    'candidates_placed': 'joinings',







    'companies_all': 'employers',







    'companies_add': 'employers',







    'companies_enquiries': 'enquiries',







    'requirements_all': 'job_categories',







    'requirements_active': 'job_approvals',







    'requirements_closed': 'jobs',







    'requirements_expired': 'jobs',







    'job_openings': 'jobs',







    'company_contacts': 'employers',







    'internships_all': 'agencies',







    'internships_add': 'agencies',







    'internships_enquiries': 'agencies',







    'internship_apps_all': 'agencies',







    'internship_apps_pending': 'agencies',







    'internship_apps_shortlisted': 'agencies',







    'internship_apps_selected': 'agencies',







    'internship_apps_rejected': 'agencies',







    'internships_active': 'agencies',







    'internships_completed': 'agencies',







    'internship_providers': 'agencies',







    'enquiries_all': 'enquiries',







    'enquiries_general': 'enquiries',







    'enquiries_company': 'enquiries',







    'enquiries_internship': 'enquiries',







    'enquiries_candidate': 'enquiries',







    'enquiries_unread': 'enquiries',







    'enquiries_resolved': 'enquiries',







    'placements_all': 'joinings',







    'placements_active': 'joinings',







    'placements_completed': 'joinings',







    'placements_pending_joining': 'joinings',







    'placements_joined': 'joinings',







    'placements_history': 'payments',







    'placements_reports': 'commission',







    'offers_all': 'offer_letters',







    'offers_create': 'offer_letters',







    'offers_pending': 'offer_letters',







    'offers_accepted': 'offer_letters',







    'offers_rejected': 'offer_letters',







    'offers_expired': 'offer_letters',







    'offers_history': 'offer_letters',







    'documents_all': 'invoices',







    'documents_candidate': 'invoices',







    'documents_company': 'invoices',







    'documents_internship': 'invoices',







    'documents_offer_letters': 'offer_letters',







    'documents_joining': 'invoices',







    'verification_pending': 'invoices',







    'verification_verified': 'invoices',







    'verification_rejected': 'invoices',







    'followups_all': 'email_sms',







    'followups_today': 'email_sms',







    'followups_upcoming': 'email_sms',







    'followups_overdue': 'email_sms',







    'followups_candidate': 'email_sms',







    'followups_company': 'email_sms',







    'followups_internship': 'email_sms',







    'followups_completed': 'email_sms',







    'users_all': 'staff',







    'users_add': 'staff',







    'users_admin': 'staff',







    'users_staff': 'staff',







    'users_candidates': 'candidates',







    'users_roles': 'roles',







    'users_permissions': 'roles',







    'users_login_activity': 'logs',







    'notifications_all': 'notifications',







    'notifications_send': 'whatsapp',







    'notifications_email': 'email_sms',







    'notifications_system': 'notifications',







    'notifications_candidate': 'notifications',







    'notifications_company': 'notifications',







    'notifications_history': 'notifications',







    'reports_candidate': 'reports',







    'reports_company': 'reports',







    'reports_internship': 'reports',







    'reports_placement': 'reports',







    'reports_job_offer': 'reports',







    'reports_funnel': 'analytics',







    'reports_export': 'reports',







    'logs_admin': 'logs',







    'logs_user': 'logs',







    'logs_login': 'logs',







    'logs_system': 'logs',







    'logs_audit': 'logs',







    'settings_general': 'settings',







    'settings_profile': 'settings',







    'settings_website': 'settings',







    'settings_email': 'settings',







    'settings_notification': 'settings',







    'settings_security': 'settings',







    'settings_password': 'settings',







    'settings_roles': 'roles',







    'settings_documents': 'settings',







    'settings_backup': 'settings',







    'settings_system': 'settings',







}















def admin_module_generic_view(request, section_key='candidates_all'):







    admin_id = request.session.get('admin_id')







    if not admin_id:







        return redirect('/admin-panel/login/')















    admin_user = AdminUser.objects.filter(id=admin_id).first()







    active_menu = SECTION_TO_ACTIVE_MENU.get(section_key, 'dashboard')















    sec_info = MODULE_SECTIONS.get(section_key, {







        'module_key': 'dashboard',







        'module_title': 'Admin Module',







        'section_name': section_key.replace('_', ' ').title(),







        'icon': 'ti-folder'







    })















    module_key = sec_info['module_key']







    records = []















    # 1. CANDIDATES MODULE







    if module_key == 'candidates':







        applicants = list(Applicant.objects.exclude(job_title__icontains="intern").all())







        resumes = list(Resume.objects.all())















        all_candidates = []















        for a in applicants:







            owner_emp = a.job.employer if (a.job and a.job.employer) else None







            has_owner_emp = bool(owner_emp)







            owner_emp_name = owner_emp.company_name if owner_emp else ""







            owner_comp_name = (a.job.company.name if (a.job and a.job.company) else "") or owner_emp_name















            comp_name = owner_emp_name or (a.company.name if a.company else (a.current_company or ""))







            job_title_disp = a.job.title if a.job else a.job_title















            sub = f"{a.email} • {a.phone}"







            if comp_name:







                sub = f"{comp_name} • {sub}"















            all_candidates.append({







                'id': f"APP-{a.id}",







                'raw_id': a.id,







                'name': a.full_name,







                'full_name': a.full_name,







                'title': a.full_name,







                'email': a.email,







                'phone': a.phone,







                'company_name': comp_name or "Sky Vision Partner",







                'employer_id': owner_emp.id if owner_emp else None,







                'employer_name': owner_emp_name,







                'has_owner_employer': has_owner_emp,







                'owner_employer_name': owner_emp_name,







                'owner_company_name': owner_comp_name,







                'job_title_display': job_title_disp,







                'subtitle': sub,







                'category': job_title_disp or "Job Seeker",







                'city': a.city or "",







                'state': a.state or "",







                'qualification': a.qualification or "",







                'experience': a.experience or 0,







                'skills': a.skills or "",







                'current_company': a.current_company or "",







                'current_salary': a.current_salary or "",







                'expected_salary': a.expected_salary or "",







                'availability': a.availability or "",







                'cover_letter': a.cover_letter or "",







                'notes': a.notes or "",







                'date': a.applied_on.strftime("%d %b %Y") if a.applied_on else "N/A",







                'created_at': a.applied_on,







                'status': a.status or "New",







                'approval_status': a.approval_status or ("Approved" if (a.status or "").lower() in ["shortlisted", "interview", "interview scheduled", "offer released", "selected", "joined", "placed"] else "Pending"),







                'flow_step': a.flow_step or 3,







                'status_class': _get_status_class(a.status),







                'resume_url': f"/api/admin/files/download/{a.resume}" if a.resume else "",







                'type': 'Job Seeker',







                'model': 'applicant',







                'job_id': a.job_id







            })















        for r in resumes:







            all_candidates.append({







                'id': f"RES-{r.id}",







                'raw_id': r.id,







                'name': r.full_name,







                'full_name': r.full_name,







                'title': r.full_name,







                'email': r.email,







                'phone': r.mobile,







                'subtitle': f"{r.email} • {r.mobile}",







                'category': r.applying_for or "Quick Resume",







                'city': r.city or "",







                'qualification': r.qualification or "",







                'experience': r.experience or "",







                'message': r.message or "",







                'notes': r.notes or "",







                'date': r.uploaded_on.strftime("%d %b %Y") if r.uploaded_on else "N/A",







                'created_at': r.uploaded_on,







                'status': r.status or "New",







                'status_class': _get_status_class(r.status),







                'resume_url': f"/api/admin/files/download/{r.resume}" if r.resume else "",







                'type': 'Quick Resume',







                'model': 'resume'







            })















        # Flag duplicates: only if the exact same candidate applies for the SAME job/role multiple times







        email_cat_counts = {}







        phone_cat_counts = {}







        for c in all_candidates:







            em = (c['email'] or "").strip().lower()







            ph = (c['phone'] or "").strip()







            cat = (c['category'] or "").strip().lower()







            if em:







                key = (em, cat)







                email_cat_counts[key] = email_cat_counts.get(key, 0) + 1







            if ph:







                key = (ph, cat)







                phone_cat_counts[key] = phone_cat_counts.get(key, 0) + 1















        for c in all_candidates:







            em = (c['email'] or "").strip().lower()







            ph = (c['phone'] or "").strip()







            cat = (c['category'] or "").strip().lower()







            is_dup = (em and email_cat_counts.get((em, cat), 0) > 1) or (ph and phone_cat_counts.get((ph, cat), 0) > 1)







            c['is_duplicate'] = is_dup















        today = timezone.now().date()







        interviews_qs = list(Interview.objects.all().order_by('-interview_date', '-interview_time'))















        if section_key == 'candidates_profiles':







            records = all_candidates







        elif section_key == 'candidates_shortlisted':







            records = [







                c for c in all_candidates 







                if c.get('flow_step', 0) >= 4 or 







                   c.get('approval_status') == 'Approved' or 







                   c['status'].lower() in ['shortlisted', 'interview', 'interview scheduled', 'selected', 'offer released', 'offered', 'offer sent', 'accepted', 'joined', 'placed']







            ]







        elif section_key == 'interviews_upcoming':







            upcoming_interviews = [iv for iv in interviews_qs if iv.status in ['Scheduled', 'Rescheduled']]







            if not upcoming_interviews and interviews_qs:







                upcoming_interviews = interviews_qs







            scheduled_cand_ids = {(iv.candidate_type, iv.candidate_id) for iv in upcoming_interviews}















            records = []







            for iv in upcoming_interviews:







                st_cls = 'rejected' if iv.is_overdue() else ('active' if iv.result == 'Selected' else ('info' if iv.status == 'Completed' else 'upcoming'))







                records.append({







                    'id': f"INT-{iv.id}",







                    'interview_id': iv.id,







                    'raw_id': iv.id,







                    'candidate_id': iv.candidate_id,







                    'name': iv.candidate_name,







                    'full_name': iv.candidate_name,







                    'title': iv.candidate_name,







                    'email': iv.candidate_email,







                    'phone': iv.candidate_phone,







                    'subtitle': f"{iv.candidate_email} • {iv.candidate_phone}",







                    'category': iv.job_title,







                    'date': iv.interview_date.strftime("%d %b %Y") if iv.interview_date else "Date not set",







                    'interview_date': iv.interview_date.strftime("%Y-%m-%d") if iv.interview_date else "",







                    'interview_time': iv.interview_time.strftime("%I:%M %p") if iv.interview_time else "",







                    'interview_mode': iv.interview_mode,







                    'location_or_link': iv.location_or_link or "",







                    'status': f"Completed ({iv.result})" if (iv.status == 'Completed' and iv.result) else iv.status,







                    'status_class': st_cls,







                    'is_overdue': iv.is_overdue(),







                    'date_not_set': False,







                    'type': 'Interview Scheduled',







                    'model': iv.candidate_type,







                    'candidate_type': iv.candidate_type,







                    'interview_obj': iv.to_dict()







                })















            # Check for legacy candidates with status 'Interview' missing an active Interview table row







            for c in all_candidates:







                if c['status'].lower() == 'interview' and (c['model'], c['raw_id']) not in scheduled_cand_ids:







                    records.append({







                        'id': f"INT-LEGACY-{c['id']}",







                        'interview_id': None,







                        'raw_id': c['raw_id'],







                        'candidate_id': c['raw_id'],







                        'name': c['name'],







                        'full_name': c['full_name'],







                        'title': c['full_name'],







                        'email': c['email'],







                        'phone': c['phone'],







                        'subtitle': f"{c['email']} • {c['phone']}",







                        'category': c['category'],







                        'date': "Date not set",







                        'interview_date': "",







                        'interview_time': "",







                        'interview_mode': "Pending Schedule",







                        'location_or_link': "",







                        'status': "Date not set",







                        'status_class': 'pending',







                        'is_overdue': False,







                        'date_not_set': True,







                        'type': c['type'],







                        'model': c['model'],







                        'candidate_type': c['model'],







                        'interview_obj': None







                    })















        elif section_key == 'interviews_completed':







            completed_ivs = [iv for iv in interviews_qs if iv.status == 'Completed']







            records = []







            for iv in completed_ivs:







                records.append({







                    'id': f"INT-{iv.id}",







                    'interview_id': iv.id,







                    'raw_id': iv.id,







                    'name': iv.candidate_name,







                    'full_name': iv.candidate_name,







                    'title': iv.candidate_name,







                    'email': iv.candidate_email,







                    'phone': iv.candidate_phone,







                    'subtitle': f"{iv.candidate_email} • {iv.candidate_phone}",







                    'category': iv.job_title,







                    'date': iv.interview_date.strftime("%d %b %Y") if iv.interview_date else "N/A",







                    'interview_date': iv.interview_date.strftime("%Y-%m-%d") if iv.interview_date else "",







                    'interview_time': iv.interview_time.strftime("%I:%M %p") if iv.interview_time else "",







                    'interview_mode': iv.interview_mode,







                    'status': f"Completed ({iv.result})" if iv.result else "Completed",







                    'result': iv.result,







                    'feedback': iv.feedback,







                    'status_class': 'active' if iv.result == 'Selected' else ('rejected' if iv.result == 'Rejected' else 'info'),







                    'type': 'Completed Interview',







                    'model': iv.candidate_type,







                    'interview_obj': iv.to_dict()







                })















        elif section_key == 'interviews_cancelled':







            cancelled_ivs = [iv for iv in interviews_qs if iv.status == 'Cancelled']







            records = []







            for iv in cancelled_ivs:







                records.append({







                    'id': f"INT-{iv.id}",







                    'interview_id': iv.id,







                    'raw_id': iv.id,







                    'name': iv.candidate_name,







                    'full_name': iv.candidate_name,







                    'title': iv.candidate_name,







                    'email': iv.candidate_email,







                    'phone': iv.candidate_phone,







                    'subtitle': f"{iv.candidate_email} • {iv.candidate_phone}",







                    'category': iv.job_title,







                    'date': iv.interview_date.strftime("%d %b %Y") if iv.interview_date else "N/A",







                    'status': 'Cancelled',







                    'cancel_reason': iv.cancel_reason,







                    'status_class': 'rejected',







                    'type': 'Cancelled Interview',







                    'model': iv.candidate_type,







                    'interview_obj': iv.to_dict()







                })















        elif section_key == 'candidates_registrations':







            reg_type = request.GET.get('type') or request.GET.get('tab') or 'candidate'







            records = []







            if reg_type == 'employer':







                emp_accounts = list(EmployerAccount.objects.all().order_by('-id'))







                for e in emp_accounts:







                    st_val = (e.status or 'PENDING').lower()







                    st_text = 'Approved' if st_val == 'approved' else ('Rejected' if st_val == 'rejected' else ('Suspended' if st_val == 'suspended' else 'Pending Approval'))







                    st_cls = 'active' if st_val == 'approved' else ('rejected' if st_val in ['rejected', 'suspended'] else 'shortlisted')







                    doc_path = getattr(e, 'document', '') or ''







                    records.append({







                        'id': f"EMP-{e.id}",







                        'raw_id': e.id,







                        'name': e.company_name,







                        'full_name': e.contact_name,







                        'title': e.company_name,







                        'company_name': e.company_name,







                        'contact_name': e.contact_name,







                        'email': e.email,







                        'phone': e.phone,







                        'subtitle': f"{e.contact_name} ({e.industry or 'Employer'}) • {e.email} • {e.phone}",







                        'category': e.industry or e.city or "Employer",







                        'city': e.city or "N/A",







                        'state': e.state or "N/A",







                        'company_size': e.company_size or "N/A",







                        'website': e.website or "",







                        'gstin': getattr(e, 'gst_number', '') or "",







                        'rejection_reason': e.rejection_reason or "",







                        'date': e.created_at.strftime("%d %b %Y, %I:%M %p") if e.created_at else "N/A",







                        'created_at': e.created_at,







                        'status': st_text,







                        'approval_status': st_val,







                        'status_class': st_cls,







                        'doc_url': f"/api/admin/files/download/{doc_path}" if doc_path else "",







                        'type': 'Employer Registration',







                        'model': 'employer_account'







                    })







                total_count = len(emp_accounts)







                active_count = sum(1 for e in emp_accounts if (e.status or '').lower() == 'approved')







                pending_count = sum(1 for e in emp_accounts if (e.status or '').lower() == 'pending')







                archived_count = sum(1 for e in emp_accounts if (e.status or '').lower() in ['rejected', 'suspended'])







            else:







                cand_accounts = list(CandidateAccount.objects.all().order_by('-id'))







                for c in cand_accounts:







                    st_text = 'Approved' if c.approval_status == 'approved' else ('Rejected' if c.approval_status == 'rejected' else 'Pending Approval')







                    st_cls = 'active' if c.approval_status == 'approved' else ('rejected' if c.approval_status == 'rejected' else 'shortlisted')







                    records.append({







                        'id': f"REG-{c.id}",







                        'raw_id': c.id,







                        'name': c.full_name,







                        'full_name': c.full_name,







                        'title': c.full_name,







                        'email': c.email,







                        'phone': c.phone,







                        'subtitle': f"{c.email} • {c.phone}",







                        'category': c.city or "General",







                        'city': c.city or "N/A",







                        'qualification': c.qualification or "N/A",







                        'experience': c.experience or 0,







                        'date': c.created_at.strftime("%d %b %Y, %I:%M %p") if c.created_at else "N/A",







                        'created_at': c.created_at,







                        'status': st_text,







                        'approval_status': c.approval_status,







                        'status_class': st_cls,







                        'resume_url': f"/api/admin/files/download/{c.resume}" if c.resume else "",







                        'type': 'Candidate Registration',







                        'model': 'candidate_account'







                    })







                total_count = len(cand_accounts)







                active_count = sum(1 for c in cand_accounts if c.approval_status == 'approved')







                pending_count = sum(1 for c in cand_accounts if c.approval_status == 'pending')







                archived_count = sum(1 for c in cand_accounts if c.approval_status == 'rejected')







        elif section_key == 'candidates_selected':







            selected_app_ids = set(Interview.objects.filter(result__iexact='Selected').values_list('applicant_id', flat=True))







            offer_app_ids = set(JobOffer.objects.values_list('applicant_id', flat=True))







            placement_app_ids = set(Placement.objects.values_list('applicant_id', flat=True))















            sync_cand_ids = set()







            for c in all_candidates:







                raw_id = c.get('raw_id')







                st = (c.get('status') or '').strip().lower()







                if (







                    st in ['selected', 'offer released', 'offered', 'offer sent', 'accepted', 'joined', 'placed'] or







                    raw_id in selected_app_ids or







                    raw_id in offer_app_ids or







                    raw_id in placement_app_ids or







                    c.get('flow_step', 0) >= 6







                ):







                    sync_cand_ids.add(raw_id)















            if sync_cand_ids:







                Interview.objects.filter(







                    applicant_id__in=sync_cand_ids, 







                    status__in=['Scheduled', 'Rescheduled']







                ).update(status='Completed', result='Selected')















            selected_records = []







            for c in all_candidates:







                raw_id = c.get('raw_id')







                st = (c.get('status') or '').strip().lower()







                if raw_id in sync_cand_ids or st == 'selected':







                    c_copy = dict(c)







                    c_copy['status_class'] = 'active'







                    selected_records.append(c_copy)







            records = selected_records







        elif section_key == 'candidates_rejected':







            records = [c for c in all_candidates if c['status'].lower() == 'rejected']







        elif section_key == 'candidates_placed':







            records = [c for c in all_candidates if c['status'].lower() == 'placed']







        elif section_key == 'candidates_add':







            records = []







        else: # candidates_all







            records = all_candidates















        if section_key != 'candidates_registrations':







            total_count = len(records)







            active_count = sum(1 for c in records if str(c.get('status', '')).lower() in ['selected', 'placed', 'active', 'completed', 'scheduled'])







            pending_count = sum(1 for c in records if str(c.get('status', '')).lower() in ['new', 'pending', 'shortlisted', 'interview', 'upcoming', 'date not set'])







            archived_count = sum(1 for c in records if str(c.get('status', '')).lower() in ['rejected', 'cancelled'])























    # 2. COMPANIES MODULE







    elif module_key == 'companies':







        sync_expired_requirements()







        records = []















        if section_key == 'companies_all':







            companies = Company.objects.prefetch_related('contacts', 'requirements').all().order_by('-id')







            for c in companies:







                all_contacts = list(c.contacts.all())







                primary_contact = next((ct for ct in all_contacts if ct.is_primary), all_contacts[0] if all_contacts else None)







                contact_info = f"{primary_contact.name} ({primary_contact.designation or 'Contact'})" if primary_contact else "No contact"







                records.append({







                    'id': f"CMP-{c.id}",







                    'raw_id': c.id,







                    'name': c.name,







                    'company_name': c.name,







                    'title': c.name,







                    'subtitle': f"{c.city} • {c.email} • {c.phone} • Primary: {contact_info}",







                    'category': c.industry or "Corporate Employer",







                    'industry': c.industry or "",







                    'website': c.website or "",







                    'email': c.email,







                    'phone': c.phone,







                    'address': c.address or "",







                    'city': c.city or "Lucknow",







                    'state': c.state or "Uttar Pradesh",







                    'gst_number': c.gst_number or "",







                    'notes': c.notes or "",







                    'primary_contact_name': primary_contact.name if primary_contact else "",







                    'primary_contact_designation': primary_contact.designation if primary_contact else "",







                    'primary_contact_email': primary_contact.email if primary_contact else "",







                    'primary_contact_phone': primary_contact.phone if primary_contact else "",







                    'contacts_count': len(all_contacts),







                    'requirements_count': c.requirements.count(),







                    'date': c.created_at.strftime("%d %b %Y") if c.created_at else "N/A",







                    'created_at': c.created_at,







                    'status': c.status or "Active",







                    'status_class': _get_status_class(c.status),







                    'type': 'Company',







                    'model': 'company'







                })















        elif section_key == 'companies_add':







            records = []















        elif section_key == 'companies_enquiries':







            enquiries = CompanyEnquiry.objects.all().order_by('-id')







            for e in enquiries:







                records.append({







                    'id': f"ENQ-{e.id}",







                    'raw_id': e.id,







                    'name': e.company_name,







                    'company_name': e.company_name,







                    'recruiter_name': e.recruiter_name,







                    'designation': e.designation or '',







                    'phone': e.phone,







                    'email': e.email,







                    'address': e.address or '',







                    'job_title': e.job_title or '',







                    'department': e.department or '',







                    'job_type': e.job_type or 'Full Time',







                    'application_deadline': e.application_deadline or '30 Days',







                    'vacancies': e.vacancies or '1',







                    'experience_req': e.experience_req or '',







                    'salary_range': e.salary_range or '',







                    'requirements': e.requirements or '',







                    'message': e.message or '',







                    'notes': e.notes or '',







                    'title': e.company_name,







                    'subtitle': f"{e.recruiter_name} ({e.designation or 'Recruiter'}) • {e.email} • {e.phone}",







                    'category': e.job_title or "Hiring Requirement",







                    'date': e.created_at.strftime("%d %b %Y") if e.created_at else "N/A",







                    'created_at': e.created_at,







                    'status': e.status or "New",







                    'status_class': _get_status_class(e.status),







                    'type': 'Company Enquiry',







                    'model': 'company_enquiry'







                })















        elif section_key in ['requirements_all', 'requirements_active', 'requirements_closed', 'requirements_expired']:







            req_qs = CompanyRequirement.objects.all().order_by('-id')







            comp_id_param = request.GET.get('company_id') or request.GET.get('company')







            if comp_id_param:







                try:







                    req_qs = req_qs.filter(company_id=int(comp_id_param))







                except (ValueError, TypeError):







                    pass















            if section_key == 'requirements_active':







                req_qs = req_qs.filter(status='Active')







            elif section_key == 'requirements_closed':







                req_qs = req_qs.filter(status__in=['Closed', 'Rejected'])







            elif section_key == 'requirements_expired':







                req_qs = req_qs.filter(status='Expired')















            for r in req_qs:







                recruiter_name = ""







                designation = ""







                email = ""







                phone = ""















                if r.contact:







                    recruiter_name = r.contact.name







                    designation = r.contact.designation or ""







                    email = r.contact.email or (r.company.email if r.company else "")







                    phone = r.contact.phone or (r.company.phone if r.company else "")







                elif r.source_enquiry:







                    recruiter_name = r.source_enquiry.recruiter_name







                    designation = r.source_enquiry.designation or ""







                    email = r.source_enquiry.email or (r.company.email if r.company else "")







                    phone = r.source_enquiry.phone or (r.company.phone if r.company else "")







                elif r.company:







                    prim = r.company.contacts.filter(is_primary=True).first() or r.company.contacts.first()







                    if prim:







                        recruiter_name = prim.name







                        designation = prim.designation or ""







                        email = prim.email or r.company.email







                        phone = prim.phone or r.company.phone







                    else:







                        email = r.company.email or ""







                        phone = r.company.phone or ""















                company_str = r.company.name if r.company else "N/A"







                recruiter_str = f" ({recruiter_name})" if recruiter_name else ""















                records.append({







                    'id': f"REQ-{r.id}",







                    'raw_id': r.id,







                    'name': r.title,







                    'title': r.title,







                    'company_name': company_str,







                    'company_id': r.company_id,







                    'contact_name': recruiter_name,







                    'contact_id': r.contact_id,







                    'recruiter_name': recruiter_name,







                    'designation': designation,







                    'email': email,







                    'phone': phone,







                    'job_id': r.job_id,







                    'job_published': bool(r.job_id),







                    'department': r.department or "General",







                    'job_type': r.job_type or "Full Time",







                    'location': r.location or "Lucknow, UP",







                    'vacancies': r.vacancies or "1",







                    'experience_req': r.experience_req or "",







                    'salary_range': r.salary_range or "",







                    'description': r.description or "",







                    'requirements': r.requirements or "",







                    'deadline': r.deadline or "",







                    'notes': r.notes or "",







                    'subtitle': f"{company_str}{recruiter_str} • {r.job_type} • {r.vacancies} Vacancies",







                    'category': r.department or "Hiring Position",







                    'date': r.created_at.strftime("%d %b %Y") if r.created_at else "N/A",







                    'created_at': r.created_at,







                    'status': r.status or "Active",







                    'status_class': _get_status_class(r.status),







                    'type': 'Company Requirement',







                    'model': 'requirement'







                })















        elif section_key == 'job_openings':







            jobs = Job.objects.select_related('company', 'employer').all().order_by('-id')







            for j in jobs:







                comp_name = j.company.name if j.company else (j.employer.company_name if j.employer else "SVG Consultancy")







                dept_cat = j.category or j.department or "General"







                loc_str = j.location or "Lucknow, UP"







                type_str = j.employment_type or "Full Time"







                vac_str = j.vacancies or "1"







                records.append({







                    'id': f"JOB-{j.id}",







                    'raw_id': j.id,







                    'name': j.title,







                    'title': j.title,







                    'company_name': comp_name,







                    'category': dept_cat,







                    'department': j.department or "General",







                    'location': loc_str,







                    'employment_type': type_str,







                    'job_type': type_str,







                    'experience': j.experience or "",







                    'salary': j.salary or "",







                    'salary_range': j.salary or "",







                    'vacancies': vac_str,







                    'description': j.description or "",







                    'requirements': j.requirements or "",







                    'subtitle': f"{comp_name} • {dept_cat} • {loc_str} • {type_str} ({vac_str} Vacancies)",







                    'date': j.created_at.strftime("%d %b %Y") if j.created_at else "N/A",







                    'created_at': j.created_at,







                    'status': j.status or "Active",







                    'status_class': _get_status_class(j.status),







                    'type': 'Job Posting',







                    'model': 'job'







                })















        elif section_key == 'company_contacts':







            contacts = CompanyContact.objects.all().order_by('-id')







            comp_id_param = request.GET.get('company_id') or request.GET.get('company')







            if comp_id_param:







                try:







                    contacts = contacts.filter(company_id=int(comp_id_param))







                except (ValueError, TypeError):







                    pass







            for c in contacts:







                records.append({







                    'id': f"CNT-{c.id}",







                    'raw_id': c.id,







                    'name': c.name,







                    'full_name': c.name,







                    'title': c.name,







                    'company_name': c.company.name if c.company else "N/A",







                    'company_id': c.company_id,







                    'designation': c.designation or "",







                    'email': c.email or "",







                    'phone': c.phone or "",







                    'is_primary': c.is_primary,







                    'notes': c.notes or "",







                    'subtitle': f"{c.company.name if c.company else 'N/A'} ({c.designation or 'Contact'}) • {c.email} • {c.phone}",







                    'category': c.designation or "Corporate Contact",







                    'date': c.created_at.strftime("%d %b %Y") if c.created_at else "N/A",







                    'created_at': c.created_at,







                    'status': "Primary" if c.is_primary else "Secondary",







                    'status_class': _get_status_class("active" if c.is_primary else "shortlisted"),







                    'type': 'Company Contact',







                    'model': 'contact'







                })















        else: # Default fallback to all companies







            companies = Company.objects.all().order_by('-id')







            for c in companies:







                records.append({







                    'id': f"CMP-{c.id}",







                    'raw_id': c.id,







                    'name': c.name,







                    'company_name': c.name,







                    'title': c.name,







                    'subtitle': f"{c.city} • {c.email} • {c.phone}",







                    'category': c.industry or "Corporate Employer",







                    'email': c.email,







                    'phone': c.phone,







                    'date': c.created_at.strftime("%d %b %Y") if c.created_at else "N/A",







                    'created_at': c.created_at,







                    'status': c.status or "Active",







                    'status_class': _get_status_class(c.status),







                    'type': 'Company',







                    'model': 'company'







                })















        total_count = len(records)







        active_count = sum(1 for c in records if str(c.get('status', '')).lower() in ['approved', 'active', 'verified', 'fulfilled', 'primary'])







        pending_count = sum(1 for c in records if str(c.get('status', '')).lower() in ['new', 'pending', 'under review', 'draft', 'secondary'])







        archived_count = sum(1 for c in records if str(c.get('status', '')).lower() in ['rejected', 'expired', 'closed', 'blocked', 'inactive'])















    # 3. INTERNSHIPS MODULE







    elif module_key == 'internships':







        if section_key == 'internship_providers':







            providers = list(InternshipProvider.objects.all())







            records = []







            for p in providers:







                records.append({







                    'id': f"PRV-{p.id}",







                    'raw_id': p.id,







                    'name': p.name,







                    'title': p.name,







                    'contact_person': p.contact_person or '',







                    'email': p.email or '',







                    'phone': p.phone or '',







                    'industry': p.industry or '',







                    'address': p.address or '',







                    'notes': p.notes or '',







                    'is_active': p.is_active,







                    'subtitle': f"Contact: {p.contact_person or 'N/A'} • {p.email or 'N/A'} • {p.phone or 'N/A'}",







                    'category': p.industry or "Provider",







                    'date': p.created_at.strftime("%d %b %Y") if p.created_at else "N/A",







                    'created_at': p.created_at,







                    'status': "Active" if p.is_active else "Inactive",







                    'status_class': 'active' if p.is_active else 'rejected',







                    'resume_url': "",







                    'type': 'Internship Provider',







                    'model': 'internship_provider'







                })







            all_list = list(InternshipProvider.objects.all())







            total_count = len(all_list)







            active_count = sum(1 for item in all_list if item.is_active)







            pending_count = 0







            archived_count = sum(1 for item in all_list if not item.is_active)















        elif section_key.startswith('internship_apps_'):







            apps_qs = InternshipApplication.objects.all().order_by('-id')







            int_id_param = request.GET.get('internship_id') or request.GET.get('internship')







            if int_id_param:







                try:







                    apps_qs = apps_qs.filter(internship_id=int(int_id_param))







                except (ValueError, TypeError):







                    pass















            if section_key == 'internship_apps_pending':







                apps_qs = apps_qs.filter(status='Pending')







            elif section_key == 'internship_apps_shortlisted':







                apps_qs = apps_qs.filter(status='Shortlisted')







            elif section_key == 'internship_apps_selected':







                apps_qs = apps_qs.filter(status='Selected')







            elif section_key == 'internship_apps_rejected':







                apps_qs = apps_qs.filter(status='Rejected')















            records = []







            for a in apps_qs:







                records.append({







                    'id': f"APP-{a.id}",







                    'raw_id': a.id,







                    'name': a.full_name,







                    'full_name': a.full_name,







                    'title': a.full_name,







                    'email': a.email,







                    'phone': a.phone,







                    'college': a.college or '',







                    'course_stream': a.course_stream or '',







                    'skills': a.skills or '',







                    'message': a.message or '',







                    'notes': a.notes or '',







                    'internship_id': a.internship_id,







                    'internship_title': a.internship.title if a.internship else '',







                    'subtitle': f"Applied for: {a.internship.title if a.internship else 'General'} • {a.email} • {a.phone}",







                    'category': a.course_stream or (a.internship.title if a.internship else "Application"),







                    'date': a.created_at.strftime("%d %b %Y") if a.created_at else "N/A",







                    'created_at': a.created_at,







                    'status': a.status or "Pending",







                    'status_class': _get_status_class(a.status),







                    'resume_url': f"/api/admin/files/download/{a.resume}" if a.resume else "",







                    'type': 'Internship Application',







                    'model': 'internship_application'







                })







            all_apps = list(InternshipApplication.objects.all())







            total_count = len(all_apps)







            active_count = sum(1 for item in all_apps if item.status == 'Selected')







            pending_count = sum(1 for item in all_apps if item.status in ['Pending', 'Shortlisted'])







            archived_count = sum(1 for item in all_apps if item.status == 'Rejected')















        elif section_key == 'internships_enquiries':







            enquiries = list(InternshipEnquiry.objects.all().order_by('-id'))







            records = []







            for i in enquiries:







                records.append({







                    'id': f"INT-{i.id}",







                    'raw_id': i.id,







                    'name': i.full_name,







                    'full_name': i.full_name,







                    'title': i.full_name,







                    'email': i.email,







                    'phone': i.phone,







                    'college': i.college or '',







                    'course_stream': i.course_stream or '',







                    'duration': i.duration or '3 Months',







                    'skills': i.skills or '',







                    'message': i.message or '',







                    'notes': i.notes or '',







                    'subtitle': f"{i.email} • {i.phone} • {i.college or 'College N/A'}",







                    'category': i.course_stream or "Internship Enquiry",







                    'date': i.created_at.strftime("%d %b %Y") if i.created_at else "N/A",







                    'created_at': i.created_at,







                    'status': i.status or "New",







                    'status_class': _get_status_class(i.status),







                    'resume_url': f"/api/admin/files/download/{i.resume}" if i.resume else "",







                    'type': 'Internship Enquiry',







                    'model': 'internship_enquiry'







                })







            total_count = len(enquiries)







            active_count = sum(1 for item in enquiries if item.status in ['Selected', 'Converted', 'Active'])







            pending_count = sum(1 for item in enquiries if item.status in ['New', 'Pending', 'Shortlisted'])







            archived_count = sum(1 for item in enquiries if item.status in ['Rejected'])















        else: # internships_all, internships_active, internships_completed, internships_add







            if section_key == 'internships_add':







                records = []







            else:







                qs = Internship.objects.all().order_by('-id')







                if section_key == 'internships_active':







                    qs = qs.filter(status='Active')







                elif section_key == 'internships_completed':







                    qs = qs.filter(status='Completed')















                records = []







                for item in qs:







                    records.append({







                        'id': f"INT-{item.id}",







                        'raw_id': item.id,







                        'name': item.title,







                        'title': item.title,







                        'provider_name': item.provider.name if item.provider else 'Sky Vision Consultancy',







                        'provider_id': item.provider_id,







                        'location': item.location or '',







                        'mode': item.mode or 'Onsite',







                        'duration': item.duration or '3 Months',







                        'stipend': item.stipend or '',







                        'seats': item.seats,







                        'skills_required': item.skills_required or '',







                        'description': item.description or '',







                        'start_date': item.start_date.strftime("%Y-%m-%d") if item.start_date else '',







                        'end_date': item.end_date.strftime("%Y-%m-%d") if item.end_date else '',







                        'applications_count': item.applications.count() if hasattr(item, 'applications') else 0,







                        'selected_count': item.applications.filter(status='Selected').count() if hasattr(item, 'applications') else 0,







                        'subtitle': f"Provider: {item.provider.name if item.provider else 'Sky Vision'} • Mode: {item.mode} • Stipend: {item.stipend or 'Unpaid'} • Seats: {item.seats}",







                        'category': f"{item.mode} ({item.duration})",







                        'date': item.created_at.strftime("%d %b %Y") if item.created_at else "N/A",







                        'created_at': item.created_at,







                        'status': item.status or "Open",







                        'status_class': _get_status_class(item.status),







                        'resume_url': "",







                        'type': 'Internship',







                        'model': 'internship'







                    })















            all_internships = list(Internship.objects.all())







            total_count = len(all_internships)







            active_count = sum(1 for item in all_internships if item.status in ['Active', 'Open'])







            pending_count = sum(1 for item in all_internships if item.status == 'Open')







            archived_count = sum(1 for item in all_internships if item.status in ['Completed', 'Closed'])























    # 4. ENQUIRIES MODULE







    elif module_key == 'enquiries':







        contact_enquiries = list(ContactEnquiry.objects.all())







        company_enquiries = list(CompanyEnquiry.objects.all())







        intern_enquiries = list(InternshipEnquiry.objects.all())















        read_set = set(EnquiryRead.objects.values_list('enquiry_type', 'enquiry_id'))















        all_enq = []















        # 1. Contacts







        for e in contact_enquiries:







            is_read = ('contact', e.id) in read_set







            bkt = bucket_of('contact', e.status)







            enq_kind = 'General' if e.enquiry_type != 'Candidate' else 'Candidate'







            all_enq.append({







                'id': f"ENQ-{e.id}",







                'raw_id': e.id,







                'name': e.name,







                'title': e.name,







                'email': e.email,







                'phone': e.phone,







                'company_name': '',







                'subtitle': f"{e.email} • {e.phone}",







                'category': e.service or "General Enquiry",







                'service_or_job': e.service or "General Enquiry",







                'message': e.message or "",







                'notes': e.notes or "",







                'date': e.created_at.strftime("%d %b %Y") if e.created_at else "N/A",







                'created_at': e.created_at,







                'status': e.status or "New",







                'bucket': bkt,







                'is_read': is_read,







                'status_class': _get_status_class(e.status),







                'type': f"{enq_kind} Enquiry",







                'enquiry_type': enq_kind,







                'model': 'contact'







            })















        # 2. Company Enquiries







        for c in company_enquiries:







            is_read = ('company', c.id) in read_set







            bkt = bucket_of('company', c.status)







            all_enq.append({







                'id': f"CMP-{c.id}",







                'raw_id': c.id,







                'name': c.recruiter_name,







                'title': c.company_name,







                'email': c.email,







                'phone': c.phone,







                'company_name': c.company_name,







                'recruiter_name': c.recruiter_name,







                'designation': c.designation or '',







                'address': c.address or '',







                'job_title': c.job_title or '',







                'department': c.department or '',







                'job_type': getattr(c, 'job_type', 'Full Time') or 'Full Time',







                'application_deadline': getattr(c, 'application_deadline', '30 Days') or '30 Days',







                'vacancies': c.vacancies or '1',







                'experience_req': c.experience_req or '',







                'salary_range': c.salary_range or '',







                'requirements': getattr(c, 'requirements', '') or '',







                'subtitle': f"{c.recruiter_name} ({c.company_name}) • {c.email}",







                'category': c.job_title or "Company Enquiry",







                'service_or_job': c.job_title or "Company Requirement",







                'message': c.message or "",







                'notes': c.notes or "",







                'date': c.created_at.strftime("%d %b %Y") if c.created_at else "N/A",







                'created_at': c.created_at,







                'status': c.status or "New",







                'bucket': bkt,







                'is_read': is_read,







                'status_class': _get_status_class(c.status),







                'type': 'Company Enquiry',







                'enquiry_type': 'Company',







                'model': 'company'







            })















        # 3. Internship Enquiries







        for i in intern_enquiries:







            is_read = ('internship', i.id) in read_set







            bkt = bucket_of('internship', i.status)







            all_enq.append({







                'id': f"INT-{i.id}",







                'raw_id': i.id,







                'name': i.full_name,







                'title': i.full_name,







                'email': i.email,







                'phone': i.phone,







                'college': i.college or '',







                'company_name': i.college or '',







                'course_stream': i.course_stream or '',







                'duration': i.duration or '3 Months',







                'skills': i.skills or '',







                'subtitle': f"{i.email} • {i.phone} • {i.college or 'College N/A'}",







                'category': f"Internship ({i.course_stream})" if i.course_stream else "Internship Enquiry",







                'service_or_job': f"Internship ({i.course_stream})" if i.course_stream else "Internship",







                'message': i.message or "",







                'notes': i.notes or "",







                'date': i.created_at.strftime("%d %b %Y") if i.created_at else "N/A",







                'created_at': i.created_at,







                'status': i.status or "New",







                'bucket': bkt,







                'is_read': is_read,







                'status_class': _get_status_class(i.status),







                'type': 'Internship Enquiry',







                'enquiry_type': 'Internship',







                'model': 'internship'







            })















        # Global unread count across system







        unread_count = sum(1 for item in all_enq if not item['is_read'])















        # Filter by section







        if section_key == 'enquiries_general':







            records = [e for e in all_enq if e['model'] == 'contact' and e['enquiry_type'] == 'General']







        elif section_key == 'enquiries_candidate':







            records = [e for e in all_enq if e['model'] == 'contact' and e['enquiry_type'] == 'Candidate']







        elif section_key == 'enquiries_company':







            records = [e for e in all_enq if e['model'] == 'company']







        elif section_key == 'enquiries_internship':







            records = [e for e in all_enq if e['model'] == 'internship']







        elif section_key == 'enquiries_unread':







            records = [e for e in all_enq if not e['is_read']]







        elif section_key == 'enquiries_resolved':







            records = [e for e in all_enq if e['bucket'] == 'resolved']







        else:  # enquiries_all







            records = all_enq















        # Additional request GET filters (q, bucket, is_read)







        q_param = request.GET.get('q', '').strip().lower()







        bucket_param = request.GET.get('bucket', '').strip().lower()







        read_param = request.GET.get('is_read', '').strip().lower()















        filtered = []







        for r in records:







            if q_param:







                match = (







                    q_param in r['name'].lower() or







                    q_param in r['email'].lower() or







                    q_param in r['phone'].lower() or







                    q_param in r['company_name'].lower() or







                    q_param in r['service_or_job'].lower() or







                    q_param in r['message'].lower()







                )







                if not match: continue







            if bucket_param and r['bucket'] != bucket_param:







                continue







            if read_param in ['1', 'true'] and not r['is_read']:







                continue







            if read_param in ['0', 'false'] and r['is_read']:







                continue







            filtered.append(r)















        filtered.sort(key=lambda x: x['created_at'] or timezone.now(), reverse=True)















        total_count = len(filtered)







        active_count = sum(1 for c in filtered if c['bucket'] == 'resolved')







        pending_count = sum(1 for c in filtered if c['bucket'] in ['open', 'in_progress'])







        archived_count = sum(1 for c in filtered if c['bucket'] == 'closed')















        records = filtered















    # 5. PLACEMENTS MODULE







    elif module_key == 'placements':







        # Auto-sync any candidate whose status is 'Joined' or 'Placed' to ensure complete Placement record







        joined_applicants = Applicant.objects.filter(status__in=['Joined', 'Placed'])







        for ja in joined_applicants:







            if not Placement.objects.filter(applicant=ja).exists():







                comp_name = (ja.job.company_name if ja.job and getattr(ja.job, 'company_name', None) else '') or (ja.job.employer.company_name if ja.job and getattr(ja.job, 'employer', None) else '') or ja.current_company or "Sky Vision Partner"







                pkg = ja.expected_salary or ja.current_salary or "As per norms"







                join_d = timezone.now().strftime("%Y-%m-%d")







                Placement.objects.create(







                    applicant=ja,







                    candidate_name=ja.full_name,







                    company_name=comp_name,







                    position=ja.job_title,







                    package=pkg,







                    placement_date=join_d,







                    joining_date=join_d,







                    status='Joined',







                    notes='Auto-synced from candidate joined status'







                )















        placements_qs = Placement.objects.select_related('applicant').all().order_by('-id')







        if section_key == 'placements_joined':







            placements_qs = placements_qs.filter(status__in=['Joined', 'Placed'])







        elif section_key == 'placements_pending_joining':







            placements_qs = placements_qs.filter(status__in=['Pending', 'Pending Joining'])







        elif section_key == 'placements_active':







            placements_qs = placements_qs.filter(status__in=['Joined', 'Placed', 'Active'])







        elif section_key == 'placements_completed':







            placements_qs = placements_qs.filter(status__in=['Completed', 'Placed'])















        all_p = []







        for p in placements_qs:







            app = p.applicant







            all_p.append({







                'id': f"PLC-{p.id}",







                'raw_id': p.id,







                'placement_id': p.id,







                'applicant_id': p.applicant_id,







                'name': p.candidate_name,







                'title': p.candidate_name,







                'full_name': p.candidate_name,







                'email': app.email if app else "",







                'phone': app.phone if app else "",







                'city': app.city if app else "",







                'state': app.state if app else "",







                'qualification': app.qualification if app else "",







                'experience': app.experience if app else 0,







                'skills': app.skills if app else "",







                'company_name': p.company_name,







                'position': p.position,







                'category': p.position,







                'package': p.package or "N/A",







                'placement_date': p.placement_date or (p.created_at.strftime("%d %b %Y") if p.created_at else "N/A"),







                'joining_date': p.joining_date or (p.created_at.strftime("%d %b %Y") if p.created_at else "N/A"),







                'date': p.joining_date or p.placement_date or (p.created_at.strftime("%d %b %Y") if p.created_at else "N/A"),







                'created_at': p.created_at,







                'subtitle': f"{p.company_name} • Package: {p.package or 'N/A'} • Joined: {p.joining_date or 'Yes'}",







                'status': p.status or "Joined",







                'status_class': 'active' if str(p.status or '').lower() in ['joined', 'placed', 'completed'] else 'shortlisted',







                'notes': p.notes or "",







                'resume_url': f"/api/admin/files/download/{app.resume}" if (app and app.resume) else "",







                'type': 'Placement',







                'model': 'placement'







            })















        total_count = len(all_p)







        active_count = sum(1 for c in all_p if c['status'].lower() in ['placed', 'joined', 'completed', 'active'])







        pending_count = sum(1 for c in all_p if c['status'].lower() in ['pending', 'pending joining'])







        archived_count = sum(1 for c in all_p if c['status'].lower() in ['cancelled', 'rejected'])







        records = all_p















    # 5B. JOB OFFERS MODULE







    elif module_key == 'offers':







        offers_qs = JobOffer.objects.select_related('applicant').all().order_by('-id')







        if section_key == 'offers_pending':







            offers_qs = offers_qs.filter(status__in=['Offer Sent', 'Pending'])







        elif section_key == 'offers_accepted':







            offers_qs = offers_qs.filter(status__in=['Accepted', 'Joined'])







        elif section_key == 'offers_rejected':







            offers_qs = offers_qs.filter(status__iexact='Rejected')







        elif section_key == 'offers_expired':







            offers_qs = offers_qs.filter(status__iexact='Expired')















        all_o = []







        for o in offers_qs:







            app = o.applicant







            all_o.append({







                'id': f"OFF-{o.id}",







                'raw_id': o.id,







                'offer_id': o.id,







                'applicant_id': o.applicant_id,







                'name': o.candidate_name,







                'title': o.candidate_name,







                'full_name': o.candidate_name,







                'email': app.email if app else "",







                'phone': app.phone if app else "",







                'city': app.city if app else "",







                'qualification': app.qualification if app else "",







                'experience': app.experience if app else 0,







                'company_name': o.company_name,







                'designation': o.designation,







                'category': o.designation,







                'offered_ctc': o.offered_ctc or "N/A",







                'offer_date': o.offer_date or (o.created_at.strftime("%d %b %Y") if o.created_at else "N/A"),







                'joining_date': o.joining_date or "TBD",







                'date': o.offer_date or (o.created_at.strftime("%d %b %Y") if o.created_at else "N/A"),







                'created_at': o.created_at,







                'subtitle': f"{o.company_name} • CTC: {o.offered_ctc or 'N/A'} • Expected Joining: {o.joining_date or 'TBD'}",







                'status': o.status or "Offer Sent",







                'status_class': _get_status_class(o.status),







                'notes': o.notes or "",







                'resume_url': f"/api/admin/files/download/{app.resume}" if (app and app.resume) else "",







                'document': o.document or "",







                'document_url': f"/api/admin/files/download/{o.document}" if o.document else "",







                'type': 'Job Offer',







                'model': 'job_offer'







            })















        total_count = len(all_o)







        active_count = sum(1 for c in all_o if c['status'].lower() in ['accepted', 'joined'])







        pending_count = sum(1 for c in all_o if c['status'].lower() in ['offer sent', 'pending'])







        archived_count = sum(1 for c in all_o if c['status'].lower() in ['rejected', 'expired'])







        records = all_o















    # 6. DOCUMENTS MODULE







    elif module_key == 'documents':







        applicants = list(Applicant.objects.exclude(resume="").exclude(resume__isnull=True))







        resumes = list(Resume.objects.exclude(resume="").exclude(resume__isnull=True))







        all_docs = []







        for a in applicants:







            all_docs.append({







                'id': f"DOC-{a.id}",







                'raw_id': a.id,







                'name': a.full_name,







                'title': a.full_name,







                'subtitle': f"{a.resume} • {a.email}",







                'category': f"Resume ({a.job_title})",







                'date': a.applied_on.strftime("%d %b %Y") if a.applied_on else "N/A",







                'created_at': a.applied_on,







                'status': "Verified",







                'status_class': 'active',







                'resume_url': f"/api/admin/files/download/{a.resume}",







                'type': 'Document'







            })







        for r in resumes:







            all_docs.append({







                'id': f"DOC-{r.id}",







                'raw_id': r.id,







                'name': r.full_name,







                'title': r.full_name,







                'subtitle': f"{r.resume} • {r.email}",







                'category': f"Resume ({r.applying_for or 'Quick Resume'})",







                'date': r.uploaded_on.strftime("%d %b %Y") if r.uploaded_on else "N/A",







                'created_at': r.uploaded_on,







                'status': "Verified",







                'status_class': 'active',







                'resume_url': f"/api/admin/files/download/{r.resume}",







                'type': 'Document'







            })







        total_count = len(all_docs)







        active_count = total_count







        pending_count = 0







        archived_count = 0







        records = all_docs















    # FALLBACK / OTHER MODULES







    else:







        total_count = 0







        active_count = 0







        pending_count = 0







        archived_count = 0







        records = []















    records.sort(key=lambda x: x.get('created_at') or timezone.now(), reverse=True)















    providers_list = [p.to_dict() for p in InternshipProvider.objects.filter(is_active=True)] if module_key == 'internships' else []















    selected_candidates_list = []







    if module_key in ['offers', 'placements', 'candidates']:







        for a in Applicant.objects.filter(models.Q(status__iexact='Selected') | models.Q(status__iexact='Offer Released') | models.Q(status__iexact='Interview') | models.Q(status__iexact='Interview Scheduled')).order_by('-id'):







            c_name = (a.job.company_name if a.job and getattr(a.job, 'company_name', None) else '') or (a.job.employer.company_name if a.job and getattr(a.job, 'employer', None) else '') or a.current_company or "Sky Vision Partner"







            selected_candidates_list.append({







                'id': a.id,







                'name': a.full_name,







                'email': a.email,







                'phone': a.phone,







                'job_title': a.job_title,







                'company': c_name,







                'status': a.status







            })















    context = {







        'admin_user': admin_user,







        'active_menu': active_menu,







        'section_key': section_key,







        'registration_type': locals().get('reg_type', 'candidate'),







        'module_key': module_key,







        'module_title': sec_info['module_title'],







        'section_name': sec_info['section_name'],







        'icon': sec_info['icon'],







        'records': records,







        'all_employers': list(EmployerAccount.objects.filter(status='APPROVED').order_by('company_name')),







        'providers_list': providers_list,







        'selected_candidates_list': selected_candidates_list,







        'total_count': total_count,







        'active_count': active_count,







        'pending_count': pending_count,







        'archived_count': archived_count,







        'total_apps_count': InternshipApplication.objects.count(),







        'total_internship_apps': InternshipApplication.objects.count(),







        'total_internships_open': Internship.objects.count(),







        'total_internship_providers': InternshipProvider.objects.count(),







        'total_internship_enquiries': InternshipEnquiry.objects.count(),







        'unread_count': locals().get('unread_count', 0),







        'page_title': f"{sec_info['section_name']} — PlacementPro Admin Panel",







    }







    return render(request, 'dashboard/module_page.html', context)























@admin_required







def dashboard_stats_api(request):







    now = timezone.now()















    total_candidates = Applicant.objects.exclude(job_title__icontains="intern").count() + Resume.objects.count()







    total_companies = CompanyEnquiry.objects.count()







    total_internships = InternshipApplication.objects.count() + InternshipEnquiry.objects.count()







    total_general = ContactEnquiry.objects.count()







    total_placements = Placement.objects.count()















    current_tz = timezone.get_current_timezone()







    today = timezone.localdate()







    dates = [(today - datetime.timedelta(days=29 - i)).strftime("%Y-%m-%d") for i in range(30)]















    chart_series = {







        "dates": [d[-5:] for d in dates],







        "candidates": [0] * 30,







        "companies": [0] * 30,







        "internships": [0] * 30,







        "general": [0] * 30







    }















    for i, date_str in enumerate(dates):







        naive_start = datetime.datetime.strptime(date_str, "%Y-%m-%d")







        d_start = timezone.make_aware(naive_start, current_tz)







        d_end = d_start + datetime.timedelta(days=1)















        c_count = Applicant.objects.exclude(job_title__icontains="intern").filter(applied_on__gte=d_start, applied_on__lt=d_end).count()







        r_count = Resume.objects.filter(uploaded_on__gte=d_start, uploaded_on__lt=d_end).count()







        chart_series["candidates"][i] = c_count + r_count















        chart_series["companies"][i] = CompanyEnquiry.objects.filter(created_at__gte=d_start, created_at__lt=d_end).count()







        chart_series["internships"][i] = InternshipApplication.objects.filter(created_at__gte=d_start, created_at__lt=d_end).count() + InternshipEnquiry.objects.filter(created_at__gte=d_start, created_at__lt=d_end).count()







        chart_series["general"][i] = ContactEnquiry.objects.filter(created_at__gte=d_start, created_at__lt=d_end).count()















    recent_activities = [a.to_dict() for a in ActivityLog.objects.all().order_by('-id')[:8]]















    latest_candidates = [a.to_dict() for a in Applicant.objects.exclude(job_title__icontains="intern").order_by('-id')[:5]]







    latest_companies = [c.to_dict() for c in CompanyEnquiry.objects.all().order_by('-id')[:5]]







    latest_internships = [i.to_dict() for i in InternshipApplication.objects.all().order_by('-id')[:5]]







    latest_general = [g.to_dict() for g in ContactEnquiry.objects.all().order_by('-id')[:5]]







    latest_placements = [p.to_dict() for p in Placement.objects.all().order_by('-id')[:5]]















    return JsonResponse({







        "status": "success",







        "metrics": {







            "total_job_seekers": total_candidates,







            "company_enquiries": total_companies,







            "internship_enquiries": total_internships,







            "general_enquiries": total_general,







            "total_placements": total_placements,







            "pending_employers": EmployerAccount.objects.filter(status='PENDING').count(),







            "pending_jobs": Job.objects.exclude(employer__isnull=True).filter(status='PENDING_APPROVAL').count(),







            "active_employers": EmployerAccount.objects.filter(status='APPROVED').count(),







        },







        "chart": chart_series,







        "recent_activities": recent_activities,







        "latest": {







            "candidates": latest_candidates,







            "companies": latest_companies,







            "internships": latest_internships,







            "general": latest_general,







            "placements": latest_placements







        }







    })















@admin_required







def admin_documents_api(request):







    docs = []







    resumes_dir = os.path.join(settings.MEDIA_ROOT, "uploads", "resumes")















    for a in Applicant.objects.exclude(job_title__icontains="intern").exclude(resume="").exclude(resume__isnull=True):







        fpath = os.path.join(resumes_dir, a.resume)







        size_kb = round(os.path.getsize(fpath) / 1024, 1) if os.path.exists(fpath) else 0







        docs.append({







            "id": a.id,







            "type": "Job Seeker",







            "candidate_name": a.full_name,







            "filename": a.resume,







            "file_size": f"{size_kb} KB",







            "role": a.job_title,







            "uploaded_on": str(a.applied_on) if a.applied_on else ""







        })















    for r in Resume.objects.exclude(resume="").exclude(resume__isnull=True):







        fpath = os.path.join(resumes_dir, r.resume)







        size_kb = round(os.path.getsize(fpath) / 1024, 1) if os.path.exists(fpath) else 0







        docs.append({







            "id": r.id,







            "type": "Quick Resume",







            "candidate_name": r.full_name,







            "filename": r.resume,







            "file_size": f"{size_kb} KB",







            "role": r.applying_for or "General",







            "uploaded_on": str(r.uploaded_on) if r.uploaded_on else ""







        })















    return JsonResponse(docs, safe=False)















def admin_file_download(request, name):







    admin_id = request.session.get('admin_id')







    employer_id = request.session.get('employer_id')







    candidate_id = request.session.get('candidate_id')







    user_auth = hasattr(request, 'user') and request.user.is_authenticated















    if not (admin_id or employer_id or candidate_id or user_auth):







        raise Http404("Unauthorized file access.")















    safe_name = os.path.basename(name)















    # Employer authorization check (IDOR protection)







    if employer_id and not admin_id and not user_auth:







        try:







            emp = EmployerAccount.objects.get(id=employer_id)







            visible_apps = Applicant.objects.visible_to_employer(emp)







            is_visible_resume = visible_apps.filter(models.Q(resume=safe_name) | models.Q(resume__icontains=safe_name)).exists()
            if not is_visible_resume:
                direct_apps = Applicant.objects.filter(
                    models.Q(job__employer=emp) | models.Q(employer=emp) |
                    (models.Q(job__company=emp.company) if getattr(emp, 'company', None) else models.Q(pk__in=[]))
                )
                is_visible_resume = direct_apps.filter(models.Q(resume=safe_name) | models.Q(resume__icontains=safe_name)).exists()







            is_visible_offer = JobOffer.objects.filter(document=safe_name, applicant__in=visible_apps).exists()







            is_own_doc = (emp.document == safe_name)







            if not (is_visible_resume or is_visible_offer or is_own_doc):







                raise Http404("File not found or access denied.")







        except EmployerAccount.DoesNotExist:







            raise Http404("Employer account not found.")















    # Candidate authorization check







    if candidate_id and not admin_id and not employer_id and not user_auth:







        try:







            cand = CandidateAccount.objects.get(id=candidate_id)







            is_own_resume = (cand.resume == safe_name) or Applicant.objects.filter(candidate_account=cand, resume=safe_name).exists()







            is_own_offer = JobOffer.objects.filter(applicant__candidate_account=cand, document=safe_name).exists()







            if not (is_own_resume or is_own_offer):







                raise Http404("File not found or access denied.")







        except CandidateAccount.DoesNotExist:







            raise Http404("Candidate account not found.")















    search_dirs = [







        os.path.join(settings.MEDIA_ROOT, "uploads", "offer_letters"),







        os.path.join(settings.MEDIA_ROOT, "uploads", "resumes"),







        os.path.join(settings.MEDIA_ROOT, "uploads", "company_documents"),







        os.path.join(settings.MEDIA_ROOT, "uploads"),







        settings.MEDIA_ROOT,







    ]







    file_path = None







    for directory in search_dirs:







        cand_path = os.path.join(directory, safe_name)







        if os.path.exists(cand_path) and os.path.isfile(cand_path):







            file_path = cand_path







            break















    if not file_path:
        # Check database persistent storage
        try:
            from apps.candidates.models import UploadedFile
            db_file = UploadedFile.objects.filter(name=safe_name).first()
            if db_file and db_file.file_data:
                cache_dir = os.path.join(settings.MEDIA_ROOT, "uploads", "resumes")
                os.makedirs(cache_dir, exist_ok=True)
                cache_path = os.path.join(cache_dir, safe_name)
                try:
                    with open(cache_path, 'wb') as cf:
                        cf.write(bytes(db_file.file_data))
                    file_path = cache_path
                except Exception:
                    pass
                if not file_path:
                    import mimetypes
                    content_type = db_file.content_type or mimetypes.guess_type(safe_name)[0] or 'application/pdf'
                    from django.http import HttpResponse
                    resp = HttpResponse(bytes(db_file.file_data), content_type=content_type)
                    disp = 'attachment' if request.GET.get('download') == '1' else 'inline'
                    resp['Content-Disposition'] = f'{disp}; filename="{safe_name}"'
                    return resp
        except Exception:
            pass

    if not file_path:
        from django.http import HttpResponse
        error_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Resume File Not Available - Sky Vision</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8fafc; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
        .card {{ background: white; padding: 40px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.08); max-width: 520px; text-align: center; border: 1px solid #e2e8f0; }}
        .icon {{ font-size: 52px; margin-bottom: 16px; }}
        h2 {{ color: #1e293b; margin: 0 0 12px 0; font-size: 22px; }}
        p {{ color: #64748b; line-height: 1.6; font-size: 14px; margin-bottom: 24px; }}
        .badge {{ background: #fef2f2; color: #ef4444; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; display: inline-block; margin-bottom: 16px; border: 1px solid #fecaca; }}
        .btn {{ background: #2563eb; color: white; padding: 10px 24px; border-radius: 50px; text-decoration: none; font-size: 14px; font-weight: 600; display: inline-block; border: none; cursor: pointer; }}
        .btn:hover {{ background: #1d4ed8; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">📄⚠️</div>
        <div class="badge">{safe_name}</div>
        <h2>Resume File Not Found on Server</h2>
        <p>Yeh resume file server restart hone ki wajah se server temporary disk se remove ho chuki hai.<br><br>
        Naye system me ab database persistent storage enable ho chuka hai, isliye ab se upload hone wali saari files permanently save rahengi.<br><br>
        <strong>Solution:</strong> Candidate se resume dubara upload karne ya email par bhejne ke liye kahein.</p>
        <button class="btn" onclick="window.close()">Close Window</button>
    </div>
</body>
</html>"""
        return HttpResponse(error_html, status=404, content_type='text/html; charset=utf-8')















    download = request.GET.get('download') == '1'
    import mimetypes
    content_type, _ = mimetypes.guess_type(safe_name)
    if not content_type:
        if safe_name.lower().endswith('.pdf'):
            content_type = 'application/pdf'
        elif safe_name.lower().endswith(('.jpg', '.jpeg')):
            content_type = 'image/jpeg'
        elif safe_name.lower().endswith('.png'):
            content_type = 'image/png'
        else:
            content_type = 'application/octet-stream'

    response = FileResponse(open(file_path, 'rb'), as_attachment=download, filename=safe_name, content_type=content_type)
    if not download and content_type == 'application/pdf':
        response['Content-Disposition'] = f'inline; filename="{safe_name}"'
    return response























# ==========================================







# SUPER ADMIN APPLICATION APPROVAL & OVERRIDE APIS







# ==========================================















@admin_required







def admin_approve_application_api(request, applicant_id):







    """Super Admin approves a candidate's job application."""







    if request.method != "POST":







        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)







    try:







        try:







            data = json.loads(request.body) if request.body else request.POST







        except Exception:







            data = request.POST















        applicant = Applicant.objects.select_related('job', 'job__employer', 'job__company').get(id=applicant_id)







        admin_user = AdminUser.objects.filter(id=request.session.get('admin_id')).first()







        admin_username = getattr(admin_user, 'email', 'Super Admin') if admin_user else "Super Admin"















        # Owner employer MUST be resolved from applicant.job.employer







        owner_employer = applicant.job.employer if (applicant.job and applicant.job.employer) else None







        if not owner_employer:







            return JsonResponse({"status": "error", "message": "Job has no owner employer; fix the job first"}, status=400)















        # Ignore/deny any employer_id from request that differs from job.employer_id







        req_employer_id = data.get("employer_id") or request.GET.get("employer_id")







        if req_employer_id:







            try:







                if int(req_employer_id) != owner_employer.id:







                    return JsonResponse({"status": "error", "message": "Cannot route approval to a different employer than the job owner"}, status=400)







            except (ValueError, TypeError):







                pass















        # Always set applicant.employer = applicant.job.employer and applicant.company = applicant.job.company







        applicant.employer = owner_employer







        applicant.company = applicant.job.company or owner_employer.company















        # Approval must be idempotent, set approved_at/approved_by







        applicant.approval_status = "Approved"







        if not applicant.approved_at:







            applicant.approved_at = timezone.now()







        applicant.approved_by = admin_username







        applicant.save(update_fields=['approval_status', 'approved_at', 'approved_by', 'employer', 'company'])















        emp_label = owner_employer.company_name















        if applicant.status in ['Application Submitted', 'New', 'Pending']:







            set_applicant_status(







                applicant,







                "Shortlisted",







                changed_by=f"admin ({admin_username})",







                notes=f"Approved and Shortlisted by Admin '{admin_username}'. Forwarded to {emp_label}."







            )















        log_activity(







            action_type="Approved Job Application",







            title=f"Application #{applicant.id} approved & forwarded to {emp_label}.",







            description=f"Admin '{admin_username}' approved application for {applicant.full_name} ({applicant.job_title}). Status set to 'Shortlisted' and visible to {emp_label}."







        )















        return JsonResponse({







            "status": "success",







            "message": f"Application for {applicant.full_name} approved successfully! Status set to 'Shortlisted' and forwarded to {emp_label}.",







            "applicant": applicant.to_dict()







        })







    except Applicant.DoesNotExist:







        return JsonResponse({"status": "error", "message": "Applicant not found."}, status=404)







    except Exception as e:







        return JsonResponse({"status": "error", "message": str(e)}, status=500)























@admin_required







def admin_assign_applicant_employer_api(request, applicant_id):







    """Admin assigns or reassigns any applicant to a specific employer."""







    if request.method != "POST":







        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)







    try:







        try:







            data = json.loads(request.body) if request.body else request.POST







        except Exception:







            data = request.POST















        applicant = Applicant.objects.select_related('job', 'job__employer', 'job__company').get(id=applicant_id)







        owner_employer = applicant.job.employer if (applicant.job and applicant.job.employer) else None







        if not owner_employer:







            return JsonResponse({"status": "error", "message": "Job has no owner employer; fix the job first"}, status=400)















        employer_id = data.get("employer_id")







        if employer_id:







            try:







                if int(employer_id) != owner_employer.id:







                    return JsonResponse({"status": "error", "message": "Cannot route approval to a different employer than the job owner"}, status=400)







            except (ValueError, TypeError):







                pass















        admin_user = AdminUser.objects.filter(id=request.session.get('admin_id')).first()







        admin_username = getattr(admin_user, 'email', 'Super Admin') if admin_user else "Super Admin"















        applicant.employer = owner_employer







        applicant.company = applicant.job.company or owner_employer.company







        applicant.approval_status = "Approved"







        if not applicant.approved_at:







            applicant.approved_at = timezone.now()







        applicant.approved_by = admin_username















        if applicant.status in ['Application Submitted', 'New', 'Pending']:







            set_applicant_status(







                applicant,







                "Shortlisted",







                changed_by=f"admin ({admin_username})",







                notes=f"Assigned and forwarded to {owner_employer.company_name} by Admin '{admin_username}'."







            )







        applicant.save(update_fields=['employer', 'company', 'approval_status', 'approved_at', 'approved_by'])















        log_activity(







            action_type="Assigned Candidate to Employer",







            title=f"Application #{applicant.id} assigned to {owner_employer.company_name}.",







            description=f"Admin '{admin_username}' assigned candidate {applicant.full_name} to employer {owner_employer.company_name}."







        )















        return JsonResponse({







            "status": "success",







            "message": f"Candidate {applicant.full_name} successfully forwarded to {owner_employer.company_name}!",







            "applicant": applicant.to_dict()







        })







    except Applicant.DoesNotExist:







        return JsonResponse({"status": "error", "message": "Applicant not found."}, status=404)







    except Exception as e:







        return JsonResponse({"status": "error", "message": str(e)}, status=500)























@admin_required







def admin_reject_application_api(request, applicant_id):







    """Super Admin rejects a job application with a reason."""







    if request.method != "POST":







        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)







    try:







        data = json.loads(request.body) if request.body else request.POST







        reason = (data.get("rejection_reason") or data.get("reason") or "").strip()







        if not reason:







            return JsonResponse({"status": "error", "message": "Rejection reason is required."}, status=400)







        







        applicant = Applicant.objects.get(id=applicant_id)







        admin_user = AdminUser.objects.filter(id=request.session.get('admin_id')).first()







        admin_username = getattr(admin_user, 'email', 'Super Admin') if admin_user else "Super Admin"







        







        applicant.approval_status = "Rejected"







        applicant.rejection_reason = reason







        applicant.save(update_fields=['approval_status', 'rejection_reason'])







        







        set_applicant_status(







            applicant,







            "Rejected",







            changed_by=f"admin ({admin_username})",







            notes=f"Rejected by Admin '{admin_username}': {reason}"







        )







        







        log_activity(







            action_type="Rejected Job Application",







            title=f"Application #{applicant.id} rejected.",







            description=f"Admin '{admin_username}' rejected application for {applicant.full_name}: {reason}"







        )







        







        return JsonResponse({







            "status": "success",







            "message": f"Application for {applicant.full_name} rejected.",







            "applicant": applicant.to_dict()







        })







    except Applicant.DoesNotExist:







        return JsonResponse({"status": "error", "message": "Applicant not found."}, status=404)







    except Exception as e:







        return JsonResponse({"status": "error", "message": str(e)}, status=500)























@admin_required







def admin_bulk_approve_applications_api(request):







    """Super Admin bulk approves selected candidate job applications."""







    if request.method != "POST":







        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)







    try:







        data = json.loads(request.body) if request.body else request.POST







        raw_ids = data.get("applicant_ids") or data.get("ids") or []







        req_employer_id = data.get("employer_id")















        if isinstance(raw_ids, str):







            applicant_ids = [int(x.strip()) for x in raw_ids.split(",") if x.strip().isdigit()]







        elif isinstance(raw_ids, list):







            applicant_ids = [int(x) for x in raw_ids if str(x).isdigit()]







        else:







            applicant_ids = []















        admin_user = AdminUser.objects.filter(id=request.session.get('admin_id')).first()







        admin_username = getattr(admin_user, 'email', 'Super Admin') if admin_user else "Super Admin"















        approved_count = 0







        error_messages = []















        for app_id in applicant_ids:







            try:







                applicant = Applicant.objects.select_related('job', 'job__employer', 'job__company').get(id=app_id)







                owner_emp = applicant.job.employer if (applicant.job and applicant.job.employer) else None







                if not owner_emp:







                    error_messages.append(f"Application #{app_id}: Job has no owner employer.")







                    continue















                if req_employer_id:







                    try:







                        if int(req_employer_id) != owner_emp.id:







                            error_messages.append(f"Application #{app_id}: Cannot route to a different employer.")







                            continue







                    except (ValueError, TypeError):







                        pass















                applicant.employer = owner_emp







                applicant.company = applicant.job.company or owner_emp.company







                applicant.approval_status = "Approved"







                if not applicant.approved_at:







                    applicant.approved_at = timezone.now()







                applicant.approved_by = admin_username







                applicant.save(update_fields=['approval_status', 'approved_at', 'approved_by', 'employer', 'company'])















                if applicant.status in ['Application Submitted', 'New', 'Pending']:







                    set_applicant_status(







                        applicant,







                        "Shortlisted",







                        changed_by=f"admin ({admin_username})",







                        notes=f"Bulk approved and shortlisted by Admin '{admin_username}'. Forwarded to {owner_emp.company_name}."







                    )







                approved_count += 1







            except Applicant.DoesNotExist:







                continue















        if approved_count == 0 and error_messages:







            return JsonResponse({"status": "error", "message": error_messages[0]}, status=400)















        return JsonResponse({







            "status": "success",







            "message": f"Successfully approved {approved_count} applications and forwarded to employer.",







            "count": approved_count







        })







    except Exception as e:







        return JsonResponse({"status": "error", "message": str(e)}, status=500)























@admin_required







def admin_override_application_step_api(request, applicant_id):







    """Super Admin manually overrides applicant status to any step (1..7)."""







    if request.method != "POST":







        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)







    try:







        data = json.loads(request.body) if request.body else request.POST







        new_status = (data.get("status") or "").strip()







        notes = (data.get("notes") or "").strip()















        if not new_status:







            return JsonResponse({"status": "error", "message": "New status is required."}, status=400)







        







        applicant = Applicant.objects.get(id=applicant_id)







        admin_user = AdminUser.objects.filter(id=request.session.get('admin_id')).first()







        admin_username = getattr(admin_user, 'email', 'Super Admin') if admin_user else "Super Admin"







        







        set_applicant_status(







            applicant,







            new_status,







            changed_by=f"admin ({admin_username})",







            notes=notes or f"Step manually overridden by Admin '{admin_username}'",







            force_override=True







        )







        







        return JsonResponse({







            "status": "success",







            "message": f"Application status overridden to '{new_status}'.",







            "applicant": applicant.to_dict()







        })







    except Applicant.DoesNotExist:







        return JsonResponse({"status": "error", "message": "Applicant not found."}, status=404)







    except Exception as e:







        return JsonResponse({"status": "error", "message": str(e)}, status=500)























# ==========================================







# REGISTRATION & APPROVAL MODULE VIEWS & APIS







# ==========================================















@admin_required







def admin_registrations_view(request, sub_type='all'):







    """Renders the Registration & Approval module page."""







    sec_key = f"registrations_{sub_type}"







    sec_info = MODULE_SECTIONS.get(sec_key, MODULE_SECTIONS['registrations_all'])







    







    context = {







        'module_key': 'registrations',







        'module_title': 'Registration & Approval',







        'section_name': sec_info['section_name'],







        'icon': sec_info['icon'],







        'sub_type': sub_type,







        'active_menu': 'registrations',







    }







    return render(request, 'dashboard/registrations_module.html', context)























@admin_required







def api_admin_registrations(request):







    """







    Unified JSON endpoint for candidate and employer registrations.







    Filters: type (all, candidate, employer), status (all, pending, approved, rejected, suspended), q, from, to.







    """







    reg_type = request.GET.get('type', 'all').lower()







    status_filter = request.GET.get('status', 'all').lower()







    query = request.GET.get('q', '').strip()







    from_date = request.GET.get('from', '').strip()







    to_date = request.GET.get('to', '').strip()















    try:







        page = max(1, int(request.GET.get('page', 1)))







        per_page = int(request.GET.get('per_page', 10))







        if per_page not in [10, 25, 50, 100]:







            per_page = 10







    except ValueError:







        page = 1







        per_page = 10















    candidates = []







    employers = []















    # 1. Fetch candidates if reg_type in ['all', 'candidate', 'candidates']







    if reg_type in ['all', 'candidate', 'candidates']:







        c_qs = CandidateAccount.objects.all()







        if status_filter != 'all':







            if status_filter in ['rejected', 'suspended']:







                c_qs = c_qs.filter(approval_status='rejected')







            else:







                c_qs = c_qs.filter(approval_status=status_filter)







        if query:







            c_qs = c_qs.filter(







                models.Q(full_name__icontains=query) |







                models.Q(email__icontains=query) |







                models.Q(phone__icontains=query) |







                models.Q(city__icontains=query)







            )







        if from_date:







            try:







                c_qs = c_qs.filter(created_at__gte=from_date)







            except Exception:







                pass







        if to_date:







            try:







                c_qs = c_qs.filter(created_at__lte=to_date + " 23:59:59")







            except Exception:







                pass







        candidates = list(c_qs)















    # 2. Fetch employers if reg_type in ['all', 'employer', 'employers']







    if reg_type in ['all', 'employer', 'employers']:







        e_qs = EmployerAccount.objects.all()







        if status_filter != 'all':







            if status_filter == 'pending':







                e_qs = e_qs.filter(status='PENDING')







            elif status_filter == 'approved':







                e_qs = e_qs.filter(status='APPROVED')







            elif status_filter == 'rejected':







                e_qs = e_qs.filter(status='REJECTED')







            elif status_filter == 'suspended':







                e_qs = e_qs.filter(status='SUSPENDED')







            elif status_filter in ['rejected_suspended', 'rejected/suspended']:







                e_qs = e_qs.filter(status__in=['REJECTED', 'SUSPENDED'])







        if query:







            e_qs = e_qs.filter(







                models.Q(company_name__icontains=query) |







                models.Q(contact_name__icontains=query) |







                models.Q(email__icontains=query) |







                models.Q(phone__icontains=query) |







                models.Q(industry__icontains=query)







            )







        if from_date:







            try:







                e_qs = e_qs.filter(created_at__gte=from_date)







            except Exception:







                pass







        if to_date:







            try:







                e_qs = e_qs.filter(created_at__lte=to_date + " 23:59:59")







            except Exception:







                pass







        employers = list(e_qs)















    # 3. Normalize into unified list







    items = []







    for c in candidates:







        st = c.approval_status or 'pending'







        items.append({







            'type': 'candidate',







            'id': c.id,







            'name': c.full_name,







            'company_name': '',







            'contact_name': c.full_name,







            'email': c.email,







            'phone': c.phone,







            'city_or_industry': f"{c.city}, {c.state}".strip(", ") if c.city or c.state else (c.qualification or "N/A"),







            'status': st.lower(),  # 'pending', 'approved', 'rejected'







            'status_label': st.capitalize(),







            'registered_on': c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else "",







            'created_at_dt': c.created_at,







            'rejection_reason': c.rejection_reason or "",







            'detail': c.to_dict()







        })















    for e in employers:







        st = (e.status or 'PENDING').upper()







        items.append({







            'type': 'employer',







            'id': e.id,







            'name': e.contact_name,







            'company_name': e.company_name,







            'contact_name': e.contact_name,







            'email': e.email,







            'phone': e.phone,







            'city_or_industry': f"{e.company_name} ({e.industry or 'N/A'})",







            'status': st.lower(),  # 'pending', 'approved', 'rejected', 'suspended'







            'status_label': st,







            'registered_on': e.created_at.strftime("%Y-%m-%d %H:%M:%S") if e.created_at else "",







            'created_at_dt': e.created_at,







            'rejection_reason': e.rejection_reason or "",







            'detail': e.to_dict()







        })















    # Sort newest first







    items.sort(key=lambda x: x['created_at_dt'] or timezone.now(), reverse=True)















    # Remove temporary sorting datetime field before JSON serialization







    for it in items:







        it.pop('created_at_dt', None)















    total_count = len(items)







    total_pages = max(1, (total_count + per_page - 1) // per_page)







    page = min(page, total_pages)















    start_idx = (page - 1) * per_page







    end_idx = start_idx + per_page







    paginated_items = items[start_idx:end_idx]















    return JsonResponse({







        'status': 'success',







        'items': paginated_items,







        'total_count': total_count,







        'page': page,







        'per_page': per_page,







        'total_pages': total_pages,







        'has_next': page < total_pages,







        'has_prev': page > 1,







    })























@admin_required







def api_admin_registrations_summary(request):







    """Returns DB summary counts for top 4 cards and sidebar badge."""







    c_total = CandidateAccount.objects.count()







    c_pending = CandidateAccount.objects.filter(approval_status='pending').count()







    c_approved = CandidateAccount.objects.filter(approval_status='approved').count()







    c_rejected = CandidateAccount.objects.filter(approval_status='rejected').count()















    e_total = EmployerAccount.objects.count()







    e_pending = EmployerAccount.objects.filter(status='PENDING').count()







    e_approved = EmployerAccount.objects.filter(status='APPROVED').count()







    e_rejected = EmployerAccount.objects.filter(status='REJECTED').count()







    e_suspended = EmployerAccount.objects.filter(status='SUSPENDED').count()















    return JsonResponse({







        'status': 'success',







        'counts': {







            'total': c_total + e_total,







            'total_candidates': c_total,







            'total_employers': e_total,















            'pending': c_pending + e_pending,







            'pending_candidates': c_pending,







            'pending_employers': e_pending,















            'approved': c_approved + e_approved,







            'approved_candidates': c_approved,







            'approved_employers': e_approved,















            'rejected_suspended': c_rejected + e_rejected + e_suspended,







            'rejected_candidates': c_rejected,







            'rejected_employers': e_rejected,







            'suspended_employers': e_suspended,







        }







    })























@admin_required







@require_http_methods(["POST"])







def api_admin_bulk_registrations_action(request):







    """Bulk approves or rejects selected candidate / employer registrations."""







    try:







        data = json.loads(request.body) if request.body else request.POST







    except Exception:







        data = request.POST















    action = (data.get('action') or '').strip().lower()  # 'approve', 'reject'







    reason = (data.get('reason') or '').strip()







    raw_items = data.get('items') or []















    if action not in ['approve', 'reject']:







        return JsonResponse({"status": "error", "message": "Invalid bulk action."}, status=400)







    if action == 'reject' and not reason:







        return JsonResponse({"status": "error", "message": "Rejection reason is mandatory for bulk rejection."}, status=400)















    processed_count = 0







    for item in raw_items:







        it_type = str(item.get('type') or '').lower()







        it_id = item.get('id')







        if not it_id:







            continue















        if it_type == 'candidate':







            if action == 'approve':







                try:







                    c = CandidateAccount.objects.get(id=it_id)







                    if c.is_approved and c.approval_status == 'approved':







                        processed_count += 1







                        continue







                    c.is_approved = True







                    c.approval_status = 'approved'







                    c.rejection_reason = ""







                    c.save()







                    from apps.candidate_portal.notifications import notify_candidate_approved







                    notify_candidate_approved(c)







                    log_activity("Candidate Approved", f"Candidate '{c.full_name}' approved.", f"Admin bulk approved candidate '{c.full_name}' ({c.email}).")







                    processed_count += 1







                except CandidateAccount.DoesNotExist:







                    pass







            elif action == 'reject':







                try:







                    c = CandidateAccount.objects.get(id=it_id)







                    c.is_approved = False







                    c.approval_status = 'rejected'







                    c.rejection_reason = reason







                    c.save()







                    from apps.candidate_portal.notifications import notify_candidate_rejected







                    notify_candidate_rejected(c, reason=reason)







                    log_activity("Candidate Rejected", f"Candidate '{c.full_name}' rejected.", f"Admin bulk rejected candidate '{c.full_name}'. Reason: {reason}")







                    processed_count += 1







                except CandidateAccount.DoesNotExist:







                    pass















        elif it_type == 'employer':







            if action == 'approve':







                try:







                    e = EmployerAccount.objects.get(id=it_id)







                    if e.status == 'APPROVED':







                        processed_count += 1







                        continue







                    e.status = 'APPROVED'







                    e.rejection_reason = ""







                    e.approved_at = timezone.now()







                    if getattr(request, 'admin_user', None):







                        e.approved_by = request.admin_user







                    e.save()







                    if e.company:







                        e.company.status = 'Active'







                        e.company.save()







                    from apps.employer_portal.notifications import notify_employer_approved







                    notify_employer_approved(e)







                    log_activity("Employer Approved", f"Employer '{e.company_name}' approved.", f"Admin bulk approved employer '{e.company_name}' ({e.email}).")







                    processed_count += 1







                except EmployerAccount.DoesNotExist:







                    pass







            elif action == 'reject':







                try:







                    e = EmployerAccount.objects.get(id=it_id)







                    e.status = 'REJECTED'







                    e.rejection_reason = reason







                    e.save()







                    from apps.employer_portal.notifications import notify_employer_rejected







                    notify_employer_rejected(e, reason)







                    log_activity("Employer Rejected", f"Employer '{e.company_name}' rejected.", f"Admin bulk rejected employer '{e.company_name}'. Reason: {reason}")







                    processed_count += 1







                except EmployerAccount.DoesNotExist:







                    pass















    extra_note = " Approval/notification email(s) dispatched." if action in ['approve', 'reject'] else ""







    return JsonResponse({







        "status": "success",







        "message": f"Successfully {action}d {processed_count} registration(s).{extra_note}",







        "count": processed_count







    })























@admin_required







def api_admin_registrations_export(request):







    """Export registration list to CSV."""







    import csv







    from django.http import HttpResponse















    response = HttpResponse(content_type='text/csv')







    response['Content-Disposition'] = f'attachment; filename="registrations_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'















    writer = csv.writer(response)







    writer.writerow(['Type', 'ID', 'Name / Company', 'Contact Person', 'Email', 'Phone', 'City / State', 'Industry / Qualification', 'Registered On', 'Status', 'Rejection Reason'])















    reg_type = request.GET.get('type', 'all').lower()







    status_filter = request.GET.get('status', 'all').lower()















    if reg_type in ['all', 'candidate', 'candidates']:







        c_qs = CandidateAccount.objects.all().order_by('-id')







        if status_filter != 'all':







            c_qs = c_qs.filter(approval_status=status_filter)







        for c in c_qs:







            writer.writerow([







                'Candidate', c.id, c.full_name, c.full_name, c.email, c.phone,







                f"{c.city}, {c.state}".strip(", "), c.qualification or "",







                c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else "",







                (c.approval_status or "pending").capitalize(), c.rejection_reason or ""







            ])















    if reg_type in ['all', 'employer', 'employers']:







        e_qs = EmployerAccount.objects.all().order_by('-id')







        if status_filter != 'all':







            e_qs = e_qs.filter(status=status_filter.upper())







        for e in e_qs:







            writer.writerow([







                'Employer', e.id, e.company_name, e.contact_name, e.email, e.phone,







                f"{e.city}, {e.state}".strip(", "), e.industry or "",







                e.created_at.strftime("%Y-%m-%d %H:%M:%S") if e.created_at else "",







                e.status, e.rejection_reason or ""







            ])















    return response























def api_admin_topbar_counts(request):







    """Returns real-time dynamic counts for admin topbar badges."""







    try:







        pending_candidates = CandidateAccount.objects.filter(approval_status='pending').count()







        pending_employers = EmployerAccount.objects.filter(status='PENDING').count()







        pending_job_apps = Applicant.objects.filter(approval_status='Pending').count()







        pending_internship_apps = InternshipApplication.objects.filter(status='Pending').count()















        contact_enquiries = ContactEnquiry.objects.count()







        company_enquiries = CompanyEnquiry.objects.count()







        internship_enquiries = InternshipEnquiry.objects.count()















        total_messages = contact_enquiries + company_enquiries + internship_enquiries







        total_notifications = pending_candidates + pending_employers + pending_job_apps







        total_mail_apps = pending_job_apps + pending_internship_apps















        return JsonResponse({







            "status": "success",







            "messages": total_messages,







            "notifications": total_notifications,







            "mail": total_mail_apps,







            "pending_candidates": pending_candidates,







            "pending_employers": pending_employers,







            "pending_job_apps": pending_job_apps







        })







    except Exception as e:







        return JsonResponse({"status": "error", "message": str(e)}, status=500)























@admin_required







def admin_reports_view(request, report_type='candidate'):







    """Renders Candidate and Employer Analytics & Reports page with weekly/monthly/yearly time filters."""







    admin_id = request.session.get('admin_id')







    if not admin_id:







        return redirect('/admin-panel/login/')















    admin_user = AdminUser.objects.filter(id=admin_id).first()







    







    period = request.GET.get('period', 'monthly').lower()  # 'weekly', 'monthly', 'yearly', 'all'







    now = timezone.now()















    if period == 'weekly':







        start_date = now - datetime.timedelta(days=7)







        period_label = "Weekly (Last 7 Days)"







    elif period == 'yearly':







        start_date = now - datetime.timedelta(days=365)







        period_label = "Yearly (Last 365 Days)"







    elif period == 'all':







        start_date = timezone.make_aware(datetime.datetime(2000, 1, 1))







        period_label = "All Time"







    else:







        period = 'monthly'







        start_date = now - datetime.timedelta(days=30)







        period_label = "Monthly (Last 30 Days)"















    from_param = request.GET.get('from', '').strip()







    to_param = request.GET.get('to', '').strip()







    







    if from_param:







        try:







            naive_from = datetime.datetime.strptime(from_param, "%Y-%m-%d")







            start_date = timezone.make_aware(naive_from)







            period_label = f"From {from_param}"







        except Exception:







            pass







    







    end_date = now







    if to_param:







        try:







            naive_to = datetime.datetime.strptime(to_param, "%Y-%m-%d") + datetime.timedelta(days=1)







            end_date = timezone.make_aware(naive_to)







            period_label += f" to {to_param}"







        except Exception:







            pass















    records = []







    







    if report_type in ['company', 'employer']:







        report_type = 'company'







        sec_title = "Employer & Corporate Reports"







        







        emp_accounts = list(EmployerAccount.objects.filter(created_at__gte=start_date, created_at__lt=end_date).order_by('-id'))







        comp_enquiries = list(CompanyEnquiry.objects.filter(created_at__gte=start_date, created_at__lt=end_date).order_by('-id'))







        







        total_employers = len(emp_accounts)







        approved_employers = sum(1 for e in emp_accounts if (e.status or '').upper() == 'APPROVED')







        pending_employers = sum(1 for e in emp_accounts if (e.status or '').upper() == 'PENDING')







        jobs_posted = Job.objects.filter(created_at__gte=start_date, created_at__lt=end_date).count()







        reqs_created = CompanyRequirement.objects.filter(created_at__gte=start_date, created_at__lt=end_date).count()







        







        for e in emp_accounts:







            st = (e.status or 'PENDING').upper()







            records.append({







                'id': f"EMP-{e.id}",







                'raw_id': e.id,







                'type': 'Employer Account',







                'name': e.company_name,







                'contact_person': e.contact_name,







                'email': e.email,







                'phone': e.phone,







                'city_industry': f"{e.city or 'N/A'} • {e.industry or 'Corporate'}",







                'date': e.created_at.strftime("%d %b %Y, %I:%M %p") if e.created_at else "N/A",







                'created_at': e.created_at,







                'status': st,







                'status_class': 'active' if st == 'APPROVED' else ('rejected' if st in ['REJECTED', 'SUSPENDED'] else 'shortlisted')







            })







            







        for ce in comp_enquiries:







            records.append({







                'id': f"ENQ-{ce.id}",







                'raw_id': ce.id,







                'type': 'Company Enquiry',







                'name': ce.company_name,







                'contact_person': ce.recruiter_name,







                'email': ce.email,







                'phone': ce.phone,







                'city_industry': f"{ce.job_title or 'Hiring'} ({ce.vacancies or 1} Vacancies)",







                'date': ce.created_at.strftime("%d %b %Y, %I:%M %p") if ce.created_at else "N/A",







                'created_at': ce.created_at,







                'status': ce.status or "New",







                'status_class': _get_status_class(ce.status)







            })















        metrics = {







            'card1_num': total_employers,







            'card1_title': 'NEW EMPLOYER REGISTRATIONS',







            'card1_sub': f"Registered in {period_label}",







            







            'card2_num': approved_employers,







            'card2_title': 'APPROVED EMPLOYERS',







            'card2_sub': f"Verified in {period_label}",







            







            'card3_num': pending_employers,







            'card3_title': 'PENDING APPROVALS',







            'card3_sub': f"Awaiting review",







            







            'card4_num': jobs_posted + reqs_created,







            'card4_title': 'JOBS & REQUIREMENTS',







            'card4_sub': f"Created in {period_label}",







        }







    







    else:







        report_type = 'candidate'







        sec_title = "Candidate Analytics & Reports"







        







        cand_accounts = list(CandidateAccount.objects.filter(created_at__gte=start_date, created_at__lt=end_date).order_by('-id'))







        applicants = list(Applicant.objects.exclude(job_title__icontains="intern").filter(applied_on__gte=start_date, applied_on__lt=end_date).order_by('-id'))







        resumes = list(Resume.objects.filter(uploaded_on__gte=start_date, uploaded_on__lt=end_date).order_by('-id'))







        







        total_candidates = len(cand_accounts) + len(resumes)







        total_applications = len(applicants)







        shortlisted_cand = Applicant.objects.filter(status__icontains='Shortlisted', applied_on__gte=start_date, applied_on__lt=end_date).count()







        placed_cand = Placement.objects.filter(created_at__gte=start_date, created_at__lt=end_date).count() + Applicant.objects.filter(status__icontains='Joined', applied_on__gte=start_date, applied_on__lt=end_date).count()







        







        for c in cand_accounts:







            st = c.approval_status or 'pending'







            records.append({







                'id': f"REG-{c.id}",







                'raw_id': c.id,







                'type': 'Candidate Registration',







                'name': c.full_name,







                'contact_person': c.qualification or 'Job Seeker',







                'email': c.email,







                'phone': c.phone,







                'city_industry': c.city or "N/A",







                'date': c.created_at.strftime("%d %b %Y, %I:%M %p") if c.created_at else "N/A",







                'created_at': c.created_at,







                'status': st.capitalize(),







                'status_class': 'active' if st == 'approved' else ('rejected' if st == 'rejected' else 'shortlisted')







            })







            







        for a in applicants:







            records.append({







                'id': f"APP-{a.id}",







                'raw_id': a.id,







                'type': 'Job Application',







                'name': a.full_name,







                'contact_person': a.job_title or 'Applicant',







                'email': a.email,







                'phone': a.phone,







                'city_industry': f"{a.city or 'N/A'} • {a.qualification or 'N/A'}",







                'date': a.applied_on.strftime("%d %b %Y, %I:%M %p") if a.applied_on else "N/A",







                'created_at': a.applied_on,







                'status': a.status or "New",







                'status_class': _get_status_class(a.status)







            })















        metrics = {







            'card1_num': total_candidates,







            'card1_title': 'NEW CANDIDATE REGISTRATIONS',







            'card1_sub': f"Registered in {period_label}",







            







            'card2_num': total_applications,







            'card2_title': 'JOB APPLICATIONS SUBMITTED',







            'card2_sub': f"Submitted in {period_label}",







            







            'card3_num': shortlisted_cand,







            'card3_title': 'SHORTLISTED CANDIDATES',







            'card3_sub': f"Shortlisted in {period_label}",







            







            'card4_num': placed_cand,







            'card4_title': 'SUCCESSFUL PLACEMENTS',







            'card4_sub': f"Joined in {period_label}",







        }















    records.sort(key=lambda x: x.get('created_at') or timezone.now(), reverse=True)















    context = {







        'admin_user': admin_user,







        'active_menu': 'analytics',







        'sec_title': sec_title,







        'report_type': report_type,







        'period': period,







        'period_label': period_label,







        'metrics': metrics,







        'records': records,







        'total_count': len(records),







        'from_param': from_param,







        'to_param': to_param,







    }







    return render(request, 'dashboard/reports.html', context)























# ==============================================================================







# JOB OPENINGS MANAGEMENT & CRUD APIS







# ==============================================================================







@admin_required







def admin_job_openings_view(request):







    """







    Dedicated Job Management Dashboard with KPI Summary Cards,







    Search/Filter, "+ Post New Job", "Edit Job", and "Delete" actions.







    """







    admin_user = getattr(request, 'admin_user', None)







    







    search_q = request.GET.get('search', '').strip()







    status_filter = request.GET.get('status', 'all').strip()







    







    jobs_qs = Job.objects.select_related('company', 'employer').all().order_by('-id')







    







    all_jobs_list = list(jobs_qs)







    total_count = len(all_jobs_list)







    active_count = sum(1 for j in all_jobs_list if j.status in Job.LIVE_STATUSES)







    pending_count = sum(1 for j in all_jobs_list if j.status in Job.PENDING_STATUSES)







    closed_count = sum(1 for j in all_jobs_list if j.status in Job.CLOSED_STATUSES)















    # Employment Type Counts for Cards







    full_time_count = 0







    part_time_count = 0







    wfh_count = 0







    other_count = 0







    for j in all_jobs_list:







        et = (j.employment_type or 'Full Time').lower()







        if 'part' in et:







            part_time_count += 1







        elif 'home' in et or 'remote' in et or 'wfh' in et:







            wfh_count += 1







        elif 'full' in et:







            full_time_count += 1







        else:







            other_count += 1







    







    if status_filter and status_filter != 'all':







        if status_filter.lower() in ['active', 'live']:







            jobs_qs = jobs_qs.filter(status__in=Job.LIVE_STATUSES)







        elif status_filter.lower() in ['pending', 'pending_approval', 'draft']:







            jobs_qs = jobs_qs.filter(status__in=Job.PENDING_STATUSES)







        elif status_filter.lower() in ['closed', 'expired', 'inactive']:







            jobs_qs = jobs_qs.filter(status__in=Job.CLOSED_STATUSES)







            







    if search_q:







        jobs_qs = jobs_qs.filter(







            models.Q(title__icontains=search_q) |







            models.Q(category__icontains=search_q) |







            models.Q(location__icontains=search_q) |







            models.Q(company__name__icontains=search_q) |







            models.Q(employer__company_name__icontains=search_q)







        )







        







    category_filter = request.GET.get('category', '').strip()







    if category_filter and category_filter != 'all':







        jobs_qs = jobs_qs.filter(







            models.Q(category__iexact=category_filter) |







            models.Q(category__icontains=category_filter)







        )















    employment_type_filter = request.GET.get('employment_type', '').strip()







    if employment_type_filter and employment_type_filter != 'all':







        jobs_qs = jobs_qs.filter(employment_type__icontains=employment_type_filter)















    employers_qs = EmployerAccount.objects.all().order_by('company_name')







    companies_qs = Company.objects.all().order_by('name')







    job_categories_qs = JobCategory.objects.filter(status='Active').order_by('category_type', 'order', 'name')















    context = {







        'admin_user': admin_user,







        'active_menu': 'companies',







        'sub_active': 'job_openings',







        'sec_title': 'Job Openings & Postings',







        'jobs': jobs_qs,







        'jobs_list': list(jobs_qs),







        'companies': companies_qs,







        'companies_list': companies_qs,







        'employers_list': employers_qs,







        'job_categories': job_categories_qs,







        'total_count': total_count,







        'total_jobs': total_count,







        'active_count': active_count,







        'active_jobs': active_count,







        'pending_count': pending_count,







        'pending_jobs': pending_count,







        'closed_count': closed_count,







        'closed_jobs': closed_count,







        'full_time_count': full_time_count,







        'part_time_count': part_time_count,







        'wfh_count': wfh_count,







        'other_count': other_count,







        'current_search': search_q,







        'current_status': status_filter,







        'current_category': category_filter,







        'current_employment_type': employment_type_filter,







    }







    return render(request, 'dashboard/job_postings_module.html', context)


@admin_required
def admin_employer_jobs_view(request, company_id=None):
    """
    Dedicated view for an Employer / Company:
    Displays employer profile, KPI stat cards (Total Jobs, Live Jobs,
    Hiring Active, Hiring Closed/Ended, Candidates Applied),
    and the comprehensive jobs list with applicants details.
    """
    import re
    from django.db.models import Q
    from apps.companies.models import Company
    from apps.accounts.models import EmployerAccount, AdminUser
    from apps.jobs.models import Job
    from apps.candidates.models import Applicant

    admin_user = getattr(request, 'admin_user', None)
    if not admin_user:
        admin_id = request.session.get('admin_id')
        if admin_id:
            admin_user = AdminUser.objects.filter(id=admin_id).first()

    name_query = request.GET.get('name', '').strip()
    id_param = request.GET.get('id', '').strip()
    target_id = company_id or (int(id_param) if id_param.isdigit() else None)

    company = None
    employer_account = None

    if target_id:
        company = Company.objects.filter(id=target_id).first()
        if not company:
            employer_account = EmployerAccount.objects.filter(id=target_id).first()
            if employer_account and employer_account.company:
                company = employer_account.company

    if not company and not employer_account and name_query:
        company = Company.objects.filter(name__iexact=name_query).first()
        if not company:
            employer_account = EmployerAccount.objects.filter(company_name__iexact=name_query).first()
            if employer_account and employer_account.company:
                company = employer_account.company

    if not company and not employer_account:
        return redirect('/admin-panel/companies/all/')

    # Gather associated employers and company
    employers = []
    if company:
        employers = list(EmployerAccount.objects.filter(
            Q(company=company) | Q(company_name__iexact=company.name)
        ))
        if not employer_account and employers:
            employer_account = employers[0]
    elif employer_account:
        employers = [employer_account]
        if employer_account.company:
            company = employer_account.company

    company_name = company.name if company else (employer_account.company_name if employer_account else "Unknown Employer")
    primary_contact_name = ""
    contact_phone = company.phone if company else (employer_account.phone if employer_account else "")
    contact_email = company.email if company else (employer_account.email if employer_account else "")
    city = company.city if company else (employer_account.city if employer_account else "Lucknow")
    state = company.state if company else (employer_account.state if employer_account else "Uttar Pradesh")
    industry = company.industry if company else "Corporate Employer"
    website = company.website if company else (employer_account.website if employer_account else "")
    gst_number = company.gst_number if company else (employer_account.gst_number if employer_account else "")

    if company:
        contacts = list(company.contacts.all())
        primary_contact = next((c for c in contacts if c.is_primary), contacts[0] if contacts else None)
        if primary_contact:
            primary_contact_name = f"{primary_contact.name} ({primary_contact.designation or 'Primary Contact'})"
            if not contact_phone:
                contact_phone = primary_contact.phone
            if not contact_email:
                contact_email = primary_contact.email
    elif employer_account:
        primary_contact_name = employer_account.contact_name or "Employer Contact"

    # Match all jobs posted by this employer/company
    job_query = Q()
    if company:
        job_query |= Q(company=company)
        job_query |= Q(requirement__company=company)
    if employers:
        job_query |= Q(employer__in=employers)
    if company_name:
        job_query |= Q(employer__company_name__iexact=company_name)
        job_query |= Q(company__name__iexact=company_name)

    jobs = Job.objects.filter(job_query).distinct().select_related('company', 'employer').order_by('-created_at', '-id')

    jobs_list = []
    total_jobs = jobs.count()
    live_jobs_count = 0
    hiring_active_count = 0
    hiring_closed_count = 0
    pending_approval_count = 0
    total_applicants_count = 0

    for job in jobs:
        is_live = job.status in Job.LIVE_STATUSES
        is_pending = job.status in Job.PENDING_STATUSES
        is_closed = job.status in Job.CLOSED_STATUSES or job.status == 'REJECTED'

        is_hiring_active = is_live

        if is_live:
            live_jobs_count += 1
        if is_hiring_active:
            hiring_active_count += 1
        elif is_closed:
            hiring_closed_count += 1
        if is_pending:
            pending_approval_count += 1

        apps = Applicant.objects.filter(job=job).order_by('-applied_on', '-id')
        app_count = apps.count()
        total_applicants_count += app_count

        applicants_data = []
        for a in apps:
            resume_val = str(a.resume or '').strip()
            resume_url = ''
            if resume_val:
                if resume_val.startswith('http://') or resume_val.startswith('https://') or resume_val.startswith('/'):
                    resume_url = resume_val
                else:
                    resume_url = f"/media/{resume_val}"

            applied_dt_str = "Recent"
            if a.applied_on:
                applied_dt_str = a.applied_on.strftime("%d %b %Y")

            applicants_data.append({
                'id': f"APP-{a.id}",
                'raw_id': a.id,
                'name': a.full_name or "Applicant",
                'email': a.email or "N/A",
                'phone': a.phone or "N/A",
                'experience': a.experience or "N/A",
                'status': a.status or "Applied",
                'applied_on': applied_dt_str,
                'resume_url': resume_url,
            })

        # Format experience
        raw_exp = str(job.experience or '').strip()
        if raw_exp in ['0', '0 Years', '0 yrs', '0 yr', '']:
            clean_exp = "Fresher"
        elif raw_exp.isdigit():
            clean_exp = f"{raw_exp}+ Yrs"
        else:
            clean_exp = raw_exp

        # Format salary
        raw_sal = str(job.salary or '').strip()
        if raw_sal.isdigit():
            clean_sal = f"₹{int(raw_sal):,} / mo"
        elif raw_sal:
            clean_sal = raw_sal
        else:
            clean_sal = "Negotiable"

        # Format category
        raw_cat = str(job.category or '').strip()
        if raw_cat.lower() == 'it':
            clean_cat = "IT & Software"
        elif raw_cat:
            clean_cat = raw_cat.title()
        else:
            clean_cat = "General"

        # Format location
        raw_loc = str(job.location or '').strip()
        if not raw_loc:
            clean_loc = f"{city}, {state}"
        else:
            clean_loc = re.sub(r'([a-zA-Z0-9])([A-Z][a-z]+)', r'\1, \2', raw_loc)

        # Format deadline
        raw_deadline = str(job.deadline or '').strip()
        if raw_deadline.isdigit():
            clean_deadline = f"{raw_deadline} Days"
        elif raw_deadline:
            clean_deadline = raw_deadline
        else:
            clean_deadline = "Open"

        jobs_list.append({
            'id': job.id,
            'ref_id': f"JOB-{job.id}",
            'title': job.title,
            'category': clean_cat,
            'raw_category': job.category or "General",
            'department': job.department or "",
            'location': clean_loc,
            'employment_type': job.employment_type or "Full Time",
            'salary': clean_sal,
            'raw_salary': job.salary or "Negotiable",
            'vacancies': job.vacancies or "1",
            'experience': clean_exp,
            'deadline': clean_deadline,
            'status': job.status,
            'is_live': is_live,
            'is_pending': is_pending,
            'is_closed': is_closed,
            'is_hiring_active': is_hiring_active,
            'created_at': job.created_at.strftime("%d %b %Y") if job.created_at else "N/A",
            'applicants_count': app_count,
            'applicants': applicants_data,
        })

    context = {
        'admin_user': admin_user,
        'active_menu': 'companies',
        'sub_active': 'companies_all',
        'company': company,
        'employer_account': employer_account,
        'company_id': target_id or (company.id if company else (employer_account.id if employer_account else 0)),
        'company_name': company_name,
        'city': city,
        'state': state,
        'industry': industry,
        'email': contact_email,
        'phone': contact_phone,
        'primary_contact_name': primary_contact_name,
        'website': website,
        'gst_number': gst_number,
        'total_jobs': total_jobs,
        'live_jobs_count': live_jobs_count,
        'hiring_active_count': hiring_active_count,
        'hiring_closed_count': hiring_closed_count,
        'pending_approval_count': pending_approval_count,
        'total_applicants_count': total_applicants_count,
        'jobs': jobs_list,
    }

    return render(request, 'dashboard/employer_jobs_detail.html', context)























@admin_required







@require_http_methods(["POST"])







def api_admin_job_save(request):







    """







    API handler for creating or updating a Job post.







    Handles both JSON bodies and FormData POST payloads.







    """







    try:







        if request.content_type and 'application/json' in request.content_type:







            data = json.loads(request.body.decode('utf-8'))







        else:







            data = request.POST.dict()







            if not data and request.body:







                try:







                    data = json.loads(request.body.decode('utf-8'))







                except Exception:







                    data = {}















        job_id = data.get('job_id')







        







        title = data.get('title', '').strip()







        if not title:







            return JsonResponse({'status': 'error', 'message': 'Job Title is required'}, status=400)







            







        company_id = data.get('company_id')







        custom_company = data.get('custom_company', '').strip()







        company_obj = None







        if custom_company and custom_company != '__custom__':







            company_obj = Company.objects.filter(name__iexact=custom_company).first()







            if not company_obj:







                from django.utils.text import slugify







                import uuid







                safe_slug = slugify(custom_company) or f"company_{uuid.uuid4().hex[:6]}"







                company_obj = Company.objects.create(







                    name=custom_company,







                    email=f"contact@{safe_slug}.com",







                    phone="",







                    city="Lucknow",







                    state="Uttar Pradesh",







                    status="Active"







                )







        elif company_id and company_id != '__custom__':







            try:







                company_obj = Company.objects.get(id=company_id)







            except (Company.DoesNotExist, ValueError):







                pass















        employer_id = data.get('employer_id')







        custom_employer = data.get('custom_employer', '').strip()







        employer_obj = None







        if custom_employer and custom_employer != '__custom__':







            employer_obj = EmployerAccount.objects.filter(company_name__iexact=custom_employer).first()







            if not employer_obj:







                employer_obj = EmployerAccount.objects.filter(contact_name__iexact=custom_employer).first()







            if not employer_obj:







                from django.utils.text import slugify







                import uuid







                safe_slug = slugify(custom_employer) or f"emp_{uuid.uuid4().hex[:6]}"







                random_email = f"{safe_slug}_{uuid.uuid4().hex[:4]}@skyvisiongoc.com"







                employer_obj = EmployerAccount(







                    company_name=custom_employer,







                    contact_name=custom_employer,







                    email=random_email,







                    phone="",







                    status="APPROVED"







                )







                employer_obj.set_password("TempEmployer123!")







                employer_obj.save()







        elif employer_id and employer_id != '__custom__':







            try:







                employer_obj = EmployerAccount.objects.get(id=employer_id)







            except (EmployerAccount.DoesNotExist, ValueError):







                pass















        if job_id:







            try:







                job = Job.objects.get(id=job_id)







            except Job.DoesNotExist:







                return JsonResponse({'status': 'error', 'message': 'Job not found'}, status=404)







        else:







            job = Job()







            







        job.title = title







        job.company = company_obj







        job.employer = employer_obj







        job.category = data.get('category', '').strip()







        job.department = data.get('department', '').strip()







        job.location = data.get('location', 'Lucknow, UP').strip()







        job.employment_type = data.get('employment_type', 'Full Time').strip()







        job.experience = data.get('experience', '').strip()







        job.salary = data.get('salary', '').strip()







        job.vacancies = str(data.get('vacancies', '1')).strip()







        job.description = data.get('description', '').strip()







        job.requirements = data.get('requirements', '').strip()







        







        req_status = data.get('status')







        if req_status:







            job.status = req_status







        elif not job_id:







            job.status = 'Active'







            







        job.save()







        return JsonResponse({'status': 'success', 'message': 'Job post saved successfully', 'job': job.to_dict()})







    except Exception as e:







        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)























@admin_required







@require_http_methods(["POST", "DELETE"])







def api_admin_job_delete(request, job_id):







    """







    API handler for deleting a Job post.







    """







    try:







        job = Job.objects.get(id=job_id)







        job.delete()







        return JsonResponse({'status': 'success', 'message': 'Job post deleted successfully'})







    except Job.DoesNotExist:







        return JsonResponse({'status': 'error', 'message': 'Job not found'}, status=404)







    except Exception as e:







        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)























@admin_required







@require_http_methods(["POST"])







def api_admin_job_status(request, job_id):







    """







    API handler for changing job status (e.g. Active, Closed, Pending).







    """







    try:







        data = {}
        if request.content_type and 'application/json' in request.content_type:
            try:
                data = json.loads(request.body.decode('utf-8'))
            except Exception:
                data = {}
        else:
            data = request.POST
            if not data:
                try:
                    data = json.loads(request.body.decode('utf-8'))
                except Exception:
                    data = {}















        new_status = data.get('status', '').strip()







        if not new_status:







            return JsonResponse({'status': 'error', 'message': 'Status value is required'}, status=400)







            







        # Standardize incoming status







        if new_status.upper() in ['ACTIVE', 'LIVE']:







            standard_status = Job.STATUS_LIVE







        elif new_status.upper() in ['INACTIVE', 'CLOSED']:







            standard_status = Job.STATUS_CLOSED







        elif new_status.upper() in ['PENDING', 'PENDING_APPROVAL']:







            standard_status = Job.STATUS_PENDING_APPROVAL







        elif new_status.upper() in [Job.STATUS_DRAFT, Job.STATUS_EXPIRED, Job.STATUS_REJECTED]:







            standard_status = new_status.upper()







        else:







            standard_status = new_status















        job = Job.objects.get(id=job_id)







        job.status = standard_status







        job.save()















        # Sync requirement status







        req = CompanyRequirement.objects.filter(job=job).first()







        if req:







            req.status = standard_status







            req.save()















        return JsonResponse({'status': 'success', 'message': f'Job status updated to {standard_status}'})







    except Job.DoesNotExist:







        return JsonResponse({'status': 'error', 'message': 'Job not found'}, status=404)







    except Exception as e:







        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)























@admin_required







def admin_job_approvals_view(request):







    """







    Dedicated Job Approvals Dashboard in Super Admin Panel.







    Lists pending employer jobs & requirements awaiting approval,







    with direct Approve & Publish (Live on Site) and Reject actions.







    """







    admin_user = getattr(request, 'admin_user', None)







    







    status_tab = request.GET.get('tab', 'pending').strip().lower()







    search_q = request.GET.get('search', '').strip()







    







    jobs_qs = Job.objects.select_related('company', 'employer').all().order_by('-id')







    all_jobs = list(jobs_qs)







    







    pending_count = sum(1 for j in all_jobs if j.status in ['PENDING_APPROVAL', 'Pending', 'pending', 'DRAFT', 'Draft', 'draft'])







    active_count = sum(1 for j in all_jobs if j.status in ['Active', 'LIVE', 'Live', 'active', 'live'])







    rejected_count = sum(1 for j in all_jobs if j.status in ['REJECTED', 'Rejected', 'rejected'])







    total_count = len(all_jobs)







    







    if status_tab == 'active':







        jobs_filtered = [j for j in all_jobs if j.status in ['Active', 'LIVE', 'Live', 'active', 'live']]







    elif status_tab == 'rejected':







        jobs_filtered = [j for j in all_jobs if j.status in ['REJECTED', 'Rejected', 'rejected']]







    else:







        status_tab = 'pending'







        jobs_filtered = [j for j in all_jobs if j.status in ['PENDING_APPROVAL', 'Pending', 'pending', 'DRAFT', 'Draft', 'draft']]















    if search_q:







        q_low = search_q.lower()







        jobs_filtered = [







            j for j in jobs_filtered







            if q_low in (j.title or '').lower()







            or q_low in (j.category or '').lower()







            or q_low in (j.location or '').lower()







            or (j.company and q_low in j.company.name.lower())







            or (j.employer and q_low in j.employer.company_name.lower())







        ]















    context = {







        'admin_user': admin_user,







        'active_menu': 'job_approvals',







        'sub_active': 'requirements_active',







        'sec_title': 'Job Approvals Queue',







        'jobs_list': jobs_filtered,







        'status_tab': status_tab,







        'pending_count': pending_count,







        'active_count': active_count,







        'rejected_count': rejected_count,







        'total_count': total_count,







        'current_search': search_q,







    }







    return render(request, 'dashboard/job_approvals_module.html', context)























# ==============================================================================







# JOB CATEGORIES MANAGEMENT (Job Pills, Industries We Serve, Job Categories)







# ==============================================================================















def admin_job_categories_view(request):







    """







    Dedicated Job Categories & Sectors Management Hub with KPI statistics,







    Category-wise Filter (Job Pills / Industries / Job Categories),







    Search, Add, Edit, Delete, and Toggle Status actions.







    """







    admin_id = request.session.get('admin_id')







    if not admin_id:







        return redirect('/admin-panel/login/')















    admin_user = AdminUser.objects.filter(id=admin_id).first()















    # Query params







    type_filter = request.GET.get('type', 'all').strip()







    status_filter = request.GET.get('status', 'all').strip()







    search_q = request.GET.get('search', '').strip()







    sort_by = request.GET.get('sort', 'order').strip()















    qs = JobCategory.objects.all()















    # KPI Statistics







    total_count = qs.count()







    pills_total = qs.filter(category_type='job_pill').count()







    pills_active = qs.filter(category_type='job_pill', status='Active').count()







    industries_total = qs.filter(category_type='industry').count()







    industries_active = qs.filter(category_type='industry', status='Active').count()







    categories_total = qs.filter(category_type='job_category').count()







    categories_active = qs.filter(category_type='job_category', status='Active').count()







    job_types_total = qs.filter(category_type='job_type').count()







    job_types_active = qs.filter(category_type='job_type', status='Active').count()







    active_count = qs.filter(status='Active').count()







    inactive_count = qs.filter(status='Inactive').count()















    # Apply Category-wise Type Filter







    if type_filter and type_filter != 'all':







        qs = qs.filter(category_type=type_filter)















    # Apply Status Filter







    if status_filter and status_filter != 'all':







        qs = qs.filter(status=status_filter)















    # Apply Search Filter







    if search_q:







        qs = qs.filter(







            models.Q(name__icontains=search_q) |







            models.Q(field_slug__icontains=search_q) |







            models.Q(count_label__icontains=search_q) |







            models.Q(icon__icontains=search_q) |







            models.Q(description__icontains=search_q)







        )















    # Apply Sorting







    if sort_by == 'newest':







        qs = qs.order_by('-id')







    elif sort_by == 'name':







        qs = qs.order_by('name')







    elif sort_by == 'type':







        qs = qs.order_by('category_type', 'order', 'name')







    else:







        qs = qs.order_by('order', 'id')















    categories_list = list(qs)















    context = {







        'admin_user': admin_user,







        'active_menu': 'job_categories',







        'sub_active': 'job_categories',







        'sec_title': 'Job Categories & Sectors Management',







        'categories': categories_list,







        'total_count': total_count,







        'pills_total': pills_total,







        'pills_active': pills_active,







        'industries_total': industries_total,







        'industries_active': industries_active,







        'categories_total': categories_total,







        'categories_active': categories_active,







        'job_types_total': job_types_total,







        'job_types_active': job_types_active,







        'active_count': active_count,







        'inactive_count': inactive_count,







        'current_type': type_filter,







        'current_status': status_filter,







        'search_q': search_q,







        'sort_by': sort_by,







    }







    return render(request, 'dashboard/job_categories_module.html', context)























def admin_requirements_or_categories_dispatcher(request):







    """







    Dispatcher for /admin-panel/companies/requirements/all/:







    - If company_id is provided, display Company Requirements for that company.







    - Otherwise, load the Job Categories management hub (matching the sidebar link).







    """







    if request.GET.get('company_id'):







        return admin_module_generic_view(request, 'requirements_all')







    return admin_job_categories_view(request)























@admin_required







@require_http_methods(["POST"])







def api_admin_category_save(request):







    """







    API to create or update a category (Job Pill, Industry, or Job Category).







    """







    try:







        if request.content_type and 'application/json' in request.content_type:







            data = json.loads(request.body.decode('utf-8'))







        else:







            data = request.POST.dict()







            if not data and request.body:







                try:







                    data = json.loads(request.body.decode('utf-8'))







                except Exception:







                    data = {}















        cat_id = data.get('category_id') or data.get('id')







        name = data.get('name', '').strip()







        if not name:







            return JsonResponse({'status': 'error', 'message': 'Category Name is required'}, status=400)















        category_type = data.get('category_type', 'job_category').strip()







        if category_type not in ['job_pill', 'industry', 'job_category', 'job_type']:







            category_type = 'job_category'















        if cat_id:







            try:







                cat = JobCategory.objects.get(id=cat_id)







            except JobCategory.DoesNotExist:







                return JsonResponse({'status': 'error', 'message': 'Category not found'}, status=404)







        else:







            cat = JobCategory()















        cat.name = name







        cat.category_type = category_type







        cat.icon = data.get('icon', 'fa-solid fa-briefcase').strip() or 'fa-solid fa-briefcase'







        cat.badge_color = data.get('badge_color', 't-indigo').strip() or 't-indigo'







        cat.count_label = data.get('count_label', '').strip()







        cat.field_slug = data.get('field_slug', '').strip()







        cat.link_url = data.get('link_url', '').strip()







        try:







            cat.order = int(data.get('order', 0))







        except (ValueError, TypeError):







            cat.order = 0







        cat.status = data.get('status', 'Active').strip() or 'Active'







        cat.description = data.get('description', '').strip()















        cat.save()















        return JsonResponse({







            'status': 'success',







            'message': 'Category saved successfully',







            'category': cat.to_dict()







        })







    except Exception as e:







        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)























@admin_required







@require_http_methods(["POST", "DELETE"])







def api_admin_category_delete(request, cat_id):







    """







    API to delete a category.







    """







    try:







        cat = JobCategory.objects.get(id=cat_id)







        cat_name = cat.name







        cat.delete()







        return JsonResponse({'status': 'success', 'message': f'"{cat_name}" deleted successfully'})







    except JobCategory.DoesNotExist:







        return JsonResponse({'status': 'error', 'message': 'Category not found'}, status=404)







    except Exception as e:







        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)























@admin_required







@require_http_methods(["POST"])







def api_admin_category_status(request, cat_id):







    """







    API to toggle category status between Active and Inactive.







    """







    try:







        data = {}
        if request.content_type and 'application/json' in request.content_type:
            try:
                data = json.loads(request.body.decode('utf-8'))
            except Exception:
                data = {}
        else:
            data = request.POST
            if not data:
                try:
                    data = json.loads(request.body.decode('utf-8'))
                except Exception:
                    data = {}















        cat = JobCategory.objects.get(id=cat_id)







        new_status = data.get('status')







        if new_status:







            cat.status = new_status







        else:







            cat.status = 'Inactive' if cat.status == 'Active' else 'Active'







        cat.save()















        return JsonResponse({







            'status': 'success',







            'message': f'Status of "{cat.name}" updated to {cat.status}',







            'status_val': cat.status







        })







    except JobCategory.DoesNotExist:







        return JsonResponse({'status': 'error', 'message': 'Category not found'}, status=404)







    except Exception as e:







        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)























@admin_required







@require_http_methods(["POST"])







def api_admin_category_seed(request):







    """







    API to re-seed default categories if needed.







    """







    try:







        from apps.jobs.seed_categories import seed_categories







        total = seed_categories(force=True)







        return JsonResponse({'status': 'success', 'message': f'Default categories re-seeded successfully. Total: {total}'})







    except Exception as e:







        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)























@admin_required







def admin_create_job_offer_api(request):







    """Admin creates and issues an official Job Offer for a candidate."""







    if request.method != "POST":







        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)















    try:







        data = json.loads(request.body) if request.body else request.POST







    except Exception:







        data = request.POST















    applicant_id = data.get('applicant_id')







    candidate_name = (data.get('candidate_name') or "").strip()







    company_name = (data.get('company_name') or "").strip()







    designation = (data.get('designation') or "").strip()







    offered_ctc = (data.get('offered_ctc') or "").strip()







    joining_date = (data.get('joining_date') or "").strip()







    notes = (data.get('notes') or "").strip()















    applicant = None







    if applicant_id:







        applicant = Applicant.objects.filter(id=applicant_id).first()







        if applicant:







            if not candidate_name:







                candidate_name = applicant.full_name







            if not designation:







                designation = applicant.job_title







            if not company_name:







                company_name = (applicant.job.company_name if applicant.job and getattr(applicant.job, 'company_name', None) else '') or (applicant.job.employer.company_name if applicant.job and getattr(applicant.job, 'employer', None) else '') or applicant.current_company or "Sky Vision Partner"















    if not candidate_name:







        return JsonResponse({"status": "error", "message": "Candidate name is required."}, status=400)







    if not company_name:







        return JsonResponse({"status": "error", "message": "Company name is required."}, status=400)















    offer_date = timezone.now().strftime("%Y-%m-%d")















    doc_filename = ""







    offer_file = request.FILES.get('document') or request.FILES.get('offer_document')







    if offer_file:







        try:







            from apps.accounts.auth_helpers import save_offer_letter_file







            doc_filename = save_offer_letter_file(offer_file) or ""







        except Exception as e:







            return JsonResponse({'status': 'error', 'message': f'Offer letter file error: {str(e)}'}, status=400)















    offer = JobOffer.objects.create(







        applicant=applicant,







        candidate_name=candidate_name,







        company_name=company_name,







        designation=designation or "Associate",







        offered_ctc=offered_ctc or "As per norms",







        offer_date=offer_date,







        joining_date=joining_date,







        status='Offer Sent',







        notes=notes,







        document=doc_filename







    )















    if applicant:







        from apps.candidates.status_helpers import set_applicant_status







        set_applicant_status(







            applicant,







            'Offer Released',







            changed_by='admin',







            notes=f"Offer letter issued by Admin for '{company_name}' as {designation}",







            force_override=True







        )















    log_activity(







        "candidate",







        "Offer Letter Generated",







        f"Admin generated job offer for {candidate_name} at {company_name}."







    )















    return JsonResponse({







        "status": "success",







        "message": f"Offer letter successfully issued for {candidate_name}!",







        "offer": offer.to_dict()







    })























@admin_required







def admin_mark_joined_api(request):







    """Admin marks candidate as Joined and creates/updates official Placement record."""







    if request.method != "POST":







        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)















    try:







        data = json.loads(request.body) if request.body else request.POST







    except Exception:







        data = request.POST















    raw_id = data.get('id') or data.get('raw_id') or data.get('applicant_id')







    model = (data.get('model') or "").strip().lower()







    ctc = data.get('package') or data.get('offered_ctc') or ""







    joining_date = data.get('joining_date') or timezone.now().strftime("%Y-%m-%d")







    notes = data.get('notes') or "Candidate joined confirmed by Admin."















    applicant = None







    candidate_name = (data.get('name') or data.get('candidate_name') or "").strip()







    company_name = (data.get('company_name') or "").strip()







    position = (data.get('position') or data.get('designation') or "").strip()















    if model == 'job_offer' or 'off-' in str(raw_id).lower() or 'offer' in str(raw_id).lower():







        clean_id = str(raw_id).replace('OFF-', '').replace('off-', '')







        offer = JobOffer.objects.filter(id=clean_id).first()







        if offer:







            offer.status = 'Joined'







            offer.save(update_fields=['status'])







            applicant = offer.applicant







            candidate_name = offer.candidate_name







            company_name = offer.company_name







            position = offer.designation







            ctc = ctc or offer.offered_ctc







            joining_date = joining_date or offer.joining_date







    elif model == 'placement' or 'plc-' in str(raw_id).lower():







        clean_id = str(raw_id).replace('PLC-', '').replace('plc-', '')







        placement = Placement.objects.filter(id=clean_id).first()







        if placement:







            placement.status = 'Joined'







            if ctc:







                placement.package = ctc







            if joining_date:







                placement.joining_date = joining_date







            placement.save()







            if placement.applicant:







                from apps.candidates.status_helpers import set_applicant_status







                set_applicant_status(placement.applicant, 'Joined', changed_by='admin', force_override=True)







            return JsonResponse({







                "status": "success",







                "message": f"Placement record for '{placement.candidate_name}' updated to Joined.",







                "placement": placement.to_dict()







            })







    else:







        clean_id = str(raw_id).replace('APP-', '').replace('app-', '')







        applicant = Applicant.objects.filter(id=clean_id).first()







        if applicant:







            candidate_name = applicant.full_name







            company_name = company_name or (applicant.job.company_name if applicant.job and getattr(applicant.job, 'company_name', None) else '') or (applicant.job.employer.company_name if applicant.job and getattr(applicant.job, 'employer', None) else '') or applicant.current_company or "Sky Vision Partner"







            position = position or applicant.job_title







            ctc = ctc or applicant.expected_salary or applicant.current_salary or "As per norms"















    if not candidate_name and applicant:







        candidate_name = applicant.full_name















    if not candidate_name:







        return JsonResponse({"status": "error", "message": "Candidate record not found."}, status=404)















    placement, created = Placement.objects.get_or_create(







        applicant=applicant,







        defaults={







            'candidate_name': candidate_name,







            'company_name': company_name or "Sky Vision Partner",







            'position': position or "Selected Role",







            'package': ctc or "As per norms",







            'placement_date': timezone.now().strftime("%Y-%m-%d"),







            'joining_date': joining_date,







            'status': 'Joined',







            'notes': notes







        }







    )







    if not created:







        placement.status = 'Joined'







        if ctc:







            placement.package = ctc







        if joining_date:







            placement.joining_date = joining_date







        placement.save()















    if applicant:







        from apps.candidates.status_helpers import set_applicant_status







        set_applicant_status(







            applicant,







            'Joined',







            changed_by='admin',







            notes=notes,







            force_override=True







        )







        JobOffer.objects.filter(applicant=applicant).update(status='Joined')







        Interview.objects.filter(applicant=applicant, status__in=['Scheduled', 'Rescheduled']).update(status='Completed', result='Selected')















    log_activity(







        "candidate",







        "Candidate Joined",







        f"Admin marked {candidate_name} as Joined at {company_name}."







    )















    return JsonResponse({







        "status": "success",







        "message": f"Candidate '{candidate_name}' successfully marked as Joined! Placement record confirmed.",







        "placement": placement.to_dict()







    })























@admin_required







def admin_website_management_view(request, sub_key='settings'):
    import json
    admin_id = request.session.get('admin_id')







    if not admin_id:







        return redirect('/admin-panel/login/')















    admin_user = AdminUser.objects.filter(id=admin_id).first()















    SECTIONS = [







        {







            'key': 'settings',







            'title': 'System Settings',







            'icon': 'ti-settings',







            'url': '/admin-panel/settings/general/',







            'subtitle': 'Manage system configuration, portal identity, branding, logos, SEO meta tags, and global settings.',







            'live_url': '/',







            'tag': 'System & Global'







        },







        {







            'key': 'header_footer',







            'title': 'Header & Footer',







            'icon': 'ti-layout-navbar',







            'url': '/admin-panel/website/header-footer/',







            'subtitle': 'Manage topbar helpline numbers, email addresses, primary menu items, and footer columns.',







            'live_url': '/',







            'tag': 'Navigation & Branding'







        },







        {







            'key': 'home',







            'title': 'Home Page',







            'icon': 'ti-home',







            'url': '/admin-panel/website/home/',







            'subtitle': 'Manage hero banner headlines, statistics counters, value propositions, and CTA sections.',







            'live_url': '/',







            'tag': 'Landing Page'







        },







        {







            'key': 'about',







            'title': 'About Us',







            'icon': 'ti-info-circle',







            'url': '/admin-panel/website/about/',







            'subtitle': 'Company background, mission, vision, core values, achievements, and journey timeline.',







            'live_url': '/about/',







            'tag': 'Company Profile'







        },







        {







            'key': 'services',







            'title': 'Services',







            'icon': 'ti-briefcase',







            'url': '/admin-panel/website/services/',







            'subtitle': 'Manage recruitment, staffing, payroll, internship, and manpower supply service offerings.',







            'live_url': '/services/',







            'tag': 'Business Solutions'







        },







        {
            'key': 'jobs',
            'title': 'Job Page Management',
            'icon': 'ti-briefcase',
            'url': '/admin-panel/website/job/',
            'subtitle': 'Manage hero banner, search bar, job types, categories, latest jobs, industries, locations, why choose us, commitment and CTA.',
            'live_url': '/job/',
            'tag': 'Job Portal'
        },







        {







            'key': 'careers',







            'title': 'Careers',







            'icon': 'ti-user-star',







            'url': '/admin-panel/website/careers/',







            'subtitle': 'Work culture highlights, benefits & perks, why work at Sky Vision, and job seeker banners.',







            'live_url': '/careers/',







            'tag': 'Work Culture'







        },







        {







            'key': 'blog',







            'title': 'Blog Management',







            'icon': 'ti-news',







            'url': '/admin-panel/website/blog/',







            'subtitle': 'Publish articles, recruitment insights, employment market trends, and industry tips.',







            'live_url': '/blog/',







            'tag': 'Articles & SEO'







        },







        {







            'key': 'gallery',







            'title': 'Gallery Management',







            'icon': 'ti-photo',







            'url': '/admin-panel/website/gallery/',







            'subtitle': 'Office gallery, celebration photos, campus placement events, and corporate activities.',







            'live_url': '/gallery/',







            'tag': 'Media Showcase'







        },







        {







            'key': 'contact',







            'title': 'Contact Information',







            'icon': 'ti-address-book',







            'url': '/admin-panel/website/contact/',







            'subtitle': 'Office locations, manager & HR phone numbers, email addresses, and Google Maps embed.',







            'live_url': '/contact/',







            'tag': 'Office & Helpline'







        },







    ]















    section_map = {s['key']: s for s in SECTIONS}







    # Handle alias if url passed with hyphen







    if sub_key == 'header-footer':







        sub_key = 'header_footer'







    elif sub_key in ('team-ceo', 'team_ceo'):







        return redirect('/admin-panel/website/about/?page=ceo')
    elif sub_key in ('jobs', 'job'):
        sub_key = 'jobs'







    elif sub_key in ('home-page', 'homepage'):







        sub_key = 'home'















    current_sec = section_map.get(sub_key, SECTIONS[0])















    if request.method == 'POST':







        from django.contrib import messages







        if sub_key == 'header_footer':







            success = handle_header_footer_save(request, admin_user)







            return redirect(request.path)







        elif sub_key == 'home':







            success = handle_home_page_save(request, admin_user)







            return redirect(request.path)







        elif sub_key == 'about':







            about_subpage = (request.POST.get('about_subpage') or request.GET.get('page') or 'company').strip().lower()







            if about_subpage not in ('company', 'ceo', 'team', 'journey'):







                about_subpage = 'company'







            success = handle_about_page_save(request, admin_user, about_subpage)







            return redirect(f"/admin-panel/website/about/?page={about_subpage}")







        elif sub_key == 'services':







            srv_subpage = (request.POST.get('service_page') or request.GET.get('page') or 'catalog').strip().lower()







            if srv_subpage == 'manpower_supply':







                handle_manpower_supply_save(request, admin_user)







            elif srv_subpage == 'recruitment_placement':







                handle_recruitment_placement_save(request, admin_user)







            elif srv_subpage == 'contract_staffing':







                handle_contract_staffing_save(request, admin_user)







                active_tab = (request.POST.get('active_tab') or '').strip().lower()







                if active_tab and active_tab != 'all':







                    return redirect(f"/admin-panel/website/services/?page={srv_subpage}&tab={active_tab}")







                return redirect(f"/admin-panel/website/services/?page={srv_subpage}")








            elif srv_subpage == 'educational_consultancy':







                handle_educational_consultancy_save(request, admin_user)







                active_tab = (request.POST.get('active_tab') or '').strip().lower()







                if active_tab and active_tab != 'all':







                    return redirect(f"/admin-panel/website/services/?page={srv_subpage}&tab={active_tab}")







                return redirect(f"/admin-panel/website/services/?page={srv_subpage}")







            elif srv_subpage == 'payroll_outsourcing':







                handle_payroll_outsourcing_save(request, admin_user)







                active_tab = (request.POST.get('active_tab') or '').strip().lower()







                if active_tab and active_tab != 'all':







                    return redirect(f"/admin-panel/website/services/?page={srv_subpage}&tab={active_tab}")







                return redirect(f"/admin-panel/website/services/?page={srv_subpage}")







            elif srv_subpage == 'hr_support':







                handle_hr_support_save(request, admin_user)







                active_tab = (request.POST.get('active_tab') or '').strip().lower()







                if active_tab and active_tab != 'all':







                    return redirect(f"/admin-panel/website/services/?page={srv_subpage}&tab={active_tab}")







                return redirect(f"/admin-panel/website/services/?page={srv_subpage}")







            elif srv_subpage == 'internship':

                handle_internship_save(request, admin_user)

                active_tab = (request.POST.get('active_tab') or '').strip().lower()

                if active_tab and active_tab != 'all':

                    return redirect(f"/admin-panel/website/services/?page={srv_subpage}&tab={active_tab}")

                return redirect(f"/admin-panel/website/services/?page={srv_subpage}")

            else:







                messages.success(request, "Service settings updated successfully!")







            return redirect(f"/admin-panel/website/services/?page={srv_subpage}")
        elif sub_key == 'jobs':
            handle_job_page_save(request, admin_user)
            active_tab = (request.POST.get('active_tab') or '').strip().lower()
            if active_tab and active_tab != 'all':
                return redirect(f"/admin-panel/website/job/?tab={active_tab}")
            return redirect("/admin-panel/website/job/")
        elif sub_key == 'careers':
            handle_careers_page_save(request, admin_user)
            active_tab = (request.POST.get('active_tab') or '').strip().lower()
            if active_tab and active_tab != 'all':
                return redirect(f"/admin-panel/website/careers/?tab={active_tab}")
            return redirect("/admin-panel/website/careers/")
        elif sub_key == 'blog':
            handle_blog_page_save(request, admin_user)
            active_tab = (request.POST.get('active_tab') or '').strip().lower()
            if active_tab and active_tab != 'all':
                return redirect(f"/admin-panel/website/blog/?tab={active_tab}")
            return redirect("/admin-panel/website/blog/")
        elif sub_key == 'gallery':
            handle_gallery_page_save(request, admin_user)
            active_tab = (request.POST.get('active_tab') or '').strip().lower()
            if active_tab and active_tab != 'all':
                return redirect(f"/admin-panel/website/gallery/?tab={active_tab}")
            return redirect("/admin-panel/website/gallery/")
        elif sub_key == 'contact':
            handle_contact_page_save(request, admin_user)
            active_tab = (request.POST.get('active_tab') or '').strip().lower()
            if active_tab and active_tab != 'all':
                return redirect(f"/admin-panel/website/contact/?tab={active_tab}")
            return redirect("/admin-panel/website/contact/")







        elif sub_key == 'settings':
            from apps.core.models import SiteSettings
            site = SiteSettings.get_settings()
            if 'site_name' in request.POST:
                site.site_name = request.POST.get('site_name', site.site_name).strip()
            if 'site_tagline' in request.POST:
                site.tagline = request.POST.get('site_tagline', site.tagline).strip()
            if 'logo_alt_text' in request.POST:
                site.logo_alt_text = request.POST.get('logo_alt_text', site.logo_alt_text).strip()
            if 'topbar_address' in request.POST:
                site.topbar_address = request.POST.get('topbar_address', site.topbar_address).strip()
            if 'support_email' in request.POST:
                site.support_email = request.POST.get('support_email', site.support_email).strip()
            if 'helpline_phone' in request.POST:
                site.helpline_phone = request.POST.get('helpline_phone', site.helpline_phone).strip()
            if 'secondary_phone' in request.POST:
                site.secondary_phone = request.POST.get('secondary_phone', site.secondary_phone).strip()
            if 'header_logo' in request.FILES:
                site.header_logo = request.FILES['header_logo']
            if 'favicon' in request.FILES:
                site.favicon = request.FILES['favicon']
            if 'footer_logo' in request.FILES:
                site.footer_logo = request.FILES['footer_logo']
            site.save()
            messages.success(request, 'System & Website Settings updated successfully!')
            return redirect(request.path)
        else:







            messages.success(request, f"{current_sec['title']} configuration updated successfully!")







            return redirect(request.path)















    context = {







        'admin_user': admin_user,







        'active_menu': 'settings' if (sub_key == 'settings' or request.path.startswith('/admin-panel/settings')) else 'website',







        'active_sub': sub_key,







        'sections_list': SECTIONS,







        'current_sec': current_sec,







        'page_title': f"{current_sec['title']} — Reports & Settings" if (sub_key == 'settings' or request.path.startswith('/admin-panel/settings')) else f"{current_sec['title']} — Website Management",







        'section_name': current_sec['title'],







        'module_title': 'Reports & Settings' if (sub_key == 'settings' or request.path.startswith('/admin-panel/settings')) else 'Website Management',







    }















    # Load Database Objects for Header & Footer







    if sub_key == 'header_footer':







        from apps.core.models import SiteSettings, NavItem, FooterColumn, SocialLink, FooterService







        site_settings = SiteSettings.get_settings()







        all_nav_items = list(







            NavItem.objects.filter(parent__isnull=True).prefetch_related('children').order_by('order', 'id')







        )







        all_footer_cols = list(







            FooterColumn.objects.prefetch_related('links').order_by('order', 'id')







        )







        all_socials = {s.platform: s for s in SocialLink.objects.all()}







        all_services = list(FooterService.objects.all().order_by('order', 'id'))















        # Prepare JSON structures for interactive JS builders







        nav_flat = []







        for r_item in all_nav_items:







            curr_idx = len(nav_flat)







            nav_flat.append({







                'label': r_item.label,







                'url': r_item.url,







                'active_key': r_item.active_key,







                'order': r_item.order,







                'is_visible': r_item.is_visible,







                'new_tab': r_item.new_tab,







                'parent_idx': None







            })







            for ch in r_item.children.all().order_by('order', 'id'):







                nav_flat.append({







                    'label': ch.label,







                    'url': ch.url,







                    'active_key': ch.active_key,







                    'order': ch.order,







                    'is_visible': ch.is_visible,







                    'new_tab': ch.new_tab,







                    'parent_idx': curr_idx







                })















        cols_init = []







        for col in all_footer_cols:







            cols_init.append({







                'title': col.title,







                'is_visible': col.is_visible,







                'links': [







                    {







                        'label': l.label,







                        'url': l.url,







                        'is_visible': l.is_visible,







                        'new_tab': l.new_tab







                    }







                    for l in col.links.all().order_by('order', 'id')







                ]







            })















        serv_init = [







            {







                'name': s.name,







                'url': s.url,







                'is_visible': s.is_visible







            }







            for s in all_services







        ]















        context.update({







            'site_settings': site_settings,







            'all_nav_items': all_nav_items,







            'all_footer_cols': all_footer_cols,







            'all_socials': all_socials,







            'all_services': all_services,







            'nav_items_json_init': json.dumps(nav_flat),







            'footer_cols_json_init': json.dumps(cols_init),







            'footer_services_json_init': json.dumps(serv_init),







        })















    # Load Database Objects for Home Page







    elif sub_key == 'home':







        from apps.core.models import (







            HomePageSettings,







            HeroStat,







            GrowthStep,







            HomeServiceCard,







            WhyChooseItem,







            HomeIndustryItem,







            InternshipCard,







            InternshipHighlight,







            FeaturedCandidate,







            GalleryImage,







            GalleryInfoBox,







        )







        home_settings = HomePageSettings.get_settings()







        all_hero_stats = list(HeroStat.objects.all().order_by('order', 'id'))







        all_growth_steps = list(GrowthStep.objects.all().order_by('order', 'step_number', 'id'))







        all_service_cards = list(HomeServiceCard.objects.all().order_by('order', 'id'))







        all_why_choose = list(WhyChooseItem.objects.all().order_by('order', 'id'))







        all_industry_items = list(HomeIndustryItem.objects.all().order_by('order', 'id'))







        all_internship_cards = list(InternshipCard.objects.all().order_by('order', 'id'))







        all_internship_benefits = list(InternshipHighlight.objects.filter(item_type='benefit').order_by('order', 'id'))







        all_internship_badges = list(InternshipHighlight.objects.filter(item_type='bottom_badge').order_by('order', 'id'))







        all_candidates = list(FeaturedCandidate.objects.all().order_by('order', 'id'))







        all_gallery_images = list(GalleryImage.objects.all().order_by('order', 'id'))







        all_gallery_info_boxes = list(GalleryInfoBox.objects.all().order_by('order', 'id'))















        context.update({







            'home_settings': home_settings,







            'all_hero_stats': all_hero_stats,







            'all_growth_steps': all_growth_steps,







            'all_service_cards': all_service_cards,







            'all_why_choose': all_why_choose,







            'all_industry_items': all_industry_items,







            'all_internship_cards': all_internship_cards,







            'all_internship_benefits': all_internship_benefits,







            'all_internship_badges': all_internship_badges,







            'all_candidates': all_candidates,







            'all_gallery_images': all_gallery_images,







            'all_gallery_info_boxes': all_gallery_info_boxes,







            'industries_items_json_init': json.dumps([







                {







                    'id': ind.id,







                    'name': ind.name,







                    'icon_class': ind.icon_class,







                    'link_url': ind.link_url,







                    'order': ind.order,







                    'is_visible': ind.is_visible,







                }







                for ind in all_industry_items







            ]),







            'hero_stats_json_init': json.dumps([







                {







                    'id': s.id,







                    'icon_class': s.icon_class,







                    'value': s.value,







                    'label': s.label,







                    'order': s.order,







                    'is_visible': s.is_visible,







                }







                for s in all_hero_stats







            ]),







            'growth_steps_json_init': json.dumps([







                {







                    'id': st.id,







                    'step_number': st.step_number,







                    'title': st.title,







                    'subtitle': st.subtitle,







                    'order': st.order,







                    'is_visible': st.is_visible,







                }







                for st in all_growth_steps







            ]),







            'service_cards_json_init': json.dumps([







                {







                    'id': sc.id,







                    'title': sc.title,







                    'icon_class': sc.icon_class,







                    'icon_color': sc.icon_color,







                    'bullets': sc.bullets,







                    'link_url': sc.link_url,







                    'link_text': sc.link_text,







                    'order': sc.order,







                    'is_visible': sc.is_visible,







                }







                for sc in all_service_cards







            ]),







            'why_choose_json_init': json.dumps([







                {







                    'id': w.id,







                    'title': w.title,







                    'icon_class': w.icon_class,







                    'description': w.description,







                    'order': w.order,







                    'is_visible': w.is_visible,







                }







                for w in all_why_choose







            ]),







            'internship_cards_json_init': json.dumps([







                {







                    'id': ic.id,







                    'domain_name': ic.domain_name,







                    'icon_class': ic.icon_class,







                    'icon_color': ic.icon_color,







                    'bullets': ic.bullets,







                    'order': ic.order,







                    'is_visible': ic.is_visible,







                }







                for ic in all_internship_cards







            ]),







            'internship_benefits_json_init': json.dumps([







                {







                    'id': ib.id,







                    'text': ib.text,







                    'order': ib.order,







                    'is_visible': ib.is_visible,







                }







                for ib in all_internship_benefits







            ]),







            'internship_badges_json_init': json.dumps([







                {







                    'id': bg.id,







                    'text': bg.text,







                    'icon_class': bg.icon_class,







                    'order': bg.order,







                    'is_visible': bg.is_visible,







                }







                for bg in all_internship_badges







            ]),







            'candidates_json_init': json.dumps([







                {







                    'id': c.id,







                    'name': c.name,







                    'role': c.role,







                    'experience': c.experience,







                    'avatar_color': c.avatar_color,







                    'company_placed': c.company_placed,







                    'show_publicly': c.show_publicly,







                    'order': c.order,







                    'is_visible': c.is_visible,







                }







                for c in all_candidates







            ]),







            'gallery_images_json_init': json.dumps([







                {







                    'id': g.id,







                    'title': g.title,







                    'static_image_path': g.static_image_path,







                    'image_url': g.get_image_url(),







                    'category': g.category,







                    'show_on_home': g.show_on_home,







                    'order': g.order,







                    'is_visible': g.is_visible,







                }







                for g in all_gallery_images







            ]),







            'gallery_info_boxes_json_init': json.dumps([







                {







                    'id': gb.id,







                    'title': gb.title,







                    'text': gb.text,







                    'icon_class': gb.icon_class,







                    'btn_label': gb.btn_label,







                    'btn_url': gb.btn_url,







                    'is_popup': gb.is_popup,







                    'order': gb.order,







                    'is_visible': gb.is_visible,







                }







                for gb in all_gallery_info_boxes







            ]),







        })















    # Load Database Objects for About Us sub-pages (4 pages)







    elif sub_key == 'about':







        from apps.core.models import (







            AboutCompanySettings,







            AboutIndustryItem,







            AboutWhyCard,







            AboutTestimonial,







            AboutTestimonialStat,







            AboutTrustPoint,







            AboutPartnerLogo,







            CEOMessageSettings,







            CEOLeadershipPrinciple,







            CEOStatBadge,







            OurTeamSettings,







            TeamMember,







            TeamFeatureHighlight,







            TeamStat,







            TeamDepartment,







            TeamTrustPoint,







            TeamCoreValue,







            OurJourneySettings,







            JourneyMilestone,







            JourneyStoryParagraph,







            JourneyStoryCard,







            JourneyMilestoneCard,







            JourneyImpactItem,







            JourneyStat,







            JourneyFutureGoal,







        )







        from apps.core.views import (







            seed_initial_ceo_principles,







            seed_initial_ceo_badges,







            seed_initial_team_members,







            seed_initial_journey_milestones,







            seed_initial_about_industries,







            seed_initial_team_highlights,







            seed_initial_team_values,







        )















        current_about_page = request.GET.get('page', 'company').strip().lower()







        if current_about_page not in ('company', 'ceo', 'team', 'journey'):







            current_about_page = 'company'















        if not AboutIndustryItem.objects.exists():







            seed_initial_about_industries()















        about_company = AboutCompanySettings.get_settings()







        all_about_industries = list(AboutIndustryItem.objects.all().order_by('order', 'id'))







        all_why_cards = list(AboutWhyCard.objects.all().order_by('order', 'id'))







        all_testimonial_stats = list(AboutTestimonialStat.objects.all().order_by('order', 'id'))







        all_candidate_testimonials = list(AboutTestimonial.objects.filter(testimonial_type='candidate').order_by('order', 'id'))







        all_employer_testimonials = list(AboutTestimonial.objects.filter(testimonial_type='employer').order_by('order', 'id'))







        all_partner_logos = list(AboutPartnerLogo.objects.all().order_by('order', 'id'))







        all_trust_points = list(AboutTrustPoint.objects.all().order_by('order', 'id'))















        ceo_message = CEOMessageSettings.get_settings()







        if not CEOLeadershipPrinciple.objects.exists():







            seed_initial_ceo_principles()







        all_principles = list(CEOLeadershipPrinciple.objects.all().order_by('order', 'id'))















        if not CEOStatBadge.objects.exists():







            seed_initial_ceo_badges()







        all_ceo_stat_badges = list(CEOStatBadge.objects.all().order_by('order', 'id'))























        team_settings = OurTeamSettings.get_settings()







        if not TeamMember.objects.exists():







            seed_initial_team_members()







        all_team_members = list(TeamMember.objects.all().order_by('order', 'id'))







        if not TeamFeatureHighlight.objects.exists():







            seed_initial_team_highlights()







        all_team_highlights = list(TeamFeatureHighlight.objects.all().order_by('order', 'id'))







        all_team_stats = list(TeamStat.objects.all().order_by('order', 'id'))







        all_team_departments = list(TeamDepartment.objects.all().order_by('order', 'id'))







        all_team_trust_points = list(TeamTrustPoint.objects.all().order_by('order', 'id'))







        if not TeamCoreValue.objects.exists():







            seed_initial_team_values()







        all_team_values = list(TeamCoreValue.objects.all().order_by('order', 'id'))















        journey_settings = OurJourneySettings.get_settings()







        if not JourneyMilestone.objects.exists():







            seed_initial_journey_milestones()







        all_milestones = list(JourneyMilestone.objects.all().order_by('order', 'id'))







        all_journey_paragraphs = list(JourneyStoryParagraph.objects.all().order_by('order', 'id'))







        all_journey_story_cards = list(JourneyStoryCard.objects.all().order_by('order', 'id'))







        all_journey_milestone_cards = list(JourneyMilestoneCard.objects.all().order_by('order', 'id'))







        all_journey_impact_items = list(JourneyImpactItem.objects.all().order_by('order', 'id'))







        all_journey_stats = list(JourneyStat.objects.all().order_by('order', 'id'))







        all_journey_future_goals = list(JourneyFutureGoal.objects.all().order_by('order', 'id'))















        about_pages_list = [







            {'key': 'company', 'label': 'About Company', 'icon': 'ti-building', 'live_url': '/about/', 'tag': 'Company Profile', 'subtitle': 'Company overview, vision, mission statements, statistics counters, and core pillars.'},







            {'key': 'ceo', 'label': 'CEO & Founder', 'icon': 'ti-user-star', 'live_url': '/about/ceo/', 'tag': 'Executive Message', 'subtitle': 'CEO portrait, desk message, vision & mission, leadership principles, and quote.'},







            {'key': 'team', 'label': 'Our Team', 'icon': 'ti-users', 'live_url': '/about/team/', 'tag': 'Our Experts', 'subtitle': 'Team hero banner, leadership management, and recruitment specialist members.'},







            {'key': 'journey', 'label': 'Journey', 'icon': 'ti-rocket', 'live_url': '/about/journey/', 'tag': 'Our Evolution', 'subtitle': 'Hero overview, milestone stats, founding story, and chronological growth timeline.'},







        ]















        cur_p = next((p for p in about_pages_list if p['key'] == current_about_page), about_pages_list[0])







        current_sec['title'] = cur_p['label']







        current_sec['page_heading'] = cur_p['label']







        current_sec['live_url'] = cur_p['live_url']







        current_sec['subtitle'] = cur_p['subtitle']







        current_sec['tag'] = cur_p['tag']







        current_sec['icon'] = cur_p['icon']







        context['section_name'] = f"About Us / {cur_p['label']}"







        context['page_title'] = f"{cur_p['label']} — About Us — Website Management"















        context.update({







            'current_about_page': current_about_page,







            'about_pages_list': about_pages_list,







            'about_company': about_company,







            'all_about_industries': all_about_industries,







            'all_why_cards': all_why_cards,







            'all_testimonial_stats': all_testimonial_stats,







            'all_candidate_testimonials': all_candidate_testimonials,







            'all_employer_testimonials': all_employer_testimonials,







            'all_partner_logos': all_partner_logos,







            'all_trust_points': all_trust_points,







            'about_industries_json_init': json.dumps([







                {







                    'id': ind.id,







                    'name': ind.name,







                    'icon_class': ind.icon_class,







                    'link_url': ind.link_url,







                    'order': ind.order,







                    'is_visible': ind.is_visible,







                }







                for ind in all_about_industries







            ]),







            'why_cards_json_init': json.dumps([







                {







                    'id': w.id,







                    'icon_class': w.icon_class,







                    'title': w.title,







                    'description': w.description,







                    'order': w.order,







                    'is_visible': w.is_visible,







                }







                for w in all_why_cards







            ]),







            'testimonial_stats_json_init': json.dumps([







                {







                    'id': s.id,







                    'icon_class': s.icon_class,







                    'color': s.color,







                    'count': s.count,







                    'suffix': s.suffix,







                    'label': s.label,







                    'order': s.order,







                    'is_visible': s.is_visible,







                }







                for s in all_testimonial_stats







            ]),







            'candidate_testimonials_json_init': json.dumps([







                {







                    'id': t.id,







                    'name': t.name,







                    'role': t.role,







                    'location': t.location,







                    'company': t.company,







                    'quote': t.quote,







                    'rating': t.rating,







                    'badge_text': t.badge_text,







                    'avatar_style': t.avatar_style,







                    'photo_url': t.photo.url if t.photo else '',







                    'order': t.order,







                    'is_visible': t.is_visible,







                }







                for t in all_candidate_testimonials







            ]),







            'employer_testimonials_json_init': json.dumps([







                {







                    'id': t.id,







                    'name': t.name,







                    'role': t.role,







                    'location': t.location,







                    'company': t.company,







                    'quote': t.quote,







                    'rating': t.rating,







                    'badge_text': t.badge_text,







                    'avatar_style': t.avatar_style,







                    'photo_url': t.photo.url if t.photo else '',







                    'order': t.order,







                    'is_visible': t.is_visible,







                }







                for t in all_employer_testimonials







            ]),







            'partner_logos_json_init': json.dumps([







                {







                    'id': l.id,







                    'name': l.name,







                    'icon_class': l.icon_class,







                    'logo_image_url': l.logo_image.url if l.logo_image else '',







                    'order': l.order,







                    'is_visible': l.is_visible,







                }







                for l in all_partner_logos







            ]),







            'trust_points_json_init': json.dumps([







                {







                    'id': tp.id,







                    'icon_class': tp.icon_class,







                    'title': tp.title,







                    'text': tp.text,







                    'order': tp.order,







                    'is_visible': tp.is_visible,







                }







                for tp in all_trust_points







            ]),







            'ceo_message': ceo_message,







            'all_principles': all_principles,







            'all_ceo_stat_badges': all_ceo_stat_badges,







            'ceo_stat_badges_json_init': json.dumps([







                {







                    'id': b.id,







                    'value': b.value,







                    'label': b.label,







                    'icon_class': b.icon_class,







                    'order': b.order,







                    'is_visible': b.is_visible,







                }







                for b in all_ceo_stat_badges







            ]),







            'team_settings': team_settings,







            'all_team_members': all_team_members,







            'leadership_members': [m for m in all_team_members if m.category == 'leadership'],







            'specialist_members': [m for m in all_team_members if m.category == 'specialist'],







            'all_team_highlights': all_team_highlights,







            'all_team_stats': all_team_stats,







            'all_team_departments': all_team_departments,







            'all_team_trust_points': all_team_trust_points,







            'all_team_values': all_team_values,







            'team_highlights_json_init': json.dumps([







                {







                    'id': h.id,







                    'title': h.title,







                    'description': h.description,







                    'icon': h.icon,







                    'icon_class': h.icon,







                    'order': h.order,







                    'is_visible': h.is_visible,







                }







                for h in all_team_highlights







            ]),







            'team_stats_json_init': json.dumps([







                {







                    'id': s.id,







                    'count': s.count,







                    'suffix': s.suffix,







                    'label': s.label,







                    'static_text': s.static_text,







                    'icon': s.icon,







                    'icon_class': s.icon,







                    'order': s.order,







                    'is_visible': s.is_visible,







                }







                for s in all_team_stats







            ]),







            'team_departments_json_init': json.dumps([







                {







                    'id': d.id,







                    'name': d.name,







                    'icon': d.icon,







                    'icon_class': d.icon,







                    'description': d.description,







                    'image_url': d.get_image_url(),







                    'team_size': d.team_size,







                    'count_badge': d.description or d.team_size,







                    'order': d.order,







                    'is_visible': d.is_visible,







                }







                for d in all_team_departments







            ]),







            'team_trust_points_json_init': json.dumps([







                {







                    'id': tp.id,







                    'title': tp.title,







                    'text': tp.title,







                    'icon_class': tp.icon_class,







                    'order': tp.order,







                    'is_visible': tp.is_visible,







                }







                for tp in all_team_trust_points







            ]),







            'team_values_json_init': json.dumps([







                {







                    'id': v.id,







                    'title': v.title,







                    'description': v.description,







                    'icon': v.icon,







                    'icon_class': v.icon,







                    'order': v.order,







                    'is_visible': v.is_visible,







                }







                for v in all_team_values







            ]),







            'team_core_values_json_init': json.dumps([







                {







                    'id': v.id,







                    'title': v.title,







                    'description': v.description,







                    'icon': v.icon,







                    'icon_class': v.icon,







                    'order': v.order,







                    'is_visible': v.is_visible,







                }







                for v in all_team_values







            ]),







            'journey_settings': journey_settings,







            'all_milestones': all_milestones,







            'principles_json_init': json.dumps([







                {







                    'id': p.id,







                    'title': p.title,







                    'description': p.description,







                    'icon_class': p.icon_class,







                    'order': p.order,







                    'is_visible': p.is_visible,







                }







                for p in all_principles







            ]),







            'team_members_json_init': json.dumps([







                {







                    'id': m.id,







                    'name': m.name,







                    'role': m.role,







                    'category': m.category,







                    'bio': m.bio,







                    'experience_text': m.experience_text,







                    'photo_url': m.get_photo_url(),







                    'static_photo_path': m.static_photo_path,







                    'linkedin_url': m.linkedin_url,







                    'email_url': m.email_url,







                    'show_on_about_page': m.show_on_about_page,







                    'about_page_order': m.about_page_order,







                    'order': m.order,







                    'is_visible': m.is_visible,







                }







                for m in all_team_members







            ]),







            'all_journey_paragraphs': all_journey_paragraphs,







            'all_journey_story_cards': all_journey_story_cards,







            'all_journey_milestone_cards': all_journey_milestone_cards,







            'all_journey_impact_items': all_journey_impact_items,







            'all_journey_stats': all_journey_stats,







            'all_journey_future_goals': all_journey_future_goals,







            'journey_paragraphs_json_init': json.dumps([







                {







                    'id': p.id,







                    'text': p.text,







                    'paragraph_text': p.text,







                    'order': p.order,







                    'is_visible': p.is_visible,







                }







                for p in all_journey_paragraphs







            ]),







            'journey_story_cards_json_init': json.dumps([







                {







                    'id': c.id,







                    'title': c.title,







                    'description': c.description,







                    'icon': c.icon,







                    'color': c.color,







                    'order': c.order,







                    'is_visible': c.is_visible,







                }







                for c in all_journey_story_cards







            ]),







            'milestones_json_init': json.dumps([







                {







                    'id': ms.id,







                    'year': ms.year,







                    'title': ms.title,







                    'description': ms.description,







                    'badge_label': ms.badge_label,







                    'icon_class': ms.icon_class,







                    'order': ms.order,







                    'is_visible': ms.is_visible,







                }







                for ms in all_milestones







            ]),







            'journey_timeline_json_init': json.dumps([







                {







                    'id': ms.id,







                    'year': ms.year,







                    'title': ms.title,







                    'description': ms.description,







                    'badge_label': ms.badge_label,







                    'icon_class': ms.icon_class,







                    'order': ms.order,







                    'is_visible': ms.is_visible,







                }







                for ms in all_milestones







            ]),







            'journey_milestone_cards_json_init': json.dumps([







                {







                    'id': mc.id,







                    'year': mc.year,







                    'title': mc.title,







                    'description': mc.description,







                    'icon_class': mc.icon_class,







                    'order': mc.order,







                    'is_visible': mc.is_visible,







                }







                for mc in all_journey_milestone_cards







            ]),







            'journey_impact_items_json_init': json.dumps([







                {







                    'id': it.id,







                    'title': it.title,







                    'description': it.description,







                    'icon': it.icon,







                    'order': it.order,







                    'is_visible': it.is_visible,







                }







                for it in all_journey_impact_items







            ]),







            'journey_stats_json_init': json.dumps([







                {







                    'id': st.id,







                    'count': st.count,







                    'suffix': st.suffix,







                    'label': st.label,







                    'icon': st.icon,







                    'order': st.order,







                    'is_visible': st.is_visible,







                }







                for st in all_journey_stats







            ]),







            'journey_future_goals_json_init': json.dumps([







                {







                    'id': fg.id,







                    'text': fg.text,







                    'icon': fg.icon,







                    'order': fg.order,







                    'is_visible': fg.is_visible,







                }







                for fg in all_journey_future_goals







            ]),







        })















    if sub_key == 'services':







        services_pages_list = [







            {







                'key': 'catalog',







                'label': 'All Services (Catalog)',







                'short_label': 'All Services',







                'icon': 'ti-grid-dots',







                'live_url': '/services/',







                'tag': 'Services Directory',







                'subtitle': 'Manage recruitment, staffing, payroll, internship, and manpower supply service offerings.',







                'features': ['7 Active Core Services', 'Navbar Dropdown Integrated', 'Interactive Cards', 'Service Inquiries Hooked'],







                'color': '#2563eb',







            },







            {







                'key': 'manpower_supply',







                'label': 'Manpower Supply',







                'short_label': 'Manpower Supply',







                'icon': 'ti-users',







                'live_url': '/services/manpower-supply/',







                'tag': 'Workforce Solutions',







                'subtitle': 'Skilled, semi-skilled, and technical workforce deployment across industrial and commercial sectors.',







                'features': ['Skilled Manpower', 'Unskilled Manpower', 'Industrial Workforce', 'Factory Staff', 'Office Staff'],







                'color': '#2563eb',







                'order_num': '01',







            },







            {







                'key': 'recruitment_placement',







                'label': 'Recruitment & Placement',







                'short_label': 'Recruitment & Placement',







                'icon': 'ti-search',







                'live_url': '/services/recruitment-placement/',







                'tag': 'Talent Acquisition',







                'subtitle': 'End-to-end recruitment, executive search, candidate screening, and permanent placements.',







                'features': ['Permanent Hiring', 'Executive Hiring', 'Bulk Hiring', 'Campus Recruitment', 'Overseas Recruitment'],







                'color': '#dc2626',







                'order_num': '02',







            },







            {







                'key': 'contract_staffing',







                'label': 'Contract Staffing',







                'short_label': 'Contract Staffing',







                'icon': 'ti-user-check',







                'live_url': '/services/contract-staffing/',







                'tag': 'Flexible Staffing',







                'subtitle': 'Flexible and agile contract staffing models for short-term and project-based demands.',







                'features': ['Temporary Staffing', 'Project Staffing', 'Seasonal Workforce', 'Third Party Payroll'],







                'color': '#0284c7',







                'order_num': '03',







            },







            {







                'key': 'educational_consultancy',







                'label': 'Educational Consultancy',







                'short_label': 'Educational Consultancy',







                'icon': 'ti-school',







                'live_url': '/services/educational-consultancy/',







                'tag': 'Education & Advisory',







                'subtitle': 'College admissions, student counseling, career guidance, and academic path advisory.',







                'features': ['Admission Guidance', 'College Selection', 'Career Planning', 'Skill Development'],







                'color': '#ea580c',







                'order_num': '04',







            },







            {







                'key': 'payroll_outsourcing',







                'label': 'Payroll & Outsourcing',







                'short_label': 'Payroll & Outsourcing',







                'icon': 'ti-calculator',







                'live_url': '/services/payroll-outsourcing/',







                'tag': 'Payroll & Compliance',







                'subtitle': 'Accurate payroll processing, statutory compliance (PF, ESIC, TDS), and salary management.',







                'features': ['Salary Processing', 'Attendance Management', 'PF & ESI Management', 'Compliance Management'],







                'color': '#16a34a',







                'order_num': '05',







            },







            {







                'key': 'hr_support',







                'label': 'HR Support',







                'short_label': 'HR Support',







                'icon': 'ti-headset',







                'live_url': '/services/hr-support/',







                'tag': 'HR Operations',







                'subtitle': 'Complete HR management, workplace policies, onboarding systems, and HR advisory.',







                'features': ['HR Policies', 'Employee Engagement', 'Performance Management', 'HR Documentation'],







                'color': '#9333ea',







                'order_num': '06',







            },







            {







                'key': 'internship',







                'label': 'Internship Programme',







                'short_label': 'Internship Programme',







                'icon': 'ti-award',







                'live_url': '/services/internship/',







                'tag': 'Internship & Training',







                'subtitle': 'Industry-oriented internship programs, live project training, and career skill development.',







                'features': ['HR Internship', 'Finance Internship', 'Marketing Internship', 'IT Internship', 'Digital Marketing Internship'],







                'color': '#0d9488',







                'order_num': '07',







            },

        ]















        current_services_page = request.GET.get('page', 'catalog').strip().lower()







        if current_services_page == 'career_counselling':

            return redirect('/admin-panel/website/careers/')

        valid_keys = [p['key'] for p in services_pages_list]







        if current_services_page not in valid_keys:







            current_services_page = 'catalog'















        cur_srv = next((s for s in services_pages_list if s['key'] == current_services_page), services_pages_list[0])







        current_sec = dict(current_sec)







        current_sec['title'] = cur_srv['label']







        current_sec['page_heading'] = cur_srv['label']







        current_sec['live_url'] = cur_srv['live_url']







        current_sec['subtitle'] = cur_srv['subtitle']







        current_sec['tag'] = cur_srv['tag']







        current_sec['icon'] = cur_srv['icon']







        context['current_sec'] = current_sec







        context['section_name'] = f"Services / {cur_srv['label']}"







        context['page_title'] = f"{cur_srv['label']} — Services — Website Management"















        context.update({







            'current_services_page': current_services_page,







            'services_pages_list': services_pages_list,







            'current_service_meta': cur_srv,







            'eight_services_only': [s for s in services_pages_list if s['key'] != 'catalog'],







        })















        if current_services_page == 'manpower_supply':







            from apps.core.models import (







                ManpowerSupplySettings,







                ManpowerChecklistItem,







                ManpowerServiceCard,







                ManpowerIndustryItem,







                ManpowerWhyChooseItem,







                ManpowerProcessStep,







                ManpowerStatItem,







                ManpowerFaqItem,







                ManpowerTrustItem,







            )







            from apps.core.views import seed_initial_manpower_supply_data















            if not ManpowerServiceCard.objects.exists():







                seed_initial_manpower_supply_data()















            ms_settings = ManpowerSupplySettings.get_settings()







            all_ms_checklist = list(ManpowerChecklistItem.objects.all().order_by('order', 'id'))







            all_ms_services = list(ManpowerServiceCard.objects.all().order_by('order', 'id'))







            all_ms_industries = list(ManpowerIndustryItem.objects.all().order_by('order', 'id'))







            all_ms_why_choose = list(ManpowerWhyChooseItem.objects.all().order_by('order', 'id'))







            all_ms_process = list(ManpowerProcessStep.objects.all().order_by('order', 'id'))







            all_ms_stats = list(ManpowerStatItem.objects.all().order_by('order', 'id'))







            all_ms_faqs = list(ManpowerFaqItem.objects.all().order_by('order', 'id'))







            all_ms_trust = list(ManpowerTrustItem.objects.all().order_by('order', 'id'))















            context.update({







                'ms_settings': ms_settings,







                'all_ms_checklist': all_ms_checklist,







                'all_ms_services': all_ms_services,







                'all_ms_industries': all_ms_industries,







                'all_ms_why_choose': all_ms_why_choose,







                'all_ms_process': all_ms_process,







                'all_ms_stats': all_ms_stats,







                'all_ms_faqs': all_ms_faqs,







                'all_ms_trust': all_ms_trust,







                'ms_checklist_json_init': json.dumps([







                    {'id': c.id, 'text': c.text, 'icon_class': c.icon_class, 'order': c.order, 'is_visible': c.is_visible}







                    for c in all_ms_checklist







                ]),







                'ms_services_json_init': json.dumps([







                    {'id': s.id, 'title': s.title, 'description': s.description, 'icon_class': s.icon_class, 'color_class': s.color_class, 'order': s.order, 'is_visible': s.is_visible}







                    for s in all_ms_services







                ]),







                'ms_industries_json_init': json.dumps([







                    {'id': i.id, 'name': i.name, 'icon_class': i.icon_class, 'order': i.order, 'is_visible': i.is_visible}







                    for i in all_ms_industries







                ]),







                'ms_why_choose_json_init': json.dumps([







                    {'id': w.id, 'title': w.title, 'icon_class': w.icon_class, 'order': w.order, 'is_visible': w.is_visible}







                    for w in all_ms_why_choose







                ]),







                'ms_process_json_init': json.dumps([







                    {'id': p.id, 'step_number': p.step_number, 'title': p.title, 'icon_class': p.icon_class, 'order': p.order, 'is_visible': p.is_visible}







                    for p in all_ms_process







                ]),







                'ms_stats_json_init': json.dumps([







                    {'id': st.id, 'value': st.value, 'label': st.label, 'icon_class': st.icon_class, 'order': st.order, 'is_visible': st.is_visible}







                    for st in all_ms_stats







                ]),







                'ms_faqs_json_init': json.dumps([







                    {'id': f.id, 'question': f.question, 'answer': f.answer, 'order': f.order, 'is_visible': f.is_visible}







                    for f in all_ms_faqs







                ]),







                'ms_trust_json_init': json.dumps([







                    {'id': tr.id, 'line1': tr.line1, 'line2': tr.line2, 'icon_class': tr.icon_class, 'order': tr.order, 'is_visible': tr.is_visible}







                    for tr in all_ms_trust







                ]),







            })















        elif current_services_page == 'recruitment_placement':







            from apps.core.models import (







                RecruitmentPlacementSettings,







                RpWhyPartnerItem,







                RpServiceCard,







                RpProcessStep,







                RpWhyChooseItem,







                RpIndustryItem,







                RpPartnerItem,







                RpFaqItem,







            )







            from apps.core.views import seed_initial_recruitment_placement_data















            if not RpServiceCard.objects.exists():







                seed_initial_recruitment_placement_data()















            rp_settings = RecruitmentPlacementSettings.get_settings()







            all_rp_why_partner = list(RpWhyPartnerItem.objects.all().order_by('order', 'id'))







            all_rp_services = list(RpServiceCard.objects.all().order_by('order', 'id'))







            all_rp_process = list(RpProcessStep.objects.all().order_by('order', 'id'))







            all_rp_why_choose = list(RpWhyChooseItem.objects.all().order_by('order', 'id'))







            all_rp_industries = list(RpIndustryItem.objects.all().order_by('order', 'id'))







            all_rp_partners = list(RpPartnerItem.objects.all().order_by('order', 'id'))







            all_rp_faqs = list(RpFaqItem.objects.all().order_by('order', 'id'))















            context.update({







                'rp_settings': rp_settings,







                'all_rp_why_partner': all_rp_why_partner,







                'all_rp_services': all_rp_services,







                'all_rp_process': all_rp_process,







                'all_rp_why_choose': all_rp_why_choose,







                'all_rp_industries': all_rp_industries,







                'all_rp_partners': all_rp_partners,







                'all_rp_faqs': all_rp_faqs,







                'rp_why_partner_json_init': json.dumps([







                    {'id': w.id, 'text': w.text, 'icon_class': w.icon_class, 'order': w.order, 'is_visible': w.is_visible}







                    for w in all_rp_why_partner







                ]),







                'rp_services_json_init': json.dumps([







                    {'id': s.id, 'title': s.title, 'description': s.description, 'icon_class': s.icon_class, 'color_class': s.color_class, 'order': s.order, 'is_visible': s.is_visible}







                    for s in all_rp_services







                ]),







                'rp_process_json_init': json.dumps([







                    {'id': p.id, 'step_number': p.step_number, 'title': p.title, 'icon_class': p.icon_class, 'order': p.order, 'is_visible': p.is_visible}







                    for p in all_rp_process







                ]),







                'rp_why_choose_json_init': json.dumps([







                    {'id': w.id, 'text': w.text, 'icon_class': w.icon_class, 'order': w.order, 'is_visible': w.is_visible}







                    for w in all_rp_why_choose







                ]),







                'rp_industries_json_init': json.dumps([







                    {'id': i.id, 'name': i.name, 'icon_class': i.icon_class, 'order': i.order, 'is_visible': i.is_visible}







                    for i in all_rp_industries







                ]),







                'rp_partners_json_init': json.dumps([







                    {'id': p.id, 'name': p.name, 'order': p.order, 'is_visible': p.is_visible}







                    for p in all_rp_partners







                ]),







                'rp_faqs_json_init': json.dumps([







                    {'id': f.id, 'question': f.question, 'answer': f.answer, 'order': f.order, 'is_visible': f.is_visible}







                    for f in all_rp_faqs







                ]),







            })















        elif current_services_page == 'contract_staffing':







            from apps.core.models import (







                ContractStaffingSettings,







                CsServiceCard,







                CsIndustryItem,







                CsWhyChooseItem,







                CsProcessStep,







                CsBenefitEmployerItem,







                CsBenefitCandidateItem,







                CsFaqItem,







            )







            from apps.core.views import seed_initial_contract_staffing_data















            if not CsServiceCard.objects.exists():







                seed_initial_contract_staffing_data()















            cs_settings = ContractStaffingSettings.get_settings()







            all_cs_services = list(CsServiceCard.objects.all().order_by('order', 'id'))







            all_cs_industries = list(CsIndustryItem.objects.all().order_by('order', 'id'))







            all_cs_why_choose = list(CsWhyChooseItem.objects.all().order_by('order', 'id'))







            all_cs_process = list(CsProcessStep.objects.all().order_by('order', 'id'))







            all_cs_employer_benefits = list(CsBenefitEmployerItem.objects.all().order_by('order', 'id'))







            all_cs_candidate_benefits = list(CsBenefitCandidateItem.objects.all().order_by('order', 'id'))







            all_cs_faqs = list(CsFaqItem.objects.all().order_by('order', 'id'))















            context.update({







                'cs_settings': cs_settings,







                'all_cs_services': all_cs_services,







                'all_cs_industries': all_cs_industries,







                'all_cs_why_choose': all_cs_why_choose,







                'all_cs_process': all_cs_process,







                'all_cs_employer_benefits': all_cs_employer_benefits,







                'all_cs_candidate_benefits': all_cs_candidate_benefits,







                'all_cs_faqs': all_cs_faqs,







                'cs_services_json_init': json.dumps([







                    {'id': s.id, 'title': s.title, 'description': s.description, 'icon_class': s.icon_class, 'order': s.order, 'is_visible': s.is_visible}







                    for s in all_cs_services







                ]),







                'cs_industries_json_init': json.dumps([







                    {'id': i.id, 'name': i.name, 'icon_class': i.icon_class, 'order': i.order, 'is_visible': i.is_visible}







                    for i in all_cs_industries







                ]),







                'cs_why_choose_json_init': json.dumps([







                    {'id': w.id, 'text': w.text, 'icon_class': w.icon_class, 'order': w.order, 'is_visible': w.is_visible}







                    for w in all_cs_why_choose







                ]),







                'cs_process_json_init': json.dumps([







                    {'id': p.id, 'step_number': p.step_number, 'title': p.title, 'description': p.description, 'icon_class': p.icon_class, 'order': p.order, 'is_visible': p.is_visible}







                    for p in all_cs_process







                ]),







                'cs_employer_benefits_json_init': json.dumps([







                    {'id': b.id, 'text': b.text, 'icon_class': b.icon_class, 'order': b.order, 'is_visible': b.is_visible}







                    for b in all_cs_employer_benefits







                ]),







                'cs_candidate_benefits_json_init': json.dumps([







                    {'id': b.id, 'text': b.text, 'icon_class': b.icon_class, 'order': b.order, 'is_visible': b.is_visible}







                    for b in all_cs_candidate_benefits







                ]),







                'cs_faqs_json_init': json.dumps([







                    {'id': f.id, 'question': f.question, 'answer': f.answer, 'order': f.order, 'is_visible': f.is_visible}







                    for f in all_cs_faqs







                ]),







            })















        elif current_services_page == 'educational_consultancy':







            from apps.core.models import (







                EducationalConsultancySettings,







                EcServiceCard,







                EcWhyChooseItem,







                EcProcessStep,







            )







            from apps.core.views import seed_initial_educational_consultancy_data















            if not EcServiceCard.objects.exists():







                seed_initial_educational_consultancy_data()















            ec_settings = EducationalConsultancySettings.get_settings()







            all_ec_services = list(EcServiceCard.objects.all().order_by('order', 'id'))







            all_ec_why_choose = list(EcWhyChooseItem.objects.all().order_by('order', 'id'))







            all_ec_process = list(EcProcessStep.objects.all().order_by('order', 'id'))















            context.update({







                'ec_settings': ec_settings,







                'all_ec_services': all_ec_services,







                'all_ec_why_choose': all_ec_why_choose,







                'all_ec_process': all_ec_process,







                'ec_services_json_init': json.dumps([







                    {'id': s.id, 'title': s.title, 'description': s.description, 'icon_class': s.icon_class, 'badge_theme': s.badge_theme, 'order': s.order, 'is_visible': s.is_visible}







                    for s in all_ec_services







                ]),







                'ec_why_choose_json_init': json.dumps([







                    {'id': w.id, 'title': w.title, 'description': w.description, 'icon_class': w.icon_class, 'order': w.order, 'is_visible': w.is_visible}







                    for w in all_ec_why_choose







                ]),







                'ec_process_json_init': json.dumps([







                    {'id': p.id, 'step_number': p.step_number, 'title': p.title, 'description': p.description, 'icon_class': p.icon_class, 'order': p.order, 'is_visible': p.is_visible}







                    for p in all_ec_process







                ]),







            })















        elif current_services_page == 'hr_support':







            from apps.core.models import (



                HrSupportSettings,



                HrFeatureItem,



                HrServiceCard,



                HrAdditionalServiceItem,



                HrWhyChooseItem,



                HrProcessStep,



                HrEmployerBenefit,



                HrEmployeeBenefit,



            )







            hr_settings = HrSupportSettings.get_settings()



            all_hr_features = list(HrFeatureItem.objects.all().order_by('order', 'id'))



            all_hr_services = list(HrServiceCard.objects.all().order_by('order', 'id'))



            all_hr_additional = list(HrAdditionalServiceItem.objects.all().order_by('order', 'id'))



            all_hr_why_choose = list(HrWhyChooseItem.objects.all().order_by('order', 'id'))



            all_hr_process = list(HrProcessStep.objects.all().order_by('order', 'id'))



            all_hr_employer_benefits = list(HrEmployerBenefit.objects.all().order_by('order', 'id'))



            all_hr_employee_benefits = list(HrEmployeeBenefit.objects.all().order_by('order', 'id'))







            context.update({



                'hr_settings': hr_settings,



                'all_hr_features': all_hr_features,



                'all_hr_services': all_hr_services,



                'all_hr_additional': all_hr_additional,



                'all_hr_why_choose': all_hr_why_choose,



                'all_hr_process': all_hr_process,



                'all_hr_employer_benefits': all_hr_employer_benefits,



                'all_hr_employee_benefits': all_hr_employee_benefits,



                'hr_features_json_init': json.dumps([



                    {'id': f.id, 'title': f.title, 'icon_class': f.icon_class, 'order': f.order, 'is_visible': f.is_visible}



                    for f in all_hr_features



                ]),



                'hr_services_json_init': json.dumps([



                    {'id': s.id, 'title': s.title, 'description': s.description, 'icon_class': s.icon_class, 'order': s.order, 'is_visible': s.is_visible}



                    for s in all_hr_services



                ]),



                'hr_additional_json_init': json.dumps([



                    {'id': a.id, 'title': a.title, 'icon_class': a.icon_class, 'order': a.order, 'is_visible': a.is_visible}



                    for a in all_hr_additional



                ]),



                'hr_why_choose_json_init': json.dumps([



                    {'id': w.id, 'title': w.title, 'order': w.order, 'is_visible': w.is_visible}



                    for w in all_hr_why_choose



                ]),



                'hr_process_json_init': json.dumps([



                    {'id': p.id, 'step_number': p.step_number, 'title': p.title, 'icon_class': p.icon_class, 'order': p.order, 'is_visible': p.is_visible}



                    for p in all_hr_process



                ]),



                'hr_employer_benefits_json_init': json.dumps([



                    {'id': b.id, 'title': b.title, 'order': b.order, 'is_visible': b.is_visible}



                    for b in all_hr_employer_benefits



                ]),



                'hr_employee_benefits_json_init': json.dumps([



                    {'id': b.id, 'title': b.title, 'order': b.order, 'is_visible': b.is_visible}



                    for b in all_hr_employee_benefits



                ]),



            })







        elif current_services_page == 'internship':

            from apps.core.models import (

                InternshipSettings,

                InternshipStripItem,

                InternshipTrackItem,

                InternshipHighlightItem,

                InternshipWhoCanApplyItem,

                InternshipWhatYouLearnItem,

                InternshipProcessStep,

                InternshipBenefitItem,

                InternshipFaqItem,

            )

            intern_settings = InternshipSettings.get_settings()

            all_intern_strip = list(InternshipStripItem.objects.all().order_by('order', 'id'))

            all_intern_tracks = list(InternshipTrackItem.objects.all().order_by('order', 'id'))

            all_intern_highlights = list(InternshipHighlightItem.objects.all().order_by('order', 'id'))

            all_intern_who = list(InternshipWhoCanApplyItem.objects.all().order_by('order', 'id'))

            all_intern_learn = list(InternshipWhatYouLearnItem.objects.all().order_by('order', 'id'))

            all_intern_process = list(InternshipProcessStep.objects.all().order_by('order', 'id'))

            all_intern_benefits = list(InternshipBenefitItem.objects.all().order_by('order', 'id'))

            all_intern_faqs = list(InternshipFaqItem.objects.all().order_by('order', 'id'))

            from apps.internships.models import Internship

            all_intern_openings = list(Internship.objects.all().order_by('-id'))



            context.update({

                'intern_settings': intern_settings,

                'all_intern_strip': all_intern_strip,

                'all_intern_tracks': all_intern_tracks,

                'all_intern_highlights': all_intern_highlights,

                'all_intern_who': all_intern_who,

                'all_intern_learn': all_intern_learn,

                'all_intern_process': all_intern_process,

                'all_intern_benefits': all_intern_benefits,

                'all_intern_faqs': all_intern_faqs,

                'intern_strip_json_init': json.dumps([

                    {'id': s.id, 'title': s.title, 'icon_class': s.icon_class, 'order': s.order, 'is_visible': s.is_visible}

                    for s in all_intern_strip

                ]),

                'intern_tracks_json_init': json.dumps([

                    {'id': t.id, 'title': t.title, 'description': t.description, 'subtitle': t.description, 'icon_class': t.icon_class, 'badge_number': t.badge_number, 'code': t.badge_number, 'card_style': t.card_style, 'order': t.order, 'is_visible': t.is_visible}

                    for t in all_intern_tracks

                ]),

                'intern_highlights_json_init': json.dumps([

                    {'id': h.id, 'title': h.title, 'text': h.title, 'icon_class': h.icon_class, 'order': h.order, 'is_visible': h.is_visible}

                    for h in all_intern_highlights

                ]),

                'intern_who_json_init': json.dumps([

                    {'id': w.id, 'title': w.title, 'icon_class': w.icon_class, 'order': w.order, 'is_visible': w.is_visible}

                    for w in all_intern_who

                ]),

                'intern_learn_json_init': json.dumps([

                    {'id': l.id, 'title': l.title, 'icon_class': l.icon_class, 'order': l.order, 'is_visible': l.is_visible}

                    for l in all_intern_learn

                ]),

                'intern_process_json_init': json.dumps([

                    {'id': p.id, 'step_number': p.step_number, 'phase_name': p.step_number, 'title': p.title, 'description': p.description, 'icon_class': p.icon_class, 'is_final': p.is_final, 'order': p.order, 'is_visible': p.is_visible}

                    for p in all_intern_process

                ]),

                'intern_benefits_json_init': json.dumps([

                    {'id': b.id, 'title': b.title, 'icon_class': b.icon_class, 'order': b.order, 'is_visible': b.is_visible}

                    for b in all_intern_benefits

                ]),

                'intern_faqs_json_init': json.dumps([

                    {'id': f.id, 'question': f.question, 'answer': f.answer, 'order': f.order, 'is_visible': f.is_visible}

                    for f in all_intern_faqs

                ]),

                'all_intern_openings': all_intern_openings,

                'intern_openings_json_init': json.dumps([

                    {

                        'id': o.id,

                        'title': o.title,

                        'mode': o.mode or 'Onsite',

                        'duration': o.duration or '3 Months',

                        'seats': o.seats or 1,

                        'skills_required': o.skills_required or '',

                        'location': o.location or '',

                        'stipend': o.stipend or '',

                        'description': o.description or '',

                        'status': o.status or 'Open',

                        'is_visible': (o.status == 'Open')

                    }

                    for o in all_intern_openings

                ]),

            })

        elif current_services_page == 'payroll_outsourcing':







            from apps.core.models import (







                PayrollOutsourcingSettings,







                PoServiceCard,







                PoIndustryItem,







                PoWhyChooseItem,







                PoProcessStep,







                PoEmployerBenefit,







                PoEmployeeBenefit,







                PoFaqItem,







            )















            po_settings = PayrollOutsourcingSettings.get_settings()







            all_po_services = list(PoServiceCard.objects.all().order_by('order', 'id'))







            all_po_industries = list(PoIndustryItem.objects.all().order_by('order', 'id'))







            all_po_why_choose = list(PoWhyChooseItem.objects.all().order_by('order', 'id'))







            all_po_process = list(PoProcessStep.objects.all().order_by('order', 'id'))







            all_po_employer_benefits = list(PoEmployerBenefit.objects.all().order_by('order', 'id'))







            all_po_employee_benefits = list(PoEmployeeBenefit.objects.all().order_by('order', 'id'))







            all_po_faqs = list(PoFaqItem.objects.all().order_by('order', 'id'))















            context.update({







                'po_settings': po_settings,







                'all_po_services': all_po_services,







                'all_po_industries': all_po_industries,







                'all_po_why_choose': all_po_why_choose,







                'all_po_process': all_po_process,







                'all_po_employer_benefits': all_po_employer_benefits,







                'all_po_employee_benefits': all_po_employee_benefits,







                'all_po_faqs': all_po_faqs,







                'po_services_json_init': json.dumps([







                    {'id': s.id, 'title': s.title, 'description': s.description, 'icon_class': s.icon_class, 'badge_theme': s.badge_theme, 'order': s.order, 'is_visible': s.is_visible}







                    for s in all_po_services







                ]),







                'po_industries_json_init': json.dumps([







                    {'id': i.id, 'name': i.name, 'order': i.order, 'is_visible': i.is_visible}







                    for i in all_po_industries







                ]),







                'po_why_choose_json_init': json.dumps([







                    {'id': w.id, 'title': w.title, 'order': w.order, 'is_visible': w.is_visible}







                    for w in all_po_why_choose







                ]),







                'po_process_json_init': json.dumps([







                    {'id': p.id, 'step_number': p.step_number, 'title': p.title, 'icon_class': p.icon_class, 'order': p.order, 'is_visible': p.is_visible}







                    for p in all_po_process







                ]),







                'po_employer_benefits_json_init': json.dumps([







                    {'id': b.id, 'title': b.title, 'order': b.order, 'is_visible': b.is_visible}







                    for b in all_po_employer_benefits







                ]),







                'po_employee_benefits_json_init': json.dumps([







                    {'id': b.id, 'title': b.title, 'order': b.order, 'is_visible': b.is_visible}







                    for b in all_po_employee_benefits







                ]),







                'po_faqs_json_init': json.dumps([







                    {'id': f.id, 'question': f.question, 'answer': f.answer, 'order': f.order, 'is_visible': f.is_visible}







                    for f in all_po_faqs







                ]),







            })















    if sub_key == 'gallery':
        from apps.core.models import GalleryPageSettings
        import json
        gallery_settings = GalleryPageSettings.get_settings()
        context.update({
            'gallery_settings': gallery_settings,
            'current_gallery_tab': request.GET.get('tab', 'all'),
            'gallery_items_list': gallery_settings.get_gallery_items(visible_only=False),
            'gallery_items_json_init': json.dumps(gallery_settings.get_gallery_items(visible_only=False)),
            'call_rows_list': gallery_settings.get_call_rows(visible_only=False),
            'call_rows_json_init': json.dumps(gallery_settings.get_call_rows(visible_only=False)),
            'email_rows_list': gallery_settings.get_email_rows(visible_only=False),
            'email_rows_json_init': json.dumps(gallery_settings.get_email_rows(visible_only=False)),
        })

    if sub_key == 'contact':
        from apps.core.models import ContactPageSettings
        import json
        contact_settings = ContactPageSettings.get_settings()
        context.update({
            'contact_settings': contact_settings,
            'current_contact_tab': request.GET.get('tab', 'all'),
            'call_rows_list': contact_settings.get_call_rows(visible_only=False),
            'call_rows_json_init': json.dumps(contact_settings.get_call_rows(visible_only=False)),
            'email_rows_list': contact_settings.get_email_rows(visible_only=False),
            'email_rows_json_init': json.dumps(contact_settings.get_email_rows(visible_only=False)),
        })

    if sub_key == 'blog':
        from apps.core.models import BlogPageSettings
        import json
        blog_settings = BlogPageSettings.get_settings()
        context.update({
            'blog_settings': blog_settings,
            'current_blog_tab': request.GET.get('tab', 'all'),
            'popular_categories_list': blog_settings.get_popular_categories(visible_only=False),
            'popular_categories_json_init': json.dumps(blog_settings.get_popular_categories(visible_only=False)),
            'latest_posts_list': blog_settings.get_latest_posts(visible_only=False),
            'latest_posts_json_init': json.dumps(blog_settings.get_latest_posts(visible_only=False)),
            'recent_posts_list': blog_settings.get_recent_posts(visible_only=False),
            'recent_posts_json_init': json.dumps(blog_settings.get_recent_posts(visible_only=False)),
        })

    if sub_key == 'careers':
        from apps.core.models import CareerPageSettings
        import json
        career_settings = CareerPageSettings.get_settings()
        context.update({
            'career_settings': career_settings,
            'current_career_tab': request.GET.get('tab', 'all'),
            'openings_list': career_settings.get_openings(visible_only=False),
            'openings_json_init': json.dumps(career_settings.get_openings(visible_only=False)),
            'why_build_list': career_settings.get_why_build(visible_only=False),
            'why_build_json_init': json.dumps(career_settings.get_why_build(visible_only=False)),
            'career_areas_list': career_settings.get_career_areas(visible_only=False),
            'career_areas_json_init': json.dumps(career_settings.get_career_areas(visible_only=False)),
            'journey_steps_list': career_settings.get_journey_steps(visible_only=False),
            'journey_steps_json_init': json.dumps(career_settings.get_journey_steps(visible_only=False)),
            'look_for_list': career_settings.get_look_for(visible_only=False),
            'look_for_json_init': json.dumps(career_settings.get_look_for(visible_only=False)),
            'benefits_list': career_settings.get_benefits(visible_only=False),
            'benefits_json_init': json.dumps(career_settings.get_benefits(visible_only=False)),
        })

    if sub_key == 'jobs':
        import json
        from apps.core.models import JobPageSettings
        from apps.jobs.models import Job, JobCategory

        job_settings = JobPageSettings.get_settings()

        context.update({

            'job_settings': job_settings,

            'current_job_tab': request.GET.get('tab', 'all'),

            'popular_industries_list': job_settings.get_popular_industries(visible_only=False),

            'popular_industries_json_init': json.dumps(job_settings.get_popular_industries(visible_only=False)),

            'locations_list': job_settings.get_jobs_by_location(visible_only=False),

            'locations_json_init': json.dumps(job_settings.get_jobs_by_location(visible_only=False)),

            'why_choose_list': job_settings.get_why_choose(visible_only=False),

            'why_choose_json_init': json.dumps(job_settings.get_why_choose(visible_only=False)),

            'commit_stats_list': job_settings.get_commit_stats(visible_only=False),

            'commit_stats_json_init': json.dumps(job_settings.get_commit_stats(visible_only=False)),

            'cta_steps_list': job_settings.get_cta_steps(visible_only=False),

            'cta_steps_json_init': json.dumps(job_settings.get_cta_steps(visible_only=False)),

            'live_jobs_count': Job.objects.live().count(),

            'active_categories_count': JobCategory.objects.filter(category_type='job_category', status='Active').count(),

            'active_types_count': JobCategory.objects.filter(category_type='job_type', status='Active').count(),
            'job_types_all': JobCategory.objects.filter(category_type='job_type').order_by('order', 'id'),
            'job_categories_all': JobCategory.objects.filter(category_type='job_category').order_by('order', 'id'),
            'recent_jobs_all': Job.objects.select_related('company', 'employer').order_by('-id')[:25],

        })



    return render(request, 'dashboard/website_management.html', context)























def validate_safe_url(url_str, field_label="URL"):







    if not url_str:







        return ""







    clean = url_str.strip()







    if 'javascript:' in clean.lower():







        from django.core.exceptions import ValidationError







        raise ValidationError(f"{field_label} cannot contain javascript: schemes.")







    valid_prefixes = ('http://', 'https://', '/', '#', 'tel:', 'mailto:')







    if not any(clean.startswith(p) for p in valid_prefixes):







        if '@' in clean and ' ' not in clean:







            return clean







        from django.core.exceptions import ValidationError







        raise ValidationError(f"{field_label} must be a valid URL or relative path (e.g. /about/).")







    return clean























def validate_safe_phone(phone_str, field_label="Phone"):







    if not phone_str:







        return ""







    import re







    from django.core.exceptions import ValidationError







    clean = phone_str.strip()







    if not re.match(r'^[+\d\s\-()]{6,30}$', clean):







        raise ValidationError(f"{field_label} must be a valid telephone number format.")







    return clean























def validate_image_upload(file_obj, field_label="Image"):







    if not file_obj:







        return None







    from django.core.exceptions import ValidationError







    # 2 MB size limit







    if file_obj.size > 2 * 1024 * 1024:







        raise ValidationError(f"{field_label} size cannot exceed 2 MB.")







    ext = os.path.splitext(file_obj.name)[1].lower()







    allowed = ('.png', '.jpg', '.jpeg', '.webp', '.svg')







    if ext not in allowed:







        raise ValidationError(f"{field_label} format must be PNG, JPG, JPEG, WEBP or SVG.")







    if ext != '.svg':







        try:







            from PIL import Image







            img = Image.open(file_obj)







            img.verify()







            file_obj.seek(0)







        except Exception:







            raise ValidationError(f"{field_label} is not a valid or readable image file.")







    return file_obj























def handle_header_footer_save(request, admin_user):







    from django.core.validators import validate_email as django_validate_email







    from django.core.exceptions import ValidationError







    from django.db import transaction







    from django.core.cache import cache







    from django.contrib import messages







    from apps.core.models import SiteSettings, NavItem, FooterColumn, FooterLink, SocialLink, FooterService







    from apps.enquiries.models import log_activity















    site = SiteSettings.get_settings()







    errors = []















    # 1. Emails







    support_email = request.POST.get('support_email', '').strip()







    if support_email:







        try:







            django_validate_email(support_email)







        except ValidationError:







            errors.append("Invalid Support Email address format.")















    office_email = request.POST.get('office_email', '').strip()







    if office_email:







        try:







            django_validate_email(office_email)







        except ValidationError:







            errors.append("Invalid Office Email address format.")















    # 2. Phones







    helpline_phone = request.POST.get('helpline_phone', '').strip()







    if helpline_phone:







        try:







            validate_safe_phone(helpline_phone, "Helpline Phone")







        except ValidationError as e:







            errors.append(str(e.message))















    secondary_phone = request.POST.get('secondary_phone', '').strip()







    if secondary_phone:







        try:







            validate_safe_phone(secondary_phone, "Secondary Phone")







        except ValidationError as e:







            errors.append(str(e.message))















    office_phone_1 = request.POST.get('office_phone_1', '').strip()







    if office_phone_1:







        try:







            validate_safe_phone(office_phone_1, "Office Phone 1")







        except ValidationError as e:







            errors.append(str(e.message))















    office_phone_2 = request.POST.get('office_phone_2', '').strip()







    if office_phone_2:







        try:







            validate_safe_phone(office_phone_2, "Office Phone 2")







        except ValidationError as e:







            errors.append(str(e.message))















    navbar_call_text = request.POST.get('navbar_call_text', '').strip()







    navbar_call_number = request.POST.get('navbar_call_number', '').strip()















    # 3. URLs







    franchise_url = request.POST.get('franchise_url', '').strip()







    if franchise_url:







        try:







            validate_safe_url(franchise_url, "Franchise URL")







        except ValidationError as e:







            errors.append(str(e.message))















    floating_whatsapp_url = request.POST.get('floating_whatsapp_url', '').strip()







    if floating_whatsapp_url:







        try:







            validate_safe_url(floating_whatsapp_url, "WhatsApp URL")







        except ValidationError as e:







            errors.append(str(e.message))















    privacy_policy_url = request.POST.get('privacy_policy_url', '').strip()







    if privacy_policy_url:







        try:







            validate_safe_url(privacy_policy_url, "Privacy Policy URL")







        except ValidationError as e:







            errors.append(str(e.message))















    terms_url = request.POST.get('terms_url', '').strip()







    if terms_url:







        try:







            validate_safe_url(terms_url, "Terms URL")







        except ValidationError as e:







            errors.append(str(e.message))















    # 4. Images







    header_logo_file = request.FILES.get('header_logo')







    if header_logo_file:







        try:







            validate_image_upload(header_logo_file, "Header Logo")







        except ValidationError as e:







            errors.append(str(e.message))















    footer_logo_file = request.FILES.get('footer_logo')







    if footer_logo_file:







        try:







            validate_image_upload(footer_logo_file, "Footer Logo")







        except ValidationError as e:







            errors.append(str(e.message))















    favicon_file = request.FILES.get('favicon')







    if favicon_file:







        try:







            validate_image_upload(favicon_file, "Favicon")







        except ValidationError as e:







            errors.append(str(e.message))















    if errors:







        for err in errors:







            messages.error(request, err)







        return False















    with transaction.atomic():







        # Update SiteSettings scalar fields







        site.site_name = request.POST.get('site_name', site.site_name).strip()







        site.tagline = request.POST.get('tagline', site.tagline).strip()







        site.logo_alt_text = request.POST.get('logo_alt_text', site.logo_alt_text).strip()







        site.topbar_address = request.POST.get('topbar_address', '').strip()







        site.support_email = support_email







        site.topbar_hours = request.POST.get('topbar_hours', '').strip()







        site.helpline_phone = helpline_phone







        site.secondary_phone = secondary_phone







        site.announcement_text = request.POST.get('announcement_text', '').strip()







        site.show_announcement = (request.POST.get('show_announcement') in ('on', '1', 'true', True))







        site.franchise_url = franchise_url or "/contact/"







        site.show_franchise_btn = (request.POST.get('show_franchise_btn') in ('on', '1', 'true', True))







        site.navbar_call_text = navbar_call_text







        site.navbar_call_number = navbar_call_number







        site.show_login_btn = (request.POST.get('show_login_btn') in ('on', '1', 'true', True))







        site.footer_about = request.POST.get('footer_about', '').strip()







        site.office_address = request.POST.get('office_address', '').strip()







        site.office_email = office_email







        site.office_phone_1 = office_phone_1







        site.office_phone_2 = office_phone_2







        site.working_hours = request.POST.get('working_hours', '').strip()







        site.copyright_text = request.POST.get('copyright_text', '').strip()







        site.privacy_policy_url = privacy_policy_url or "#"







        site.terms_url = terms_url or "#"







        site.footer_credit = request.POST.get('footer_credit', '').strip()







        site.floating_call_number = request.POST.get('floating_call_number', '').strip()







        site.floating_whatsapp_url = floating_whatsapp_url







        site.show_floating_buttons = (request.POST.get('show_floating_buttons') in ('on', '1', 'true', True))















        if header_logo_file:







            site.header_logo = header_logo_file







        elif request.POST.get('clear_header_logo') == '1':







            site.header_logo = None















        if footer_logo_file:







            site.footer_logo = footer_logo_file







        elif request.POST.get('clear_footer_logo') == '1':







            site.footer_logo = None















        if favicon_file:







            site.favicon = favicon_file







        elif request.POST.get('clear_favicon') == '1':







            site.favicon = None















        site.save()















        # Update Social Links







        for plat in ['facebook', 'instagram', 'linkedin', 'youtube', 'twitter', 'whatsapp']:







            plat_url = request.POST.get(f'social_url_{plat}', '').strip()







            plat_enabled = (request.POST.get(f'social_enabled_{plat}') in ('on', '1', 'true', True))







            if plat_url:







                try:







                    validate_safe_url(plat_url, f"{plat.capitalize()} URL")







                except ValidationError as e:







                    messages.warning(request, str(e.message))







                    continue







            SocialLink.objects.update_or_create(







                platform=plat,







                defaults={'url': plat_url, 'is_enabled': plat_enabled}







            )















        # Update Nav Items if JSON provided







        nav_json_str = request.POST.get('nav_items_json')







        if nav_json_str:







            try:







                nav_data = json.loads(nav_json_str)







                NavItem.objects.all().delete()







                created_items = {}







                # Pass 1: Root items







                for idx, item in enumerate(nav_data):







                    parent_idx = item.get('parent_idx')







                    if parent_idx is None or parent_idx == "":







                        url = item.get('url', '/').strip() or '/'







                        if 'javascript:' not in url.lower():







                            obj = NavItem.objects.create(







                                label=item.get('label', 'Menu Item').strip(),







                                url=url,







                                active_key=item.get('active_key', '').strip(),







                                order=idx + 1,







                                is_visible=bool(item.get('is_visible', True)),







                                new_tab=bool(item.get('new_tab', False))







                            )







                            created_items[str(idx)] = obj







                # Pass 2: Child dropdown items







                for idx, item in enumerate(nav_data):







                    parent_idx = item.get('parent_idx')







                    if parent_idx is not None and str(parent_idx) in created_items:







                        url = item.get('url', '/').strip() or '/'







                        if 'javascript:' not in url.lower():







                            NavItem.objects.create(







                                parent=created_items[str(parent_idx)],







                                label=item.get('label', 'Submenu Item').strip(),







                                url=url,







                                active_key=item.get('active_key', '').strip(),







                                order=idx + 1,







                                is_visible=bool(item.get('is_visible', True)),







                                new_tab=bool(item.get('new_tab', False))







                            )







            except Exception as e:







                messages.warning(request, f"Error updating menu items: {str(e)}")















        # Update Footer Columns & Links if JSON provided







        footer_cols_json = request.POST.get('footer_cols_json')







        if footer_cols_json:







            try:







                cols_data = json.loads(footer_cols_json)







                FooterColumn.objects.all().delete()







                for c_idx, c_item in enumerate(cols_data):







                    col = FooterColumn.objects.create(







                        title=c_item.get('title', 'Links').strip(),







                        order=c_idx + 1,







                        is_visible=bool(c_item.get('is_visible', True))







                    )







                    for l_idx, l_item in enumerate(c_item.get('links', [])):







                        url = l_item.get('url', '/').strip() or '/'







                        if 'javascript:' not in url.lower():







                            FooterLink.objects.create(







                                column=col,







                                label=l_item.get('label', 'Link').strip(),







                                url=url,







                                order=l_idx + 1,







                                is_visible=bool(l_item.get('is_visible', True)),







                                new_tab=bool(l_item.get('new_tab', False))







                            )







            except Exception as e:







                messages.warning(request, f"Error updating footer columns: {str(e)}")















        # Update Footer Services if JSON provided







        services_json = request.POST.get('footer_services_json')







        if services_json:







            try:







                serv_data = json.loads(services_json)







                FooterService.objects.all().delete()







                for s_idx, s_item in enumerate(serv_data):







                    url = s_item.get('url', '/services/').strip() or '/services/'







                    if 'javascript:' not in url.lower():







                        FooterService.objects.create(







                            name=s_item.get('name', 'Service').strip(),







                            url=url,







                            order=s_idx + 1,







                            is_visible=bool(s_item.get('is_visible', True))







                        )







            except Exception as e:







                messages.warning(request, f"Error updating footer services: {str(e)}")















        # Clear Cache







        cache.delete('public_site_context')















        # Log Activity







        actor = getattr(admin_user, 'full_name', '') or getattr(admin_user, 'username', '') or getattr(admin_user, 'name', '') or 'Admin'







        log_activity(







            'HEADER_FOOTER_UPDATE',







            'Header & Footer Updated',







            description="Admin updated Topbar, Navbar, Branding, Social Links, and Footer configuration.",







            actor=actor







        )















        messages.success(request, "Header, Navbar, and Footer settings saved successfully! Changes are live on the website.")







        return True























def handle_home_page_save(request, admin_user):







    from django.core.exceptions import ValidationError







    from django.db import transaction







    from django.core.cache import cache







    from django.contrib import messages







    from apps.core.models import (







        HomePageSettings,







        HeroStat,







        GrowthStep,







        HomeServiceCard,







        WhyChooseItem,







        HomeIndustryItem,







        InternshipCard,







        InternshipHighlight,







        FeaturedCandidate,







        GalleryImage,







        GalleryInfoBox,







    )







    from apps.enquiries.models import log_activity















    home = HomePageSettings.get_settings()







    errors = []















    # Validations







    hero_cta_primary_url = request.POST.get('hero_cta_primary_url', '').strip()







    if hero_cta_primary_url:







        try:







            validate_safe_url(hero_cta_primary_url, "Primary CTA URL")







        except ValidationError as e:







            errors.append(str(e.message))















    hero_cta_secondary_url = request.POST.get('hero_cta_secondary_url', '').strip()







    if hero_cta_secondary_url:







        try:







            validate_safe_url(hero_cta_secondary_url, "Secondary CTA URL")







        except ValidationError as e:







            errors.append(str(e.message))















    hero_cta_internship_url = request.POST.get('hero_cta_internship_url', '').strip()







    if hero_cta_internship_url:







        try:







            validate_safe_url(hero_cta_internship_url, "Internship CTA URL")







        except ValidationError as e:







            errors.append(str(e.message))















    about_btn_url = request.POST.get('about_btn_url', '').strip()







    if about_btn_url:







        try:







            validate_safe_url(about_btn_url, "About Read More URL")







        except ValidationError as e:







            errors.append(str(e.message))















    internship_cta_url = request.POST.get('internship_cta_url', '').strip()







    if internship_cta_url:







        try:







            validate_safe_url(internship_cta_url, "Internship Programme URL")







        except ValidationError as e:







            errors.append(str(e.message))















    gallery_btn_url = request.POST.get('gallery_btn_url', '').strip()







    if gallery_btn_url:







        try:







            validate_safe_url(gallery_btn_url, "Gallery View All URL")







        except ValidationError as e:







            errors.append(str(e.message))















    contact_map_url = request.POST.get('contact_map_url', '').strip()







    if contact_map_url:







        try:







            validate_safe_url(contact_map_url, "Contact Map URL")







        except ValidationError as e:







            errors.append(str(e.message))















    # Image uploads







    hero_image_file = request.FILES.get('hero_image')







    if hero_image_file:







        try:







            validate_image_upload(hero_image_file, "Hero Image")







        except ValidationError as e:







            errors.append(str(e.message))















    about_image_file = request.FILES.get('about_image')







    if about_image_file:







        try:







            validate_image_upload(about_image_file, "About Image")







        except ValidationError as e:







            errors.append(str(e.message))















    og_image_file = request.FILES.get('og_image')







    if og_image_file:







        try:







            validate_image_upload(og_image_file, "SEO OG Image")







        except ValidationError as e:







            errors.append(str(e.message))















    if errors:







        for err in errors:







            messages.error(request, err)







        return False















    with transaction.atomic():







        # 1. Hero







        home.hero_visible = ('hero_visible' in request.POST)







        home.hero_unit_tag = request.POST.get('hero_unit_tag', '').strip()







        home.hero_eyebrow = request.POST.get('hero_eyebrow', '').strip()







        home.hero_title = request.POST.get('hero_title', home.hero_title).strip()







        home.hero_title_highlight = request.POST.get('hero_title_highlight', '').strip()







        home.hero_subtitle = request.POST.get('hero_subtitle', '').strip()







        home.hero_cta_primary_label = request.POST.get('hero_cta_primary_label', 'Apply Now').strip()







        home.hero_cta_primary_url = hero_cta_primary_url or '#'







        home.hero_cta_primary_visible = ('hero_cta_primary_visible' in request.POST)







        home.hero_cta_secondary_label = request.POST.get('hero_cta_secondary_label', 'Hire Talent').strip()







        home.hero_cta_secondary_url = hero_cta_secondary_url or '/employer/hire-talent/'







        home.hero_cta_secondary_visible = ('hero_cta_secondary_visible' in request.POST)







        home.hero_cta_internship_label = request.POST.get('hero_cta_internship_label', 'Apply Internship').strip()







        home.hero_cta_internship_url = hero_cta_internship_url or '#'







        home.hero_cta_internship_visible = ('hero_cta_internship_visible' in request.POST)







        home.hero_image_alt = request.POST.get('hero_image_alt', '').strip()







        home.hero_search_visible = ('hero_search_visible' in request.POST)







        home.hero_growth_steps_visible = ('hero_growth_steps_visible' in request.POST)







        home.job_pills_visible = ('job_pills_visible' in request.POST)















        if hero_image_file:







            home.hero_image = hero_image_file







        elif request.POST.get('clear_hero_image') == '1':







            home.hero_image = None















        # 2. Services







        home.services_tag = request.POST.get('services_tag', '').strip()







        home.services_title = request.POST.get('services_title', home.services_title).strip()







        home.services_subtitle = request.POST.get('services_subtitle', '').strip()







        home.services_visible = ('services_visible' in request.POST)















        # 3. About







        home.about_tag = request.POST.get('about_tag', '').strip()







        home.about_heading = request.POST.get('about_heading', home.about_heading).strip()







        home.about_heading_highlight = request.POST.get('about_heading_highlight', '').strip()







        home.about_content = request.POST.get('about_content', '').strip()







        home.about_badge_text = request.POST.get('about_badge_text', '').strip()







        home.about_image_alt = request.POST.get('about_image_alt', '').strip()







        home.about_sub_title = request.POST.get('about_sub_title', '').strip()







        home.about_sub_snippet = request.POST.get('about_sub_snippet', '').strip()







        home.about_vision_title = request.POST.get('about_vision_title', '').strip()







        home.about_vision_desc = request.POST.get('about_vision_desc', '').strip()







        home.about_mission_title = request.POST.get('about_mission_title', '').strip()







        home.about_mission_desc = request.POST.get('about_mission_desc', '').strip()







        home.about_btn_label = request.POST.get('about_btn_label', 'Read More').strip()







        home.about_btn_url = about_btn_url or '/about/'







        home.about_btn_visible = ('about_btn_visible' in request.POST)







        home.about_visible = ('about_visible' in request.POST)















        if about_image_file:







            home.about_image = about_image_file







        elif request.POST.get('clear_about_image') == '1':







            home.about_image = None















        # 4. Why Choose Us







        home.why_choose_tag = request.POST.get('why_choose_tag', '').strip()







        home.why_choose_title = request.POST.get('why_choose_title', home.why_choose_title).strip()







        home.why_choose_subtitle = request.POST.get('why_choose_subtitle', '').strip()







        home.why_choose_visible = ('why_choose_visible' in request.POST)















        # 5. Industries







        home.industries_tag = request.POST.get('industries_tag', '').strip()







        home.industries_title = request.POST.get('industries_title', home.industries_title).strip()







        home.industries_subtitle = request.POST.get('industries_subtitle', '').strip()







        home.industries_visible = ('industries_visible' in request.POST)















        # 6. Internship







        home.internship_heading = request.POST.get('internship_heading', home.internship_heading).strip()







        home.internship_subtitle = request.POST.get('internship_subtitle', '').strip()







        home.internship_box_title = request.POST.get('internship_box_title', home.internship_box_title).strip()







        home.internship_cta_label = request.POST.get('internship_cta_label', 'Apply Now').strip()







        home.internship_cta_url = internship_cta_url or '#'







        home.internship_visible = ('internship_visible' in request.POST)















        # 7. Categories & Latest Jobs







        home.job_categories_visible = ('job_categories_visible' in request.POST)







        home.latest_jobs_visible = ('latest_jobs_visible' in request.POST)















        # 8. Candidates







        home.candidates_tag = request.POST.get('candidates_tag', '').strip()







        home.candidates_title = request.POST.get('candidates_title', home.candidates_title).strip()







        home.candidates_subtitle = request.POST.get('candidates_subtitle', '').strip()







        home.candidates_visible = ('candidates_visible' in request.POST)















        # 9. Gallery







        home.gallery_tag = request.POST.get('gallery_tag', '').strip()







        home.gallery_title = request.POST.get('gallery_title', home.gallery_title).strip()







        home.gallery_subtitle = request.POST.get('gallery_subtitle', '').strip()







        home.gallery_btn_label = request.POST.get('gallery_btn_label', 'View Full Gallery').strip()







        home.gallery_btn_url = gallery_btn_url or '/gallery/'







        home.gallery_btn_visible = ('gallery_btn_visible' in request.POST)







        home.gallery_visible = ('gallery_visible' in request.POST)















        # 10. Contact







        home.contact_title = request.POST.get('contact_title', home.contact_title).strip()







        home.contact_form_title = request.POST.get('contact_form_title', home.contact_form_title).strip()







        home.contact_map_url = contact_map_url or home.contact_map_url







        home.contact_visible = ('contact_visible' in request.POST)















        # SEO







        home.meta_title = request.POST.get('meta_title', '').strip()







        home.meta_description = request.POST.get('meta_description', '').strip()







        if og_image_file:







            home.og_image = og_image_file







        elif request.POST.get('clear_og_image') == '1':







            home.og_image = None















        home.save()















        # Dynamic JSON Parsers







        # A. Hero Stats







        hero_stats_json = request.POST.get('hero_stats_json')







        if hero_stats_json:







            try:







                stats_data = json.loads(hero_stats_json)







                HeroStat.objects.all().delete()







                for idx, s in enumerate(stats_data, 1):







                    HeroStat.objects.create(







                        icon_class=s.get('icon_class', 'fa-solid fa-briefcase').strip(),







                        value=s.get('value', '').strip(),







                        label=s.get('label', '').strip(),







                        order=int(s.get('order', idx)),







                        is_visible=bool(s.get('is_visible', True))







                    )







            except Exception as e:







                messages.warning(request, f"Error updating hero statistics: {e}")















        # B. Growth Steps







        growth_steps_json = request.POST.get('growth_steps_json')







        if growth_steps_json:







            try:







                steps_data = json.loads(growth_steps_json)







                GrowthStep.objects.all().delete()







                for idx, st in enumerate(steps_data, 1):







                    GrowthStep.objects.create(







                        step_number=int(st.get('step_number', idx)),







                        title=st.get('title', '').strip(),







                        subtitle=st.get('subtitle', '').strip(),







                        order=int(st.get('order', idx)),







                        is_visible=bool(st.get('is_visible', True))







                    )







            except Exception as e:







                messages.warning(request, f"Error updating growth steps: {e}")















        # C. Service Cards







        service_cards_json = request.POST.get('service_cards_json')







        if service_cards_json is not None and service_cards_json.strip() != "":







            try:







                cards_data = json.loads(service_cards_json)







                HomeServiceCard.objects.all().delete()







                for idx, sc in enumerate(cards_data, 1):







                    title = sc.get('title', '').strip()







                    if not title:







                        continue







                    is_vis = sc.get('is_visible')







                    if isinstance(is_vis, str):







                        is_vis = is_vis.lower() in ('true', '1', 'yes')







                    elif is_vis is None:







                        is_vis = True







                    else:







                        is_vis = bool(is_vis)















                    HomeServiceCard.objects.create(







                        title=title,







                        icon_class=sc.get('icon_class', 'fas fa-users').strip() or 'fas fa-users',







                        icon_color=sc.get('icon_color', 'blue').strip() or 'blue',







                        bullets=sc.get('bullets', '').strip(),







                        link_url=sc.get('link_url', '/services/').strip() or '/services/',







                        link_text=sc.get('link_text', 'Read More').strip() or 'Read More',







                        order=idx,







                        is_visible=is_vis







                    )







            except Exception as e:







                messages.warning(request, f"Error updating service cards: {e}")















        # D. Why Choose Us







        why_choose_json = request.POST.get('why_choose_json')







        if why_choose_json is not None and why_choose_json.strip() != "":







            try:







                why_data = json.loads(why_choose_json)







                WhyChooseItem.objects.all().delete()







                for idx, w in enumerate(why_data, 1):







                    title = w.get('title', '').strip()







                    if not title:







                        continue







                    is_vis = w.get('is_visible')







                    if isinstance(is_vis, str):







                        is_vis = is_vis.lower() in ('true', '1', 'yes')







                    elif is_vis is None:







                        is_vis = True







                    else:







                        is_vis = bool(is_vis)















                    WhyChooseItem.objects.create(







                        title=title,







                        icon_class=w.get('icon_class', 'fas fa-users').strip() or 'fas fa-check-circle',







                        description=w.get('description', '').strip(),







                        order=idx,







                        is_visible=is_vis







                    )







            except Exception as e:







                messages.warning(request, f"Error updating Why Choose items: {e}")















        # Industries We Serve Items







        industries_items_json = request.POST.get('industries_items_json')







        if industries_items_json is not None and industries_items_json.strip() != "":







            try:







                ind_data = json.loads(industries_items_json)







                HomeIndustryItem.objects.all().delete()







                for idx, ind in enumerate(ind_data, 1):







                    name = ind.get('name', '').strip()







                    if not name:







                        continue







                    is_vis = ind.get('is_visible')







                    if isinstance(is_vis, str):







                        is_vis = is_vis.lower() in ('true', '1', 'yes')







                    elif is_vis is None:







                        is_vis = True







                    else:







                        is_vis = bool(is_vis)















                    HomeIndustryItem.objects.create(







                        name=name,







                        icon_class=ind.get('icon_class', 'fas fa-industry').strip() or 'fas fa-industry',







                        link_url=ind.get('link_url', '').strip(),







                        order=idx,







                        is_visible=is_vis







                    )







            except Exception as e:







                messages.warning(request, f"Error updating industries: {e}")















        # E. Internship Cards







        internship_cards_json = request.POST.get('internship_cards_json')







        if internship_cards_json:







            try:







                ic_data = json.loads(internship_cards_json)







                InternshipCard.objects.all().delete()







                for idx, ic in enumerate(ic_data, 1):







                    InternshipCard.objects.create(







                        domain_name=ic.get('domain_name', '').strip(),







                        icon_class=ic.get('icon_class', 'fa-solid fa-users').strip(),







                        icon_color=ic.get('icon_color', '#2563EB').strip(),







                        bullets=ic.get('bullets', '').strip(),







                        order=int(ic.get('order', idx)),







                        is_visible=bool(ic.get('is_visible', True))







                    )







            except Exception as e:







                messages.warning(request, f"Error updating internship domains: {e}")















        # F. Internship Highlights







        internship_benefits_json = request.POST.get('internship_benefits_json')







        if internship_benefits_json:







            try:







                ib_data = json.loads(internship_benefits_json)







                InternshipHighlight.objects.filter(item_type='benefit').delete()







                for idx, b in enumerate(ib_data, 1):







                    InternshipHighlight.objects.create(







                        item_type='benefit',







                        text=b.get('text', '').strip(),







                        order=int(b.get('order', idx)),







                        is_visible=bool(b.get('is_visible', True))







                    )







            except Exception as e:







                messages.warning(request, f"Error updating internship benefits: {e}")















        internship_badges_json = request.POST.get('internship_badges_json')







        if internship_badges_json:







            try:







                badges_data = json.loads(internship_badges_json)







                InternshipHighlight.objects.filter(item_type='bottom_badge').delete()







                for idx, bg in enumerate(badges_data, 1):







                    InternshipHighlight.objects.create(







                        item_type='bottom_badge',







                        text=bg.get('text', '').strip(),







                        icon_class=bg.get('icon_class', 'fa-solid fa-check').strip(),







                        order=int(bg.get('order', idx)),







                        is_visible=bool(bg.get('is_visible', True))







                    )







            except Exception as e:







                messages.warning(request, f"Error updating internship badges: {e}")















        # G. Featured Candidates







        candidates_json = request.POST.get('candidates_json')







        if candidates_json:







            try:







                cand_data = json.loads(candidates_json)







                FeaturedCandidate.objects.all().delete()







                for idx, c in enumerate(cand_data, 1):







                    FeaturedCandidate.objects.create(







                        name=c.get('name', '').strip(),







                        role=c.get('role', '').strip(),







                        experience=c.get('experience', '').strip(),







                        avatar_color=c.get('avatar_color', 'linear-gradient(135deg,#5B7CFF,#2F3FA6)').strip(),







                        company_placed=c.get('company_placed', '').strip(),







                        show_publicly=bool(c.get('show_publicly', True)),







                        order=int(c.get('order', idx)),







                        is_visible=bool(c.get('is_visible', True))







                    )







            except Exception as e:







                messages.warning(request, f"Error updating featured candidates: {e}")















        # H. Gallery Images







        gallery_images_json = request.POST.get('gallery_images_json')







        if gallery_images_json is not None and gallery_images_json.strip() != "":







            try:







                gal_data = json.loads(gallery_images_json)







                GalleryImage.objects.all().delete()







                for idx, g in enumerate(gal_data, 1):







                    title = g.get('title', '').strip()







                    static_path = g.get('static_image_path', '').strip()







                    if not title and not static_path:







                        continue















                    show_home = g.get('show_on_home')







                    if isinstance(show_home, str):







                        show_home = show_home.lower() in ('true', '1', 'yes')







                    elif show_home is None:







                        show_home = True







                    else:







                        show_home = bool(show_home)















                    is_vis = g.get('is_visible')







                    if isinstance(is_vis, str):







                        is_vis = is_vis.lower() in ('true', '1', 'yes')







                    elif is_vis is None:







                        is_vis = True







                    else:







                        is_vis = bool(is_vis)















                    img_kwargs = {







                        'title': title or 'Corporate Event',







                        'category': g.get('category', 'Events').strip() or 'Events',







                        'show_on_home': show_home,







                        'order': idx,







                        'is_visible': is_vis







                    }







                    if static_path.startswith('/media/'):







                        img_kwargs['static_image_path'] = static_path







                    elif static_path.startswith('gallery/'):







                        img_kwargs['image'] = static_path







                        img_kwargs['static_image_path'] = f"/media/{static_path}"







                    else:







                        img_kwargs['static_image_path'] = static_path















                    GalleryImage.objects.create(**img_kwargs)







            except Exception as e:







                messages.warning(request, f"Error updating gallery images: {e}")















        # I. Gallery Info Boxes







        gallery_info_boxes_json = request.POST.get('gallery_info_boxes_json')







        if gallery_info_boxes_json:







            try:







                boxes_data = json.loads(gallery_info_boxes_json)







                GalleryInfoBox.objects.all().delete()







                for idx, gb in enumerate(boxes_data, 1):







                    GalleryInfoBox.objects.create(







                        title=gb.get('title', '').strip(),







                        text=gb.get('text', '').strip(),







                        icon_class=gb.get('icon_class', 'fa-solid fa-bullseye').strip(),







                        btn_label=gb.get('btn_label', 'Explore Now').strip(),







                        btn_url=gb.get('btn_url', '#').strip(),







                        is_popup=bool(gb.get('is_popup', False)),







                        order=int(gb.get('order', idx)),







                        is_visible=bool(gb.get('is_visible', True))







                    )







            except Exception as e:







                messages.warning(request, f"Error updating gallery info boxes: {e}")















        # Clear Cache







        cache.delete('home_page_context')







        cache.delete('public_site_context')















        # Log Activity







        actor = getattr(admin_user, 'full_name', '') or getattr(admin_user, 'username', '') or getattr(admin_user, 'name', '') or getattr(admin_user, 'email', '') or 'Admin'







        log_activity(







            'HOME_PAGE_UPDATE',







            'Home Page Updated',







            description="Admin updated Home Page hero banner, statistics, services, about, why choose, internship, and gallery.",







            actor=actor







        )















        messages.success(request, "Home Page settings and sections saved successfully! Changes are live on the website.")







        return True























@admin_required







def api_admin_upload_image(request):







    """







    Ajax endpoint for uploading gallery / website images.







    POST /api/admin/website/upload-image/







    """







    from django.core.files.storage import default_storage







    import uuid, os















    if request.method != 'POST':







        return JsonResponse({'status': 'error', 'message': 'POST method required'}, status=405)















    image_file = request.FILES.get('image')







    if not image_file:







        return JsonResponse({'status': 'error', 'message': 'No image file uploaded.'}, status=400)















    try:







        validate_image_upload(image_file, "Uploaded Image")







    except Exception as e:







        return JsonResponse({'status': 'error', 'message': str(getattr(e, 'message', e))}, status=400)















    ext = os.path.splitext(image_file.name)[1].lower() or '.jpg'







    clean_name = os.path.splitext(os.path.basename(image_file.name))[0]







    clean_name = "".join(c for c in clean_name if c.isalnum() or c in ('-', '_'))[:25] or 'gallery'







    filename = f"gallery/{clean_name}_{uuid.uuid4().hex[:8]}{ext}"















    saved_path = default_storage.save(filename, image_file)







    image_url = default_storage.url(saved_path)















    return JsonResponse({







        'status': 'success',







        'image_url': image_url,







        'file_path': saved_path,







        'message': 'Image uploaded successfully'







    })























def handle_about_page_save(request, admin_user, about_subpage='company'):







    from django.db import transaction







    from django.core.cache import cache







    from django.contrib import messages







    from apps.core.models import (







        AboutCompanySettings,







        AboutIndustryItem,







        AboutWhyCard,







        AboutTestimonial,







        AboutTestimonialStat,







        AboutTrustPoint,







        AboutPartnerLogo,







        CEOMessageSettings,







        CEOLeadershipPrinciple,







        CEOStatBadge,







        OurTeamSettings,







        TeamMember,







        TeamFeatureHighlight,







        TeamStat,







        TeamDepartment,







        TeamTrustPoint,







        TeamCoreValue,







        OurJourneySettings,







        JourneyMilestone,







        JourneyStoryParagraph,







        JourneyStoryCard,







        JourneyMilestoneCard,







        JourneyImpactItem,







        JourneyStat,







        JourneyFutureGoal,







    )







    from apps.enquiries.models import log_activity















    MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 MB







    ALLOWED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.svg')















    try:







        with transaction.atomic():







            if about_subpage == 'company':







                company = AboutCompanySettings.get_settings()







                # 1. Page Header & Welcome Banner







                company.page_title = request.POST.get('page_title', company.page_title).strip()







                company.page_eyebrow = request.POST.get('page_eyebrow', company.page_eyebrow).strip()







                company.experience_badge = request.POST.get('experience_badge', company.experience_badge).strip()







                company.visual_heading = request.POST.get('visual_heading', company.visual_heading).strip()







                company.visual_subtext = request.POST.get('visual_subtext', company.visual_subtext).strip()















                company.welcome_tag = request.POST.get('welcome_tag', company.welcome_tag).strip()







                company.welcome_heading = request.POST.get('welcome_heading', company.welcome_heading).strip()







                company.welcome_p1 = request.POST.get('welcome_p1', company.welcome_p1).strip()







                company.welcome_p2 = request.POST.get('welcome_p2', company.welcome_p2).strip()















                company.vision_title = request.POST.get('vision_title', company.vision_title).strip()







                company.vision_text = request.POST.get('vision_text', company.vision_text).strip()







                company.mission_title = request.POST.get('mission_title', company.mission_title).strip()







                company.mission_text = request.POST.get('mission_text', company.mission_text).strip()















                company.stat_1_count = request.POST.get('stat_1_count', company.stat_1_count).strip()







                company.stat_1_label = request.POST.get('stat_1_label', company.stat_1_label).strip()







                company.stat_2_count = request.POST.get('stat_2_count', company.stat_2_count).strip()







                company.stat_2_label = request.POST.get('stat_2_label', company.stat_2_label).strip()







                company.stat_3_count = request.POST.get('stat_3_count', company.stat_3_count).strip()







                company.stat_3_label = request.POST.get('stat_3_label', company.stat_3_label).strip()







                company.stat_4_count = request.POST.get('stat_4_count', company.stat_4_count).strip()







                company.stat_4_label = request.POST.get('stat_4_label', company.stat_4_label).strip()















                company.why_tag = request.POST.get('why_tag', company.why_tag).strip()







                company.why_heading = request.POST.get('why_heading', company.why_heading).strip()







                company.why_subtext = request.POST.get('why_subtext', company.why_subtext).strip()















                company.pillar_1 = request.POST.get('pillar_1', company.pillar_1).strip()







                company.pillar_2 = request.POST.get('pillar_2', company.pillar_2).strip()







                company.pillar_3 = request.POST.get('pillar_3', company.pillar_3).strip()







                company.pillar_4 = request.POST.get('pillar_4', company.pillar_4).strip()















                # Section toggles







                company.why_visible = ('why_visible' in request.POST)







                company.industries_visible = ('industries_visible' in request.POST)







                company.team_visible = ('team_visible' in request.POST)







                company.testimonials_visible = ('testimonials_visible' in request.POST)







                company.logos_visible = ('logos_visible' in request.POST)







                company.cta_visible = ('cta_visible' in request.POST)















                # Industries Section







                company.industries_tag = request.POST.get('industries_tag', company.industries_tag).strip()







                company.industries_heading = request.POST.get('industries_heading', company.industries_heading).strip()







                company.industries_subtext = request.POST.get('industries_subtext', company.industries_subtext).strip()















                # Team Section







                company.team_tag = request.POST.get('team_tag', company.team_tag).strip()







                company.team_heading_prefix = request.POST.get('team_heading_prefix', company.team_heading_prefix).strip()







                company.team_heading_highlight = request.POST.get('team_heading_highlight', company.team_heading_highlight).strip()







                company.team_subtext = request.POST.get('team_subtext', company.team_subtext).strip()







                try:







                    company.team_max_items = max(1, min(50, int(request.POST.get('team_max_items', company.team_max_items) or 20)))







                except (ValueError, TypeError):







                    company.team_max_items = 20















                # Testimonials Header







                company.tt_eyebrow = request.POST.get('tt_eyebrow', company.tt_eyebrow).strip()







                company.tt_heading_prefix = request.POST.get('tt_heading_prefix', company.tt_heading_prefix).strip()







                company.tt_highlight_1 = request.POST.get('tt_highlight_1', company.tt_highlight_1).strip()







                company.tt_heading_middle = request.POST.get('tt_heading_middle', company.tt_heading_middle).strip()







                company.tt_highlight_2 = request.POST.get('tt_highlight_2', company.tt_highlight_2).strip()







                company.tt_heading_suffix = request.POST.get('tt_heading_suffix', company.tt_heading_suffix).strip()







                company.tt_subheading = request.POST.get('tt_subheading', company.tt_subheading).strip()







                company.tt_description = request.POST.get('tt_description', company.tt_description).strip()















                # Google Reviews Card







                company.google_visible = ('google_visible' in request.POST)







                company.google_label = request.POST.get('google_label', company.google_label).strip()







                company.google_rating = request.POST.get('google_rating', company.google_rating).strip()







                try:







                    company.google_review_count = max(0, int(request.POST.get('google_review_count', company.google_review_count) or 1200))







                except (ValueError, TypeError):







                    company.google_review_count = 1200







                company.google_count_suffix = request.POST.get('google_count_suffix', company.google_count_suffix).strip()







                company.google_verified_text = request.POST.get('google_verified_text', company.google_verified_text).strip()















                # Sliders







                company.candidate_slider_title = request.POST.get('candidate_slider_title', company.candidate_slider_title).strip()







                company.candidate_slider_subtitle = request.POST.get('candidate_slider_subtitle', company.candidate_slider_subtitle).strip()







                company.employer_slider_title = request.POST.get('employer_slider_title', company.employer_slider_title).strip()







                company.employer_slider_subtitle = request.POST.get('employer_slider_subtitle', company.employer_slider_subtitle).strip()















                # Logos Marquee







                company.logos_title = request.POST.get('logos_title', company.logos_title).strip()







                company.logos_subtitle = request.POST.get('logos_subtitle', company.logos_subtitle).strip()















                # CTA Section







                company.cta_heading = request.POST.get('cta_heading', company.cta_heading).strip()







                company.cta_text = request.POST.get('cta_text', company.cta_text).strip()







                company.cta_primary_label = request.POST.get('cta_primary_label', company.cta_primary_label).strip()







                cta_raw_url = request.POST.get('cta_primary_url', company.cta_primary_url).strip()







                if cta_raw_url:







                    validate_safe_url(cta_raw_url, "Primary CTA URL")







                    company.cta_primary_url = cta_raw_url







                company.cta_franchise_visible = ('cta_franchise_visible' in request.POST)







                company.cta_franchise_label = request.POST.get('cta_franchise_label', company.cta_franchise_label).strip()







                company.cta_trophy_visible = ('cta_trophy_visible' in request.POST)















                # Visual Image







                if 'visual_image' in request.FILES:







                    validate_image_upload(request.FILES['visual_image'], "Visual Image")







                    company.visual_image = request.FILES['visual_image']







                elif request.POST.get('clear_visual_image') == '1':







                    company.visual_image = None







                company.save()















                # Repeaters Saving







                # A. Why Cards







                why_cards_raw = request.POST.get('why_cards_json')







                if why_cards_raw:







                    why_data = json.loads(why_cards_raw)







                    seen_why_ids = []







                    for idx, item in enumerate(why_data, 1):







                        item_id = item.get('id')







                        w_obj = AboutWhyCard.objects.filter(id=item_id).first() if item_id else AboutWhyCard()







                        w_obj.icon_class = (item.get('icon_class') or 'fas fa-star').strip()







                        w_obj.title = (item.get('title') or '').strip()







                        w_obj.description = (item.get('description') or '').strip()







                        w_obj.order = int(item.get('order', idx))







                        w_obj.is_visible = bool(item.get('is_visible', True))







                        w_obj.save()







                        seen_why_ids.append(w_obj.id)







                    AboutWhyCard.objects.exclude(id__in=seen_why_ids).delete()















                # B. Testimonial Stats







                testimonial_stats_raw = request.POST.get('testimonial_stats_json')







                if testimonial_stats_raw:







                    stat_data = json.loads(testimonial_stats_raw)







                    seen_stat_ids = []







                    for idx, item in enumerate(stat_data, 1):







                        item_id = item.get('id')







                        s_obj = AboutTestimonialStat.objects.filter(id=item_id).first() if item_id else AboutTestimonialStat()







                        s_obj.icon_class = (item.get('icon_class') or 'fas fa-chart-line').strip()







                        col_val = (item.get('color') or 'blue').strip().lower()







                        s_obj.color = col_val if col_val in ('blue', 'purple', 'green', 'gold') else 'blue'







                        try:







                            s_obj.count = max(0, int(item.get('count', 0)))







                        except (ValueError, TypeError):







                            s_obj.count = 0







                        s_obj.suffix = (item.get('suffix') or '').strip()







                        s_obj.label = (item.get('label') or '').strip()







                        s_obj.order = int(item.get('order', idx))







                        s_obj.is_visible = bool(item.get('is_visible', True))







                        s_obj.save()







                        seen_stat_ids.append(s_obj.id)







                    AboutTestimonialStat.objects.exclude(id__in=seen_stat_ids).delete()















                # C. Candidate Testimonials







                candidate_testimonials_raw = request.POST.get('candidate_testimonials_json')







                if candidate_testimonials_raw:







                    cand_data = json.loads(candidate_testimonials_raw)







                    seen_cand_ids = []







                    for idx, item in enumerate(cand_data, 1):







                        item_id = item.get('id')







                        t_obj = AboutTestimonial.objects.filter(id=item_id, testimonial_type='candidate').first() if item_id else AboutTestimonial(testimonial_type='candidate')







                        t_obj.name = (item.get('name') or '').strip()







                        t_obj.role = (item.get('role') or '').strip()







                        t_obj.location = (item.get('location') or '').strip()







                        t_obj.quote = (item.get('quote') or '').strip()







                        try:







                            t_obj.rating = max(1, min(5, int(item.get('rating', 5))))







                        except (ValueError, TypeError):







                            t_obj.rating = 5







                        t_obj.badge_text = (item.get('badge_text') or 'Verified Candidate').strip()







                        try:







                            t_obj.avatar_style = max(1, min(6, int(item.get('avatar_style', 1))))







                        except (ValueError, TypeError):







                            t_obj.avatar_style = 1







                        t_obj.order = int(item.get('order', idx))







                        t_obj.is_visible = bool(item.get('is_visible', True))















                        photo_key = f"candidate_photo_{item.get('temp_id', item_id)}"







                        if photo_key in request.FILES:







                            validate_image_upload(request.FILES[photo_key], "Candidate Photo")







                            t_obj.photo = request.FILES[photo_key]







                        elif item.get('clear_photo') == '1':







                            t_obj.photo = None















                        t_obj.save()







                        seen_cand_ids.append(t_obj.id)







                    AboutTestimonial.objects.filter(testimonial_type='candidate').exclude(id__in=seen_cand_ids).delete()















                # D. Employer Testimonials







                employer_testimonials_raw = request.POST.get('employer_testimonials_json')







                if employer_testimonials_raw:







                    emp_data = json.loads(employer_testimonials_raw)







                    seen_emp_ids = []







                    for idx, item in enumerate(emp_data, 1):







                        item_id = item.get('id')







                        t_obj = AboutTestimonial.objects.filter(id=item_id, testimonial_type='employer').first() if item_id else AboutTestimonial(testimonial_type='employer')







                        t_obj.name = (item.get('name') or '').strip()







                        t_obj.role = (item.get('role') or '').strip()







                        t_obj.company = (item.get('company') or '').strip()







                        t_obj.location = (item.get('location') or '').strip()







                        t_obj.quote = (item.get('quote') or '').strip()







                        try:







                            t_obj.rating = max(1, min(5, int(item.get('rating', 5))))







                        except (ValueError, TypeError):







                            t_obj.rating = 5







                        t_obj.badge_text = (item.get('badge_text') or 'Verified Hiring Partner').strip()







                        try:







                            t_obj.avatar_style = max(1, min(6, int(item.get('avatar_style', 1))))







                        except (ValueError, TypeError):







                            t_obj.avatar_style = 1







                        t_obj.order = int(item.get('order', idx))







                        t_obj.is_visible = bool(item.get('is_visible', True))















                        photo_key = f"employer_photo_{item.get('temp_id', item_id)}"







                        if photo_key in request.FILES:







                            validate_image_upload(request.FILES[photo_key], "Employer Photo")







                            t_obj.photo = request.FILES[photo_key]







                        elif item.get('clear_photo') == '1':







                            t_obj.photo = None















                        t_obj.save()







                        seen_emp_ids.append(t_obj.id)







                    AboutTestimonial.objects.filter(testimonial_type='employer').exclude(id__in=seen_emp_ids).delete()















                # E. Partner Logos







                partner_logos_raw = request.POST.get('partner_logos_json')







                if partner_logos_raw:







                    logo_data = json.loads(partner_logos_raw)







                    seen_logo_ids = []







                    for idx, item in enumerate(logo_data, 1):







                        item_id = item.get('id')







                        l_obj = AboutPartnerLogo.objects.filter(id=item_id).first() if item_id else AboutPartnerLogo()







                        l_obj.name = (item.get('name') or '').strip()







                        l_obj.icon_class = (item.get('icon_class') or '').strip()







                        l_obj.order = int(item.get('order', idx))







                        l_obj.is_visible = bool(item.get('is_visible', True))















                        logo_key = f"partner_logo_file_{item.get('temp_id', item_id)}"







                        if logo_key in request.FILES:







                            validate_image_upload(request.FILES[logo_key], "Partner Logo")







                            l_obj.logo_image = request.FILES[logo_key]







                        elif item.get('clear_logo') == '1':







                            l_obj.logo_image = None















                        l_obj.save()







                        seen_logo_ids.append(l_obj.id)







                    AboutPartnerLogo.objects.exclude(id__in=seen_logo_ids).delete()















                # F. Trust Points







                trust_points_raw = request.POST.get('trust_points_json')







                if trust_points_raw:







                    tp_data = json.loads(trust_points_raw)







                    seen_tp_ids = []







                    for idx, item in enumerate(tp_data, 1):







                        item_id = item.get('id')







                        tp_obj = AboutTrustPoint.objects.filter(id=item_id).first() if item_id else AboutTrustPoint()







                        tp_obj.icon_class = (item.get('icon_class') or 'fas fa-shield-alt').strip()







                        tp_obj.title = (item.get('title') or '').strip()







                        tp_obj.text = (item.get('text') or '').strip()







                        tp_obj.order = int(item.get('order', idx))







                        tp_obj.is_visible = bool(item.get('is_visible', True))







                        tp_obj.save()







                        seen_tp_ids.append(tp_obj.id)







                    AboutTrustPoint.objects.exclude(id__in=seen_tp_ids).delete()















                # G. Team Members on About Page







                about_team_raw = request.POST.get('about_team_json')







                if about_team_raw:







                    try:







                        t_data = json.loads(about_team_raw)







                        for item in t_data:







                            m_id = item.get('id')







                            if m_id:







                                m_obj = TeamMember.objects.filter(id=m_id).first()







                                if m_obj:







                                    m_obj.show_on_about_page = bool(item.get('show_on_about_page', False))







                                    m_obj.about_page_order = int(item.get('about_page_order', 0))







                                    m_obj.save(update_fields=['show_on_about_page', 'about_page_order'])







                    except Exception:







                        pass







                else:







                    for member in TeamMember.objects.all():







                        chk_name = f"show_on_about_{member.id}"







                        ord_name = f"about_order_{member.id}"







                        if chk_name in request.POST or ord_name in request.POST or 'team_form_submitted' in request.POST:







                            member.show_on_about_page = (chk_name in request.POST)







                            try:







                                member.about_page_order = int(request.POST.get(ord_name, member.about_page_order) or 0)







                            except (ValueError, TypeError):







                                pass







                            member.save(update_fields=['show_on_about_page', 'about_page_order'])















                # H. Industries We Serve Items







                about_industries_raw = request.POST.get('about_industries_json')







                if about_industries_raw:







                    ind_data = json.loads(about_industries_raw)







                    seen_ind_ids = []







                    for idx, item in enumerate(ind_data, 1):







                        item_id = item.get('id')







                        ind_obj = AboutIndustryItem.objects.filter(id=item_id).first() if item_id else AboutIndustryItem()







                        ind_obj.name = (item.get('name') or '').strip()







                        if not ind_obj.name:







                            continue







                        ind_obj.icon_class = (item.get('icon_class') or 'fas fa-industry').strip()







                        raw_link = (item.get('link_url') or '').strip()







                        if raw_link:







                            validate_safe_url(raw_link, "Industry Link URL")







                        ind_obj.link_url = raw_link







                        ind_obj.order = int(item.get('order', idx))







                        ind_obj.is_visible = bool(item.get('is_visible', True))







                        ind_obj.save()







                        seen_ind_ids.append(ind_obj.id)







                    AboutIndustryItem.objects.exclude(id__in=seen_ind_ids).delete()















            elif about_subpage == 'ceo':







                from django.core.exceptions import ValidationError







                ceo_msg = CEOMessageSettings.get_settings()















                # Section toggles







                if 'ceo_has_toggles' in request.POST or any(k in request.POST for k in ('hero_visible', 'profile_visible', 'message_visible', 'principles_visible', 'vm_visible', 'cta_visible')):







                    ceo_msg.hero_visible = ('hero_visible' in request.POST)







                    ceo_msg.profile_visible = ('profile_visible' in request.POST)







                    ceo_msg.message_visible = ('message_visible' in request.POST)







                    ceo_msg.principles_visible = ('principles_visible' in request.POST)







                    ceo_msg.vm_visible = ('vm_visible' in request.POST)







                    ceo_msg.cta_visible = ('cta_visible' in request.POST)















                # Hero / Header Banner







                ceo_msg.page_title = request.POST.get('page_title', ceo_msg.page_title).strip()







                ceo_msg.page_eyebrow = request.POST.get('page_eyebrow', ceo_msg.page_eyebrow).strip()







                ceo_msg.hero_subtitle = request.POST.get('hero_subtitle', ceo_msg.hero_subtitle).strip()







                ceo_msg.breadcrumb_title = request.POST.get('breadcrumb_title', ceo_msg.breadcrumb_title).strip()















                # CEO Profile Card







                ceo_name_input = request.POST.get('ceo_name', ceo_msg.ceo_name).strip()







                if not ceo_name_input:







                    raise ValidationError("CEO Full Name is required.")







                ceo_msg.ceo_name = ceo_name_input







                ceo_msg.ceo_role = request.POST.get('ceo_role', ceo_msg.ceo_role).strip()







                ceo_msg.ceo_org = request.POST.get('ceo_org', ceo_msg.ceo_org).strip()







                ceo_msg.ceo_tagline = request.POST.get('ceo_tagline', ceo_msg.ceo_tagline).strip()







                ceo_msg.ceo_photo_alt = request.POST.get('ceo_photo_alt', ceo_msg.ceo_photo_alt).strip()















                # Message Copy







                ceo_msg.title_eyebrow = request.POST.get('title_eyebrow', ceo_msg.title_eyebrow).strip()







                ceo_msg.title_main = request.POST.get('title_main', ceo_msg.title_main).strip()







                ceo_msg.message_p1 = request.POST.get('message_p1', ceo_msg.message_p1).strip()







                ceo_msg.message_p2 = request.POST.get('message_p2', ceo_msg.message_p2).strip()







                ceo_msg.message_p3 = request.POST.get('message_p3', ceo_msg.message_p3).strip()







                ceo_msg.message_p4 = request.POST.get('message_p4', ceo_msg.message_p4).strip()







                ceo_msg.quote_text = request.POST.get('quote_text', ceo_msg.quote_text).strip()







                ceo_msg.closing_text = request.POST.get('closing_text', ceo_msg.closing_text).strip()







                ceo_msg.signoff_text = request.POST.get('signoff_text', ceo_msg.signoff_text).strip()















                # Principles Section Heading







                ceo_msg.principles_tag = request.POST.get('principles_tag', ceo_msg.principles_tag).strip()







                ceo_msg.principles_title = request.POST.get('principles_title', ceo_msg.principles_title).strip()







                ceo_msg.principles_subtitle = request.POST.get('principles_subtitle', ceo_msg.principles_subtitle).strip()















                # Vision & Mission







                ceo_msg.vision_title = request.POST.get('vision_title', ceo_msg.vision_title).strip()







                ceo_msg.vision_icon = request.POST.get('vision_icon', ceo_msg.vision_icon).strip() or "fa-solid fa-eye"







                ceo_msg.vision_text = request.POST.get('vision_text', ceo_msg.vision_text).strip()







                ceo_msg.mission_title = request.POST.get('mission_title', ceo_msg.mission_title).strip()







                ceo_msg.mission_icon = request.POST.get('mission_icon', ceo_msg.mission_icon).strip() or "fa-solid fa-bullseye"







                ceo_msg.mission_text = request.POST.get('mission_text', ceo_msg.mission_text).strip()















                # Signature & Contact







                ceo_msg.signature_name = request.POST.get('signature_name', ceo_msg.signature_name).strip()















                raw_linkedin = request.POST.get('linkedin_url', '').strip()







                if raw_linkedin:







                    validate_safe_url(raw_linkedin, "LinkedIn URL")







                ceo_msg.linkedin_url = raw_linkedin















                raw_fb = request.POST.get('facebook_url', '').strip()







                if raw_fb:







                    validate_safe_url(raw_fb, "Facebook URL")







                ceo_msg.facebook_url = raw_fb















                raw_tw = request.POST.get('twitter_url', '').strip()







                if raw_tw:







                    validate_safe_url(raw_tw, "Twitter/X URL")







                ceo_msg.twitter_url = raw_tw















                raw_ig = request.POST.get('instagram_url', '').strip()







                if raw_ig:







                    validate_safe_url(raw_ig, "Instagram URL")







                ceo_msg.instagram_url = raw_ig















                email_input = request.POST.get('email_address', '').strip()







                if email_input:







                    from django.core.validators import validate_email







                    try:







                        validate_email(email_input)







                    except Exception:







                        raise ValidationError("Please provide a valid email address.")







                ceo_msg.email_address = email_input















                # Bottom CTA Section







                ceo_msg.cta_heading = request.POST.get('cta_heading', ceo_msg.cta_heading).strip()







                ceo_msg.cta_text = request.POST.get('cta_text', ceo_msg.cta_text).strip()







                ceo_msg.cta_btn_label = request.POST.get('cta_btn_label', ceo_msg.cta_btn_label).strip()







                raw_cta_url = request.POST.get('cta_btn_url', '').strip()







                if raw_cta_url:







                    validate_safe_url(raw_cta_url, "Primary CTA URL")







                ceo_msg.cta_btn_url = raw_cta_url















                ceo_msg.cta_btn2_label = request.POST.get('cta_btn2_label', ceo_msg.cta_btn2_label).strip()







                raw_cta2_url = request.POST.get('cta_btn2_url', '').strip()







                if raw_cta2_url:







                    validate_safe_url(raw_cta2_url, "Secondary CTA URL")







                ceo_msg.cta_btn2_url = raw_cta2_url















                # SEO & Meta







                ceo_msg.meta_title = request.POST.get('meta_title', ceo_msg.meta_title).strip()







                ceo_msg.meta_description = request.POST.get('meta_description', ceo_msg.meta_description).strip()















                # Images Handling







                # 1. CEO Portrait







                if request.POST.get('remove_ceo_photo') == '1':







                    ceo_msg.ceo_photo = None







                elif 'ceo_photo' in request.FILES:







                    c_file = request.FILES['ceo_photo']







                    ext = os.path.splitext(c_file.name)[1].lower()







                    if ext not in ALLOWED_EXTENSIONS or c_file.size > MAX_FILE_BYTES:







                        raise ValidationError("CEO portrait must be a valid image (JPG, PNG, WEBP) under 5MB.")







                    ceo_msg.ceo_photo = c_file















                # 2. Signature Image







                if request.POST.get('remove_signature_image') == '1':







                    ceo_msg.signature_image = None







                elif 'signature_image' in request.FILES:







                    s_file = request.FILES['signature_image']







                    ext = os.path.splitext(s_file.name)[1].lower()







                    if ext not in ALLOWED_EXTENSIONS or s_file.size > MAX_FILE_BYTES:







                        raise ValidationError("Signature image must be a valid image (JPG, PNG, WEBP, SVG) under 5MB.")







                    ceo_msg.signature_image = s_file















                # 3. Hero Background Image







                if request.POST.get('remove_hero_bg_image') == '1':







                    ceo_msg.hero_bg_image = None







                elif 'hero_bg_image' in request.FILES:







                    h_file = request.FILES['hero_bg_image']







                    ext = os.path.splitext(h_file.name)[1].lower()







                    if ext not in ALLOWED_EXTENSIONS or h_file.size > MAX_FILE_BYTES:







                        raise ValidationError("Hero background banner must be a valid image (JPG, PNG, WEBP) under 5MB.")







                    ceo_msg.hero_bg_image = h_file















                # 4. OG Image







                if request.POST.get('remove_og_image') == '1':







                    ceo_msg.og_image = None







                elif 'og_image' in request.FILES:







                    o_file = request.FILES['og_image']







                    ext = os.path.splitext(o_file.name)[1].lower()







                    if ext not in ALLOWED_EXTENSIONS or o_file.size > MAX_FILE_BYTES:







                        raise ValidationError("OG Image must be a valid image (JPG, PNG, WEBP) under 5MB.")







                    ceo_msg.og_image = o_file















                ceo_msg.save()















                # Principles JSON handling







                principles_raw = request.POST.get('principles_json')







                if principles_raw:







                    try:







                        principles_data = json.loads(principles_raw)







                        seen_ids = []







                        for idx, item in enumerate(principles_data, 1):







                            item_id = item.get('id')







                            p_obj = None







                            if item_id:







                                p_obj = CEOLeadershipPrinciple.objects.filter(id=item_id).first()







                            if not p_obj:







                                p_obj = CEOLeadershipPrinciple()







                            p_title = (item.get('title') or '').strip()







                            if not p_title:







                                continue







                            p_obj.title = p_title







                            p_obj.description = (item.get('description') or '').strip()







                            p_obj.icon_class = (item.get('icon_class') or 'fa-solid fa-shield-halved').strip()







                            p_obj.order = int(item.get('order', idx))







                            p_obj.is_visible = bool(item.get('is_visible', True))







                            p_obj.save()







                            seen_ids.append(p_obj.id)







                        CEOLeadershipPrinciple.objects.exclude(id__in=seen_ids).delete()







                    except (json.JSONDecodeError, ValueError):







                        pass















                # Stats Badges JSON handling







                stats_raw = request.POST.get('ceo_stats_json') or request.POST.get('ceo_stat_badges_json')







                if stats_raw:







                    try:







                        stats_data = json.loads(stats_raw)







                        seen_s_ids = []







                        for idx, item in enumerate(stats_data, 1):







                            item_id = item.get('id')







                            s_obj = None







                            if item_id:







                                s_obj = CEOStatBadge.objects.filter(id=item_id).first()







                            if not s_obj:







                                s_obj = CEOStatBadge()







                            val = (item.get('value') or '').strip()







                            lbl = (item.get('label') or '').strip()







                            if not val and not lbl:







                                continue







                            s_obj.value = val







                            s_obj.label = lbl







                            s_obj.icon_class = (item.get('icon_class') or 'fa-solid fa-award').strip()







                            s_obj.order = int(item.get('order', idx))







                            s_obj.is_visible = bool(item.get('is_visible', True))







                            s_obj.save()







                            seen_s_ids.append(s_obj.id)







                        CEOStatBadge.objects.exclude(id__in=seen_s_ids).delete()







                    except (json.JSONDecodeError, ValueError):







                        pass























            elif about_subpage == 'team':







                from django.core.exceptions import ValidationError







                team_set = OurTeamSettings.get_settings()















                # Master and section visibility toggles







                if 'team_has_toggles' in request.POST or any(k in request.POST for k in (







                    'hero_visible', 'about_visible', 'leadership_visible', 'specialists_visible',







                    'departments_visible', 'stats_visible', 'trust_visible', 'values_visible',







                    'quote_visible', 'cta_visible'







                )):







                    team_set.hero_visible = ('hero_visible' in request.POST)







                    team_set.about_visible = ('about_visible' in request.POST)







                    team_set.leadership_visible = ('leadership_visible' in request.POST)







                    team_set.specialists_visible = ('specialists_visible' in request.POST)







                    team_set.departments_visible = ('departments_visible' in request.POST)







                    team_set.stats_visible = ('stats_visible' in request.POST)







                    team_set.trust_visible = ('trust_visible' in request.POST)







                    team_set.values_visible = ('values_visible' in request.POST)







                    team_set.quote_visible = ('quote_visible' in request.POST)







                    team_set.cta_visible = ('cta_visible' in request.POST)















                # Section A: Hero Banner







                team_set.hero_eyebrow = request.POST.get('hero_eyebrow', team_set.hero_eyebrow).strip()







                team_set.hero_title = request.POST.get('hero_title', team_set.hero_title).strip()







                team_set.hero_description = request.POST.get('hero_description', team_set.hero_description).strip()







                team_set.hero_btn1_text = request.POST.get('hero_btn1_text', team_set.hero_btn1_text).strip()







                raw_h_btn1_url = request.POST.get('hero_btn1_url', '').strip()







                if raw_h_btn1_url:







                    validate_safe_url(raw_h_btn1_url, "Hero Primary Button URL")







                team_set.hero_btn1_url = raw_h_btn1_url















                team_set.hero_btn2_text = request.POST.get('hero_btn2_text', team_set.hero_btn2_text).strip()







                raw_h_btn2_url = request.POST.get('hero_btn2_url', '').strip()







                if raw_h_btn2_url:







                    validate_safe_url(raw_h_btn2_url, "Hero Secondary Button URL")







                team_set.hero_btn2_url = raw_h_btn2_url















                if request.POST.get('remove_hero_image') == '1':







                    team_set.hero_image = None







                elif 'hero_image' in request.FILES:







                    validate_image_upload(request.FILES['hero_image'], "Hero Banner Image")







                    team_set.hero_image = request.FILES['hero_image']















                # Section B: About Our Team







                team_set.about_eyebrow = request.POST.get('about_eyebrow', team_set.about_eyebrow).strip()







                about_hd = request.POST.get('about_heading') or request.POST.get('about_title')







                if about_hd:







                    team_set.about_heading = about_hd.strip()







                team_set.about_description = request.POST.get('about_description', team_set.about_description).strip()















                if request.POST.get('remove_about_image') == '1':







                    team_set.about_image = None







                elif 'about_image' in request.FILES:







                    validate_image_upload(request.FILES['about_image'], "About Section Image")







                    team_set.about_image = request.FILES['about_image']















                # Section C: Leadership Team







                team_set.leadership_tag = request.POST.get('leadership_tag', team_set.leadership_tag).strip()







                lead_clean = request.POST.get('leadership_clean_title', '').strip()







                lead_hl = request.POST.get('leadership_highlight_word', '').strip()







                lead_hd = request.POST.get('leadership_title', '').strip()







                if lead_clean and lead_hl and lead_hl.lower() in lead_clean.lower():







                    import re







                    team_set.leadership_title = re.sub(re.escape(lead_hl), f"<span>{lead_hl}</span>", lead_clean, count=1, flags=re.IGNORECASE)







                elif lead_clean:







                    team_set.leadership_title = lead_clean







                elif lead_hd:







                    team_set.leadership_title = lead_hd







                team_set.leadership_subtitle = request.POST.get('leadership_subtitle', team_set.leadership_subtitle).strip()







                try:







                    team_set.leadership_max_items = max(1, min(50, int(request.POST.get('leadership_max_items', team_set.leadership_max_items) or 4)))







                except (ValueError, TypeError):







                    team_set.leadership_max_items = 4















                # Section D: Recruitment Specialists







                team_set.specialists_tag = request.POST.get('specialists_tag', team_set.specialists_tag).strip()







                spec_clean = request.POST.get('specialists_clean_title', '').strip()







                spec_hl = request.POST.get('specialists_highlight_word', '').strip()







                spec_hd = request.POST.get('specialists_title', '').strip()







                if spec_clean and spec_hl and spec_hl.lower() in spec_clean.lower():







                    import re







                    team_set.specialists_title = re.sub(re.escape(spec_hl), f"<span>{spec_hl}</span>", spec_clean, count=1, flags=re.IGNORECASE)







                elif spec_clean:







                    team_set.specialists_title = spec_clean







                elif spec_hd:







                    team_set.specialists_title = spec_hd







                team_set.specialists_subtitle = request.POST.get('specialists_subtitle', team_set.specialists_subtitle).strip()







                try:







                    team_set.specialists_max_items = max(1, min(50, int(request.POST.get('specialists_max_items', team_set.specialists_max_items) or 4)))







                except (ValueError, TypeError):







                    team_set.specialists_max_items = 4















                # Section E: Departments Marquee







                team_set.departments_tag = request.POST.get('departments_tag', team_set.departments_tag).strip()







                dept_clean = request.POST.get('departments_clean_title', '').strip()







                dept_hl = request.POST.get('departments_highlight_word', '').strip()







                dept_hd = request.POST.get('departments_title', '').strip()







                if dept_clean and dept_hl and dept_hl.lower() in dept_clean.lower():







                    import re







                    team_set.departments_title = re.sub(re.escape(dept_hl), f"<span>{dept_hl}</span>", dept_clean, count=1, flags=re.IGNORECASE)







                elif dept_clean:







                    team_set.departments_title = dept_clean







                elif dept_hd:







                    team_set.departments_title = dept_hd







                team_set.departments_subtitle = request.POST.get('departments_subtitle', team_set.departments_subtitle).strip()















                # Section G: Why Clients Trust Our Team







                team_set.trust_tag = request.POST.get('trust_tag', team_set.trust_tag).strip()







                trust_clean = request.POST.get('trust_clean_title', '').strip()







                trust_hl = request.POST.get('trust_highlight_word', '').strip()







                trust_hd = request.POST.get('trust_heading') or request.POST.get('trust_title')







                if trust_clean and trust_hl and trust_hl.lower() in trust_clean.lower():







                    import re







                    team_set.trust_heading = re.sub(re.escape(trust_hl), f"<span>{trust_hl}</span>", trust_clean, count=1, flags=re.IGNORECASE)







                elif trust_clean:







                    team_set.trust_heading = trust_clean







                elif trust_hd:







                    team_set.trust_heading = trust_hd.strip()







                team_set.trust_subtitle = request.POST.get('trust_subtitle', team_set.trust_subtitle).strip()















                if request.POST.get('remove_trust_image') == '1':







                    team_set.trust_image = None







                elif 'trust_image' in request.FILES:







                    validate_image_upload(request.FILES['trust_image'], "Trust Section Image")







                    team_set.trust_image = request.FILES['trust_image']















                # Section H: Our Core Values







                team_set.values_tag = request.POST.get('values_tag', team_set.values_tag).strip()







                val_clean = request.POST.get('values_clean_title', '').strip()







                val_hl = request.POST.get('values_highlight_word', '').strip()







                val_hd = request.POST.get('values_heading') or request.POST.get('values_title')







                if val_clean and val_hl and val_hl.lower() in val_clean.lower():







                    import re







                    team_set.values_heading = re.sub(re.escape(val_hl), f"<span>{val_hl}</span>", val_clean, count=1, flags=re.IGNORECASE)







                elif val_clean:







                    team_set.values_heading = val_clean







                elif val_hd:







                    team_set.values_heading = val_hd.strip()







                team_set.values_subtitle = request.POST.get('values_subtitle', team_set.values_subtitle).strip()















                # Section I: Leadership Quote Band







                team_set.quote_text = request.POST.get('quote_text', team_set.quote_text).strip()







                team_set.quote_author_name = request.POST.get('quote_author_name', team_set.quote_author_name).strip()







                team_set.quote_author_role = request.POST.get('quote_author_role', team_set.quote_author_role).strip()















                if request.POST.get('remove_quote_author_image') == '1':







                    team_set.quote_author_image = None







                elif 'quote_author_image' in request.FILES:







                    validate_image_upload(request.FILES['quote_author_image'], "Quote Author Image")







                    team_set.quote_author_image = request.FILES['quote_author_image']















                # Section J: Want to Work With Us? (CTA)







                team_set.cta_icon = request.POST.get('cta_icon', team_set.cta_icon).strip() or 'fa-solid fa-handshake'







                team_set.cta_heading = request.POST.get('cta_heading', team_set.cta_heading).strip()







                cta_txt = request.POST.get('cta_description') or request.POST.get('cta_text')







                if cta_txt is not None:







                    team_set.cta_description = cta_txt.strip()







                team_set.cta_btn1_text = request.POST.get('cta_btn1_text', team_set.cta_btn1_text).strip()







                raw_cta_btn1_url = request.POST.get('cta_btn1_url', '').strip()







                if raw_cta_btn1_url:







                    validate_safe_url(raw_cta_btn1_url, "CTA Primary Button URL")







                team_set.cta_btn1_url = raw_cta_btn1_url















                team_set.cta_btn2_text = request.POST.get('cta_btn2_text', team_set.cta_btn2_text).strip()







                raw_cta_btn2_url = request.POST.get('cta_btn2_url', '').strip()







                if raw_cta_btn2_url:







                    validate_safe_url(raw_cta_btn2_url, "CTA Secondary Button URL")







                team_set.cta_btn2_url = raw_cta_btn2_url















                # Section K: SEO & Meta







                team_set.meta_title = request.POST.get('meta_title', team_set.meta_title).strip()







                team_set.meta_description = request.POST.get('meta_description', team_set.meta_description).strip()















                if request.POST.get('remove_og_image') == '1':







                    team_set.og_image = None







                elif 'og_image' in request.FILES:







                    validate_image_upload(request.FILES['og_image'], "OG Social Image")







                    team_set.og_image = request.FILES['og_image']















                team_set.save()















                # Repeaters Saving:







                # 1. TeamFeatureHighlight (Section B)







                highlights_raw = request.POST.get('team_highlights_json')







                if highlights_raw:







                    try:







                        h_data = json.loads(highlights_raw)







                        seen_h_ids = []







                        for idx, item in enumerate(h_data, 1):







                            item_id = item.get('id')







                            h_obj = TeamFeatureHighlight.objects.filter(id=item_id).first() if item_id else TeamFeatureHighlight()







                            h_title = str(item.get('title') or '').strip()







                            if not h_title:







                                continue







                            h_obj.title = h_title







                            h_obj.description = str(item.get('description') or '').strip()







                            h_obj.icon = str(item.get('icon') or item.get('icon_class') or '👥').strip()







                            h_obj.order = int(item.get('order', idx))







                            h_obj.is_visible = bool(item.get('is_visible', True))







                            h_obj.save()







                            seen_h_ids.append(h_obj.id)







                        TeamFeatureHighlight.objects.exclude(id__in=seen_h_ids).delete()







                    except (json.JSONDecodeError, ValueError, Exception):







                        pass















                # 2. TeamStat (Section F)







                stats_raw = request.POST.get('team_stats_json')







                if stats_raw:







                    try:







                        s_data = json.loads(stats_raw)







                        seen_s_ids = []







                        for idx, item in enumerate(s_data, 1):







                            item_id = item.get('id')







                            s_obj = TeamStat.objects.filter(id=item_id).first() if item_id else TeamStat()







                            cnt_val = item.get('count')







                            s_obj.count = str(cnt_val).strip() if cnt_val is not None else ''







                            s_obj.suffix = str(item.get('suffix') or '').strip()







                            s_obj.label = str(item.get('label') or '').strip()







                            s_obj.static_text = str(item.get('static_text') or '').strip()







                            if not s_obj.label and not s_obj.count and not s_obj.static_text:







                                continue







                            s_obj.icon = str(item.get('icon') or item.get('icon_class') or '👥').strip()







                            s_obj.order = int(item.get('order', idx))







                            s_obj.is_visible = bool(item.get('is_visible', True))







                            s_obj.save()







                            seen_s_ids.append(s_obj.id)







                        TeamStat.objects.exclude(id__in=seen_s_ids).delete()







                    except (json.JSONDecodeError, ValueError, Exception):







                        pass















                # 3. TeamDepartment (Section E)







                depts_raw = request.POST.get('team_departments_json')







                if depts_raw:







                    try:







                        d_data = json.loads(depts_raw)







                        seen_d_ids = []







                        for idx, item in enumerate(d_data, 1):







                            item_id = item.get('id')







                            d_obj = TeamDepartment.objects.filter(id=item_id).first() if item_id else TeamDepartment()







                            d_name = str(item.get('name') or '').strip()







                            if not d_name:







                                continue







                            d_obj.name = d_name







                            d_obj.icon = str(item.get('icon') or item.get('icon_class') or '👔').strip()







                            d_obj.description = str(item.get('description') or item.get('count_badge') or '').strip()







                            d_img_url = str(item.get('image_url') or '').strip()







                            d_obj.image_url = d_img_url







                            if d_obj.image and d_img_url:







                                try:







                                    if d_obj.image.url != d_img_url:







                                        d_obj.image = None







                                except Exception:







                                    d_obj.image = None















                            img_file_key = f"dept_image_{item.get('temp_id', item_id)}"







                            if img_file_key in request.FILES:







                                validate_image_upload(request.FILES[img_file_key], f"Department {d_name} Image")







                                d_obj.image = request.FILES[img_file_key]















                            d_obj.team_size = str(item.get('team_size') or item.get('count_badge') or '').strip()







                            d_obj.order = int(item.get('order', idx))







                            d_obj.is_visible = bool(item.get('is_visible', True))







                            d_obj.save()







                            seen_d_ids.append(d_obj.id)







                        TeamDepartment.objects.exclude(id__in=seen_d_ids).delete()







                    except (json.JSONDecodeError, ValueError, Exception):







                        pass















                # 4. TeamTrustPoint (Section G)







                trust_raw = request.POST.get('team_trust_points_json')







                if trust_raw:







                    try:







                        tp_data = json.loads(trust_raw)







                        seen_tp_ids = []







                        for idx, item in enumerate(tp_data, 1):







                            item_id = item.get('id')







                            tp_obj = TeamTrustPoint.objects.filter(id=item_id).first() if item_id else TeamTrustPoint()







                            tp_text = str(item.get('title') or item.get('text') or '').strip()







                            if not tp_text:







                                continue







                            tp_obj.title = tp_text







                            tp_obj.icon_class = str(item.get('icon_class') or '✓').strip()







                            tp_obj.order = int(item.get('order', idx))







                            tp_obj.is_visible = bool(item.get('is_visible', True))







                            tp_obj.save()







                            seen_tp_ids.append(tp_obj.id)







                        TeamTrustPoint.objects.exclude(id__in=seen_tp_ids).delete()







                    except (json.JSONDecodeError, ValueError, Exception):







                        pass















                # 5. TeamCoreValue (Section H)







                values_raw = request.POST.get('team_values_json')







                if values_raw:







                    try:







                        v_data = json.loads(values_raw)







                        seen_v_ids = []







                        for idx, item in enumerate(v_data, 1):







                            item_id = item.get('id')







                            v_obj = TeamCoreValue.objects.filter(id=item_id).first() if item_id else TeamCoreValue()







                            v_title = str(item.get('title') or '').strip()







                            if not v_title:







                                continue







                            v_obj.title = v_title







                            v_obj.description = str(item.get('description') or '').strip()







                            v_obj.icon = str(item.get('icon') or item.get('icon_class') or '🤝').strip()







                            v_obj.order = int(item.get('order', idx))







                            v_obj.is_visible = bool(item.get('is_visible', True))







                            v_obj.save()







                            seen_v_ids.append(v_obj.id)







                        TeamCoreValue.objects.exclude(id__in=seen_v_ids).delete()







                    except (json.JSONDecodeError, ValueError, Exception):







                        pass















                # 6. TeamMember (Sections C & D)







                team_raw = request.POST.get('team_members_json')







                if team_raw:







                    try:







                        team_data = json.loads(team_raw)







                        seen_ids = []







                        for idx, item in enumerate(team_data):







                            item_id = item.get('id')







                            m_obj = None







                            if item_id:







                                m_obj = TeamMember.objects.filter(id=item_id).first()







                            if not m_obj:







                                m_obj = TeamMember()







                            m_name = (item.get('name') or '').strip()







                            if not m_name:







                                continue







                            m_obj.name = m_name







                            m_obj.role = (item.get('role') or '').strip()







                            cat = (item.get('category') or 'leadership').strip().lower()







                            m_obj.category = cat if cat in ('leadership', 'specialist') else 'leadership'







                            m_obj.bio = (item.get('bio') or '').strip()







                            m_obj.experience_text = (item.get('experience_text') or '').strip()







                            raw_lk = (item.get('linkedin_url') or '').strip()







                            if raw_lk and raw_lk != '#':







                                validate_safe_url(raw_lk, f"Member {m_name} LinkedIn URL")







                            m_obj.linkedin_url = raw_lk or '#'







                            raw_em = (item.get('email_url') or '').strip()







                            if raw_em and raw_em != '#':







                                validate_safe_url(raw_em, f"Member {m_name} Email URL")







                            m_obj.email_url = raw_em or '#'







                            m_obj.static_photo_path = (item.get('static_photo_path') or '').strip()







                            m_obj.order = int(item.get('order', idx + 1))







                            m_obj.is_visible = bool(item.get('is_visible', True))















                            photo_file_key = f"member_photo_{item.get('temp_id', item_id)}"







                            if photo_file_key in request.FILES:







                                validate_image_upload(request.FILES[photo_file_key], f"Member {m_name} Photo")







                                m_obj.photo = request.FILES[photo_file_key]







                            elif item.get('clear_photo') == '1':







                                m_obj.photo = None















                            m_obj.save()







                            seen_ids.append(m_obj.id)







                        TeamMember.objects.exclude(id__in=seen_ids).delete()







                    except (json.JSONDecodeError, ValueError):







                        pass















            elif about_subpage == 'journey':







                j_set = OurJourneySettings.get_settings()















                # Master and section visibility toggles







                if 'journey_has_toggles' in request.POST or any(k in request.POST for k in (







                    'hero_visible', 'story_visible', 'timeline_visible', 'milestones_visible',







                    'impact_visible', 'numbers_visible', 'ahead_visible'







                )):







                    j_set.hero_visible = ('hero_visible' in request.POST)







                    j_set.story_visible = ('story_visible' in request.POST)







                    j_set.timeline_visible = ('timeline_visible' in request.POST)







                    j_set.milestones_visible = ('milestones_visible' in request.POST)







                    j_set.impact_visible = ('impact_visible' in request.POST)







                    j_set.numbers_visible = ('numbers_visible' in request.POST)







                    j_set.ahead_visible = ('ahead_visible' in request.POST)















                # Section 1: Hero Banner







                j_set.hero_eyebrow = request.POST.get('hero_eyebrow', j_set.hero_eyebrow).strip()







                hero_clean = request.POST.get('hero_clean_title', '').strip()







                hero_hl = request.POST.get('hero_highlight_word', '').strip()







                hero_hd = request.POST.get('hero_title', '').strip()







                if hero_clean and hero_hl and hero_hl.lower() in hero_clean.lower():







                    import re







                    j_set.hero_title = re.sub(re.escape(hero_hl), f"<span>{hero_hl}</span>", hero_clean, count=1, flags=re.IGNORECASE)







                    j_set.hero_highlight = hero_hl







                elif hero_clean:







                    j_set.hero_title = hero_clean







                    j_set.hero_highlight = hero_hl







                elif hero_hd:







                    j_set.hero_title = hero_hd















                j_set.hero_description = request.POST.get('hero_description', j_set.hero_description).strip()







                j_set.badge_num = request.POST.get('badge_num', j_set.badge_num).strip()







                j_set.badge_text = request.POST.get('badge_text', j_set.badge_text).strip()















                j_set.hero_btn1_text = request.POST.get('hero_btn1_text', j_set.hero_btn1_text).strip()







                raw_h_btn1_url = request.POST.get('hero_btn1_url', '').strip()







                if raw_h_btn1_url:







                    validate_safe_url(raw_h_btn1_url, "Hero Primary Button URL")







                j_set.hero_btn1_url = raw_h_btn1_url















                j_set.hero_btn2_text = request.POST.get('hero_btn2_text', j_set.hero_btn2_text).strip()







                raw_h_btn2_url = request.POST.get('hero_btn2_url', '').strip()







                if raw_h_btn2_url:







                    validate_safe_url(raw_h_btn2_url, "Hero Secondary Button URL")







                j_set.hero_btn2_url = raw_h_btn2_url















                j_set.stat1_num = request.POST.get('stat1_num', j_set.stat1_num).strip()







                j_set.stat1_label = request.POST.get('stat1_label', j_set.stat1_label).strip()







                j_set.stat2_num = request.POST.get('stat2_num', j_set.stat2_num).strip()







                j_set.stat2_label = request.POST.get('stat2_label', j_set.stat2_label).strip()







                j_set.stat3_num = request.POST.get('stat3_num', j_set.stat3_num).strip()







                j_set.stat3_label = request.POST.get('stat3_label', j_set.stat3_label).strip()















                if request.POST.get('remove_hero_image') == '1':







                    j_set.hero_image = None







                elif 'hero_image' in request.FILES:







                    validate_image_upload(request.FILES['hero_image'], "Hero Banner Image")







                    j_set.hero_image = request.FILES['hero_image']















                # Section 2: Our Story







                j_set.story_tag = request.POST.get('story_tag', j_set.story_tag).strip()







                story_clean = request.POST.get('story_clean_title', '').strip()







                story_hl = request.POST.get('story_highlight_word', '').strip()







                story_hd = request.POST.get('story_title', '').strip()







                if story_clean and story_hl and story_hl.lower() in story_clean.lower():







                    import re







                    j_set.story_title = re.sub(re.escape(story_hl), f"<span>{story_hl}</span>", story_clean, count=1, flags=re.IGNORECASE)







                    j_set.story_highlight = story_hl







                elif story_clean:







                    j_set.story_title = story_clean







                    j_set.story_highlight = story_hl







                elif story_hd:







                    j_set.story_title = story_hd















                j_set.story_p1 = request.POST.get('story_p1', j_set.story_p1).strip()







                j_set.story_p2 = request.POST.get('story_p2', j_set.story_p2).strip()







                j_set.story_p3 = request.POST.get('story_p3', j_set.story_p3).strip()















                if request.POST.get('remove_story_image') == '1':







                    j_set.story_image = None







                elif 'story_image' in request.FILES:







                    validate_image_upload(request.FILES['story_image'], "Story Section Image")







                    j_set.story_image = request.FILES['story_image']















                # Section 3: Growth Timeline







                j_set.timeline_tag = request.POST.get('timeline_tag', j_set.timeline_tag).strip()







                tl_clean = request.POST.get('timeline_clean_title', '').strip()







                tl_hl = request.POST.get('timeline_highlight_word', '').strip()







                tl_hd = request.POST.get('timeline_title', '').strip()







                if tl_clean and tl_hl and tl_hl.lower() in tl_clean.lower():







                    import re







                    j_set.timeline_title = re.sub(re.escape(tl_hl), f"<span>{tl_hl}</span>", tl_clean, count=1, flags=re.IGNORECASE)







                    j_set.timeline_highlight = tl_hl







                elif tl_clean:







                    j_set.timeline_title = tl_clean







                    j_set.timeline_highlight = tl_hl







                elif tl_hd:







                    j_set.timeline_title = tl_hd







                j_set.timeline_subtitle = request.POST.get('timeline_subtitle', j_set.timeline_subtitle).strip()















                # Section 4: Our Milestones







                j_set.milestones_tag = request.POST.get('milestones_tag', j_set.milestones_tag).strip()







                ms_clean = request.POST.get('milestones_clean_title', '').strip()







                ms_hl = request.POST.get('milestones_highlight_word', '').strip()







                ms_hd = request.POST.get('milestones_title', '').strip()







                if ms_clean and ms_hl and ms_hl.lower() in ms_clean.lower():







                    import re







                    j_set.milestones_title = re.sub(re.escape(ms_hl), f"<span>{ms_hl}</span>", ms_clean, count=1, flags=re.IGNORECASE)







                    j_set.milestones_highlight = ms_hl







                elif ms_clean:







                    j_set.milestones_title = ms_clean







                    j_set.milestones_highlight = ms_hl







                elif ms_hd:







                    j_set.milestones_title = ms_hd







                j_set.milestones_subtitle = request.POST.get('milestones_subtitle', j_set.milestones_subtitle).strip()















                # Section 5: Our Impact







                j_set.impact_tag = request.POST.get('impact_tag', j_set.impact_tag).strip()







                imp_clean = request.POST.get('impact_clean_title', '').strip()







                imp_hl = request.POST.get('impact_highlight_word', '').strip()







                imp_hd = request.POST.get('impact_title', '').strip()







                if imp_clean and imp_hl and imp_hl.lower() in imp_clean.lower():







                    import re







                    j_set.impact_title = re.sub(re.escape(imp_hl), f"<span>{imp_hl}</span>", imp_clean, count=1, flags=re.IGNORECASE)







                    j_set.impact_highlight = imp_hl







                elif imp_clean:







                    j_set.impact_title = imp_clean







                    j_set.impact_highlight = imp_hl







                elif imp_hd:







                    j_set.impact_title = imp_hd







                j_set.impact_description = request.POST.get('impact_description', j_set.impact_description).strip()















                if request.POST.get('remove_impact_image') == '1':







                    j_set.impact_image = None







                elif 'impact_image' in request.FILES:







                    validate_image_upload(request.FILES['impact_image'], "Impact Section Image")







                    j_set.impact_image = request.FILES['impact_image']















                # Section 6: By The Numbers







                j_set.numbers_tag = request.POST.get('numbers_tag', j_set.numbers_tag).strip()







                num_clean = request.POST.get('numbers_clean_title', '').strip()







                num_hl = request.POST.get('numbers_highlight_word', '').strip()







                num_hd = request.POST.get('numbers_title', '').strip()







                if num_clean and num_hl and num_hl.lower() in num_clean.lower():







                    import re







                    j_set.numbers_title = re.sub(re.escape(num_hl), f"<span>{num_hl}</span>", num_clean, count=1, flags=re.IGNORECASE)







                    j_set.numbers_highlight = num_hl







                elif num_clean:







                    j_set.numbers_title = num_clean







                    j_set.numbers_highlight = num_hl







                elif num_hd:







                    j_set.numbers_title = num_hd







                j_set.numbers_subtitle = request.POST.get('numbers_subtitle', j_set.numbers_subtitle).strip()















                # Section 7: Looking Ahead







                j_set.ahead_tag = request.POST.get('ahead_tag', j_set.ahead_tag).strip()







                ah_clean = request.POST.get('ahead_clean_title', '').strip()







                ah_hl = request.POST.get('ahead_highlight_word', '').strip()







                ah_hd = request.POST.get('ahead_title', '').strip()







                if ah_clean and ah_hl and ah_hl.lower() in ah_clean.lower():







                    import re







                    j_set.ahead_title = re.sub(re.escape(ah_hl), f"<span>{ah_hl}</span>", ah_clean, count=1, flags=re.IGNORECASE)







                    j_set.ahead_highlight = ah_hl







                elif ah_clean:







                    j_set.ahead_title = ah_clean







                    j_set.ahead_highlight = ah_hl







                elif ah_hd:







                    j_set.ahead_title = ah_hd







                j_set.ahead_description = request.POST.get('ahead_description', j_set.ahead_description).strip()















                j_set.cta_btn1_text = request.POST.get('cta_btn1_text', j_set.cta_btn1_text).strip()







                raw_cta1_url = request.POST.get('cta_btn1_url', '').strip()







                if raw_cta1_url:







                    validate_safe_url(raw_cta1_url, "CTA Primary Button URL")







                j_set.cta_btn1_url = raw_cta1_url















                j_set.cta_btn2_text = request.POST.get('cta_btn2_text', j_set.cta_btn2_text).strip()







                raw_cta2_url = request.POST.get('cta_btn2_url', '').strip()







                if raw_cta2_url:







                    validate_safe_url(raw_cta2_url, "CTA Secondary Button URL")







                j_set.cta_btn2_url = raw_cta2_url















                # SEO & Meta







                j_set.meta_title = request.POST.get('meta_title', j_set.meta_title).strip()







                j_set.meta_description = request.POST.get('meta_description', j_set.meta_description).strip()















                if request.POST.get('remove_og_image') == '1':







                    j_set.og_image = None







                elif 'og_image' in request.FILES:







                    validate_image_upload(request.FILES['og_image'], "OG Social Image")







                    j_set.og_image = request.FILES['og_image']















                j_set.save()















                # Repeaters:







                # 1. JourneyStoryParagraph







                paragraphs_raw = request.POST.get('journey_paragraphs_json')







                if paragraphs_raw:







                    try:







                        p_data = json.loads(paragraphs_raw)







                        seen_p_ids = []







                        saved_texts = []







                        for idx, item in enumerate(p_data, 1):







                            item_id = item.get('id')







                            p_obj = JourneyStoryParagraph.objects.filter(id=item_id).first() if item_id else JourneyStoryParagraph()







                            txt = str(item.get('paragraph_text') or item.get('text') or '').strip()







                            if not txt:







                                continue







                            p_obj.text = txt







                            p_obj.order = int(item.get('order', idx))







                            p_obj.is_visible = bool(item.get('is_visible', True))







                            if 'is_highlight' in item:







                                p_obj.is_highlight = bool(item.get('is_highlight'))







                            p_obj.save()







                            seen_p_ids.append(p_obj.id)







                            saved_texts.append(txt)







                        JourneyStoryParagraph.objects.exclude(id__in=seen_p_ids).delete()







                        # Sync fallback story_p1..p3 from visible paragraphs only







                        visible_texts = [







                            str(item.get('paragraph_text') or item.get('text') or '').strip()







                            for item in p_data







                            if bool(item.get('is_visible', True)) and str(item.get('paragraph_text') or item.get('text') or '').strip()







                        ]







                        j_set.story_p1 = visible_texts[0] if len(visible_texts) > 0 else ''







                        j_set.story_p2 = visible_texts[1] if len(visible_texts) > 1 else ''







                        j_set.story_p3 = visible_texts[2] if len(visible_texts) > 2 else ''







                        j_set.save()







                    except (json.JSONDecodeError, ValueError, Exception):







                        pass















                # 2. JourneyStoryCard







                story_cards_raw = request.POST.get('journey_story_cards_json')







                if story_cards_raw:







                    try:







                        sc_data = json.loads(story_cards_raw)







                        seen_sc_ids = []







                        for idx, item in enumerate(sc_data, 1):







                            item_id = item.get('id')







                            sc_obj = JourneyStoryCard.objects.filter(id=item_id).first() if item_id else JourneyStoryCard()







                            title_val = str(item.get('title') or '').strip()







                            if not title_val:







                                continue







                            sc_obj.title = title_val







                            sc_obj.description = str(item.get('description') or '').strip()







                            sc_obj.icon = str(item.get('icon') or item.get('icon_class') or 'fa-solid fa-shield-halved').strip()







                            col = str(item.get('color') or 'blue').strip().lower()







                            sc_obj.color = 'red' if 'red' in col else 'blue'







                            sc_obj.order = int(item.get('order', idx))







                            sc_obj.is_visible = bool(item.get('is_visible', True))







                            sc_obj.save()







                            seen_sc_ids.append(sc_obj.id)







                        JourneyStoryCard.objects.exclude(id__in=seen_sc_ids).delete()







                    except (json.JSONDecodeError, ValueError, Exception):







                        pass















                # 3. Growth Timeline (JourneyMilestone)







                ms_raw = request.POST.get('milestones_json') or request.POST.get('journey_timeline_json')







                if ms_raw:







                    try:







                        ms_data = json.loads(ms_raw)







                        seen_ids = []







                        for idx, item in enumerate(ms_data, 1):







                            item_id = item.get('id')







                            m_obj = JourneyMilestone.objects.filter(id=item_id).first() if item_id else JourneyMilestone()







                            m_title = (item.get('title') or '').strip()







                            if not m_title:







                                continue







                            m_obj.year = (item.get('year') or '2022').strip()







                            m_obj.title = m_title







                            m_obj.description = (item.get('description') or '').strip()







                            m_obj.badge_label = (item.get('badge_label') or '').strip()







                            m_obj.icon_class = (item.get('icon_class') or 'fa-solid fa-flag').strip()







                            m_obj.order = int(item.get('order', idx))







                            m_obj.is_visible = bool(item.get('is_visible', True))







                            m_obj.save()







                            seen_ids.append(m_obj.id)







                        JourneyMilestone.objects.exclude(id__in=seen_ids).delete()







                    except (json.JSONDecodeError, ValueError, Exception):







                        pass















                # 4. JourneyMilestoneCard (Milestone Grid Cards)







                mc_raw = request.POST.get('journey_milestone_cards_json')







                if mc_raw:







                    try:







                        mc_data = json.loads(mc_raw)







                        seen_mc_ids = []







                        for idx, item in enumerate(mc_data, 1):







                            item_id = item.get('id')







                            mc_obj = JourneyMilestoneCard.objects.filter(id=item_id).first() if item_id else JourneyMilestoneCard()







                            title_val = str(item.get('title') or '').strip()







                            if not title_val:







                                continue







                            mc_obj.year = str(item.get('year') or '2022').strip()







                            mc_obj.title = title_val







                            mc_obj.description = str(item.get('description') or '').strip()







                            mc_obj.icon_class = str(item.get('icon_class') or 'fa-solid fa-trophy').strip()







                            mc_obj.order = int(item.get('order', idx))







                            mc_obj.is_visible = bool(item.get('is_visible', True))







                            mc_obj.save()







                            seen_mc_ids.append(mc_obj.id)







                        JourneyMilestoneCard.objects.exclude(id__in=seen_mc_ids).delete()







                    except (json.JSONDecodeError, ValueError, Exception):







                        pass















                # 5. JourneyImpactItem







                imp_raw = request.POST.get('journey_impact_items_json')







                if imp_raw:







                    try:







                        imp_data = json.loads(imp_raw)







                        seen_imp_ids = []







                        for idx, item in enumerate(imp_data, 1):







                            item_id = item.get('id')







                            it_obj = JourneyImpactItem.objects.filter(id=item_id).first() if item_id else JourneyImpactItem()







                            t_val = str(item.get('title') or '').strip()







                            if not t_val:







                                continue







                            it_obj.title = t_val







                            it_obj.description = str(item.get('description') or '').strip()







                            it_obj.icon = str(item.get('icon') or item.get('icon_class') or 'fa-solid fa-check').strip()







                            it_obj.order = int(item.get('order', idx))







                            it_obj.is_visible = bool(item.get('is_visible', True))







                            it_obj.save()







                            seen_imp_ids.append(it_obj.id)







                        JourneyImpactItem.objects.exclude(id__in=seen_imp_ids).delete()







                    except (json.JSONDecodeError, ValueError, Exception):







                        pass















                # 6. JourneyStat







                stats_raw = request.POST.get('journey_stats_json')







                if stats_raw:







                    try:







                        stats_data = json.loads(stats_raw)







                        seen_st_ids = []







                        for idx, item in enumerate(stats_data, 1):







                            item_id = item.get('id')







                            st_obj = JourneyStat.objects.filter(id=item_id).first() if item_id else JourneyStat()







                            lbl = str(item.get('label') or '').strip()







                            cnt = str(item.get('count') or '').strip()







                            if not lbl and not cnt:







                                continue







                            st_obj.count = cnt







                            st_obj.suffix = str(item.get('suffix') or '').strip()







                            st_obj.label = lbl







                            st_obj.icon = str(item.get('icon') or item.get('icon_class') or 'fa-solid fa-calendar-check').strip()







                            st_obj.order = int(item.get('order', idx))







                            st_obj.is_visible = bool(item.get('is_visible', True))







                            st_obj.save()







                            seen_st_ids.append(st_obj.id)







                        JourneyStat.objects.exclude(id__in=seen_st_ids).delete()







                    except (json.JSONDecodeError, ValueError, Exception):







                        pass















                # 7. JourneyFutureGoal







                goals_raw = request.POST.get('journey_future_goals_json')







                if goals_raw:







                    try:







                        g_data = json.loads(goals_raw)







                        seen_g_ids = []







                        for idx, item in enumerate(g_data, 1):







                            item_id = item.get('id')







                            g_obj = JourneyFutureGoal.objects.filter(id=item_id).first() if item_id else JourneyFutureGoal()







                            txt = str(item.get('text') or '').strip()







                            if not txt:







                                continue







                            g_obj.text = txt







                            g_obj.icon = str(item.get('icon') or item.get('icon_class') or 'fa-solid fa-circle-check').strip()







                            g_obj.order = int(item.get('order', idx))







                            g_obj.is_visible = bool(item.get('is_visible', True))







                            g_obj.save()







                            seen_g_ids.append(g_obj.id)







                        JourneyFutureGoal.objects.exclude(id__in=seen_g_ids).delete()







                    except (json.JSONDecodeError, ValueError, Exception):







                        pass















            cache.delete('about_pages_context')







            cache.delete('public_site_context')















            page_names = {







                'company': 'About Company',







                'ceo': 'CEO & Founder',







                'team': 'Our Team',







                'journey': 'Our Journey',







            }







            p_display = page_names.get(about_subpage, 'About Us')







            try:







                log_activity(







                    admin_user,







                    "Website Content Updated",







                    f"Updated {p_display} page dynamic content successfully."







                )







            except Exception:







                pass







            messages.success(request, f"{p_display} content updated and published live successfully!")







            return True















    except Exception as e:







        messages.error(request, f"Error updating content: {str(e)}")







        return False























def handle_manpower_supply_save(request, admin_user):







    from django.db import transaction







    from django.core.cache import cache







    from django.contrib import messages







    from apps.core.models import (







        MANPOWER_SUPPLY_CACHE_KEY,







        ManpowerSupplySettings,







        ManpowerChecklistItem,







        ManpowerServiceCard,







        ManpowerIndustryItem,







        ManpowerWhyChooseItem,







        ManpowerProcessStep,







        ManpowerStatItem,







        ManpowerFaqItem,







        ManpowerTrustItem,







    )







    from apps.enquiries.models import log_activity















    try:







        with transaction.atomic():







            ms = ManpowerSupplySettings.get_settings()















            # Section Visibility Switches







            ms.hero_visible = ('hero_visible' in request.POST)







            ms.about_visible = ('about_visible' in request.POST)







            ms.services_visible = ('services_visible' in request.POST)







            ms.industries_why_visible = ('industries_why_visible' in request.POST)







            ms.process_visible = ('process_visible' in request.POST)







            ms.stats_visible = ('stats_visible' in request.POST)







            ms.faq_cta_visible = ('faq_cta_visible' in request.POST)







            ms.trust_visible = ('trust_visible' in request.POST)















            # 1. Hero Section Fields







            ms.hero_eyebrow = request.POST.get('hero_eyebrow', ms.hero_eyebrow).strip()







            ms.hero_title = request.POST.get('hero_title', ms.hero_title).strip()







            ms.hero_subtitle = request.POST.get('hero_subtitle', ms.hero_subtitle).strip()







            ms.hero_badge_text = request.POST.get('hero_badge_text', ms.hero_badge_text).strip()







            ms.hero_enquire_btn_text = request.POST.get('hero_enquire_btn_text', ms.hero_enquire_btn_text).strip()







            raw_h_enq_url = request.POST.get('hero_enquire_btn_url', '').strip()







            if raw_h_enq_url:







                validate_safe_url(raw_h_enq_url, "Hero Enquire URL")







            ms.hero_enquire_btn_url = raw_h_enq_url or '/contact/'







            ms.hero_call_btn_text = request.POST.get('hero_call_btn_text', ms.hero_call_btn_text).strip()







            raw_h_phone = request.POST.get('hero_call_phone', '').strip()







            if raw_h_phone:







                validate_safe_phone(raw_h_phone, "Hero Call Phone")







            ms.hero_call_phone = raw_h_phone or '+91 88531 11111'















            ms.hero_feat1_icon = request.POST.get('hero_feat1_icon', ms.hero_feat1_icon).strip()







            ms.hero_feat1_text = request.POST.get('hero_feat1_text', ms.hero_feat1_text).strip()







            ms.hero_feat2_icon = request.POST.get('hero_feat2_icon', ms.hero_feat2_icon).strip()







            ms.hero_feat2_text = request.POST.get('hero_feat2_text', ms.hero_feat2_text).strip()







            ms.hero_feat3_icon = request.POST.get('hero_feat3_icon', ms.hero_feat3_icon).strip()







            ms.hero_feat3_text = request.POST.get('hero_feat3_text', ms.hero_feat3_text).strip()















            if request.POST.get('remove_hero_image') == '1':







                ms.hero_image = None







            elif 'hero_image' in request.FILES:







                validate_image_upload(request.FILES['hero_image'], "Hero Banner Image")







                ms.hero_image = request.FILES['hero_image']















            # 2. About Section Fields







            ms.about_tag = request.POST.get('about_tag', ms.about_tag).strip()







            ms.about_title = request.POST.get('about_title', ms.about_title).strip()







            ms.about_description = request.POST.get('about_description', ms.about_description).strip()















            if request.POST.get('remove_about_image') == '1':







                ms.about_image = None







            elif 'about_image' in request.FILES:







                validate_image_upload(request.FILES['about_image'], "About Section Photo")







                ms.about_image = request.FILES['about_image']















            # 3. Services Grid Section Header







            ms.services_tag = request.POST.get('services_tag', ms.services_tag).strip()







            ms.services_title = request.POST.get('services_title', ms.services_title).strip()















            # 4. Industries & Why Choose Header Fields







            ms.industries_tag = request.POST.get('industries_tag', ms.industries_tag).strip()







            ms.industries_title = request.POST.get('industries_title', ms.industries_title).strip()







            ms.why_choose_tag = request.POST.get('why_choose_tag', ms.why_choose_tag).strip()







            ms.why_choose_title = request.POST.get('why_choose_title', ms.why_choose_title).strip()















            # 5. Process Section Fields







            ms.process_tag = request.POST.get('process_tag', ms.process_tag).strip()







            ms.process_title = request.POST.get('process_title', ms.process_title).strip()







            ms.process_subtitle = request.POST.get('process_subtitle', ms.process_subtitle).strip()















            # 6. FAQ & CTA Card Section Fields







            ms.faq_tag = request.POST.get('faq_tag', ms.faq_tag).strip()







            ms.cta_tag = request.POST.get('cta_tag', ms.cta_tag).strip()







            ms.cta_title = request.POST.get('cta_title', ms.cta_title).strip()







            ms.cta_subtitle = request.POST.get('cta_subtitle', ms.cta_subtitle).strip()







            ms.cta_call_btn_text = request.POST.get('cta_call_btn_text', ms.cta_call_btn_text).strip()







            raw_cta_phone = request.POST.get('cta_call_phone', '').strip()







            if raw_cta_phone:







                validate_safe_phone(raw_cta_phone, "CTA Call Phone")







            ms.cta_call_phone = raw_cta_phone or '+91 88531 11111'







            ms.cta_enquire_btn_text = request.POST.get('cta_enquire_btn_text', ms.cta_enquire_btn_text).strip()







            raw_cta_url = request.POST.get('cta_enquire_url', '').strip()







            if raw_cta_url:







                validate_safe_url(raw_cta_url, "CTA Enquire URL")







            ms.cta_enquire_url = raw_cta_url or '/contact/'















            if request.POST.get('remove_cta_image') == '1':







                ms.cta_image = None







            elif 'cta_image' in request.FILES:







                validate_image_upload(request.FILES['cta_image'], "CTA Card Image")







                ms.cta_image = request.FILES['cta_image']















            # SEO & Meta







            ms.meta_title = request.POST.get('meta_title', ms.meta_title).strip()







            ms.meta_description = request.POST.get('meta_description', ms.meta_description).strip()















            ms.save()















            # --- Process JSON Repeaters ---







            # 1. ManpowerChecklistItem







            chk_raw = request.POST.get('manpower_checklist_json')







            if chk_raw:







                try:







                    chk_data = json.loads(chk_raw)







                    seen_chk_ids = []







                    for idx, item in enumerate(chk_data, 1):







                        item_id = item.get('id')







                        chk_obj = ManpowerChecklistItem.objects.filter(id=item_id).first() if item_id else ManpowerChecklistItem()







                        txt = str(item.get('text') or '').strip()







                        if not txt:







                            continue







                        chk_obj.text = txt







                        chk_obj.icon_class = str(item.get('icon_class') or 'fa-solid fa-circle-check').strip()







                        chk_obj.order = int(item.get('order', idx))







                        chk_obj.is_visible = bool(item.get('is_visible', True))







                        chk_obj.save()







                        seen_chk_ids.append(chk_obj.id)







                    ManpowerChecklistItem.objects.exclude(id__in=seen_chk_ids).delete()







                except Exception:







                    pass















            # 2. ManpowerServiceCard







            srv_raw = request.POST.get('manpower_services_json')







            if srv_raw:







                try:







                    srv_data = json.loads(srv_raw)







                    seen_srv_ids = []







                    for idx, item in enumerate(srv_data, 1):







                        item_id = item.get('id')







                        srv_obj = ManpowerServiceCard.objects.filter(id=item_id).first() if item_id else ManpowerServiceCard()







                        t_val = str(item.get('title') or '').strip()







                        if not t_val:







                            continue







                        srv_obj.title = t_val







                        srv_obj.description = str(item.get('description') or '').strip()







                        srv_obj.icon_class = str(item.get('icon_class') or 'fa-solid fa-people-group').strip()







                        srv_obj.color_class = str(item.get('color_class') or 'i-blue').strip()







                        srv_obj.order = int(item.get('order', idx))







                        srv_obj.is_visible = parse_bool_val(item.get('is_visible'), True)







                        srv_obj.save()







                        seen_srv_ids.append(srv_obj.id)







                    ManpowerServiceCard.objects.exclude(id__in=seen_srv_ids).delete()







                except Exception:







                    pass















            # 3. ManpowerIndustryItem







            ind_raw = request.POST.get('manpower_industries_json')







            if ind_raw:







                try:







                    ind_data = json.loads(ind_raw)







                    seen_ind_ids = []







                    for idx, item in enumerate(ind_data, 1):







                        item_id = item.get('id')







                        ind_obj = ManpowerIndustryItem.objects.filter(id=item_id).first() if item_id else ManpowerIndustryItem()







                        n_val = str(item.get('name') or '').strip()







                        if not n_val:







                            continue







                        ind_obj.name = n_val







                        ind_obj.icon_class = str(item.get('icon_class') or 'fa-solid fa-industry').strip()







                        ind_obj.order = int(item.get('order', idx))







                        ind_obj.is_visible = bool(item.get('is_visible', True))







                        ind_obj.save()







                        seen_ind_ids.append(ind_obj.id)







                    ManpowerIndustryItem.objects.exclude(id__in=seen_ind_ids).delete()







                except Exception:







                    pass















            # 4. ManpowerWhyChooseItem







            why_raw = request.POST.get('manpower_why_choose_json')







            if why_raw:







                try:







                    why_data = json.loads(why_raw)







                    seen_why_ids = []







                    for idx, item in enumerate(why_data, 1):







                        item_id = item.get('id')







                        why_obj = ManpowerWhyChooseItem.objects.filter(id=item_id).first() if item_id else ManpowerWhyChooseItem()







                        t_val = str(item.get('title') or '').strip()







                        if not t_val:







                            continue







                        why_obj.title = t_val







                        why_obj.icon_class = str(item.get('icon_class') or 'fa-solid fa-user-group').strip()







                        why_obj.order = int(item.get('order', idx))







                        why_obj.is_visible = parse_bool_val(item.get('is_visible'), True)







                        why_obj.save()







                        seen_why_ids.append(why_obj.id)







                    ManpowerWhyChooseItem.objects.exclude(id__in=seen_why_ids).delete()







                except Exception:







                    pass















            # 5. ManpowerProcessStep







            proc_raw = request.POST.get('manpower_process_json')







            if proc_raw:







                try:







                    proc_data = json.loads(proc_raw)







                    seen_proc_ids = []







                    for idx, item in enumerate(proc_data, 1):







                        item_id = item.get('id')







                        proc_obj = ManpowerProcessStep.objects.filter(id=item_id).first() if item_id else ManpowerProcessStep()







                        t_val = str(item.get('title') or '').strip()







                        if not t_val:







                            continue







                        proc_obj.step_number = str(item.get('step_number') or f"0{idx}").strip()







                        proc_obj.title = t_val







                        proc_obj.icon_class = str(item.get('icon_class') or 'fa-solid fa-clipboard-list').strip()







                        proc_obj.order = int(item.get('order', idx))







                        proc_obj.is_visible = parse_bool_val(item.get('is_visible'), True)







                        proc_obj.save()







                        seen_proc_ids.append(proc_obj.id)







                    ManpowerProcessStep.objects.exclude(id__in=seen_proc_ids).delete()







                except Exception:







                    pass















            # 6. ManpowerStatItem







            stat_raw = request.POST.get('manpower_stats_json')







            if stat_raw:







                try:







                    stat_data = json.loads(stat_raw)







                    seen_st_ids = []







                    for idx, item in enumerate(stat_data, 1):







                        item_id = item.get('id')







                        st_obj = ManpowerStatItem.objects.filter(id=item_id).first() if item_id else ManpowerStatItem()







                        v_val = str(item.get('value') or '').strip()







                        l_val = str(item.get('label') or '').strip()







                        if not v_val and not l_val:







                            continue







                        st_obj.value = v_val







                        st_obj.label = l_val







                        st_obj.icon_class = str(item.get('icon_class') or 'fa-solid fa-user-group').strip()







                        st_obj.order = int(item.get('order', idx))







                        st_obj.is_visible = bool(item.get('is_visible', True))







                        st_obj.save()







                        seen_st_ids.append(st_obj.id)







                    ManpowerStatItem.objects.exclude(id__in=seen_st_ids).delete()







                except Exception:







                    pass















            # 7. ManpowerFaqItem







            faq_raw = request.POST.get('manpower_faqs_json')







            if faq_raw:







                try:







                    faq_data = json.loads(faq_raw)







                    seen_f_ids = []







                    for idx, item in enumerate(faq_data, 1):







                        item_id = item.get('id')







                        f_obj = ManpowerFaqItem.objects.filter(id=item_id).first() if item_id else ManpowerFaqItem()







                        q_val = str(item.get('question') or '').strip()







                        a_val = str(item.get('answer') or '').strip()







                        if not q_val:







                            continue







                        f_obj.question = q_val







                        f_obj.answer = a_val







                        f_obj.order = int(item.get('order', idx))







                        f_obj.is_visible = bool(item.get('is_visible', True))







                        f_obj.save()







                        seen_f_ids.append(f_obj.id)







                    ManpowerFaqItem.objects.exclude(id__in=seen_f_ids).delete()







                except Exception:







                    pass















            # 8. ManpowerTrustItem







            tr_raw = request.POST.get('manpower_trust_json')







            if tr_raw:







                try:







                    tr_data = json.loads(tr_raw)







                    seen_tr_ids = []







                    for idx, item in enumerate(tr_data, 1):







                        item_id = item.get('id')







                        tr_obj = ManpowerTrustItem.objects.filter(id=item_id).first() if item_id else ManpowerTrustItem()







                        l1 = str(item.get('line1') or '').strip()







                        l2 = str(item.get('line2') or '').strip()







                        if not l1 and not l2:







                            continue







                        tr_obj.line1 = l1







                        tr_obj.line2 = l2







                        tr_obj.icon_class = str(item.get('icon_class') or 'fa-solid fa-award').strip()







                        tr_obj.order = int(item.get('order', idx))







                        tr_obj.is_visible = bool(item.get('is_visible', True))







                        tr_obj.save()







                        seen_tr_ids.append(tr_obj.id)







                    ManpowerTrustItem.objects.exclude(id__in=seen_tr_ids).delete()







                except Exception:







                    pass















            cache.delete(MANPOWER_SUPPLY_CACHE_KEY)







            cache.delete('public_site_context')















            try:







                log_activity(







                    admin_user,







                    "Website Content Updated",







                    "Updated Manpower Supply service page dynamic sections and published live."







                )







            except Exception:







                pass















            messages.success(request, "Manpower Supply page content updated and published live successfully!")







            return True















    except Exception as e:







        messages.error(request, f"Error updating Manpower Supply content: {str(e)}")







        return False















































































































def handle_recruitment_placement_save(request, admin_user):







    from django.db import transaction







    from django.core.cache import cache







    from django.contrib import messages







    from apps.core.models import (







        RECRUITMENT_PLACEMENT_CACHE_KEY,







        RecruitmentPlacementSettings,







        RpWhyPartnerItem,







        RpServiceCard,







        RpProcessStep,







        RpWhyChooseItem,







        RpIndustryItem,







        RpPartnerItem,







        RpFaqItem,







    )







    from apps.enquiries.models import log_activity















    try:







        with transaction.atomic():







            rp = RecruitmentPlacementSettings.get_settings()















            # Master Section Visibility Switches







            rp.hero_visible = ('hero_visible' in request.POST)







            rp.about_visible = ('about_visible' in request.POST)







            rp.why_partner_visible = ('why_partner_visible' in request.POST)







            rp.services_visible = ('services_visible' in request.POST)







            rp.process_visible = ('process_visible' in request.POST)







            rp.insights_visible = ('insights_visible' in request.POST)







            rp.partners_visible = ('partners_visible' in request.POST)







            rp.faq_visible = ('faq_visible' in request.POST)







            rp.cta_visible = ('cta_visible' in request.POST)















            # 1. Hero Section







            rp.hero_eyebrow = request.POST.get('hero_eyebrow', rp.hero_eyebrow).strip()







            import re







            raw_rp_title = request.POST.get('hero_title', rp.hero_title)







            rp.hero_title = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', str(raw_rp_title)).replace('&amp;', '&')).strip()







            rp.hero_subtitle = request.POST.get('hero_subtitle', rp.hero_subtitle).strip()







            rp.hero_hire_btn_text = request.POST.get('hero_hire_btn_text', rp.hero_hire_btn_text).strip()







            raw_h_hire_url = request.POST.get('hero_hire_btn_url', '').strip()







            if raw_h_hire_url:







                validate_safe_url(raw_h_hire_url, "Hero Hire URL")







            rp.hero_hire_btn_url = raw_h_hire_url or '/employer/hire-talent/'







            rp.hero_jobs_btn_text = request.POST.get('hero_jobs_btn_text', rp.hero_jobs_btn_text).strip()







            raw_h_jobs_url = request.POST.get('hero_jobs_btn_url', '').strip()







            if raw_h_jobs_url:







                validate_safe_url(raw_h_jobs_url, "Hero Jobs URL")







            rp.hero_jobs_btn_url = raw_h_jobs_url or '/jobs/'















            rp.hero_stat1_value = request.POST.get('hero_stat1_value', rp.hero_stat1_value).strip()







            rp.hero_stat1_label = request.POST.get('hero_stat1_label', rp.hero_stat1_label).strip()







            rp.hero_stat2_value = request.POST.get('hero_stat2_value', rp.hero_stat2_value).strip()







            rp.hero_stat2_label = request.POST.get('hero_stat2_label', rp.hero_stat2_label).strip()







            rp.hero_stat3_value = request.POST.get('hero_stat3_value', rp.hero_stat3_value).strip()







            rp.hero_stat3_label = request.POST.get('hero_stat3_label', rp.hero_stat3_label).strip()







            rp.hero_stat4_value = request.POST.get('hero_stat4_value', rp.hero_stat4_value).strip()







            rp.hero_stat4_label = request.POST.get('hero_stat4_label', rp.hero_stat4_label).strip()















            # 2. About Section







            rp.about_tag = request.POST.get('about_tag', rp.about_tag).strip()







            rp.about_title = request.POST.get('about_title', rp.about_title).strip()







            rp.about_desc1 = request.POST.get('about_desc1', rp.about_desc1).strip()







            rp.about_desc2 = request.POST.get('about_desc2', rp.about_desc2).strip()







            rp.about_exp_years = request.POST.get('about_exp_years', rp.about_exp_years).strip()







            raw_rp_exp = request.POST.get('about_exp_label', rp.about_exp_label)







            rp.about_exp_label = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', str(raw_rp_exp)).replace('&amp;', '&')).strip()







            rp.about_feat1_text = request.POST.get('about_feat1_text', rp.about_feat1_text).strip()







            rp.about_feat1_icon = request.POST.get('about_feat1_icon', rp.about_feat1_icon).strip()







            rp.about_feat2_text = request.POST.get('about_feat2_text', rp.about_feat2_text).strip()







            rp.about_feat2_icon = request.POST.get('about_feat2_icon', rp.about_feat2_icon).strip()







            rp.about_feat3_text = request.POST.get('about_feat3_text', rp.about_feat3_text).strip()







            rp.about_feat3_icon = request.POST.get('about_feat3_icon', rp.about_feat3_icon).strip()







            rp.about_feat4_text = request.POST.get('about_feat4_text', rp.about_feat4_text).strip()







            rp.about_feat4_icon = request.POST.get('about_feat4_icon', rp.about_feat4_icon).strip()















            # 3. Why Partner Card







            rp.why_partner_title = request.POST.get('why_partner_title', rp.why_partner_title).strip()







            rp.why_partner_learn_btn_text = request.POST.get('why_partner_learn_btn_text', rp.why_partner_learn_btn_text).strip()







            raw_wp_url = request.POST.get('why_partner_learn_btn_url', '').strip()







            if raw_wp_url:







                validate_safe_url(raw_wp_url, "Why Partner Learn URL")







            rp.why_partner_learn_btn_url = raw_wp_url or '/about/journey/'















            # 4. Services Grid Section Header







            rp.services_tag = request.POST.get('services_tag', rp.services_tag).strip()







            rp.services_title = request.POST.get('services_title', rp.services_title).strip()







            rp.services_subtitle = request.POST.get('services_subtitle', rp.services_subtitle).strip()















            # 5. Process Section







            rp.process_tag = request.POST.get('process_tag', rp.process_tag).strip()







            rp.process_title = request.POST.get('process_title', rp.process_title).strip()







            rp.process_subtitle = request.POST.get('process_subtitle', rp.process_subtitle).strip()















            # 6. Insights Grid - Card Titles & Achievements & Testimonial







            rp.why_choose_title = request.POST.get('why_choose_title', rp.why_choose_title).strip()







            rp.achievements_title = request.POST.get('achievements_title', rp.achievements_title).strip()







            rp.achieve1_value = request.POST.get('achieve1_value', rp.achieve1_value).strip()







            rp.achieve1_label = request.POST.get('achieve1_label', rp.achieve1_label).strip()







            rp.achieve1_icon = request.POST.get('achieve1_icon', rp.achieve1_icon).strip()







            rp.achieve1_color = request.POST.get('achieve1_color', rp.achieve1_color).strip()







            rp.achieve2_value = request.POST.get('achieve2_value', rp.achieve2_value).strip()







            rp.achieve2_label = request.POST.get('achieve2_label', rp.achieve2_label).strip()







            rp.achieve2_icon = request.POST.get('achieve2_icon', rp.achieve2_icon).strip()







            rp.achieve2_color = request.POST.get('achieve2_color', rp.achieve2_color).strip()







            rp.achieve3_value = request.POST.get('achieve3_value', rp.achieve3_value).strip()







            rp.achieve3_label = request.POST.get('achieve3_label', rp.achieve3_label).strip()







            rp.achieve3_icon = request.POST.get('achieve3_icon', rp.achieve3_icon).strip()







            rp.achieve3_color = request.POST.get('achieve3_color', rp.achieve3_color).strip()







            rp.achieve4_value = request.POST.get('achieve4_value', rp.achieve4_value).strip()







            rp.achieve4_label = request.POST.get('achieve4_label', rp.achieve4_label).strip()







            rp.achieve4_icon = request.POST.get('achieve4_icon', rp.achieve4_icon).strip()







            rp.achieve4_color = request.POST.get('achieve4_color', rp.achieve4_color).strip()















            rp.industries_title = request.POST.get('industries_title', rp.industries_title).strip()















            rp.testimonial_title = request.POST.get('testimonial_title', rp.testimonial_title).strip()







            rp.testimonial_quote = request.POST.get('testimonial_quote', rp.testimonial_quote).strip()







            rp.testimonial_author = request.POST.get('testimonial_author', rp.testimonial_author).strip()







            rp.testimonial_role = request.POST.get('testimonial_role', rp.testimonial_role).strip()







            rp.testimonial_avatar = request.POST.get('testimonial_avatar', rp.testimonial_avatar).strip()















            # 7. Partners Section







            rp.partners_title = request.POST.get('partners_title', rp.partners_title).strip()















            # 8. FAQ Section







            rp.faq_tag = request.POST.get('faq_tag', rp.faq_tag).strip()







            rp.faq_title = request.POST.get('faq_title', rp.faq_title).strip()















            # 9. Bottom CTA Section







            rp.cta_title = request.POST.get('cta_title', rp.cta_title).strip()







            rp.cta_subtitle = request.POST.get('cta_subtitle', rp.cta_subtitle).strip()







            rp.cta_btn_text = request.POST.get('cta_btn_text', rp.cta_btn_text).strip()







            raw_cta_url = request.POST.get('cta_btn_url', '').strip()







            if raw_cta_url:







                validate_safe_url(raw_cta_url, "CTA Button URL")







            rp.cta_btn_url = raw_cta_url or '/contact/'















            # 10. SEO & Meta







            rp.meta_title = request.POST.get('meta_title', rp.meta_title).strip()







            rp.meta_description = request.POST.get('meta_description', rp.meta_description).strip()







            if 'og_image' in request.FILES:







                validate_image_upload(request.FILES['og_image'], "OG Image")







                rp.og_image = request.FILES['og_image']















            rp.save()















            # --- JSON Repeaters ---







            # 1. RpWhyPartnerItem







            wp_raw = request.POST.get('rp_why_partner_json')







            if wp_raw:







                try:







                    wp_data = json.loads(wp_raw)







                    seen_wp_ids = []







                    for idx, item in enumerate(wp_data, 1):







                        item_id = item.get('id')







                        wp_obj = RpWhyPartnerItem.objects.filter(id=item_id).first() if item_id else RpWhyPartnerItem()







                        txt = str(item.get('text') or '').strip()







                        if not txt:







                            continue







                        wp_obj.text = txt







                        wp_obj.icon_class = str(item.get('icon_class') or 'fa-solid fa-check').strip()







                        wp_obj.order = int(item.get('order', idx))







                        wp_obj.is_visible = bool(item.get('is_visible', True))







                        wp_obj.save()







                        seen_wp_ids.append(wp_obj.id)







                    RpWhyPartnerItem.objects.exclude(id__in=seen_wp_ids).delete()







                except Exception:







                    pass















            # 2. RpServiceCard







            srv_raw = request.POST.get('rp_services_json')







            if srv_raw:







                try:







                    srv_data = json.loads(srv_raw)







                    seen_srv_ids = []







                    for idx, item in enumerate(srv_data, 1):







                        item_id = item.get('id')







                        srv_obj = RpServiceCard.objects.filter(id=item_id).first() if item_id else RpServiceCard()







                        t_val = str(item.get('title') or '').strip()







                        if not t_val:







                            continue







                        srv_obj.title = t_val







                        srv_obj.description = str(item.get('description') or '').strip()







                        srv_obj.icon_class = str(item.get('icon_class') or 'fa-solid fa-user').strip()







                        srv_obj.color_class = str(item.get('color_class') or 'i-blue').strip()







                        srv_obj.order = int(item.get('order', idx))







                        srv_obj.is_visible = bool(item.get('is_visible', True))







                        srv_obj.save()







                        seen_srv_ids.append(srv_obj.id)







                    RpServiceCard.objects.exclude(id__in=seen_srv_ids).delete()







                except Exception:







                    pass















            # 3. RpProcessStep







            proc_raw = request.POST.get('rp_process_json')







            if proc_raw:







                try:







                    proc_data = json.loads(proc_raw)







                    seen_proc_ids = []







                    for idx, item in enumerate(proc_data, 1):







                        item_id = item.get('id')







                        proc_obj = RpProcessStep.objects.filter(id=item_id).first() if item_id else RpProcessStep()







                        t_val = str(item.get('title') or '').strip()







                        if not t_val:







                            continue







                        proc_obj.step_number = str(item.get('step_number') or f"0{idx}").strip()







                        proc_obj.title = t_val







                        proc_obj.icon_class = str(item.get('icon_class') or 'fa-solid fa-clipboard-list').strip()







                        proc_obj.order = int(item.get('order', idx))







                        proc_obj.is_visible = bool(item.get('is_visible', True))







                        proc_obj.save()







                        seen_proc_ids.append(proc_obj.id)







                    RpProcessStep.objects.exclude(id__in=seen_proc_ids).delete()







                except Exception:







                    pass















            # 4. RpWhyChooseItem







            wc_raw = request.POST.get('rp_why_choose_json')







            if wc_raw:







                try:







                    wc_data = json.loads(wc_raw)







                    seen_wc_ids = []







                    for idx, item in enumerate(wc_data, 1):







                        item_id = item.get('id')







                        wc_obj = RpWhyChooseItem.objects.filter(id=item_id).first() if item_id else RpWhyChooseItem()







                        t_val = str(item.get('text') or '').strip()







                        if not t_val:







                            continue







                        wc_obj.text = t_val







                        wc_obj.icon_class = str(item.get('icon_class') or 'fa-solid fa-circle-check').strip()







                        wc_obj.order = int(item.get('order', idx))







                        wc_obj.is_visible = bool(item.get('is_visible', True))







                        wc_obj.save()







                        seen_wc_ids.append(wc_obj.id)







                    RpWhyChooseItem.objects.exclude(id__in=seen_wc_ids).delete()







                except Exception:







                    pass















            # 5. RpIndustryItem







            ind_raw = request.POST.get('rp_industries_json')







            if ind_raw:







                try:







                    ind_data = json.loads(ind_raw)







                    seen_ind_ids = []







                    for idx, item in enumerate(ind_data, 1):







                        item_id = item.get('id')







                        ind_obj = RpIndustryItem.objects.filter(id=item_id).first() if item_id else RpIndustryItem()







                        n_val = str(item.get('name') or '').strip()







                        if not n_val:







                            continue







                        ind_obj.name = n_val







                        ind_obj.icon_class = str(item.get('icon_class') or 'fa-solid fa-desktop').strip()







                        ind_obj.order = int(item.get('order', idx))







                        ind_obj.is_visible = bool(item.get('is_visible', True))







                        ind_obj.save()







                        seen_ind_ids.append(ind_obj.id)







                    RpIndustryItem.objects.exclude(id__in=seen_ind_ids).delete()







                except Exception:







                    pass















            # 6. RpPartnerItem







            part_raw = request.POST.get('rp_partners_json')







            if part_raw:







                try:







                    part_data = json.loads(part_raw)







                    seen_part_ids = []







                    for idx, item in enumerate(part_data, 1):







                        item_id = item.get('id')







                        part_obj = RpPartnerItem.objects.filter(id=item_id).first() if item_id else RpPartnerItem()







                        n_val = str(item.get('name') or '').strip()







                        if not n_val:







                            continue







                        part_obj.name = n_val







                        part_obj.order = int(item.get('order', idx))







                        part_obj.is_visible = bool(item.get('is_visible', True))







                        part_obj.save()







                        seen_part_ids.append(part_obj.id)







                    RpPartnerItem.objects.exclude(id__in=seen_part_ids).delete()







                except Exception:







                    pass















            # 7. RpFaqItem







            faq_raw = request.POST.get('rp_faqs_json')







            if faq_raw:







                try:







                    faq_data = json.loads(faq_raw)







                    seen_f_ids = []







                    for idx, item in enumerate(faq_data, 1):







                        item_id = item.get('id')







                        f_obj = RpFaqItem.objects.filter(id=item_id).first() if item_id else RpFaqItem()







                        q_val = str(item.get('question') or '').strip()







                        a_val = str(item.get('answer') or '').strip()







                        if not q_val:







                            continue







                        f_obj.question = q_val







                        f_obj.answer = a_val







                        f_obj.order = int(item.get('order', idx))







                        f_obj.is_visible = bool(item.get('is_visible', True))







                        f_obj.save()







                        seen_f_ids.append(f_obj.id)







                    RpFaqItem.objects.exclude(id__in=seen_f_ids).delete()







                except Exception:







                    pass















            cache.delete(RECRUITMENT_PLACEMENT_CACHE_KEY)







            cache.delete('public_site_context')















            try:







                log_activity(







                    admin_user,







                    "Website Content Updated",







                    "Updated Recruitment & Placement service page dynamic sections and published live."







                )







            except Exception:







                pass















            messages.success(request, "Recruitment & Placement page content updated and published live successfully!")







            return True















    except Exception as e:







        messages.error(request, f"Error updating Recruitment & Placement content: {str(e)}")







        return False































def handle_contract_staffing_save(request, admin_user):







    from django.db import transaction







    from django.core.cache import cache







    from django.contrib import messages







    from apps.core.models import (







        CONTRACT_STAFFING_CACHE_KEY,







        ContractStaffingSettings,







        CsServiceCard,







        CsIndustryItem,







        CsWhyChooseItem,







        CsProcessStep,







        CsBenefitEmployerItem,







        CsBenefitCandidateItem,







        CsFaqItem,







    )







    from apps.enquiries.models import log_activity















    try:







        with transaction.atomic():







            cs = ContractStaffingSettings.get_settings()















            # Master Section Visibility Switches







            cs.hero_visible = ('hero_visible' in request.POST)







            cs.about_visible = ('about_visible' in request.POST)







            cs.services_visible = ('services_visible' in request.POST)







            cs.industries_why_visible = ('industries_why_visible' in request.POST)







            cs.process_visible = ('process_visible' in request.POST)







            cs.benefits_visible = ('benefits_visible' in request.POST)







            cs.faq_visible = ('faq_visible' in request.POST)







            cs.cta_visible = ('cta_visible' in request.POST)















            # 1. Hero Section







            cs.hero_eyebrow = request.POST.get('hero_eyebrow', cs.hero_eyebrow).strip()







            cs.hero_eyebrow_icon = request.POST.get('hero_eyebrow_icon', cs.hero_eyebrow_icon).strip()







            import re







            raw_cs_title = request.POST.get('hero_title', cs.hero_title)







            cs.hero_title = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', str(raw_cs_title)).replace('&amp;', '&')).strip()







            cs.hero_subtitle = request.POST.get('hero_subtitle', cs.hero_subtitle).strip()







            cs.hero_req_btn_text = request.POST.get('hero_req_btn_text', cs.hero_req_btn_text).strip()







            raw_h_req_url = request.POST.get('hero_req_btn_url', '').strip()







            if raw_h_req_url:







                validate_safe_url(raw_h_req_url, "Hero Request URL")







            cs.hero_req_btn_url = raw_h_req_url or '#contact'







            cs.hero_contact_btn_text = request.POST.get('hero_contact_btn_text', cs.hero_contact_btn_text).strip()







            raw_h_ct_url = request.POST.get('hero_contact_btn_url', '').strip()







            if raw_h_ct_url:







                validate_safe_url(raw_h_ct_url, "Hero Contact URL")







            cs.hero_contact_btn_url = raw_h_ct_url or '/contact/'















            if 'hero_image' in request.FILES:







                validate_image_upload(request.FILES['hero_image'], "Hero Visual Image")







                cs.hero_image = request.FILES['hero_image']







            elif request.POST.get('remove_hero_image') == '1':







                cs.hero_image = None















            # 2. About Section & 3 Stats







            cs.about_tag = request.POST.get('about_tag', cs.about_tag).strip()







            cs.about_title = request.POST.get('about_title', cs.about_title).strip()







            cs.about_description = request.POST.get('about_description', cs.about_description).strip()







            cs.about_stat1_value = request.POST.get('about_stat1_value', cs.about_stat1_value).strip()







            cs.about_stat1_label = request.POST.get('about_stat1_label', cs.about_stat1_label).strip()







            cs.about_stat1_icon = request.POST.get('about_stat1_icon', cs.about_stat1_icon).strip()







            cs.about_stat2_value = request.POST.get('about_stat2_value', cs.about_stat2_value).strip()







            cs.about_stat2_label = request.POST.get('about_stat2_label', cs.about_stat2_label).strip()







            cs.about_stat2_icon = request.POST.get('about_stat2_icon', cs.about_stat2_icon).strip()







            cs.about_stat3_value = request.POST.get('about_stat3_value', cs.about_stat3_value).strip()







            cs.about_stat3_label = request.POST.get('about_stat3_label', cs.about_stat3_label).strip()







            cs.about_stat3_icon = request.POST.get('about_stat3_icon', cs.about_stat3_icon).strip()















            # 3. Services Tag







            cs.services_tag = request.POST.get('services_tag', cs.services_tag).strip()















            # 4. Industries & Why Choose Section







            cs.industries_tag = request.POST.get('industries_tag', cs.industries_tag).strip()







            if 'center_image' in request.FILES:







                validate_image_upload(request.FILES['center_image'], "Center Activities Image")







                cs.center_image = request.FILES['center_image']







            cs.why_choose_tag = request.POST.get('why_choose_tag', cs.why_choose_tag).strip()















            # 5. Process Section







            cs.process_tag = request.POST.get('process_tag', cs.process_tag).strip()







            cs.process_title = request.POST.get('process_title', cs.process_title).strip()







            cs.process_subtitle = request.POST.get('process_subtitle', cs.process_subtitle).strip()















            # 6. Benefits & FAQs Section







            cs.benefits_tag = request.POST.get('benefits_tag', cs.benefits_tag).strip()







            cs.benefits_employer_title = request.POST.get('benefits_employer_title', cs.benefits_employer_title).strip()







            cs.benefits_candidate_title = request.POST.get('benefits_candidate_title', cs.benefits_candidate_title).strip()







            cs.faq_tag = request.POST.get('faq_tag', cs.faq_tag).strip()















            # 7. Bottom CTA Banner







            cs.cta_tag = request.POST.get('cta_tag', cs.cta_tag).strip()







            cs.cta_title = request.POST.get('cta_title', cs.cta_title).strip()







            cs.cta_subtitle = request.POST.get('cta_subtitle', cs.cta_subtitle).strip()







            cs.cta_btn1_text = request.POST.get('cta_btn1_text', cs.cta_btn1_text).strip()







            raw_c_b1 = request.POST.get('cta_btn1_url', '').strip()







            if raw_c_b1:







                validate_safe_url(raw_c_b1, "CTA Button 1 URL")







            cs.cta_btn1_url = raw_c_b1 or '/contact/'







            cs.cta_btn2_text = request.POST.get('cta_btn2_text', cs.cta_btn2_text).strip()







            raw_c_b2 = request.POST.get('cta_btn2_url', '').strip()







            if raw_c_b2:







                validate_safe_url(raw_c_b2, "CTA Button 2 URL")







            cs.cta_btn2_url = raw_c_b2 or '/contact/'















            # 8. SEO & Social Meta







            cs.meta_title = request.POST.get('meta_title', cs.meta_title).strip()







            cs.meta_description = request.POST.get('meta_description', cs.meta_description).strip()







            if 'og_image' in request.FILES:







                validate_image_upload(request.FILES['og_image'], "OG Image")







                cs.og_image = request.FILES['og_image']















            cs.save()















            # --- JSON Repeaters ---







            # 1. CsServiceCard







            srv_raw = request.POST.get('cs_services_json')







            if srv_raw:







                try:







                    srv_data = json.loads(srv_raw)







                    seen_srv_ids = []







                    for idx, item in enumerate(srv_data, 1):







                        item_id = item.get('id')







                        srv_obj = CsServiceCard.objects.filter(id=item_id).first() if item_id else CsServiceCard()







                        t_val = str(item.get('title') or '').strip()







                        if not t_val:







                            continue







                        srv_obj.title = t_val







                        srv_obj.description = str(item.get('description') or '').strip()







                        srv_obj.icon_class = str(item.get('icon_class') or 'fa-regular fa-clock').strip()







                        srv_obj.order = int(item.get('order', idx))







                        srv_obj.is_visible = bool(item.get('is_visible', True))







                        srv_obj.save()







                        seen_srv_ids.append(srv_obj.id)







                    CsServiceCard.objects.exclude(id__in=seen_srv_ids).delete()







                except Exception:







                    pass















            # 2. CsIndustryItem







            ind_raw = request.POST.get('cs_industries_json')







            if ind_raw:







                try:







                    ind_data = json.loads(ind_raw)







                    seen_ind_ids = []







                    for idx, item in enumerate(ind_data, 1):







                        item_id = item.get('id')







                        ind_obj = CsIndustryItem.objects.filter(id=item_id).first() if item_id else CsIndustryItem()







                        n_val = str(item.get('name') or '').strip()







                        if not n_val:







                            continue







                        ind_obj.name = n_val







                        ind_obj.icon_class = str(item.get('icon_class') or 'fa-solid fa-industry').strip()







                        ind_obj.order = int(item.get('order', idx))







                        ind_obj.is_visible = bool(item.get('is_visible', True))







                        ind_obj.save()







                        seen_ind_ids.append(ind_obj.id)







                    CsIndustryItem.objects.exclude(id__in=seen_ind_ids).delete()







                except Exception:







                    pass















            # 3. CsWhyChooseItem







            wc_raw = request.POST.get('cs_why_choose_json')







            if wc_raw:







                try:







                    wc_data = json.loads(wc_raw)







                    seen_wc_ids = []







                    for idx, item in enumerate(wc_data, 1):







                        item_id = item.get('id')







                        wc_obj = CsWhyChooseItem.objects.filter(id=item_id).first() if item_id else CsWhyChooseItem()







                        t_val = str(item.get('text') or '').strip()







                        if not t_val:







                            continue







                        wc_obj.text = t_val







                        wc_obj.icon_class = str(item.get('icon_class') or 'fa-solid fa-circle-check').strip()







                        wc_obj.order = int(item.get('order', idx))







                        wc_obj.is_visible = bool(item.get('is_visible', True))







                        wc_obj.save()







                        seen_wc_ids.append(wc_obj.id)







                    CsWhyChooseItem.objects.exclude(id__in=seen_wc_ids).delete()







                except Exception:







                    pass















            # 4. CsProcessStep







            proc_raw = request.POST.get('cs_process_json')







            if proc_raw:







                try:







                    proc_data = json.loads(proc_raw)







                    seen_proc_ids = []







                    for idx, item in enumerate(proc_data, 1):







                        item_id = item.get('id')







                        proc_obj = CsProcessStep.objects.filter(id=item_id).first() if item_id else CsProcessStep()







                        t_val = str(item.get('title') or '').strip()







                        if not t_val:







                            continue







                        proc_obj.step_number = str(item.get('step_number') or f"0{idx}").strip()







                        proc_obj.title = t_val







                        proc_obj.description = str(item.get('description') or '').strip()







                        proc_obj.icon_class = str(item.get('icon_class') or 'fa-solid fa-comments').strip()







                        proc_obj.order = int(item.get('order', idx))







                        proc_obj.is_visible = bool(item.get('is_visible', True))







                        proc_obj.save()







                        seen_proc_ids.append(proc_obj.id)







                    CsProcessStep.objects.exclude(id__in=seen_proc_ids).delete()







                except Exception:







                    pass















            # 5. CsBenefitEmployerItem







            emp_raw = request.POST.get('cs_employer_benefits_json')







            if emp_raw:







                try:







                    emp_data = json.loads(emp_raw)







                    seen_emp_ids = []







                    for idx, item in enumerate(emp_data, 1):







                        item_id = item.get('id')







                        emp_obj = CsBenefitEmployerItem.objects.filter(id=item_id).first() if item_id else CsBenefitEmployerItem()







                        t_val = str(item.get('text') or '').strip()







                        if not t_val:







                            continue







                        emp_obj.text = t_val







                        emp_obj.icon_class = str(item.get('icon_class') or 'fa-solid fa-circle-check').strip()







                        emp_obj.order = int(item.get('order', idx))







                        emp_obj.is_visible = bool(item.get('is_visible', True))







                        emp_obj.save()







                        seen_emp_ids.append(emp_obj.id)







                    CsBenefitEmployerItem.objects.exclude(id__in=seen_emp_ids).delete()







                except Exception:







                    pass















            # 6. CsBenefitCandidateItem







            cand_raw = request.POST.get('cs_candidate_benefits_json')







            if cand_raw:







                try:







                    cand_data = json.loads(cand_raw)







                    seen_cand_ids = []







                    for idx, item in enumerate(cand_data, 1):







                        item_id = item.get('id')







                        cand_obj = CsBenefitCandidateItem.objects.filter(id=item_id).first() if item_id else CsBenefitCandidateItem()







                        t_val = str(item.get('text') or '').strip()







                        if not t_val:







                            continue







                        cand_obj.text = t_val







                        cand_obj.icon_class = str(item.get('icon_class') or 'fa-solid fa-circle-check').strip()







                        cand_obj.order = int(item.get('order', idx))







                        cand_obj.is_visible = bool(item.get('is_visible', True))







                        cand_obj.save()







                        seen_cand_ids.append(cand_obj.id)







                    CsBenefitCandidateItem.objects.exclude(id__in=seen_cand_ids).delete()







                except Exception:







                    pass















            # 7. CsFaqItem







            faq_raw = request.POST.get('cs_faqs_json')







            if faq_raw:







                try:







                    faq_data = json.loads(faq_raw)







                    seen_f_ids = []







                    for idx, item in enumerate(faq_data, 1):







                        item_id = item.get('id')







                        f_obj = CsFaqItem.objects.filter(id=item_id).first() if item_id else CsFaqItem()







                        q_val = str(item.get('question') or '').strip()







                        a_val = str(item.get('answer') or '').strip()







                        if not q_val:







                            continue







                        f_obj.question = q_val







                        f_obj.answer = a_val







                        f_obj.order = int(item.get('order', idx))







                        f_obj.is_visible = bool(item.get('is_visible', True))







                        f_obj.save()







                        seen_f_ids.append(f_obj.id)







                    CsFaqItem.objects.exclude(id__in=seen_f_ids).delete()







                except Exception:







                    pass















            cache.delete(CONTRACT_STAFFING_CACHE_KEY)







            cache.delete('public_site_context')















            try:







                log_activity(







                    admin_user,







                    "Website Content Updated",







                    "Updated Contract Staffing service page dynamic sections and published live."







                )







            except Exception:







                pass















            messages.success(request, "Contract Staffing page content updated and published live successfully!")







            return True















    except Exception as e:







        messages.error(request, f"Error updating Contract Staffing content: {str(e)}")







        return False































def handle_educational_consultancy_save(request, admin_user):







    from django.db import transaction







    from django.core.cache import cache







    from django.contrib import messages







    import json







    from apps.core.models import (







        EDUCATIONAL_CONSULTANCY_CACHE_KEY,







        EducationalConsultancySettings,







        EcServiceCard,







        EcWhyChooseItem,







        EcProcessStep,







    )







    from apps.enquiries.models import log_activity















    try:







        with transaction.atomic():







            ec = EducationalConsultancySettings.get_settings()















            # Master Section Visibility Switches







            ec.hero_visible = ('hero_visible' in request.POST)







            ec.services_visible = ('services_visible' in request.POST)







            ec.why_choose_visible = ('why_choose_visible' in request.POST)







            ec.process_visible = ('process_visible' in request.POST)







            ec.stats_visible = ('stats_visible' in request.POST)







            ec.cta_visible = ('cta_visible' in request.POST)















            def clean_text_field(val, fallback=''):







                import re







                if not val:







                    return fallback







                clean = re.sub(r'<[^>]+>', '', str(val))







                clean = clean.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')







                return re.sub(r'\s+', ' ', clean).strip()















            def parse_bool_val(v, default=True):







                if v is None:







                    return default







                if isinstance(v, bool):







                    return v







                if isinstance(v, (int, float)):







                    return bool(v)







                s = str(v).strip().lower()







                if s in ('true', '1', 'yes', 'on'):







                    return True







                if s in ('false', '0', 'no', 'off', ''):







                    return False







                return default























            # 1. Hero Section







            ec.hero_eyebrow = request.POST.get('hero_eyebrow', ec.hero_eyebrow).strip()







            ec.hero_title = clean_text_field(request.POST.get('hero_title'), ec.hero_title)







            ec.hero_subhead = request.POST.get('hero_subhead', ec.hero_subhead).strip()







            ec.hero_subtitle = request.POST.get('hero_subtitle', ec.hero_subtitle).strip()







            ec.hero_counsel_btn_text = request.POST.get('hero_counsel_btn_text', ec.hero_counsel_btn_text).strip()







            raw_counsel_url = request.POST.get('hero_counsel_btn_url', '').strip()







            if raw_counsel_url:







                validate_safe_url(raw_counsel_url, "Hero Counselling URL")







            ec.hero_counsel_btn_url = raw_counsel_url or '#contact'















            ec.hero_contact_btn_text = request.POST.get('hero_contact_btn_text', ec.hero_contact_btn_text).strip()







            raw_h_ct_url = request.POST.get('hero_contact_btn_url', '').strip()







            if raw_h_ct_url:







                validate_safe_url(raw_h_ct_url, "Hero Contact URL")







            ec.hero_contact_btn_url = raw_h_ct_url or '/contact/'















            if 'hero_image' in request.FILES:







                validate_image_upload(request.FILES['hero_image'], "Hero Banner Image")







                ec.hero_image = request.FILES['hero_image']







            elif request.POST.get('remove_hero_image') == '1':







                ec.hero_image = None















            # 2. Services Section







            ec.services_title = clean_text_field(request.POST.get('services_title'), ec.services_title)















            # 3. Why Choose Section







            ec.why_choose_title = clean_text_field(request.POST.get('why_choose_title'), ec.why_choose_title)







            if 'why_choose_image' in request.FILES:







                validate_image_upload(request.FILES['why_choose_image'], "Why Choose Photo")







                ec.why_choose_image = request.FILES['why_choose_image']







            elif request.POST.get('remove_why_choose_image') == '1':







                ec.why_choose_image = None















            # 4. Process Section







            ec.process_title = clean_text_field(request.POST.get('process_title'), ec.process_title)















            # 5. Stats Bar







            ec.stat1_value = request.POST.get('stat1_value', ec.stat1_value).strip()







            ec.stat1_label = request.POST.get('stat1_label', ec.stat1_label).strip()







            ec.stat1_icon = request.POST.get('stat1_icon', ec.stat1_icon).strip()















            ec.stat2_value = request.POST.get('stat2_value', ec.stat2_value).strip()







            ec.stat2_label = request.POST.get('stat2_label', ec.stat2_label).strip()







            ec.stat2_icon = request.POST.get('stat2_icon', ec.stat2_icon).strip()















            ec.stat3_value = request.POST.get('stat3_value', ec.stat3_value).strip()







            ec.stat3_label = request.POST.get('stat3_label', ec.stat3_label).strip()







            ec.stat3_icon = request.POST.get('stat3_icon', ec.stat3_icon).strip()















            ec.stat4_value = request.POST.get('stat4_value', ec.stat4_value).strip()







            ec.stat4_label = request.POST.get('stat4_label', ec.stat4_label).strip()







            ec.stat4_icon = request.POST.get('stat4_icon', ec.stat4_icon).strip()















            # 6. Bottom CTA & SEO







            ec.cta_title = request.POST.get('cta_title', ec.cta_title).strip()







            ec.cta_subtitle = request.POST.get('cta_subtitle', ec.cta_subtitle).strip()







            ec.cta_btn_text = request.POST.get('cta_btn_text', ec.cta_btn_text).strip()







            raw_cta_url = request.POST.get('cta_btn_url', '').strip()







            if raw_cta_url:







                validate_safe_url(raw_cta_url, "CTA Button URL")







            ec.cta_btn_url = raw_cta_url or '/contact/'















            ec.cta_btn2_text = request.POST.get('cta_btn2_text', ec.cta_btn2_text).strip()







            raw_cta2_url = request.POST.get('cta_btn2_url', '').strip()







            if raw_cta2_url:







                validate_safe_url(raw_cta2_url, "CTA Secondary Button URL")







            ec.cta_btn2_url = raw_cta2_url or '/contact/'















            ec.meta_title = request.POST.get('meta_title', ec.meta_title).strip()







            ec.meta_description = request.POST.get('meta_description', ec.meta_description).strip()







            ec.meta_keywords = request.POST.get('meta_keywords', ec.meta_keywords).strip()















            ec.save()















            # Process Repeaters from JSON







            # 1. EcServiceCard







            srv_raw = request.POST.get('ec_services_json')







            if srv_raw:







                try:







                    srv_data = json.loads(srv_raw)







                    seen_srv_ids = []







                    for idx, item in enumerate(srv_data, 1):







                        item_id = item.get('id')







                        srv_obj = EcServiceCard.objects.filter(id=item_id).first() if item_id else EcServiceCard()







                        t_val = str(item.get('title') or '').strip()







                        if not t_val:







                            continue







                        srv_obj.title = t_val







                        srv_obj.description = str(item.get('description') or '').strip()







                        srv_obj.icon_class = str(item.get('icon_class') or 'fa-solid fa-graduation-cap').strip()







                        srv_obj.badge_theme = str(item.get('badge_theme') or 'navy').strip()







                        srv_obj.order = int(item.get('order', idx))







                        srv_obj.is_visible = bool(item.get('is_visible', True))







                        srv_obj.save()







                        seen_srv_ids.append(srv_obj.id)







                    EcServiceCard.objects.exclude(id__in=seen_srv_ids).delete()







                except Exception:







                    pass















            # 2. EcWhyChooseItem







            why_raw = request.POST.get('ec_why_choose_json')







            if why_raw:







                try:







                    why_data = json.loads(why_raw)







                    seen_why_ids = []







                    for idx, item in enumerate(why_data, 1):







                        item_id = item.get('id')







                        why_obj = EcWhyChooseItem.objects.filter(id=item_id).first() if item_id else EcWhyChooseItem()







                        t_val = str(item.get('title') or '').strip()







                        if not t_val:







                            continue







                        why_obj.title = t_val







                        why_obj.description = str(item.get('description') or '').strip()







                        why_obj.icon_class = str(item.get('icon_class') or 'fa-solid fa-user-graduate').strip()







                        why_obj.order = int(item.get('order', idx))







                        why_obj.is_visible = bool(item.get('is_visible', True))







                        why_obj.save()







                        seen_why_ids.append(why_obj.id)







                    EcWhyChooseItem.objects.exclude(id__in=seen_why_ids).delete()







                except Exception:







                    pass















            # 3. EcProcessStep







            proc_raw = request.POST.get('ec_process_json')







            if proc_raw:







                try:







                    proc_data = json.loads(proc_raw)







                    seen_proc_ids = []







                    for idx, item in enumerate(proc_data, 1):







                        item_id = item.get('id')







                        proc_obj = EcProcessStep.objects.filter(id=item_id).first() if item_id else EcProcessStep()







                        t_val = str(item.get('title') or '').strip()







                        if not t_val:







                            continue







                        proc_obj.step_number = str(item.get('step_number') or f"0{idx}").strip()







                        proc_obj.title = t_val







                        proc_obj.description = str(item.get('description') or '').strip()







                        proc_obj.icon_class = str(item.get('icon_class') or 'fa-solid fa-comment-dots').strip()







                        proc_obj.order = int(item.get('order', idx))







                        proc_obj.is_visible = bool(item.get('is_visible', True))







                        proc_obj.save()







                        seen_proc_ids.append(proc_obj.id)







                    EcProcessStep.objects.exclude(id__in=seen_proc_ids).delete()







                except Exception:







                    pass















            cache.delete(EDUCATIONAL_CONSULTANCY_CACHE_KEY)







            cache.delete('public_site_context')















            try:







                log_activity(







                    admin_user,







                    "Website Content Updated",







                    "Updated Educational Consultancy service page dynamic sections and published live."







                )







            except Exception:







                pass















            messages.success(request, "Educational Consultancy page content updated and published live successfully!")







            return True















    except Exception as e:







        messages.error(request, f"Error updating Educational Consultancy content: {str(e)}")







        return False























def handle_payroll_outsourcing_save(request, admin_user):







    from django.db import transaction







    from django.core.cache import cache







    from django.contrib import messages







    import json







    from apps.core.models import (







        PAYROLL_OUTSOURCING_CACHE_KEY,







        PayrollOutsourcingSettings,







        PoServiceCard,







        PoIndustryItem,







        PoWhyChooseItem,







        PoProcessStep,







        PoEmployerBenefit,







        PoEmployeeBenefit,







        PoFaqItem,







    )







    from apps.enquiries.models import log_activity















    try:







        with transaction.atomic():







            po = PayrollOutsourcingSettings.get_settings()















            # Master Section Visibility Switches







            po.hero_visible = ('hero_visible' in request.POST)







            po.about_visible = ('about_visible' in request.POST)







            po.services_visible = ('services_visible' in request.POST)







            po.panel_visible = ('panel_visible' in request.POST)







            po.compare_visible = ('compare_visible' in request.POST)







            po.faq_visible = ('faq_visible' in request.POST)







            po.cta_visible = ('cta_visible' in request.POST)















            def clean_text_field(val, fallback=''):







                import re







                if not val:







                    return fallback







                clean = re.sub(r'<[^>]+>', '', str(val))







                clean = clean.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')







                return re.sub(r'\s+', ' ', clean).strip()















            def parse_bool_val(v, default=True):







                if v is None:







                    return default







                if isinstance(v, bool):







                    return v







                if isinstance(v, (int, float)):







                    return bool(v)







                s = str(v).strip().lower()







                if s in ('true', '1', 'yes', 'on'):







                    return True







                if s in ('false', '0', 'no', 'off', ''):







                    return False







                return default















            # 1. Hero Section







            po.hero_eyebrow = request.POST.get('hero_eyebrow', po.hero_eyebrow).strip()







            po.hero_title = clean_text_field(request.POST.get('hero_title'), po.hero_title)







            po.hero_subtitle = request.POST.get('hero_subtitle', po.hero_subtitle).strip()







            po.hero_primary_btn_text = request.POST.get('hero_primary_btn_text', po.hero_primary_btn_text).strip()







            raw_p_btn_url = request.POST.get('hero_primary_btn_url', '').strip()







            if raw_p_btn_url:







                validate_safe_url(raw_p_btn_url, "Hero Primary Button URL")







            po.hero_primary_btn_url = raw_p_btn_url or '#contact'















            po.hero_secondary_btn_text = request.POST.get('hero_secondary_btn_text', po.hero_secondary_btn_text).strip()







            raw_s_btn_url = request.POST.get('hero_secondary_btn_url', '').strip()







            if raw_s_btn_url:







                validate_safe_url(raw_s_btn_url, "Hero Secondary Button URL")







            po.hero_secondary_btn_url = raw_s_btn_url or '/contact/'















            if 'hero_image' in request.FILES:







                validate_image_upload(request.FILES['hero_image'], "Hero Banner Image")







                po.hero_image = request.FILES['hero_image']







            elif request.POST.get('remove_hero_image') == '1':







                po.hero_image = None















            # 2. About Section







            po.about_tag = request.POST.get('about_tag', po.about_tag).strip()







            po.about_title = clean_text_field(request.POST.get('about_title'), po.about_title)







            po.about_description = request.POST.get('about_description', po.about_description).strip()







            if 'about_image' in request.FILES:







                validate_image_upload(request.FILES['about_image'], "About Image")







                po.about_image = request.FILES['about_image']







            elif request.POST.get('remove_about_image') == '1':







                po.about_image = None















            # 3. Services Grid Section







            po.services_title = clean_text_field(request.POST.get('services_title'), po.services_title)















            # 4. Triple Panel Section







            po.industries_tag = request.POST.get('industries_tag', po.industries_tag).strip()







            po.why_choose_tag = request.POST.get('why_choose_tag', po.why_choose_tag).strip()







            po.process_tag = request.POST.get('process_tag', po.process_tag).strip()















            # 5. Compare Section







            po.employers_badge = request.POST.get('employers_badge', po.employers_badge).strip()







            po.employees_badge = request.POST.get('employees_badge', po.employees_badge).strip()















            # 6. FAQ Section







            po.faq_title = clean_text_field(request.POST.get('faq_title'), po.faq_title)















            # 7. CTA & SEO







            po.cta_title = clean_text_field(request.POST.get('cta_title'), po.cta_title)







            po.cta_subtitle = request.POST.get('cta_subtitle', po.cta_subtitle).strip()







            po.cta_primary_btn_text = request.POST.get('cta_primary_btn_text', po.cta_primary_btn_text).strip()







            raw_cta_p_url = request.POST.get('cta_primary_btn_url', '').strip()







            if raw_cta_p_url:







                validate_safe_url(raw_cta_p_url, "CTA Primary Button URL")







            po.cta_primary_btn_url = raw_cta_p_url or '#contact'















            po.cta_secondary_btn_text = request.POST.get('cta_secondary_btn_text', po.cta_secondary_btn_text).strip()







            raw_cta_s_url = request.POST.get('cta_secondary_btn_url', '').strip()







            if raw_cta_s_url:







                validate_safe_url(raw_cta_s_url, "CTA Secondary Button URL")







            po.cta_secondary_btn_url = raw_cta_s_url or '/contact/'















            po.meta_title = request.POST.get('meta_title', po.meta_title).strip()







            po.meta_description = request.POST.get('meta_description', po.meta_description).strip()







            po.meta_keywords = request.POST.get('meta_keywords', po.meta_keywords).strip()















            po.save()















            # 1. PoServiceCard







            srv_raw = request.POST.get('po_services_json')







            if srv_raw:







                try:







                    srv_data = json.loads(srv_raw)







                    seen_srv_ids = []







                    for idx, item in enumerate(srv_data, 1):







                        item_id = item.get('id')







                        srv_obj = PoServiceCard.objects.filter(id=item_id).first() if item_id else PoServiceCard()







                        t_val = str(item.get('title') or '').strip()







                        if not t_val:







                            continue







                        srv_obj.title = t_val







                        srv_obj.description = str(item.get('description') or '').strip()







                        srv_obj.icon_class = str(item.get('icon_class') or 'fa-solid fa-file-invoice').strip()







                        srv_obj.badge_theme = str(item.get('badge_theme') or 'navy').strip()







                        srv_obj.order = int(item.get('order', idx))







                        srv_obj.is_visible = parse_bool_val(item.get('is_visible'), True)







                        srv_obj.save()







                        seen_srv_ids.append(srv_obj.id)







                    PoServiceCard.objects.exclude(id__in=seen_srv_ids).delete()







                except Exception:







                    pass















            # 2. PoIndustryItem







            ind_raw = request.POST.get('po_industries_json')







            if ind_raw:







                try:







                    ind_data = json.loads(ind_raw)







                    seen_ind_ids = []







                    for idx, item in enumerate(ind_data, 1):







                        item_id = item.get('id')







                        ind_obj = PoIndustryItem.objects.filter(id=item_id).first() if item_id else PoIndustryItem()







                        n_val = str(item.get('name') or '').strip()







                        if not n_val:







                            continue







                        ind_obj.name = n_val







                        ind_obj.order = int(item.get('order', idx))







                        ind_obj.is_visible = parse_bool_val(item.get('is_visible'), True)







                        ind_obj.save()







                        seen_ind_ids.append(ind_obj.id)







                    PoIndustryItem.objects.exclude(id__in=seen_ind_ids).delete()







                except Exception:







                    pass















            # 3. PoWhyChooseItem







            why_raw = request.POST.get('po_why_choose_json')







            if why_raw:







                try:







                    why_data = json.loads(why_raw)







                    seen_why_ids = []







                    for idx, item in enumerate(why_data, 1):







                        item_id = item.get('id')







                        why_obj = PoWhyChooseItem.objects.filter(id=item_id).first() if item_id else PoWhyChooseItem()







                        t_val = str(item.get('title') or '').strip()







                        if not t_val:







                            continue







                        why_obj.title = t_val







                        why_obj.order = int(item.get('order', idx))







                        why_obj.is_visible = parse_bool_val(item.get('is_visible'), True)







                        why_obj.save()







                        seen_why_ids.append(why_obj.id)







                    PoWhyChooseItem.objects.exclude(id__in=seen_why_ids).delete()







                except Exception:







                    pass















            # 4. PoProcessStep







            proc_raw = request.POST.get('po_process_json')







            if proc_raw:







                try:







                    proc_data = json.loads(proc_raw)







                    seen_proc_ids = []







                    for idx, item in enumerate(proc_data, 1):







                        item_id = item.get('id')







                        proc_obj = PoProcessStep.objects.filter(id=item_id).first() if item_id else PoProcessStep()







                        t_val = str(item.get('title') or '').strip()







                        if not t_val:







                            continue







                        proc_obj.step_number = str(item.get('step_number') or f"0{idx}").strip()







                        proc_obj.title = t_val







                        proc_obj.icon_class = str(item.get('icon_class') or 'fa-solid fa-database').strip()







                        proc_obj.order = int(item.get('order', idx))







                        proc_obj.is_visible = parse_bool_val(item.get('is_visible'), True)







                        proc_obj.save()







                        seen_proc_ids.append(proc_obj.id)







                    PoProcessStep.objects.exclude(id__in=seen_proc_ids).delete()







                except Exception:







                    pass















            # 5. PoEmployerBenefit







            emp_raw = request.POST.get('po_employer_benefits_json')







            if emp_raw:







                try:







                    emp_data = json.loads(emp_raw)







                    seen_emp_ids = []







                    for idx, item in enumerate(emp_data, 1):







                        item_id = item.get('id')







                        emp_obj = PoEmployerBenefit.objects.filter(id=item_id).first() if item_id else PoEmployerBenefit()







                        t_val = str(item.get('title') or '').strip()







                        if not t_val:







                            continue







                        emp_obj.title = t_val







                        emp_obj.order = int(item.get('order', idx))







                        emp_obj.is_visible = parse_bool_val(item.get('is_visible'), True)







                        emp_obj.save()







                        seen_emp_ids.append(emp_obj.id)







                    PoEmployerBenefit.objects.exclude(id__in=seen_emp_ids).delete()







                except Exception:







                    pass















            # 6. PoEmployeeBenefit







            ee_raw = request.POST.get('po_employee_benefits_json')







            if ee_raw:







                try:







                    ee_data = json.loads(ee_raw)







                    seen_ee_ids = []







                    for idx, item in enumerate(ee_data, 1):







                        item_id = item.get('id')







                        ee_obj = PoEmployeeBenefit.objects.filter(id=item_id).first() if item_id else PoEmployeeBenefit()







                        t_val = str(item.get('title') or '').strip()







                        if not t_val:







                            continue







                        ee_obj.title = t_val







                        ee_obj.order = int(item.get('order', idx))







                        ee_obj.is_visible = parse_bool_val(item.get('is_visible'), True)







                        ee_obj.save()







                        seen_ee_ids.append(ee_obj.id)







                    PoEmployeeBenefit.objects.exclude(id__in=seen_ee_ids).delete()







                except Exception:







                    pass















            # 7. PoFaqItem







            faq_raw = request.POST.get('po_faqs_json')







            if faq_raw:







                try:







                    faq_data = json.loads(faq_raw)







                    seen_faq_ids = []







                    for idx, item in enumerate(faq_data, 1):







                        item_id = item.get('id')







                        faq_obj = PoFaqItem.objects.filter(id=item_id).first() if item_id else PoFaqItem()







                        q_val = str(item.get('question') or '').strip()







                        if not q_val:







                            continue







                        faq_obj.question = q_val







                        faq_obj.answer = str(item.get('answer') or '').strip()







                        faq_obj.order = int(item.get('order', idx))







                        faq_obj.is_visible = parse_bool_val(item.get('is_visible'), True)







                        faq_obj.save()







                        seen_faq_ids.append(faq_obj.id)







                    PoFaqItem.objects.exclude(id__in=seen_faq_ids).delete()







                except Exception:







                    pass















            cache.delete(PAYROLL_OUTSOURCING_CACHE_KEY)







            cache.delete('public_site_context')















            try:







                log_activity(







                    admin_user,







                    "Website Content Updated",







                    "Updated Payroll & Outsourcing service page dynamic sections and published live."







                )







            except Exception:







                pass















            messages.success(request, "Payroll & Outsourcing page content updated and published live successfully!")







            return True















    except Exception as e:







        messages.error(request, f"Error updating Payroll & Outsourcing content: {str(e)}")







        return False























def handle_hr_support_save(request, admin_user):



    from django.db import transaction



    from django.core.cache import cache



    from django.contrib import messages



    import json



    from apps.core.models import (



        HR_SUPPORT_CACHE_KEY,



        HrSupportSettings,



        HrFeatureItem,



        HrServiceCard,



        HrAdditionalServiceItem,



        HrWhyChooseItem,



        HrProcessStep,



        HrEmployerBenefit,



        HrEmployeeBenefit,



    )



    from apps.enquiries.models import log_activity







    try:



        with transaction.atomic():



            hr = HrSupportSettings.get_settings()







            # Master Section Visibility Switches



            hr.hero_visible = ('hero_visible' in request.POST)



            hr.about_visible = ('about_visible' in request.POST)



            hr.services_visible = ('services_visible' in request.POST)



            hr.additional_visible = ('additional_visible' in request.POST)



            hr.why_choose_visible = ('why_choose_visible' in request.POST)



            hr.process_visible = ('process_visible' in request.POST)



            hr.benefits_visible = ('benefits_visible' in request.POST)



            hr.cta_visible = ('cta_visible' in request.POST)







            def clean_text_field(val, fallback=''):



                import re



                if not val:



                    return fallback



                clean = re.sub(r'<[^>]+>', '', str(val))



                clean = clean.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')



                return re.sub(r'\s+', ' ', clean).strip()







            def parse_bool_val(v, default=True):



                if v is None:



                    return default



                if isinstance(v, bool):



                    return v



                if isinstance(v, (int, float)):



                    return bool(v)



                s = str(v).strip().lower()



                if s in ('true', '1', 'yes', 'on'):



                    return True



                if s in ('false', '0', 'no', 'off'):



                    return False



                return default







            # 1. Hero



            hr.hero_eyebrow = clean_text_field(request.POST.get('hero_eyebrow'), hr.hero_eyebrow)



            hr.hero_title = clean_text_field(request.POST.get('hero_title'), hr.hero_title)



            hr.hero_subtitle = clean_text_field(request.POST.get('hero_subtitle'), hr.hero_subtitle)



            hr.hero_primary_btn_text = clean_text_field(request.POST.get('hero_primary_btn_text'), hr.hero_primary_btn_text)



            hr.hero_primary_btn_url = clean_text_field(request.POST.get('hero_primary_btn_url'), hr.hero_primary_btn_url)



            hr.hero_secondary_btn_text = clean_text_field(request.POST.get('hero_secondary_btn_text'), hr.hero_secondary_btn_text)



            hr.hero_secondary_btn_url = clean_text_field(request.POST.get('hero_secondary_btn_url'), hr.hero_secondary_btn_url)



            if 'hero_image' in request.FILES:



                hr.hero_image = request.FILES['hero_image']







            # 2. About



            hr.about_tag = clean_text_field(request.POST.get('about_tag'), hr.about_tag)



            hr.about_title = clean_text_field(request.POST.get('about_title'), hr.about_title)



            hr.about_description = clean_text_field(request.POST.get('about_description'), hr.about_description)







            # 3. Services Grid



            hr.services_tag = clean_text_field(request.POST.get('services_tag'), hr.services_tag)



            hr.services_title = clean_text_field(request.POST.get('services_title'), hr.services_title)







            # 4. Additional Services



            hr.additional_title = clean_text_field(request.POST.get('additional_title'), hr.additional_title)







            # 5. Why Choose Us



            hr.why_choose_tag = clean_text_field(request.POST.get('why_choose_tag'), hr.why_choose_tag)



            if 'why_choose_image' in request.FILES:



                hr.why_choose_image = request.FILES['why_choose_image']







            # 6. Process



            hr.process_tag = clean_text_field(request.POST.get('process_tag'), hr.process_tag)







            # 7. Benefits



            hr.benefits_tag = clean_text_field(request.POST.get('benefits_tag'), hr.benefits_tag)



            hr.employers_badge = clean_text_field(request.POST.get('employers_badge'), hr.employers_badge)



            hr.employees_badge = clean_text_field(request.POST.get('employees_badge'), hr.employees_badge)







            # 8. CTA & SEO



            hr.cta_title = clean_text_field(request.POST.get('cta_title'), hr.cta_title)



            hr.cta_subtitle = clean_text_field(request.POST.get('cta_subtitle'), hr.cta_subtitle)



            hr.cta_primary_btn_text = clean_text_field(request.POST.get('cta_primary_btn_text'), hr.cta_primary_btn_text)



            hr.cta_primary_btn_url = clean_text_field(request.POST.get('cta_primary_btn_url'), hr.cta_primary_btn_url)



            hr.cta_secondary_btn_text = clean_text_field(request.POST.get('cta_secondary_btn_text'), hr.cta_secondary_btn_text)



            hr.cta_secondary_btn_url = clean_text_field(request.POST.get('cta_secondary_btn_url'), hr.cta_secondary_btn_url)



            hr.meta_title = clean_text_field(request.POST.get('meta_title'), hr.meta_title)



            hr.meta_description = clean_text_field(request.POST.get('meta_description'), hr.meta_description)



            hr.meta_keywords = clean_text_field(request.POST.get('meta_keywords'), hr.meta_keywords)







            hr.save()







            # Repeater Sync 1: About Features



            features_raw = request.POST.get('hr_features_json')



            if features_raw:



                try:



                    feat_list = json.loads(features_raw)



                    seen_feat_ids = []



                    for idx, item in enumerate(feat_list, 1):



                        item_id = item.get('id')



                        feat_obj = HrFeatureItem.objects.filter(id=item_id).first() if item_id else HrFeatureItem()



                        t_val = clean_text_field(item.get('title'))



                        if not t_val:



                            continue



                        feat_obj.title = t_val



                        feat_obj.icon_class = clean_text_field(item.get('icon_class'), 'fa-solid fa-check')



                        feat_obj.order = int(item.get('order', idx))



                        feat_obj.is_visible = parse_bool_val(item.get('is_visible'), True)



                        feat_obj.save()



                        seen_feat_ids.append(feat_obj.id)



                    HrFeatureItem.objects.exclude(id__in=seen_feat_ids).delete()



                except Exception:



                    pass







            # Repeater Sync 2: Services Grid Cards



            services_raw = request.POST.get('hr_services_json')



            if services_raw:



                try:



                    serv_list = json.loads(services_raw)



                    seen_serv_ids = []



                    for idx, item in enumerate(serv_list, 1):



                        item_id = item.get('id')



                        serv_obj = HrServiceCard.objects.filter(id=item_id).first() if item_id else HrServiceCard()



                        t_val = clean_text_field(item.get('title'))



                        if not t_val:



                            continue



                        serv_obj.title = t_val



                        serv_obj.description = clean_text_field(item.get('description'))



                        serv_obj.icon_class = clean_text_field(item.get('icon_class'), 'fa-solid fa-file-signature')



                        serv_obj.order = int(item.get('order', idx))



                        serv_obj.is_visible = parse_bool_val(item.get('is_visible'), True)



                        serv_obj.save()



                        seen_serv_ids.append(serv_obj.id)



                    HrServiceCard.objects.exclude(id__in=seen_serv_ids).delete()



                except Exception:



                    pass







            # Repeater Sync 3: Additional Services



            add_raw = request.POST.get('hr_additional_json')



            if add_raw:



                try:



                    add_list = json.loads(add_raw)



                    seen_add_ids = []



                    for idx, item in enumerate(add_list, 1):



                        item_id = item.get('id')



                        add_obj = HrAdditionalServiceItem.objects.filter(id=item_id).first() if item_id else HrAdditionalServiceItem()



                        t_val = clean_text_field(item.get('title'))



                        if not t_val:



                            continue



                        add_obj.title = t_val



                        add_obj.icon_class = clean_text_field(item.get('icon_class'), 'fa-solid fa-briefcase')



                        add_obj.order = int(item.get('order', idx))



                        add_obj.is_visible = parse_bool_val(item.get('is_visible'), True)



                        add_obj.save()



                        seen_add_ids.append(add_obj.id)



                    HrAdditionalServiceItem.objects.exclude(id__in=seen_add_ids).delete()



                except Exception:



                    pass







            # Repeater Sync 4: Why Choose



            why_raw = request.POST.get('hr_why_choose_json')



            if why_raw:



                try:



                    why_list = json.loads(why_raw)



                    seen_why_ids = []



                    for idx, item in enumerate(why_list, 1):



                        item_id = item.get('id')



                        why_obj = HrWhyChooseItem.objects.filter(id=item_id).first() if item_id else HrWhyChooseItem()



                        t_val = clean_text_field(item.get('title'))



                        if not t_val:



                            continue



                        why_obj.title = t_val



                        why_obj.order = int(item.get('order', idx))



                        why_obj.is_visible = parse_bool_val(item.get('is_visible'), True)



                        why_obj.save()



                        seen_why_ids.append(why_obj.id)



                    HrWhyChooseItem.objects.exclude(id__in=seen_why_ids).delete()



                except Exception:



                    pass







            # Repeater Sync 5: Process Steps



            proc_raw = request.POST.get('hr_process_json')



            if proc_raw:



                try:



                    proc_list = json.loads(proc_raw)



                    seen_proc_ids = []



                    for idx, item in enumerate(proc_list, 1):



                        item_id = item.get('id')



                        proc_obj = HrProcessStep.objects.filter(id=item_id).first() if item_id else HrProcessStep()



                        t_val = clean_text_field(item.get('title'))



                        if not t_val:



                            continue



                        proc_obj.step_number = clean_text_field(item.get('step_number'), f"Step {idx}")



                        proc_obj.title = t_val



                        proc_obj.icon_class = clean_text_field(item.get('icon_class'), 'fa-solid fa-clipboard-list')



                        proc_obj.order = int(item.get('order', idx))



                        proc_obj.is_visible = parse_bool_val(item.get('is_visible'), True)



                        proc_obj.save()



                        seen_proc_ids.append(proc_obj.id)



                    HrProcessStep.objects.exclude(id__in=seen_proc_ids).delete()



                except Exception:



                    pass







            # Repeater Sync 6: Employer Benefits



            emp_raw = request.POST.get('hr_employer_benefits_json')



            if emp_raw:



                try:



                    emp_list = json.loads(emp_raw)



                    seen_emp_ids = []



                    for idx, item in enumerate(emp_list, 1):



                        item_id = item.get('id')



                        emp_obj = HrEmployerBenefit.objects.filter(id=item_id).first() if item_id else HrEmployerBenefit()



                        t_val = clean_text_field(item.get('title'))



                        if not t_val:



                            continue



                        emp_obj.title = t_val



                        emp_obj.order = int(item.get('order', idx))



                        emp_obj.is_visible = parse_bool_val(item.get('is_visible'), True)



                        emp_obj.save()



                        seen_emp_ids.append(emp_obj.id)



                    HrEmployerBenefit.objects.exclude(id__in=seen_emp_ids).delete()



                except Exception:



                    pass







            # Repeater Sync 7: Employee Benefits



            ee_raw = request.POST.get('hr_employee_benefits_json')



            if ee_raw:



                try:



                    ee_list = json.loads(ee_raw)



                    seen_ee_ids = []



                    for idx, item in enumerate(ee_list, 1):



                        item_id = item.get('id')



                        ee_obj = HrEmployeeBenefit.objects.filter(id=item_id).first() if item_id else HrEmployeeBenefit()



                        t_val = clean_text_field(item.get('title'))



                        if not t_val:



                            continue



                        ee_obj.title = t_val



                        ee_obj.order = int(item.get('order', idx))



                        ee_obj.is_visible = parse_bool_val(item.get('is_visible'), True)



                        ee_obj.save()



                        seen_ee_ids.append(ee_obj.id)



                    HrEmployeeBenefit.objects.exclude(id__in=seen_ee_ids).delete()



                except Exception:



                    pass







            cache.delete(HR_SUPPORT_CACHE_KEY)



            cache.delete('public_site_context')







            try:

                log_activity(

                    admin_user,

                    'Website Content Updated',

                    'Updated HR Support Services Configuration and published live.'

                )

            except Exception:

                pass





            messages.success(request, "HR Support content & sections saved successfully live!")



            return True







    except Exception as e:



        messages.error(request, f"Error updating HR Support content: {str(e)}")



        return False















def handle_internship_save(request, admin_user):

    from django.db import transaction

    from django.core.cache import cache

    from django.contrib import messages

    import json

    from apps.core.models import (

        INTERNSHIP_CACHE_KEY,

        InternshipSettings,

        InternshipStripItem,

        InternshipTrackItem,

        InternshipHighlightItem,

        InternshipWhoCanApplyItem,

        InternshipWhatYouLearnItem,

        InternshipProcessStep,

        InternshipBenefitItem,

        InternshipFaqItem,

    )

    from apps.enquiries.models import log_activity



    try:

        with transaction.atomic():

            intern = InternshipSettings.get_settings()



            # Master Section Visibility Switches

            intern.hero_visible = ('hero_visible' in request.POST)

            intern.strip_visible = ('strip_visible' in request.POST)

            intern.domains_visible = ('domains_visible' in request.POST)

            intern.highlights_visible = ('highlights_visible' in request.POST)

            intern.who_can_apply_visible = ('who_can_apply_visible' in request.POST)

            intern.what_you_learn_visible = ('what_you_learn_visible' in request.POST)

            intern.process_visible = ('process_visible' in request.POST)

            intern.benefits_visible = ('benefits_visible' in request.POST)

            intern.faqs_visible = ('faqs_visible' in request.POST)

            intern.openings_visible = ('openings_visible' in request.POST)

            intern.cta_visible = ('cta_visible' in request.POST)



            def clean_text_field(val, fallback=''):

                import re

                if not val:

                    return fallback

                clean = re.sub(r'<[^>]+>', '', str(val))

                clean = clean.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')

                return re.sub(r'\s+', ' ', clean).strip()



            def parse_bool_val(v, default=True):

                if v is None:

                    return default

                if isinstance(v, bool):

                    return v

                if isinstance(v, (int, float)):

                    return bool(v)

                s = str(v).strip().lower()

                if s in ('true', '1', 'yes', 'on'):

                    return True

                if s in ('false', '0', 'no', 'off'):

                    return False

                return default



            # 1. Hero

            intern.hero_eyebrow = clean_text_field(request.POST.get('hero_eyebrow'), intern.hero_eyebrow)

            intern.hero_title = clean_text_field(request.POST.get('hero_title'), intern.hero_title)

            intern.hero_subtitle = clean_text_field(request.POST.get('hero_subtitle'), intern.hero_subtitle)

            intern.hero_tagline = clean_text_field(request.POST.get('hero_tagline'), intern.hero_tagline)

            intern.hero_badge_text = clean_text_field(request.POST.get('hero_badge_text'), intern.hero_badge_text)

            intern.hero_primary_btn_text = clean_text_field(request.POST.get('hero_primary_btn_text'), intern.hero_primary_btn_text)

            intern.hero_primary_btn_url = clean_text_field(request.POST.get('hero_primary_btn_url'), intern.hero_primary_btn_url)

            intern.hero_secondary_btn_text = clean_text_field(request.POST.get('hero_secondary_btn_text'), intern.hero_secondary_btn_text)

            intern.hero_secondary_btn_url = clean_text_field(request.POST.get('hero_secondary_btn_url'), intern.hero_secondary_btn_url)

            if 'hero_image' in request.FILES:

                intern.hero_image = request.FILES['hero_image']



            # 2. Domains / Explore

            intern.domains_tag = clean_text_field(request.POST.get('domains_tag'), intern.domains_tag)

            intern.domains_title = clean_text_field(request.POST.get('domains_title'), intern.domains_title)

            intern.domains_subtitle = clean_text_field(request.POST.get('domains_subtitle'), intern.domains_subtitle)



            # 3. Programme Highlights

            intern.highlights_tag = clean_text_field(request.POST.get('highlights_tag'), intern.highlights_tag)



            # 4. Who Can Apply & What You'll Learn

            intern.who_can_apply_title = clean_text_field(request.POST.get('who_can_apply_title'), intern.who_can_apply_title)

            intern.what_you_learn_title = clean_text_field(request.POST.get('what_you_learn_title'), intern.what_you_learn_title)



            # 5. Process / Flight Path

            intern.process_tag = clean_text_field(request.POST.get('process_tag'), intern.process_tag)

            intern.process_title = clean_text_field(request.POST.get('process_title'), intern.process_title)



            # 6. Benefits

            intern.benefits_tag = clean_text_field(request.POST.get('benefits_tag'), intern.benefits_tag)

            intern.benefits_title = clean_text_field(request.POST.get('benefits_title'), intern.benefits_title)



            # 7. FAQs

            intern.faqs_tag = clean_text_field(request.POST.get('faqs_tag'), intern.faqs_tag)

            intern.faqs_title = clean_text_field(request.POST.get('faqs_title'), intern.faqs_title)



            # 8. Live Openings

            intern.openings_tag = clean_text_field(request.POST.get('openings_tag'), intern.openings_tag)

            intern.openings_title = clean_text_field(request.POST.get('openings_title'), intern.openings_title)

            intern.openings_subtitle = clean_text_field(request.POST.get('openings_subtitle'), intern.openings_subtitle)



            # 9. CTA & SEO

            intern.cta_title = clean_text_field(request.POST.get('cta_title'), intern.cta_title)

            intern.cta_subtitle = clean_text_field(request.POST.get('cta_subtitle'), intern.cta_subtitle)

            intern.cta_primary_btn_text = clean_text_field(request.POST.get('cta_primary_btn_text'), intern.cta_primary_btn_text)

            intern.cta_primary_btn_url = clean_text_field(request.POST.get('cta_primary_btn_url'), intern.cta_primary_btn_url)

            intern.cta_secondary_btn_text = clean_text_field(request.POST.get('cta_secondary_btn_text'), intern.cta_secondary_btn_text)

            intern.cta_secondary_btn_url = clean_text_field(request.POST.get('cta_secondary_btn_url'), intern.cta_secondary_btn_url)



            intern.meta_title = clean_text_field(request.POST.get('meta_title'), intern.meta_title)

            intern.meta_description = clean_text_field(request.POST.get('meta_description'), intern.meta_description)

            intern.meta_keywords = clean_text_field(request.POST.get('meta_keywords'), intern.meta_keywords)



            intern.save()



            # Repeater Sync 1: Strip Items

            strip_raw = request.POST.get('intern_strip_json')

            if strip_raw:

                try:

                    strip_list = json.loads(strip_raw)

                    seen_strip_ids = []

                    for idx, item in enumerate(strip_list, 1):

                        item_id = item.get('id')

                        strip_obj = InternshipStripItem.objects.filter(id=item_id).first() if item_id else InternshipStripItem()

                        t_val = clean_text_field(item.get('title'))

                        if not t_val:

                            continue

                        strip_obj.title = t_val

                        strip_obj.icon_class = clean_text_field(item.get('icon_class'), 'fa-solid fa-graduation-cap')

                        strip_obj.order = int(item.get('order', idx))

                        strip_obj.is_visible = parse_bool_val(item.get('is_visible'), True)

                        strip_obj.save()

                        seen_strip_ids.append(strip_obj.id)

                    InternshipStripItem.objects.exclude(id__in=seen_strip_ids).delete()

                except Exception:

                    pass



            # Repeater Sync 2: Tracks / Domains

            tracks_raw = request.POST.get('intern_tracks_json')

            if tracks_raw:

                try:

                    track_list = json.loads(tracks_raw)

                    seen_track_ids = []

                    for idx, item in enumerate(track_list, 1):

                        item_id = item.get('id')

                        track_obj = InternshipTrackItem.objects.filter(id=item_id).first() if item_id else InternshipTrackItem()

                        t_val = clean_text_field(item.get('title'))

                        if not t_val:

                            continue

                        track_obj.title = t_val

                        track_obj.description = clean_text_field(item.get('description'), '')

                        track_obj.icon_class = clean_text_field(item.get('icon_class'), 'fa-solid fa-briefcase')

                        track_obj.badge_number = clean_text_field(item.get('badge_number'), str(idx))

                        track_obj.card_style = clean_text_field(item.get('card_style'), f"d{((idx-1)%7)+1}")

                        track_obj.order = int(item.get('order', idx))

                        track_obj.is_visible = parse_bool_val(item.get('is_visible'), True)

                        track_obj.save()

                        seen_track_ids.append(track_obj.id)

                    InternshipTrackItem.objects.exclude(id__in=seen_track_ids).delete()

                except Exception:

                    pass



            # Repeater Sync 3: Programme Highlights

            hl_raw = request.POST.get('intern_highlights_json')

            if hl_raw:

                try:

                    hl_list = json.loads(hl_raw)

                    seen_hl_ids = []

                    for idx, item in enumerate(hl_list, 1):

                        item_id = item.get('id')

                        hl_obj = InternshipHighlightItem.objects.filter(id=item_id).first() if item_id else InternshipHighlightItem()

                        t_val = clean_text_field(item.get('title') or item.get('text'))

                        if not t_val:

                            continue

                        hl_obj.title = t_val

                        hl_obj.icon_class = clean_text_field(item.get('icon_class'), 'fa-solid fa-circle-check')

                        hl_obj.order = int(item.get('order', idx))

                        hl_obj.is_visible = parse_bool_val(item.get('is_visible'), True)

                        hl_obj.save()

                        seen_hl_ids.append(hl_obj.id)

                    InternshipHighlightItem.objects.exclude(id__in=seen_hl_ids).delete()

                except Exception:

                    pass



            # Repeater Sync 4: Who Can Apply

            who_raw = request.POST.get('intern_who_json')

            if who_raw:

                try:

                    who_list = json.loads(who_raw)

                    seen_who_ids = []

                    for idx, item in enumerate(who_list, 1):

                        item_id = item.get('id')

                        who_obj = InternshipWhoCanApplyItem.objects.filter(id=item_id).first() if item_id else InternshipWhoCanApplyItem()

                        t_val = clean_text_field(item.get('title'))

                        if not t_val:

                            continue

                        who_obj.title = t_val

                        who_obj.icon_class = clean_text_field(item.get('icon_class'), 'fa-solid fa-circle-check')

                        who_obj.order = int(item.get('order', idx))

                        who_obj.is_visible = parse_bool_val(item.get('is_visible'), True)

                        who_obj.save()

                        seen_who_ids.append(who_obj.id)

                    InternshipWhoCanApplyItem.objects.exclude(id__in=seen_who_ids).delete()

                except Exception:

                    pass



            # Repeater Sync 5: What You'll Learn

            learn_raw = request.POST.get('intern_learn_json')

            if learn_raw:

                try:

                    learn_list = json.loads(learn_raw)

                    seen_learn_ids = []

                    for idx, item in enumerate(learn_list, 1):

                        item_id = item.get('id')

                        learn_obj = InternshipWhatYouLearnItem.objects.filter(id=item_id).first() if item_id else InternshipWhatYouLearnItem()

                        t_val = clean_text_field(item.get('title'))

                        if not t_val:

                            continue

                        learn_obj.title = t_val

                        learn_obj.icon_class = clean_text_field(item.get('icon_class'), 'fa-solid fa-circle-check')

                        learn_obj.order = int(item.get('order', idx))

                        learn_obj.is_visible = parse_bool_val(item.get('is_visible'), True)

                        learn_obj.save()

                        seen_learn_ids.append(learn_obj.id)

                    InternshipWhatYouLearnItem.objects.exclude(id__in=seen_learn_ids).delete()

                except Exception:

                    pass



            # Repeater Sync 6: Process Steps

            proc_raw = request.POST.get('intern_process_json')

            if proc_raw:

                try:

                    proc_list = json.loads(proc_raw)

                    seen_proc_ids = []

                    for idx, item in enumerate(proc_list, 1):

                        item_id = item.get('id')

                        proc_obj = InternshipProcessStep.objects.filter(id=item_id).first() if item_id else InternshipProcessStep()

                        t_val = clean_text_field(item.get('title'))

                        if not t_val:

                            continue

                        proc_obj.step_number = clean_text_field(item.get('step_number'), f"{idx:02d}")

                        proc_obj.title = t_val

                        proc_obj.description = clean_text_field(item.get('description'), '')

                        proc_obj.icon_class = clean_text_field(item.get('icon_class'), 'fa-solid fa-file-signature')

                        proc_obj.is_final = parse_bool_val(item.get('is_final'), False)

                        proc_obj.order = int(item.get('order', idx))

                        proc_obj.is_visible = parse_bool_val(item.get('is_visible'), True)

                        proc_obj.save()

                        seen_proc_ids.append(proc_obj.id)

                    InternshipProcessStep.objects.exclude(id__in=seen_proc_ids).delete()

                except Exception:

                    pass



            # Repeater Sync 7: Benefits

            ben_raw = request.POST.get('intern_benefits_json')

            if ben_raw:

                try:

                    ben_list = json.loads(ben_raw)

                    seen_ben_ids = []

                    for idx, item in enumerate(ben_list, 1):

                        item_id = item.get('id')

                        ben_obj = InternshipBenefitItem.objects.filter(id=item_id).first() if item_id else InternshipBenefitItem()

                        t_val = clean_text_field(item.get('title'))

                        if not t_val:

                            continue

                        ben_obj.title = t_val

                        ben_obj.icon_class = clean_text_field(item.get('icon_class'), 'fa-solid fa-chart-line')

                        ben_obj.order = int(item.get('order', idx))

                        ben_obj.is_visible = parse_bool_val(item.get('is_visible'), True)

                        ben_obj.save()

                        seen_ben_ids.append(ben_obj.id)

                    InternshipBenefitItem.objects.exclude(id__in=seen_ben_ids).delete()

                except Exception:

                    pass



            # Repeater Sync 8: FAQs

            faq_raw = request.POST.get('intern_faqs_json')

            if faq_raw:

                try:

                    faq_list = json.loads(faq_raw)

                    seen_faq_ids = []

                    for idx, item in enumerate(faq_list, 1):

                        item_id = item.get('id')

                        faq_obj = InternshipFaqItem.objects.filter(id=item_id).first() if item_id else InternshipFaqItem()

                        q_val = clean_text_field(item.get('question'))

                        if not q_val:

                            continue

                        faq_obj.question = q_val

                        faq_obj.answer = clean_text_field(item.get('answer'), '')

                        faq_obj.order = int(item.get('order', idx))

                        faq_obj.is_visible = parse_bool_val(item.get('is_visible'), True)

                        faq_obj.save()

                        seen_faq_ids.append(faq_obj.id)

                    InternshipFaqItem.objects.exclude(id__in=seen_faq_ids).delete()

                except Exception:

                    pass



            # Repeater Sync 9: Available Internship Openings / Position Cards

            openings_raw = request.POST.get('intern_openings_json')

            if openings_raw:

                try:

                    from apps.internships.models import Internship

                    openings_list = json.loads(openings_raw)

                    seen_op_ids = []

                    for item in openings_list:

                        item_id = item.get('id')

                        op_obj = Internship.objects.filter(id=item_id).first() if item_id else Internship()

                        t_val = clean_text_field(item.get('title'))

                        if not t_val:

                            continue

                        op_obj.title = t_val

                        op_obj.mode = clean_text_field(item.get('mode'), 'Onsite')

                        op_obj.duration = clean_text_field(item.get('duration'), '3 Months')

                        try:

                            op_obj.seats = int(item.get('seats', 1))

                        except Exception:

                            op_obj.seats = 1

                        op_obj.location = clean_text_field(item.get('location'), '')

                        op_obj.stipend = clean_text_field(item.get('stipend'), '')

                        op_obj.skills_required = clean_text_field(item.get('skills_required') or item.get('skills'), '')

                        op_obj.description = clean_text_field(item.get('description'), '')

                        is_vis = parse_bool_val(item.get('is_visible'), True)

                        raw_st = clean_text_field(item.get('status'), 'Open')

                        op_obj.status = 'Open' if is_vis else ('Closed' if raw_st == 'Open' else raw_st)

                        op_obj.save()

                        seen_op_ids.append(op_obj.id)

                    Internship.objects.exclude(id__in=seen_op_ids).delete()

                except Exception:

                    pass



            cache.delete(INTERNSHIP_CACHE_KEY)

            cache.delete('public_site_context')



            try:

                log_activity(

                    admin_user,

                    'Website Content Updated',

                    'Updated Internship Programme Configuration and published live.'

                )

            except Exception:

                pass



            messages.success(request, "Internship Programme content & sections saved successfully live!")

            return True



    except Exception as e:

        messages.error(request, f"Error updating Internship Programme content: {str(e)}")

        return False





@require_http_methods(["POST"])







def api_admin_toggle_repeater_visible(request):







    """







    Instant AJAX endpoint to toggle visibility for repeater items across dynamic service pages:







    Supports: ec_process, ec_service, ec_why, cs_process, cs_industry, cs_why,







              cs_emp_benefit, cs_cand_benefit, cs_faq







    """







    admin_id = request.session.get('admin_id')







    if not admin_id and not (request.user and request.user.is_authenticated and request.user.is_staff):







        return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)















    data = {}
    if request.content_type and 'application/json' in request.content_type:
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = {}
    else:
        data = request.POST
        if not data:
            try:
                data = json.loads(request.body.decode('utf-8'))
            except Exception:
                data = {}















    item_type = str(data.get('item_type') or '').strip().lower()







    item_id = data.get('item_id')







    raw_visible = data.get('is_visible')















    if not item_type or item_id is None:







        return JsonResponse({'status': 'error', 'message': 'item_type and item_id are required.'}, status=400)















    try:







        item_id = int(item_id)







    except (ValueError, TypeError):







        return JsonResponse({'status': 'error', 'message': 'Invalid item_id.'}, status=400)















    if isinstance(raw_visible, bool):







        is_visible = raw_visible







    elif isinstance(raw_visible, (int, float)):







        is_visible = bool(raw_visible)







    else:







        is_visible = str(raw_visible).strip().lower() in ('true', '1', 'yes', 'on')















    from apps.core.models import (







        EcServiceCard, EcWhyChooseItem, EcProcessStep,







        CsServiceCard, CsProcessStep, CsWhyChooseItem, CsIndustryItem,







        CsBenefitEmployerItem, CsBenefitCandidateItem, CsFaqItem,







        EDUCATIONAL_CONSULTANCY_CACHE_KEY, CONTRACT_STAFFING_CACHE_KEY







    )







    from django.core.cache import cache















    updated = False







    if item_type in ('ec_process', 'ec_process_step'):







        updated = bool(EcProcessStep.objects.filter(id=item_id).update(is_visible=is_visible))







        cache.delete(EDUCATIONAL_CONSULTANCY_CACHE_KEY)







    elif item_type in ('ec_service', 'ec_service_card'):







        updated = bool(EcServiceCard.objects.filter(id=item_id).update(is_visible=is_visible))







        cache.delete(EDUCATIONAL_CONSULTANCY_CACHE_KEY)







    elif item_type in ('ec_why', 'ec_why_choose'):







        updated = bool(EcWhyChooseItem.objects.filter(id=item_id).update(is_visible=is_visible))







        cache.delete(EDUCATIONAL_CONSULTANCY_CACHE_KEY)







    elif item_type in ('cs_service', 'cs_service_card'):







        updated = bool(CsServiceCard.objects.filter(id=item_id).update(is_visible=is_visible))







        cache.delete(CONTRACT_STAFFING_CACHE_KEY)







    elif item_type in ('cs_process', 'cs_process_step'):







        updated = bool(CsProcessStep.objects.filter(id=item_id).update(is_visible=is_visible))







        cache.delete(CONTRACT_STAFFING_CACHE_KEY)







    elif item_type in ('cs_industry', 'cs_industry_item'):







        updated = bool(CsIndustryItem.objects.filter(id=item_id).update(is_visible=is_visible))







        cache.delete(CONTRACT_STAFFING_CACHE_KEY)







    elif item_type in ('cs_why', 'cs_why_choose'):







        updated = bool(CsWhyChooseItem.objects.filter(id=item_id).update(is_visible=is_visible))







        cache.delete(CONTRACT_STAFFING_CACHE_KEY)







    elif item_type in ('cs_emp_benefit', 'cs_employer_benefit'):







        updated = bool(CsBenefitEmployerItem.objects.filter(id=item_id).update(is_visible=is_visible))







        cache.delete(CONTRACT_STAFFING_CACHE_KEY)







    elif item_type in ('cs_cand_benefit', 'cs_candidate_benefit'):







        updated = bool(CsBenefitCandidateItem.objects.filter(id=item_id).update(is_visible=is_visible))







        cache.delete(CONTRACT_STAFFING_CACHE_KEY)







    elif item_type in ('cs_faq', 'cs_faq_item'):







        updated = bool(CsFaqItem.objects.filter(id=item_id).update(is_visible=is_visible))







        cache.delete(CONTRACT_STAFFING_CACHE_KEY)







    elif item_type in ('po_service', 'po_service_card'):







        from apps.core.models import PoServiceCard, PAYROLL_OUTSOURCING_CACHE_KEY







        updated = bool(PoServiceCard.objects.filter(id=item_id).update(is_visible=is_visible))







        cache.delete(PAYROLL_OUTSOURCING_CACHE_KEY)







    elif item_type in ('po_industry', 'po_industry_item'):







        from apps.core.models import PoIndustryItem, PAYROLL_OUTSOURCING_CACHE_KEY







        updated = bool(PoIndustryItem.objects.filter(id=item_id).update(is_visible=is_visible))







        cache.delete(PAYROLL_OUTSOURCING_CACHE_KEY)







    elif item_type in ('po_why', 'po_why_choose'):







        from apps.core.models import PoWhyChooseItem, PAYROLL_OUTSOURCING_CACHE_KEY







        updated = bool(PoWhyChooseItem.objects.filter(id=item_id).update(is_visible=is_visible))







        cache.delete(PAYROLL_OUTSOURCING_CACHE_KEY)







    elif item_type in ('po_process', 'po_process_step'):







        from apps.core.models import PoProcessStep, PAYROLL_OUTSOURCING_CACHE_KEY







        updated = bool(PoProcessStep.objects.filter(id=item_id).update(is_visible=is_visible))







        cache.delete(PAYROLL_OUTSOURCING_CACHE_KEY)







    elif item_type in ('po_emp_benefit', 'po_employer_benefit'):







        from apps.core.models import PoEmployerBenefit, PAYROLL_OUTSOURCING_CACHE_KEY







        updated = bool(PoEmployerBenefit.objects.filter(id=item_id).update(is_visible=is_visible))







        cache.delete(PAYROLL_OUTSOURCING_CACHE_KEY)







    elif item_type in ('po_employee_benefit', 'po_ee_benefit'):







        from apps.core.models import PoEmployeeBenefit, PAYROLL_OUTSOURCING_CACHE_KEY







        updated = bool(PoEmployeeBenefit.objects.filter(id=item_id).update(is_visible=is_visible))







        cache.delete(PAYROLL_OUTSOURCING_CACHE_KEY)







    elif item_type in ('po_faq', 'po_faq_item'):







        from apps.core.models import PoFaqItem, PAYROLL_OUTSOURCING_CACHE_KEY







        updated = bool(PoFaqItem.objects.filter(id=item_id).update(is_visible=is_visible))







        cache.delete(PAYROLL_OUTSOURCING_CACHE_KEY)







    elif item_type in ('hr_feature', 'hr_feature_item', 'hr_features'):

        from apps.core.models import HrFeatureItem, HR_SUPPORT_CACHE_KEY

        updated = bool(HrFeatureItem.objects.filter(id=item_id).update(is_visible=is_visible))

        cache.delete(HR_SUPPORT_CACHE_KEY)

    elif item_type in ('hr_service', 'hr_service_card', 'hr_services'):

        from apps.core.models import HrServiceCard, HR_SUPPORT_CACHE_KEY

        updated = bool(HrServiceCard.objects.filter(id=item_id).update(is_visible=is_visible))

        cache.delete(HR_SUPPORT_CACHE_KEY)

    elif item_type in ('hr_additional', 'hr_additional_service', 'hr_additionals'):

        from apps.core.models import HrAdditionalServiceItem, HR_SUPPORT_CACHE_KEY

        updated = bool(HrAdditionalServiceItem.objects.filter(id=item_id).update(is_visible=is_visible))

        cache.delete(HR_SUPPORT_CACHE_KEY)

    elif item_type in ('hr_why_choose', 'hr_why_choose_item', 'hr_why'):

        from apps.core.models import HrWhyChooseItem, HR_SUPPORT_CACHE_KEY

        updated = bool(HrWhyChooseItem.objects.filter(id=item_id).update(is_visible=is_visible))

        cache.delete(HR_SUPPORT_CACHE_KEY)

    elif item_type in ('hr_process', 'hr_process_step', 'hr_processes'):

        from apps.core.models import HrProcessStep, HR_SUPPORT_CACHE_KEY

        updated = bool(HrProcessStep.objects.filter(id=item_id).update(is_visible=is_visible))

        cache.delete(HR_SUPPORT_CACHE_KEY)

    elif item_type in ('hr_employer_benefit', 'hr_emp_benefit', 'hr_employer_benefits'):

        from apps.core.models import HrEmployerBenefit, HR_SUPPORT_CACHE_KEY

        updated = bool(HrEmployerBenefit.objects.filter(id=item_id).update(is_visible=is_visible))

        cache.delete(HR_SUPPORT_CACHE_KEY)

    elif item_type in ('hr_employee_benefit', 'hr_ee_benefit', 'hr_employee_benefits'):

        from apps.core.models import HrEmployeeBenefit, HR_SUPPORT_CACHE_KEY

        updated = bool(HrEmployeeBenefit.objects.filter(id=item_id).update(is_visible=is_visible))

        cache.delete(HR_SUPPORT_CACHE_KEY)

    elif item_type in ('intern_strip', 'intern_strip_item'):

        from apps.core.models import InternshipStripItem, INTERNSHIP_CACHE_KEY

        updated = bool(InternshipStripItem.objects.filter(id=item_id).update(is_visible=is_visible))

        cache.delete(INTERNSHIP_CACHE_KEY)

    elif item_type in ('intern_track', 'intern_track_item', 'intern_domain', 'intern_domains'):

        from apps.core.models import InternshipTrackItem, INTERNSHIP_CACHE_KEY

        updated = bool(InternshipTrackItem.objects.filter(id=item_id).update(is_visible=is_visible))

        cache.delete(INTERNSHIP_CACHE_KEY)

    elif item_type in ('intern_highlight', 'intern_highlight_item'):

        from apps.core.models import InternshipHighlightItem, INTERNSHIP_CACHE_KEY

        updated = bool(InternshipHighlightItem.objects.filter(id=item_id).update(is_visible=is_visible))

        cache.delete(INTERNSHIP_CACHE_KEY)

    elif item_type in ('intern_who', 'intern_who_can_apply', 'intern_who_item'):

        from apps.core.models import InternshipWhoCanApplyItem, INTERNSHIP_CACHE_KEY

        updated = bool(InternshipWhoCanApplyItem.objects.filter(id=item_id).update(is_visible=is_visible))

        cache.delete(INTERNSHIP_CACHE_KEY)

    elif item_type in ('intern_learn', 'intern_what_you_learn', 'intern_learn_item'):

        from apps.core.models import InternshipWhatYouLearnItem, INTERNSHIP_CACHE_KEY

        updated = bool(InternshipWhatYouLearnItem.objects.filter(id=item_id).update(is_visible=is_visible))

        cache.delete(INTERNSHIP_CACHE_KEY)

    elif item_type in ('intern_process', 'intern_process_step'):

        from apps.core.models import InternshipProcessStep, INTERNSHIP_CACHE_KEY

        updated = bool(InternshipProcessStep.objects.filter(id=item_id).update(is_visible=is_visible))

        cache.delete(INTERNSHIP_CACHE_KEY)

    elif item_type in ('intern_benefit', 'intern_benefit_item'):

        from apps.core.models import InternshipBenefitItem, INTERNSHIP_CACHE_KEY

        updated = bool(InternshipBenefitItem.objects.filter(id=item_id).update(is_visible=is_visible))

        cache.delete(INTERNSHIP_CACHE_KEY)

    elif item_type in ('intern_faq', 'intern_faq_item'):

        from apps.core.models import InternshipFaqItem, INTERNSHIP_CACHE_KEY

        updated = bool(InternshipFaqItem.objects.filter(id=item_id).update(is_visible=is_visible))

        cache.delete(INTERNSHIP_CACHE_KEY)

    elif item_type in ('intern_opening', 'intern_position', 'internship_opening'):

        from apps.internships.models import Internship

        from apps.core.models import INTERNSHIP_CACHE_KEY

        op = Internship.objects.filter(id=item_id).first()

        if op:

            op.status = 'Open' if is_visible else 'Closed'

            op.save()

            updated = True

            cache.delete(INTERNSHIP_CACHE_KEY)







    else:







        return JsonResponse({'status': 'error', 'message': f'Unknown item_type: {item_type}'}, status=400)















    cache.delete('public_site_context')















    if not updated:







        return JsonResponse({'status': 'error', 'message': f'Item with id {item_id} not found.'}, status=404)















    return JsonResponse({







        'status': 'success',







        'success': True,







        'item_type': item_type,







        'item_id': item_id,







        'is_visible': is_visible,







        'message': f"Item visibility updated to {'Visible' if is_visible else 'Hidden'} live!"







    })











def handle_job_page_save(request, admin_user):
    from apps.core.models import JobPageSettings
    from django.contrib import messages
    import json
    import re

    settings = JobPageSettings.get_settings()

    # 0. Master Visibility Toggles
    if 'save_visibility' in request.POST or 'hero_visible' in request.POST or 'hero_title' in request.POST:
        settings.hero_visible = request.POST.get('hero_visible') in ('on', '1', 'true')
        settings.search_visible = request.POST.get('search_visible') in ('on', '1', 'true')
        settings.job_types_visible = request.POST.get('job_types_visible') in ('on', '1', 'true')
        settings.categories_visible = request.POST.get('categories_visible') in ('on', '1', 'true')
        settings.latest_jobs_visible = request.POST.get('latest_jobs_visible') in ('on', '1', 'true')
        settings.industries_visible = request.POST.get('industries_visible') in ('on', '1', 'true')
        settings.locations_visible = request.POST.get('locations_visible') in ('on', '1', 'true')
        settings.why_choose_visible = request.POST.get('why_choose_visible') in ('on', '1', 'true')
        settings.commit_visible = request.POST.get('commit_visible') in ('on', '1', 'true')
        settings.cta_visible = request.POST.get('cta_visible') in ('on', '1', 'true')

    # 1. Hero & Stats & Action Buttons
    if 'hero_title' in request.POST:
        settings.hero_chip = request.POST.get('hero_chip', '').strip()
        raw_title = request.POST.get('hero_title', '').strip()
        settings.hero_title = re.sub(r'<[^>]+>', '', raw_title).strip()
        settings.hero_title_highlight = request.POST.get('hero_title_highlight', 'Dream').strip()
        settings.hero_subtitle = request.POST.get('hero_subtitle', '').strip()

        settings.feature_1_title = request.POST.get('feature_1_title', '').strip()
        settings.feature_1_desc = request.POST.get('feature_1_desc', '').strip()
        settings.feature_2_title = request.POST.get('feature_2_title', '').strip()
        settings.feature_2_desc = request.POST.get('feature_2_desc', '').strip()
        settings.feature_3_title = request.POST.get('feature_3_title', '').strip()
        settings.feature_3_desc = request.POST.get('feature_3_desc', '').strip()

        settings.stat_1_num = request.POST.get('stat_1_num', '').strip()
        settings.stat_1_label = request.POST.get('stat_1_label', '').strip()
        settings.stat_2_num = request.POST.get('stat_2_num', '').strip()
        settings.stat_2_label = request.POST.get('stat_2_label', '').strip()
        settings.stat_3_num = request.POST.get('stat_3_num', '').strip()
        settings.stat_3_label = request.POST.get('stat_3_label', '').strip()
        settings.stat_4_num = request.POST.get('stat_4_num', '').strip()
        settings.stat_4_label = request.POST.get('stat_4_label', '').strip()

        settings.hero_btn1_text = request.POST.get('hero_btn1_text', '').strip()
        settings.hero_btn1_url = request.POST.get('hero_btn1_url', '').strip()
        settings.hero_btn2_text = request.POST.get('hero_btn2_text', '').strip()
        settings.hero_btn2_url = request.POST.get('hero_btn2_url', '').strip()
        settings.hero_btn3_text = request.POST.get('hero_btn3_text', '').strip()
        settings.hero_btn3_url = request.POST.get('hero_btn3_url', '').strip()

        settings.search_keyword_placeholder = request.POST.get('search_keyword_placeholder', '').strip()
        settings.search_location_placeholder = request.POST.get('search_location_placeholder', '').strip()
        settings.search_btn_text = request.POST.get('search_btn_text', '').strip()

    if 'hero_image' in request.FILES:
        settings.hero_image = request.FILES['hero_image']

    # 2. Section Headings & View All Buttons
    if 'types_title' in request.POST:
        settings.types_title = request.POST.get('types_title', '').strip()
        settings.types_view_all_text = request.POST.get('types_view_all_text', '').strip()
        settings.types_view_all_url = request.POST.get('types_view_all_url', '').strip()
    if 'categories_title' in request.POST:
        settings.categories_title = request.POST.get('categories_title', '').strip()
        settings.categories_view_all_text = request.POST.get('categories_view_all_text', '').strip()
        settings.categories_view_all_url = request.POST.get('categories_view_all_url', '').strip()
    if 'latest_title' in request.POST:
        settings.latest_eyebrow = request.POST.get('latest_eyebrow', '').strip()
        settings.latest_title = request.POST.get('latest_title', '').strip()
        settings.latest_subtitle = request.POST.get('latest_subtitle', '').strip()
        settings.latest_view_all_text = request.POST.get('latest_view_all_text', '').strip()

    # 3. Triple Panel Headings & JSON Repeaters
    if 'industries_title' in request.POST:
        settings.industries_title = request.POST.get('industries_title', '').strip()
        settings.industries_view_all_text = request.POST.get('industries_view_all_text', '').strip()
        settings.industries_view_all_url = request.POST.get('industries_view_all_url', '').strip()
    if 'popular_industries_json' in request.POST:
        val = request.POST.get('popular_industries_json', '').strip()
        if val:
            try:
                json.loads(val)
                settings.popular_industries_json = val
            except Exception:
                pass

    if 'locations_title' in request.POST:
        settings.locations_title = request.POST.get('locations_title', '').strip()
        settings.locations_view_all_text = request.POST.get('locations_view_all_text', '').strip()
        settings.locations_view_all_url = request.POST.get('locations_view_all_url', '').strip()
    if 'jobs_by_location_json' in request.POST:
        val = request.POST.get('jobs_by_location_json', '').strip()
        if val:
            try:
                json.loads(val)
                settings.jobs_by_location_json = val
            except Exception:
                pass

    if 'why_choose_title' in request.POST:
        settings.why_choose_title = request.POST.get('why_choose_title', '').strip()
    if 'why_choose_json' in request.POST:
        val = request.POST.get('why_choose_json', '').strip()
        if val:
            try:
                json.loads(val)
                settings.why_choose_json = val
            except Exception:
                pass

    # 4. Commitment Banner & CTA
    if 'commit_title' in request.POST:
        settings.commit_title = request.POST.get('commit_title', '').strip()
    if 'commit_stats_json' in request.POST:
        val = request.POST.get('commit_stats_json', '').strip()
        if val:
            try:
                json.loads(val)
                settings.commit_stats_json = val
            except Exception:
                pass
    if 'commit_image' in request.FILES:
        settings.commit_image = request.FILES['commit_image']

    if 'cta_title' in request.POST:
        settings.cta_title = request.POST.get('cta_title', '').strip()
        settings.cta_subtitle = request.POST.get('cta_subtitle', '').strip()
        settings.cta_btn_text = request.POST.get('cta_btn_text', '').strip()
        settings.cta_btn_url = request.POST.get('cta_btn_url', '').strip()
    if 'cta_steps_json' in request.POST:
        val = request.POST.get('cta_steps_json', '').strip()
        if val:
            try:
                json.loads(val)
                settings.cta_steps_json = val
            except Exception:
                pass
    if 'cta_image' in request.FILES:
        settings.cta_image = request.FILES['cta_image']

    # 5. SEO & Meta
    if 'meta_title' in request.POST:
        settings.meta_title = request.POST.get('meta_title', '').strip()
        settings.meta_description = request.POST.get('meta_description', '').strip()
        settings.meta_keywords = request.POST.get('meta_keywords', '').strip()

    settings.save()
    messages.success(request, "Job page configuration updated successfully!")
    return True


def handle_careers_page_save(request, admin_user):
    from apps.core.models import CareerPageSettings
    from django.contrib import messages
    import json
    import re

    settings = CareerPageSettings.get_settings()

    # 0. Master Visibility Toggles
    if 'save_visibility' in request.POST or 'hero_visible' in request.POST or 'hero_title' in request.POST:
        settings.hero_visible = request.POST.get('hero_visible') in ('on', '1', 'true')
        settings.openings_visible = request.POST.get('openings_visible') in ('on', '1', 'true')
        settings.resume_cta_visible = request.POST.get('resume_cta_visible') in ('on', '1', 'true')
        settings.why_build_visible = request.POST.get('why_build_visible') in ('on', '1', 'true')
        settings.career_areas_visible = request.POST.get('career_areas_visible') in ('on', '1', 'true')
        settings.journey_visible = request.POST.get('journey_visible') in ('on', '1', 'true')
        settings.look_for_visible = request.POST.get('look_for_visible') in ('on', '1', 'true')
        settings.benefits_visible = request.POST.get('benefits_visible') in ('on', '1', 'true')
        settings.cta_visible = request.POST.get('cta_visible') in ('on', '1', 'true')

    # 1. Hero & Features
    if 'hero_title' in request.POST:
        settings.hero_eyebrow = request.POST.get('hero_eyebrow', '').strip()
        raw_title = request.POST.get('hero_title', '').strip()
        settings.hero_title = re.sub(r'<[^>]+>', '', raw_title).strip()
        settings.hero_title_highlight = request.POST.get('hero_title_highlight', '').strip()
        settings.hero_subtitle = request.POST.get('hero_subtitle', '').strip()

        settings.hero_btn1_text = request.POST.get('hero_btn1_text', '').strip()
        settings.hero_btn1_url = request.POST.get('hero_btn1_url', '').strip()
        settings.hero_btn2_text = request.POST.get('hero_btn2_text', '').strip()
        settings.hero_btn2_url = request.POST.get('hero_btn2_url', '').strip()
        settings.hero_rating_badge = request.POST.get('hero_rating_badge', '').strip()
        settings.hero_placed_badge = request.POST.get('hero_placed_badge', '').strip()

        settings.feature_1_icon = request.POST.get('feature_1_icon', '').strip()
        settings.feature_1_title = request.POST.get('feature_1_title', '').strip()
        settings.feature_1_desc = request.POST.get('feature_1_desc', '').strip()

        settings.feature_2_icon = request.POST.get('feature_2_icon', '').strip()
        settings.feature_2_title = request.POST.get('feature_2_title', '').strip()
        settings.feature_2_desc = request.POST.get('feature_2_desc', '').strip()

        settings.feature_3_icon = request.POST.get('feature_3_icon', '').strip()
        settings.feature_3_title = request.POST.get('feature_3_title', '').strip()
        settings.feature_3_desc = request.POST.get('feature_3_desc', '').strip()

        settings.feature_4_icon = request.POST.get('feature_4_icon', '').strip()
        settings.feature_4_title = request.POST.get('feature_4_title', '').strip()
        settings.feature_4_desc = request.POST.get('feature_4_desc', '').strip()

    if 'hero_image' in request.FILES:
        settings.hero_image = request.FILES['hero_image']

    # 2. Current Openings Jobs Section
    if 'openings_title' in request.POST:
        settings.openings_eyebrow = request.POST.get('openings_eyebrow', '').strip()
        settings.openings_title = request.POST.get('openings_title', '').strip()
        settings.openings_subtitle = request.POST.get('openings_subtitle', '').strip()
        settings.openings_desc = request.POST.get('openings_desc', '').strip()

    if 'openings_json' in request.POST:
        val = request.POST.get('openings_json', '').strip()
        if val:
            try:
                json.loads(val)
                settings.openings_json = val
            except Exception:
                pass

    # 3. Didn't Find the Right Job? (Resume CTA)
    if 'resume_cta_title' in request.POST:
        settings.resume_cta_icon = request.POST.get('resume_cta_icon', '').strip()
        settings.resume_cta_title = request.POST.get('resume_cta_title', '').strip()
        settings.resume_cta_desc = request.POST.get('resume_cta_desc', '').strip()
        settings.resume_btn_text = request.POST.get('resume_btn_text', '').strip()
        settings.resume_contact_btn_text = request.POST.get('resume_contact_btn_text', '').strip()
        settings.resume_contact_btn_url = request.POST.get('resume_contact_btn_url', '').strip()

    # 4. Why Build Here
    if 'why_build_title' in request.POST:
        settings.why_build_tag = request.POST.get('why_build_tag', '').strip()
        settings.why_build_title = request.POST.get('why_build_title', '').strip()
    if 'why_build_json' in request.POST:
        val = request.POST.get('why_build_json', '').strip()
        if val:
            try:
                json.loads(val)
                settings.why_build_json = val
            except Exception:
                pass

    # 5. Career Areas
    if 'career_areas_title' in request.POST:
        settings.career_areas_tag = request.POST.get('career_areas_tag', '').strip()
        settings.career_areas_title = request.POST.get('career_areas_title', '').strip()
    if 'career_areas_json' in request.POST:
        val = request.POST.get('career_areas_json', '').strip()
        if val:
            try:
                json.loads(val)
                settings.career_areas_json = val
            except Exception:
                pass

    # 6. Your Career Journey
    if 'journey_title' in request.POST:
        settings.journey_tag = request.POST.get('journey_tag', '').strip()
        settings.journey_title = request.POST.get('journey_title', '').strip()
    if 'journey_steps_json' in request.POST:
        val = request.POST.get('journey_steps_json', '').strip()
        if val:
            try:
                json.loads(val)
                settings.journey_steps_json = val
            except Exception:
                pass

    # 7. What We Look For
    if 'look_for_tag' in request.POST:
        settings.look_for_tag = request.POST.get('look_for_tag', '').strip()
    if 'look_for_json' in request.POST:
        val = request.POST.get('look_for_json', '').strip()
        if val:
            try:
                json.loads(val)
                settings.look_for_json = val
            except Exception:
                pass

    # 8. Employee Benefits
    if 'benefits_tag' in request.POST:
        settings.benefits_tag = request.POST.get('benefits_tag', '').strip()
    if 'benefits_json' in request.POST:
        val = request.POST.get('benefits_json', '').strip()
        if val:
            try:
                json.loads(val)
                settings.benefits_json = val
            except Exception:
                pass

    # 9. Bottom CTA Banner
    if 'cta_title' in request.POST:
        settings.cta_title = request.POST.get('cta_title', '').strip()
        settings.cta_subtitle = request.POST.get('cta_subtitle', '').strip()
        settings.cta_icon = request.POST.get('cta_icon', '').strip()
        settings.cta_btn1_text = request.POST.get('cta_btn1_text', '').strip()
        settings.cta_btn1_url = request.POST.get('cta_btn1_url', '').strip()
        settings.cta_btn2_text = request.POST.get('cta_btn2_text', '').strip()
        settings.cta_btn2_url = request.POST.get('cta_btn2_url', '').strip()

    # 10. SEO & Meta
    if 'meta_title' in request.POST:
        settings.meta_title = request.POST.get('meta_title', '').strip()
        settings.meta_description = request.POST.get('meta_description', '').strip()
        settings.meta_keywords = request.POST.get('meta_keywords', '').strip()

    settings.save()
    messages.success(request, "Careers page configuration updated successfully!")
    return True


def handle_blog_page_save(request, admin_user):
    from apps.core.models import BlogPageSettings
    from django.contrib import messages
    import json
    import re

    settings = BlogPageSettings.get_settings()

    # 0. Master Visibility Toggles
    if 'save_visibility' in request.POST or 'hero_visible' in request.POST or 'hero_title' in request.POST:
        settings.hero_visible = request.POST.get('hero_visible') in ('on', '1', 'true')
        settings.featured_article_visible = request.POST.get('featured_article_visible') in ('on', '1', 'true')
        settings.categories_visible = request.POST.get('categories_visible') in ('on', '1', 'true')
        settings.latest_posts_visible = request.POST.get('latest_posts_visible') in ('on', '1', 'true')
        settings.newsletter_visible = request.POST.get('newsletter_visible') in ('on', '1', 'true')
        settings.recent_posts_visible = request.POST.get('recent_posts_visible') in ('on', '1', 'true')
        settings.dream_cta_visible = request.POST.get('dream_cta_visible') in ('on', '1', 'true')
        settings.stats_visible = request.POST.get('stats_visible') in ('on', '1', 'true')

    # 1. Hero & Badges
    if 'hero_title' in request.POST:
        settings.hero_chip = request.POST.get('hero_chip', '').strip()
        raw_title = request.POST.get('hero_title', '').strip()
        settings.hero_title = re.sub(r'<[^>]+>', '', raw_title).strip()
        settings.hero_title_highlight = request.POST.get('hero_title_highlight', 'Insights').strip()
        settings.hero_subtitle = request.POST.get('hero_subtitle', '').strip()

        settings.hero_btn1_text = request.POST.get('hero_btn1_text', '').strip()
        settings.hero_btn1_url = request.POST.get('hero_btn1_url', '').strip()
        settings.hero_btn2_text = request.POST.get('hero_btn2_text', '').strip()
        settings.hero_btn2_url = request.POST.get('hero_btn2_url', '').strip()

        settings.hero_badge_num = request.POST.get('hero_badge_num', '').strip()
        settings.hero_badge_label = request.POST.get('hero_badge_label', '').strip()
        settings.hero_badge_icon = request.POST.get('hero_badge_icon', '').strip()

    if 'hero_image' in request.FILES:
        settings.hero_image = request.FILES['hero_image']

    # 2. Featured Article
    if 'featured_title' in request.POST:
        settings.featured_section_title = request.POST.get('featured_section_title', '').strip()
        settings.featured_tag = request.POST.get('featured_tag', '').strip()
        settings.featured_title = request.POST.get('featured_title', '').strip()
        settings.featured_desc = request.POST.get('featured_desc', '').strip()
        settings.featured_date = request.POST.get('featured_date', '').strip()
        settings.featured_read_time = request.POST.get('featured_read_time', '').strip()
        settings.featured_link_url = request.POST.get('featured_link_url', '').strip()
        settings.featured_btn_text = request.POST.get('featured_btn_text', '').strip()

    if 'featured_image' in request.FILES:
        settings.featured_image = request.FILES['featured_image']

    # 3. Popular Categories (Sidebar)
    if 'categories_title' in request.POST:
        settings.categories_title = request.POST.get('categories_title', '').strip()
    if 'popular_categories_json' in request.POST:
        val = request.POST.get('popular_categories_json', '').strip()
        if val:
            try:
                json.loads(val)
                settings.popular_categories_json = val
            except Exception:
                pass

    # 4. Latest Blog Posts Grid
    if 'latest_posts_title' in request.POST:
        settings.latest_posts_title = request.POST.get('latest_posts_title', '').strip()
        settings.latest_view_more_text = request.POST.get('latest_view_more_text', '').strip()
        settings.latest_view_more_url = request.POST.get('latest_view_more_url', '').strip()
    if 'latest_posts_json' in request.POST:
        val = request.POST.get('latest_posts_json', '').strip()
        if val:
            try:
                json.loads(val)
                settings.latest_posts_json = val
            except Exception:
                pass

    # 5. Newsletter Box
    if 'newsletter_title' in request.POST:
        settings.newsletter_title = request.POST.get('newsletter_title', '').strip()
        settings.newsletter_desc = request.POST.get('newsletter_desc', '').strip()
        settings.newsletter_placeholder = request.POST.get('newsletter_placeholder', '').strip()
        settings.newsletter_btn_text = request.POST.get('newsletter_btn_text', '').strip()

    # 6. Recent Posts (Sidebar)
    if 'recent_posts_title' in request.POST:
        settings.recent_posts_title = request.POST.get('recent_posts_title', '').strip()
    if 'recent_posts_json' in request.POST:
        val = request.POST.get('recent_posts_json', '').strip()
        if val:
            try:
                json.loads(val)
                settings.recent_posts_json = val
            except Exception:
                pass

    # 7. Looking for Your Dream Job? (Dream CTA Banner)
    if 'dream_cta_title' in request.POST:
        settings.dream_cta_title = request.POST.get('dream_cta_title', '').strip()
        settings.dream_cta_desc = request.POST.get('dream_cta_desc', '').strip()
        settings.dream_btn1_text = request.POST.get('dream_btn1_text', '').strip()
        settings.dream_btn1_url = request.POST.get('dream_btn1_url', '').strip()
        settings.dream_btn2_text = request.POST.get('dream_btn2_text', '').strip()
        settings.dream_btn2_url = request.POST.get('dream_btn2_url', '').strip()

        settings.dream_feat_1_icon = request.POST.get('dream_feat_1_icon', '').strip()
        settings.dream_feat_1_title = request.POST.get('dream_feat_1_title', '').strip()
        settings.dream_feat_1_desc = request.POST.get('dream_feat_1_desc', '').strip()

        settings.dream_feat_2_icon = request.POST.get('dream_feat_2_icon', '').strip()
        settings.dream_feat_2_title = request.POST.get('dream_feat_2_title', '').strip()
        settings.dream_feat_2_desc = request.POST.get('dream_feat_2_desc', '').strip()

        settings.dream_feat_3_icon = request.POST.get('dream_feat_3_icon', '').strip()
        settings.dream_feat_3_title = request.POST.get('dream_feat_3_title', '').strip()
        settings.dream_feat_3_desc = request.POST.get('dream_feat_3_desc', '').strip()

        settings.dream_feat_4_icon = request.POST.get('dream_feat_4_icon', '').strip()
        settings.dream_feat_4_title = request.POST.get('dream_feat_4_title', '').strip()
        settings.dream_feat_4_desc = request.POST.get('dream_feat_4_desc', '').strip()

    if 'dream_image' in request.FILES:
        settings.dream_image = request.FILES['dream_image']

    # 8. Stats Counter Bar
    if 'stat_1_num' in request.POST:
        settings.stat_1_num = request.POST.get('stat_1_num', '').strip()
        settings.stat_1_label = request.POST.get('stat_1_label', '').strip()
        settings.stat_1_icon = request.POST.get('stat_1_icon', '').strip()

        settings.stat_2_num = request.POST.get('stat_2_num', '').strip()
        settings.stat_2_label = request.POST.get('stat_2_label', '').strip()
        settings.stat_2_icon = request.POST.get('stat_2_icon', '').strip()

        settings.stat_3_num = request.POST.get('stat_3_num', '').strip()
        settings.stat_3_label = request.POST.get('stat_3_label', '').strip()
        settings.stat_3_icon = request.POST.get('stat_3_icon', '').strip()

        settings.stat_4_num = request.POST.get('stat_4_num', '').strip()
        settings.stat_4_label = request.POST.get('stat_4_label', '').strip()
        settings.stat_4_icon = request.POST.get('stat_4_icon', '').strip()

    # 9. SEO & Meta
    if 'meta_title' in request.POST:
        settings.meta_title = request.POST.get('meta_title', '').strip()
        settings.meta_description = request.POST.get('meta_description', '').strip()
        settings.meta_keywords = request.POST.get('meta_keywords', '').strip()

    settings.save()
    messages.success(request, "Blog page configuration updated successfully!")
    return True



def handle_gallery_page_save(request, admin_user):
    from apps.core.models import GalleryPageSettings
    from django.contrib import messages
    import json

    settings = GalleryPageSettings.get_settings()

    # 0. Master Visibility Toggles
    if 'save_visibility' in request.POST or 'header_visible' in request.POST or 'header_title' in request.POST:
        settings.header_visible = request.POST.get('header_visible') in ('on', '1', 'true')
        settings.gallery_visible = request.POST.get('gallery_visible') in ('on', '1', 'true')
        settings.info_boxes_visible = request.POST.get('info_boxes_visible') in ('on', '1', 'true')
        settings.contact_visible = request.POST.get('contact_visible') in ('on', '1', 'true')
        settings.info_cards_visible = request.POST.get('info_cards_visible') in ('on', '1', 'true')

    # 1. Header Banner
    if 'header_title' in request.POST:
        settings.header_eyebrow = request.POST.get('header_eyebrow', '').strip()
        settings.header_title = request.POST.get('header_title', '').strip()
        settings.header_breadcrumb_root = request.POST.get('header_breadcrumb_root', '').strip()
        settings.header_breadcrumb_sub = request.POST.get('header_breadcrumb_sub', '').strip()

    # 2. Our Gallery Section
    if 'gallery_title' in request.POST:
        settings.gallery_title = request.POST.get('gallery_title', '').strip()
    if 'gallery_items_json' in request.POST:
        val = request.POST.get('gallery_items_json', '').strip()
        if val:
            try:
                json.loads(val)
                settings.gallery_items_json = val
            except Exception:
                pass

    # 3. Gallery Info Boxes (3 Boxes)
    if 'box1_title' in request.POST:
        import re
        def _clean_plain_title(text):
            if not text:
                return ''
            cleaned = re.sub(r'<\s*br\s*/?>', ' ', text, flags=re.IGNORECASE)
            cleaned = re.sub(r'<[^>]+>', '', cleaned)
            return ' '.join(cleaned.split())

        settings.box1_icon = request.POST.get('box1_icon', '').strip()
        settings.box1_color = request.POST.get('box1_color', 'red-icon').strip()
        settings.box1_title = _clean_plain_title(request.POST.get('box1_title', ''))
        settings.box1_text = request.POST.get('box1_text', '').strip()
        settings.box1_btn_text = request.POST.get('box1_btn_text', '').strip()
        settings.box1_btn_url = request.POST.get('box1_btn_url', '').strip()

        settings.box2_icon = request.POST.get('box2_icon', '').strip()
        settings.box2_color = request.POST.get('box2_color', 'blue-icon').strip()
        settings.box2_title = _clean_plain_title(request.POST.get('box2_title', ''))
        settings.box2_text = request.POST.get('box2_text', '').strip()
        settings.box2_btn_text = request.POST.get('box2_btn_text', '').strip()
        settings.box2_btn_url = request.POST.get('box2_btn_url', '').strip()

        settings.box3_icon = request.POST.get('box3_icon', '').strip()
        settings.box3_color = request.POST.get('box3_color', 'blue-icon').strip()
        settings.box3_title = _clean_plain_title(request.POST.get('box3_title', ''))
        settings.box3_text = request.POST.get('box3_text', '').strip()
        settings.box3_btn_text = request.POST.get('box3_btn_text', '').strip()
        settings.box3_btn_url = request.POST.get('box3_btn_url', '').strip()

    # 4. Get In Touch & Send Message Form
    if 'contact_title' in request.POST or 'form_title' in request.POST:
        import re
        settings.contact_title = request.POST.get('contact_title', '').strip()
        settings.contact_phone = request.POST.get('contact_phone', '').strip()
        settings.contact_email = request.POST.get('contact_email', '').strip()
        settings.contact_website = request.POST.get('contact_website', '').strip()
        raw_c_addr = request.POST.get('contact_address', '').strip()
        raw_c_addr = re.sub(r'<\s*br\s*/?>', '\n', raw_c_addr, flags=re.IGNORECASE)
        settings.contact_address = re.sub(r'<[^>]+>', '', raw_c_addr).strip()

        settings.social_facebook = request.POST.get('social_facebook', '').strip()
        settings.social_instagram = request.POST.get('social_instagram', '').strip()
        settings.social_linkedin = request.POST.get('social_linkedin', '').strip()
        settings.social_youtube = request.POST.get('social_youtube', '').strip()

        settings.form_title = request.POST.get('form_title', '').strip()
        settings.form_btn_text = request.POST.get('form_btn_text', '').strip()

    # 5. Info Cards Section (Address, Call Us, Email Us)
    if 'card_address_title' in request.POST:
        import re
        settings.card_address_title = request.POST.get('card_address_title', '').strip()
        raw_card_addr = request.POST.get('card_address_text', '').strip()
        raw_card_addr = re.sub(r'<\s*br\s*/?>', '\n', raw_card_addr, flags=re.IGNORECASE)
        settings.card_address_text = re.sub(r'<[^>]+>', '', raw_card_addr).strip()
        settings.card_address_map_url = request.POST.get('card_address_map_url', '').strip()
        settings.card_address_map_badge_url = request.POST.get('card_address_map_badge_url', '').strip()
        settings.card_address_directions_url = request.POST.get('card_address_directions_url', '').strip()
        settings.card_address_directions_text = request.POST.get('card_address_directions_text', '').strip()

    if 'card_call_title' in request.POST:
        settings.card_call_title = request.POST.get('card_call_title', '').strip()
    if 'call_rows_json' in request.POST:
        val = request.POST.get('call_rows_json', '').strip()
        if val:
            try:
                json.loads(val)
                settings.call_rows_json = val
            except Exception:
                pass

    if 'card_email_title' in request.POST:
        settings.card_email_title = request.POST.get('card_email_title', '').strip()
    if 'email_rows_json' in request.POST:
        val = request.POST.get('email_rows_json', '').strip()
        if val:
            try:
                json.loads(val)
                settings.email_rows_json = val
            except Exception:
                pass

    # 6. SEO & Meta Tags
    if 'meta_title' in request.POST:
        settings.meta_title = request.POST.get('meta_title', '').strip()
        settings.meta_description = request.POST.get('meta_description', '').strip()
        settings.meta_keywords = request.POST.get('meta_keywords', '').strip()

    settings.save()
    messages.success(request, "Gallery page configuration updated successfully!")
    return True


def handle_contact_page_save(request, admin_user):
    from apps.core.models import ContactPageSettings
    from django.contrib import messages
    import json
    import re

    settings = ContactPageSettings.get_settings()

    # 0. Master Visibility Toggles
    if 'save_visibility' in request.POST or 'header_visible' in request.POST or 'header_title' in request.POST:
        settings.header_visible = request.POST.get('header_visible') in ('on', '1', 'true')
        settings.contact_section_visible = request.POST.get('contact_section_visible') in ('on', '1', 'true')
        settings.info_cards_visible = request.POST.get('info_cards_visible') in ('on', '1', 'true')

    # 1. Header Banner
    if 'header_title' in request.POST:
        settings.header_eyebrow = request.POST.get('header_eyebrow', '').strip()
        settings.header_title = request.POST.get('header_title', '').strip()
        settings.header_breadcrumb_root = request.POST.get('header_breadcrumb_root', '').strip()
        settings.header_breadcrumb_sub = request.POST.get('header_breadcrumb_sub', '').strip()

    # 2. Contact Section
    if 'contact_phone' in request.POST:
        settings.contact_phone = request.POST.get('contact_phone', '').strip()
        settings.contact_email = request.POST.get('contact_email', '').strip()
        settings.contact_website = request.POST.get('contact_website', '').strip()
        
        c_addr = request.POST.get('contact_address', '').strip()
        c_addr = re.sub(r'<\s*br\s*/?>', '\n', c_addr, flags=re.IGNORECASE)
        settings.contact_address = re.sub(r'<[^>]+>', '', c_addr).strip()

        settings.social_facebook = request.POST.get('social_facebook', '').strip()
        settings.social_instagram = request.POST.get('social_instagram', '').strip()
        settings.social_linkedin = request.POST.get('social_linkedin', '').strip()
        settings.social_youtube = request.POST.get('social_youtube', '').strip()

        settings.form_title = request.POST.get('form_title', '').strip()
        settings.form_btn_text = request.POST.get('form_btn_text', '').strip()

        settings.location_badge_title = request.POST.get('location_badge_title', '').strip()
        loc_b_addr = request.POST.get('location_badge_address', '').strip()
        loc_b_addr = re.sub(r'<\s*br\s*/?>', '\n', loc_b_addr, flags=re.IGNORECASE)
        settings.location_badge_address = re.sub(r'<[^>]+>', '', loc_b_addr).strip()
        settings.location_badge_image = request.POST.get('location_badge_image', '').strip()
        if 'location_map_url' in request.POST:
            loc_map = request.POST.get('location_map_url', '').strip()
            if '<iframe' in loc_map and 'src=' in loc_map:
                m = re.search(r'src=["\']([^"\']+)["\']', loc_map, re.IGNORECASE)
                if m:
                    loc_map = m.group(1)
            settings.location_map_url = loc_map

    # 3. Contact Info Cards (Address, Call Us, Email Us)
    if 'card_address_title' in request.POST:
        settings.card_address_title = request.POST.get('card_address_title', '').strip()
        card_addr = request.POST.get('card_address_text', '').strip()
        card_addr = re.sub(r'<\s*br\s*/?>', '\n', card_addr, flags=re.IGNORECASE)
        settings.card_address_text = re.sub(r'<[^>]+>', '', card_addr).strip()
        
        settings.card_address_map_url = request.POST.get('card_address_map_url', '').strip()
        settings.card_address_map_badge_url = request.POST.get('card_address_map_badge_url', '').strip()
        settings.card_address_directions_url = request.POST.get('card_address_directions_url', '').strip()
        settings.card_address_directions_text = request.POST.get('card_address_directions_text', '').strip()

    if 'card_call_title' in request.POST:
        settings.card_call_title = request.POST.get('card_call_title', '').strip()
    if 'call_rows_json' in request.POST:
        val = request.POST.get('call_rows_json', '').strip()
        if val:
            try:
                json.loads(val)
                settings.call_rows_json = val
            except Exception:
                pass

    if 'card_email_title' in request.POST:
        settings.card_email_title = request.POST.get('card_email_title', '').strip()
    if 'email_rows_json' in request.POST:
        val = request.POST.get('email_rows_json', '').strip()
        if val:
            try:
                json.loads(val)
                settings.email_rows_json = val
            except Exception:
                pass

    settings.save()
    messages.success(request, "Contact page configuration updated successfully!")
    return True
