import django_tables2 as tables
from django_tables2 import A, TemplateColumn

from .models import TypeMovement, Movement, LawSuit, Folder, Task, CourtDistrict


class TypeMovementTable(tables.Table):
    selection = TemplateColumn(
        '<div class="checkbox"><label><input type="checkbox" value="{{ record.pk }}" /></label></div>',
        verbose_name='', accessor='pk', attrs={'th__input':
                                                   {'onclick': 'toggle( this)'}}, orderable=False)

    name = tables.LinkColumn(viewname='type_movement_update', attrs={'a': {'target': 'type_movement_update'}},
                             args=[A('pk')])

    class Meta:
        sequence = ('selection', 'legacy_code', 'name', 'uses_wo')
        model = TypeMovement
        fields = ['selection', 'name', 'legacy_code', 'uses_wo']
        attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem tipos de movimentação cadastrados"


class MovementTable(tables.Table):
    selection = TemplateColumn(
        '<div class="checkbox"><label><input type="checkbox" value="{{ record.pk }}" /></label></div>',
        verbose_name='', accessor='pk', attrs={'th__input':
                                                   {'onclick': 'toggle( this)'}}, orderable=False)

    legacy_code = tables.LinkColumn(viewname='type_movement_update', attrs={'a': {'target': 'movement_update'}},
                                    args=[A('pk')])

    class Meta:
        sequence = ('selection', 'law_suit', 'person_lawyer', 'type_movement')
        model = Movement
        attrs = {"class": "table-striped table-bordered"}
        fields = ['selection', 'legacy_code', 'law_suit', 'person_lawyer', 'type_movement']
        empty_text = "Não existem movimentações cadastrados"


class FolderTable(tables.Table):
    # selection = tables.CheckBoxColumn(accessor="pk", attrs={'th__input':
    #                                                             {'onclick': 'toggle( this)'}}, orderable=False)
    selection = TemplateColumn(
        '<div class="checkbox"><label><input type="checkbox" value="{{ record.pk }}" /></label></div>',
        verbose_name='', accessor='pk', attrs={'th__input':
                                                   {'onclick': 'toggle( this)'}}, orderable=False)
    legacy_code = tables.LinkColumn(viewname='folder_update', attrs={'a': {'target': 'folder_update'}}, args=[A('pk')])

    class Meta:
        sequence = ('selection', 'legacy_code', 'person_customer', '...')
        model = Folder
        fields = ['selection', 'legacy_code', 'person_customer']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem pastas cadastradas"


class LawSuitTable(tables.Table):
    selection = TemplateColumn(
        '<div class="checkbox"><label><input type="checkbox" value="{{ record.pk }}" /></label></div>',
        verbose_name='', accessor='pk', attrs={'th__input':
                                                   {'onclick': 'toggle( this)'}}, orderable=False)

    class Meta:
        sequence = ('selection', 'folder', 'person_lawyer')
        model = LawSuit
        fields = ['selection', 'folder', 'person_lawyer']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem processos cadastrados"


class TaskTable(tables.Table):
    selection = TemplateColumn(
        '<div class="checkbox"><label><input type="checkbox" value="{{ record.pk }}" /></label></div>',
        verbose_name='', accessor='pk', attrs={'th__input':
                                                   {'onclick': 'toggle( this)'}}, orderable=False)
    legacy_code = tables.LinkColumn(viewname='task_update', attrs={'a': {'target': 'task_update'}}, args=[A('pk')])

    class Meta:
        model = Task
        fields = ['selection', 'legacy_code', 'movement', 'person', 'type_movement', 'delegation_date',
                  'acceptance_date', 'deadline_date', 'final_deadline_date', 'execution_deadline_date']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem providências cadastrados"


class CourtDistrictTable(tables.Table):
    selection = TemplateColumn(
        '<div class="checkbox"><label><input type="checkbox" value="{{ record.pk }}" /></label></div>',
        verbose_name='', accessor='pk', attrs={'th__input':
                                                   {'onclick': 'toggle( this)'}}, orderable=False)

    name = tables.LinkColumn(viewname='folder_update', attrs={'a': {'target': 'courtdistrict_update'}}, args=[A('pk')])

    class Meta:
        sequence = ('selection', 'name', 'state')
        model = CourtDistrict
        fields = ['selection', 'name', 'state']
        # attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem comarcas cadastrados"
