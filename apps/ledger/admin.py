from django.contrib import admin
from apps.ledger.models import PlacementCommission, LedgerEntry


@admin.register(PlacementCommission)
class PlacementCommissionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'candidate_name', 'company_name', 'position',
        'first_month_salary', 'commission_amount', 'status', 'created_at'
    )
    list_filter = ('status', 'payer_type', 'joining_date')
    search_fields = ('candidate_name', 'company_name', 'position', 'salary_source')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'commission', 'entry_type', 'amount',
        'running_balance', 'receipt_no', 'entry_date', 'created_at'
    )
    list_filter = ('entry_type', 'payment_mode', 'entry_date')
    search_fields = ('commission__candidate_name', 'receipt_no', 'reference_no', 'remarks')
    readonly_fields = ('created_at',)
