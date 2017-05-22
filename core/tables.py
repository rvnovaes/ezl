import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor

from .models import Person


class PersonTable(tables.Table):
    name = tables.LinkColumn(viewname='person_update', attrs={'a': {'target': '_blank'}}, args=[A('pk')])

    class Meta:
        model = Person
        fields = ['name', 'is_lawyer', 'is_corresponding', 'legal_type', 'auth_user', 'active', 'cpf_cnpj']
        attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem pessoas cadastradas"
