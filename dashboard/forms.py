from django import forms
from .models import Dashboard, Card
from codemirror import CodeMirrorTextarea
import json
from .schemas import *


class DashboardForm(forms.ModelForm):
    class Meta:
        model = Dashboard
        fields = '__all__'


code_mirror = CodeMirrorTextarea(
    mode="python",
    theme="material",
    config={
        'fixedGutter': True
    }
)
code_mirror_schema = CodeMirrorTextarea(
    mode="javascript",
    theme="material",
    config={
        'fixedGutter': True
    }
)


class CardForm(forms.ModelForm):
    code = forms.CharField(label="Código", widget=code_mirror)
    schema = forms.CharField(
        label="Schema", widget=code_mirror_schema, initial=json.dumps(CARD))

    class Meta:
        model = Card
        fields = '__all__'
