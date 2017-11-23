from etl.models import DashboardETL, ErrorETL
from django.contrib import admin



class DashboardErrorInline(admin.TabularInline):
    model = ErrorETL
    fk_name = 'log'
    max_num = 1
    readonly_fields = ('create_date', 'error')
    fields = ('create_date', 'error',)


class DashboardETLAdmin(admin.ModelAdmin):
    readonly_fields = ('name', 'execution_date_start', 'execution_date_finish',
                       'read_quantity', 'imported_quantity', 'status',
                       'code_executed_query')

    def execution_date_start(self, instance):
        return instance.execution_date_start

    def time_seconds_start(self, obj):
        return obj.execution_date_start.strftime("%d-%m-%Y às %H:%M:%S")

    def time_seconds_finish(self, obj):
        if not obj.execution_date_finish:
            return '-'
        return obj.execution_date_finish.strftime("%d-%m-%Y às %H:%M:%S")

    def code_executed_query(self, instance):
        return '<pre>{}</pre>'.format(instance.executed_query)

    time_seconds_start.short_description = 'Inicio'
    time_seconds_finish.short_description = 'Fim'
    code_executed_query.allow_tags  = True
    list_display = ['name', 'time_seconds_start', 'time_seconds_finish',
                    'read_quantity', 'imported_quantity', 'status']
    date_hierarchy = 'execution_date_start'
    fields = ('name', 'execution_date_start', 'execution_date_finish',
              'read_quantity', 'imported_quantity',
              'status', 'code_executed_query')

    inlines = [
        DashboardErrorInline
    ]

admin.site.register(DashboardETL, DashboardETLAdmin)
