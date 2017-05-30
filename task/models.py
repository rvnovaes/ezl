from asyncio import Task
from enum import Enum

from django.db import models
from django.utils import timezone

from core.models import Person, Audit
from lawsuit.models import Movement, TypeMovement


class TaskStatus(Enum):
    def __str__(self):
        return str(self.value)

    ACCEPTED = "Aceita"
    OPEN = "Aberta"
    RETURN = "Retorno"
    DONE = "Cumprida"
    REFUSED = "Recusada"

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
    first_deadline_date = models.DateTimeField(null=True, verbose_name="Primeiro Prazo")
    second_deadline_date = models.DateTimeField(null=True, verbose_name="Segundo Prazo")
    execution_date = models.DateTimeField(null=True, verbose_name="Data de Execução")

    return_date = models.DateTimeField(null=True, verbose_name="Data de Retorno")
    refused_date = models.DateTimeField(null=True, verbose_name="Data de Recusa")

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
        if acceptance_date is not None and execution_date is None and return_date is None:
            return TaskStatus.ACCEPTED
        # return_date IS NOT NULL
        elif return_date is not None:
            return TaskStatus.RETURN
        # acceptance_date IS NULL
        elif acceptance_date is None:
            return TaskStatus.OPEN
        # execution_date IS NOT NUL
        elif execution_date is not None:
            return TaskStatus.DONE
        # refused_date IS NOT NULL
        elif refused_date is not None:
            return TaskStatus.REFUSED
