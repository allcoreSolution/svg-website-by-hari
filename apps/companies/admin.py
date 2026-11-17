from django.contrib import admin
from .models import CompanyEnquiry, Company, CompanyContact, CompanyRequirement

@admin.register(CompanyEnquiry)
class CompanyEnquiryAdmin(admin.ModelAdmin):
    list_display = ('id', 'company_name', 'recruiter_name', 'phone', 'email', 'vacancies', 'status', 'created_at')
    search_fields = ('company_name', 'recruiter_name', 'phone', 'email')
    list_filter = ('status',)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'city', 'status', 'created_at')
    search_fields = ('name', 'email', 'phone', 'city', 'gst_number')
    list_filter = ('status', 'city')

@admin.register(CompanyContact)
class CompanyContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'company', 'designation', 'email', 'phone', 'is_primary', 'created_at')
    search_fields = ('name', 'company__name', 'email', 'phone')
    list_filter = ('is_primary',)

@admin.register(CompanyRequirement)
class CompanyRequirementAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'company', 'job_type', 'vacancies', 'status', 'deadline', 'created_at')
    search_fields = ('title', 'company__name', 'department')
    list_filter = ('status', 'job_type')
