from django.contrib import admin
from core.models import AddressType, ContactMechanismType, ContactMechanism

# Todo: Remover office
from core.models import Office, Invite


# Register your models here.


class ContactMechanismTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'create_user', 'create_date', 'alter_user', 'alter_date']
    search_fields = ['name']
    list_filter = ['name']

    class Meta:
        verbose_name = 'Tipo de Contato'
        verbose_name_plural = 'Tipos de Contato'


class InviteUserAdmin(admin.ModelAdmin):
    list_display = ['pk', 'create_user', 'person', 'office', 'status']
    fields = ['create_user', 'person', 'office', 'status']


admin.site.register(AddressType)
admin.site.register(ContactMechanism)
admin.site.register(ContactMechanismType, ContactMechanismTypeAdmin)
admin.site.register(Office)
admin.site.register(Invite, InviteUserAdmin)
