from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from core.models import AddressType, ContactMechanismType, ContactMechanism, Team, ControlFirstAccessUser, EmailTemplate
#Todo: Remover office
from core.models import Office, Invite, InviteOffice, OfficeRelGroup, CustomSettings, Company, CompanyUser, City, \
    State, Country, OfficeNetwork, OfficeOffices
from task.models import TaskWorkflow, TaskShowStatus


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    pass


class TaskWorkflowInline(admin.TabularInline):
    model = TaskWorkflow
    fields = ('create_user', 'task_from', 'task_to', 'responsible_user')


class TaskShowStatusInline(admin.TabularInline):
    model = TaskShowStatus
    fields = ('create_user', 'status_to_show', 'send_mail_template', 'mail_recipients')


@admin.register(CustomSettings)
class CustomSettingsAdmin(admin.ModelAdmin):
    list_display = ('office', 'email_to_notification', 'default_customer', 'i_work_alone')
    inlines = [TaskShowStatusInline, TaskWorkflowInline]

    def save_form(self, request, form, change):
        return super().save_form(request, form, change)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    pass


@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ['company', 'user']


@admin.register(ContactMechanismType)
class ContactMechanismTypeAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'create_user', 'create_date', 'alter_user', 'alter_date'
    ]
    search_fields = ['name']
    list_filter = ['name']

    class Meta:
        verbose_name = 'Tipo de Contato'
        verbose_name_plural = 'Tipos de Contato'


@admin.register(ContactMechanism)
class ContactMechanism(admin.ModelAdmin):
    list_display = ['person', 'contact_mechanism_type', 'description']
    search_fields = ['person__legal_name', 'description']
    list_filter = ['contact_mechanism_type']

    class Meta:
        verbose_name = 'Mecanismo de Contato'
        verbose_name_plural = 'Mecanismos de Contato'


class VersionFilter(SimpleListFilter):
    title = 'Escritório de Origem'
    parameter_name = 'from_office__legal_name'
    template = 'admin/input_filter.html'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        return [(i, i) for i in qs.values_list('from_office__legal_name',
                                               flat=True).distinct().order_by('from_office__legal_name')]

    def choices(self, changelist):
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k == self.parameter_name
        )
        yield all_choice

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(from_office__legal_name__unaccent__icontains=self.value())


@admin.register(OfficeOffices)
class OfficeOfficesAdmin(admin.ModelAdmin):
    list_display = ['from_office', 'to_office', 'person_reference']
    search_fields = ['from_office__legal_name', 'to_office__legal_name']
    list_filter = (VersionFilter,)
    readonly_fields = ('from_office', 'to_office')

    def get_field_queryset(self, db, db_field, request):
        ret = super().get_field_queryset(db, db_field, request)
        if db_field.name == 'person_reference':
            office_id = list(request.resolver_match.args)
            ret = db_field.remote_field.model._default_manager.using(db).filter(
                offices__in=office_id).order_by('legal_name')
        return ret

    def get_fields(self, request, obj=None):
        if self.fields:
            return self.fields
        form = self.get_formset(request, obj, fields=None).form
        return list(self.get_readonly_fields(request, obj)) + list(form.base_fields)

    def has_add_permission(self, request):
        return False


@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    filter_horizontal = ['persons', 'offices']
    search_fields = ['legal_name', 'name']
    list_display = ['legal_name', 'cpf_cnpj']


@admin.register(Invite)
class InviteUserAdmin(admin.ModelAdmin):
    list_display = ['pk', 'create_user', 'person', 'office', 'status']
    fields = ['create_user', 'person', 'office', 'status']


@admin.register(InviteOffice)
class InviteOfficeAdmin(admin.ModelAdmin):
    list_display = ['pk', 'create_user', 'office_invite', 'office', 'status']
    fields = ['create_user', 'office_invite', 'office', 'status']


@admin.register(OfficeRelGroup)
class OfficeRelGroupAdmin(admin.ModelAdmin):
    list_display = ['pk', 'office', 'group']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    ordering = ('state', 'name')
    list_filter = ['state']
    list_display = ['name', 'state', 'court_district']
    search_fields = ['name']


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(OfficeNetwork)
class OfficeNetworkAdmin(admin.ModelAdmin):
    search_fields = ['name', 'members__legal_name']
    list_display = ['name', 'list_members']
    filter_horizontal = ['members']


admin.site.register(AddressType)
admin.site.register(ControlFirstAccessUser)
admin.site.register(Country)
