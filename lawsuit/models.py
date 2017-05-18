from django.db import models
from core.models import Audit, Person, CourtDistrict


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


class Movement(Audit):
    legacy_code = models.CharField(max_length=255, blank=False, null=False, default="", unique=True)
    migraperson_lawyer = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False)
    type_movement = models.ForeignKey(TypeMovement, on_delete=models.PROTECT, blank=False, null=False)

    class Meta:
        db_table = "movement"
        ordering = ['-id']

    def __str__(self):
        return self.legacy_code  # TODO verificar novos campos e refatorar o toString


class Folder(Audit):
    name = models.CharField(max_length=255, blank=False, null=False, default="", unique=True)
    legacy_code = models.CharField(max_length=255, blank=False, null=False, default="", unique=True)
    person_customer = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False)

    class Meta:
        db_table = "folder"
        ordering = ['-id']

    def __str__(self):
        return self.name


class LawSuit(Audit):
    person_lawyer = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False, related_name='lawyer')
    person_court = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False, related_name='court')
    court_district = models.ForeignKey(CourtDistrict, on_delete=models.PROTECT, blank=False, null=False)
    instance = models.ForeignKey(Instance, on_delete=models.PROTECT, blank=False, null=False)
    folder = models.ForeignKey(Folder, on_delete=models.PROTECT, blank=False, null=False)

    class Meta:
        db_table = "law_suit"
        ordering = ['-id']

    def __str__(self):
        return self.name  # TODO verificar novos campos e refatorar o toString


class Task(Audit):
    legacy_code = models.CharField(max_length=255, blank=False, null=False, default="", unique=True)
    movement = models.ForeignKey(Movement, on_delete=models.PROTECT, blank=False, null=False)
    person = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False)
    type_movement = models.ForeignKey(TypeMovement, on_delete=models.PROTECT, blank=False, null=False)
    delegation_date = models.DateTimeField()
    acceptance_date = models.DateTimeField()
    deadline_date = models.DateTimeField()
    final_deadline_date = models.DateTimeField()
    execution_deadline_date = models.DateTimeField()  # TODO ou first_deadline_date e second_deadline_date?

    #  pq no advwin tem 3 prazos, assim podemos ter quantos quisermos)

    class Meta:
        db_table = 'providence'
        ordering = ['-id']

    def __str__(self):
        return self.legacy_code  # TODO verificar campo para toString
