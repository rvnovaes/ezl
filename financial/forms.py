from django import forms
from core.models import Person, State, City
from core.utils import filter_valid_choice_form, get_office_field, get_office_related_office_field, get_office_session
from lawsuit.models import CourtDistrict, CourtDistrictComplement
from task.models import TypeTask
from .models import CostCenter, ServicePriceTable, ImportServicePriceTable, PolicyPrice
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
    policy_price = forms.ModelChoiceField(
      queryset=PolicyPrice.objects.all(),
      empty_label='', 
      required=True, 
      label='Política de preço'
    )    
    value = forms.CharField(label="Valor",
                            localize=True,
                            required=False,
                            # O valor pode ser 0.00 porque os correspondentes internos não cobram para fazer serviço
                            widget=forms.TextInput(attrs={'mask': 'money'}))

    class Meta:
        model = ServicePriceTable
        fields = ('office', 'office_correspondent', 'office_network', 'client', 'type_task', 'state', 'court_district',
                  'court_district_complement', 'city', 'policy_price', 'value', 'is_active')

    def clean_value(self):
        value = self.cleaned_data['value'] if self.cleaned_data['value'] != '' else '0,00'
        value = value.replace('.', '')
        value = value.replace(',', '.')
        return Decimal(value)

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data["court_district"] and cleaned_data["court_district_complement"]:
            cleaned_data["court_district"] = self.cleaned_data["court_district_complement"].court_district
        if not cleaned_data["state"] and cleaned_data['court_district']:
            cleaned_data["state"] = cleaned_data['court_district'].state
        elif not cleaned_data["state"] and cleaned_data['city']:
            cleaned_data["state"] = cleaned_data['city'].state
        if cleaned_data["state"] and cleaned_data["court_district"] \
            and not CourtDistrict.objects.filter(name=cleaned_data["court_district"].name,
                                                 state=cleaned_data["state"]):
            raise forms.ValidationError('A comarca selecionada não pertence à UF selecionada')
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        office_session = get_office_session(self.request)
        self.fields['office'] = get_office_field(self.request)
        if self.fields['office'].initial == office_session.id:
            self.fields['office'].widget = forms.HiddenInput()
        self.fields['office_correspondent'] = get_office_related_office_field(self.request)
        self.fields['office_correspondent'].label = u"Escritório Correspondente"
        self.fields['office'].required = True
        self.fields['type_task'].queryset = filter_valid_choice_form(TypeTask.objects.get_queryset(
            office=office_session.id).order_by('name'))
        self.fields['office_network'].queryset = self.fields['office_network'].queryset.filter(members=office_session)
        self.fields['office_network'].required = True


class ImportServicePriceTableForm(forms.ModelForm):
    file_xls = XlsxFileField(label='Arquivo', required=True,
                             headers_to_check=['Correspondente', 'Serviço', 'Cliente', 'UF', 'Comarca',
                                               'Complemento de comarca', 'Cidade', 'Valor'])

    class Meta:
        model = ImportServicePriceTable
        fields = ('file_xls', )


class PolicyPriceForm(BaseModelForm):  
  class Meta: 
    model = PolicyPrice
    fields = ('office', 'name', 'category', 'billing_type', 'billing_moment')

  def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.fields['office'] = get_office_field(self.request)