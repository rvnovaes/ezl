from django.contrib import admin
from core.models import AddressType, ContactMechanismType, ContactMechanism, Team, ControlFirstAccessUser
#Todo: Remover office
from core.models import Office, Invite, InviteOffice, OfficeRelGroup, CustomSettings
from task.models import TaskWorkflow, TaskShowStatus



class TaskWorkflowInline(admin.TabularInline):
    model = TaskWorkflow
    fields = ('create_user', 'task_from', 'task_to', 'responsible_user')

class TaskShowStatusInline(admin.TabularInline):
    model = TaskShowStatus
    fields = ('create_user', 'status_to_show')


@admin.register(CustomSettings)
class CustomSettingsAdmin(admin.ModelAdmin):
    list_display = ('office', 'email_to_notification', 'i_work_alone')
    inlines = [
        TaskShowStatusInline,
        TaskWorkflowInline
    ]

@admin.register(ContactMechanismType)
class ContactMechanismTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'create_user', 'create_date', 'alter_user', 'alter_date']
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
    list_display = ['name', 'auth_user']


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

admin.site.register(AddressType)
admin.site.register(ControlFirstAccessUser)