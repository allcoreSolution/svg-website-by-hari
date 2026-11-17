from django.urls import path
from . import views

app_name = 'placements'

urlpatterns = [
    path('api/placements', views.placements_api, name='placements_api'),
    path('api/placements/', views.placements_api),
    path('api/placement/<int:id>', views.placement_detail, name='placement_detail'),
    path('api/placement/<int:id>/', views.placement_detail),
    path('api/placements/<int:id>', views.placement_detail),
    path('api/placements/<int:id>/', views.placement_detail),
    path('api/job-offers', views.job_offers_api, name='job_offers_api'),
    path('api/job-offers/', views.job_offers_api),
    path('api/job-offer/<int:id>', views.delete_job_offer, name='delete_job_offer'),
    path('api/job-offer/<int:id>/', views.delete_job_offer),
    path('api/job-offers/<int:id>', views.delete_job_offer),
    path('api/job-offers/<int:id>/', views.delete_job_offer),
]
