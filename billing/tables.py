import django_tables2 as tables
from .models import BillingDetails
from core.tables import CheckBoxMaterial


class BillingDetailsTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    class Meta:
        model = BillingDetails
        sequecence = (
            'selection', 'card_name', 'email', 'cpf_cnpj', 'birth_date', 'phone_number', 'billing_address'
        )
        fields = [
            'selection', 'card_name', 'email', 'cpf_cnpj', 'birth_date', 'phone_number', 'billing_address'
        ]
        attrs = {"class": "table-striped table-bordered"}
        row_attrs = {
            'pk': lambda record: str(record.pk),
            'data_href': lambda record: '/billing_details/' + str(record.pk) + '/'
        }
