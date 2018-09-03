from django.contrib import admin
from .models import TypeTask, TypeTaskMain
from .forms import TypeTaskMainForm
# Register your models here.


@admin.register(TypeTask)
class TypeTaskModelAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'survey', 'is_active']
    list_display_links = ['pk', 'name']
    search_fields = ['name']
    fields = ['create_user', 'name', 'survey', 'is_active']
    list_filter = ['is_active']
    ordering = ['name']


@admin.register(TypeTaskMain)
class TypeTaskMainAdmin(admin.ModelAdmin):
    form = TypeTaskMainForm
