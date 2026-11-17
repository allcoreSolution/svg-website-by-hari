import re
import logging
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date, timedelta
from django.db import transaction, models
from django.conf import settings
from django.utils import timezone

from apps.ledger.models import PlacementCommission, LedgerEntry

logger = logging.getLogger(__name__)


def parse_salary_to_monthly(text):
    """
    Parses a free-text salary string into a monthly salary Decimal and a descriptive source note.
    Returns: (monthly_salary: Decimal | None, source_note: str)
    Never raises an exception.
    """
    if not text or not str(text).strip():
        return None, "Salary text empty"

    raw = str(text).strip()
    s_lower = raw.lower()

    # Remove currency symbols and clean up range delimiters
    cleaned = re.sub(r'[₹$$,]', '', raw)
    cleaned_lower = cleaned.lower()

    # Range handling e.g. "4 LPA - 5 LPA", "30000 - 40000", "4 to 5 lakh"
    # Look for range separator
    range_match = re.split(r'\s*(?:-|to)\s*', cleaned_lower)
    is_range = len(range_match) > 1 and any(c.isdigit() for c in range_match[0]) and any(c.isdigit() for c in range_match[1])

    target_text = range_match[0] if is_range else cleaned_lower
    range_note = f" (Parsed from range '{raw}', lower bound used)" if is_range else ""

    # Unit indicators
    is_monthly = any(u in s_lower for u in ['month', 'pm', 'p.m', 'monthly', 'per month', '/month', '/m'])
    is_annual = any(u in s_lower for u in ['lpa', 'lakh', 'lac', 'annum', 'p.a', 'pa', 'yearly', 'ctc', 'annual', 'per annum'])

    # Helper to parse number with k/lakh multipliers
    def extract_number_value(val_str):
        val_str = val_str.strip()
        # Check "25k" -> 25000
        k_match = re.search(r'([\d.]+)\s*k\b', val_str)
        if k_match:
            try:
                return Decimal(k_match.group(1)) * Decimal('1000')
            except Exception:
                pass

        # Check "3.6 lakh" or "3.6 lpa"
        lakh_match = re.search(r'([\d.]+)\s*(?:lakh|lac|lpa)\b', val_str)
        if lakh_match:
            try:
                return Decimal(lakh_match.group(1)) * Decimal('100000')
            except Exception:
                pass

        # Plain number extract
        nums = re.findall(r'[\d.]+', val_str)
        if nums:
            try:
                return Decimal(nums[0])
            except Exception:
                pass
        return None

    num_val = extract_number_value(target_text)
    if num_val is None or num_val <= Decimal('0'):
        return None, f"Could not parse numeric salary from '{raw}'"

    # Monthly calculation logic
    if is_monthly:
        monthly = num_val
        note = f"Parsed as monthly salary from '{raw}'{range_note}"
    elif is_annual:
        # If numeric value was e.g. 6 (from "6 LPA"), multiply by 100,000 if num_val < 100
        if num_val < Decimal('100'):
            annual = num_val * Decimal('100000')
        else:
            annual = num_val
        monthly = annual / Decimal('12')
        note = f"Parsed from annual package '{raw}' ({annual:,.2f}/12){range_note}"
    elif num_val >= Decimal('100000'):
        # Large number without unit assumed annual
        annual = num_val
        monthly = annual / Decimal('12')
        note = f"Parsed as annual salary >= 100,000 from '{raw}' ({annual:,.2f}/12){range_note}"
    else:
        # Ambiguous smaller number e.g. "25000"
        # If < 200 (e.g. "4 - 5"), might be LPA without "LPA"
        if num_val < Decimal('100'):
            annual = num_val * Decimal('100000')
            monthly = annual / Decimal('12')
            note = f"Ambiguous figure '{raw}' treated as annual LPA ({annual:,.2f}/12){range_note}"
        else:
            monthly = num_val
            note = f"Ambiguous figure '{raw}' treated as monthly salary{range_note}"

    # Round to 2 decimal places
    monthly_rounded = monthly.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return monthly_rounded, note


def parse_date_flexible(val):
    if not val:
        return None
    if isinstance(val, date):
        return val
    if isinstance(val, datetime):
        return val.date()

    val_str = str(val).strip()
    if not val_str:
        return None

    formats = [
        '%Y-%m-%d',
        '%d-%m-%Y',
        '%d/%m/%Y',
        '%Y/%m/%d',
        '%d %b %Y',
        '%d %B %Y',
        '%Y-%m-%dT%H:%M:%S',
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(val_str, fmt)
            return dt.date()
        except ValueError:
            pass

    return None


def generate_receipt_number():
    year = timezone.now().year
    prefix = f"RCPT-{year}-"
    with transaction.atomic():
        last_entry = LedgerEntry.objects.filter(
            receipt_no__startswith=prefix
        ).select_for_update().order_by('-id').first()

        if last_entry and last_entry.receipt_no:
            try:
                num = int(last_entry.receipt_no.split('-')[-1]) + 1
            except Exception:
                num = 1
        else:
            num = 1

        return f"{prefix}{num:04d}"


def ensure_commission_for_joined(applicant=None, placement=None, created_by='System'):
    """
    Creates or retrieves a PlacementCommission for a joined candidate.
    Idempotent: Safe to call multiple times.
    """
    if not applicant and not placement:
        raise ValueError("Either applicant or placement must be provided")

    with transaction.atomic():
        # Search for existing commission
        commission = None
        if placement:
            commission = PlacementCommission.objects.filter(placement=placement).first()

        if not commission and applicant:
            commission = PlacementCommission.objects.filter(applicant=applicant).first()

        if commission:
            return commission

        # Determine snapshot fields
        candidate_name = ""
        company_name = ""
        position = ""
        joining_date_val = None

        if placement:
            candidate_name = placement.candidate_name or (placement.applicant.full_name if placement.applicant else "Candidate")
            company_name = placement.company_name or "Sky Vision Client"
            position = placement.position or ""
            joining_date_val = parse_date_flexible(placement.joining_date)
            if not applicant and placement.applicant:
                applicant = placement.applicant

        if applicant:
            if not candidate_name:
                candidate_name = applicant.full_name or "Candidate"
            if not company_name:
                if applicant.job and (applicant.job.employer_name or applicant.job.company_name):
                    company_name = applicant.job.employer_name or applicant.job.company_name
                elif applicant.company:
                    company_name = applicant.company.name
                else:
                    company_name = applicant.current_company or "Sky Vision Client"
            if not position:
                position = applicant.job_title or (applicant.job.title if applicant.job else "")
            if not joining_date_val:
                joining_date_val = parse_date_flexible(getattr(applicant, 'joining_date', None))

        if not joining_date_val:
            joining_date_val = timezone.now().date()

        # Resolve salary text priority: Placement.package -> JobOffer.offered_ctc -> Applicant salaries
        salary_text = ""
        if placement and placement.package:
            salary_text = placement.package
        elif applicant:
            from apps.placements.models import JobOffer
            offer = JobOffer.objects.filter(applicant=applicant).order_by('-id').first()
            if offer and offer.offered_ctc:
                salary_text = offer.offered_ctc
            elif applicant.expected_salary:
                salary_text = applicant.expected_salary
            elif applicant.current_salary:
                salary_text = applicant.current_salary

        monthly_salary, note = parse_salary_to_monthly(salary_text)

        default_percent = Decimal(str(getattr(settings, 'LEDGER_COMMISSION_PERCENT', 50)))
        due_days = getattr(settings, 'LEDGER_DEFAULT_DUE_DAYS', 30)
        due_date_val = joining_date_val + timedelta(days=due_days)

        if monthly_salary and monthly_salary > Decimal('0.00'):
            first_month_salary = monthly_salary
            commission_amount = (first_month_salary * (default_percent / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            initial_status = 'PENDING'
            salary_source_val = note
        else:
            first_month_salary = Decimal('0.00')
            commission_amount = Decimal('0.00')
            initial_status = 'SALARY_MISSING'
            salary_source_val = note or "Salary missing or unparseable"

        commission = PlacementCommission.objects.create(
            applicant=applicant,
            placement=placement,
            candidate_name=candidate_name,
            company_name=company_name,
            position=position,
            joining_date=joining_date_val,
            first_month_salary=first_month_salary,
            commission_percent=default_percent,
            commission_amount=commission_amount,
            payer_type='Candidate',
            due_date=due_date_val,
            status=initial_status,
            salary_source=salary_source_val,
            created_by=str(created_by)
        )

        # Create initial DEBIT ledger entry if commission > 0
        if commission_amount > Decimal('0.00'):
            LedgerEntry.objects.create(
                commission=commission,
                entry_type='DEBIT',
                amount=commission_amount,
                entry_date=joining_date_val,
                running_balance=commission_amount,
                remarks=f"Initial receivable created ({default_percent}% of ₹{first_month_salary:,.2f})",
                created_by=str(created_by)
            )

        # Log audit activity
        try:
            from apps.enquiries.models import log_activity
            log_activity(
                "general",
                "Ledger Commission Created",
                f"Commission of ₹{commission_amount:,.2f} created for {candidate_name} ({company_name})"
            )
        except Exception as e:
            logger.warning(f"Failed to log activity for commission creation: {e}")

        return commission


def record_payment(commission, amount, entry_date=None, payment_mode='Bank Transfer', reference_no='', remarks='', created_by='System'):
    """
    Records a payment received against a commission.
    """
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))

    amount = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    if amount <= Decimal('0.00'):
        raise ValueError("Payment amount must be greater than zero.")

    if not entry_date:
        entry_date = timezone.now().date()
    else:
        entry_date = parse_date_flexible(entry_date) or timezone.now().date()

    with transaction.atomic():
        comm = PlacementCommission.objects.select_for_update().get(id=commission.id)
        current_bal = comm.balance

        if amount > current_bal:
            raise ValueError(f"Payment amount (₹{amount:,.2f}) cannot exceed current balance (₹{current_bal:,.2f}).")

        rcpt_no = generate_receipt_number()
        new_balance = current_bal - amount

        entry = LedgerEntry.objects.create(
            commission=comm,
            entry_type='CREDIT',
            amount=amount,
            entry_date=entry_date,
            payment_mode=payment_mode or 'Bank Transfer',
            reference_no=reference_no or '',
            remarks=remarks or f"Payment received via {payment_mode}",
            running_balance=new_balance,
            receipt_no=rcpt_no,
            created_by=str(created_by)
        )

        comm.update_status_from_ledger()

        # Log audit activity
        try:
            from apps.enquiries.models import log_activity
            log_activity(
                "general",
                "Ledger Payment Received",
                f"Payment of ₹{amount:,.2f} ({rcpt_no}) received for {comm.candidate_name}"
            )
        except Exception as e:
            logger.warning(f"Failed to log activity for payment: {e}")

        return entry


def update_salary(commission, new_first_month_salary, reason='', created_by='System'):
    """
    Updates the first month salary of a commission and records an adjustment ledger entry.
    """
    if not isinstance(new_first_month_salary, Decimal):
        new_first_month_salary = Decimal(str(new_first_month_salary))

    new_first_month_salary = new_first_month_salary.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    if new_first_month_salary < Decimal('0.00'):
        raise ValueError("Salary cannot be negative.")

    with transaction.atomic():
        comm = PlacementCommission.objects.select_for_update().get(id=commission.id)
        old_salary = comm.first_month_salary
        old_comm_amount = comm.commission_amount
        old_bal = comm.balance

        new_comm_amount = (new_first_month_salary * (comm.commission_percent / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        diff = new_comm_amount - old_comm_amount

        comm.first_month_salary = new_first_month_salary
        comm.commission_amount = new_comm_amount
        comm.salary_source = f"Manually set salary to ₹{new_first_month_salary:,.2f}" + (f" ({reason})" if reason else "")

        if old_comm_amount == Decimal('0.00') and not comm.entries.exists():
            # Initial debit for previously missing salary
            new_bal = new_comm_amount
            if new_comm_amount > Decimal('0.00'):
                LedgerEntry.objects.create(
                    commission=comm,
                    entry_type='DEBIT',
                    amount=new_comm_amount,
                    entry_date=timezone.now().date(),
                    remarks=reason or f"Initial salary set to ₹{new_first_month_salary:,.2f}",
                    running_balance=new_bal,
                    created_by=str(created_by)
                )
        elif diff > Decimal('0.00'):
            new_bal = old_bal + diff
            LedgerEntry.objects.create(
                commission=comm,
                entry_type='ADJUSTMENT_DR',
                amount=diff,
                entry_date=timezone.now().date(),
                remarks=reason or f"Salary updated from ₹{old_salary:,.2f} to ₹{new_first_month_salary:,.2f} (+₹{diff:,.2f} commission)",
                running_balance=new_bal,
                created_by=str(created_by)
            )
        elif diff < Decimal('0.00'):
            abs_diff = abs(diff)
            new_bal = old_bal - abs_diff
            LedgerEntry.objects.create(
                commission=comm,
                entry_type='ADJUSTMENT_CR',
                amount=abs_diff,
                entry_date=timezone.now().date(),
                remarks=reason or f"Salary updated from ₹{old_salary:,.2f} to ₹{new_first_month_salary:,.2f} (-₹{abs_diff:,.2f} commission)",
                running_balance=new_bal,
                created_by=str(created_by)
            )

        if comm.status == 'SALARY_MISSING':
            comm.status = 'PENDING'

        comm.save()
        comm.update_status_from_ledger()

        # Log audit activity
        try:
            from apps.enquiries.models import log_activity
            log_activity(
                "general",
                "Ledger Salary Updated",
                f"Salary updated to ₹{new_first_month_salary:,.2f} for {comm.candidate_name}"
            )
        except Exception as e:
            logger.warning(f"Failed to log activity for salary update: {e}")

        return comm


def waive_commission(commission, reason, created_by='System'):
    """
    Waives the remaining balance of a commission.
    """
    if not reason or not str(reason).strip():
        raise ValueError("Reason for waiver is required.")

    with transaction.atomic():
        comm = PlacementCommission.objects.select_for_update().get(id=commission.id)
        bal = comm.balance

        if bal <= Decimal('0.00'):
            raise ValueError("Commission has no outstanding balance to waive.")

        entry = LedgerEntry.objects.create(
            commission=comm,
            entry_type='WAIVER',
            amount=bal,
            entry_date=timezone.now().date(),
            remarks=reason.strip(),
            running_balance=Decimal('0.00'),
            created_by=str(created_by)
        )

        comm.status = 'WAIVED'
        comm.save(update_fields=['status', 'updated_at'])

        # Log activity
        try:
            from apps.enquiries.models import log_activity
            log_activity(
                "general",
                "Ledger Commission Waived",
                f"Waived ₹{bal:,.2f} for {comm.candidate_name}: {reason}"
            )
        except Exception as e:
            logger.warning(f"Failed to log activity for waiver: {e}")

        return entry


def cancel_commission(commission, reason, created_by='System'):
    """
    Cancels a commission (e.g. offer withdrawn / candidate left).
    """
    if not reason or not str(reason).strip():
        raise ValueError("Reason for cancellation is required.")

    with transaction.atomic():
        comm = PlacementCommission.objects.select_for_update().get(id=commission.id)
        bal = comm.balance

        if bal > Decimal('0.00'):
            LedgerEntry.objects.create(
                commission=comm,
                entry_type='REVERSAL',
                amount=bal,
                entry_date=timezone.now().date(),
                remarks=f"Cancelled: {reason.strip()}",
                running_balance=Decimal('0.00'),
                created_by=str(created_by)
            )

        comm.status = 'CANCELLED'
        comm.save(update_fields=['status', 'updated_at'])

        # Log activity
        try:
            from apps.enquiries.models import log_activity
            log_activity(
                "general",
                "Ledger Commission Cancelled",
                f"Cancelled commission for {comm.candidate_name}: {reason}"
            )
        except Exception as e:
            logger.warning(f"Failed to log activity for cancellation: {e}")

        return comm
