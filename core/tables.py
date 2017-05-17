import django_tables2 as tables
from django_tables2.utils import A
from .models import Person


class PersonTable(tables.Table):
    #legal_name = tables.LinkColumn('', args=[A('pk')])
    #name = tables.LinkColumn('', args=[A('pk')])
    #auth_user = tables.LinkColumn('', args=[A('pk')])

    class Meta:
        model = Person
        fields = ['legal_name', 'name', 'is_lawyer', 'is_corresponding', 'legal_type', 'auth_user', 'active']
        attrs = {"class": "table-striped table-bordered"}
        empty_text = "There are no customers matching the search criteria..."
