import os
from enum import Enum
from django.db import transaction

import pickle
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.urls.base import reverse
from django.utils import timezone
from sequences import get_next_value
from core.models import Person, Audit, AuditCreate, LegacyCode, OfficeMixin, OfficeManager, Office
from lawsuit.models import Movement, Folder
from chat.models import Chat
from decimal import Decimal


class Permissions(Enum):
    view_delegated_tasks = 'Can view tasks delegated to the user'
    view_all_tasks = 'Can view all tasks'
    return_all_tasks = 'Can return tasks'
    validate_all_tasks = 'Can validade tasks'
    view_requested_tasks = 'Can view tasks requested by the user'
    block_payment_tasks = 'Can block tasks payment'
    can_access_general_data = 'Can access general data screens'
    view_distributed_tasks = 'Can view tasks distributed by the user'
    can_distribute_tasks = 'Can distribute tasks to another user'


# Dicionário para retornar o icone referente ao status da providencia
icon_dict = {
    'ACCEPTED': 'mdi mdi-calendar-clock',
    'OPEN': 'mdi mdi-account-location',
    'RETURN': 'mdi mdi-backburger',
    'DONE': 'mdi mdi-checkbox-marked-circle-outline',
    'REFUSED': 'mdi mdi-clipboard-alert',
    'INVALID': 'mdi mdi-exclamation',
    'FINISHED': 'mdi mdi-gavel',
    'BLOCKEDPAYMENT':'mdi mdi-currency-usd-off',
    'ERROR': 'mdi mdi-close-circle-outline',
    'REQUESTED': 'mdi mdi-playlist-play',
    'ACCEPTED_SERVICE': 'mdi mdi-thumb-up-outline',
    'REFUSED_SERVICE': 'mdi mdi-thumb-down-outline',
}

color_dict = {
    'ACCEPTED': 'success',
    'OPEN': 'primary',
    'RETURN': 'warning',
    'DONE': 'info',
    'REFUSED': 'warning',
    'INVALID': 'muted',
    'FINISHED': 'success',
    'BLOCKEDPAYMENT':'muted',
    'ERROR': 'danger',
    'REQUESTED': 'danger',
    'ACCEPTED_SERVICE': 'danger',
    'REFUSED_SERVICE': 'danger',
}


# next_action = {'ACCEPTED': 'cumprir', 'OPEN': 'assignment', 'RETURN': 'keyboard_return',
# 'DONE': 'done', 'REFUSED': 'assignment_late'}


class TaskStatus(Enum):
    REQUESTED = 'Solicitada'
    ACCEPTED_SERVICE = 'Aceita pelo Service'
    OPEN = 'Em Aberto'
    ACCEPTED = 'A Cumprir'
    DONE = 'Cumprida'
    RETURN = 'Retorno'
    FINISHED = 'Finalizada'
    REFUSED_SERVICE = 'Recusada pelo Service'
    REFUSED = 'Recusada'
    BLOCKEDPAYMENT = 'Glosada'
    INVALID = 'Inválida'
    ERROR = 'Erro no sistema de origem'

    @property
    def get_icon(self):
        return icon_dict[self.name]

    def get_color(self):
        return color_dict[self.name]

    def __str__(self):
        return str(self.value)

    @classmethod
    def choices(cls):
        return [(x.value, x.name) for x in cls]
        # 'Em Aberto' = 1  # Providencias que foram delegadas
        # (1, 'Aceita/Retorno'),
        #  Retorno (return) / Aceitas (accepted) providencias que foram executadas com sucesso ou
        # retornadas ao correspondente por pendencias
        # (2, 'Recusada'),  # providencias recusadas pelo correposndente
        # (3, 'Cumprida'),  # providencias executadas sem nenhuma pendencia

    @classmethod
    def choices_icons(cls):
        return [(x.get_icon, x.value) for x in cls]


class SurveyType(Enum):
    BLANK = ''
    OPERATIONLICENSE = 'Cumprimento de Ordem de Serviço do tipo Alvará'
    COURTHEARING = 'Cumprimento de Ordem de Serviço do tipo Audiência'
    DILIGENCE = 'Cumprimento de Ordem de Serviço do tipo Diligência'
    PROTOCOL = 'Cumprimento de Ordem de Serviço do tipo Protocolo'

    def __str__(self):
        return str(self.value)

    @classmethod
    def choices(cls):
        return [(x.value, x.name) for x in cls]


class CheckPointType(Enum):
    CHECKIN = 'Checkin'
    CHECKOUT = 'Checkout'

    def __str__(self):
        return str(self.value)

    @classmethod
    def choices(cls):
        return [(x.value, x.name) for x in cls]


class TypeTask(Audit, LegacyCode, OfficeMixin):
    name = models.CharField(max_length=255, null=False, blank=False,
                            verbose_name='Tipo de Serviço')
    survey = models.ForeignKey(
        'survey.Survey',
        null=True,
        verbose_name='Tipo de Formulário'
    )

    objects = OfficeManager()

    class Meta:
        db_table = 'type_task'
        ordering = ('name',)
        verbose_name = 'Tipo de Serviço'
        verbose_name_plural = 'Tipos de Serviço'
        unique_together = (('office', 'name'),)

    def __str__(self):
        return self.name


class Task(Audit, LegacyCode, OfficeMixin):
    TASK_NUMBER_SEQUENCE = 'task_task_task_number'

    parent = models.OneToOneField('self', null=True, blank=True, related_name='child')

    task_number = models.PositiveIntegerField(verbose_name='Número da Providência',
                                              unique=False)

    movement = models.ForeignKey(Movement, on_delete=models.PROTECT, blank=False, null=False,
                                 verbose_name='Movimentação')
    person_asked_by = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False,
                                        related_name='%(class)s_asked_by',
                                        verbose_name='Solicitante')
    person_executed_by = models.ForeignKey(Person, on_delete=models.PROTECT, blank=True, null=True,
                                           related_name='%(class)s_executed_by',
                                           verbose_name='Correspondente')
    person_distributed_by = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False,
                                              null=True,
                                              verbose_name='Contratante')
    type_task = models.ForeignKey(TypeTask, on_delete=models.PROTECT, blank=False, null=False,
                                  verbose_name='Tipo de Serviço')
    delegation_date = models.DateTimeField(null=True, default=timezone.now, blank=True, verbose_name='Data de Delegação')
    acceptance_date = models.DateTimeField(null=True, verbose_name='Data de Aceitação')
    final_deadline_date = models.DateTimeField(null=False, blank=False, default=timezone.now, verbose_name='Prazo Fatal')
    execution_date = models.DateTimeField(null=True, verbose_name='Data de Cumprimento')

    requested_date = models.DateTimeField(null=True, verbose_name='Data de Solicitação')
    acceptance_service_date = models.DateTimeField(null=True, verbose_name='Data de Aceitação pelo Contratante')
    refused_service_date = models.DateTimeField(null=True, verbose_name='Data de Recusa pelo Contratante')
    return_date = models.DateTimeField(null=True, verbose_name='Data de Retorno')
    refused_date = models.DateTimeField(null=True, verbose_name='Data de Recusa')

    blocked_payment_date = models.DateTimeField(null=True, verbose_name='Data da Glosa')
    finished_date = models.DateTimeField(null=True, verbose_name='Data de Finalização')

    description = models.TextField(null=True, blank=True, verbose_name=u'Descrição do serviço')

    task_status = models.CharField(null=False, verbose_name=u'', max_length=30,
                                   choices=((x.value, x.name.title()) for x in TaskStatus),
                                   default=TaskStatus.REQUESTED)
    survey_result = models.TextField(verbose_name=u'Respotas do Formulário', blank=True, null=True)
    amount = models.DecimalField(null=False, blank=False, verbose_name='Valor',
                                 max_digits=9, decimal_places=2, default=Decimal('0.00'))
    chat = models.ForeignKey(Chat, verbose_name='Chat', on_delete=models.SET_NULL, null=True,
                             blank=True)
    __previous_status = None  # atributo transient
    __notes = None  # atributo transient

    objects = OfficeManager()

    class Meta:
        db_table = 'task'
        ordering = ['-alter_date']
        verbose_name = 'Providência'
        verbose_name_plural = 'Providências'
        permissions = [(i.name, i.value) for i in Permissions]
        unique_together = ('task_number', 'office')

    @property
    def status(self):
        return TaskStatus(self.task_status)

    @property
    def client(self):
        folder = Folder.objects.get(folders__law_suits__task__exact=self)
        return folder.person_customer

    def __str__(self):
        return self.type_task.name

    @property
    def court_division(self):
        return self.movement.law_suit.court_division

    @property
    def court_district(self):
        return self.movement.law_suit.court_district

    @property
    def court(self):
        return self.movement.law_suit.organ

    # TODO fazer composição para buscar no endereço completo
    # TODO Modifiquei pois quando não há orgão cadastrado em lawsuit lança erro de
    # variável nula / Martins
    @property
    def address(self):
        address = ''
        organ = self.movement.law_suit.organ
        if organ:
            address = organ.address_set.first()
        return address

    def get_absolute_url(self):
        return reverse("task_detail",
                       kwargs={"pk": self.id})

    @property
    def opposing_party(self):
        return self.movement.law_suit.opposing_party

    @property
    def lawsuit_number(self):
        return self.movement.law_suit.law_suit_number

    def serialize(self):
        """JSON representation of object"""
        data = {
            "id": self.id,
            "url": self.get_absolute_url(),
            "task_number": self.task_number,
            "lawsuit_number": self.lawsuit_number,
            "client": self.client.simple_serialize(),
            "opposing_party": self.opposing_party,
            "status": str(self.status),
            "type_task": {"name": self.type_task.name, "id": self.type_task.id},
            "final_deadline_date": self.final_deadline_date.strftime(settings.DATETIME_FORMAT) if self.final_deadline_date else "",
            "delegation_date": self.delegation_date.strftime(settings.DATETIME_FORMAT) if self.delegation_date else ""
        }
        return data

    # TODO Remover Property após modificação do ECM da Task para o ECM genérico
    @property
    def use_upload(self):
        return False

    def save(self, *args, **kwargs):
        self._skip_signal = kwargs.pop('skip_signal', False)
        if not self.task_number:
            self.task_number = self.get_task_number()
        return super().save(*args, **kwargs)

    @property
    def get_child(self):
        if hasattr(self, 'child'):
            return self.child
        return None

    @transaction.atomic
    def get_task_number(self):
        return get_next_value('office_{office_pk}_{name}'.format(office_pk=self.office.pk,
                                                                 name=self.TASK_NUMBER_SEQUENCE))


class TaskFeedback(models.Model):
    feedback_date = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey('Task', verbose_name='OS')
    rating = models.SmallIntegerField(
        verbose_name='Nota',
        choices=[(x, x) for x in range(1,6)]
    )
    comment = models.TextField(null=True, verbose_name='Comentário')
    create_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='%(class)s_create_user',
        verbose_name='Criado por'
    )


def get_dir_name(instance, filename):
    path = os.path.join('media', 'ECM', str(instance.task_id))
    if not os.path.exists(path):
        os.makedirs(path)
    return 'ECM/{0}/{1}'.format(instance.task.pk, filename)


class EcmQuerySet(models.QuerySet):
    def delete(self):
        # Não podemos apagar os ECMs que possuam legacy_code
        queryset = self.exclude(legacy_code__isnull=False)
        return super(EcmQuerySet, queryset).delete()


class EcmManager(models.Manager):

    def get_queryset(self):
        return EcmQuerySet(self.model, using=self._db)


class Ecm(Audit, LegacyCode):
    path = models.FileField(upload_to=get_dir_name, max_length=255, null=False)
    task = models.ForeignKey(Task, blank=False, null=False, on_delete=models.PROTECT)
    updated = models.BooleanField(default=True, null=False)

    objects = EcmManager()

    # Retorna o nome do arquivo no Path, para renderizar no tamplate
    @property
    def filename(self):
        return os.path.basename(self.path.path)

    @property
    def user(self):
        return User.objects.get(username=self.path.instance.create_user)

    def delete(self, *args, **kwargs):
        if self.legacy_code:
            raise ValidationError("Você não pode apagar um GED cadastrado em um sistema legado")
        return super().delete(*args, **kwargs)


class TaskHistory(AuditCreate):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, blank=False, null=False)
    notes = models.TextField(null=True, blank=True, verbose_name=u'Observações')
    status = models.CharField(max_length=30, choices=TaskStatus.choices())

    class Meta:
        verbose_name = 'Histórico da Providência'
        verbose_name_plural = 'Histórico das Providências'

    def save(self, *args, **kwargs):
        self._skip_signal = kwargs.pop('skip_signal', False)
        return super(TaskHistory, self).save(*args, **kwargs)


class TaskGeolocation(Audit):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, blank=False, null=False,
                            related_name='geolocation')
    date = models.DateTimeField(null=True, verbose_name='Data de Início')
    checkpointtype = models.CharField(null=True, verbose_name='Tipo de Marcação', max_length=10,
                                      choices=((x.value, x.name.title()) for x in CheckPointType),
                                      default=CheckPointType.CHECKIN)
    latitude = models.DecimalField(null=True, blank=True, verbose_name='Latitude',
                                   max_digits=9, decimal_places=6)
    longitude = models.DecimalField(null=True, blank=True, verbose_name='Longitude',
                                   max_digits=9, decimal_places=6)

    class Meta:
        verbose_name = 'Geolocalização da Providência'
        verbose_name_plural = 'Geolocalização das Providências'

    @property
    def position(self):
        return "{},{}".format(self.latitude, self.longitude)


class DashboardViewModel(Audit, OfficeMixin):
    legacy_code = models.CharField(max_length=255, blank=True, null=True,
                                   verbose_name='Código legado')
    task_number = models.PositiveIntegerField(default=0, verbose_name='Número da Providência')

    movement = models.ForeignKey(Movement, on_delete=models.PROTECT, blank=False, null=False,
                                 verbose_name='Movimentação')
    person_asked_by = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False,
                                        related_name='%(class)s_asked_by',
                                        verbose_name='Solicitante')
    person_executed_by = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False,
                                           null=False,
                                           related_name='%(class)s_executed_by',
                                           verbose_name='Correspondente')
    person_distributed_by = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False,
                                              null=True,
                                              verbose_name='Service')
    type_task = models.ForeignKey(TypeTask, on_delete=models.PROTECT, blank=False, null=False,
                                  verbose_name='Tipo de Serviço')
    requested_date = models.DateTimeField(null=True, verbose_name='Data de Solicitação')
    acceptance_service_date = models.DateTimeField(null=True, verbose_name='Data de Aceitação pelo Contratante')
    refused_service_date = models.DateTimeField(null=True, verbose_name='Data de Recusa pelo Contratante')
    delegation_date = models.DateTimeField(default=timezone.now, verbose_name='Data de Delegação')
    acceptance_date = models.DateTimeField(null=True, verbose_name='Data de Aceitação')
    final_deadline_date = models.DateTimeField(null=True, verbose_name='Prazo')
    execution_date = models.DateTimeField(null=True, verbose_name='Data de Cumprimento')

    return_date = models.DateTimeField(null=True, verbose_name='Data de Retorno')
    refused_date = models.DateTimeField(null=True, verbose_name='Data de Recusa')

    blocked_payment_date = models.DateTimeField(null=True, verbose_name='Data da Glosa')
    finished_date = models.DateTimeField(null=True, verbose_name='Data de Finalização')

    description = models.TextField(null=True, blank=True, verbose_name=u'Descrição do serviço')

    task_status = models.CharField(null=False, verbose_name=u'', max_length=30,
                                   choices=((x.value, x.name.title()) for x in TaskStatus),
                                   default=TaskStatus.OPEN)
    client = models.CharField(null=True, verbose_name='Cliente', max_length=255)
    type_service = models.CharField(null=True, verbose_name='Serviço', max_length=255)
    survey_result = models.TextField(verbose_name=u'Respotas do Formulário', blank=True, null=True)
    lawsuit_number = models.CharField(max_length=255, blank=True, null=True,
                                      verbose_name='Número do Processo')
    opposing_party = models.CharField(null=True, verbose_name=u'Parte adversa', max_length=255)
    __previous_status = None  # atributo transient
    __notes = None  # atributo transient

    class Meta:
        db_table = 'dashboard_view'
        managed = False
        verbose_name = 'Providência'
        verbose_name_plural = 'Providências'

    @property
    def status(self):
        return TaskStatus(self.task_status)

    def __str__(self):
        return self.type_task.name

    @property
    def court_district(self):
        return self.movement.law_suit.court_district

    @property
    def court(self):
        return self.movement.law_suit.organ



    # TODO fazer composição para buscar no endereço completo
    # TODO Modifiquei pois quando não há orgão cadastrado em lawsuit lança erro de
    # variável nula / Martins
    @property
    def address(self):
        address = ''
        organ = self.movement.law_suit.organ
        if organ:
            address = organ.address_set.first()
        return address

    @property
    def lawsuit_number(self):
        return self.movement.law_suit.law_suit_number

    @property
    def opposing_party(self):
        return self.movement.law_suit.opposing_party

    @property
    def cost_center(self):
        folder = Folder.objects.get(folders__law_suits__task__exact=self)
        return folder.cost_center

    @property
    def folder_number(self):
        folder = Folder.objects.get(folders__law_suits__task__exact=self)
        return folder.folder_number


class Filter(Audit):
    name = models.TextField(verbose_name='Nome', blank=False, null=False, max_length=255)
    description = models.TextField(verbose_name='Descrição', blank=True, null=True)
    query = models.BinaryField(verbose_name='query', blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def query_sql(self):
        return str(DashboardViewModel.objects.filter(pickle.loads(self.query)).query)

    class Meta:
        verbose_name = 'Filtro'
        verbose_name_plural = 'Filtros'
        unique_together = (('create_user', 'name'),)
