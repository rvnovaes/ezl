from django import forms
from .models import Dashboard, Card, DoughnutChart, LineChart, BarChart
import json
from .schemas import *
from core.forms import code_mirror, code_mirror_schema


class DashboardForm(forms.ModelForm):
    class Meta:
        model = Dashboard
        fields = '__all__'


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


class BarChartForm(ComponentForm):
    schema = forms.CharField(
        label="Schema", widget=code_mirror_schema, initial=json.dumps(
            BAR, indent=4))

    class Meta:
        model = BarChart
        fields = '__all__'
