import os
import csv
import json
import uuid
import datetime
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q
from django.conf import settings
from django.utils import timezone

from apps.accounts.models import AdminUser, StaffMember, StaffSalaryPayment
from apps.accounts.auth_helpers import admin_required


def format_inr(number):
    """Format a number into Indian Rupee representation (e.g. ₹12,50,000 or ₹50,000)."""
    try:
        val = int(round(float(number)))
    except Exception:
        return f"₹{number}"
    
    is_neg = val < 0
    val = abs(val)
    s = str(val)
    
    if len(s) <= 3:
        res = s
    else:
        last3 = s[-3:]
        other = s[:-3]
        groups = []
        while len(other) > 2:
            groups.insert(0, other[-2:])
            other = other[:-2]
        if other:
            groups.insert(0, other)
        res = ",".join(groups) + "," + last3
        
    prefix = "-₹" if is_neg else "₹"
    return f"{prefix}{res}"


def format_lakhs(number):
    """Format number into Lakhs string like 6.5L or 4.0L."""
    try:
        val = float(number)
        if val >= 100000:
            lakhs = val / 100000
            return f"{lakhs:.1f}L"
        elif val >= 1000:
            k = val / 1000
            return f"{k:.1f}K"
        return str(int(val))
    except Exception:
        return "0"


def admin_staff_management_view(request):
    """
    Dedicated Staff Management Hub with Top KPI Cards,
    Interactive Visual Analytics (Staff by Profession, Salary by Dept, Payment Status),
    Filtered Staff Directory Table, and CRUD Modals.
    Strictly protected for Super Admin / Admin users only.
    """
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return redirect('/admin-panel/login/')
    try:
        admin_user = AdminUser.objects.get(id=admin_id, is_active=True)
    except AdminUser.DoesNotExist:
        request.session.flush()
        return redirect('/admin-panel/login/')

    # Filtering parameters
    dept_filter = (request.GET.get('dept') or '').strip()
    desig_filter = (request.GET.get('desig') or '').strip()
    status_filter = (request.GET.get('status') or '').strip()
    search_q = (request.GET.get('q') or '').strip()
    page_num = request.GET.get('page', 1)

    all_staff_qs = StaffMember.objects.all()

    # Calculate KPIs across entire staff database
    total_staff = all_staff_qs.count()
    active_staff = all_staff_qs.filter(status='Active').count()
    on_leave_staff = all_staff_qs.filter(status='On Leave').count()
    inactive_staff = all_staff_qs.filter(status='Inactive').count()

    agg = all_staff_qs.aggregate(
        tot_sal=Sum('monthly_salary'),
        tot_paid=Sum('total_paid'),
        tot_adv=Sum('advance_salary'),
        tot_pend=Sum('pending_salary')
    )
    total_monthly_salary = float(agg['tot_sal'] or 0)
    total_paid = float(agg['tot_paid'] or 0)
    total_advance = float(agg['tot_adv'] or 0)
    total_pending = float(agg['tot_pend'] or 0)

    paid_pct = round((total_paid / total_monthly_salary * 100), 1) if total_monthly_salary > 0 else 0
    adv_pct = round((total_advance / total_monthly_salary * 100), 1) if total_monthly_salary > 0 else 0
    pending_pct = max(0.0, round(100.0 - paid_pct - adv_pct, 1)) if total_monthly_salary > 0 else 0
    avg_salary = (total_monthly_salary / total_staff) if total_staff > 0 else 0
    pending_staff_count = all_staff_qs.filter(pending_salary__gt=0).count()

    # Analytics 1: Staff by Profession / Department (Donut Chart)
    palette = ['#2563EB', '#10B981', '#F59E0B', '#8B5CF6', '#06B6D4', '#EC4899', '#6366F1', '#14B8A6']
    dept_counts = list(all_staff_qs.values('department').annotate(count=Count('id')).order_by('-count'))
    chart_dept_labels = []
    chart_dept_data = []
    chart_dept_colors = []
    chart_dept_legends = []

    for idx, d in enumerate(dept_counts):
        d_name = d['department'] or 'General'
        cnt = d['count']
        pct = round((cnt / total_staff * 100), 1) if total_staff > 0 else 0
        color = palette[idx % len(palette)]
        chart_dept_labels.append(d_name)
        chart_dept_data.append(cnt)
        chart_dept_colors.append(color)
        chart_dept_legends.append({
            'name': d_name,
            'count': cnt,
            'pct': pct,
            'color': color
        })

    # Analytics 2: Salary by Department (Bar Chart)
    dept_sals = list(all_staff_qs.values('department').annotate(sal=Sum('monthly_salary')).order_by('-sal'))
    chart_sal_labels = []
    chart_sal_data = []
    chart_sal_formatted = []
    chart_sal_colors = []

    for idx, s in enumerate(dept_sals):
        d_name = s['department'] or 'General'
        val = float(s['sal'] or 0)
        color = palette[idx % len(palette)]
        chart_sal_labels.append(d_name)
        chart_sal_data.append(val)
        chart_sal_formatted.append(format_lakhs(val))
        chart_sal_colors.append(color)

    # Analytics 3: Payment Status Donut
    payment_chart_labels = ['Paid', 'Advance', 'Pending']
    payment_chart_data = [total_paid, total_advance, total_pending]
    payment_chart_colors = ['#10B981', '#3B82F6', '#F59E0B']

    chart_payload = {
        'total_staff': total_staff,
        'paid_pct': paid_pct,
        'adv_pct': adv_pct,
        'pending_pct': pending_pct,
        'dept_chart': {
            'labels': chart_dept_labels,
            'data': chart_dept_data,
            'colors': chart_dept_colors,
        },
        'sal_chart': {
            'labels': chart_sal_labels,
            'data': chart_sal_data,
            'formatted': chart_sal_formatted,
            'colors': chart_sal_colors,
        },
        'payment_chart': {
            'labels': payment_chart_labels,
            'data': payment_chart_data,
            'colors': payment_chart_colors,
            'paid_pct': paid_pct,
        }
    }

    # Filtered Queryset for the table
    qs = all_staff_qs.order_by('-id')
    if dept_filter:
        qs = qs.filter(department__iexact=dept_filter)
    if desig_filter:
        qs = qs.filter(designation__iexact=desig_filter)
    if status_filter:
        qs = qs.filter(status__iexact=status_filter)
    if search_q:
        qs = qs.filter(
            Q(full_name__icontains=search_q) |
            Q(email__icontains=search_q) |
            Q(phone__icontains=search_q) |
            Q(designation__icontains=search_q) |
            Q(department__icontains=search_q)
        )

    # Distinct dropdown options
    dept_options = sorted(list(set(all_staff_qs.values_list('department', flat=True).distinct())))
    desig_options = sorted(list(set(all_staff_qs.values_list('designation', flat=True).distinct())))

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(page_num)

    can_view_salary = bool(admin_user and ((admin_user.role and admin_user.role.is_super) or admin_user.has_perm('staff.view_salary')))

    if not can_view_salary:
        chart_payload['sal_chart']['data'] = [0] * len(chart_sal_labels)
        chart_payload['sal_chart']['formatted'] = ['••••••'] * len(chart_sal_labels)
        chart_payload['payment_chart']['data'] = [0, 0, 0]

    kpi_dict = {
        'total_staff': total_staff,
        'total_staff_fmt': str(total_staff),
        'total_monthly_salary': format_inr(total_monthly_salary) if can_view_salary else '••••••',
        'total_paid': format_inr(total_paid) if can_view_salary else '••••••',
        'total_advance': format_inr(total_advance) if can_view_salary else '••••••',
        'total_pending': format_inr(total_pending) if can_view_salary else '••••••',
        'active_staff': active_staff,
        'on_leave_staff': on_leave_staff,
        'inactive_staff': inactive_staff,
        'paid_pct': paid_pct if can_view_salary else 0,
        'adv_pct': adv_pct if can_view_salary else 0,
        'pending_pct': pending_pct if can_view_salary else 0,
        'avg_salary_fmt': format_inr(avg_salary) if can_view_salary else '••••••',
        'pending_staff_count': pending_staff_count,
    }

    context = {
        'admin_user': admin_user,
        'active_menu': 'staff',
        'page_obj': page_obj,
        'staff_list': page_obj.object_list,
        'total_filtered': qs.count(),
        'can_view_salary': can_view_salary,
        'kpi': kpi_dict,
        'chart_dept_legends': chart_dept_legends,
        'dept_options': dept_options,
        'desig_options': desig_options,
        'dept_filter': dept_filter,
        'desig_filter': desig_filter,
        'status_filter': status_filter,
        'search_q': search_q,
        'chart_payload_json': json.dumps(chart_payload),
    }
    return render(request, 'dashboard/staff_management_module.html', context)


# =========================================================================
# ADMIN STAFF CRUD & PAYMENT APIS (STRICTLY ADMIN PROTECTED)
# =========================================================================

@admin_required
@require_http_methods(["POST"])
def api_admin_staff_add(request):
    """Add a new staff member with optional photo upload."""
    try:
        data = request.POST.dict() if request.POST else json.loads(request.body.decode('utf-8'))
        
        full_name = (data.get('full_name') or '').strip()
        if not full_name:
            return JsonResponse({'status': 'error', 'message': 'Staff full name is required.'}, status=400)
            
        email = (data.get('email') or '').strip().lower()
        phone = (data.get('phone') or '').strip()
        department = (data.get('department') or 'IT').strip()
        designation = (data.get('designation') or 'Executive').strip()
        
        try:
            monthly_salary = Decimal(str(data.get('monthly_salary') or 0))
        except Exception:
            monthly_salary = Decimal('0.00')

        try:
            total_paid = Decimal(str(data.get('total_paid') or 0))
        except Exception:
            total_paid = Decimal('0.00')

        try:
            advance_salary = Decimal(str(data.get('advance_salary') or 0))
        except Exception:
            advance_salary = Decimal('0.00')

        try:
            p_raw = data.get('pending_salary')
            pending_salary = Decimal(str(p_raw)) if p_raw not in [None, ''] else None
        except Exception:
            pending_salary = None

        status = data.get('status') or 'Active'
        if status not in ['Active', 'On Leave', 'Inactive']:
            status = 'Active'

        joining_date = None
        j_str = data.get('joining_date')
        if j_str:
            try:
                joining_date = datetime.datetime.strptime(j_str, '%Y-%m-%d').date()
            except Exception:
                pass

        photo_url = ''
        if 'photo' in request.FILES:
            photo_file = request.FILES['photo']
            ext = os.path.splitext(photo_file.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.webp', '.svg']:
                ext = '.jpg'
            fname = f"staff_{uuid.uuid4().hex[:12]}{ext}"
            save_dir = os.path.join(settings.MEDIA_ROOT, 'staff_photos')
            os.makedirs(save_dir, exist_ok=True)
            with open(os.path.join(save_dir, fname), 'wb+') as dest:
                for chunk in photo_file.chunks():
                    dest.write(chunk)
            photo_url = f"{settings.MEDIA_URL}staff_photos/{fname}"

        staff = StaffMember(
            full_name=full_name,
            email=email,
            phone=phone,
            photo=photo_url,
            department=department,
            designation=designation,
            monthly_salary=monthly_salary,
            total_paid=total_paid,
            advance_salary=advance_salary,
            pending_salary=pending_salary,
            status=status,
            joining_date=joining_date,
            bank_name=(data.get('bank_name') or '').strip(),
            bank_account_no=(data.get('bank_account_no') or '').strip(),
            ifsc_code=(data.get('ifsc_code') or '').strip(),
            pan_number=(data.get('pan_number') or '').strip(),
            aadhaar_number=(data.get('aadhaar_number') or '').strip(),
            address=(data.get('address') or '').strip(),
            notes=(data.get('notes') or '').strip(),
        )
        staff.save()

        # If initial paid or advance was set, log payments
        if total_paid > 0:
            StaffSalaryPayment.objects.create(
                staff=staff,
                amount=total_paid,
                payment_type='salary',
                payment_date=timezone.now().date(),
                payment_mode='Bank Transfer',
                reference_id=f"INIT-SAL-{staff.id}",
                remarks='Initial recorded salary'
            )
        if advance_salary > 0:
            StaffSalaryPayment.objects.create(
                staff=staff,
                amount=advance_salary,
                payment_type='advance',
                payment_date=timezone.now().date(),
                payment_mode='UPI',
                reference_id=f"INIT-ADV-{staff.id}",
                remarks='Initial recorded advance'
            )

        return JsonResponse({
            'status': 'success',
            'message': f"Staff member '{staff.full_name}' added successfully.",
            'staff': staff.to_dict()
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f"Failed to add staff: {str(e)}"}, status=500)


@admin_required
@require_http_methods(["POST"])
def api_admin_staff_update(request, staff_id):
    """Update an existing staff member with full support for salaries, paid, advance, and pending."""
    try:
        staff = get_object_or_404(StaffMember, id=staff_id)
        data = request.POST.dict() if request.POST else json.loads(request.body.decode('utf-8'))

        def clean_val(key):
            if key in data:
                val = data.get(key)
                return str(val).strip() if val is not None else ''
            return None

        def clean_decimal(key):
            if key in data:
                raw = str(data.get(key) or '').replace(',', '').strip()
                if raw == '':
                    return Decimal('0.00')
                try:
                    return Decimal(raw)
                except Exception:
                    return Decimal('0.00')
            return None

        fn = clean_val('full_name')
        if fn:
            staff.full_name = fn

        em = clean_val('email')
        if em is not None:
            staff.email = em.lower()

        ph = clean_val('phone')
        if ph is not None:
            staff.phone = ph

        dept = clean_val('department')
        if dept:
            staff.department = dept

        desig = clean_val('designation')
        if desig:
            staff.designation = desig

        msal = clean_decimal('monthly_salary')
        if msal is not None:
            staff.monthly_salary = msal

        tpaid = clean_decimal('total_paid')
        if tpaid is not None:
            staff.total_paid = tpaid

        adv = clean_decimal('advance_salary')
        if adv is not None:
            staff.advance_salary = adv

        pend = clean_decimal('pending_salary')
        if pend is not None:
            staff.pending_salary = pend
        else:
            # Auto-calculate pending if not explicitly passed
            rem = staff.monthly_salary - (staff.total_paid + staff.advance_salary)
            staff.pending_salary = max(Decimal('0.00'), rem)

        st = clean_val('status')
        if st in ['Active', 'On Leave', 'Inactive']:
            staff.status = st

        j_str = clean_val('joining_date')
        if j_str is not None:
            if j_str:
                try:
                    staff.joining_date = datetime.datetime.strptime(j_str, '%Y-%m-%d').date()
                except Exception:
                    pass
            else:
                staff.joining_date = None

        bn = clean_val('bank_name')
        if bn is not None:
            staff.bank_name = bn

        acc = clean_val('bank_account_no')
        if acc is not None:
            staff.bank_account_no = acc

        ifsc = clean_val('ifsc_code')
        if ifsc is not None:
            staff.ifsc_code = ifsc

        pan = clean_val('pan_number')
        if pan is not None:
            staff.pan_number = pan

        aadh = clean_val('aadhaar_number')
        if aadh is not None:
            staff.aadhaar_number = aadh

        addr = clean_val('address')
        if addr is not None:
            staff.address = addr

        notes = clean_val('notes')
        if notes is not None:
            staff.notes = notes

        # Handle new photo upload
        if 'photo' in request.FILES:
            photo_file = request.FILES['photo']
            ext = os.path.splitext(photo_file.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.webp', '.svg']:
                ext = '.jpg'
            fname = f"staff_{uuid.uuid4().hex[:12]}{ext}"
            save_dir = os.path.join(settings.MEDIA_ROOT, 'staff_photos')
            os.makedirs(save_dir, exist_ok=True)
            with open(os.path.join(save_dir, fname), 'wb+') as dest:
                for chunk in photo_file.chunks():
                    dest.write(chunk)
            staff.photo = f"{settings.MEDIA_URL}staff_photos/{fname}"

        staff.save()

        return JsonResponse({
            'status': 'success',
            'message': f"Staff '{staff.full_name}' updated successfully.",
            'staff': staff.to_dict()
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f"Update failed: {str(e)}"}, status=500)


@admin_required
def api_admin_staff_delete(request, staff_id):
    """Remove a staff member from the database."""
    try:
        staff = get_object_or_404(StaffMember, id=staff_id)
        name = staff.full_name
        staff.delete()
        return JsonResponse({
            'status': 'success',
            'message': f"Staff member '{name}' has been deleted successfully."
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f"Delete failed: {str(e)}"}, status=500)


@admin_required
def api_admin_staff_detail(request, staff_id):
    """Get full details of a staff member along with payment transactions history, masking confidential data if unauthorized."""
    try:
        staff = get_object_or_404(StaffMember, id=staff_id)
        admin_user = getattr(request, 'admin_user', None)
        if not admin_user and request.session.get('admin_id'):
            from apps.accounts.models import AdminUser
            admin_user = AdminUser.objects.filter(id=request.session.get('admin_id'), is_active=True).select_related('role').first()

        can_view_salary = bool(admin_user and ((admin_user.role and admin_user.role.is_super) or admin_user.has_perm('staff.view_salary')))

        data = staff.to_dict()

        if can_view_salary:
            payments = staff.payments.all().order_by('-payment_date', '-id')
            payment_list = []
            for p in payments:
                payment_list.append({
                    'id': p.id,
                    'amount': float(p.amount),
                    'amount_fmt': format_inr(p.amount),
                    'payment_type': p.payment_type,
                    'payment_date': p.payment_date.strftime('%d %b %Y') if p.payment_date else '',
                    'payment_mode': p.payment_mode,
                    'reference_id': p.reference_id,
                    'remarks': p.remarks,
                })
            data['monthly_salary_fmt'] = format_inr(staff.monthly_salary)
            data['total_paid_fmt'] = format_inr(staff.total_paid)
            data['advance_salary_fmt'] = format_inr(staff.advance_salary)
            data['pending_salary_fmt'] = format_inr(staff.pending_salary)
            data['payments'] = payment_list
        else:
            # Mask sensitive salary, bank, PAN, and Aadhaar numbers
            data['monthly_salary'] = 0.0
            data['total_paid'] = 0.0
            data['advance_salary'] = 0.0
            data['pending_salary'] = 0.0
            data['monthly_salary_fmt'] = '••••••'
            data['total_paid_fmt'] = '••••••'
            data['advance_salary_fmt'] = '••••••'
            data['pending_salary_fmt'] = '••••••'
            data['bank_name'] = '••••••'
            data['bank_account_no'] = '••••••••'
            data['ifsc_code'] = '••••••••'
            data['pan_number'] = '••••••••'
            data['aadhaar_number'] = '••••••••'
            data['payments'] = []

        return JsonResponse({'status': 'success', 'staff': data, 'can_view_salary': can_view_salary})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@admin_required
@require_http_methods(["POST"])
def api_admin_staff_record_payment(request, staff_id):
    """Record a salary or advance payment for staff, updating totals and adding a transaction."""
    try:
        admin_user = getattr(request, 'admin_user', None)
        if not admin_user and request.session.get('admin_id'):
            from apps.accounts.models import AdminUser
            admin_user = AdminUser.objects.filter(id=request.session.get('admin_id'), is_active=True).select_related('role').first()

        can_view_salary = bool(admin_user and ((admin_user.role and admin_user.role.is_super) or admin_user.has_perm('staff.view_salary')))
        if not can_view_salary:
            return JsonResponse({'status': 'error', 'message': 'Permission denied. Required privilege: staff.view_salary'}, status=403)
        staff = get_object_or_404(StaffMember, id=staff_id)
        data = json.loads(request.body.decode('utf-8')) if request.content_type == 'application/json' else request.POST.dict()

        amount_raw = data.get('amount')
        try:
            amount = Decimal(str(amount_raw))
            if amount <= 0:
                raise ValueError("Amount must be positive.")
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Valid payment amount is required.'}, status=400)

        payment_type = data.get('payment_type', 'salary') # 'salary' or 'advance' or 'bonus'
        payment_mode = data.get('payment_mode', 'Bank Transfer')
        reference_id = (data.get('reference_id') or '').strip()
        remarks = (data.get('remarks') or '').strip()

        p_date = timezone.now().date()
        date_str = data.get('payment_date')
        if date_str:
            try:
                p_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            except Exception:
                pass

        # Update staff totals
        if payment_type == 'advance':
            staff.advance_salary = staff.advance_salary + amount
        elif payment_type == 'salary':
            staff.total_paid = staff.total_paid + amount
        # Recalculate remaining pending salary
        rem = staff.monthly_salary - (staff.total_paid + staff.advance_salary)
        staff.pending_salary = max(Decimal('0.00'), rem)
        staff.save()

        # Create record
        payment = StaffSalaryPayment.objects.create(
            staff=staff,
            amount=amount,
            payment_type=payment_type,
            payment_date=p_date,
            payment_mode=payment_mode,
            reference_id=reference_id,
            remarks=remarks
        )

        return JsonResponse({
            'status': 'success',
            'message': f"Recorded {payment_type.title()} of {format_inr(amount)} for {staff.full_name}.",
            'staff': staff.to_dict()
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f"Payment failed: {str(e)}"}, status=500)


@admin_required
def api_admin_staff_export(request):
    """Export staff list as CSV spreadsheet."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="staff_directory_{timestamp}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Full Name', 'Department', 'Designation', 'Status',
        'Monthly Salary (INR)', 'Total Paid (INR)', 'Advance Salary (INR)', 'Pending (INR)',
        'Phone', 'Email', 'Joining Date', 'Bank Name', 'Account No', 'IFSC Code', 'Address'
    ])

    for s in StaffMember.objects.all().order_by('id'):
        writer.writerow([
            s.id,
            s.full_name,
            s.department,
            s.designation,
            s.status,
            float(s.monthly_salary),
            float(s.total_paid),
            float(s.advance_salary),
            float(s.pending_salary),
            s.phone or '',
            s.email or '',
            s.joining_date.strftime('%Y-%m-%d') if s.joining_date else '',
            s.bank_name or '',
            s.bank_account_no or '',
            s.ifsc_code or '',
            s.address or ''
        ])

    return response

