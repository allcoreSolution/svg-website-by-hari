from django.urls import path
from . import views

app_name = 'candidates'

urlpatterns = [
    # Public & Candidate Uploads
    path('api/apply', views.apply_job, name='apply_job'),
    path('api/apply/', views.apply_job),
    path('api/upload-resume', views.upload_quick_resume, name='upload_quick_resume'),
    path('api/upload-resume/', views.upload_quick_resume),

    # Applicants
    path('api/applicants', views.get_applicants, name='get_applicants'),
    path('api/applicants/', views.get_applicants),
    path('api/admin/applicants', views.admin_create_applicant, name='admin_create_applicant'),
    path('api/admin/applicants/', views.admin_create_applicant),
    path('api/candidates/create', views.admin_create_applicant),
    path('api/candidates/create/', views.admin_create_applicant),
    path('api/applicant/<int:id>', views.applicant_detail, name='applicant_detail'),
    path('api/applicant/<int:id>/', views.applicant_detail),

    # Resumes
    path('api/resumes', views.get_resumes, name='get_resumes'),
    path('api/resumes/', views.get_resumes),
    path('api/resume/<int:id>', views.resume_detail, name='resume_detail'),
    path('api/resume/<int:id>/', views.resume_detail),

    # Interviews
    path('api/admin/schedule-interview', views.admin_schedule_interview, name='admin_schedule_interview'),
    path('api/admin/schedule-interview/', views.admin_schedule_interview),

    path('api/interviews', views.get_interviews, name='get_interviews'),
    path('api/interviews/', views.get_interviews),
    path('api/interviews/<int:id>', views.interview_detail, name='interview_detail'),
    path('api/interviews/<int:id>/', views.interview_detail),
    path('api/interviews/<int:id>/reschedule', views.reschedule_interview, name='reschedule_interview'),
    path('api/interviews/<int:id>/reschedule/', views.reschedule_interview),
    path('api/interviews/<int:id>/complete', views.complete_interview, name='complete_interview'),
    path('api/interviews/<int:id>/complete/', views.complete_interview),
    path('api/interviews/<int:id>/cancel', views.cancel_interview, name='cancel_interview'),
    path('api/interviews/<int:id>/cancel/', views.cancel_interview),
]
