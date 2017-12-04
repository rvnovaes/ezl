import django_tables2 as tables

from core.tables import CheckBoxMaterial
from .models import CostCenter


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
