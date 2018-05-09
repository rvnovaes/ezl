from django.db import models
from djmoney.models.fields import MoneyField
from core.models import Audit, Office


class Plan(Audit):
    name = models.CharField(max_length=255, blank=False, null=False, verbose_name="Nome")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    month_value = MoneyField(max_digits=10, decimal_places=2, default_currency='BRL', verbose_name="Valor mensal",
                             null=False, blank=False)
    task_limit = models.IntegerField(verbose_name="Limite mensal", null=True, blank=True)

    class Meta:
        ordering = ['month_value']
        verbose_name = "Plano"
        verbose_name_plural = "Planos"

    def __str__(self):
        return '{} ({})'.format(self.name, self.month_value)


class PlanOffice(Audit):
    office = models.ForeignKey(Office, on_delete=models.CASCADE, blank=False, null=False)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, blank=False, null=False)
    subscription_date = models.DateTimeField('Data de inscrição', auto_now_add=True, blank=False, null=False)
    cancelation_date = models.DateTimeField('Data de cancelamento', auto_now_add=False, blank=True, null=True)
    month_value = MoneyField(max_digits=10, decimal_places=2, default_currency='BRL', verbose_name="Valor mensal",
                             null=False, blank=False)
    task_limit = models.IntegerField(verbose_name="Limite mensal", null=True, blank=True)

    class Meta:
        ordering = ['office']

    def __str__(self):
        return '{} - {} - {}'.format(self.office.legal_name, self.plan.name, self.subscription_date)
