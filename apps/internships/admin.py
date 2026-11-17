from django.contrib import admin
from .models import InternshipEnquiry, InternshipProvider, Internship, InternshipApplication

@admin.register(InternshipEnquiry)
class InternshipEnquiryAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'course_stream', 'duration', 'status', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'college', 'course_stream')
    list_filter = ('status', 'duration')

@admin.register(InternshipProvider)
class InternshipProviderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'contact_person', 'email', 'phone', 'industry', 'is_active', 'created_at')
    search_fields = ('name', 'contact_person', 'email', 'phone', 'industry')
    list_filter = ('is_active', 'industry')

@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'provider', 'mode', 'duration', 'seats', 'status', 'created_at')
    search_fields = ('title', 'location', 'skills_required', 'description')
    list_filter = ('status', 'mode')

@admin.register(InternshipApplication)
class InternshipApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'internship', 'email', 'phone', 'college', 'status', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'college', 'course_stream', 'skills')
    list_filter = ('status',)

