from django.db import models
from core.models import Company
from django.contrib.postgres.fields import JSONField
import json
from .schemas import *






class Dashboard(models.Model):
	company = models.ForeignKey(Company, verbose_name='Empresa')
	refresh = models.IntegerField(verbose_name='Refresh por millesegundo', blank=True, null=True)	

	def __str__(self):
		return self.company.name


class Card(models.Model):		
	name = models.CharField(verbose_name='Nome', max_length=255, blank=True, null=True)
	code = models.TextField(verbose_name='Codigo', blank=True, null=True)	
	dashboards = models.ManyToManyField(Dashboard, related_name='cards', through='DashboardCard', blank=True)
	schema = JSONField(verbose_name=u'Schema', blank=True, null=True, default=json.dumps(CARD))

	def __str__(self):
		return self.name

class DashboardCard(models.Model):
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, blank=True)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, blank=True)
