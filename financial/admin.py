from django.contrib import admin
from .models import ServicePriceTable


# Register your models here.


@admin.register(ServicePriceTable)
class ServicePriceTableModelAdmin(admin.ModelAdmin):
	pass

