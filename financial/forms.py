from django import forms
from .models import CostCenter
from material import Layout, Row


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
