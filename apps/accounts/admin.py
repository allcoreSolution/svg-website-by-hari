from django.contrib import admin
from .models import AdminUser

@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'is_active', 'created_at')
    search_fields = ('email',)
