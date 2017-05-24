from django.db import models
from django.utils import timezone

from core.models import Audit, Person, State


class TypeMovement(Audit):
    name = models.CharField(max_length=255, blank=False, null=False, default="", unique=True, verbose_name='Nome')
    legacy_code = models.CharField(max_length=255, blank=False, null=False, default="", unique=True,
                                   verbose_name='Código legado')
    uses_wo = models.BooleanField(default=False, verbose_name='Utiliza ordem de serviço?')

    class Meta:
        db_table = "type_movement"
        ordering = ['-id']

    def __str__(self):
        return self.name


class Instance(Audit):
    name = models.CharField(max_length=255, null=False, blank=False, default="", unique=True)

    class Meta:
        db_table = "instance"
        ordering = ['-id']

    def __str__(self):
        return self.name


class Folder(Audit):
    legacy_code = models.CharField(max_length=255, blank=False, null=False, default="", unique=True,
                                   verbose_name='Código Legado')
    person_customer = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False,
                                        verbose_name='Cliente')

    class Meta:
        db_table = "folder"
        ordering = ['-id']

    def __str__(self):
        return str(self.id)


class LawSuit(Audit):
    person_lawyer = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False,
                                      verbose_name='Advogado')
    folder = models.ForeignKey(Folder, on_delete=models.PROTECT, blank=False, null=False)

    class Meta:
        db_table = "law_suit"
        ordering = ['-id']

    def __str__(self):
        return str(self.id)  # TODO verificar novos campos e refatorar o toString


class Movement(Audit):
    legacy_code = models.CharField(max_length=255, blank=False, null=False, default="", unique=True)
    person_lawyer = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False,
                                      related_name='%(class)s_lawyer')
    person_court = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False,
                                     related_name='%(class)s_court')
    type_movement = models.ForeignKey(TypeMovement, on_delete=models.PROTECT, blank=False, null=False)
    law_suit = models.ForeignKey(LawSuit, on_delete=models.PROTECT, blank=False, null=False)
    deadline = models.DateTimeField(null=True)

    class Meta:
        db_table = "movement"
        ordering = ['-id']

    def __str__(self):
        return self.legacy_code  # TODO verificar novos campos e refatorar o toString


class Task(Audit):
    legacy_code = models.CharField(max_length=255, blank=False, null=False, default="", unique=True)
    movement = models.ForeignKey(Movement, on_delete=models.PROTECT, blank=False, null=False)
    person = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False)
    type_movement = models.ForeignKey(TypeMovement, on_delete=models.PROTECT, blank=False, null=False)
    delegation_date = models.DateTimeField(default=timezone.now)
    acceptance_date = models.DateTimeField(null=True)
    deadline_date = models.DateTimeField(null=True)
    final_deadline_date = models.DateTimeField(null=True)
    execution_deadline_date = models.DateTimeField(null=True)  # TODO ou first_deadline_date e second_deadline_date?

    class Meta:
        db_table = 'task'
        ordering = ['-id']

    def __str__(self):
        return self.legacy_code  # TODO verificar campo para toString


class CourtDistrict(Audit):
    name = models.CharField(max_length=255, null=False, unique=True, verbose_name='Nome')
    state = models.ForeignKey(State, on_delete=models.PROTECT, null=False, blank=False, verbose_name='Estado')

    class Meta:
        db_table = "court_district"

    def __str__(self):
        return self.name
