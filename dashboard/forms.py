from django import forms
from .models import Dashboard, Card, DoughnutChart, LineChart
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


class ComponentForm(forms.ModelForm):
    code = forms.CharField(label="Código", widget=code_mirror)


class CardForm(ComponentForm):
    schema = forms.CharField(
        label="Schema", widget=code_mirror_schema, initial=json.dumps(
            CARD, indent=4))

    class Meta:
        model = Card
        fields = '__all__'


class DoughnutChartForm(ComponentForm):
    schema = forms.CharField(
        label="Schema", widget=code_mirror_schema, initial=json.dumps(
            DOUGHNUT, indent=4))

    class Meta:
        model = DoughnutChart
        fields = '__all__'


class LineChartForm(ComponentForm):
    schema = forms.CharField(
        label="Schema", widget=code_mirror_schema, initial=json.dumps(LINE, indent=4))

    class Meta:
        model = LineChart
        fields = '__all__'
