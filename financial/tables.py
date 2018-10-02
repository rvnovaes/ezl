from django.core.urlresolvers import reverse_lazy
import django_tables2 as tables

from core.tables import CheckBoxMaterial
from .models import CostCenter, ServicePriceTable
from djmoney.money import Money


class CostCenterTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)
    court_district_complement = tables.Column(orderable=False, verbose_name='Complemento')

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
        sequence = ('selection', 'office', 'office_correspondent', 'type_task', 'state', 'court_district',
                    'court_district_complement', 'client', 'value')
        model = ServicePriceTable
        fields = ('selection', 'office', 'office_correspondent', 'type_task', 'court_district', 'state', 'client',
                  'value', 'is_active', 'court_district_complement')
        attrs = {"class": "table stable-striped table-bordered"}
        empty_text = "Não existe tabela de preços cadastrada."
        row_attrs = {
            'data_href': lambda record: reverse_lazy('servicepricetable_update', args=(record.pk,))
        }
        order_by = 'office'


class ServicePriceTableTaskTable(tables.Table):
    office_correspondent = tables.Column(orderable=False, verbose_name='Escritório correspondente')
    court_district = tables.Column(orderable=False, verbose_name='Comarca')
    court_district_complement = tables.Column(orderable=False, verbose_name='Complemento da comarca')
    state = tables.Column(orderable=False, verbose_name='UF')
    client = tables.Column(orderable=False, verbose_name='Cliente')
    value = tables.Column(orderable=False, verbose_name='Valor')
    office_rating = tables.Column(orderable=False, verbose_name='Avaliação*')
    office_return_rating = tables.Column(orderable=False, verbose_name='OS Retornadas')

    class Meta:
        sequence = ('office_correspondent', 'state', 'court_district', 'court_district_complement', 'client', 'value')
        model = ServicePriceTable
        fields = ('office_correspondent', 'court_district', 'state', 'client', 'value', 'court_district_complement',
                  'office_rating', 'office_return_rating')
        attrs = {"class": "table stable-striped table-bordered correspondents-table", "id": "correspondents-table"}
        empty_text = "Não existe tabela de preços cadastrada para o tipo de serviço selecionado."
        order_by = ("value", "office_rating", "office_return_rating", "office_correspondent__legal_name")
        row_attrs = {
            'id': lambda record: 'office-{}'.format(record.pk),
            'data-id': lambda record: record.pk,
            'data-value': lambda record: record.value,
            'data-formated-value': lambda record: Money(record.value, 'BRL').__str__(),
            'data-office-public': lambda record: record.office_correspondent.public_office,
            'class': 'tr_select'
        }
