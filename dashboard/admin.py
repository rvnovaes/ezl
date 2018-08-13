from django.contrib import admin
from .models import Dashboard, Card
from .forms import DashboardForm, CardForm


class CardsInline(admin.TabularInline):
	model = Dashboard.cards.through

@admin.register(Dashboard)
class DashboardModelAdmin(admin.ModelAdmin):
	fields = ['company']
	inlines = [
		CardsInline
	]

@admin.register(Card)
class CardModelAdmin(admin.ModelAdmin):
	list_display = ['title', 'subtitle']
	form=CardForm
