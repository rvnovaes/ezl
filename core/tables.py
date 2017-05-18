import django_tables2 as tables
from .models import Person


class PersonTable(tables.Table):
    class Meta:
        model = Person
        fields = ['legal_name', 'name', 'is_lawyer', 'is_corresponding', 'legal_type', 'auth_user', 'active']
        attrs = {"class": "table-striped table-bordered"}
        empty_text = "There are no customers matching the search criteria..."
