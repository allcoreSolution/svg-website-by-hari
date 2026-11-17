from django.contrib import admin
from .models import ContactEnquiry, EnquiryRead, SubmissionThrottle, FollowUp, ActivityLog

@admin.register(ContactEnquiry)
class ContactEnquiryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'service', 'enquiry_type', 'status', 'created_at')
    search_fields = ('name', 'email', 'phone', 'service')
    list_filter = ('status', 'enquiry_type', 'service')

@admin.register(EnquiryRead)
class EnquiryReadAdmin(admin.ModelAdmin):
    list_display = ('id', 'enquiry_type', 'enquiry_id', 'read_by', 'read_at')
    search_fields = ('enquiry_type', 'enquiry_id', 'read_by')
    list_filter = ('enquiry_type',)

@admin.register(SubmissionThrottle)
class SubmissionThrottleAdmin(admin.ModelAdmin):
    list_display = ('id', 'kind', 'key_hash', 'timestamp')
    search_fields = ('key_hash', 'kind')
    list_filter = ('kind',)

@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ('id', 'contact_person', 'type', 'phone_or_email', 'followup_date', 'status', 'created_at')
    search_fields = ('contact_person', 'phone_or_email')
    list_filter = ('status', 'type')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'action_type', 'title', 'actor', 'timestamp')
    search_fields = ('title', 'description', 'actor')
    list_filter = ('action_type',)
