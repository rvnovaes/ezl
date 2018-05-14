from django.contrib import admin
from .models import TypeTask
# Register your models here.


@admin.register(TypeTask)
class TypeTaskModelAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'survey', 'simple_service', 'is_active']
    list_display_links = ['pk', 'name']
    search_fields = ['name']
    fields = ['create_user', 'name', 'survey', 'simple_service', 'is_active']
    list_filter = ['simple_service', 'is_active']
    ordering = ['name']
