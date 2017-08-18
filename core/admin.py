from django.contrib import admin
from core.models import AddressType, ContactMechanismType, ContactMechanism
# Register your models here.

admin.site.register(AddressType)
admin.site.register(ContactMechanism)
admin.site.register(ContactMechanismType)
