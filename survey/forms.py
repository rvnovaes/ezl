from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import Survey
from material import Layout, Row
from core.forms import BaseModelForm


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
