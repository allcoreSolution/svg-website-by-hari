from django.contrib import admin
from .models import Placement, JobOffer

@admin.register(Placement)
class PlacementAdmin(admin.ModelAdmin):
    list_display = ('id', 'candidate_name', 'company_name', 'position', 'package', 'status', 'placement_date')
    search_fields = ('candidate_name', 'company_name', 'position')
    list_filter = ('status',)

@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'candidate_name', 'company_name', 'designation', 'offered_ctc', 'status', 'offer_date')
    search_fields = ('candidate_name', 'company_name', 'designation')
    list_filter = ('status',)
