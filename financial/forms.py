from django import forms
from task.models import TypeTask
from material import Layout, Row
from core.widgets import MDModelSelect2
from core.models import Person
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

    correspondent = forms.ModelChoiceField(
        label='Correspondente',
        queryset=Person.objects.filter(auth_user__groups__name=Person.CORRESPONDENT_GROUP),
    )

    class Meta:
        model = ServicePriceTable
        fields = ('type_task', 'court_district', 'state', 'client', 'correspondent', 'value')
