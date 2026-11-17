from django.contrib import admin
from .models import ApplicationStatusHistory, CandidateSavedJob

@admin.register(ApplicationStatusHistory)
class ApplicationStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'applicant', 'old_status', 'new_status', 'changed_by', 'created_at')
    search_fields = ('applicant__full_name', 'old_status', 'new_status')

@admin.register(CandidateSavedJob)
class CandidateSavedJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'candidate_account', 'job', 'created_at')
    search_fields = ('candidate_account__full_name', 'job__title')
