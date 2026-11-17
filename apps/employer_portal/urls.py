from django.urls import path
from . import views

app_name = 'employer_portal'

urlpatterns = [
    path('employer/hire-talent/', views.employer_hire_talent_view, name='hire_talent'),
    path('employer/register/', views.employer_register_view, name='register'),
    path('employer/login/', views.employer_login_view, name='login'),
    path('employer/logout/', views.employer_logout_view, name='logout'),
    path('employer/pending/', views.employer_pending_view, name='pending'),
    path('employer/dashboard/', views.employer_dashboard_view, name='dashboard'),
    path('employer/jobs/', views.employer_jobs_list_view, name='jobs_list'),
    path('employer/jobs/new/', views.employer_job_create_view, name='job_create'),
    path('employer/jobs/<int:job_id>/', views.employer_job_detail_view, name='job_detail'),
    path('employer/jobs/<int:job_id>/edit/', views.employer_job_edit_view, name='job_edit'),
    path('employer/jobs/<int:job_id>/close/', views.employer_job_close_view, name='job_close'),
    path('employer/applicants/', views.employer_applicants_list_view, name='applicants_list'),
    path('employer/applicants/<int:applicant_id>/status/', views.employer_applicant_status_api, name='applicant_status_api'),
    path('employer/interviews/', views.employer_interviews_list_view, name='interviews_list'),
    path('employer/interviews/<int:interview_id>/action/', views.employer_interview_action_api, name='interview_action_api'),
    path('employer/offers/', views.employer_offers_list_view, name='offers_list'),
    path('employer/hired/', views.employer_hired_list_view, name='hired_list'),
    path('employer/profile/', views.employer_profile_view, name='profile'),

    # Admin Approval APIs
    path('api/admin/employer-registrations/', views.api_admin_employer_registrations, name='api_admin_employer_registrations'),
    path('api/admin/employer-registrations/<int:employer_id>/', views.api_admin_employer_registration_detail, name='api_admin_employer_registration_detail'),
    path('api/admin/employer-registrations/<int:employer_id>/approve/', views.api_admin_approve_employer, name='api_admin_approve_employer'),
    path('api/admin/employer-registrations/<int:employer_id>/reject/', views.api_admin_reject_employer, name='api_admin_reject_employer'),
    path('api/admin/employer-registrations/<int:employer_id>/suspend/', views.api_admin_suspend_employer, name='api_admin_suspend_employer'),
    path('api/admin/job-approvals/', views.api_admin_job_approvals, name='api_admin_job_approvals'),
    path('api/admin/job-approvals/<int:job_id>/approve/', views.api_admin_approve_job, name='api_admin_approve_job'),
    path('api/admin/job-approvals/<int:job_id>/reject/', views.api_admin_reject_job, name='api_admin_reject_job'),
]

