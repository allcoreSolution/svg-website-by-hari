import os
import csv
import json
import time
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q, Count, F
from django.conf import settings
from django.core.cache import cache
from django.core.validators import validate_email, ValidationError

from apps.accounts.auth_helpers import admin_required, candidate_required, employer_required
from apps.accounts.models import CandidateAccount, EmployerAccount
from apps.jobs.models import Job
from apps.companies.models import Company
from apps.communication.models import BulkMessage, MessageRecipient, MessageTemplate
from apps.communication.sanitizer import sanitize_html, html_to_plain_text
from apps.communication.services import (
    resolve_recipients,
    render_placeholders,
    get_daily_sent_email_count,
    create_recipient_snapshots,
    send_test_email,
    queue_bulk_message_send,
    recompute_bulk_message_status,
    validate_attachment_file,
    check_stale_sending_messages,
    mask_sensitive_info
)
from apps.enquiries.models import log_activity


# ==============================================================================
# ADMIN BULK MESSAGING VIEWS
# ==============================================================================

@admin_required
def compose_view(request):
    check_stale_sending_messages()

    preset_template_id = request.GET.get('template', '').strip()
    duplicate_msg_id = request.GET.get('duplicate', '').strip()

    initial_title = ""
    initial_subject = ""
    initial_body = ""
    initial_audience = "candidate"
    initial_cand_filter = "registered"

    if preset_template_id:
        try:
            if preset_template_id.isdigit():
                tpl = MessageTemplate.objects.filter(id=int(preset_template_id)).first()
            else:
                tpl = MessageTemplate.objects.filter(name__icontains=preset_template_id).first()
            if tpl:
                initial_subject = tpl.subject
                initial_body = tpl.body
                initial_audience = tpl.audience_type if tpl.audience_type in ['candidate', 'employer'] else 'candidate'
                initial_title = f"{tpl.name} Broadcast"
        except Exception:
            pass

    if duplicate_msg_id and duplicate_msg_id.isdigit():
        try:
            dup_msg = BulkMessage.objects.filter(id=int(duplicate_msg_id)).first()
            if dup_msg:
                initial_title = f"Copy of {dup_msg.title}"
                initial_subject = dup_msg.subject
                initial_body = dup_msg.body
                initial_audience = dup_msg.audience_type
                initial_cand_filter = dup_msg.candidate_filter or 'registered'
        except Exception:
            pass

    is_gmail_configured = bool(getattr(settings, 'EMAIL_HOST_USER', '') and getattr(settings, 'EMAIL_HOST_PASSWORD', ''))
    daily_limit = getattr(settings, 'COMM_EMAIL_DAILY_LIMIT', 400)
    daily_sent = get_daily_sent_email_count()
    daily_remaining = max(0, daily_limit - daily_sent)
    sms_whatsapp_enabled = getattr(settings, 'COMM_ENABLE_SMS_WHATSAPP', False)

    context = {
        'active_menu': 'communication',
        'sub_active': 'compose',
        'initial_title': initial_title,
        'initial_subject': initial_subject,
        'initial_body': initial_body,
        'initial_audience': initial_audience,
        'initial_cand_filter': initial_cand_filter,
        'approved_employers': EmployerAccount.objects.filter(status='APPROVED').order_by('company_name'),
        'pending_employers': EmployerAccount.objects.filter(status='PENDING').order_by('company_name'),
        'active_jobs': Job.objects.filter(status='ACTIVE').order_by('title')[:100],
        'companies': Company.objects.all().order_by('name')[:100],
        'candidates_sample': resolve_recipients(audience_type='candidate', candidate_filter=initial_cand_filter)[:200],
        'templates_list': MessageTemplate.objects.filter(is_active=True).order_by('name'),
        'is_gmail_configured': is_gmail_configured,
        'email_host_user': getattr(settings, 'EMAIL_HOST_USER', ''),
        'daily_sent': daily_sent,
        'daily_limit': daily_limit,
        'daily_remaining': daily_remaining,
        'sms_whatsapp_enabled': sms_whatsapp_enabled,
        'max_attachment_mb': getattr(settings, 'COMM_MAX_ATTACHMENT_MB', 5),
    }
    return render(request, 'communication/compose.html', context)


@admin_required
@require_http_methods(["POST"])
def preview_recipients_api(request):
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST.dict()

        audience_type = data.get('audience_type', 'candidate')
        candidate_filter = data.get('candidate_filter', 'registered')
        include_pending = str(data.get('include_pending', '')).lower() in ['true', '1', 'yes', 'on']

        raw_emp_ids = data.get('employer_ids', [])
        if isinstance(raw_emp_ids, str):
            raw_emp_ids = [int(i.strip()) for i in raw_emp_ids.split(',') if i.strip().isdigit()]

        raw_cand_ids = data.get('specific_candidate_ids', [])
        if isinstance(raw_cand_ids, str):
            raw_cand_ids = [int(i.strip()) for i in raw_cand_ids.split(',') if i.strip().isdigit()]

        job_id = data.get('job_id') or None
        company_id = data.get('company_id') or None

        recipients = resolve_recipients(
            audience_type=audience_type,
            candidate_filter=candidate_filter,
            include_pending=include_pending,
            employer_ids=raw_emp_ids,
            specific_candidate_ids=raw_cand_ids,
            job_id=job_id,
            company_id=company_id
        )

        candidates_data = []
        employers_data = []
        if audience_type == 'candidate':
            category_candidates = resolve_recipients(
                audience_type='candidate',
                candidate_filter=candidate_filter,
                include_pending=include_pending,
                job_id=job_id,
                company_id=company_id
            )
            candidates_data = [
                {
                    'id': c.id,
                    'full_name': c.full_name,
                    'email': c.email or 'No email'
                }
                for c in category_candidates[:200]
            ]
        elif audience_type == 'employer':
            category_employers = resolve_recipients(
                audience_type='employer',
                candidate_filter=candidate_filter,
            )
            employers_data = [
                {
                    'id': e.id,
                    'company_name': e.company_name,
                    'contact_name': e.contact_name,
                    'email': e.email or 'No email'
                }
                for e in category_employers[:200]
            ]

        total_count = len(recipients)
        preview_list = []
        no_email_count = 0
        opted_out_count = 0
        seen_emails = set()
        duplicate_count = 0

        for r in recipients:
            email_addr = getattr(r, 'email', '').strip().lower()
            if not email_addr:
                no_email_count += 1
            else:
                if email_addr in seen_emails:
                    duplicate_count += 1
                seen_emails.add(email_addr)

            if not getattr(r, 'email_notifications_enabled', True):
                opted_out_count += 1

        for r in recipients[:10]:
            if isinstance(r, CandidateAccount):
                preview_list.append(f"{r.full_name} ({r.email or 'No email'})")
            else:
                preview_list.append(f"{r.company_name} - {r.contact_name} ({r.email or 'No email'})")

        return JsonResponse({
            'status': 'success',
            'count': total_count,
            'preview': preview_list,
            'candidates': candidates_data,
            'employers': employers_data,
            'skipped': {
                'no_email': no_email_count,
                'opted_out': opted_out_count,
                'duplicates': duplicate_count,
                'total_skipped': no_email_count + opted_out_count + duplicate_count
            }
        })
    except Exception as e:
        logger.warning(f"Error in preview_recipients_api: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@admin_required
@require_http_methods(["POST"])
def send_test_email_api(request):
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST.dict()

        to_email = data.get('to_email', '').strip()
        subject = data.get('subject', 'Sky Vision Test Email').strip()
        body = data.get('body', 'This is a test email sent from Sky Vision Group Bulk Communication module.').strip()

        admin_user = getattr(request, 'admin_user', None)
        admin_email = getattr(admin_user, 'email', None) or request.session.get('admin_name', 'Admin')

        if not to_email:
            to_email = getattr(admin_user, 'email', None) or 'admin@skyvision.com'

        ok, msg = send_test_email(to_email, subject, body, recipient_name="Admin")
        if ok:
            log_activity(
                action_type="Communication Test Email",
                title=f"Test email sent to {to_email}",
                description=f"Subject: {subject}",
                actor=admin_email
            )
            return JsonResponse({'status': 'success', 'message': msg})
        else:
            return JsonResponse({'status': 'error', 'message': msg}, status=400)
    except Exception as e:
        logger.warning(f"Error in send_test_email_api: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@admin_required
@require_http_methods(["POST"])
def send_bulk_message_api(request):
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST.dict()

        admin_user = getattr(request, 'admin_user', None)
        admin_id = getattr(admin_user, 'id', 'session')
        admin_email = getattr(admin_user, 'email', None) or request.session.get('admin_name', 'Admin')

        # 1. Rate Limiting: max 10 sends/minute per admin
        rate_key = f"rate_limit_comm_{admin_id}_{int(time.time() // 60)}"
        current_sends = cache.get(rate_key, 0)
        if current_sends >= 10:
            return JsonResponse({
                'status': 'error',
                'message': 'Rate limit exceeded: Maximum 10 broadcasts per minute per admin account.'
            }, status=429)
        cache.set(rate_key, current_sends + 1, timeout=65)

        title = data.get('title', '').strip()
        subject = data.get('subject', '').strip()
        body = data.get('body', '').strip()
        audience_type = data.get('audience_type', 'candidate')
        candidate_filter = data.get('candidate_filter', 'registered')
        include_pending = str(data.get('include_pending', '')).lower() in ['true', '1', 'yes', 'on']

        raw_emp_ids = data.get('employer_ids', [])
        raw_cand_ids = data.get('specific_candidate_ids', [])
        job_id = data.get('job_id') or None
        company_id = data.get('company_id') or None
        idempotency_key = data.get('idempotency_key', '').strip()

        # Handle channels
        if request.content_type == 'application/json':
            channels = data.get('channels', [])
        else:
            channels = request.POST.getlist('channels') or data.get('channels', [])
            if isinstance(channels, str):
                channels = [c.strip() for c in channels.split(',') if c.strip()]

        action = data.get('action', 'send')
        is_sync = str(data.get('sync', '')).lower() in ['true', '1', 'yes']

        # Attachment handling
        attachment_file = request.FILES.get('attachment')
        if attachment_file:
            try:
                validate_attachment_file(attachment_file)
            except ValidationError as ve:
                return JsonResponse({'status': 'error', 'message': str(ve)}, status=400)

        # Basic validations
        if action == 'draft':
            if not title:
                return JsonResponse({'status': 'error', 'message': 'Title is required to save a draft.'}, status=400)
        else:
            if not title or not subject or not body:
                return JsonResponse({'status': 'error', 'message': 'Title, subject, and message content are required.'}, status=400)

            # Channels validation (Must select at least one)
            valid_channels = [c for c in channels if c in ['email', 'dashboard', 'sms', 'whatsapp']]
            if not valid_channels:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please select at least one delivery channel (Email or Dashboard Notification).'
                }, status=400)
            channels = valid_channels

        # Sanitize HTML body
        sanitized_body = sanitize_html(body)

        # 2. Server-side Idempotency Check
        if idempotency_key and action == 'send':
            existing = BulkMessage.objects.filter(idempotency_key=idempotency_key).first()
            if existing:
                return JsonResponse({
                    'status': 'success',
                    'message': 'Broadcast already initiated (idempotency key recognized).',
                    'message_id': existing.id
                })

        # Clean employer IDs
        cleaned_emp_ids = []
        if audience_type == 'employer':
            if isinstance(raw_emp_ids, str):
                raw_emp_ids = [int(i.strip()) for i in raw_emp_ids.split(',') if i.strip().isdigit()]
            if isinstance(raw_emp_ids, list):
                for e in raw_emp_ids:
                    try:
                        val = int(e)
                        if val not in cleaned_emp_ids:
                            cleaned_emp_ids.append(val)
                    except (ValueError, TypeError):
                        pass

            if cleaned_emp_ids:
                approved_ids = list(EmployerAccount.objects.filter(status='APPROVED', id__in=cleaned_emp_ids).values_list('id', flat=True))
                if len(cleaned_emp_ids) > 0 and len(approved_ids) == 0:
                    return JsonResponse({'status': 'error', 'message': 'Selected employer(s) no longer valid or approved.'}, status=400)
                cleaned_emp_ids = approved_ids

        # Clean specific candidate IDs
        cleaned_cand_ids = []
        if audience_type == 'candidate' and raw_cand_ids:
            if isinstance(raw_cand_ids, str):
                raw_cand_ids = [int(i.strip()) for i in raw_cand_ids.split(',') if i.strip().isdigit()]
            if isinstance(raw_cand_ids, list):
                for c in raw_cand_ids:
                    try:
                        val = int(c)
                        if val not in cleaned_cand_ids:
                            cleaned_cand_ids.append(val)
                    except (ValueError, TypeError):
                        pass

        # Channel gating for SMS/WA
        enable_sms_wa = getattr(settings, 'COMM_ENABLE_SMS_WHATSAPP', False)
        if not enable_sms_wa:
            channels = [c for c in channels if c not in ['sms', 'whatsapp']]

        if action == 'test':
            recipients = resolve_recipients(
                audience_type,
                candidate_filter=candidate_filter,
                include_pending=include_pending,
                employer_ids=cleaned_emp_ids,
                specific_candidate_ids=cleaned_cand_ids,
                job_id=job_id,
                company_id=company_id
            )
            sample_rec = recipients[0] if recipients else (admin_user or CandidateAccount(full_name='Test Admin', email='admin@skyvision.com'))
            rendered_subj = render_placeholders(subject, sample_rec, is_html=False)
            rendered_body = render_placeholders(sanitized_body, sample_rec, is_html=True)
            return JsonResponse({
                'status': 'success',
                'message': 'Test preview generated successfully.',
                'test_subject': rendered_subj,
                'test_body': rendered_body
            })

        bulk_msg = BulkMessage.objects.create(
            title=title,
            subject=subject,
            body=sanitized_body,
            audience_type=audience_type,
            candidate_filter=candidate_filter if audience_type == 'candidate' else '',
            include_pending=include_pending if audience_type == 'candidate' else False,
            employer_ids=cleaned_emp_ids if audience_type == 'employer' else [],
            candidate_ids=cleaned_cand_ids if audience_type == 'candidate' else [],
            job_id=int(job_id) if job_id else None,
            company_id=int(company_id) if company_id else None,
            channels=channels,
            attachment=attachment_file,
            idempotency_key=idempotency_key,
            created_by=admin_user,
            status='Draft' if action == 'draft' else 'Sending'
        )

        create_recipient_snapshots(bulk_msg)

        if action == 'draft':
            bulk_msg.status = 'Draft'
            bulk_msg.save(update_fields=['status'])
            log_activity(
                action_type="Communication Draft Saved",
                title=f"Saved draft '{bulk_msg.title}'",
                actor=admin_email
            )
            return JsonResponse({'status': 'success', 'message': 'Draft saved successfully.', 'message_id': bulk_msg.id})

        if bulk_msg.total_recipients == 0:
            bulk_msg.delete()
            return JsonResponse({'status': 'error', 'message': 'No eligible recipients match your target audience filter.'}, status=400)

        queue_bulk_message_send(
            bulk_msg.id,
            actor_name=admin_email,
            sync=is_sync
        )

        log_activity(
            action_type="Communication Broadcast Sent",
            title=f"Dispatched broadcast '{bulk_msg.title}'",
            description=f"Audience: {bulk_msg.audience_type}, Channels: {', '.join(channels)}",
            actor=admin_email
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Bulk message queued and sending started!',
            'message_id': bulk_msg.id
        })
    except Exception as e:
        logger.exception(f"Error in send_bulk_message_api: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@admin_required
def history_view(request):
    check_stale_sending_messages()

    q = request.GET.get('q', '').strip()
    audience = request.GET.get('audience', '').strip()
    channel = request.GET.get('channel', '').strip()
    status_val = request.GET.get('status', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    qs = BulkMessage.objects.all().order_by('-created_at')

    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(subject__icontains=q))
    if audience:
        qs = qs.filter(audience_type=audience)
    if status_val:
        qs = qs.filter(status=status_val)
    if channel:
        qs = qs.filter(channels__icontains=channel)
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)

    paginator = Paginator(qs, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'active_menu': 'communication',
        'sub_active': 'history',
        'page_obj': page_obj,
        'q': q,
        'audience': audience,
        'channel': channel,
        'status_val': status_val,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'communication/history.html', context)


@admin_required
def history_detail_view(request, id):
    check_stale_sending_messages()

    bulk_msg = get_object_or_404(BulkMessage, id=id)
    recipients_qs = bulk_msg.recipients.select_related('candidate_account', 'employer_account').all().order_by('-id')

    channel_filter = request.GET.get('channel', '').strip().lower()
    if channel_filter in ['email', 'dashboard']:
        recipients_qs = recipients_qs.filter(channel=channel_filter)

    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        recipients_qs = recipients_qs.filter(delivery_status=status_filter)

    paginator = Paginator(recipients_qs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    daily_limit = getattr(settings, 'COMM_EMAIL_DAILY_LIMIT', 400)
    daily_sent = get_daily_sent_email_count()
    daily_remaining = max(0, daily_limit - daily_sent)

    total_recipients = bulk_msg.recipients.count()
    email_channel_count = bulk_msg.recipients.filter(channel='email').count()
    dashboard_channel_count = bulk_msg.recipients.filter(channel='dashboard').count()

    context = {
        'active_menu': 'communication',
        'sub_active': 'history',
        'bulk_msg': bulk_msg,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'channel_filter': channel_filter,
        'daily_remaining': daily_remaining,
        'total_recipients': total_recipients,
        'email_channel_count': email_channel_count,
        'dashboard_channel_count': dashboard_channel_count,
    }
    return render(request, 'communication/history_detail.html', context)


@admin_required
def bulk_message_status_api(request, id):
    """
    JSON polling endpoint for live history progress bar.
    """
    bulk_msg = get_object_or_404(BulkMessage, id=id)
    is_complete = bulk_msg.status in ['Sent', 'Partial', 'Failed', 'Stopped', 'Interrupted']

    return JsonResponse({
        'status': bulk_msg.status,
        'sent_count': bulk_msg.sent_count,
        'failed_count': bulk_msg.failed_count,
        'skipped_count': bulk_msg.skipped_count,
        'pending_count': bulk_msg.pending_count,
        'total_recipients': bulk_msg.total_recipients,
        'is_complete': is_complete,
        'stop_reason': bulk_msg.stop_reason
    })


@admin_required
@require_http_methods(["POST"])
def stop_sending_api(request, id):
    """
    Sets is_stopped=True on BulkMessage to halt sending between recipients/batches.
    """
    bulk_msg = get_object_or_404(BulkMessage, id=id)
    if bulk_msg.status != 'Sending':
        return JsonResponse({'status': 'error', 'message': f'Cannot stop message with status {bulk_msg.status}.'}, status=400)

    bulk_msg.is_stopped = True
    bulk_msg.status = 'Stopped'
    bulk_msg.stop_reason = 'Stopped by admin'
    bulk_msg.save(update_fields=['is_stopped', 'status', 'stop_reason'])

    admin_user = getattr(request, 'admin_user', None)
    admin_email = getattr(admin_user, 'email', None) or request.session.get('admin_name', 'Admin')

    log_activity(
        action_type="Communication Stopped",
        title=f"Broadcast '{bulk_msg.title}' stopped by admin",
        actor=admin_email
    )

    return JsonResponse({'status': 'success', 'message': 'Broadcast sending stopped successfully.'})


@admin_required
def export_recipients_csv_api(request, id):
    """
    Exports recipient log for a given BulkMessage as a downloadable CSV file.
    """
    bulk_msg = get_object_or_404(BulkMessage, id=id)
    recipients = bulk_msg.recipients.select_related('candidate_account', 'employer_account').all().order_by('-id')

    channel_filter = request.GET.get('channel', '').strip().lower()
    if channel_filter in ['email', 'dashboard']:
        recipients = recipients.filter(channel=channel_filter)

    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        recipients = recipients.filter(delivery_status=status_filter)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="broadcast_{bulk_msg.id}_recipients.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Recipient Name',
        'Account Type',
        'Email Address',
        'Phone Number',
        'Channel',
        'Delivery Status',
        'Error or Skip Reason',
        'Sent Timestamp',
        'Read Status',
        'Read Timestamp'
    ])

    for r in recipients:
        if r.candidate_account:
            name = r.candidate_account.full_name
            acc_type = "Candidate"
            email = r.candidate_account.email
            phone = r.candidate_account.phone
        elif r.employer_account:
            name = f"{r.employer_account.company_name} ({r.employer_account.contact_name})"
            acc_type = "Employer"
            email = r.employer_account.email
            phone = r.employer_account.phone
        else:
            name = "Unknown"
            acc_type = "Unknown"
            email = ""
            phone = ""

        writer.writerow([
            name,
            acc_type,
            email,
            phone,
            r.channel.upper(),
            r.delivery_status,
            r.error,
            r.sent_at.strftime('%Y-%m-%d %H:%M:%S') if r.sent_at else '',
            'Read' if r.is_read else 'Unread',
            r.read_at.strftime('%Y-%m-%d %H:%M:%S') if r.read_at else ''
        ])

    return response


@admin_required
@require_http_methods(["POST"])
def send_draft_api(request, id):
    bulk_msg = get_object_or_404(BulkMessage, id=id)
    if bulk_msg.status != 'Draft':
        return JsonResponse({'status': 'error', 'message': 'Message is not in Draft status.'}, status=400)

    updated = BulkMessage.objects.filter(id=id, status='Draft').update(status='Sending', is_stopped=False)
    if updated == 0:
        return JsonResponse({'status': 'error', 'message': 'Message is already sending.'}, status=409)

    bulk_msg.refresh_from_db()
    if not bulk_msg.recipients.exists():
        create_recipient_snapshots(bulk_msg)

    is_sync = request.POST.get('sync', False) or (request.content_type == 'application/json' and json.loads(request.body.decode('utf-8') or '{}').get('sync', False))
    admin_user = getattr(request, 'admin_user', None)
    admin_email = getattr(admin_user, 'email', None) or request.session.get('admin_name', 'Admin')

    queue_bulk_message_send(bulk_msg.id, actor_name=admin_email, sync=is_sync)
    log_activity(
        action_type="Communication Draft Dispatched",
        title=f"Draft '{bulk_msg.title}' dispatched",
        actor=admin_email
    )

    return JsonResponse({'status': 'success', 'message': 'Draft message queued and sending started!'})


@admin_required
@require_http_methods(["POST"])
def retry_failed_api(request, id):
    bulk_msg = get_object_or_404(BulkMessage, id=id)

    if bulk_msg.status == 'Sending':
        return JsonResponse({'status': 'error', 'message': 'Message is currently sending.'}, status=409)

    previous_status = bulk_msg.status
    updated = BulkMessage.objects.filter(id=id).exclude(status='Sending').update(status='Sending', stop_reason='', is_stopped=False)
    if updated == 0:
        return JsonResponse({'status': 'error', 'message': 'Message is currently sending.'}, status=409)

    eligible_recipients = bulk_msg.recipients.filter(delivery_status__in=['Pending', 'Failed'])
    count = eligible_recipients.count()

    if count == 0:
        BulkMessage.objects.filter(id=id).update(status=previous_status)
        return JsonResponse({'status': 'error', 'message': 'No pending or failed recipients found to retry.'}, status=400)

    eligible_recipients.update(delivery_status='Pending', error='')

    is_sync = request.POST.get('sync', False) or (request.content_type == 'application/json' and json.loads(request.body.decode('utf-8') or '{}').get('sync', False))
    admin_user = getattr(request, 'admin_user', None)
    admin_email = getattr(admin_user, 'email', None) or request.session.get('admin_name', 'Admin')

    queue_bulk_message_send(bulk_msg.id, actor_name=admin_email, sync=is_sync)
    log_activity(
        action_type="Communication Retry",
        title=f"Retried delivery for '{bulk_msg.title}' ({count} recipients)",
        actor=admin_email
    )

    return JsonResponse({'status': 'success', 'message': f'Retried / resumed delivery for {count} recipients.'})


# ==============================================================================
# TEMPLATES CRUD VIEWS & APIS
# ==============================================================================

@admin_required
def templates_view(request):
    templates_list = MessageTemplate.objects.all().order_by('-id')
    context = {
        'active_menu': 'communication',
        'sub_active': 'templates',
        'templates_list': templates_list,
    }
    return render(request, 'communication/templates.html', context)


@admin_required
def template_json_api(request, id):
    tpl = get_object_or_404(MessageTemplate, id=id)
    return JsonResponse({
        'status': 'success',
        'template': {
            'id': tpl.id,
            'name': tpl.name,
            'audience_type': tpl.audience_type,
            'subject': tpl.subject,
            'body': tpl.body,
            'is_active': tpl.is_active,
        }
    })


@admin_required
@require_http_methods(["POST"])
def template_save_api(request):
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST.dict()

        tpl_id = data.get('id')
        name = data.get('name', '').strip()
        audience_type = data.get('audience_type', 'candidate')
        subject = data.get('subject', '').strip()
        body = data.get('body', '').strip()
        is_active = str(data.get('is_active', 'true')).lower() in ['true', '1', 'yes', 'on']

        if not name or not subject or not body:
            return JsonResponse({'status': 'error', 'message': 'Name, subject, and body are required.'}, status=400)

        sanitized_body = sanitize_html(body)
        admin_user = getattr(request, 'admin_user', None)
        admin_email = getattr(admin_user, 'email', None) or request.session.get('admin_name', 'Admin')

        if tpl_id and str(tpl_id).isdigit():
            tpl = get_object_or_404(MessageTemplate, id=int(tpl_id))
            tpl.name = name
            tpl.audience_type = audience_type
            tpl.subject = subject
            tpl.body = sanitized_body
            tpl.is_active = is_active
            tpl.save()
            log_activity("Template Updated", f"Updated template '{name}'", actor=admin_email)
            return JsonResponse({'status': 'success', 'message': 'Template updated successfully.', 'id': tpl.id})
        else:
            tpl = MessageTemplate.objects.create(
                name=name,
                audience_type=audience_type,
                subject=subject,
                body=sanitized_body,
                is_active=is_active
            )
            log_activity("Template Created", f"Created template '{name}'", actor=admin_email)
            return JsonResponse({'status': 'success', 'message': 'Template created successfully.', 'id': tpl.id})
    except Exception as e:
        logger.warning(f"Error saving template: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@admin_required
@require_http_methods(["POST"])
def template_delete_api(request, id):
    tpl = get_object_or_404(MessageTemplate, id=id)
    tpl_name = tpl.name
    tpl.delete()
    admin_user = getattr(request, 'admin_user', None)
    admin_email = getattr(admin_user, 'email', None) or request.session.get('admin_name', 'Admin')
    log_activity("Template Deleted", f"Deleted template '{tpl_name}'", actor=admin_email)
    return JsonResponse({'status': 'success', 'message': f"Template '{tpl_name}' deleted successfully."})


# ==============================================================================
# DELIVERY SETTINGS PAGE
# ==============================================================================

@admin_required
def delivery_settings_view(request):
    is_gmail_configured = bool(getattr(settings, 'EMAIL_HOST_USER', '') and getattr(settings, 'EMAIL_HOST_PASSWORD', ''))
    daily_limit = getattr(settings, 'COMM_EMAIL_DAILY_LIMIT', 400)
    daily_sent = get_daily_sent_email_count()
    daily_remaining = max(0, daily_limit - daily_sent)

    raw_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
    masked_password = "•" * len(raw_password) if raw_password else "Not configured"

    context = {
        'active_menu': 'communication',
        'sub_active': 'settings',
        'backend_in_use': getattr(settings, 'EMAIL_BACKEND', ''),
        'email_host': getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com'),
        'email_port': getattr(settings, 'EMAIL_PORT', 587),
        'email_use_tls': getattr(settings, 'EMAIL_USE_TLS', True),
        'email_host_user': getattr(settings, 'EMAIL_HOST_USER', ''),
        'email_password_masked': masked_password,
        'default_from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', ''),
        'reply_to': getattr(settings, 'COMM_REPLY_TO', ''),
        'daily_limit': daily_limit,
        'daily_sent': daily_sent,
        'daily_remaining': daily_remaining,
        'batch_size': getattr(settings, 'COMM_EMAIL_BATCH_SIZE', 20),
        'delay_seconds': getattr(settings, 'COMM_EMAIL_DELAY_SECONDS', 1.0),
        'timeout_seconds': getattr(settings, 'EMAIL_TIMEOUT', 20),
        'is_gmail_configured': is_gmail_configured,
        'max_attachment_mb': getattr(settings, 'COMM_MAX_ATTACHMENT_MB', 5),
    }
    return render(request, 'communication/settings.html', context)


# Redirects for old notification URLs
@admin_required
def notifications_email_redirect(request):
    return redirect('/admin-panel/communication/compose/')

@admin_required
def notifications_send_redirect(request):
    return redirect('/admin-panel/communication/compose/')

@admin_required
def notifications_all_redirect(request):
    return redirect('/admin-panel/communication/history/')


# ==============================================================================
# CANDIDATE PORTAL INBOX VIEWS & APIs
# ==============================================================================

@candidate_required
def candidate_inbox_view(request):
    candidate = request.candidate_user
    messages_qs = MessageRecipient.objects.filter(
        candidate_account=candidate,
        channel='dashboard',
        delivery_status='Sent'
    ).select_related('bulk_message').order_by('-id')

    paginator = Paginator(messages_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    unread_count = MessageRecipient.objects.filter(
        candidate_account=candidate,
        channel='dashboard',
        is_read=False,
        delivery_status='Sent'
    ).count()

    context = {
        'candidate': candidate,
        'page_obj': page_obj,
        'unread_count': unread_count,
        'active_page': 'messages',
    }
    return render(request, 'candidate_portal/messages.html', context)


@candidate_required
def candidate_unread_count_api(request):
    candidate = request.candidate_user
    unread_count = MessageRecipient.objects.filter(
        candidate_account=candidate,
        channel='dashboard',
        is_read=False,
        delivery_status='Sent'
    ).count()
    return JsonResponse({'status': 'success', 'unread_count': unread_count})


@candidate_required
@require_http_methods(["POST"])
def candidate_mark_read_api(request, id):
    try:
        recipient = MessageRecipient.objects.get(
            id=id,
            candidate_account=request.candidate_user,
            channel='dashboard',
            delivery_status='Sent'
        )
    except MessageRecipient.DoesNotExist:
        raise Http404("Message not found")

    recipient.mark_as_read()

    rendered_subject = render_placeholders(recipient.bulk_message.subject, request.candidate_user, is_html=False)
    rendered_body = render_placeholders(recipient.bulk_message.body, request.candidate_user, is_html=True)

    attachment_url = recipient.bulk_message.attachment.url if recipient.bulk_message.attachment else None
    attachment_name = os.path.basename(recipient.bulk_message.attachment.name) if recipient.bulk_message.attachment else None

    return JsonResponse({
        'status': 'success',
        'id': recipient.id,
        'title': recipient.bulk_message.title,
        'subject': rendered_subject,
        'body': rendered_body,
        'attachment_url': attachment_url,
        'attachment_name': attachment_name,
        'created_at': recipient.bulk_message.created_at.strftime('%b %d, %Y %I:%M %p'),
        'is_read': recipient.is_read
    })


@candidate_required
@require_http_methods(["POST"])
def candidate_mark_all_read_api(request):
    candidate = request.candidate_user
    updated_count = MessageRecipient.objects.filter(
        candidate_account=candidate,
        channel='dashboard',
        delivery_status='Sent',
        is_read=False
    ).update(is_read=True, read_at=timezone.now())

    return JsonResponse({'status': 'success', 'updated_count': updated_count})


# ==============================================================================
# EMPLOYER PORTAL INBOX VIEWS & APIs
# ==============================================================================

@employer_required
def employer_inbox_view(request):
    employer = request.employer_user
    messages_qs = MessageRecipient.objects.filter(
        employer_account=employer,
        channel='dashboard',
        delivery_status='Sent'
    ).select_related('bulk_message').order_by('-id')

    paginator = Paginator(messages_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    unread_count = MessageRecipient.objects.filter(
        employer_account=employer,
        channel='dashboard',
        is_read=False,
        delivery_status='Sent'
    ).count()

    context = {
        'employer': employer,
        'page_obj': page_obj,
        'unread_count': unread_count,
        'active_page': 'messages',
    }
    return render(request, 'employer_portal/messages.html', context)


@employer_required
def employer_unread_count_api(request):
    employer = request.employer_user
    unread_count = MessageRecipient.objects.filter(
        employer_account=employer,
        channel='dashboard',
        is_read=False,
        delivery_status='Sent'
    ).count()
    return JsonResponse({'status': 'success', 'unread_count': unread_count})


@employer_required
@require_http_methods(["POST"])
def employer_mark_read_api(request, id):
    try:
        recipient = MessageRecipient.objects.get(
            id=id,
            employer_account=request.employer_user,
            channel='dashboard',
            delivery_status='Sent'
        )
    except MessageRecipient.DoesNotExist:
        raise Http404("Message not found")

    recipient.mark_as_read()

    rendered_subject = render_placeholders(recipient.bulk_message.subject, request.employer_user, is_html=False)
    rendered_body = render_placeholders(recipient.bulk_message.body, request.employer_user, is_html=True)

    attachment_url = recipient.bulk_message.attachment.url if recipient.bulk_message.attachment else None
    attachment_name = os.path.basename(recipient.bulk_message.attachment.name) if recipient.bulk_message.attachment else None

    return JsonResponse({
        'status': 'success',
        'id': recipient.id,
        'title': recipient.bulk_message.title,
        'subject': rendered_subject,
        'body': rendered_body,
        'attachment_url': attachment_url,
        'attachment_name': attachment_name,
        'created_at': recipient.bulk_message.created_at.strftime('%b %d, %Y %I:%M %p'),
        'is_read': recipient.is_read
    })


@employer_required
@require_http_methods(["POST"])
def employer_mark_all_read_api(request):
    employer = request.employer_user
    updated_count = MessageRecipient.objects.filter(
        employer_account=employer,
        channel='dashboard',
        delivery_status='Sent',
        is_read=False
    ).update(is_read=True, read_at=timezone.now())

    return JsonResponse({'status': 'success', 'updated_count': updated_count})
