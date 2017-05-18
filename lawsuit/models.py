from django.db import models
from core.models import Audit, Person, CourtDistrict
from django.utils import timezone


class TypeMovement(Audit):
    name = models.CharField(max_length=255, blank=False, null=False, default="", unique=True)
    legacy_code = models.CharField(max_length=255, blank=False, null=False, default="", unique=True)
    uses_wo = models.BooleanField(default=False)

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
    legacy_code = models.CharField(max_length=255, blank=False, null=False, default="", unique=True)
    person_customer = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False)

    class Meta:
        db_table = "folder"
        ordering = ['-id']

    def __str__(self):
        return self.id


class LawSuit(Audit):
    person_lawyer = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False,
                                      related_name='lawyer_lawsuit')
    folder = models.ForeignKey(Folder, on_delete=models.PROTECT, blank=False, null=False)

    class Meta:
        db_table = "law_suit"
        ordering = ['-id']

    def __str__(self):
        return self.id  # TODO verificar novos campos e refatorar o toString


class Movement(Audit):
    legacy_code = models.CharField(max_length=255, blank=False, null=False, default="", unique=True)
    person_lawyer = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False,
                                      related_name='lawyer_movement')
    person_court = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False, related_name='court')
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
