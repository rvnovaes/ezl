from django.db import models

from core.models import Audit, Person, State, LegacyCode


class TypeMovement(Audit, LegacyCode):
    name = models.CharField(max_length=255, blank=False, null=False, default="", unique=True, verbose_name='Nome')
    uses_wo = models.BooleanField(default=False, verbose_name='Utiliza ordem de serviço?')

    class Meta:
        db_table = "type_movement"
        ordering = ['-id']
        verbose_name = "Tipo de Movimentação"
        verbose_name_plural = "Tipos de Movimentação"

    def __str__(self):
        return self.name


class Instance(Audit, LegacyCode):
    name = models.CharField(verbose_name="Nome", max_length=255, null=False, blank=False, default="", unique=True)

    class Meta:
        db_table = "instance"
        ordering = ['-id']
        verbose_name = "Instância"
        verbose_name_plural = "Instâncias"

    def __str__(self):
        return self.name


class Folder(Audit, LegacyCode):
    person_customer = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False,
                                        verbose_name='Cliente')

    class Meta:
        db_table = "folder"
        ordering = ['-id']
        verbose_name = "Pasta"
        verbose_name_plural = "Pastas"

    def __str__(self):
        return str(self.legacy_code)


class LawSuit(Audit):
    person_lawyer = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False,
                                      verbose_name='Advogado')
    folder = models.ForeignKey(Folder, on_delete=models.PROTECT, blank=False, null=False, verbose_name="Pasta")

    class Meta:
        db_table = "law_suit"
        ordering = ['-id']
        verbose_name = "Processo"
        verbose_name_plural = "Processos"

    def __str__(self):
        return str(self.id)  # TODO verificar novos campos e refatorar o toString


class CourtDistrict(Audit):
    name = models.CharField(max_length=255, null=False, verbose_name="Nome")
    state = models.ForeignKey(State, on_delete=models.PROTECT, null=False, blank=False, verbose_name="Estado")

    class Meta:
        db_table = "court_district"
        verbose_name = "Comarca"
        verbose_name_plural = "Comarcas"
        # cria constraint unique para a combinação de estado e comarca
        unique_together = (('state', 'name'),)

    def __str__(self):
        return self.name


class CourtDivision(Audit, LegacyCode):
    name = models.CharField(max_length=255, null=False, unique=True, verbose_name="Vara")

    class Meta:
        db_table = "court_division"
        verbose_name = "Vara"
        verbose_name_plural = "Varas"

    def __str__(self):
        return self.name


class LawSuitInstance(Audit, LegacyCode):
    law_suit = models.ForeignKey(LawSuit, on_delete=models.PROTECT, blank=False, null=False, verbose_name="Processo")

    person_court = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False,
                                     related_name='%(class)s_court', verbose_name="Tribunal")
    court_district = models.ForeignKey(CourtDistrict, on_delete=models.PROTECT, blank=False, null=False,
                                       verbose_name='Comarca')
    instance = models.ForeignKey(Instance, on_delete=models.PROTECT, blank=False, null=False, verbose_name='Instância')

    # id_court_division fk not null TODO criar modelo para Vara
    law_suit_number = models.CharField(max_length=255, unique=True, blank=False, null=False,
                                       verbose_name='Número do Processo')

    class Meta:
        verbose_name = "Instância do Processo"
        verbose_name_plural = "Instâncias dos Processos"
        ordering = ['-id']

    def __str__(self):
        return self.law_suit_number


class Movement(Audit, LegacyCode):
    person_lawyer = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False,
                                      related_name='%(class)s_lawyer', verbose_name="Advogado")
    type_movement = models.ForeignKey(TypeMovement, on_delete=models.PROTECT, blank=False, null=False,
                                      verbose_name="Tipo de Movimentação")

    deadline = models.DateTimeField(null=True, verbose_name="Data da Movimentação")

    law_suit_instance = models.ForeignKey(LawSuitInstance, on_delete=models.PROTECT, blank=False, null=False,
                                          verbose_name="Instância do Processo")

    class Meta:
        db_table = "movement"
        ordering = ['-id']
        verbose_name = "Movimentação"
        verbose_name_plural = "Movimentação"

    def __str__(self):
        return self.legacy_code  # TODO verificar novos campos e refatorar o toString
