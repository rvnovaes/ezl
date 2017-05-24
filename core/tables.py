import django_tables2 as tables
from django_tables2 import TemplateColumn
from django_tables2.utils import A  # alias for Accessor

from .models import Person


class PersonTable(tables.Table):
    selection = TemplateColumn(
        '<div class="checkbox"><label><input type="checkbox" value="{{ record.pk }}" /></label></div>',
        verbose_name='', accessor='pk', attrs={'th__input':
                                                   {'onclick': 'toggle( this)'}}, orderable=False)

    name = tables.LinkColumn(viewname='person_update', attrs={'a': {'target': '_blank'}}, args=[A('pk')])

    class Meta:
        sequecence = (
            'selection', 'name', 'is_lawyer', 'is_corresponding', 'is_court', 'legal_type', 'auth_user',
            'cpf_cnpj')
        model = Person
        fields = ['selection', 'name', 'is_lawyer', 'is_corresponding', 'is_court', 'legal_type', 'auth_user',
                  'cpf_cnpj']
        attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem pessoas cadastradas"
