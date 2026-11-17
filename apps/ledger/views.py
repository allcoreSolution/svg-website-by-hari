import csv
import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db import models
from django.utils import timezone
from django.core.paginator import Paginator

from django.conf import settings
from apps.accounts.auth_helpers import admin_required
from apps.ledger.models import PlacementCommission, LedgerEntry
from apps.ledger.services import (
    ensure_commission_for_joined, record_payment, update_salary,
    waive_commission, cancel_commission, parse_date_flexible
)


def num2words_indian(number):
    try:
        num = int(Decimal(str(number)))
    except Exception:
        return ""
    if num == 0:
        return "Zero Rupees Only"

    units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
             "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

    def _convert_less_than_thousand(n):
        if n == 0:
            return ""
        elif n < 20:
            return units[n]
        elif n < 100:
            return tens[n // 10] + (" " + units[n % 10] if n % 10 != 0 else "")
        else:
            return units[n // 100] + " Hundred" + (" " + _convert_less_than_thousand(n % 100) if n % 100 != 0 else "")

    res = ""
    crore = num // 10000000
    rem = num % 10000000
    lakh = rem // 100000
    rem = rem % 100000
    thousand = rem // 1000
    rem = rem % 1000

    if crore > 0:
        res += _convert_less_than_thousand(crore) + " Crore "
    if lakh > 0:
        res += _convert_less_than_thousand(lakh) + " Lakh "
    if thousand > 0:
        res += _convert_less_than_thousand(thousand) + " Thousand "
    if rem > 0:
        res += _convert_less_than_thousand(rem)

    return res.strip() + " Rupees Only"


def _get_filtered_commissions_qs(request):
    qs = PlacementCommission.objects.all().select_related('applicant', 'placement').prefetch_related('entries')

    status = request.GET.get('status', '').strip()
    company = request.GET.get('company', '').strip()
    payer_type = request.GET.get('payer_type', '').strip()
    joining_from = request.GET.get('joining_from', '').strip()
    joining_to = request.GET.get('joining_to', '').strip()
    q = request.GET.get('q', '').strip()
    salary_missing = request.GET.get('salary_missing', '').strip()

    if status:
        qs = qs.filter(status__iexact=status)
    if company:
        qs = qs.filter(company_name__icontains=company)
    if payer_type:
        qs = qs.filter(payer_type__iexact=payer_type)
    if salary_missing == '1' or salary_missing.lower() == 'true':
        qs = qs.filter(status='SALARY_MISSING')

    if joining_from:
        d_from = parse_date_flexible(joining_from)
        if d_from:
            qs = qs.filter(joining_date__gte=d_from)
    if joining_to:
        d_to = parse_date_flexible(joining_to)
        if d_to:
            qs = qs.filter(joining_date__lte=d_to)

    if q:
        qs = qs.filter(
            models.Q(candidate_name__icontains=q) |
            models.Q(company_name__icontains=q) |
            models.Q(position__icontains=q) |
            models.Q(notes__icontains=q)
        )

    return qs


@admin_required
def ledger_list_view(request):
    qs = _get_filtered_commissions_qs(request)

    # Calculate overall summary metrics
    all_commissions = PlacementCommission.objects.all().prefetch_related('entries')
    total_receivable = Decimal('0.00')
    total_received = Decimal('0.00')
    total_waived = Decimal('0.00')
    total_adjustments = Decimal('0.00')
    pending_count = 0
    salary_missing_count = 0

    now_date = timezone.now().date()
    month_start = now_date.replace(day=1)
    joinings_this_month_count = PlacementCommission.objects.filter(joining_date__gte=month_start).count()

    for comm in all_commissions:
        if comm.status != 'CANCELLED':
            total_receivable += comm.commission_amount
        total_received += comm.total_received
        total_waived += comm.total_waived
        total_adjustments += comm.total_adjustments
        if comm.balance > Decimal('0.00') and comm.status not in ['CANCELLED', 'WAIVED']:
            pending_count += 1
        if comm.status == 'SALARY_MISSING':
            salary_missing_count += 1

    outstanding_balance = total_receivable + total_adjustments - total_received - total_waived

    # Pagination
    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Unique companies for filter dropdown
    companies_list = PlacementCommission.objects.values_list('company_name', flat=True).distinct()

    context = {
        'active_menu': 'ledger',
        'sub_active': 'ledger',
        'commissions': page_obj,
        'page_obj': page_obj,
        'companies_list': [c for c in companies_list if c],
        'total_receivable': total_receivable,
        'total_received': total_received,
        'outstanding_balance': outstanding_balance,
        'pending_candidates_count': pending_count,
        'joinings_this_month_count': joinings_this_month_count,
        'salary_missing_count': salary_missing_count,
        'filters': {
            'status': request.GET.get('status', ''),
            'company': request.GET.get('company', ''),
            'payer_type': request.GET.get('payer_type', ''),
            'joining_from': request.GET.get('joining_from', ''),
            'joining_to': request.GET.get('joining_to', ''),
            'q': request.GET.get('q', ''),
            'salary_missing': request.GET.get('salary_missing', ''),
        }
    }
    return render(request, 'ledger/ledger_list.html', context)


@admin_required
def ledger_detail_view(request, id):
    commission = get_object_or_404(PlacementCommission, id=id)
    entries = commission.entries.all().order_by('id')

    context = {
        'active_menu': 'ledger',
        'commission': commission,
        'entries': entries,
    }
    return render(request, 'ledger/ledger_detail.html', context)


@admin_required
def payments_list_view(request):
    mode_filter = request.GET.get('mode', '').strip()
    company_filter = request.GET.get('company', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    q = request.GET.get('q', '').strip()
    active_tab = request.GET.get('tab', 'received')

    # Payments (CREDIT entries)
    credits_qs = LedgerEntry.objects.filter(entry_type='CREDIT').select_related('commission')

    if mode_filter:
        credits_qs = credits_qs.filter(payment_mode__iexact=mode_filter)
    if company_filter:
        credits_qs = credits_qs.filter(commission__company_name__icontains=company_filter)
    if date_from:
        d_from = parse_date_flexible(date_from)
        if d_from:
            credits_qs = credits_qs.filter(entry_date__gte=d_from)
    if date_to:
        d_to = parse_date_flexible(date_to)
        if d_to:
            credits_qs = credits_qs.filter(entry_date__lte=d_to)
    if q:
        credits_qs = credits_qs.filter(
            models.Q(commission__candidate_name__icontains=q) |
            models.Q(commission__company_name__icontains=q) |
            models.Q(receipt_no__icontains=q) |
            models.Q(reference_no__icontains=q)
        )

    # Fully Paid Commissions
    fully_paid_qs = PlacementCommission.objects.filter(status='PAID').select_related('applicant', 'placement').prefetch_related('entries')
    if company_filter:
        fully_paid_qs = fully_paid_qs.filter(company_name__icontains=company_filter)
    if q:
        fully_paid_qs = fully_paid_qs.filter(
            models.Q(candidate_name__icontains=q) |
            models.Q(company_name__icontains=q)
        )

    # Summary metrics
    all_credits = LedgerEntry.objects.filter(entry_type='CREDIT')
    total_received = all_credits.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

    now_date = timezone.now().date()
    month_start = now_date.replace(day=1)
    received_this_month = all_credits.filter(entry_date__gte=month_start).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

    total_payments_count = all_credits.count()
    fully_paid_count = PlacementCommission.objects.filter(status='PAID').count()

    paginator_credits = Paginator(credits_qs.order_by('-id'), 20)
    page_credits = paginator_credits.get_page(request.GET.get('page', 1))

    paginator_paid = Paginator(fully_paid_qs.order_by('-id'), 20)
    page_paid = paginator_paid.get_page(request.GET.get('page', 1))

    context = {
        'active_menu': 'payments',
        'sub_active': 'payments',
        'active_tab': active_tab,
        'payments': page_credits,
        'fully_paid_commissions': page_paid,
        'total_received': total_received,
        'received_this_month': received_this_month,
        'total_payments_count': total_payments_count,
        'fully_paid_count': fully_paid_count,
        'filters': {
            'mode': mode_filter,
            'company': company_filter,
            'date_from': date_from,
            'date_to': date_to,
            'q': q,
            'tab': active_tab,
        }
    }
    return render(request, 'ledger/payments_list.html', context)


@admin_required
def receipt_print_view(request, entry_id):
    entry = get_object_or_404(LedgerEntry, id=entry_id, entry_type='CREDIT')
    comm = entry.commission
    amount_words = num2words_indian(entry.amount)

    context = {
        'entry': entry,
        'commission': comm,
        'amount_words': amount_words,
        'site_url': getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
    }
    return render(request, 'ledger/receipt_print.html', context)


# ==========================================
# REST API ENDPOINTS (ADMIN ONLY, CSRF ENFORCED)
# ==========================================

@admin_required
def api_ledger_list(request):
    qs = _get_filtered_commissions_qs(request)
    data = []
    for c in qs[:100]:
        data.append({
            'id': c.id,
            'candidate_name': c.candidate_name,
            'company_name': c.company_name,
            'position': c.position,
            'joining_date': c.joining_date.strftime('%Y-%m-%d') if c.joining_date else '',
            'first_month_salary': float(c.first_month_salary),
            'commission_percent': float(c.commission_percent),
            'commission_amount': float(c.commission_amount),
            'received': float(c.total_received),
            'balance': float(c.balance),
            'payer_type': c.payer_type,
            'status': c.status,
            'due_date': c.due_date.strftime('%Y-%m-%d') if c.due_date else '',
            'salary_source': c.salary_source,
        })
    return JsonResponse({'status': 'success', 'data': data})


@admin_required
def api_ledger_detail(request, id):
    commission = get_object_or_404(PlacementCommission, id=id)
    entries = []
    for e in commission.entries.all().order_by('id'):
        entries.append({
            'id': e.id,
            'entry_type': e.entry_type,
            'amount': float(e.amount),
            'entry_date': e.entry_date.strftime('%Y-%m-%d') if e.entry_date else '',
            'payment_mode': e.payment_mode,
            'reference_no': e.reference_no,
            'remarks': e.remarks,
            'running_balance': float(e.running_balance),
            'receipt_no': e.receipt_no,
            'created_by': e.created_by,
            'created_at': e.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })

    return JsonResponse({
        'status': 'success',
        'commission': {
            'id': commission.id,
            'candidate_name': commission.candidate_name,
            'company_name': commission.company_name,
            'position': commission.position,
            'joining_date': commission.joining_date.strftime('%Y-%m-%d') if commission.joining_date else '',
            'first_month_salary': float(commission.first_month_salary),
            'commission_percent': float(commission.commission_percent),
            'commission_amount': float(commission.commission_amount),
            'received': float(commission.total_received),
            'balance': float(commission.balance),
            'payer_type': commission.payer_type,
            'status': commission.status,
            'salary_source': commission.salary_source,
            'notes': commission.notes,
        },
        'entries': entries
    })


@admin_required
@require_http_methods(["POST"])
def api_ledger_record_payment(request, id):
    commission = get_object_or_404(PlacementCommission, id=id)
    try:
        if request.content_type == 'application/json':
            body = json.loads(request.body.decode('utf-8'))
        else:
            body = request.POST.dict()

        amount_val = body.get('amount')
        if amount_val is None or str(amount_val).strip() == '':
            return JsonResponse({'status': 'error', 'message': 'Payment amount is required'}, status=400)

        amount = Decimal(str(amount_val))
        payment_date = body.get('entry_date') or body.get('payment_date')
        payment_mode = body.get('payment_mode', 'Bank Transfer')
        reference_no = body.get('reference_no', '').strip()
        remarks = body.get('remarks', '').strip()

        admin_name = request.session.get('admin_name', 'Admin')

        entry = record_payment(
            commission=commission,
            amount=amount,
            entry_date=payment_date,
            payment_mode=payment_mode,
            reference_no=reference_no,
            remarks=remarks,
            created_by=admin_name
        )

        return JsonResponse({
            'status': 'success',
            'message': f'Payment of ₹{entry.amount:,.2f} recorded successfully ({entry.receipt_no}).',
            'receipt_no': entry.receipt_no,
            'entry_id': entry.id,
            'new_balance': float(commission.balance),
            'commission_status': commission.status
        })
    except ValueError as ve:
        return JsonResponse({'status': 'error', 'message': str(ve)}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@admin_required
@require_http_methods(["POST"])
def api_ledger_update_salary(request, id):
    commission = get_object_or_404(PlacementCommission, id=id)
    try:
        if request.content_type == 'application/json':
            body = json.loads(request.body.decode('utf-8'))
        else:
            body = request.POST.dict()

        salary_val = body.get('first_month_salary') or body.get('salary')
        if salary_val is None or str(salary_val).strip() == '':
            return JsonResponse({'status': 'error', 'message': 'First month salary is required'}, status=400)

        new_salary = Decimal(str(salary_val))
        reason = body.get('reason', '').strip()
        admin_name = request.session.get('admin_name', 'Admin')

        comm = update_salary(
            commission=commission,
            new_first_month_salary=new_salary,
            reason=reason,
            created_by=admin_name
        )

        return JsonResponse({
            'status': 'success',
            'message': f'Salary updated to ₹{comm.first_month_salary:,.2f} (Commission: ₹{comm.commission_amount:,.2f}).',
            'first_month_salary': float(comm.first_month_salary),
            'commission_amount': float(comm.commission_amount),
            'new_balance': float(comm.balance),
            'commission_status': comm.status
        })
    except ValueError as ve:
        return JsonResponse({'status': 'error', 'message': str(ve)}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@admin_required
@require_http_methods(["POST"])
def api_ledger_waive(request, id):
    commission = get_object_or_404(PlacementCommission, id=id)
    try:
        if request.content_type == 'application/json':
            body = json.loads(request.body.decode('utf-8'))
        else:
            body = request.POST.dict()

        action = body.get('action', 'waive').lower()
        reason = body.get('reason', '').strip()
        if not reason:
            return JsonResponse({'status': 'error', 'message': 'Reason is required for waiver or cancellation'}, status=400)

        admin_name = request.session.get('admin_name', 'Admin')

        if action == 'cancel':
            cancel_commission(commission, reason, created_by=admin_name)
            msg = 'Commission cancelled successfully.'
        else:
            waive_commission(commission, reason, created_by=admin_name)
            msg = 'Commission balance waived successfully.'

        return JsonResponse({
            'status': 'success',
            'message': msg,
            'commission_status': commission.status
        })
    except ValueError as ve:
        return JsonResponse({'status': 'error', 'message': str(ve)}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@admin_required
@require_http_methods(["POST"])
def api_ledger_change_payer(request, id):
    commission = get_object_or_404(PlacementCommission, id=id)
    try:
        if request.content_type == 'application/json':
            body = json.loads(request.body.decode('utf-8'))
        else:
            body = request.POST.dict()

        payer_type = body.get('payer_type', 'Candidate').strip()
        if payer_type not in ['Candidate', 'Company']:
            return JsonResponse({'status': 'error', 'message': 'Invalid payer type'}, status=400)

        commission.payer_type = payer_type
        commission.save(update_fields=['payer_type', 'updated_at'])

        return JsonResponse({
            'status': 'success',
            'message': f'Payer updated to {payer_type}.',
            'payer_type': payer_type
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@admin_required
@require_http_methods(["POST"])
def api_ledger_sync(request):
    try:
        from apps.ledger.management.commands.sync_ledger import Command
        cmd = Command()
        cmd.handle()
        return JsonResponse({'status': 'success', 'message': 'Ledger backfill sync completed successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@admin_required
def api_ledger_payments(request):
    credits_qs = LedgerEntry.objects.filter(entry_type='CREDIT').select_related('commission').order_by('-id')
    data = []
    for e in credits_qs[:100]:
        data.append({
            'receipt_no': e.receipt_no,
            'date': e.entry_date.strftime('%Y-%m-%d') if e.entry_date else '',
            'candidate_name': e.commission.candidate_name,
            'company_name': e.commission.company_name,
            'amount': float(e.amount),
            'payment_mode': e.payment_mode,
            'reference_no': e.reference_no,
            'created_by': e.created_by,
            'commission_id': e.commission.id,
        })
    return JsonResponse({'status': 'success', 'payments': data})


@admin_required
def api_ledger_export_csv(request):
    export_type = request.GET.get('type', 'ledger')

    response = HttpResponse(content_type='text/csv')
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')

    if export_type == 'payments':
        response['Content-Disposition'] = f'attachment; filename="ledger_payments_{timestamp}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Receipt No', 'Date', 'Candidate', 'Company', 'Amount (INR)', 'Mode', 'Reference No', 'Received By'])

        credits_qs = LedgerEntry.objects.filter(entry_type='CREDIT').select_related('commission').order_by('-id')
        for e in credits_qs:
            writer.writerow([
                e.receipt_no,
                e.entry_date.strftime('%Y-%m-%d') if e.entry_date else '',
                e.commission.candidate_name,
                e.commission.company_name,
                f"{e.amount:.2f}",
                e.payment_mode,
                e.reference_no,
                e.created_by
            ])
    else:
        response['Content-Disposition'] = f'attachment; filename="ledger_commissions_{timestamp}.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Candidate Name', 'Company Name', 'Position', 'Joining Date', 'First Month Salary', 'Commission %', 'Commission Amount', 'Total Received', 'Outstanding Balance', 'Payer', 'Status', 'Due Date'])

        qs = _get_filtered_commissions_qs(request)
        for c in qs:
            writer.writerow([
                c.id,
                c.candidate_name,
                c.company_name,
                c.position,
                c.joining_date.strftime('%Y-%m-%d') if c.joining_date else '',
                f"{c.first_month_salary:.2f}",
                f"{c.commission_percent:.2f}",
                f"{c.commission_amount:.2f}",
                f"{c.total_received:.2f}",
                f"{c.balance:.2f}",
                c.payer_type,
                c.status,
                c.due_date.strftime('%Y-%m-%d') if c.due_date else ''
            ])

    return response
