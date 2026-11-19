from django.urls import path
from . import views

urlpatterns = [
    # Public candidate auth pages
    path('candidate/register/', views.candidate_register_view, name='candidate_register'),
    path('candidate/login/', views.candidate_login_view, name='candidate_login'),
    path('candidate/forgot-password/', views.candidate_forgot_password_view, name='candidate_forgot_password'),
    path('candidate/reset-password/', views.candidate_reset_password_view, name='candidate_reset_password'),
    path('candidate/logout/', views.api_candidate_logout, name='candidate_logout_view'),
    path('candidate/logout', views.api_candidate_logout),

    # Public candidate auth APIs (with & without trailing slash)
    path('api/candidate/register/', views.api_candidate_register, name='api_candidate_register'),
    path('api/candidate/register', views.api_candidate_register),
    path('api/candidate/login/', views.api_candidate_login, name='api_candidate_login'),
    path('api/candidate/login', views.api_candidate_login),
    path('api/candidate/logout/', views.api_candidate_logout, name='api_candidate_logout'),
    path('api/candidate/logout', views.api_candidate_logout),
    path('api/candidate/forgot-password/', views.api_candidate_forgot_password, name='api_candidate_forgot_password'),
    path('api/candidate/forgot-password', views.api_candidate_forgot_password),
    path('api/candidate/reset-password/', views.api_candidate_reset_password, name='api_candidate_reset_password'),
    path('api/candidate/reset-password', views.api_candidate_reset_password),

    # Candidate portal protected pages
    path('candidate/dashboard/', views.candidate_dashboard_view, name='candidate_dashboard'),
    path('candidate/profile/', views.candidate_profile_view, name='candidate_profile'),
    path('candidate/applied-jobs/', views.candidate_applied_jobs_view, name='candidate_applied_jobs'),
    path('candidate/saved-jobs/', views.candidate_saved_jobs_view, name='candidate_saved_jobs'),
    path('candidate/interviews/', views.candidate_interviews_view, name='candidate_interviews'),
    path('candidate/offers/', views.candidate_offers_view, name='candidate_offers'),
    path('candidate/documents/', views.candidate_documents_view, name='candidate_documents'),
    path('candidate/internships/', views.candidate_internships_view, name='candidate_internships'),
    path('candidate/applied-internships/', views.candidate_internships_view),

    # Candidate portal protected APIs (with & without trailing slash)
    path('api/candidate/jobs/', views.api_candidate_jobs, name='api_candidate_jobs'),
    path('api/candidate/jobs', views.api_candidate_jobs),
    path('api/candidate/apply-job/', views.api_candidate_apply_job, name='api_candidate_apply_job'),
    path('api/candidate/apply-job', views.api_candidate_apply_job),
    path('api/candidate/apply/', views.api_candidate_apply_job),
    path('api/candidate/apply', views.api_candidate_apply_job),
    path('api/candidate/internships/', views.api_candidate_internships, name='api_candidate_internships'),
    path('api/candidate/internships', views.api_candidate_internships),
    path('api/candidate/me/', views.api_candidate_me, name='api_candidate_me'),
    path('api/candidate/me', views.api_candidate_me),
    path('api/candidate/profile/update/', views.api_candidate_profile_update, name='api_candidate_profile_update'),
    path('api/candidate/profile/update', views.api_candidate_profile_update),
    path('api/candidate/dashboard-stats/', views.api_candidate_dashboard_stats, name='api_candidate_dashboard_stats'),
    path('api/candidate/dashboard-stats', views.api_candidate_dashboard_stats),
    path('api/candidate/applied-jobs/', views.api_candidate_applied_jobs, name='api_candidate_applied_jobs'),
    path('api/candidate/applied-jobs', views.api_candidate_applied_jobs),
    path('api/candidate/saved-jobs/', views.api_candidate_saved_jobs, name='api_candidate_saved_jobs'),
    path('api/candidate/saved-jobs', views.api_candidate_saved_jobs),
    path('api/candidate/saved-jobs/toggle/', views.api_candidate_saved_jobs, name='api_candidate_saved_jobs_toggle'),
    path('api/candidate/saved-jobs/toggle', views.api_candidate_saved_jobs),
    path('api/candidate/interviews/', views.api_candidate_interviews, name='api_candidate_interviews'),
    path('api/candidate/interviews', views.api_candidate_interviews),
    path('api/candidate/offers/', views.api_candidate_offers, name='api_candidate_offers'),
    path('api/candidate/offers', views.api_candidate_offers),
    path('api/candidate/offers/<int:offer_id>/accept/', views.api_candidate_accept_offer, name='api_candidate_accept_offer'),
    path('api/candidate/offers/<int:offer_id>/accept', views.api_candidate_accept_offer),

    # Admin candidate approval management (Phase 2)
    path('admin-panel/candidates/registrations/', views.admin_candidate_registrations_view, name='admin_candidate_registrations'),
    path('api/admin/candidate-registrations/', views.api_admin_candidate_registrations, name='api_admin_candidate_registrations'),
    path('api/admin/candidate-registrations', views.api_admin_candidate_registrations),
    path('api/admin/candidate-registrations/<int:candidate_id>/', views.api_admin_candidate_registration_detail, name='api_admin_candidate_registration_detail'),
    path('api/admin/candidate-registrations/<int:candidate_id>', views.api_admin_candidate_registration_detail),
    path('api/admin/candidate-registrations/<int:candidate_id>/approve/', views.api_admin_approve_candidate, name='api_admin_approve_candidate'),
    path('api/admin/candidate-registrations/<int:candidate_id>/approve', views.api_admin_approve_candidate),
    path('api/admin/candidate-registrations/<int:candidate_id>/reject/', views.api_admin_reject_candidate, name='api_admin_reject_candidate'),
    path('api/admin/candidate-registrations/<int:candidate_id>/reject', views.api_admin_reject_candidate),
]
