from django import forms
from .models import Survey
from material import Layout, Row


class BaseModelForm(forms.ModelForm):
    def get_model_verbose_name(self):
        return self._meta.model._meta.verbose_name


class SurveyForm(BaseModelForm):

    layout = Layout(
        Row('type_task'),
        Row('data'),
    )

    class Meta:
        model = Survey
        fields = ['type_task', 'data']
