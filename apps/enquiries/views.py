import json
import csv
import re
import hashlib
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings

from .models import ContactEnquiry, EnquiryRead, SubmissionThrottle, FollowUp, ActivityLog, log_activity
from .constants import (
    SPAM_PHRASES, BUSINESS_SERVICES, CANDIDATE_SERVICES,
    CONTACT_STATUS_CHOICES, COMPANY_STATUS_CHOICES, INTERNSHIP_STATUS_CHOICES,
    bucket_of, classify_enquiry_type
)
from .validators import (
    validate_name, validate_email, validate_phone,
    validate_service, validate_message, check_spam_phrases
)
from apps.accounts.auth_helpers import admin_required
from apps.companies.models import CompanyEnquiry
from apps.internships.models import InternshipEnquiry


def get_client_ip(request):
    if getattr(settings, 'TRUST_PROXY_HEADERS', False):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')


@require_http_methods(["POST"])
def contact(request):
    """Public contact enquiry submission with size limit, honeypot, rate limiting, and spam check."""
    # 1. Payload size limit check (20KB = 20480 bytes)
    if request.body and len(request.body) > 20480:
        return JsonResponse({
            "status": "error",
            "message": "Payload too large. Maximum allowed size is 20KB."
        }, status=413)

    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST

    # 2. Honeypot check
    honeypot = data.get("website_url") or data.get("website") or data.get("address_confirm")
    if honeypot and str(honeypot).strip():
        # Silent rejection for bots
        return JsonResponse({
            "status": "success",
            "message": "Thank you! Your enquiry has been received. We will contact you soon."
        })

    # 3. Rate limiting (DB-backed SubmissionThrottle)
    client_ip = get_client_ip(request)
    secret_key = getattr(settings, 'SECRET_KEY', 'default_secret')
    ip_hash = hashlib.sha256(f"{secret_key}:{client_ip}".encode('utf-8')).hexdigest()

    now = timezone.now()
    one_hour_ago = now - timedelta(hours=1)
    one_day_ago = now - timedelta(days=1)

    ip_hourly = SubmissionThrottle.objects.filter(kind='ip', key_hash=ip_hash, timestamp__gte=one_hour_ago).count()
    ip_daily = SubmissionThrottle.objects.filter(kind='ip', key_hash=ip_hash, timestamp__gte=one_day_ago).count()

    if ip_hourly >= 5 or ip_daily >= 15:
        return JsonResponse({
            "status": "error",
            "message": "Too many requests. Please try again later."
        }, status=429)

    # 4. Input validation
    raw_name = data.get("name") or data.get("full_name") or ""
    raw_email = data.get("email") or ""
    raw_phone = data.get("phone") or data.get("mobile") or ""
    raw_service = data.get("service") or "General Inquiry"
    raw_message = data.get("message") or ""

    v_name_ok, v_name = validate_name(raw_name)
    if not v_name_ok:
        return JsonResponse({"status": "error", "message": v_name}, status=400)

    v_email_ok, v_email = validate_email(raw_email)
    if not v_email_ok:
        return JsonResponse({"status": "error", "message": v_email}, status=400)

    v_phone_ok, v_phone = validate_phone(raw_phone)
    if not v_phone_ok:
        return JsonResponse({"status": "error", "message": v_phone}, status=400)

    _, v_service = validate_service(raw_service)
    v_msg_ok, v_message = validate_message(raw_message)
    if not v_msg_ok:
        return JsonResponse({"status": "error", "message": v_message}, status=400)

    # Throttle email & phone
    email_hash = hashlib.sha256(f"{secret_key}:{v_email}".encode('utf-8')).hexdigest()
    clean_digits = re.sub(r'\D', '', v_phone)
    phone_hash = hashlib.sha256(f"{secret_key}:{clean_digits}".encode('utf-8')).hexdigest()

    email_daily = SubmissionThrottle.objects.filter(kind='email', key_hash=email_hash, timestamp__gte=one_day_ago).count()
    phone_daily = SubmissionThrottle.objects.filter(kind='phone', key_hash=phone_hash, timestamp__gte=one_day_ago).count()

    if email_daily >= 3 or phone_daily >= 3:
        return JsonResponse({
            "status": "error",
            "message": "Too many requests from this email/phone. Please try again tomorrow."
        }, status=429)

    # 5. Duplicate submission guard (10 minutes)
    ten_mins_ago = now - timedelta(minutes=10)
    duplicate_exists = ContactEnquiry.objects.filter(
        email=v_email,
        message=v_message,
        created_at__gte=ten_mins_ago
    ).exists()

    if duplicate_exists:
        return JsonResponse({
            "status": "error",
            "message": "Duplicate submission detected. Please wait a few minutes before submitting again."
        }, status=400)

    # 6. Spam Heuristics
    is_spam = check_spam_phrases(f"{v_name} {v_email} {v_service} {v_message}")
    init_status = "Spam" if is_spam else "New"

    # 7. Classification Engine
    enq_type = classify_enquiry_type(v_service, v_message)

    # 8. Record throttles
    SubmissionThrottle.objects.create(kind='ip', key_hash=ip_hash)
    SubmissionThrottle.objects.create(kind='email', key_hash=email_hash)
    SubmissionThrottle.objects.create(kind='phone', key_hash=phone_hash)

    # 9. Save ContactEnquiry
    new_contact = ContactEnquiry.objects.create(
        name=v_name,
        email=v_email,
        phone=v_phone,
        service=v_service,
        message=v_message,
        enquiry_type=enq_type,
        status=init_status,
        notes=""
    )

    log_activity(
        "general",
        "General enquiry received",
        f"From {v_name} ({v_email}) regarding {v_service} [{enq_type}]"
    )

    return JsonResponse({
        "status": "success",
        "message": "Thank you! Your enquiry has been received. We will contact you soon."
    })


@require_http_methods(["GET"])
@admin_required
def get_contacts(request):
    q = request.GET.get("q", "").strip().lower()
    status_filter = request.GET.get("status", "").strip()
    enq_type_filter = request.GET.get("enquiry_type", "").strip()

    queryset = ContactEnquiry.objects.all().order_by('-id')
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    if enq_type_filter:
        queryset = queryset.filter(enquiry_type=enq_type_filter)

    read_ids = set(EnquiryRead.objects.filter(enquiry_type='contact').values_list('enquiry_id', flat=True))

    results = []
    for c in queryset:
        if q:
            match = (
                q in c.name.lower() or
                q in c.email.lower() or
                q in c.phone.lower() or
                q in c.service.lower() or
                q in (c.message or "").lower()
            )
            if not match:
                continue
        d = c.to_dict()
        d["is_read"] = c.id in read_ids
        results.append(d)

    return JsonResponse(results, safe=False)


@admin_required
def contact_detail(request, id):
    try:
        c = ContactEnquiry.objects.get(id=id)
    except ContactEnquiry.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Contact enquiry not found."}, status=404)

    actor_email = getattr(getattr(request, 'admin_user', None), 'email', '') or getattr(getattr(request, 'admin_user', None), 'username', '')

    if request.method == "GET":
        d = c.to_dict()
        d["is_read"] = EnquiryRead.objects.filter(enquiry_type='contact', enquiry_id=c.id).exists()
        return JsonResponse(d)

    elif request.method == "PUT":
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        if "name" in data:
            ok, val = validate_name(data["name"])
            if not ok: return JsonResponse({"status": "error", "message": val}, status=400)
            c.name = val
        if "email" in data:
            ok, val = validate_email(data["email"])
            if not ok: return JsonResponse({"status": "error", "message": val}, status=400)
            c.email = val
        if "phone" in data:
            ok, val = validate_phone(data["phone"])
            if not ok: return JsonResponse({"status": "error", "message": val}, status=400)
            c.phone = val
        if "service" in data: c.service = data["service"]
        if "message" in data: c.message = data["message"]
        if "status" in data: c.status = data["status"]
        if "notes" in data: c.notes = data["notes"]
        if "enquiry_type" in data and data["enquiry_type"]:
            c.enquiry_type = data["enquiry_type"]
        elif ("service" in data or "message" in data) and "enquiry_type" not in data:
            c.enquiry_type = classify_enquiry_type(c.service, c.message)

        c.save()
        log_activity(
            "general",
            "General enquiry updated",
            f"Updated contact #{c.id} ({c.name})",
            actor=actor_email
        )
        d = c.to_dict()
        d["is_read"] = EnquiryRead.objects.filter(enquiry_type='contact', enquiry_id=c.id).exists()
        return JsonResponse({"status": "success", "message": "Contact enquiry updated.", "contact": d})

    elif request.method == "DELETE":
        c_name = c.name
        c.delete()
        log_activity(
            "general",
            "General enquiry deleted",
            f"Deleted contact #{id} ({c_name})",
            actor=actor_email
        )
        return JsonResponse({"status": "success", "message": "Contact enquiry deleted successfully."})

    return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)


@require_http_methods(["GET"])
@admin_required
def api_enquiries_list(request):
    """Unified enquiries API with filtering, pagination, read state, and search."""
    type_param = request.GET.get("type", "all").strip().lower()
    read_param = request.GET.get("read", "all").strip().lower()
    bucket_param = request.GET.get("bucket", "").strip().lower()
    q_param = request.GET.get("q", "").strip().lower()
    from_param = request.GET.get("from", "").strip()
    to_param = request.GET.get("to", "").strip()

    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1
    try:
        page_size = int(request.GET.get("page_size", 25))
    except ValueError:
        page_size = 25
    if page_size > 100: page_size = 100

    read_records = set(EnquiryRead.objects.values_list('enquiry_type', 'enquiry_id'))

    items = []

    # 1. ContactEnquiry
    contacts = ContactEnquiry.objects.all().order_by('-id')
    for c in contacts:
        is_read = ('contact', c.id) in read_records
        bkt = bucket_of('contact', c.status)
        enq_kind = 'General' if c.enquiry_type != 'Candidate' else 'Candidate'
        items.append({
            'id': f"ENQ-{c.id}",
            'raw_id': c.id,
            'model': 'contact',
            'type_label': f"{enq_kind} Enquiry",
            'enquiry_type': enq_kind,
            'name': c.name,
            'title': c.name,
            'email': c.email,
            'phone': c.phone,
            'service_or_job': c.service,
            'company_name': '',
            'message': c.message or '',
            'notes': c.notes or '',
            'status': c.status or 'New',
            'bucket': bkt,
            'is_read': is_read,
            'created_at': c.created_at,
            'date_str': c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else ''
        })

    # 2. CompanyEnquiry
    companies = CompanyEnquiry.objects.all().order_by('-id')
    for comp in companies:
        is_read = ('company', comp.id) in read_records
        bkt = bucket_of('company', comp.status)
        items.append({
            'id': f"CMP-{comp.id}",
            'raw_id': comp.id,
            'model': 'company',
            'type_label': 'Company Enquiry',
            'enquiry_type': 'Company',
            'name': comp.recruiter_name,
            'title': comp.company_name,
            'email': comp.email,
            'phone': comp.phone,
            'service_or_job': comp.job_title or 'Requirement',
            'company_name': comp.company_name,
            'message': comp.message or '',
            'notes': comp.notes or '',
            'status': comp.status or 'New',
            'bucket': bkt,
            'is_read': is_read,
            'created_at': comp.created_at,
            'date_str': comp.created_at.strftime("%Y-%m-%d %H:%M:%S") if comp.created_at else ''
        })

    # 3. InternshipEnquiry
    internships = InternshipEnquiry.objects.all().order_by('-id')
    for ie in internships:
        is_read = ('internship', ie.id) in read_records
        bkt = bucket_of('internship', ie.status)
        items.append({
            'id': f"INT-{ie.id}",
            'raw_id': ie.id,
            'model': 'internship',
            'type_label': 'Internship Enquiry',
            'enquiry_type': 'Internship',
            'name': ie.full_name,
            'title': ie.full_name,
            'email': ie.email,
            'phone': ie.phone,
            'service_or_job': f"Internship ({ie.course_stream})" if ie.course_stream else "Internship",
            'company_name': ie.college or '',
            'message': ie.message or '',
            'notes': ie.notes or '',
            'status': ie.status or 'New',
            'bucket': bkt,
            'is_read': is_read,
            'created_at': ie.created_at,
            'date_str': ie.created_at.strftime("%Y-%m-%d %H:%M:%S") if ie.created_at else ''
        })

    # Apply Filters
    filtered = []
    for item in items:
        # Type filter
        if type_param == 'general' and not (item['model'] == 'contact' and item['enquiry_type'] == 'General'):
            continue
        if type_param == 'candidate' and not (item['model'] == 'contact' and item['enquiry_type'] == 'Candidate'):
            continue
        if type_param == 'company' and item['model'] != 'company':
            continue
        if type_param == 'internship' and item['model'] != 'internship':
            continue

        # Read filter
        if read_param in ['1', 'true', 'read'] and not item['is_read']:
            continue
        if read_param in ['0', 'false', 'unread'] and item['is_read']:
            continue

        # Bucket filter
        if bucket_param and item['bucket'] != bucket_param and not (bucket_param == 'spam' and item['status'].lower() == 'spam'):
            continue

        # Search filter
        if q_param:
            match = (
                q_param in item['name'].lower() or
                q_param in item['email'].lower() or
                q_param in item['phone'].lower() or
                q_param in item['company_name'].lower() or
                q_param in item['service_or_job'].lower() or
                q_param in item['message'].lower()
            )
            if not match:
                continue

        # Date filter
        if item['created_at']:
            item_date_str = item['created_at'].strftime("%Y-%m-%d")
            if from_param and item_date_str < from_param:
                continue
            if to_param and item_date_str > to_param:
                continue

        filtered.append(item)

    # Sort by created_at descending
    filtered.sort(key=lambda x: x['created_at'] or timezone.now(), reverse=True)

    total_count = len(filtered)
    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1
    if page < 1: page = 1

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_results = filtered[start_idx:end_idx]

    # Convert datetime to string for JSON serialization
    for r in paginated_results:
        r['created_at'] = r['date_str']

    return JsonResponse({
        "status": "success",
        "count": total_count,
        "pages": total_pages,
        "page": page,
        "page_size": page_size,
        "results": paginated_results
    })


@admin_required
def mark_enquiry_read(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)

    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST

    model_type = (data.get("type") or data.get("model") or "").strip().lower()
    raw_id = data.get("id") or data.get("raw_id")

    if not model_type or not raw_id:
        return JsonResponse({"status": "error", "message": "Type and ID are required."}, status=400)

    actor_email = getattr(getattr(request, 'admin_user', None), 'email', '') or getattr(getattr(request, 'admin_user', None), 'username', '')

    EnquiryRead.objects.get_or_create(
        enquiry_type=model_type,
        enquiry_id=int(raw_id),
        defaults={'read_by': actor_email}
    )

    return JsonResponse({"status": "success", "message": "Enquiry marked as read."})


@admin_required
def mark_enquiry_unread(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)

    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST

    model_type = (data.get("type") or data.get("model") or "").strip().lower()
    raw_id = data.get("id") or data.get("raw_id")

    if not model_type or not raw_id:
        return JsonResponse({"status": "error", "message": "Type and ID are required."}, status=400)

    EnquiryRead.objects.filter(enquiry_type=model_type, enquiry_id=int(raw_id)).delete()
    return JsonResponse({"status": "success", "message": "Enquiry marked as unread."})


@admin_required
def bulk_status_enquiry(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)

    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST

    items = data.get("items") or []
    new_status = (data.get("status") or "").strip()

    if not items or not new_status:
        return JsonResponse({"status": "error", "message": "Items list and status are required."}, status=400)

    actor_email = getattr(getattr(request, 'admin_user', None), 'email', '') or getattr(getattr(request, 'admin_user', None), 'username', '')
    updated_count = 0

    for item in items:
        model_type = (item.get("type") or item.get("model") or "").strip().lower()
        raw_id = item.get("id") or item.get("raw_id")
        if not model_type or not raw_id:
            continue

        if model_type == 'contact':
            ContactEnquiry.objects.filter(id=raw_id).update(status=new_status)
            updated_count += 1
        elif model_type == 'company':
            CompanyEnquiry.objects.filter(id=raw_id).update(status=new_status)
            updated_count += 1
        elif model_type == 'internship':
            InternshipEnquiry.objects.filter(id=raw_id).update(status=new_status)
            updated_count += 1

    log_activity(
        "general",
        "Bulk enquiry status update",
        f"Updated status of {updated_count} items to '{new_status}'",
        actor=actor_email
    )

    return JsonResponse({"status": "success", "message": f"{updated_count} enquiry status(es) updated."})


@admin_required
def mark_enquiry_spam(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)

    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST

    items = data.get("items")
    if not items:
        model_type = (data.get("type") or data.get("model") or "").strip().lower()
        raw_id = data.get("id") or data.get("raw_id")
        if model_type and raw_id:
            items = [{"type": model_type, "id": raw_id}]
        else:
            items = []

    if not items:
        return JsonResponse({"status": "error", "message": "Item(s) specification required."}, status=400)

    actor_email = getattr(getattr(request, 'admin_user', None), 'email', '') or getattr(getattr(request, 'admin_user', None), 'username', '')
    count = 0

    for item in items:
        m_type = (item.get("type") or item.get("model") or "").strip().lower()
        r_id = item.get("id") or item.get("raw_id")
        if m_type == 'contact':
            ContactEnquiry.objects.filter(id=r_id).update(status="Spam")
            count += 1
        elif m_type == 'company':
            CompanyEnquiry.objects.filter(id=r_id).update(status="Spam")
            count += 1
        elif m_type == 'internship':
            InternshipEnquiry.objects.filter(id=r_id).update(status="Spam")
            count += 1

    log_activity(
        "general",
        "Enquiry marked as spam",
        f"Marked {count} enquiry item(s) as Spam",
        actor=actor_email
    )

    return JsonResponse({"status": "success", "message": f"{count} enquiry item(s) marked as Spam."})


@admin_required
def restore_enquiry(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)

    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST

    items = data.get("items")
    if not items:
        model_type = (data.get("type") or data.get("model") or "").strip().lower()
        raw_id = data.get("id") or data.get("raw_id")
        if model_type and raw_id:
            items = [{"type": model_type, "id": raw_id}]
        else:
            items = []

    if not items:
        return JsonResponse({"status": "error", "message": "Item(s) specification required."}, status=400)

    actor_email = getattr(getattr(request, 'admin_user', None), 'email', '') or getattr(getattr(request, 'admin_user', None), 'username', '')
    count = 0

    for item in items:
        m_type = (item.get("type") or item.get("model") or "").strip().lower()
        r_id = item.get("id") or item.get("raw_id")
        if m_type == 'contact':
            ContactEnquiry.objects.filter(id=r_id).update(status="New")
            count += 1
        elif m_type == 'company':
            CompanyEnquiry.objects.filter(id=r_id).update(status="New")
            count += 1
        elif m_type == 'internship':
            InternshipEnquiry.objects.filter(id=r_id).update(status="New")
            count += 1

    log_activity(
        "general",
        "Enquiry restored from spam",
        f"Restored {count} enquiry item(s) to New",
        actor=actor_email
    )

    return JsonResponse({"status": "success", "message": f"{count} enquiry item(s) restored."})


@require_http_methods(["GET"])
@admin_required
def enquiry_counts_api(request):
    contact_qs = ContactEnquiry.objects.all()
    company_qs = CompanyEnquiry.objects.all()
    internship_qs = InternshipEnquiry.objects.all()

    total_contact = contact_qs.count()
    total_company = company_qs.count()
    total_internship = internship_qs.count()
    total = total_contact + total_company + total_internship

    general = contact_qs.filter(enquiry_type='General').count()
    candidate = contact_qs.filter(enquiry_type='Candidate').count()

    read_records = set(EnquiryRead.objects.values_list('enquiry_type', 'enquiry_id'))
    
    # Calculate read counts for each
    read_contacts = sum(1 for c in contact_qs if ('contact', c.id) in read_records)
    read_companies = sum(1 for c in company_qs if ('company', c.id) in read_records)
    read_internships = sum(1 for c in internship_qs if ('internship', c.id) in read_records)
    total_read = read_contacts + read_companies + read_internships
    total_unread = total - total_read

    resolved_count = 0
    spam_count = 0

    for c in contact_qs:
        if bucket_of('contact', c.status) == 'resolved': resolved_count += 1
        if c.status and c.status.lower() == 'spam': spam_count += 1
    for c in company_qs:
        if bucket_of('company', c.status) == 'resolved': resolved_count += 1
        if c.status and c.status.lower() == 'spam': spam_count += 1
    for c in internship_qs:
        if bucket_of('internship', c.status) == 'resolved': resolved_count += 1
        if c.status and c.status.lower() == 'spam': spam_count += 1

    return JsonResponse({
        "status": "success",
        "metrics": {
            "total": total,
            "general": general,
            "candidate": candidate,
            "company": total_company,
            "internship": total_internship,
            "read": total_read,
            "unread": total_unread,
            "resolved": resolved_count,
            "spam": spam_count
        }
    })


@require_http_methods(["GET"])
@admin_required
def export_enquiries_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="enquiries_export.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "ID", "Model", "Type Label", "Name", "Email", "Phone",
        "Service / Job Title", "Company / College", "Status", "Bucket",
        "Read", "Created At", "Message"
    ])

    read_records = set(EnquiryRead.objects.values_list('enquiry_type', 'enquiry_id'))

    def safe_val(val):
        s = str(val or "").strip()
        if s and s[0] in ('=', '+', '-', '@'):
            return "'" + s
        return s

    # Contacts
    for c in ContactEnquiry.objects.all().order_by('-id'):
        is_read = "Yes" if ('contact', c.id) in read_records else "No"
        bkt = bucket_of('contact', c.status)
        enq_label = f"{'General' if c.enquiry_type != 'Candidate' else 'Candidate'} Enquiry"
        created_str = c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else ""
        writer.writerow([
            safe_val(f"ENQ-{c.id}"), "contact", safe_val(enq_label), safe_val(c.name),
            safe_val(c.email), safe_val(c.phone), safe_val(c.service), "",
            safe_val(c.status), safe_val(bkt), is_read, safe_val(created_str), safe_val(c.message)
        ])

    # Companies
    for comp in CompanyEnquiry.objects.all().order_by('-id'):
        is_read = "Yes" if ('company', comp.id) in read_records else "No"
        bkt = bucket_of('company', comp.status)
        created_str = comp.created_at.strftime("%Y-%m-%d %H:%M:%S") if comp.created_at else ""
        writer.writerow([
            safe_val(f"CMP-{comp.id}"), "company", "Company Enquiry", safe_val(comp.recruiter_name),
            safe_val(comp.email), safe_val(comp.phone), safe_val(comp.job_title), safe_val(comp.company_name),
            safe_val(comp.status), safe_val(bkt), is_read, safe_val(created_str), safe_val(comp.message)
        ])

    # Internships
    for ie in InternshipEnquiry.objects.all().order_by('-id'):
        is_read = "Yes" if ('internship', ie.id) in read_records else "No"
        bkt = bucket_of('internship', ie.status)
        created_str = ie.created_at.strftime("%Y-%m-%d %H:%M:%S") if ie.created_at else ""
        writer.writerow([
            safe_val(f"INT-{ie.id}"), "internship", "Internship Enquiry", safe_val(ie.full_name),
            safe_val(ie.email), safe_val(ie.phone), safe_val(ie.course_stream), safe_val(ie.college),
            safe_val(ie.status), safe_val(bkt), is_read, safe_val(created_str), safe_val(ie.message)
        ])

    return response


@admin_required
def follow_ups_api(request):
    if request.method == "GET":
        followups = FollowUp.objects.all().order_by('-id')
        return JsonResponse([f.to_dict() for f in followups], safe=False)

    elif request.method == "POST":
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        if not data.get("contact_person"):
            return JsonResponse({"status": "error", "message": "Contact person is required."}, status=400)

        f = FollowUp.objects.create(
            contact_person=data.get("contact_person"),
            type=data.get("type", "Candidate"),
            phone_or_email=data.get("phone_or_email", ""),
            followup_date=data.get("followup_date", ""),
            remarks=data.get("remarks", ""),
            status=data.get("status", "Pending")
        )
        return JsonResponse({"status": "success", "message": "Follow-up scheduled.", "follow_up": f.to_dict()})

    return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)


@require_http_methods(["DELETE"])
@admin_required
def delete_follow_up(request, id):
    try:
        f = FollowUp.objects.get(id=id)
        f.delete()
    except FollowUp.DoesNotExist:
        pass
    return JsonResponse({"status": "success", "message": "Follow-up removed."})
