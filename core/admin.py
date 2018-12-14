from django.contrib import admin
from core.models import AddressType, ContactMechanismType, ContactMechanism, Team, ControlFirstAccessUser, EmailTemplate
#Todo: Remover office
from core.models import Office, Invite, InviteOffice, OfficeRelGroup, CustomSettings, Company, CompanyUser, City, \
    State, Country, AreaOfExpertise, OfficeNetwork
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


@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    filter_horizontal = ['persons', 'offices']
    search_fields = ['legal_name']
    list_display = ['legal_name', 'name', 'cpf_cnpj']


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


@admin.register(AreaOfExpertise)
class AreaOfExpertiseAdmin(admin.ModelAdmin):
    search_fields = ['area']

@admin.register(OfficeNetwork)
class OfficeNetworkAdmin(admin.ModelAdmin):
    search_fields = ['name', 'members__legal_name']
    list_display = ['name', 'list_members']
    filter_horizontal = ['members']


admin.site.register(AddressType)
admin.site.register(ControlFirstAccessUser)
admin.site.register(Country)
