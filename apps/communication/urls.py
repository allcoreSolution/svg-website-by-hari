from django.urls import path
from . import views

urlpatterns = [
    # Admin Communication Module
    path('admin-panel/communication/compose/', views.compose_view, name='communication_compose'),
    path('admin-panel/communication/preview-recipients/', views.preview_recipients_api, name='communication_preview'),
    path('admin-panel/communication/send/', views.send_bulk_message_api, name='communication_send'),
    path('admin-panel/communication/send-test/', views.send_test_email_api, name='communication_send_test'),
    path('admin-panel/communication/history/', views.history_view, name='communication_history'),
    path('admin-panel/communication/history/<int:id>/', views.history_detail_view, name='communication_history_detail'),
    path('admin-panel/communication/history/<int:id>/status/', views.bulk_message_status_api, name='communication_status_poll'),
    path('admin-panel/communication/history/<int:id>/stop/', views.stop_sending_api, name='communication_stop'),
    path('admin-panel/communication/history/<int:id>/export-csv/', views.export_recipients_csv_api, name='communication_export_csv'),
    path('admin-panel/communication/history/<int:id>/send-draft/', views.send_draft_api, name='communication_send_draft'),
    path('admin-panel/communication/history/<int:id>/retry/', views.retry_failed_api, name='communication_retry'),

    # Templates CRUD
    path('admin-panel/communication/templates/', views.templates_view, name='communication_templates'),
    path('admin-panel/communication/templates/<int:id>/json/', views.template_json_api, name='communication_template_json'),
    path('admin-panel/communication/templates/save/', views.template_save_api, name='communication_template_save'),
    path('admin-panel/communication/templates/<int:id>/delete/', views.template_delete_api, name='communication_template_delete'),

    # Delivery Settings
    path('admin-panel/communication/settings/', views.delivery_settings_view, name='communication_settings'),

    # Redirects for old notification URLs
    path('admin-panel/notifications/email/', views.notifications_email_redirect),
    path('admin-panel/notifications/send/', views.notifications_send_redirect),
    path('admin-panel/notifications/all/', views.notifications_all_redirect),

    # Candidate Portal Messages
    path('candidate/messages/', views.candidate_inbox_view, name='candidate_inbox'),
    path('api/candidate/messages/unread-count/', views.candidate_unread_count_api, name='candidate_unread_count'),
    path('api/candidate/messages/<int:id>/read/', views.candidate_mark_read_api, name='candidate_mark_read'),
    path('api/candidate/messages/mark-all-read/', views.candidate_mark_all_read_api, name='candidate_mark_all_read'),

    # Employer Portal Messages
    path('employer/messages/', views.employer_inbox_view, name='employer_inbox'),
    path('api/employer/messages/unread-count/', views.employer_unread_count_api, name='employer_unread_count'),
    path('api/employer/messages/<int:id>/read/', views.employer_mark_read_api, name='employer_mark_read'),
    path('api/employer/messages/mark-all-read/', views.employer_mark_all_read_api, name='employer_mark_all_read'),
]
