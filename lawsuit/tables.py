import django_tables2 as tables
from django_tables2 import A

from core.tables import CheckBoxMaterial
from .models import TypeMovement, Movement, Folder, CourtDistrict, Instance, LawSuit


class InstanceTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)
    name = tables.LinkColumn(viewname='instance_update', attrs={'a': {'target': 'instance_update'}},
                             args=[A('pk')])

    class Meta:
        sequence = ('selection', 'name', 'is_active', 'legacy_code')
        model = Instance
        fields = ['name', 'is_active','legacy_code']
        attrs = {"class": "table stable-striped table-bordered"}
        empty_text = "Não existem instâncias cadastradas"
        row_attrs = {
            'data_href': lambda record: '/processos/instancias/' + str(record.pk) + '/'
        }


class TypeMovementTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    name = tables.LinkColumn(viewname='type_movement_update', attrs={'a': {'target': 'type_movement_update'}},
                             args=[A('pk')])

    class Meta:
        sequence = ('selection', 'name',  'is_active','legacy_code')
        model = TypeMovement
        fields = ['selection', 'name', 'legacy_code', 'is_active']
        attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem tipos de movimentação cadastrados"
        row_attrs = {
            'data_href': lambda record: '/processos/tipo-movimentacao/' + str(record.pk) + '/'
        }


class MovementTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    type_movement = tables.LinkColumn(viewname='movement_update', attrs={'a': {'target': 'movement_update'}},
                                      args=[A('law_suit.pk'), A('pk')])

    class Meta:
        sequence = ('selection', 'type_movement', 'law_suit', 'person_lawyer', 'deadline',
                    'is_active', 'legacy_code')
        model = Movement
        attrs = {"class": "table-striped table-bordered"}
        fields = ['selection', 'legacy_code', 'person_lawyer', 'type_movement', 'law_suit', 'deadline',
                  'is_active']
        empty_text = "Não existem movimentações cadastrados"
        row_attrs = {
            'data_href': lambda record: '/processos/movimentacao/' + str(record.law_suit.pk) + '/' + str(record.pk) + '/'
        }


class FolderTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    legacy_code = tables.LinkColumn(viewname='folder_update', attrs={'a': {'target': 'folder_update'}}, args=[A('pk')])

    class Meta:
        sequence = ('selection', 'folder_number', 'person_customer', 'is_active', 'legacy_code')
        model = Folder
        fields = ['folder_number','selection', 'legacy_code', 'person_customer', 'is_active']
        readonly_fields = ['folder_number']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem pastas cadastradas"
        row_attrs = {
            'data_href': lambda record: '/processos/pastas/' + str(record.pk) + '/'
        }


class LawSuitTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)
    law_suit_number = tables.LinkColumn(viewname='lawsuit_update',
                                        attrs={'a': {'target': 'lawsuit_update'}}, args=[A('folder.pk'), A('pk')])

    class Meta:
        sequence = (
            'selection', 'law_suit_number', 'folder', 'instance', 'court_district', 'person_court', 'court_division',
            'person_lawyer', 'is_current_instance', 'is_active', 'legacy_code')
        model = LawSuit
        fields = ['selection', 'folder', 'instance', 'court_district', 'person_court', 'court_division',
                  'law_suit_number', 'person_lawyer', 'is_active', 'is_current_instance','legacy_code']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem processos cadastrados"
        row_attrs = {
            'data_href': lambda record: '/processos/processos/' + str(record.folder.pk) + '/' + str(record.pk)
        }


class CourtDivisionTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    legacy_code = tables.LinkColumn(viewname='courtdivision_update', attrs={'a': {'target': 'courtdivision_update'}},
                                    args=[A('pk')])
    name = tables.LinkColumn(viewname='courtdivision_update', attrs={'a': {'target': 'courtdivision_update'}},
                             args=[A('pk')])

    class Meta:
        sequence = ('selection', 'name', 'is_active','legacy_code')
        model = CourtDistrict
        fields = ['selection', 'legacy_code', 'name', 'is_active']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem varas cadastradas"
        row_attrs = {
            'data_href': lambda record: '/processos/varas/' + str(record.pk) + '/'
        }


class CourtDistrictTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    name = tables.LinkColumn(viewname='courtdistrict_update', attrs={'a': {'target': 'courtdistrict_update'}},
                             args=[A('pk')])

    class Meta:
        sequence = ('selection', 'name', 'state', 'is_active','legacy_code')
        model = CourtDistrict
        fields = ['selection', 'name', 'state', 'is_active','legacy_code']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem comarcas cadastradas"
        row_attrs = {
            'data_href': lambda record: '/processos/comarcas/' + str(record.pk) + '/'
        }

