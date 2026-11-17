import logging
from apps.candidate_portal.models import ApplicationStatusHistory
from apps.candidates.constants import ALLOWED_TRANSITIONS, get_candidate_step

logger = logging.getLogger(__name__)

def set_applicant_status(applicant, new_status, changed_by='system', notes='', send_email_notification=True, force_override=False):
    """
    Updates an Applicant's status, updates flow_step, records status history, and optionally sends an email notification.
    Enforces server-side sequential transition rules unless force_override is True or changed_by is admin.
    """
    old_status = applicant.status or "Application Submitted"

    # 1. Enforce server-side transition checks
    is_admin = changed_by in ['admin', 'superadmin', 'Super Admin'] or str(changed_by).lower().startswith('admin')
    if not force_override and not is_admin:
        allowed = ALLOWED_TRANSITIONS.get(old_status, set())
        if new_status not in allowed and new_status != old_status:
            raise ValueError(f"Invalid status transition from '{old_status}' to '{new_status}'. Allowed next statuses: {list(allowed)}")

    has_history = ApplicationStatusHistory.objects.filter(applicant=applicant).exists()
    if old_status == new_status and applicant.flow_step == get_candidate_step(new_status) and has_history:
        return applicant

    applicant.status = new_status
    applicant.flow_step = get_candidate_step(new_status)

    from django.utils import timezone

    if new_status in ['Shortlisted', 'Interview', 'Interview Scheduled', 'Selected', 'Offer Released', 'Offered', 'Joined', 'Placed', 'Hired']:
        if applicant.approval_status != 'Approved':
            applicant.approval_status = 'Approved'
        if not applicant.approved_at:
            applicant.approved_at = timezone.now()
        if not applicant.approved_by:
            admin_label = str(changed_by or 'Admin')
            applicant.approved_by = admin_label if not admin_label.lower().startswith('system') else 'Super Admin'

        # Ensure applicant is linked to an employer so they appear on employer portal
        if not applicant.employer:
            try:
                from apps.accounts.models import EmployerAccount
                assigned_emp = None
                if applicant.job and applicant.job.employer:
                    assigned_emp = applicant.job.employer
                elif applicant.job and applicant.job.company:
                    assigned_emp = (
                        EmployerAccount.objects.filter(company=applicant.job.company).first()
                        or EmployerAccount.objects.filter(company_name__iexact=applicant.job.company.name).first()
                    )
                elif applicant.company:
                    assigned_emp = (
                        EmployerAccount.objects.filter(company=applicant.company).first()
                        or EmployerAccount.objects.filter(company_name__iexact=applicant.company.name).first()
                    )

                if not assigned_emp:
                    assigned_emp = EmployerAccount.objects.filter(status='APPROVED').first() or EmployerAccount.objects.first()

                if assigned_emp:
                    applicant.employer = assigned_emp
                    if not applicant.company and assigned_emp.company:
                        applicant.company = assigned_emp.company
                    if applicant.job and not applicant.job.employer:
                        applicant.job.employer = assigned_emp
                        if not applicant.job.company and assigned_emp.company:
                            applicant.job.company = assigned_emp.company
                        applicant.job.save(update_fields=['employer', 'company'])
            except Exception as e:
                logger.error(f"Error auto-linking employer for applicant {applicant.id}: {e}")

    if new_status in ['Joined', 'Placed', 'Candidate Joined', 'Hired', 'Offered & Joined', 'Completed']:
        try:
            from apps.ledger.services import ensure_commission_for_joined
            ensure_commission_for_joined(applicant=applicant, created_by=str(changed_by or 'System'))
        except Exception as e:
            logger.error(f"Failed to auto-create ledger commission for applicant {applicant.id}: {e}")

    if new_status == 'Rejected':
        if not applicant.approval_status or applicant.approval_status == 'Pending':
            applicant.approval_status = 'Rejected'
            if notes and not applicant.rejection_reason:
                applicant.rejection_reason = notes

    applicant.save()

    # 2. Record in status history
    try:
        ApplicationStatusHistory.objects.create(
            applicant=applicant,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            notes=notes or f"Status updated from '{old_status}' to '{new_status}' by {changed_by}"
        )
    except Exception as e:
        logger.error(f"Failed to record status history for applicant {applicant.id}: {e}")

    # 3. Trigger notification email if enabled
    if send_email_notification:
        try:
            from apps.candidate_portal.notifications import notify_applicant_status_change
            notify_applicant_status_change(applicant, old_status, new_status, notes=notes)
        except Exception as e:
            logger.error(f"Failed to send status change email notification for applicant {applicant.id}: {e}")

    return applicant

