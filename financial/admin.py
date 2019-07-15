from decimal import Decimal

from django.contrib import admin
from .models import ServicePriceTable, ImportServicePriceTable, PolicyPrice

@admin.register(ServicePriceTable)
class ServicePriceTableModelAdmin(admin.ModelAdmin):
    list_display = ['office',
                    'office_correspondent',
                    'court_district',
                    'court_district_complement',
                    'policy_price',
                    'type_task',
                    'state',
                    'city',
                    'value',
                    'office_network',
                    'is_active' ]
    search_fields = ['office__name']
    list_filter = ['is_active', 'state']
    change_form_template = 'financial/admin_change_form.html'
    add_form_template = change_form_template

    def response_change(self, request, obj):
        print(request.POST)
        if 'rate_commission_requestor' in request.POST and not request.POST['rate_commission_requestor'] == '':
            percent = Decimal(request.POST['rate_commission_requestor']) / 100
            if percent > 0:
                if obj.rate_type_receive == 'PERCENT':
                    obj.value_to_receive = abs((obj.value * percent) + obj.value)
                else:
                    obj.value_to_receive = abs(percent + obj.value)
            else:
                obj.value_to_receive = obj.value
        else:
            obj.value_to_receive = obj.value

        if 'rate_commission_correspondent' in request.POST and not request.POST['rate_commission_correspondent'] == '':
            percent = Decimal(request.POST['rate_commission_correspondent']) / 100
            if percent > 0:
                if obj.rate_type_receive == 'PERCENT':
                    obj.value_to_pay = abs((obj.value * percent) - obj.value)
                else:
                    obj.value_to_pay = abs(percent - obj.value)
            else:
                obj.value_to_pay = obj.value
        else:
            obj.value_to_pay = obj.value
        obj.save()

        return super().response_change(request, obj)

    def deactivate_price(self, request, queryset):
        rows_updated = queryset.update(
            is_active=False
        )
        if rows_updated == 1:
            message_bit = "1 preço foi inativado"
        else:
            message_bit = "%s preços foram inativados" % rows_updated
        self.message_user(request, "%s" % message_bit)

    deactivate_price.short_description = "Inativar preços em lote"

    def activate_price(self, request, queryset):
        rows_updated = queryset.update(
            is_active=True
        )
        if rows_updated == 1:
            message_bit = "1 preço foi inativado"
        else:
            message_bit = "%s preços foram inativados" % rows_updated
        self.message_user(request, "%s" % message_bit)

    activate_price.short_description = "Ativar preços em lote"
    actions = ['deactivate_price', 'activate_price']




@admin.register(ImportServicePriceTable)
class ImportServicePriceTableModelAdmin(admin.ModelAdmin):
	pass


@admin.register(PolicyPrice)
class PolicyPriceAdmin(admin.ModelAdmin):
	pass