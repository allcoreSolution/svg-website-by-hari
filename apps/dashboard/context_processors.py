from django.core.cache import cache
from apps.accounts.models import CandidateAccount, EmployerAccount, AdminUser
from apps.candidates.models import Applicant
from apps.enquiries.models import ContactEnquiry
from apps.companies.models import CompanyEnquiry
from apps.internships.models import InternshipEnquiry, InternshipApplication

def admin_counts_context(request):
    """
    Context processor that injects dynamic live counts for topbar icons and admin modules,
    as well as current AdminUser, Role, and active Permission codes.
    """
    admin_user = getattr(request, 'admin_user', None)
    if not admin_user and hasattr(request, 'session') and request.session.get('admin_id'):
        try:
            admin_user = AdminUser.objects.filter(id=request.session.get('admin_id'), is_active=True).select_related('role').first()
            if admin_user:
                request.admin_user = admin_user
        except Exception:
            admin_user = None

    admin_role = admin_user.role if admin_user else None
    is_super_admin = bool(admin_role and admin_role.is_super)
    perms = admin_user.get_permission_codes() if admin_user else set()

    data = {
        'admin_user': admin_user,
        'admin_role': admin_role,
        'is_super_admin': is_super_admin,
        'perms': perms,
    }

    if request.path.startswith('/admin-panel/'):
        try:
            failed_delivery_count = cache.get('comm_failed_delivery_count')
            if failed_delivery_count is None:
                try:
                    from apps.communication.models import MessageRecipient
                    failed_delivery_count = MessageRecipient.objects.filter(delivery_status='Failed').count()
                    cache.set('comm_failed_delivery_count', failed_delivery_count, timeout=60)
                except Exception:
                    failed_delivery_count = 0

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
            total_pending_registrations = pending_candidates + pending_employers

            from django.conf import settings
            is_smtp_configured = bool(getattr(settings, 'EMAIL_HOST_USER', '') and getattr(settings, 'EMAIL_HOST_PASSWORD', ''))

            data.update({
                'unread_messages_count': total_messages,
                'notifications_count': total_notifications,
                'mail_applications_count': total_mail_apps,
                'total_pending_registrations': total_pending_registrations,
                'pending_candidates_count': pending_candidates,
                'pending_employers_count': pending_employers,
                'pending_job_apps_count': pending_job_apps,
                'failed_delivery_count': failed_delivery_count,
                'is_smtp_configured': is_smtp_configured,
            })
            return data
        except Exception:
            pass

    from django.conf import settings
    is_smtp_configured = bool(getattr(settings, 'EMAIL_HOST_USER', '') and getattr(settings, 'EMAIL_HOST_PASSWORD', ''))

    data.update({
        'unread_messages_count': 0,
        'notifications_count': 0,
        'mail_applications_count': 0,
        'total_pending_registrations': 0,
        'pending_candidates_count': 0,
        'pending_employers_count': 0,
        'pending_job_apps_count': 0,
        'failed_delivery_count': 0,
        'is_smtp_configured': is_smtp_configured,
    })
    return data
