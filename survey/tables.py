import django_tables2 as tables

from .models import Survey


class SurveyTable(tables.Table):

    class Meta:
        sequence = ('name',)
        model = Survey
        fields = ['name']
        attrs = {"class": "table stable-striped table-bordered"}
        empty_text = "Não existem pesquisas cadastradas"
        row_attrs = {
            'data_href': lambda record: '/pesquisa/pesquisas/' + str(record.pk) + '/'
        }
        order_by = 'id'
