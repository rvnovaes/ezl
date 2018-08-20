from django.db import models
from core.models import Company
from django.contrib.postgres.fields import JSONField
import json
from .schemas import *


class Dashboard(models.Model):
    company = models.ForeignKey(Company, verbose_name='Empresa')
    logo = models.ImageField(verbose_name='Logo', null=True, blank=True)
    refresh = models.IntegerField(
        verbose_name='Refresh por millesegundo', blank=True, null=True)

    def __str__(self):
        return self.company.name


class Component(models.Model):
    name = models.CharField(verbose_name='Nome',
                            max_length=255, blank=True, null=True)
    code = models.TextField(verbose_name='Codigo', blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Card(Component):
    dashboards = models.ManyToManyField(
        Dashboard, related_name='cards', through='DashboardCard', blank=True)
    schema = JSONField(verbose_name=u'Schema', blank=True,
                       null=True, default=json.dumps(CARD))


class DoughnutChart(Component):
    dashboards = models.ManyToManyField(
        Dashboard, related_name='doughnut_charts', through='DashboardDoughnutChart', blank=True)
    schema = JSONField(verbose_name=u'Schema', blank=True,
                       null=True, default=json.dumps(DOUGHNUT))


class DashboardComponent(models.Model):
    dashboard = models.ForeignKey(
        Dashboard, on_delete=models.CASCADE, blank=True)
    sequence = models.IntegerField('Sequencia')

    class Meta:
        ordering = ['sequence']
        abstract = True


class DashboardCard(DashboardComponent):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, blank=True)


class DashboardDoughnutChart(DashboardComponent):
    doughnut_chart = models.ForeignKey(
        DoughnutChart, on_delete=models.CASCADE, blank=True)
