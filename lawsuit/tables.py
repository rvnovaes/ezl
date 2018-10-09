import django_tables2 as tables

from core.tables import CheckBoxMaterial
from core.models import Address
from .models import (TypeMovement, Movement, Folder, CourtDistrict, Instance, LawSuit, Organ, CourtDistrictComplement)
from django_tables2.utils import A


class InstanceTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    class Meta:
        sequence = ('selection', 'name', 'is_active', 'legacy_code')
        model = Instance
        fields = ['name', 'is_active', 'legacy_code']
        attrs = {"class": "table stable-striped table-bordered"}
        empty_text = "Não existem instâncias cadastradas"
        row_attrs = {
            'data_href':
            lambda record: '/processos/instancias/' + str(record.pk) + '/'
        }
        order_by = 'name'


class TypeMovementTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    class Meta:
        sequence = ('selection', 'name', 'is_active', 'legacy_code',
                    'is_default')
        model = TypeMovement
        fields = [
            'selection', 'name', 'legacy_code', 'is_default', 'is_active'
        ]
        attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem tipos de movimentações cadastradas"
        row_attrs = {
            'data_href':
            lambda record: '/processos/tipo-movimentacao/' + str(record.pk) + '/'
        }
        order_by = 'name'


class MovementTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    class Meta:
        sequence = ('selection', 'type_movement', 'is_active', 'legacy_code')
        model = Movement
        attrs = {"class": "table-striped table-bordered"}
        fields = [
            'selection', 'legacy_code', 'type_movement', 'is_active',
            'create_date'
        ]
        empty_text = "Não existem movimentações cadastradas"
        row_attrs = {
            'data_href':
            lambda record: '/processos/movimentacao/' + str(record.law_suit.pk) + '/' + str(record.pk) + '/'
        }
        order_by = '-create_date'


class FolderTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    class Meta:
        sequence = ('selection', 'folder_number', 'person_customer',
                    'cost_center', 'is_active', 'legacy_code', 'is_default')
        model = Folder
        fields = [
            'folder_number', 'selection', 'legacy_code', 'person_customer',
            'cost_center', 'is_active', 'is_default'
        ]
        readonly_fields = ['folder_number']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem pastas cadastradas"
        row_attrs = {
            'data_href':
            lambda record: '/processos/pastas/' + str(record.pk) + '/'
        }
        order_by = 'folder_number'


class LawSuitTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    class Meta:
        sequence = ('selection', 'type_lawsuit', 'law_suit_number', 'opposing_party',
                    'court_district', 'instance', 'organ', 'court_division',
                    'person_lawyer', 'is_current_instance', 'is_active',
                    'legacy_code')
        model = LawSuit
        fields = [
            'selection', 'instance', 'court_district', 'organ', 'court_division', 'law_suit_number', 'person_lawyer',
            'is_active', 'is_current_instance', 'legacy_code', 'opposing_party', 'type_lawsuit'
        ]
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem processos cadastrados"
        row_attrs = {
            'data_href':
            lambda record: '/processos/processos/' + str(record.folder.pk) + '/' + str(record.pk)
        }


class CourtDivisionTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    class Meta:
        sequence = ('selection', 'name', 'is_active', 'legacy_code')
        model = CourtDistrict
        fields = ['selection', 'legacy_code', 'name', 'is_active']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem varas cadastradas"
        row_attrs = {
            'data_href':
            lambda record: '/processos/varas/' + str(record.pk) + '/'
        }
        order_by = 'name'


class CourtDistrictTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    class Meta:
        sequence = ('selection', 'name', 'state', 'is_active', 'legacy_code')
        model = CourtDistrict
        fields = ['selection', 'name', 'state', 'is_active', 'legacy_code']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem comarcas cadastradas"
        row_attrs = {
            'data_href':
            lambda record: '/processos/comarcas/' + str(record.pk) + '/'
        }


class OrganTable(tables.Table):
    """
    Classe responsavel por gerar a tabela de orgaos cadastrados para a listagem de orgaos
    """
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    class Meta:
        sequence = []
        model = Organ
        fields = [
            'selection', 'legal_name', 'cnpj', 'court_district', 'is_active',
            'legacy_code'
        ]
        attrs = {}
        empty_text = ""
        row_attrs = {
            'data_href':
            lambda record: '/processos/orgaos/' + str(record.pk) + '/'
        }
        order_by = 'name'


class AddressOrganTable(tables.Table):
    edit_link = tables.LinkColumn(
        'address_organ_update',
        verbose_name="",
        text="Editar",
        args=[A('person_id'), A('pk')])

    delete_link = tables.LinkColumn(
        'address_organ_delete',
        verbose_name="",
        text="Excluir",
        args=[A('person_id'), A('pk')])

    class Meta:
        model = Address
        fields = [
            'street', 'number', 'complement', 'city_region', 'zip_code',
            'country', 'state', 'city', 'notes', 'address_type', 'is_active',
            'edit_link', 'delete_link'
        ]
        attrs = {'class': 'table table-hover'}


class CourtDistrictComplementTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    class Meta:
        sequence = ('selection', 'name', 'court_district', 'is_active')
        model = CourtDistrictComplement
        fields = ['selection', 'name', 'court_district', 'is_active', 'office']
        empty_text = "Não existem complementos de comarca cadastrados"
        row_attrs = {
            'data_href':
            lambda record: '/processos/complemento/' + str(record.pk) + '/'
        }
        order_by = ('office', 'name')
