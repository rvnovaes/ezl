from asyncio import Task
from enum import Enum

from django.db import models
from django.utils import timezone

from core.models import Person, Audit
from lawsuit.models import Movement, TypeMovement, Folder

# Dicionário para retornar o icone referente ao status da providencia
icon_dict = {'ACCEPTED': 'assignment_ind', 'OPEN': 'assignment', 'RETURN': 'keyboard_return', 'DONE': 'done',
             'REFUSED': 'assignment_late'}


class TaskStatus(Enum):
    __ordering__ = ['accepted', 'open', 'return', 'done', 'refused']

    def get_icon(self):
        return icon_dict[self.name]

    # def order(self):
    #     if
    def __str__(self):
        return str(self.value)

    ACCEPTED = u"A Cumprir"
    OPEN = u"Em Aberto"
    RETURN = u"Retorno"
    DONE = u"Cumprida"
    REFUSED = u"Recusada"

    # 'Em Aberto' = 1  # Providencias que foram delegadas
    # (1, 'Aceita/Retorno'),
    #  Retorno (return) / Aceitas (accepted) providencias que foram executadas com sucesso ou retornadas ao correspondente por pendencias
    # (2, 'Recusada'),  # providencias recusadas pelo correposndente
    # (3, 'Cumprida'),  # providencias executadas sem nenhuma pendencia


class Task(Audit):
    legacy_code = models.CharField(max_length=255, blank=False, null=False, default="", unique=True,
                                   verbose_name="Código Legado")
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

    notes = models.TextField(null=True, blank=True, verbose_name=u"Observações")

    #
    class Meta:
        db_table = 'task'
        ordering = ['-id']
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
        elif acceptance_date is not None and refused_date is None and execution_date is not None and return_date is not None:
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

    @property
    def name_person_asked_by(self):
        person_asked_by = Person.objects.get(id=self.person_asked_by_id).legal_name
        return person_asked_by

    @property
    def name_type_service(self):
        type_service = TypeMovement.objects.get(id=self.type_movement_id)
        return type_service
