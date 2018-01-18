from django.core.urlresolvers import reverse_lazy
import django_tables2 as tables

from core.tables import CheckBoxMaterial
from .models import CostCenter, ServicePriceTable


class CostCenterTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    class Meta:
        sequence = ('selection', 'name', 'is_active', 'legacy_code')
        model = CostCenter
        fields = ['selection', 'name', 'is_active', 'legacy_code']
        attrs = {"class": "table stable-striped table-bordered"}
        empty_text = "Não existem centros de custo cadastrados"
        row_attrs = {
            'data_href': lambda record: '/financeiro/centros-de-custos/' + str(record.pk) + '/'
        }
        order_by = 'name'


class ServicePriceTableTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)
    value = tables.Column(attrs={"editable": True, "mask": "money"})

    class Meta:
        sequence = ('selection', 'office', 'type_task', 'court_district', 'state', 'client', 'value')
        model = ServicePriceTable
        fields = ('selection', 'office', 'type_task', 'court_district', 'state', 'client', 'value')
        attrs = {"class": "table stable-striped table-bordered"}
        empty_text = "Não existe tabela de preços cadastrada."
        row_attrs = {
            'data_href': lambda record: reverse_lazy('servicepricetable_update', args=(record.pk,))
        }
        order_by = 'office'


class ServicePriceTableTaskTable(tables.Table):
    office = tables.Column(orderable=False)
    court_district = tables.Column(orderable=False)
    state = tables.Column(orderable=False)
    client = tables.Column(orderable=False)
    value = tables.Column(orderable=False)

    class Meta:
        sequence = ('office', 'court_district', 'state', 'client', 'value')
        model = ServicePriceTable
        fields = ('office', 'court_district', 'state', 'client', 'value')
        attrs = {"class": "table stable-striped table-bordered correspondents-table", "id": "correspondents-table"}
        empty_text = "Não existe tabela de preços cadastrada."
        order_by = ("value",)
        row_attrs = {
            'data-id': lambda record: record.pk,
            'data-value': lambda record: record.value,
            'class': 'tr_select'
        }
