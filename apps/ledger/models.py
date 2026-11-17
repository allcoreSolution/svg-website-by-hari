from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone


class PlacementCommission(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partial'),
        ('PAID', 'Paid'),
        ('WAIVED', 'Waived'),
        ('CANCELLED', 'Cancelled'),
        ('SALARY_MISSING', 'Salary Missing'),
    ]

    PAYER_CHOICES = [
        ('Candidate', 'Candidate'),
        ('Company', 'Company'),
    ]

    applicant = models.ForeignKey(
        'candidates.Applicant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ledger_commissions'
    )
    placement = models.ForeignKey(
        'placements.Placement',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ledger_commissions'
    )

    # Snapshot fields
    candidate_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255, blank=True, default='')
    joining_date = models.DateField(null=True, blank=True)

    first_month_salary = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('50.00'))
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    payer_type = models.CharField(max_length=20, choices=PAYER_CHOICES, default='Candidate')
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING')

    salary_source = models.CharField(max_length=255, blank=True, default='')
    notes = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=150, blank=True, default='System')

    class Meta:
        db_table = 'ledger_placement_commissions'
        ordering = ['-id']

    def __str__(self):
        return f"Commission for {self.candidate_name} ({self.company_name}) - ₹{self.commission_amount}"

    @property
    def total_received(self):
        credits = self.entries.filter(entry_type='CREDIT').aggregate(total=models.Sum('amount'))['total']
        return credits or Decimal('0.00')

    @property
    def total_waived(self):
        waived = self.entries.filter(entry_type__in=['WAIVER', 'REVERSAL']).aggregate(total=models.Sum('amount'))['total']
        return waived or Decimal('0.00')

    @property
    def total_adjustments(self):
        dr = self.entries.filter(entry_type='ADJUSTMENT_DR').aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        cr = self.entries.filter(entry_type='ADJUSTMENT_CR').aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        return dr - cr

    @property
    def balance(self):
        last_entry = self.entries.order_by('-id').first()
        if last_entry:
            return last_entry.running_balance
        return self.commission_amount

    @property
    def paid_on_date(self):
        if self.status == 'PAID':
            last_credit = self.entries.filter(entry_type='CREDIT').order_by('-id').first()
            if last_credit:
                return last_credit.entry_date
        return None

    def update_status_from_ledger(self):
        """Recomputes and saves status based on current ledger entries and running balance."""
        if self.status == 'CANCELLED':
            return self.status

        if self.first_month_salary == Decimal('0.00') or self.status == 'SALARY_MISSING':
            if self.first_month_salary > Decimal('0.00'):
                pass  # salary was set
            else:
                self.status = 'SALARY_MISSING'
                self.save(update_fields=['status', 'updated_at'])
                return self.status

        bal = self.balance
        rec = self.total_received
        waived = self.total_waived

        if bal <= Decimal('0.00'):
            if waived >= (self.commission_amount + self.total_adjustments) and rec == Decimal('0.00'):
                self.status = 'WAIVED'
            else:
                self.status = 'PAID'
        elif rec > Decimal('0.00'):
            self.status = 'PARTIAL'
        else:
            self.status = 'PENDING'

        self.save(update_fields=['status', 'updated_at'])
        return self.status


class LedgerEntry(models.Model):
    ENTRY_TYPE_CHOICES = [
        ('DEBIT', 'Debit (Receivable)'),
        ('CREDIT', 'Credit (Payment Received)'),
        ('ADJUSTMENT_DR', 'Adjustment (Increase)'),
        ('ADJUSTMENT_CR', 'Adjustment (Decrease)'),
        ('WAIVER', 'Waiver'),
        ('REVERSAL', 'Reversal'),
    ]

    PAYMENT_MODE_CHOICES = [
        ('Cash', 'Cash'),
        ('Bank Transfer', 'Bank Transfer'),
        ('UPI', 'UPI'),
        ('Cheque', 'Cheque'),
        ('Other', 'Other'),
    ]

    commission = models.ForeignKey(
        PlacementCommission,
        on_delete=models.PROTECT,
        related_name='entries'
    )
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    entry_date = models.DateField(default=timezone.now)

    payment_mode = models.CharField(max_length=30, choices=PAYMENT_MODE_CHOICES, blank=True, default='')
    reference_no = models.CharField(max_length=100, blank=True, default='')
    remarks = models.TextField(blank=True, default='')

    running_balance = models.DecimalField(max_digits=12, decimal_places=2)
    receipt_no = models.CharField(max_length=50, blank=True, default='')

    created_by = models.CharField(max_length=150, blank=True, default='System')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ledger_entries'
        ordering = ['id']

    def __str__(self):
        return f"{self.entry_type} ₹{self.amount} for {self.commission.candidate_name} (Bal: ₹{self.running_balance})"
