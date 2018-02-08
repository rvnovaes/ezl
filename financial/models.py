from django.db import models
from core.models import Audit, LegacyCode, OfficeMixin, OfficeManager, Office
from decimal import Decimal


class CostCenter(Audit, LegacyCode, OfficeMixin):
    name = models.CharField(
        verbose_name="Nome",
        max_length=255,
        null=False,
        blank=False,
        default=""
    )

    objects = OfficeManager()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'cost_center'
        ordering = ['name']
        verbose_name = 'Centro de custo'
        verbose_name_plural = 'Centros de custos'
        unique_together = (('name', 'office'),)


class ServicePriceTable(Audit, LegacyCode, OfficeMixin):
    office_correspondent = models.ForeignKey(Office, on_delete=models.PROTECT, blank=False,
                                             null=False,
                                             related_name='office_correspondent',
                                             verbose_name='Escritório Correspondente')
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
    value = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        verbose_name="Valor",
        default=Decimal('0.00')
    )

    objects = OfficeManager()

    def __str__(self):
        return self.office.name if self.office else ""

    class Meta:
        db_table = 'service_price_table'
        ordering = ['value']
        verbose_name = 'Tabela de preço de serviços'
        verbose_name_plural = 'Tabelas de preço de serviços'
        unique_together = (("office", "office_correspondent", "type_task", "client", "court_district", "state"),)
