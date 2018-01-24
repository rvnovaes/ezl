from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import Survey
from material import Layout, Row


class BaseModelForm(forms.ModelForm):
    def get_model_verbose_name(self):
        return self._meta.model._meta.verbose_name


class SurveyForm(BaseModelForm):

    layout = Layout(
        Row('name'),
        Row('data'),
    )

    data = forms.CharField(
        label=_('Conteúdo'),
    )

    class Meta:
        model = Survey
        fields = ['name', 'data']
