import django_tables2 as tables
from .models import TemplateAnswers


class TemplateAnswersTable(tables.Table):

    description = tables.Column(accessor='template.description')

    class Meta:
        model = TemplateAnswers
        fields = ['template', 'description', 'answers']
        attrs = {"class": "table-striped table-bordered"}
        row_attrs = {
            'data_href': lambda record: '/teams/' + str(record.pk) + '/'
        }