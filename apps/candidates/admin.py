from django.contrib import admin
from .models import Applicant, Resume, Interview

@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'job_title', 'status', 'applied_on')
    search_fields = ('full_name', 'email', 'phone', 'job_title')
    list_filter = ('status', 'job_title')

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'mobile', 'email', 'applying_for', 'status', 'uploaded_on')
    search_fields = ('full_name', 'mobile', 'email', 'applying_for')
    list_filter = ('status',)

@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'candidate_name', 'candidate_email', 'interview_date', 'interview_time', 'interview_mode', 'status', 'result')
    search_fields = ('candidate_name', 'candidate_email', 'candidate_phone', 'job_title')
    list_filter = ('status', 'result', 'interview_mode', 'interview_date')

