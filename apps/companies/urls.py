from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    # Public Hiring Requirement Submission
    path('api/company-enquiry', views.create_company_enquiry, name='create_company_enquiry'),
    path('api/company-enquiry/', views.create_company_enquiry),

    # Admin Enquiry Management
    path('api/company-enquiries', views.get_company_enquiries, name='get_company_enquiries'),
    path('api/company-enquiries/', views.get_company_enquiries),
    path('api/company-enquiry/<int:id>', views.company_enquiry_detail, name='company_enquiry_detail'),
    path('api/company-enquiry/<int:id>/', views.company_enquiry_detail),
    path('api/company-enquiry/<int:id>/convert', views.convert_company_enquiry_api, name='convert_company_enquiry'),
    path('api/company-enquiry/<int:id>/convert/', views.convert_company_enquiry_api),
    path('api/company-enquiry/<int:id>/approve-publish', views.approve_publish_company_enquiry_api, name='approve_publish_company_enquiry'),
    path('api/company-enquiry/<int:id>/approve-publish/', views.approve_publish_company_enquiry_api),

    # Admin Companies CRUD
    path('api/companies', views.companies_api, name='companies_api'),
    path('api/companies/', views.companies_api),
    path('api/companies/<int:id>', views.company_detail_api, name='company_detail_api'),
    path('api/companies/<int:id>/', views.company_detail_api),

    # Admin Company Contacts CRUD
    path('api/company-contacts', views.company_contacts_api, name='company_contacts_api'),
    path('api/company-contacts/', views.company_contacts_api),
    path('api/company-contacts/<int:id>', views.company_contact_detail_api, name='company_contact_detail_api'),
    path('api/company-contacts/<int:id>/', views.company_contact_detail_api),
    path('api/company-contacts/<int:id>/set-primary', views.set_primary_contact_api, name='set_primary_contact_api'),
    path('api/company-contacts/<int:id>/set-primary/', views.set_primary_contact_api),

    # Admin Company Requirements CRUD
    path('api/company-requirements', views.company_requirements_api, name='company_requirements_api'),
    path('api/company-requirements/', views.company_requirements_api),
    path('api/company-requirements/<int:id>', views.company_requirement_detail_api, name='company_requirement_detail_api'),
    path('api/company-requirements/<int:id>/', views.company_requirement_detail_api),
    path('api/company-requirements/<int:id>/publish', views.publish_company_requirement_api, name='publish_company_requirement_api'),
    path('api/company-requirements/<int:id>/publish/', views.publish_company_requirement_api),
    path('api/company-requirements/<int:id>/close', views.close_company_requirement_api, name='close_company_requirement_api'),
    path('api/company-requirements/<int:id>/close/', views.close_company_requirement_api),
    path('api/company-requirements/<int:id>/reopen', views.reopen_company_requirement_api, name='reopen_company_requirement_api'),
    path('api/company-requirements/<int:id>/reopen/', views.reopen_company_requirement_api),
    path('api/company-requirements/<int:id>/reject', views.reject_company_requirement_api, name='reject_company_requirement_api'),
    path('api/company-requirements/<int:id>/reject/', views.reject_company_requirement_api),

    # Admin Job Openings CRUD
    path('api/admin/jobs', views.admin_jobs_api, name='admin_jobs_api'),
    path('api/admin/jobs/', views.admin_jobs_api),
    path('api/admin/jobs/<int:id>', views.admin_job_detail_api, name='admin_job_detail_api'),
    path('api/admin/jobs/<int:id>/', views.admin_job_detail_api),

    # Admin Employer / Company Posted Jobs & Applications Overview
    path('api/admin/companies/jobs', views.admin_company_jobs_api, name='admin_company_jobs_query_api'),
    path('api/admin/companies/jobs/', views.admin_company_jobs_api),
    path('api/admin/companies/<int:id>/jobs', views.admin_company_jobs_api, name='admin_company_jobs_api'),
    path('api/admin/companies/<int:id>/jobs/', views.admin_company_jobs_api),
    path('api/admin/employers/<int:id>/jobs', views.admin_company_jobs_api),
    path('api/admin/employers/<int:id>/jobs/', views.admin_company_jobs_api),
]
