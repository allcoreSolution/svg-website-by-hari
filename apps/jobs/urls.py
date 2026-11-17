from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('api/jobs', views.jobs_list_api, name='jobs_list_api'),
    path('api/jobs/', views.jobs_list_api),
]
