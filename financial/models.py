from django.db import models
from core.models import Audit, LegacyCode


class CostCenter(Audit, LegacyCode):
    name = models.CharField(
        verbose_name="Nome",
        max_length=255,
        null=False,
        blank=False,
        default="",
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'cost_center'
        ordering = ['name']
        verbose_name = 'Centro de custo'
        verbose_name_plural = 'Centros de custos'


class ServicePriceTable(models.Model):
    type_task = models.ForeignKey(
        'task.TypeTask',
        on_delete=models.PROTECT,
        related_name='%(class)s_type_task',
        verbose_name='Tipo de Serviço'
    )
    court_district = models.ForeignKey(
        'lawsuit.CourtDistrict',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='%(class)s_court_district',
        verbose_name='Comarca'
    )
    state = models.ForeignKey(
        'core.State',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='%(class)s_state',
        verbose_name='UF'
    )
    client = models.ForeignKey(
        'core.Person',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='%(class)s_client',
        verbose_name='Cliente'
    )
    correspondent = models.ForeignKey(
        'core.Person',
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name='%(class)s_correspondent',
        verbose_name='Correspondente'
    )
    value = models.DecimalField(max_digits=9, decimal_places=2)

    class Meta:
        db_table = 'service_price_table'
        ordering = ['id']
        verbose_name = 'Tabela de preço de serviços'
        verbose_name_plural = 'Tabelas de preço de serviços'

