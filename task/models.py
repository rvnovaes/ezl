# from asyncio import Task
import os
from enum import Enum

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from core.models import Person, Audit, AuditCreate, LegacyCode
from lawsuit.models import Movement, TypeMovement, Folder

# Dicionário para retornar o icone referente ao status da providencia
icon_dict = {'ACCEPTED': 'assignment_ind', 'OPEN': 'assignment', 'RETURN': 'assignment_return',
             'DONE': 'assignment_turned_in',
             'REFUSED': 'assignment_late', 'INVALID': 'error', 'FINISHED': "gavel", 'BLOCKEDPAYMENT': 'money_off'}


# next_action = {'ACCEPTED': 'cumprir', 'OPEN': 'assignment', 'RETURN': 'keyboard_return', 'DONE': 'done',
#                'REFUSED': 'assignment_late'}


class TaskStatus(Enum):
    ACCEPTED = "A Cumprir"
    OPEN = "Em Aberto"
    RETURN = "Retorno"
    DONE = "Cumprida"
    REFUSED = "Recusada"
    BLOCKEDPAYMENT = "Glosada"
    FINISHED = "Finalizada"
    INVALID = "Inválida"

    def get_icon(self):
        return icon_dict[self.name]

    def __str__(self):
        return str(self.value)

    @classmethod
    def choices(cls):
        return [(x.value, x.name) for x in cls]
        # 'Em Aberto' = 1  # Providencias que foram delegadas
        # (1, 'Aceita/Retorno'),
        #  Retorno (return) / Aceitas (accepted) providencias que foram executadas com sucesso ou retornadas ao correspondente por pendencias
        # (2, 'Recusada'),  # providencias recusadas pelo correposndente
        # (3, 'Cumprida'),  # providencias executadas sem nenhuma pendencia


class SurveyType(Enum):
    BLANK = ""
    OPERATIONLICENSE = "Cumprimento de Ordem de Serviço do tipo Alvará"
    COURTHEARING = "Cumprimento de Ordem de Serviço do tipo Audiência"
    DILIGENCE = "Cumprimento de Ordem de Serviço do tipo Diligência"
    PROTOCOL = "Cumprimento de Ordem de Serviço do tipo Protocolo"

    def __str__(self):
        return str(self.value)

    @classmethod
    def choices(cls):
        return [(x.value, x.name) for x in cls]


class TypeTask(Audit, LegacyCode):
    name = models.CharField(max_length=255, null=False, unique=True, verbose_name="Tipo de Serviço")
    survey_type = models.CharField(null=False, verbose_name="Tipo de Formulário", max_length=100,
                                   choices=((x.name.title(), x.value) for x in SurveyType),
                                   default=SurveyType.BLANK)

    class Meta:
        db_table = "type_task"
        verbose_name = "Tipo de Serviço"
        verbose_name_plural = "Tipos de Serviço"

    def __str__(self):
        return self.name


class Task(Audit, LegacyCode):
    movement = models.ForeignKey(Movement, on_delete=models.PROTECT, blank=False, null=False,
                                 verbose_name="Movimentação")
    person_asked_by = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False,
                                        related_name='%(class)s_asked_by',
                                        verbose_name="Solicitante")
    person_executed_by = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False,
                                           related_name='%(class)s_executed_by',
                                           verbose_name="Correspondente")
    person_distributed_by = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=True,
                                              verbose_name="Service")
    type_task = models.ForeignKey(TypeTask, on_delete=models.PROTECT, blank=False, null=False,
                                  verbose_name="Tipo de Serviço")
    delegation_date = models.DateTimeField(default=timezone.now, verbose_name="Data de Delegação")
    acceptance_date = models.DateTimeField(null=True, verbose_name="Data de Aceitação")
    reminder_deadline_date = models.DateTimeField(null=True, verbose_name="Primeiro Prazo")
    final_deadline_date = models.DateTimeField(null=True, verbose_name="Segundo Prazo")
    execution_date = models.DateTimeField(null=True, verbose_name="Data de Cumprimento")

    return_date = models.DateTimeField(null=True, verbose_name="Data de Retorno")
    refused_date = models.DateTimeField(null=True, verbose_name="Data de Recusa")

    blocked_payment_date = models.DateTimeField(null=True, verbose_name="Data da Glosa")
    finished_date = models.DateTimeField(null=True, verbose_name="Data de Finalização")

    description = models.TextField(null=True, blank=True, verbose_name=u"Descrição do serviço")

    task_status = models.CharField(null=False, verbose_name=u"", max_length=30,
                                   choices=((x.value, x.name.title()) for x in TaskStatus),
                                   default=TaskStatus.OPEN)
    survey_result = models.TextField(verbose_name=u'Respotas do Formulário', blank=True, null=True)
    __previous_status = None  # atributo transient
    __notes = None  # atributo transient

    class Meta:
        db_table = 'task'
        ordering = ['-alter_date']
        verbose_name = "Providência"
        verbose_name_plural = "Providências"

    @property
    def status(self):
        acceptance_date, return_date, execution_date, refused_date, blocked_payment_date, finished_date = Task.objects.filter(
            id=self.id).values_list(
            'acceptance_date', 'return_date', 'execution_date', 'refused_date', 'blocked_payment_date',
            'finished_date').first()
        # acceptance_date IS NOT NULL AND execution_date IS NULL AND return_date IS NULL
        if acceptance_date is not None and refused_date is None and execution_date is None and return_date is None \
                and finished_date is None and blocked_payment_date is None:
            return TaskStatus.ACCEPTED
        # return_date IS NOT NULL
        elif acceptance_date is not None and refused_date is None and execution_date is None and return_date is not None \
                and finished_date is None and blocked_payment_date is None:
            return TaskStatus.RETURN
        # acceptance_date IS NULL
        elif acceptance_date is None and refused_date is None and execution_date is None and return_date is None \
                and finished_date is None and blocked_payment_date is None:
            return TaskStatus.OPEN
        # execution_date IS NOT NUL
        elif acceptance_date is not None and refused_date is None and execution_date is not None and return_date is None \
                and finished_date is None and blocked_payment_date is None:
            return TaskStatus.DONE
        # refused_date IS NOT NULL
        elif acceptance_date is None and refused_date is not None and execution_date is None and return_date is None:
            return TaskStatus.REFUSED
        elif acceptance_date is not None and refused_date is None and execution_date is not None and return_date is None \
                and finished_date is None and blocked_payment_date is not None:
            return TaskStatus.BLOCKEDPAYMENT
        elif acceptance_date is not None and refused_date is None and execution_date is not None and return_date is None \
                and finished_date is not None and blocked_payment_date is None:
            return TaskStatus.FINISHED

    @property
    def client(self):
        folder = Folder.objects.get(folders__law_suits__task__exact=self)
        return folder.person_customer

    def __str__(self):
        return self.type_task.name

    @property
    def court_district(self):
        return self.movement.law_suit.court_district

    @property
    def court(self):
        return self.movement.law_suit.person_court

    # TODO fazer composição para buscar no endereço completo
    @property
    def address(self):
        address = self.movement.law_suit.person_court.address_set.first()
        return address if address else ''


def get_dir_name(self, filename):
    upload_dir = os.path.join('opt', 'media', 'GEDs', str(self.task_id))
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    path = os.path.join('GEDs', str(self.task_id), filename)
    return path


class Ecm(Audit, LegacyCode):
    path = models.FileField(upload_to=get_dir_name, max_length=255, unique=True, null=False)
    task = models.ForeignKey(Task, blank=False, null=False, on_delete=models.PROTECT)
    updated = models.BooleanField(default=True, null=False)

    # Retorna o nome do arquivo no Path, para renderizar no tamplate
    @property
    def filename(self):
        return os.path.basename(self.path.path)

    @property
    def user(self):
        return User.objects.get(username=self.path.instance.create_user)


class TaskHistory(AuditCreate):
    task = models.ForeignKey(Task, on_delete=models.PROTECT, blank=False, null=False)
    notes = models.TextField(null=True, blank=True, verbose_name=u"Observações")
    status = models.CharField(max_length=10, choices=TaskStatus.choices())

    class Meta:
        verbose_name = "Histórico da Providência"
        verbose_name_plural = "Histórico das Providências"
