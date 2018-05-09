from django.contrib import admin
from billing.models import Plan


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'month_value', 'task_limit']
    search_fields = ['name', 'description']

    class Meta:
        verbose_name = 'Plano'
        verbose_name_plural = 'Planos'
