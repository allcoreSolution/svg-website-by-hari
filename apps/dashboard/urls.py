from django.urls import path
from django.shortcuts import redirect
from . import views
from apps.candidate_portal.views import admin_candidate_registrations_view
from apps.employer_portal import views as employer_portal_views
from . import staff_views
from . import role_views

app_name = 'dashboard'

urlpatterns = [
    # Admin root & auth
    path('admin/', views.admin_root_redirect, name='admin_root_alt'),
    path('admin-panel/', views.admin_root_redirect, name='admin_root'),
    path('admin-panel/login/', views.admin_login_view, name='admin_login_page'),
    path('admin-panel/dashboard/', views.admin_dashboard_view, name='admin_dashboard_page'),
    
    # Legacy URL compatibility
    path('admin/login', views.admin_login_view),
    path('admin/login/', views.admin_login_view),
    path('admin/dashboard', views.admin_dashboard_view),
    path('admin/dashboard/', views.admin_dashboard_view),

    # Registration & Approval Module
    path('admin-panel/registrations/', lambda r: views.admin_registrations_view(r, 'all'), name='registrations_all'),
    path('admin-panel/registrations', lambda r: views.admin_registrations_view(r, 'all')),
    path('admin-panel/registrations/candidates/', lambda r: views.admin_registrations_view(r, 'candidates'), name='registrations_candidates'),
    path('admin-panel/registrations/candidates', lambda r: views.admin_registrations_view(r, 'candidates')),
    path('admin-panel/registrations/employers/', lambda r: views.admin_registrations_view(r, 'employers'), name='registrations_employers'),
    path('admin-panel/registrations/employers', lambda r: views.admin_registrations_view(r, 'employers')),
    path('admin-panel/registrations/rejected/', lambda r: views.admin_registrations_view(r, 'rejected'), name='registrations_rejected'),
    path('admin-panel/registrations/rejected', lambda r: views.admin_registrations_view(r, 'rejected')),

    # Unified Registration APIs
    path('api/admin/registrations/', views.api_admin_registrations, name='api_admin_registrations'),
    path('api/admin/registrations', views.api_admin_registrations),
    path('api/admin/registrations/summary/', views.api_admin_registrations_summary, name='api_admin_registrations_summary'),
    path('api/admin/registrations/summary', views.api_admin_registrations_summary),
    path('api/admin/registrations/bulk-action/', views.api_admin_bulk_registrations_action, name='api_admin_bulk_registrations_action'),
    path('api/admin/registrations/bulk-action', views.api_admin_bulk_registrations_action),
    path('api/admin/registrations/export/', views.api_admin_registrations_export, name='api_admin_registrations_export'),
    path('api/admin/registrations/export', views.api_admin_registrations_export),

    # Candidates Module
    path('admin-panel/candidates/all/', lambda r: views.admin_module_generic_view(r, 'candidates_all'), name='candidates_all'),
    path('admin-panel/candidates/registrations/', admin_candidate_registrations_view, name='candidates_registrations'),
    path('admin-panel/candidates/registrations', admin_candidate_registrations_view),
    path('admin-panel/candidates/add/', lambda r: views.admin_module_generic_view(r, 'candidates_add'), name='candidates_add'),
    path('admin-panel/candidates/profiles/', lambda r: views.admin_module_generic_view(r, 'candidates_profiles'), name='candidates_profiles'),
    path('admin-panel/candidates/shortlisted/', lambda r: views.admin_module_generic_view(r, 'candidates_shortlisted'), name='candidates_shortlisted'),
    path('admin-panel/candidates/interviews/upcoming/', lambda r: views.admin_module_generic_view(r, 'interviews_upcoming'), name='interviews_upcoming'),
    path('admin-panel/candidates/interviews/completed/', lambda r: views.admin_module_generic_view(r, 'interviews_completed'), name='interviews_completed'),
    path('admin-panel/candidates/interviews/cancelled/', lambda r: views.admin_module_generic_view(r, 'interviews_cancelled'), name='interviews_cancelled'),
    path('admin-panel/candidates/interviews/', lambda r: views.admin_module_generic_view(r, 'interviews_upcoming'), name='interviews_all'),
    path('admin-panel/candidates/selected/', lambda r: views.admin_module_generic_view(r, 'candidates_selected'), name='candidates_selected'),
    path('admin-panel/candidates/rejected/', lambda r: views.admin_module_generic_view(r, 'candidates_rejected'), name='candidates_rejected'),
    path('admin-panel/candidates/placed/', lambda r: views.admin_module_generic_view(r, 'candidates_placed'), name='candidates_placed'),
    path('admin-panel/candidates/', lambda r: views.admin_module_generic_view(r, 'candidates_all')),

    # Companies & Job Categories Module
    path('admin-panel/companies/all/', lambda r: views.admin_module_generic_view(r, 'companies_all'), name='companies_all'),
    path('admin-panel/companies/add/', lambda r: views.admin_module_generic_view(r, 'companies_add'), name='companies_add'),
    path('admin-panel/companies/enquiries/', lambda r: views.admin_module_generic_view(r, 'companies_enquiries'), name='companies_enquiries'),
    path('admin-panel/job-categories/', views.admin_job_categories_view, name='job_categories'),
    path('admin-panel/job-categories', views.admin_job_categories_view),
    path('admin-panel/companies/requirements/all/', views.admin_requirements_or_categories_dispatcher, name='requirements_all'),
    path('admin-panel/companies/requirements/all', views.admin_requirements_or_categories_dispatcher),
    path('admin-panel/companies/requirements/active/', views.admin_job_approvals_view, name='requirements_active'),
    path('admin-panel/companies/job-approvals/', views.admin_job_approvals_view, name='job_approvals'),
    path('admin-panel/companies/job-approvals', views.admin_job_approvals_view),
    path('admin-panel/companies/requirements/closed/', lambda r: views.admin_module_generic_view(r, 'requirements_closed'), name='requirements_closed'),
    path('admin-panel/companies/requirements/expired/', lambda r: views.admin_module_generic_view(r, 'requirements_expired'), name='requirements_expired'),
    path('admin-panel/companies/job-openings/', views.admin_job_openings_view, name='job_openings'),
    path('admin-panel/companies/job-openings', views.admin_job_openings_view),
    path('admin-panel/companies/contacts/', lambda r: views.admin_module_generic_view(r, 'company_contacts'), name='company_contacts'),
    path('admin-panel/companies/', lambda r: views.admin_module_generic_view(r, 'companies_all')),

    # Internships Module
    path('admin-panel/internships/all/', lambda r: views.admin_module_generic_view(r, 'internships_all'), name='internships_all'),
    path('admin-panel/internships/add/', lambda r: views.admin_module_generic_view(r, 'internships_add'), name='internships_add'),
    path('admin-panel/internships/enquiries/', lambda r: views.admin_module_generic_view(r, 'internships_enquiries'), name='internships_enquiries'),
    path('admin-panel/internships/applications/all/', lambda r: views.admin_module_generic_view(r, 'internship_apps_all'), name='internship_apps_all'),
    path('admin-panel/internships/applications/pending/', lambda r: views.admin_module_generic_view(r, 'internship_apps_pending'), name='internship_apps_pending'),
    path('admin-panel/internships/applications/shortlisted/', lambda r: views.admin_module_generic_view(r, 'internship_apps_shortlisted'), name='internship_apps_shortlisted'),
    path('admin-panel/internships/applications/selected/', lambda r: views.admin_module_generic_view(r, 'internship_apps_selected'), name='internship_apps_selected'),
    path('admin-panel/internships/applications/rejected/', lambda r: views.admin_module_generic_view(r, 'internship_apps_rejected'), name='internship_apps_rejected'),
    path('admin-panel/internships/active/', lambda r: views.admin_module_generic_view(r, 'internships_active'), name='internships_active'),
    path('admin-panel/internships/completed/', lambda r: views.admin_module_generic_view(r, 'internships_completed'), name='internships_completed'),
    path('admin-panel/internships/providers/', lambda r: views.admin_module_generic_view(r, 'internship_providers'), name='internship_providers'),
    path('admin-panel/internships/', lambda r: views.admin_module_generic_view(r, 'internship_apps_all'), name='internships_default'),
    path('admin-panel/internships', lambda r: views.admin_module_generic_view(r, 'internship_apps_all')),

    # Enquiries Module
    path('admin-panel/enquiries/all/', lambda r: views.admin_module_generic_view(r, 'enquiries_all'), name='enquiries_all'),
    path('admin-panel/enquiries/general/', lambda r: views.admin_module_generic_view(r, 'enquiries_general'), name='enquiries_general'),
    path('admin-panel/enquiries/company/', lambda r: views.admin_module_generic_view(r, 'enquiries_company'), name='enquiries_company'),
    path('admin-panel/enquiries/internship/', lambda r: views.admin_module_generic_view(r, 'enquiries_internship'), name='enquiries_internship'),
    path('admin-panel/enquiries/candidate/', lambda r: views.admin_module_generic_view(r, 'enquiries_candidate'), name='enquiries_candidate'),
    path('admin-panel/enquiries/unread/', lambda r: views.admin_module_generic_view(r, 'enquiries_unread'), name='enquiries_unread'),
    path('admin-panel/enquiries/resolved/', lambda r: views.admin_module_generic_view(r, 'enquiries_resolved'), name='enquiries_resolved'),
    path('admin-panel/enquiries/', lambda r: views.admin_module_generic_view(r, 'enquiries_all')),

    # Placements Module
    path('admin-panel/placements/all/', lambda r: views.admin_module_generic_view(r, 'placements_all'), name='placements_all'),
    path('admin-panel/placements/active/', lambda r: views.admin_module_generic_view(r, 'placements_active'), name='placements_active'),
    path('admin-panel/placements/completed/', lambda r: views.admin_module_generic_view(r, 'placements_completed'), name='placements_completed'),
    path('admin-panel/placements/pending-joining/', lambda r: views.admin_module_generic_view(r, 'placements_pending_joining'), name='placements_pending_joining'),
    path('admin-panel/placements/joined/', lambda r: views.admin_module_generic_view(r, 'placements_joined'), name='placements_joined'),
    path('admin-panel/placements/history/', lambda r: views.admin_module_generic_view(r, 'placements_history'), name='placements_history'),
    path('admin-panel/placements/reports/', lambda r: views.admin_module_generic_view(r, 'placements_reports'), name='placements_reports'),
    path('admin-panel/placements/', lambda r: views.admin_module_generic_view(r, 'placements_all')),

    # Job Offers Module
    path('admin-panel/job-offers/all/', lambda r: views.admin_module_generic_view(r, 'offers_all'), name='offers_all'),
    path('admin-panel/job-offers/create/', lambda r: views.admin_module_generic_view(r, 'offers_create'), name='offers_create'),
    path('admin-panel/job-offers/pending/', lambda r: views.admin_module_generic_view(r, 'offers_pending'), name='offers_pending'),
    path('admin-panel/job-offers/accepted/', lambda r: views.admin_module_generic_view(r, 'offers_accepted'), name='offers_accepted'),
    path('admin-panel/job-offers/rejected/', lambda r: views.admin_module_generic_view(r, 'offers_rejected'), name='offers_rejected'),
    path('admin-panel/job-offers/expired/', lambda r: views.admin_module_generic_view(r, 'offers_expired'), name='offers_expired'),
    path('admin-panel/job-offers/history/', lambda r: views.admin_module_generic_view(r, 'offers_history'), name='offers_history'),
    path('admin-panel/job-offers/', lambda r: views.admin_module_generic_view(r, 'offers_all')),
    path('admin-panel/offers/all/', lambda r: views.admin_module_generic_view(r, 'offers_all'), name='offers_alias_all'),
    path('admin-panel/offers/', lambda r: views.admin_module_generic_view(r, 'offers_all')),

    # Placements & Job Offers APIs
    path('api/admin/job-offers/create/', views.admin_create_job_offer_api, name='api_admin_create_job_offer'),
    path('api/admin/job-offers/create', views.admin_create_job_offer_api),
    path('api/admin/placements/mark-joined/', views.admin_mark_joined_api, name='api_admin_mark_joined'),
    path('api/admin/placements/mark-joined', views.admin_mark_joined_api),

    # Documents Module
    path('admin-panel/documents/all/', lambda r: views.admin_module_generic_view(r, 'documents_all'), name='documents_all'),
    path('admin-panel/documents/candidate/', lambda r: views.admin_module_generic_view(r, 'documents_candidate'), name='documents_candidate'),
    path('admin-panel/documents/company/', lambda r: views.admin_module_generic_view(r, 'documents_company'), name='documents_company'),
    path('admin-panel/documents/internship/', lambda r: views.admin_module_generic_view(r, 'documents_internship'), name='documents_internship'),
    path('admin-panel/documents/offer-letters/', lambda r: views.admin_module_generic_view(r, 'documents_offer_letters'), name='documents_offer_letters'),
    path('admin-panel/documents/joining/', lambda r: views.admin_module_generic_view(r, 'documents_joining'), name='documents_joining'),
    path('admin-panel/documents/verification/pending/', lambda r: views.admin_module_generic_view(r, 'verification_pending'), name='verification_pending'),
    path('admin-panel/documents/verification/verified/', lambda r: views.admin_module_generic_view(r, 'verification_verified'), name='verification_verified'),
    path('admin-panel/documents/verification/rejected/', lambda r: views.admin_module_generic_view(r, 'verification_rejected'), name='verification_rejected'),
    path('admin-panel/documents/', lambda r: views.admin_module_generic_view(r, 'documents_all')),

    # Follow-ups Module
    path('admin-panel/followups/all/', lambda r: views.admin_module_generic_view(r, 'followups_all'), name='followups_all'),
    path('admin-panel/followups/today/', lambda r: views.admin_module_generic_view(r, 'followups_today'), name='followups_today'),
    path('admin-panel/followups/upcoming/', lambda r: views.admin_module_generic_view(r, 'followups_upcoming'), name='followups_upcoming'),
    path('admin-panel/followups/overdue/', lambda r: views.admin_module_generic_view(r, 'followups_overdue'), name='followups_overdue'),
    path('admin-panel/followups/candidate/', lambda r: views.admin_module_generic_view(r, 'followups_candidate'), name='followups_candidate'),
    path('admin-panel/followups/company/', lambda r: views.admin_module_generic_view(r, 'followups_company'), name='followups_company'),
    path('admin-panel/followups/internship/', lambda r: views.admin_module_generic_view(r, 'followups_internship'), name='followups_internship'),
    path('admin-panel/followups/completed/', lambda r: views.admin_module_generic_view(r, 'followups_completed'), name='followups_completed'),
    path('admin-panel/followups/', lambda r: views.admin_module_generic_view(r, 'followups_all')),

    # Users & Roles Module (Real Role & Permission System)
    path('admin-panel/users/all/', role_views.admin_users_list_view, name='users_all'),
    path('admin-panel/users/all', role_views.admin_users_list_view),
    path('admin-panel/users/add/', lambda r: views.admin_module_generic_view(r, 'users_add'), name='users_add'),
    path('admin-panel/users/admin/', role_views.admin_users_list_view, name='users_admin'),
    path('admin-panel/users/admin', role_views.admin_users_list_view),
    # Staff Management Module & APIs
    path('admin-panel/users/staff/', staff_views.admin_staff_management_view, name='users_staff'),
    path('admin-panel/users/staff', staff_views.admin_staff_management_view),
    path('api/admin/staff/add/', staff_views.api_admin_staff_add, name='api_admin_staff_add'),
    path('api/admin/staff/add', staff_views.api_admin_staff_add),
    path('api/admin/staff/<int:staff_id>/update/', staff_views.api_admin_staff_update, name='api_admin_staff_update'),
    path('api/admin/staff/<int:staff_id>/update', staff_views.api_admin_staff_update),
    path('api/admin/staff/<int:staff_id>/delete/', staff_views.api_admin_staff_delete, name='api_admin_staff_delete'),
    path('api/admin/staff/<int:staff_id>/delete', staff_views.api_admin_staff_delete),
    path('api/admin/staff/<int:staff_id>/detail/', staff_views.api_admin_staff_detail, name='api_admin_staff_detail'),
    path('api/admin/staff/<int:staff_id>/detail', staff_views.api_admin_staff_detail),
    path('api/admin/staff/<int:staff_id>/record-payment/', staff_views.api_admin_staff_record_payment, name='api_admin_staff_record_payment'),
    path('api/admin/staff/<int:staff_id>/record-payment', staff_views.api_admin_staff_record_payment),
    path('api/admin/staff/export/', staff_views.api_admin_staff_export, name='api_admin_staff_export'),
    path('api/admin/staff/export', staff_views.api_admin_staff_export),
    path('admin-panel/users/candidates/', lambda r: views.admin_module_generic_view(r, 'users_candidates'), name='users_candidates'),
    path('admin-panel/users/roles/', role_views.admin_roles_list_view, name='users_roles'),
    path('admin-panel/users/roles', role_views.admin_roles_list_view),
    path('admin-panel/users/permissions/', role_views.admin_permissions_matrix_view, name='users_permissions'),
    path('admin-panel/users/permissions', role_views.admin_permissions_matrix_view),
    path('admin-panel/users/login-activity/', role_views.admin_login_activity_view, name='users_login_activity'),
    path('admin-panel/users/login-activity', role_views.admin_login_activity_view),
    path('admin-panel/users/', role_views.admin_users_list_view),

    # Role Management APIs
    path('api/admin/roles/save/', role_views.api_admin_role_save, name='api_admin_role_save'),
    path('api/admin/roles/save', role_views.api_admin_role_save),
    path('api/admin/roles/<int:role_id>/', role_views.api_admin_role_detail, name='api_admin_role_detail'),
    path('api/admin/roles/<int:role_id>', role_views.api_admin_role_detail),
    path('api/admin/roles/<int:role_id>/archive/', role_views.api_admin_role_archive, name='api_admin_role_archive'),
    path('api/admin/roles/<int:role_id>/archive', role_views.api_admin_role_archive),
    path('api/admin/roles/<int:role_id>/duplicate/', role_views.api_admin_role_duplicate, name='api_admin_role_duplicate'),
    path('api/admin/roles/<int:role_id>/duplicate', role_views.api_admin_role_duplicate),
    path('api/admin/roles/export/', role_views.api_admin_roles_export, name='api_admin_roles_export'),
    path('api/admin/roles/export', role_views.api_admin_roles_export),

    # Notifications Module
    path('admin-panel/notifications/all/', lambda r: views.admin_module_generic_view(r, 'notifications_all'), name='notifications_all'),
    path('admin-panel/notifications/send/', lambda r: views.admin_module_generic_view(r, 'notifications_send'), name='notifications_send'),
    path('admin-panel/notifications/email/', lambda r: views.admin_module_generic_view(r, 'notifications_email'), name='notifications_email'),
    path('admin-panel/notifications/system/', lambda r: views.admin_module_generic_view(r, 'notifications_system'), name='notifications_system'),
    path('admin-panel/notifications/candidate/', lambda r: views.admin_module_generic_view(r, 'notifications_candidate'), name='notifications_candidate'),
    path('admin-panel/notifications/company/', lambda r: views.admin_module_generic_view(r, 'notifications_company'), name='notifications_company'),
    path('admin-panel/notifications/history/', lambda r: views.admin_module_generic_view(r, 'notifications_history'), name='notifications_history'),
    path('admin-panel/notifications/', lambda r: views.admin_module_generic_view(r, 'notifications_all')),

    # Reports & Analytics Module
    path('admin-panel/reports/candidate/', lambda r: views.admin_reports_view(r, 'candidate'), name='reports_candidate'),
    path('admin-panel/reports/company/', lambda r: views.admin_reports_view(r, 'company'), name='reports_company'),
    path('admin-panel/reports/employer/', lambda r: views.admin_reports_view(r, 'company')),
    path('admin-panel/reports/internship/', lambda r: views.admin_reports_view(r, 'candidate')),
    path('admin-panel/reports/placement/', lambda r: views.admin_reports_view(r, 'candidate')),
    path('admin-panel/reports/', lambda r: views.admin_reports_view(r, 'candidate')),

    # Activity & Logs Module (Redirect removed Activity Logs to Dashboard)
    path('admin-panel/logs/admin/', lambda r: redirect('/admin-panel/dashboard/'), name='logs_admin'),
    path('admin-panel/logs/user/', lambda r: redirect('/admin-panel/dashboard/'), name='logs_user'),
    path('admin-panel/logs/login/', lambda r: redirect('/admin-panel/dashboard/'), name='logs_login'),
    path('admin-panel/logs/system/', lambda r: redirect('/admin-panel/dashboard/'), name='logs_system'),
    path('admin-panel/logs/audit/', lambda r: redirect('/admin-panel/dashboard/'), name='logs_audit'),
    path('admin-panel/logs/', lambda r: redirect('/admin-panel/dashboard/')),

    # Settings Module (Merged System & Website Settings)
    path('admin-panel/settings/general/', lambda r: views.admin_website_management_view(r, 'settings'), name='settings_general'),
    path('admin-panel/settings/profile/', lambda r: views.admin_module_generic_view(r, 'settings_profile'), name='settings_profile'),
    path('admin-panel/settings/website/', lambda r: views.admin_website_management_view(r, 'settings'), name='settings_website'),
    path('admin-panel/settings/email/', lambda r: views.admin_module_generic_view(r, 'settings_email'), name='settings_email'),
    path('admin-panel/settings/notification/', lambda r: views.admin_module_generic_view(r, 'settings_notification'), name='settings_notification'),
    path('admin-panel/settings/security/', lambda r: views.admin_module_generic_view(r, 'settings_security'), name='settings_security'),
    path('admin-panel/settings/password/', lambda r: views.admin_module_generic_view(r, 'settings_password'), name='settings_password'),
    path('admin-panel/settings/roles/', role_views.admin_roles_list_view, name='settings_roles'),
    path('admin-panel/settings/roles', role_views.admin_roles_list_view),
    path('admin-panel/settings/documents/', lambda r: views.admin_module_generic_view(r, 'settings_documents'), name='settings_documents'),
    path('admin-panel/settings/backup/', lambda r: views.admin_module_generic_view(r, 'settings_backup'), name='settings_backup'),
    path('admin-panel/settings/', lambda r: views.admin_website_management_view(r, 'settings'), name='settings_root'),

    # Website Management Module (9 Sub-Sections)
    path('admin-panel/website/', lambda r: views.admin_website_management_view(r, 'header_footer'), name='admin_website_root'),
    path('admin-panel/website/settings/', lambda r: redirect('/admin-panel/settings/general/'), name='admin_website_settings'),
    path('admin-panel/website/header-footer/', lambda r: views.admin_website_management_view(r, 'header_footer'), name='admin_website_header_footer'),
    path('admin-panel/website/home/', lambda r: views.admin_website_management_view(r, 'home'), name='admin_website_home'),
    path('admin-panel/website/home-page/', lambda r: views.admin_website_management_view(r, 'home'), name='admin_website_home_alias'),
    path('admin-panel/website/home-page', lambda r: views.admin_website_management_view(r, 'home')),
    path('admin-panel/website/about/', lambda r: views.admin_website_management_view(r, 'about'), name='admin_website_about'),
    path('admin-panel/website/services/', lambda r: views.admin_website_management_view(r, 'services'), name='admin_website_services'),
    path('admin-panel/website/job/', lambda r: views.admin_website_management_view(r, 'jobs'), name='admin_website_job'),
    path('admin-panel/website/jobs/', lambda r: views.admin_website_management_view(r, 'jobs'), name='admin_website_jobs'),
    path('admin-panel/website/team-ceo/', lambda r: views.admin_website_management_view(r, 'team_ceo'), name='admin_website_team_ceo'),
    path('admin-panel/website/careers/', lambda r: views.admin_website_management_view(r, 'careers'), name='admin_website_careers'),
    path('admin-panel/website/blog/', lambda r: views.admin_website_management_view(r, 'blog'), name='admin_website_blog'),
    path('admin-panel/website/gallery/', lambda r: views.admin_website_management_view(r, 'gallery'), name='admin_website_gallery'),
    path('admin-panel/website/contact/', lambda r: views.admin_website_management_view(r, 'contact'), name='admin_website_contact'),
    path('api/admin/website/upload-image/', views.api_admin_upload_image, name='api_admin_upload_image'),
    path('api/admin/website/upload-image', views.api_admin_upload_image),
    path('api/admin/website/toggle-repeater-visible/', views.api_admin_toggle_repeater_visible, name='api_admin_toggle_repeater_visible'),
    path('api/admin/website/toggle-repeater-visible', views.api_admin_toggle_repeater_visible),
    path('admin-panel/api/admin/website/toggle-repeater-visible/', views.api_admin_toggle_repeater_visible, name='api_admin_toggle_repeater_visible_prefixed'),
    path('admin-panel/api/admin/website/toggle-repeater-visible', views.api_admin_toggle_repeater_visible),
    path('admin-panel/website/services/api/toggle-repeater-visible/', views.api_admin_toggle_repeater_visible),
    path('admin-panel/website/services/api/toggle-repeater-visible', views.api_admin_toggle_repeater_visible),

    # Job Applications Approval Module
    path('admin-panel/job-applications/all/', lambda r: views.admin_module_generic_view(r, 'job_applications_all'), name='job_applications_all'),
    path('admin-panel/job-applications/pending/', lambda r: views.admin_module_generic_view(r, 'job_applications_pending'), name='job_applications_pending'),

    # Application Approval & Step Override APIs
    path('api/admin/applications/<int:applicant_id>/approve/', views.admin_approve_application_api, name='admin_approve_application_api'),
    path('api/admin/applications/<int:applicant_id>/assign-employer/', views.admin_assign_applicant_employer_api, name='admin_assign_applicant_employer_api'),
    path('api/admin/applications/<int:applicant_id>/reject/', views.admin_reject_application_api, name='admin_reject_application_api'),
    path('api/admin/applications/bulk-approve/', views.admin_bulk_approve_applications_api, name='admin_bulk_approve_applications_api'),
    path('api/admin/applications/<int:applicant_id>/override-step/', views.admin_override_application_step_api, name='admin_override_application_step_api'),

    # Dashboard APIs
    path('api/admin/dashboard-stats', views.dashboard_stats_api, name='dashboard_stats_api'),
    path('api/admin/dashboard-stats/', views.dashboard_stats_api),
    path('api/admin/topbar-counts/', views.api_admin_topbar_counts, name='api_admin_topbar_counts'),
    path('api/admin/topbar-counts', views.api_admin_topbar_counts),
    path('api/admin/documents', views.admin_documents_api, name='admin_documents_api'),
    path('api/admin/documents/', views.admin_documents_api),
    path('api/admin/file/<path:name>', views.admin_file_download, name='admin_file_download'),
    path('api/admin/files/download/<path:name>', views.admin_file_download, name='admin_files_download'),
    path('api/admin/files/download/<path:name>/', views.admin_file_download),

    # Job Management CRUD & Approval APIs
    path('api/admin/jobs/save/', views.api_admin_job_save, name='api_admin_job_save'),
    path('api/admin/jobs/save', views.api_admin_job_save),
    path('api/admin/jobs/<int:job_id>/delete/', views.api_admin_job_delete, name='api_admin_job_delete'),
    path('api/admin/jobs/<int:job_id>/delete', views.api_admin_job_delete),
    path('api/admin/jobs/<int:job_id>/status/', views.api_admin_job_status, name='api_admin_job_status'),
    path('api/admin/jobs/<int:job_id>/status', views.api_admin_job_status),

    # Job Approvals APIs
    path('api/admin/job-approvals/<int:job_id>/approve/', employer_portal_views.api_admin_approve_job, name='api_admin_approve_job_alt'),
    path('api/admin/job-approvals/<int:job_id>/approve', employer_portal_views.api_admin_approve_job),
    path('api/admin/job-approvals/<int:job_id>/reject/', employer_portal_views.api_admin_reject_job, name='api_admin_reject_job_alt'),
    path('api/admin/job-approvals/<int:job_id>/reject', employer_portal_views.api_admin_reject_job),

    # Job Categories CRUD & Status APIs
    path('api/admin/job-categories/save/', views.api_admin_category_save, name='api_admin_category_save'),
    path('api/admin/job-categories/save', views.api_admin_category_save),
    path('api/admin/job-categories/<int:cat_id>/delete/', views.api_admin_category_delete, name='api_admin_category_delete'),
    path('api/admin/job-categories/<int:cat_id>/delete', views.api_admin_category_delete),
    path('api/admin/job-categories/<int:cat_id>/status/', views.api_admin_category_status, name='api_admin_category_status'),
    path('api/admin/job-categories/<int:cat_id>/status', views.api_admin_category_status),
    path('api/admin/job-categories/seed/', views.api_admin_category_seed, name='api_admin_category_seed'),
    path('api/admin/job-categories/seed', views.api_admin_category_seed),
]
