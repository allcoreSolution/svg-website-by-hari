from django.urls import path
from . import views

app_name = 'internships'

urlpatterns = [
    # Enquiry APIs (existing)
    path('api/internship-enquiry', views.create_internship_enquiry, name='create_internship_enquiry'),
    path('api/internship-enquiry/', views.create_internship_enquiry),
    path('api/internship-enquiries', views.get_internship_enquiries, name='get_internship_enquiries'),
    path('api/internship-enquiries/', views.get_internship_enquiries),
    path('api/internship-enquiry/<int:id>', views.internship_enquiry_detail, name='internship_enquiry_detail'),
    path('api/internship-enquiry/<int:id>/', views.internship_enquiry_detail),
    path('api/internship-enquiry/<int:id>/convert', views.convert_enquiry_to_application_api, name='convert_enquiry_to_application'),
    path('api/internship-enquiry/<int:id>/convert/', views.convert_enquiry_to_application_api),

    # Internship Provider APIs
    path('api/internship-providers', views.internship_providers_api, name='internship_providers_api'),
    path('api/internship-providers/', views.internship_providers_api),
    path('api/internship-providers/<int:id>', views.internship_provider_detail_api, name='internship_provider_detail_api'),
    path('api/internship-providers/<int:id>/', views.internship_provider_detail_api),

    # Internship APIs
    path('api/internships', views.internships_api, name='internships_api'),
    path('api/internships/', views.internships_api),
    path('api/internships/<int:id>', views.internship_detail_api, name='internship_detail_api'),
    path('api/internships/<int:id>/', views.internship_detail_api),
    path('api/internships/<int:id>/status', views.internship_change_status_api, name='internship_change_status_api'),
    path('api/internships/<int:id>/status/', views.internship_change_status_api),

    # Internship Application APIs
    path('api/internship-applications', views.internship_applications_api, name='internship_applications_api'),
    path('api/internship-applications/', views.internship_applications_api),
    path('api/internship-applications/<int:id>', views.internship_application_detail_api, name='internship_application_detail_api'),
    path('api/internship-applications/<int:id>/', views.internship_application_detail_api),

    # Public APIs
    path('api/internship-apply', views.public_internship_apply_api, name='public_internship_apply_api'),
    path('api/internship-apply/', views.public_internship_apply_api),
    path('api/public/internships', views.public_internships_api, name='public_internships_api'),
    path('api/public/internships/', views.public_internships_api),
]
