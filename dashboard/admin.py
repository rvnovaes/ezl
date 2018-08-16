from django.contrib import admin
from .models import Dashboard, Card
from .forms import DashboardForm, CardForm


class CardsInline(admin.TabularInline):
	model = Dashboard.cards.through

@admin.register(Dashboard)
class DashboardModelAdmin(admin.ModelAdmin):
	fields = ['company', 'refresh']
	inlines = [
		CardsInline
	]

@admin.register(Card)
class CardModelAdmin(admin.ModelAdmin):
	list_display = ['name', 'code']
	form=CardForm
	fields = ('name', 'schema', 'code')
