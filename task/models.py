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
             'REFUSED': 'assignment_late'}


# next_action = {'ACCEPTED': 'cumprir', 'OPEN': 'assignment', 'RETURN': 'keyboard_return', 'DONE': 'done',
#                'REFUSED': 'assignment_late'}


class TaskStatus(Enum):
    # __ordering__ = ['accepted', 'open', 'return', 'done', 'refused']
    ACCEPTED = u"A Cumprir"
    OPEN = u"Em Aberto"
    RETURN = u"Retorno"
    DONE = u"Cumprida"
    REFUSED = u"Recusada"

    def get_icon(self):
        return icon_dict[self.name]

    # def order(self):
    #     if
    def __str__(self):
        return str(self.value)

    # @classmethod
    # def choices(cls):
    #     # get all members of the class
    #     members = inspect.getmembers(cls, lambda m: not (inspect.isroutine(m)))
    #     # filter down to just properties
    #     props = [m for m in members if not (m[0][:2] == '__')]
    #     # format into django choice tuple
    #     choices = tuple([(str(p[1].value), p[0]) for p in props])
    #     return choices
    @classmethod
    def choices(cls):
        return [(x.value, x.name) for x in cls]


        # 'Em Aberto' = 1  # Providencias que foram delegadas
        # (1, 'Aceita/Retorno'),
        #  Retorno (return) / Aceitas (accepted) providencias que foram executadas com sucesso ou retornadas ao correspondente por pendencias
        # (2, 'Recusada'),  # providencias recusadas pelo correposndente
        # (3, 'Cumprida'),  # providencias executadas sem nenhuma pendencia


class Task(Audit, LegacyCode):
    # legacy_code = models.CharField(max_length=255, blank=False, null=False, default="", unique=True,
    #                                verbose_name="Código Legado")
    movement = models.ForeignKey(Movement, on_delete=models.PROTECT, blank=False, null=False,
                                 verbose_name="Movimentação")
    person_asked_by = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False,
                                        related_name='%(class)s_asked_by',
                                        verbose_name="Solicitante")
    person_executed_by = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False,
                                           related_name='%(class)s_executed_by',
                                           verbose_name="Correspondente")
    type_movement = models.ForeignKey(TypeMovement, on_delete=models.PROTECT, blank=False, null=False,
                                      verbose_name="Tipo de Movimentação")
    delegation_date = models.DateTimeField(default=timezone.now, verbose_name="Data de Delegação")
    acceptance_date = models.DateTimeField(null=True, verbose_name="Data de Aceitação")
    reminder_deadline_date = models.DateTimeField(null=True, verbose_name="Primeiro Prazo")
    final_deadline_date = models.DateTimeField(null=True, verbose_name="Segundo Prazo")
    execution_date = models.DateTimeField(null=True, verbose_name="Data de Cumprimento")

    return_date = models.DateTimeField(null=True, verbose_name="Data de Retorno")
    refused_date = models.DateTimeField(null=True, verbose_name="Data de Recusa")

    # notes = models.TextField(null=True, blank=True, verbose_name=u"Observações")

    description = models.TextField(null=True, blank=True, verbose_name=u"Descrição do serviço")
    task_status = models.CharField(null=True, verbose_name=u"Status",choices=TaskStatus.choices(), max_length=30, default="-")

    #
    class Meta:
        db_table = 'task'
        ordering = ['-alter_date']
        verbose_name = "Providência"
        verbose_name_plural = "Providências"

    def __str__(self):
        return self.legacy_code  # TODO verificar campo para toString

    @property
    def status(self):
        acceptance_date, return_date, execution_date, refused_date = Task.objects.filter(id=self.id).values_list(
            'acceptance_date', 'return_date', 'execution_date', 'refused_date').first()
        # acceptance_date IS NOT NULL AND execution_date IS NULL AND return_date IS NULL
        if acceptance_date is not None and refused_date is None and execution_date is None and return_date is None:
            return TaskStatus.ACCEPTED
        # return_date IS NOT NULL
        elif acceptance_date is not None and refused_date is None and execution_date is None and return_date is not None:
            return TaskStatus.RETURN
        # acceptance_date IS NULL
        elif acceptance_date is None and refused_date is None and execution_date is None and return_date is None:
            return TaskStatus.OPEN
        # execution_date IS NOT NUL
        elif acceptance_date is not None and refused_date is None and execution_date is not None and return_date is None:
            return TaskStatus.DONE
        # refused_date IS NOT NULL
        elif acceptance_date is None and refused_date is not None and execution_date is None and return_date is None:
            return TaskStatus.REFUSED

    @property
    def client(self):
        mv = Movement.objects.get(task__exact=self.id).id
        client = Folder.objects.get(lawsuit__lawsuitinstance__movement__exact=mv).person_customer
        return client

    @property
    def service(self):
        type_movement = TypeMovement.objects.get(movement__task=self.id).name
        return type_movement

        # @property
        # def name_person_asked_by(self):
        #     person_asked_by = Person.objects.get(id=self.person_asked_by_id).legal_name
        #     return person_asked_by
        #
        # @property
        # def name_type_service(self):
        #     type_service = TypeMovement.objects.get(id=self.type_movement_id)
        #     return type_service


def get_dir_name(self, filename):
    upload_dir = os.path.join('opt', 'media', 'GEDs', str(self.task_id))
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    path = os.path.join('GEDs', str(self.task_id), filename)
    return path


class Ecm(Audit):
    path = models.FileField(upload_to=get_dir_name, max_length=255, unique=True, null=False)
    task = models.ForeignKey(Task, blank=False, null=False, on_delete=models.PROTECT)

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
