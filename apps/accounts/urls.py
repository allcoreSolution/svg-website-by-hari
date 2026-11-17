from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('api/admin/login', views.admin_login, name='admin_login'),
    path('api/admin/login/', views.admin_login),
    path('api/admin/logout', views.admin_logout, name='admin_logout'),
    path('api/admin/logout/', views.admin_logout),
    path('api/admin/me', views.admin_me, name='admin_me'),
    path('api/admin/me/', views.admin_me),
    path('api/admin/forgot-password', views.admin_forgot_password, name='admin_forgot_password'),
    path('api/admin/forgot-password/', views.admin_forgot_password),
    path('api/admin/reset-password', views.admin_reset_password, name='admin_reset_password'),
    path('api/admin/reset-password/', views.admin_reset_password),
    path('api/admin/users', views.admin_users_api, name='admin_users_api'),
    path('api/admin/users/', views.admin_users_api),
    path('api/admin/users/<int:id>', views.admin_user_detail_api, name='admin_user_detail_api'),
    path('api/admin/users/<int:id>/', views.admin_user_detail_api),
]
