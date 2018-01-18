from django import forms
from task.models import TypeTask
from material import Layout, Row
from core.widgets import MDModelSelect2
from core.models import Person, State, Office
from core.utils import filter_valid_choice_form, get_office_field
from lawsuit.models import CourtDistrict
from task.models import TypeTask
from .models import CostCenter, ServicePriceTable


class BaseModelForm(forms.ModelForm):
    def get_model_verbose_name(self):
        return self._meta.model._meta.verbose_name


class CostCenterForm(BaseModelForm):

    layout = Layout(
        Row('office'),
        Row('name', 'is_active')
    )

    legacy_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = CostCenter
        fields = ['office', 'name', 'legacy_code', 'is_active']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['office'] = get_office_field(self.request)


class ServicePriceTableForm(BaseModelForm):

    layout = Layout(
        Row('office', 'type_task', 'value'),
        Row('client', 'state', 'court_district'),
    )

    client = forms.ModelChoiceField(
        queryset=Person.objects.filter(is_customer=True),
        widget=MDModelSelect2(
            url='client_autocomplete',
            attrs={
                'class': 'select-with-search material-ignore form-control',
                'data-placeholder': '',
                'data-label': 'Cliente'
            }),
        required=False,
        label="Cliente"
    )

    state = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(State.objects.all().order_by('initials')),
        empty_label='',
        required=False,
        label='UF',
    )

    court_district = forms.ModelChoiceField(
        queryset=CourtDistrict.objects.filter(),
        widget=MDModelSelect2(
            url='courtdistrict_autocomplete',
            forward=['state'],
            attrs={
                'class': 'select-with-search material-ignore form-control',
                'data-placeholder': '',
                'data-label': 'Comarca'
            }),
        required=False,
        label="Comarca"
    )

    type_task = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(TypeTask.objects.all().order_by('name')),
        empty_label='',
        required=False,
        label=u"Tipo de Serviço",
    )

    value = forms.CharField(label="Valor",
                            required=False, # O valor pode ser 0.00 porque os correspondentes internos não cobram para fazer serviço
                            widget=forms.TextInput(attrs={'mask': 'money'}))

    class Meta:
        model = ServicePriceTable
        fields = ('type_task', 'court_district', 'state', 'client', 'value', 'office')

    def clean_value(self):
        value = self.cleaned_data['value'] if self.cleaned_data['value'] != '' else '0,00'
        value = value.replace('.', '')
        value = value.replace(',', '.')
        return float(value)

    def clean_office(self):
        office = self.cleaned_data['office']
        if not office:
            raise forms.ValidationError("Favor Selecionar um escritório")
        return office

    def clean_type_task(self):
        type_task = self.cleaned_data['type_task']
        if not type_task:
            raise forms.ValidationError("Favor Selecionar um Tipo de Serviço")
        return type_task

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['office'] = get_office_field(self.request)
