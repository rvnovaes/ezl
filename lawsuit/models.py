from django.db import models
from core.models import Audit, Person, State, LegacyCode, OfficeMixin, OfficeManager
from sequences import get_next_value
from django.db import transaction
from django.core.validators import ValidationError
from django.core.exceptions import NON_FIELD_ERRORS
from django.db.models import Q


@transaction.atomic
def get_folder_number(office):
    return get_next_value('lawsuit_office_%s_folder_folder_number' % office.pk)


class TypeMovement(Audit, LegacyCode, OfficeMixin):
    name = models.CharField(max_length=255, blank=False, null=False, default="", unique=True, verbose_name='Nome')
    uses_wo = models.BooleanField(default=False, verbose_name='Utiliza ordem de serviço?')

    objects = OfficeManager()

    class Meta:
        db_table = "type_movement"
        ordering = ['-id']
        verbose_name = "Tipo de Movimentação"
        verbose_name_plural = "Tipos de Movimentação"

    def __str__(self):
        return self.name


class Instance(Audit, LegacyCode, OfficeMixin):
    name = models.CharField(verbose_name="Nome", max_length=255, null=False, blank=False, default="", unique=True)

    objects = OfficeManager()

    class Meta:
        db_table = "instance"
        ordering = ['-id']
        verbose_name = "Instância"
        verbose_name_plural = "Instâncias"

    def __str__(self):
        return self.name


class Folder(Audit, LegacyCode, OfficeMixin):
    folder_number = models.IntegerField(verbose_name='Número da Pasta', null=False, default=0)
    person_customer = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False,
                                        verbose_name='Cliente')
    cost_center = models.ForeignKey('financial.CostCenter',
                                    on_delete=models.PROTECT,
                                    blank=True,
                                    null=True,
                                    verbose_name='Centro de custo')

    objects = OfficeManager()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.folder_number = get_folder_number(self.office)
        super(Folder, self).save(*args, **kwargs)

    class Meta:
        db_table = "folder"
        ordering = ['-id']
        verbose_name = "Pasta"
        verbose_name_plural = "Pastas"

    def __str__(self):
        return str(self.folder_number)


class CourtDivision(Audit, LegacyCode, OfficeMixin):
    name = models.CharField(max_length=255, null=False, unique=True, verbose_name="Vara")

    objects = OfficeManager()

    class Meta:
        db_table = "court_division"
        verbose_name = "Vara"
        verbose_name_plural = "Varas"

    def __str__(self):
        return self.name


class CourtDistrict(Audit, LegacyCode):
    name = models.CharField(max_length=255, null=False, verbose_name="Nome")
    state = models.ForeignKey(State, on_delete=models.PROTECT, null=False, blank=False, verbose_name="Estado")

    class Meta:
        ordering = ('name', )
        db_table = "court_district"
        verbose_name = "Comarca"
        verbose_name_plural = "Comarcas"
        # cria constraint unique para a combinação de estado e comarca
        unique_together = (('state', 'name'),)

    def __str__(self):
        return self.name


class Organ(Person, OfficeMixin):
    """
    Classe responsavel por manter o cadastro dos tribunais.
    """
    court_district = models.ForeignKey(CourtDistrict, on_delete=models.PROTECT,
                                       verbose_name='Comarca')

    objects = OfficeManager()

    class Meta:
        db_table = 'organ'
        verbose_name = 'Órgao'
        verbose_name_plural = 'Órgãos'

    def validate_unique(self, exclude=None):
        """
        Este metodo faz a validacao dos campos unicos do modelo. Ele esta sendo sobrescrito pela
        necessidade de checar se existe ja existe um nome de orgao para a mesma comarca.
        (Verificar issue 0000411).
        obs.: unique_together nao funciona para esta classe pelo fato dele herdar de uma classe
        que nao e abstrata.
        :param exclude: Argumento opcional que permite que os campos informados nesta lista, nao
        sejam validados
        :type exclude: ValidationError
        """
        from django.core.exceptions import ObjectDoesNotExist
        res = super(Organ, self).validate_unique(exclude)
        try:
            if Organ.objects.filter(~Q(pk=self.pk), legal_name__iexact=self.legal_name,
                                    court_district=self.court_district):
                raise ValidationError({
                    NON_FIELD_ERRORS: ['Órgão deve ser único para a comarca']
                })
        except ObjectDoesNotExist:
            """Tratado exceção para quando estiver inserindo um novo registro e o `court_district` não for preenchido"""
        return res


class LawSuit(Audit, LegacyCode, OfficeMixin):
    person_lawyer = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False,
                                      verbose_name='Advogado', related_name='person_lawyers')
    folder = models.ForeignKey(Folder, on_delete=models.PROTECT, blank=False, null=False, verbose_name="Pasta",
                               related_name='folders')
    instance = models.ForeignKey(Instance, on_delete=models.PROTECT, blank=False, null=False, verbose_name='Instância',
                                 related_name='instances')
    court_district = models.ForeignKey(CourtDistrict, on_delete=models.PROTECT, blank=False, null=False,
                                       verbose_name='Comarca', related_name='court_districts')
    organ = models.ForeignKey(Organ, on_delete=models.PROTECT, blank=False, null=True,
                              related_name='organs', verbose_name=u'Tribunal')
    court_division = models.ForeignKey(CourtDivision, on_delete=models.PROTECT, blank=False, null=False,
                                       verbose_name='Vara', related_name='court_divisions')
    law_suit_number = models.CharField(max_length=255, blank=False, null=False,
                                       verbose_name='Número do Processo')
    is_current_instance = models.BooleanField(verbose_name='Instância Atual', default=False)
    opposing_party = models.TextField(blank=True, null=True, verbose_name='Parte adversa')

    objects = OfficeManager()

    class Meta:
        db_table = "law_suit"
        ordering = ['-id']
        verbose_name = "Processo"
        verbose_name_plural = "Processos"
        # cria constraint unique para a combinação de instancia e nr processo
        unique_together = (('instance', 'law_suit_number'),)

    def __str__(self):
        return self.law_suit_number


class Movement(Audit, LegacyCode, OfficeMixin):
    type_movement = models.ForeignKey(TypeMovement, on_delete=models.PROTECT, blank=False, null=False,
                                      verbose_name="Tipo de Movimentação")
    law_suit = models.ForeignKey(LawSuit, on_delete=models.PROTECT, blank=True, null=True,
                                 verbose_name="Processo", related_name='law_suits')
    folder = models.ForeignKey(Folder, on_delete=models.PROTECT, blank=False, null=False,
                               verbose_name="Pasta", related_name='folders_movement')

    objects = OfficeManager()

    class Meta:
        db_table = "movement"
        ordering = ['-id']
        verbose_name = "Movimentação"
        verbose_name_plural = "Movimentações"
        # unique_together = (('law_suit'),)

    def __str__(self):
        return self.type_movement.name  # TODO verificar novos campos e refatorar o toString
