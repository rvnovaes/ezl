import os
from django.core.validators import ValidationError
from django.core.exceptions import NON_FIELD_ERRORS, ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from core.models import Audit, LegacyCode, OfficeMixin, OfficeManager, Office
from decimal import Decimal
from task.metrics import get_office_correspondent_metrics


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
    court_district_complement = models.ForeignKey(
        'lawsuit.CourtDistrictComplement',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='%(class)s_court_district_complement',
        verbose_name='Complemento de comarca'
    )

    objects = OfficeManager()

    @property
    def office_rating(self):
        return get_office_correspondent_metrics(self.office_correspondent)['rating']

    @property
    def office_return_rating(self):
        return get_office_correspondent_metrics(self.office_correspondent)['returned_os_rate']

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
        office_correspondent_q = Q(office_correspondent=self.office_correspondent) if self.office_correspondent \
            else Q(office_correspondent__isnull=True)
        state_q = Q(state=self.state) if self.state else Q(state__isnull=True)
        court_district_q = Q(court_district=self.court_district) if self.court_district \
            else Q(court_district__isnull=True)
        court_district_complement_q = Q(court_district_complement=self.court_district_complement) if \
            self.court_district_complement else Q(court_district_complement__isnull=True)
        type_task_q = Q(type_task=self.type_task) if self.type_task else Q(type_task__isnull=True)
        client_q = Q(client=self.client) if self.client else Q(client__isnull=True)
        try:
            if ServicePriceTable.objects.filter(~Q(pk=self.pk),
                                                office_q,
                                                office_correspondent_q,
                                                state_q,
                                                court_district_q,
                                                court_district_complement_q,
                                                type_task_q,
                                                client_q):
                raise ValidationError({
                    NON_FIELD_ERRORS: [
                        "Os campos office, office_correspondent, type_task, client, court_district, state e "
                        "court_district_complement devem criar um set único."
                    ],
                    'office_correspondent': ['Favor verificar o escritório correspondente'],
                    'type_task': ['Favor verificar o tipo de serviço'],
                    'state': ['Favor verificar o estado'],
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
