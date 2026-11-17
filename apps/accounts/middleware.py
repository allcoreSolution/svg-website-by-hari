import re
from django.shortcuts import render, redirect
from django.http import JsonResponse
from apps.accounts.models import AdminUser
from apps.accounts.permissions import URL_PERMISSION_MAP
from apps.enquiries.models import log_activity

# Routes that are completely exempt from admin auth and permission checks
EXEMPT_PREFIXES = (
    '/admin-panel/login',
    '/api/admin/login',
    '/api/admin/logout',
    '/api/admin/forgot-password',
    '/api/admin/reset-password',
    '/django-admin',
    '/static/',
)

# Public customer-facing candidate/employer portal endpoints
PORTAL_PUBLIC_PREFIXES = (
    '/api/candidate/',
    '/api/employer/',
)

# Admin API prefixes that must be protected by AdminPermissionMiddleware
ADMIN_API_PREFIXES = (
    '/api/admin/',
    '/api/applicants',
    '/api/applicant/',
    '/api/candidates/create',
    '/api/resumes',
    '/api/resume/',
    '/api/interviews',
    '/api/interview/',
    '/api/companies',
    '/api/company/',
    '/api/company-contacts',
    '/api/company-contact/',
    '/api/company-requirements',
    '/api/company-requirement/',
    '/api/company-enquiries',
    '/api/company-enquiry/',
    '/api/enquiries',
    '/api/enquiry/',
    '/api/contacts',
    '/api/contact/',
    '/api/follow-ups',
    '/api/follow-up/',
    '/api/placements',
    '/api/placement/',
    '/api/job-offers',
    '/api/job-offer/',
    '/api/internships',
    '/api/internship/',
    '/api/internship-providers',
    '/api/internship-provider/',
    '/api/internship-applications',
    '/api/internship-application/',
    '/api/internship-enquiries',
    '/api/internship-enquiry/',
)

class AdminPermissionMiddleware:
    """
    Central server-side permission enforcement for SVG Consultancy.
    Protects /admin-panel pages and all admin data APIs with granular method-wise checks.
    Allows public applicant/contact form submissions for anonymous users.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Compile regexes once for high-performance matching
        self._compiled_map = [
            (mod, re.compile(pat), method.upper(), perm)
            for mod, pat, method, perm in URL_PERMISSION_MAP
        ]

    def is_public_exempt(self, path, method):
        """Determine if a request is a public/exempt endpoint."""
        # 1. Static and public admin auth
        for pfx in EXEMPT_PREFIXES:
            if path.startswith(pfx):
                return True

        # 2. Candidate & Employer public portal auth/forms
        for pfx in PORTAL_PUBLIC_PREFIXES:
            if path.startswith(pfx):
                return True

        # 3. Public job listing and public applications
        if method == 'POST':
            if path in ('/api/apply', '/api/apply/',
                        '/api/upload-resume', '/api/upload-resume/',
                        '/api/contact', '/api/contact/',
                        '/api/company-enquiry', '/api/company-enquiry/',
                        '/api/internship-apply', '/api/internship-apply/',
                        '/api/internship-enquiry', '/api/internship-enquiry/'):
                return True

        if method == 'GET':
            if path in ('/api/jobs', '/api/jobs/',
                        '/api/public/internships', '/api/public/internships/'):
                return True

        return False

    def is_admin_scope(self, path):
        """Check if request URL falls into admin panel or admin data APIs."""
        if path.startswith('/admin-panel'):
            return True
        for pfx in ADMIN_API_PREFIXES:
            if path.startswith(pfx):
                return True
        return False

    def __call__(self, request):
        path = request.path
        method = request.method.upper()

        # 1. Skip public/exempt requests
        if self.is_public_exempt(path, method):
            return self.get_response(request)

        # 2. Only process admin scope
        if not self.is_admin_scope(path):
            return self.get_response(request)

        is_ajax_or_api = path.startswith('/api/') or request.headers.get('x-requested-with') == 'XMLHttpRequest'
        admin_id = request.session.get('admin_id')

        # 3. Authentication Check
        if not admin_id:
            if is_ajax_or_api:
                return JsonResponse({"status": "error", "message": "Authentication required. Please log in as admin."}, status=401)
            return redirect(f'/admin-panel/login/?next={path}')

        # 4. Fetch fresh AdminUser record
        admin_user = AdminUser.objects.filter(id=admin_id, is_active=True).select_related('role').first()
        if not admin_user:
            request.session.flush()
            if is_ajax_or_api:
                return JsonResponse({"status": "error", "message": "Your admin account is inactive or not found."}, status=401)
            return redirect('/admin-panel/login/')

        # Attach active admin user to request
        request.admin_user = admin_user

        # 5. Role Assignment Check (Requirement 5)
        # If user has no role or the assigned role is archived/inactive
        if not admin_user.role or not admin_user.role.is_active:
            if is_ajax_or_api:
                return JsonResponse({
                    "status": "error",
                    "code": "NO_ROLE_ASSIGNED",
                    "message": "Your admin account has no active role assigned. Please contact Super Admin."
                }, status=403)
            return render(request, 'dashboard/no_role_assigned.html', {
                "admin_user": admin_user,
            }, status=403)

        # 6. Super Admin Bypass
        if admin_user.role.is_super:
            return self.get_response(request)

        # 7. Match against URL_PERMISSION_MAP
        matched_perm = None
        for mod, compiled_pat, req_method, perm_code in self._compiled_map:
            if req_method in ('ANY', method):
                if compiled_pat.match(path):
                    matched_perm = perm_code
                    break

        if matched_perm:
            if admin_user.has_perm(matched_perm):
                return self.get_response(request)
            else:
                log_activity("security", "Access Denied", f"Admin {admin_user.email} denied {method} on {path} (Requires: {matched_perm})")
                if is_ajax_or_api:
                    return JsonResponse({
                        "status": "error",
                        "message": f"Permission denied. Required privilege: {matched_perm}"
                    }, status=403)
                return render(request, 'dashboard/admin_403.html', {
                    "admin_user": admin_user,
                    "required_perm": matched_perm,
                    "attempted_url": path,
                }, status=403)
        else:
            # Unmapped admin route: Default DENY for non-super admin
            log_activity("security", "Unmapped Route Denied", f"Admin {admin_user.email} tried unmapped admin route {method} {path}")
            if is_ajax_or_api:
                return JsonResponse({
                    "status": "error",
                    "message": "Access restricted. Contact Super Admin to configure access for this route."
                }, status=403)
            return render(request, 'dashboard/admin_403.html', {
                "admin_user": admin_user,
                "required_perm": "Restricted (Unmapped)",
                "attempted_url": path,
            }, status=403)
