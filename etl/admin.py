from etl.models import DashboardETL
from django.contrib import admin


class DashboardETLAdmin(admin.ModelAdmin):
    def time_seconds_start(self, obj):
        return obj.execution_date_start.strftime("%d-%m-%Y às %H:%M:%S")

    def time_seconds_finish(self, obj):
        if not obj.execution_date_finish:
            return '-'
        return obj.execution_date_finish.strftime("%d-%m-%Y às %H:%M:%S")

    time_seconds_start.short_description = 'Inicio'
    time_seconds_finish.short_description = 'Fim'
    list_display = ['time_seconds_start', 'time_seconds_finish', 'name']
    date_hierarchy = 'execution_date_start'

admin.site.register(DashboardETL, DashboardETLAdmin)
