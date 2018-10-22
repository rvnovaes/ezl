from django import forms
from core.models import Person, State, City
from core.utils import filter_valid_choice_form, get_office_field, get_office_related_office_field
from lawsuit.models import CourtDistrict, CourtDistrictComplement
from task.models import TypeTask
from .models import CostCenter, ServicePriceTable, ImportServicePriceTable
from decimal import Decimal
from core.forms import BaseModelForm, XlsxFileField
from core.widgets import TypeaHeadForeignKeyWidget


class CostCenterForm(BaseModelForm):
    legacy_code = forms.CharField(required=False)

    class Meta:
        model = CostCenter
        fields = ['office', 'name', 'legacy_code', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['office'] = get_office_field(self.request)


class ServicePriceTableForm(BaseModelForm):
    client = forms.CharField(label="Cliente",
                             required=False,
                             widget=TypeaHeadForeignKeyWidget(model=Person,
                                                              field_related='legal_name',
                                                              name='client',
                                                              url='/client_form'))

    state = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(State.objects.all().order_by('initials')),
        empty_label='',
        required=False,
        label='UF',
    )

    court_district = forms.CharField(label="Comarca",
                                     required=False,
                                     widget=TypeaHeadForeignKeyWidget(model=CourtDistrict,
                                                                      field_related='name',
                                                                      forward='state',
                                                                      name='court_district',
                                                                      url='/processos/typeahead/search/comarca'))

    court_district_complement = forms.CharField(label="Complemento de Comarca",
                                                required=False,
                                                widget=TypeaHeadForeignKeyWidget(
                                                    model=CourtDistrictComplement,
                                                    field_related='name',
                                                    forward='court_district',
                                                    name='court_district_complement',
                                                    url='/processos/typeahead/search/complemento',
                                                ))

    city = forms.CharField(label="Cidade", required=False,
                           widget=TypeaHeadForeignKeyWidget(
                               model=City,
                               field_related='name',
                               forward='state',
                               name='city',
                               url='/city/autocomplete/',
                           ))

    type_task = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(TypeTask.objects.all().order_by('name')),
        empty_label='',
        required=False,
        label=u"Tipo de Serviço",
    )

    value = forms.CharField(label="Valor",
                            localize=True,
                            required=False,
                            # O valor pode ser 0.00 porque os correspondentes internos não cobram para fazer serviço
                            widget=forms.TextInput(attrs={'mask': 'money'}))

    class Meta:
        model = ServicePriceTable
        fields = ('office', 'office_correspondent', 'client', 'type_task', 'state', 'court_district',
                  'court_district_complement', 'city', 'value', 'is_active')

    def clean_value(self):
        value = self.cleaned_data['value'] if self.cleaned_data['value'] != '' else '0,00'
        value = value.replace('.', '')
        value = value.replace(',', '.')
        return Decimal(value)

    def form_valid(self, form):
        if self.cleaned_data["state"] and self.cleaned_data["court_district"] \
            and not CourtDistrict.objects.filter(name=self.cleaned_data["court_district"].name,
                                                 state=self.cleaned_data["state"]):
            raise forms.ValidationError('A comarca selecionada não pertence à UF selecionada')
        if ServicePriceTable.objects.filter(type_task=self.cleaned_data["type_task"],
                                            court_district=self.cleaned_data["court_district"],
                                            state=self.cleaned_data["state"],
                                            client=self.cleaned_data["client"],
                                            office_correspondent=self.cleaned_data["office_correspondent"]).first():
            raise forms.ValidationError('Já existe um registro com os dados selecionados')
        return super().form_valid(form)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['office'] = get_office_field(self.request)
        self.fields['office_correspondent'] = get_office_related_office_field(self.request)
        self.fields['office_correspondent'].label = u"Escritório Correspondente"
        self.fields['office_correspondent'].required = True
        self.fields['office'].required = True


class ImportServicePriceTableForm(forms.ModelForm):
    file_xls = XlsxFileField(label='Arquivo', required=True,
                             headers_to_check=['Correspondente', 'Serviço', 'Cliente', 'Comarca', 'UF', 'Valor'])

    class Meta:
        model = ImportServicePriceTable
        fields = ('file_xls', )
