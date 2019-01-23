from django.contrib import admin
from .models import ServicePriceTable, ImportServicePriceTable, PolicyPrice


# Register your models here.


@admin.register(ServicePriceTable)
class ServicePriceTableModelAdmin(admin.ModelAdmin):
	pass

@admin.register(ImportServicePriceTable)
class ImportServicePriceTableModelAdmin(admin.ModelAdmin):
	pass


@admin.register(PolicyPrice)
class PolicyPriceAdmin(admin.ModelAdmin):
	pass