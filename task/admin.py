from django.contrib import admin
from .models import TypeTask, TypeTaskMain
from .forms import TypeTaskMainForm


@admin.register(TypeTask)
class TypeTaskModelAdmin(admin.ModelAdmin):
    list_display = ['pk', 'office', 'name', 'survey', 'is_active']
    list_display_links = ['pk', 'name']
    search_fields = ['name', 'type_task_main__name', 'office__legal_name']
    fields = [
        'create_user', 'office', 'type_task_main', 'name', 'survey',
        'is_active'
    ]
    list_filter = ['is_active', 'type_task_main', 'office']
    ordering = ['office__legal_name', 'name']
    save_as = True


@admin.register(TypeTaskMain)
class TypeTaskMainAdmin(admin.ModelAdmin):
    form = TypeTaskMainForm
    list_display = ['pk', 'name', 'is_hearing']
    list_display_links = ['pk', 'name']
    search_fields = ['name', 'characteristics']
