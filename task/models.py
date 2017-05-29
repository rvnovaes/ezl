from django.db import models
from django.utils import timezone

from core.models import Person, Audit
from lawsuit.models import Movement, TypeMovement


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
