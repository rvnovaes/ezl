from django.contrib import admin
from lawsuit.models import CourtDistrict


@admin.register(CourtDistrict)
class ContactMechanism(admin.ModelAdmin):
    list_display = ['name', 'state']
    search_fields = ['name']
    list_filter = ['state__initials']
