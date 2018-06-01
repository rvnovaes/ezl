from django.contrib import admin
from .models import ServicePriceTable, ImportServicePriceTable


# Register your models here.


@admin.register(ServicePriceTable)
class ServicePriceTableModelAdmin(admin.ModelAdmin):
	pass

@admin.register(ImportServicePriceTable)
class ImportServicePriceTableModelAdmin(admin.ModelAdmin):
	pass
