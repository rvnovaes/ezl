import os
from django.core.validators import ValidationError
from django.core.exceptions import NON_FIELD_ERRORS, ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from core.models import Audit, LegacyCode, OfficeMixin, OfficeManager, Office, OfficeNetwork
from decimal import Decimal
from task.metrics import get_office_finished_by_rate, get_office_rating, get_office_returned_os_rate
from djmoney.models.fields import MoneyField
from enum import Enum
from .enums import CategoryPrice, BillingMoment, RateType


class PolicyPrice(Audit, OfficeMixin):
    name = models.CharField(verbose_name='Nome', max_length=255)
    category = models.CharField(verbose_name='Categoria', max_length=255,
                                choices=CategoryPrice.choices())
    billing_moment = models.CharField(verbose_name='Momento do faturamento', max_length=255,
                                      choices=BillingMoment.choices())
    objects = OfficeManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tipo de Preço'
        verbose_name_plural = 'Tipos de Preço'
        ordering = ['name']


class FinancialPermissions(Enum):
    view_financial_report = 'View financial reports'
    billing_task = 'Change task billing date'


class CostCenter(Audit, LegacyCode, OfficeMixin):
    name = models.CharField(
        verbose_name="Nome",
        max_length=255,
        null=False,
        blank=False
    )

    objects = OfficeManager()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'cost_center'
        ordering = ['name']
        verbose_name = 'Centro de custo'
        verbose_name_plural = 'Centros de custos'
        unique_together = (('name', 'office', 'legacy_code'),)


class ServicePriceTable(Audit, LegacyCode, OfficeMixin):
    office_correspondent = models.ForeignKey(Office, on_delete=models.PROTECT, blank=True,
                                             null=True,
                                             related_name='office_correspondent',
                                             verbose_name='Escritório Correspondente')
    office_network = models.ForeignKey(OfficeNetwork, on_delete=models.PROTECT, blank=True,
                                       null=True,
                                       related_name='office_network',
                                       verbose_name='Rede de escritórios')
    type_task = models.ForeignKey(
        'task.TypeTask',
        null=True,
        blank=True,
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
    value_to_receive = MoneyField(
        max_digits=9,
        decimal_places=2,
        default_currency='BRL',
        verbose_name="Valor a receber",
        default=Decimal('0.00'),
        null=False,
        blank=False
    )
    value_to_pay = MoneyField(
        max_digits=9,
        decimal_places=2,
        default_currency='BRL',
        verbose_name="Valor a pagar",
        default=Decimal('0.00'),
        null=False,
        blank=False
    )
    rate_type_receive = models.CharField(verbose_name='Tipo de taxa a receber', max_length=10,
                                         choices=RateType.choices(), default=RateType.PERCENT)
    rate_type_pay = models.CharField(verbose_name='Tipo de taxa a pagar', max_length=10,
                                     choices=RateType.choices(), default=RateType.PERCENT)
    court_district_complement = models.ForeignKey(
        'lawsuit.CourtDistrictComplement',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='%(class)s_court_district_complement',
        verbose_name='Complemento de comarca'
    )
    city = models.ForeignKey(
        'core.City',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='%(class)s_city',
        verbose_name='Cidade'
    )
    policy_price = models.ForeignKey(
        PolicyPrice,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name='service_prices',
        verbose_name='Tipo de preço'
    )

    objects = OfficeManager()

    @property
    def office_rating(self):
        return get_office_rating(self.office_correspondent)

    @property
    def office_return_rating(self):
        return get_office_returned_os_rate(self.office_correspondent)

    @property
    def finished_by_rate(self):
        return get_office_finished_by_rate(self.office_correspondent, self.state, self.court_district)

    def __str__(self):
        return self.office.legal_name if self.office else ""

    class Meta:
        db_table = 'service_price_table'
        ordering = ['value']
        verbose_name = 'Tabela de preço de serviços'
        verbose_name_plural = 'Tabelas de preço de serviços'

    def validate_unique(self, exclude=None):
        res = super().validate_unique(exclude)
        office_q = Q(office=self.office)
        office_correspondent_q = Q(office_correspondent=self.office_correspondent) \
            if getattr(self, 'office_correspondent', None) else Q(office_correspondent__isnull=True)
        office_network_q = Q(office_network=self.office_network) \
            if getattr(self, 'office_network', None) else Q(office_network__isnull=True)
        state_q = Q(state=self.state) if self.state else Q(state__isnull=True)
        city_q = Q(city=self.city) if self.city else Q(city__isnull=True)
        court_district_q = Q(court_district=self.court_district) if self.court_district \
            else Q(court_district__isnull=True)
        court_district_complement_q = Q(court_district_complement=self.court_district_complement) if \
            self.court_district_complement else Q(court_district_complement__isnull=True)
        type_task_q = Q(type_task=self.type_task) if self.type_task else Q(type_task__isnull=True)
        client_q = Q(client=self.client) if self.client else Q(client__isnull=True)
        policy_price_q = Q(policy_price=self.policy_price) if self.policy_price else Q(policy_price__isnull=True)
        try:
            if ServicePriceTable.objects.filter(~Q(pk=self.pk),
                                                office_q,
                                                office_correspondent_q,
                                                office_network_q,
                                                state_q,
                                                city_q,
                                                court_district_q,
                                                court_district_complement_q,
                                                type_task_q,
                                                client_q,
                                                policy_price_q):
                raise ValidationError({
                    NON_FIELD_ERRORS: [
                        "Os campos office, office_correspondent, office_network, type_task, client, court_district, "
                        "state, city, policy_price e court_district_complement devem criar um set único."
                    ],
                    'office_correspondent': ['Favor verificar o escritório correspondente'],
                    'office_network': ['Favor verificar a rede de escritórios'],
                    'policy_price': ['Favor verificar tipo de preço'],
                    'type_task': ['Favor verificar o tipo de serviço'],
                    'state': ['Favor verificar o estado'],
                    'city': ['Favor verificar a cidade'],
                    'court_district': ['Favor verificar a comarca'],
                    'court_district_complement': ['Favor verificar o complemento de comarcar'],
                    'client': ['Favor verificar o cliente']

                })
        except ObjectDoesNotExist:
            pass
        return res


def get_dir_name(instance, filename):
    path = os.path.join('media', 'service_price_table')
    if not os.path.exists(path):
        os.makedirs(path)
    return 'service_price_table/{0}'.format(filename)


class ImportServicePriceTable(Audit, OfficeMixin):
    file_xls = models.FileField('Arquivo', upload_to=get_dir_name)        
    log = models.TextField('Log', null=True)
    start = models.DateTimeField('Início processo')
    end = models.DateTimeField('Fim processo', null=True)

    def __str__(self):
        return self.file_xls.file.name + ' - ' + 'Início: ' + str(self.start) + ' - ' + 'Fim: ' + str(self.end)

    class Meta:
        verbose_name = 'Arquivos Importados de Tabela de Preços'


