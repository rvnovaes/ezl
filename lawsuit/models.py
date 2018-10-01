from django.db import models
from core.models import Audit, Person, State, LegacyCode, OfficeMixin, OfficeManager
from sequences import get_next_value
from django.db import transaction
from django.core.validators import ValidationError
from django.core.exceptions import NON_FIELD_ERRORS, ObjectDoesNotExist
from django.db.models import Q


@transaction.atomic
def get_folder_number(office):
    return get_next_value('lawsuit_office_%s_folder_folder_number' % office.pk)


@transaction.atomic
def get_lawsuit_number():
    return get_next_value('lawsuit_lawsuit_lawsuit_number')


class TypeMovement(Audit, LegacyCode, OfficeMixin):
    name = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        default="",
        verbose_name='Nome')
    uses_wo = models.BooleanField(
        default=False, verbose_name='Utiliza ordem de serviço?')
    is_default = models.BooleanField(
        default=False, verbose_name='Movimentação padrão para importação')

    objects = OfficeManager()

    class Meta:
        db_table = "type_movement"
        ordering = ['-id']
        verbose_name = "Tipo de Movimentação"
        verbose_name_plural = "Tipos de Movimentação"
        unique_together = (('name', 'office'), )

    def __str__(self):
        return self.name


class Instance(Audit, LegacyCode, OfficeMixin):
    name = models.CharField(
        verbose_name="Nome",
        max_length=255,
        null=False,
        blank=False,
        default="")

    objects = OfficeManager()

    class Meta:
        db_table = "instance"
        ordering = ['-id']
        verbose_name = "Instância"
        verbose_name_plural = "Instâncias"
        unique_together = (('name', 'office'), )

    def __str__(self):
        return self.name


class Folder(Audit, LegacyCode, OfficeMixin):
    folder_number = models.IntegerField(
        verbose_name='Número da Pasta', null=False, default=0)
    person_customer = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        verbose_name='Cliente')
    cost_center = models.ForeignKey(
        'financial.CostCenter',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='Centro de custo')
    is_default = models.BooleanField(
        default=False, verbose_name='Pasta padrão para importação')

    objects = OfficeManager()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.folder_number = get_folder_number(self.office)
        super(Folder, self).save(*args, **kwargs)

    def simple_serialize(self):
        return {"id": self.id}

    class Meta:
        db_table = "folder"
        ordering = ['-id']
        verbose_name = "Pasta"
        verbose_name_plural = "Pastas"
        unique_together = (('folder_number', 'person_customer', 'office'), )

    def __str__(self):
        return "{} - {}".format(self.folder_number,
                                self.person_customer.legal_name)


class CourtDivision(Audit, LegacyCode, OfficeMixin):
    name = models.CharField(max_length=255, null=False, verbose_name="Vara")

    objects = OfficeManager()

    class Meta:
        db_table = "court_division"
        verbose_name = "Vara"
        verbose_name_plural = "Varas"
        unique_together = (('name', 'office'), )

    def __str__(self):
        return self.name


class CourtDistrict(Audit, LegacyCode):
    name = models.CharField(max_length=255, null=False, verbose_name="Nome")
    state = models.ForeignKey(
        State,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        verbose_name="Estado")

    class Meta:
        ordering = ('name', )
        db_table = "court_district"
        verbose_name = "Comarca"
        verbose_name_plural = "Comarcas"
        # cria constraint unique para a combinação de estado e comarca
        unique_together = (('state', 'name'), )

    def __str__(self):
        return '{} ({})'.format(self.name, self.state.initials)

    def simple_serialize(self):
        """Simple JSON representation of instance"""
        return {"id": self.id, "name": self.name}


class CourtDistrictComplement(Audit, LegacyCode, OfficeMixin):
    name = models.CharField(max_length=255, null=False, verbose_name="Nome")
    court_district = models.ForeignKey(CourtDistrict, on_delete=models.PROTECT, verbose_name='Comarca')

    objects = OfficeManager()

    class Meta:
        ordering = ('office', 'name',)
        verbose_name = "Complemento de comarca"
        verbose_name_plural = "Complementos de comarca"
        unique_together = (('name', 'court_district', 'office'),)


class Organ(Person, OfficeMixin):
    """
    Classe responsavel por manter o cadastro dos tribunais.
    """
    court_district = models.ForeignKey(
        CourtDistrict, on_delete=models.PROTECT, verbose_name='Comarca')

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
        res = super(Organ, self).validate_unique(exclude)
        try:
            if Organ.objects.filter(
                    ~Q(pk=self.pk),
                    legal_name__iexact=self.legal_name,
                    court_district=self.court_district,
                    office=self.office):
                raise ValidationError({
                    NON_FIELD_ERRORS: ['Órgão deve ser único para a comarca']
                })
        except ObjectDoesNotExist:
            """Tratado exceção para quando estiver inserindo um novo registro e o `court_district` não for preenchido"""
        return res

    def __str__(self):
        return self.legal_name


class LawSuit(Audit, LegacyCode, OfficeMixin):
    person_lawyer = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='Advogado',
        related_name='person_lawyers')
    folder = models.ForeignKey(
        Folder,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        verbose_name="Pasta",
        related_name='folders')
    instance = models.ForeignKey(
        Instance,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        verbose_name='Instância',
        related_name='instances')
    court_district = models.ForeignKey(
        CourtDistrict,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        verbose_name='Comarca',
        related_name='court_districts')
    organ = models.ForeignKey(
        Organ,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='organs',
        verbose_name=u'Órgão')
    court_division = models.ForeignKey(
        CourtDivision,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='Vara',
        related_name='court_divisions')
    law_suit_number = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        verbose_name='Número do Processo')
    is_current_instance = models.BooleanField(
        verbose_name='Instância Atual', default=False)
    opposing_party = models.TextField(
        blank=True, null=True, verbose_name='Parte adversa')

    objects = OfficeManager()

    def serialize(self):
        """JSON representation of instance"""
        data = {
            "id":
            self.id,
            "court_district":
            self.court_district.simple_serialize()
            if self.court_district else False,
            "law_suit_number":
            self.law_suit_number,
            "folder":
            self.folder.simple_serialize()
        }
        return data

    class Meta:
        db_table = "law_suit"
        ordering = ['-id']
        verbose_name = "Processo"
        verbose_name_plural = "Processos"

    def validate_unique(self, exclude=None):
        """
        Este metodo faz a validacao dos campos unicos do modelo. Ele esta sendo sobrescrito pela
        necessidade de checar se existe um registro com os mesmos dados de instance, law_suit_number, office,
        folder__folder_number, folder__person_customer.
        (https://mttech.atlassian.net/browse/EZL-939).
        obs.: unique_together nao funciona para esta classe porque seria necessário verificar campos de dois models
        distintos, e isso não pode ser feito pelo SQL.
        (https://stackoverflow.com/questions/4440010/django-unique-together-with-foreign-keys/4440189#4440189)
        :param exclude: Argumento opcional que permite que os campos informados nesta lista, nao sejam validados
        :type exclude: ValidationError
        """
        res = super(LawSuit, self).validate_unique(exclude)
        try:
            if LawSuit.objects.filter(
                    ~Q(pk=self.pk),
                    instance=self.instance,
                    law_suit_number=self.law_suit_number,
                    office=self.office,
                    folder__folder_number=self.folder.folder_number,
                    folder__person_customer=self.folder.person_customer):
                raise ValidationError({
                    NON_FIELD_ERRORS: [
                        'Processo com valores duplicados para os campos office, instance, '
                        'law_suit_number, folder__folder_number e folder__person_customer'
                        'DETAIL: Key(office, instance, law_suit_number, folder__folder_number, '
                        'folder__person_customer)=({}, {}, {}, {}, {})'.format(
                            self.office, self.instance, self.law_suit_number,
                            self.folder.folder_number,
                            self.folder.person_customer)
                    ]
                })
        except ObjectDoesNotExist:
            pass
        return res

    def __str__(self):
        ret = "{}".format(self.law_suit_number)
        if self.court_district:
            ret = "{} - {}".format(ret, self.court_district.name)
        return ret

    def save(self, *args, **kwargs):
        if not self.law_suit_number:
            self.law_suit_number = get_lawsuit_number()
        self.full_clean()
        super().save(*args, **kwargs)


class Movement(Audit, LegacyCode, OfficeMixin):
    type_movement = models.ForeignKey(
        TypeMovement,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        verbose_name="Tipo de Movimentação")
    law_suit = models.ForeignKey(
        LawSuit,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="Processo",
        related_name='law_suits')
    folder = models.ForeignKey(
        Folder,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        verbose_name="Pasta",
        related_name='folders_movement')

    def serialize(self):
        """JSON representation of instance"""
        data = {"id": self.id, "type_movement_name": self.type_movement.name}
        return data

    objects = OfficeManager()

    class Meta:
        db_table = "movement"
        ordering = ['-id']
        verbose_name = "Movimentação"
        verbose_name_plural = "Movimentações"

    def __str__(self):
        return self.type_movement.name  # TODO verificar novos campos e refatorar o toString
