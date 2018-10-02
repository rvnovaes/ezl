import django_tables2 as tables
from core.tables import CheckBoxMaterial

from .models import Survey


class SurveyTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    class Meta:
        sequence = (
            'selection',
            'name',
        )
        model = Survey
        fields = ['name']
        attrs = {"class": "table stable-striped table-bordered"}
        empty_text = "Não existem questionários cadastrados"
        row_attrs = {
            'data_href':
            lambda record: '/pesquisa/pesquisas/' + str(record.pk) + '/'
        }
        order_by = 'id'
