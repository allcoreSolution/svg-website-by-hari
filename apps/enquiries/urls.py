from django.urls import path
from . import views

app_name = 'enquiries'

urlpatterns = [
    # Public contact endpoint
    path('api/contact', views.contact, name='contact'),
    path('api/contact/', views.contact),

    # Legacy / Admin contact endpoints
    path('api/contacts', views.get_contacts, name='get_contacts'),
    path('api/contacts/', views.get_contacts),
    path('api/contact/<int:id>', views.contact_detail, name='contact_detail'),
    path('api/contact/<int:id>/', views.contact_detail),

    # Unified Enquiries Admin REST APIs
    path('api/enquiries', views.api_enquiries_list, name='api_enquiries_list'),
    path('api/enquiries/', views.api_enquiries_list),
    path('api/enquiry/mark-read', views.mark_enquiry_read, name='mark_enquiry_read'),
    path('api/enquiry/mark-read/', views.mark_enquiry_read),
    path('api/enquiry/mark-unread', views.mark_enquiry_unread, name='mark_enquiry_unread'),
    path('api/enquiry/mark-unread/', views.mark_enquiry_unread),
    path('api/enquiry/bulk-status', views.bulk_status_enquiry, name='bulk_status_enquiry'),
    path('api/enquiry/bulk-status/', views.bulk_status_enquiry),
    path('api/enquiry/mark-spam', views.mark_enquiry_spam, name='mark_enquiry_spam'),
    path('api/enquiry/mark-spam/', views.mark_enquiry_spam),
    path('api/enquiry/restore', views.restore_enquiry, name='restore_enquiry'),
    path('api/enquiry/restore/', views.restore_enquiry),
    path('api/enquiry/counts', views.enquiry_counts_api, name='enquiry_counts_api'),
    path('api/enquiry/counts/', views.enquiry_counts_api),
    path('api/enquiry/export.csv', views.export_enquiries_csv, name='export_enquiries_csv'),
    path('api/enquiry/export.csv/', views.export_enquiries_csv),

    # Follow-ups endpoints
    path('api/follow-ups', views.follow_ups_api, name='follow_ups_api'),
    path('api/follow-ups/', views.follow_ups_api),
    path('api/follow-up/<int:id>', views.delete_follow_up, name='delete_follow_up'),
    path('api/follow-up/<int:id>/', views.delete_follow_up),
]
