from django.contrib import admin
from .models import Job, JobCategory

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'location', 'employment_type', 'status', 'created_at')
    search_fields = ('title', 'category', 'department', 'location')
    list_filter = ('status', 'employment_type')

@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category_type', 'count_label', 'field_slug', 'order', 'status')
    list_filter = ('category_type', 'status')
    search_fields = ('name', 'field_slug', 'count_label')
    list_editable = ('order', 'status')

