from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('about/company/', views.about_company, name='about_company'),
    path('about/team/', views.ourteam, name='ourteam'),
    path('about/ceo/', views.ceo, name='ceo'),
    path('about/journey/', views.ourjourney, name='ourjourney'),
    # Canonical Service Routes
    path('services/', views.services, name='services'),
    path('services/manpower-supply/', views.manpower_supply, name='manpower_supply'),
    path('services/recruitment-placement/', views.recruitment_placement, name='recruitment_placement'),
    path('services/contract-staffing/', views.contract_staffing, name='contract_staffing'),
    path('services/educational-consultancy/', views.educational_consultancy, name='educational_consultancy'),
    path('services/payroll-outsourcing/', views.payroll_outsourcing, name='payroll_outsourcing'),
    path('services/hr-support/', views.hr_support, name='hr_support'),
    path('services/internship/', views.internship, name='internship'),

    # Direct Service URL Aliases (support direct /contract-staffing/, etc.)
    path('contract-staffing/', views.contract_staffing, name='contract_staffing_direct'),
    path('contract-staffing.html', views.contract_staffing, name='contract_staffing_html_alias'),
    path('contract-staffing', views.contract_staffing, name='contract_staffing_no_slash'),

    path('manpower-supply/', views.manpower_supply, name='manpower_supply_direct'),
    path('manpower-supply.html', views.manpower_supply, name='manpower_supply_html_alias'),
    path('manpower-supply', views.manpower_supply, name='manpower_supply_no_slash'),

    path('recruitment-placement/', views.recruitment_placement, name='recruitment_placement_direct'),
    path('recruitment-placement.html', views.recruitment_placement, name='recruitment_placement_html_alias'),
    path('recruitment-Placement.html', views.recruitment_placement, name='recruitment_placement_case_alias'),
    path('recruitment-placement', views.recruitment_placement, name='recruitment_placement_no_slash'),

    path('educational-consultancy/', views.educational_consultancy, name='educational_consultancy_direct'),
    path('educational-consultancy.html', views.educational_consultancy, name='educational_consultancy_html_alias'),
    path('educational-consultancy', views.educational_consultancy, name='educational_consultancy_no_slash'),

    path('payroll-outsourcing/', views.payroll_outsourcing, name='payroll_outsourcing_direct'),
    path('payroll-outsourcing.html', views.payroll_outsourcing, name='payroll_outsourcing_html_alias'),
    path('payroll-outsourcing', views.payroll_outsourcing, name='payroll_outsourcing_no_slash'),

    path('hr-support/', views.hr_support, name='hr_support_direct'),
    path('hr-support.html', views.hr_support, name='hr_support_html_alias'),
    path('hr-support', views.hr_support, name='hr_support_no_slash'),

    path('internship/', views.internship, name='internship_direct'),
    path('internship.html', views.internship, name='internship_html_alias'),
    path('internship', views.internship, name='internship_no_slash'),

    # About Subpages Direct Aliases
    path('about-company/', views.about_company, name='about_company_direct'),
    path('about_company.html', views.about_company, name='about_company_html_alias'),
    path('about.html', views.about, name='about_html_alias'),

    path('ceo/', views.ceo, name='ceo_direct'),
    path('CEO.html', views.ceo, name='ceo_html_alias'),

    path('our-team/', views.ourteam, name='ourteam_direct'),
    path('team/', views.ourteam, name='team_direct'),
    path('ourteam.html', views.ourteam, name='ourteam_html_alias'),

    path('our-journey/', views.ourjourney, name='ourjourney_direct'),
    path('journey/', views.ourjourney, name='journey_direct'),
    path('ourjourney.html', views.ourjourney, name='ourjourney_html_alias'),

    # Core Pages & Static HTML Aliases
    path('careers/', views.careers, name='careers'),
    path('careers.html', views.careers, name='careers_html_alias'),

    path('job/', views.job, name='job'),
    path('job', views.job, name='job_no_slash'),
    path('jobs/', views.job, name='jobs'),
    path('job.html', views.job, name='job_html_alias'),
    path('jobs', views.job, name='jobs_no_slash_alias'),

    path('index.html', views.home, name='index_html_alias'),
    path('services.html', views.services, name='services_html_alias'),

    path('gallery/', views.gallery, name='gallery'),
    path('gallery.html', views.gallery, name='gallery_html_alias'),

    path('blog/', views.blog, name='blog'),
    path('blog.html', views.blog, name='blog_html_alias'),

    path('contact/', views.contact, name='contact'),
    path('contact.html', views.contact, name='contact_html_alias'),
]
