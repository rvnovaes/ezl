from django.contrib import admin
from .models import Dashboard, Card, DoughnutChart, LineChart, BarChart
from .forms import DashboardForm, CardForm, DoughnutChartForm, LineChartForm, BarChartForm


class CardsInline(admin.TabularInline):
    model = Dashboard.cards.through


class DoughnutChartInline(admin.TabularInline):
    model = Dashboard.doughnut_charts.through


class LineChartInline(admin.TabularInline):
    model = Dashboard.line_charts.through


class BarChartInline(admin.TabularInline):
    model = Dashboard.bar_charts.through


@admin.register(Dashboard)
class DashboardModelAdmin(admin.ModelAdmin):
    fields = ['company', 'logo', 'refresh']
    inlines = [
        CardsInline,
        DoughnutChartInline,
        LineChartInline,
        BarChartInline
    ]


class ComponentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    fields = ('name', 'schema', 'code')


@admin.register(Card)
class CardModelAdmin(ComponentAdmin):
    form = CardForm


@admin.register(DoughnutChart)
class DoughnutChartAdmin(ComponentAdmin):
    form = DoughnutChartForm


@admin.register(LineChart)
class LineChartAdmin(ComponentAdmin):
    form = LineChartForm


@admin.register(BarChart)
class BarChartAdmin(ComponentAdmin):
    form = BarChartForm

