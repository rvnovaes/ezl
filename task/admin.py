from django.contrib import admin
from .models import TypeTask, TypeTaskMain
from .forms import TypeTaskMainForm
# Register your models here.


@admin.register(TypeTask)
class TypeTaskModelAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'type_task_main', 'survey', 'is_active']
    list_display_links = ['pk', 'name']
    search_fields = ['name', 'type_task_main__name']
    fields = ['create_user', 'office', 'type_task_main', 'name', 'survey', 'is_active']
    list_filter = ['is_active', 'type_task_main']
    ordering = ['name']


@admin.register(TypeTaskMain)
class TypeTaskMainAdmin(admin.ModelAdmin):
    form = TypeTaskMainForm
