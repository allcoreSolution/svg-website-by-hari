from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.views.static import serve
from django.http import HttpResponseForbidden

PROTECTED_MEDIA_DIRS = (
    'uploads/resumes',
    'uploads/offer_letters',
    'uploads/company_documents',
    'uploads/communication',
)

def protected_media_serve(request, path):
    """
    Protected media file server:
    - Public branding, gallery, services, and staff photos are served freely.
    - Uploaded resumes, offer letters, company documents, and communication files
      require authorized admin permissions or verified portal access.
    """
    norm_path = path.replace('\\', '/').lstrip('/')
    is_protected = any(norm_path.startswith(pdir) for pdir in PROTECTED_MEDIA_DIRS)

    if not is_protected:
        # Public images: branding, gallery, services, staff_photos, etc.
        return serve(request, path, document_root=settings.MEDIA_ROOT)

    # Protected documents: require authenticated session and proper permission
    admin_id = request.session.get('admin_id')
    candidate_id = request.session.get('candidate_id')
    employer_id = request.session.get('employer_id')

    if not (admin_id or candidate_id or employer_id):
        return HttpResponseForbidden("Access denied. Please log in to view this document.")

    if admin_id:
        from apps.accounts.models import AdminUser
        admin_user = getattr(request, 'admin_user', None)
        if not admin_user:
            admin_user = AdminUser.objects.filter(id=admin_id, is_active=True).select_related('role').first()

        if admin_user and admin_user.role and admin_user.role.is_active:
            if admin_user.role.is_super:
                return serve(request, path, document_root=settings.MEDIA_ROOT)

            if norm_path.startswith('uploads/resumes') and admin_user.has_perm('candidates.view'):
                return serve(request, path, document_root=settings.MEDIA_ROOT)
            elif norm_path.startswith('uploads/offer_letters') and admin_user.has_perm('offer_letters.view'):
                return serve(request, path, document_root=settings.MEDIA_ROOT)
            elif norm_path.startswith('uploads/company_documents') and admin_user.has_perm('employers.view'):
                return serve(request, path, document_root=settings.MEDIA_ROOT)
            elif norm_path.startswith('uploads/communication') and (admin_user.has_perm('comm_history.view') or admin_user.has_perm('comm_compose.view')):
                return serve(request, path, document_root=settings.MEDIA_ROOT)

    if candidate_id or employer_id:
        return serve(request, path, document_root=settings.MEDIA_ROOT)

    return HttpResponseForbidden("Access denied. You do not have permission to view this document.")

urlpatterns = [
    # Django Built-in Admin
    path('django-admin/', admin.site.urls),

    # Custom Admin Dashboard & Authentication
    path('', include('apps.dashboard.urls')),
    path('', include('apps.accounts.urls')),

    # REST APIs & Candidate Portal
    path('', include('apps.candidate_portal.urls')),
    path('', include('apps.employer_portal.urls')),
    path('', include('apps.candidates.urls')),
    path('', include('apps.companies.urls')),
    path('', include('apps.internships.urls')),
    path('', include('apps.placements.urls')),
    path('', include('apps.enquiries.urls')),
    path('', include('apps.jobs.urls')),
    path('', include('apps.ledger.urls')),
    path('', include('apps.communication.urls')),

    # Core Frontend Pages (Home, About, Services, etc.)
    path('', include('apps.core.urls')),

    # Protected Media Route
    re_path(r'^media/(?P<path>.*)$', protected_media_serve, name='media_serve'),
]
