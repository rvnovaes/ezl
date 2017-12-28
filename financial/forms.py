from django import forms
from task.models import TypeTask
from material import Layout, Row
from core.widgets import MDModelSelect2
from core.models import Person, State
from core.utils import filter_valid_choice_form
from lawsuit.models import CourtDistrict
from task.models import TypeTask
from .models import CostCenter, ServicePriceTable


class BaseModelForm(forms.ModelForm):
    def get_model_verbose_name(self):
        return self._meta.model._meta.verbose_name


class CostCenterForm(BaseModelForm):

    layout = Layout(
        Row('name', 'is_active'),
    )

    legacy_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = CostCenter
        fields = ['name', 'legacy_code', 'is_active']


class ServicePriceTableForm(BaseModelForm):

    layout = Layout(
        Row('correspondent', 'type_task', 'value'),
        Row('client', 'court_district', 'state'),
    )

    correspondent = forms.ModelChoiceField(
        label="Correspondente",
        queryset=Person.objects.filter(auth_user__groups__name=Person.CORRESPONDENT_GROUP),
        widget=MDModelSelect2(
            url='correspondent_autocomplete',
            attrs={
                'class': 'select-with-search material-ignore form-control',
                'data-placeholder': '',
                'data-label': 'Cidade'
            }),
        required=True,
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

    court_district = forms.ModelChoiceField(
        queryset=CourtDistrict.objects.filter(),
        widget=MDModelSelect2(
            url='courtdistrict_autocomplete',
            attrs={
                'class': 'select-with-search material-ignore form-control',
                'data-placeholder': '',
                'data-label': 'Comarca'
            }),
        required=False,
        label="Comarca"
    )

    state = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(State.objects.all().order_by('initials')),
        empty_label='',
        required=True,
        label='UF',
    )

    type_task = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(TypeTask.objects.all().order_by('name')),
        empty_label='',
        required=True,
        label=u"Tipo de Serviço",
    )

    class Meta:
        model = ServicePriceTable
        fields = ('type_task', 'court_district', 'state', 'client', 'correspondent', 'value')
