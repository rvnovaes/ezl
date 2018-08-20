from django.contrib import admin
from .models import Dashboard, Card, DoughnutChart
from .forms import DashboardForm, CardForm, DoughnutChartForm


class CardsInline(admin.TabularInline):
    model = Dashboard.cards.through


class DoughnutChartInline(admin.TabularInline):
    model = Dashboard.doughnut_charts.through


@admin.register(Dashboard)
class DashboardModelAdmin(admin.ModelAdmin):
    fields = ['company', 'logo', 'refresh']
    inlines = [
        CardsInline,
        DoughnutChartInline,
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
