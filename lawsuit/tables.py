import django_tables2 as tables
from django_tables2 import A

from core.tables import CheckBoxMaterial
from .models import TypeMovement, Movement, LawSuit, Folder, CourtDistrict, Instance, LawSuitInstance


class InstanceTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)
    name = tables.LinkColumn(viewname='instance_update', attrs={'a': {'target': 'instance_update'}},
                             args=[A('pk')])

    class Meta:
        sequence = ('selection', 'name', 'is_active')
        model = Instance
        fields = ['name', 'is_active']
        attrs = {"class": "table stable-striped table-bordered"}
        empty_text = "Não existem instâncias cadastradas"


class TypeMovementTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    name = tables.LinkColumn(viewname='type_movement_update', attrs={'a': {'target': 'type_movement_update'}},
                             args=[A('pk')])

    class Meta:
        sequence = ('selection', 'name', 'legacy_code', 'uses_wo', 'is_active')
        model = TypeMovement
        fields = ['selection', 'name', 'legacy_code', 'uses_wo', 'is_active']
        attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem tipos de movimentação cadastrados"


class MovementTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    legacy_code = tables.LinkColumn(viewname='movement_update', attrs={'a': {'target': 'movement_update'}},
                                    args=[A('pk')])

    class Meta:
        sequence = ('selection', 'legacy_code', 'person_lawyer', 'type_movement', 'law_suit_instance', 'deadline',
                    'is_active')
        model = Movement
        attrs = {"class": "table-striped table-bordered"}
        fields = ['selection', 'legacy_code', 'person_lawyer', 'type_movement', 'law_suit_instance', 'deadline',
                  'is_active']
        empty_text = "Não existem movimentações cadastrados"


class FolderTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    legacy_code = tables.LinkColumn(viewname='folder_update', attrs={'a': {'target': 'folder_update'}}, args=[A('pk')])

    class Meta:
        sequence = ('selection', 'legacy_code', 'person_customer', 'is_active', '...')
        model = Folder
        fields = ['selection', 'legacy_code', 'person_customer', 'is_active']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem pastas cadastradas"


class LawSuitTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    class Meta:
        sequence = ('selection', 'folder', 'person_lawyer', 'is_active')
        model = LawSuit
        fields = ['selection', 'folder', 'person_lawyer', 'is_active']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem processos cadastrados"


class CourtDivisionTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    legacy_code = tables.LinkColumn(viewname='courtdivision_update', attrs={'a': {'target': 'courtdivision_update'}},
                                    args=[A('pk')])
    name = tables.LinkColumn(viewname='courtdivision_update', attrs={'a': {'target': 'courtdivision_update'}},
                             args=[A('pk')])

    class Meta:
        sequence = ('selection', 'legacy_code', 'name', 'is_active')
        model = CourtDistrict
        fields = ['selection', 'legacy_code', 'name', 'is_active']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem varas cadastradas"


class CourtDistrictTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    name = tables.LinkColumn(viewname='courtdistrict_update', attrs={'a': {'target': 'courtdistrict_update'}},
                             args=[A('pk')])

    class Meta:
        sequence = ('selection', 'name', 'state', 'is_active')
        model = CourtDistrict
        fields = ['selection', 'name', 'state', 'is_active']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem comarcas cadastradas"


class LawSuitInstanceTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)
    law_suit_number = tables.LinkColumn(viewname='lawsuitinstance_update',
                                        attrs={'a': {'target': 'lawsuitinstance_update'}}, args=[A('pk')])

    class Meta:
        sequence = ('selection', 'law_suit_number', 'law_suit', 'instance', 'court_district', 'person_court',
                    'is_active')
        model = LawSuitInstance
        fields = ['selection', 'law_suit_number', 'law_suit', 'instance', 'court_district', 'person_court',
                  'is_active']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem instâncias de processo cadastrados"
