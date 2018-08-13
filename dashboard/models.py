from django.db import models
from core.models import Company

class Dashboard(models.Model):
	company = models.ForeignKey(Company, verbose_name='Empresa')

	def __str__(self):
		return self.company.name


class Card(models.Model):
	title = models.CharField(verbose_name='Título', max_length=255)
	subtitle = models.CharField(verbose_name='Subtitle', max_length=255)
	value = models.TextField(verbose_name='Valor')
	dashboards = models.ManyToManyField(Dashboard, related_name='cards')


	def __str__(self):
		return self.title


