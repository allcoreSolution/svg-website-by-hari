from django.urls import path
from apps.ledger import views

urlpatterns = [
    # Admin UI views
    path('admin-panel/ledger/', views.ledger_list_view, name='ledger_list'),
    path('admin-panel/ledger', views.ledger_list_view),
    path('admin-panel/ledger/<int:id>/', views.ledger_detail_view, name='ledger_detail'),
    path('admin-panel/ledger/payments/', views.payments_list_view, name='ledger_payments'),
    path('admin-panel/ledger/payments', views.payments_list_view),
    path('admin-panel/ledger/receipt/<int:entry_id>/', views.receipt_print_view, name='ledger_receipt_print'),

    # REST APIs
    path('api/admin/ledger/', views.api_ledger_list, name='api_ledger_list'),
    path('api/admin/ledger', views.api_ledger_list),
    path('api/admin/ledger/<int:id>/', views.api_ledger_detail, name='api_ledger_detail'),
    path('api/admin/ledger/<int:id>/payment/', views.api_ledger_record_payment, name='api_ledger_record_payment'),
    path('api/admin/ledger/<int:id>/salary/', views.api_ledger_update_salary, name='api_ledger_update_salary'),
    path('api/admin/ledger/<int:id>/waive/', views.api_ledger_waive, name='api_ledger_waive'),
    path('api/admin/ledger/<int:id>/payer/', views.api_ledger_change_payer, name='api_ledger_change_payer'),
    path('api/admin/ledger/sync/', views.api_ledger_sync, name='api_ledger_sync'),
    path('api/admin/ledger/payments/', views.api_ledger_payments, name='api_ledger_payments'),
    path('api/admin/ledger/export/', views.api_ledger_export_csv, name='api_ledger_export_csv'),
]
