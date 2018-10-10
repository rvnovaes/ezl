from core.models import Person
from decimal import Decimal
from django.utils import timezone
from financial.models import CostCenter
from import_export import resources
from import_export.widgets import DecimalWidget
from lawsuit.models import Folder, LawSuit, Movement, TypeMovement, CourtDistrict, CourtDivision, Organ, Instance, \
    TypeLawsuit, CourtDistrictComplement, City
from task.fields import CustomFieldImportExport
from task.instance_loaders import TaskModelInstanceLoader
from task.messages import *
from task.models import Task, TypeTask
from task.widgets import PersonAskedByWidget, UnaccentForeignKeyWidget, TaskStatusWidget, DateTimeWidgetMixin

TRUE_FALSE_DICT = {'V': True, 'F': False}

COLUMN_NAME_DICT = {
    'system_prefix': {
        'column_name': 'sistema',
        'attribute': 'system_prefix',
        'required': True,
        'verbose_name': Task._meta.get_field('system_prefix').verbose_name,
    },
    'folder_number': {
        'column_name': 'pasta.numero',
        'attribute': 'folder_number',
        'required': False,
        'verbose_name': Folder._meta.get_field('folder_number').verbose_name,
    },
    'folder_legacy_code': {
        'column_name': 'pasta.codigo_legado',
        'attribute': 'movement__folder__legacy_code',
        'required': False,
        'verbose_name': Folder._meta.get_field('legacy_code').verbose_name,
    },
    'folder_person_customer': {
        'column_name': 'pasta.cliente',
        'attribute': 'movement__folder__person_customer',
        'required': True,
        'verbose_name': Folder._meta.get_field('person_customer').verbose_name,
    },
    'folder_cost_center': {
        'column_name': 'pasta.centro_custo',
        'attribute': 'movement__folder__legacy_code',
        'required': False,
        'verbose_name': Folder._meta.get_field('cost_center').verbose_name,
    },
    'law_suit_number': {
        'column_name': 'processo.numero',
        'attribute': 'movement__law_suit__law_suit_number',
        'required': True,
        'verbose_name': LawSuit._meta.get_field('law_suit_number').verbose_name,
    },
    'type_lawsuit': {
        'column_name': 'processo.tipo',
        'attribute': 'movement__law_suit__type_lawsuit',
        'required': True,
        'verbose_name': LawSuit._meta.get_field('type_lawsuit').verbose_name,
    },
    'instance': {
        'column_name': 'processo.instancia',
        'attribute': 'movement__law_suit__instance__name',
        'required': False,
        'verbose_name': LawSuit._meta.get_field('instance').verbose_name,
    },
    'lawsuit_is_current_instance': {
        'column_name': 'processo.instancia_atual',
        'attribute': 'movement__law_suit__is_current_instance',
        'required': True,
        'verbose_name': LawSuit._meta.get_field('is_current_instance').verbose_name,
    },
    'lawsuit_person_lawyer': {
        'column_name': 'processo.advogado',
        'attribute': 'movement__law_suit__person_lawyer',
        'required': False,
        'verbose_name': LawSuit._meta.get_field('person_lawyer').verbose_name,
    },
    'lawsuit_court_district': {
        'column_name': 'processo.comarca',
        'attribute': 'movement__law_suit__court_district',
        'required': False,
        'verbose_name': LawSuit._meta.get_field('court_district').verbose_name,
    },
    'lawsuit_court_district_complement': {
        'column_name': 'processo.complemento_comarca',
        'attribute': 'movement__law_suit__court_district_complement',
        'required': False,
        'verbose_name': LawSuit._meta.get_field('court_district_complement').verbose_name,
    },
    'lawsuit_city': {
        'column_name': 'processo.cidade',
        'attribute': 'movement__law_suit__city',
        'required': False,
        'verbose_name': LawSuit._meta.get_field('city').verbose_name,
    },
    'lawsuit_court_division': {
        'column_name': 'processo.vara',
        'attribute': 'movement__law_suit__court_division',
        'required': False,
        'verbose_name': LawSuit._meta.get_field('court_division').verbose_name,
    },
    'lawsuit_organ': {
        'column_name': 'processo.orgao',
        'attribute': 'movement__law_suit__organ',
        'required': False,
        'verbose_name': LawSuit._meta.get_field('organ').verbose_name,
    },
    'lawsuit_opposing_party': {
        'column_name': 'processo.parte_adversa',
        'attribute': 'movement__law_suit__opposing_party',
        'required': False,
        'verbose_name': LawSuit._meta.get_field('opposing_party').verbose_name,
    },
    'lawsuit_legacy_code': {
        'column_name': 'processo.codigo_legado',
        'attribute': 'movement__law_suit__legacy_code',
        'required': False,
        'verbose_name': LawSuit._meta.get_field('legacy_code').verbose_name,
    },
    'type_movement': {
        'column_name': 'movimentacao.tipo',
        'attribute': 'movement__type_movement__name',
        'required': True,
        'verbose_name': Movement._meta.get_field('type_movement').verbose_name,
    },
    'movement_legacy_code': {
        'column_name': 'movimentacao.codigo_legado',
        'attribute': 'movement__legacy_code',
        'required': False,
        'verbose_name': Movement._meta.get_field('legacy_code').verbose_name,
    },
    'person_asked_by': {
        'column_name': 'os.solicitante',
        'attribute': 'person_asked_by',
        'required': True,
        'verbose_name': Task._meta.get_field('person_asked_by').verbose_name,
    },
    'type_task': {
        'column_name': 'os.tipo_servico',
        'attribute': 'type_task',
        'required': True,
        'verbose_name': Task._meta.get_field('type_task').verbose_name,
    },
    'final_deadline_date': {
        'column_name': 'os.prazo_fatal',
        'attribute': 'final_deadline_date',
        'required': True,
        'verbose_name': Task._meta.get_field('final_deadline_date').verbose_name,
    },
    'performance_place': {
        'column_name': 'os.local_cumprimento',
        'attribute': 'billing_date',
        'required': True,
        'verbose_name': Task._meta.get_field('performance_place').verbose_name,
    },
    'description': {
        'column_name': 'os.descricao',
        'attribute': 'description',
        'required': False,
        'verbose_name': Task._meta.get_field('description').verbose_name,
    },
    'person_executed_by': {
        'column_name': 'os.correspondente',
        'attribute': 'person_executed_by',
        'required': False,
        'verbose_name': Task._meta.get_field('person_executed_by').verbose_name,
    },
    'person_distributed_by': {
        'column_name': 'os.contratante',
        'attribute': 'person_distributed_by',
        'required': False,
        'verbose_name': Task._meta.get_field('person_distributed_by').verbose_name,
    },
    'delegation_date': {
        'column_name': 'os.data_delegacao',
        'attribute': 'delegation_date',
        'required': False,
        'verbose_name': Task._meta.get_field('delegation_date').verbose_name,
    },
    'execution_date': {
        'column_name': 'os.data_cumprimento',
        'attribute': 'execution_date',
        'required': False,
        'verbose_name': Task._meta.get_field('execution_date').verbose_name,
    },
    'requested_date': {
        'column_name': 'os.data_solicitacao',
        'attribute': 'requested_date',
        'required': False,
        'verbose_name': Task._meta.get_field('requested_date').verbose_name,
    },
    'acceptance_date': {
        'column_name': 'os.data_aceite',
        'attribute': 'acceptance_date',
        'required': False,
        'verbose_name': Task._meta.get_field('acceptance_date').verbose_name,
    },
    'task_status': {
        'column_name': 'os.status',
        'attribute': 'task_status',
        'required': True,
        'verbose_name': Task._meta.get_field('task_status').verbose_name,
    },
    'amount': {
        'column_name': 'os.valor',
        'attribute': 'amount',
        'required': False,
        'verbose_name': Task._meta.get_field('amount').verbose_name,
    },
    'is_active': {
        'column_name': 'os.ativa',
        'attribute': 'is_active',
        'required': False,
        'verbose_name': Task._meta.get_field('is_active').verbose_name,
    },
    'acceptance_service_date': {
        'column_name': 'os.data_aceite_service',
        'attribute': 'acceptance_service_date',
        'required': False,
        'verbose_name': Task._meta.get_field('acceptance_service_date').verbose_name,
    },
    'refused_service_date': {
        'column_name': 'os.data_recusa_service',
        'attribute': 'refused_service_date',
        'required': False,
        'verbose_name': Task._meta.get_field('refused_service_date').verbose_name,
    },
    'refused_date': {
        'column_name': 'os.data_recusa_correspondente',
        'attribute': 'refused_date',
        'required': False,
        'verbose_name': Task._meta.get_field('refused_date').verbose_name,
    },
    'return_date': {
        'column_name': 'os.data_retorno',
        'attribute': 'return_date',
        'required': False,
        'verbose_name': Task._meta.get_field('return_date').verbose_name,
    },
    'blocked_payment_date': {
        'column_name': 'os.data_glosa',
        'attribute': 'blocked_payment_date',
        'required': False,
        'verbose_name': Task._meta.get_field('blocked_payment_date').verbose_name,
    },
    'finished_date': {
        'column_name': 'os.data_finalizacao',
        'attribute': 'finished_date',
        'required': False,
        'verbose_name': Task._meta.get_field('finished_date').verbose_name,
    },
    'receipt_date': {
        'column_name': 'os.data_recebimento',
        'attribute': 'receipt_date',
        'required': False,
        'verbose_name': Task._meta.get_field('receipt_date').verbose_name,
    },
    'billing_date': {
        'column_name': 'os.data_pagamento',
        'attribute': 'billing_date',
        'required': False,
        'verbose_name': Task._meta.get_field('billing_date').verbose_name,
    },
    'legacy_code': {
        'column_name': 'os.codigo_legado',
        'attribute': 'legacy_code',
        'required': False,
        'verbose_name': Task._meta.get_field('legacy_code').verbose_name,
    },
}


def self_or_none(obj):
    return obj if obj else None


def insert_incorrect_natural_key_message(row, key):
    return INCORRECT_NATURAL_KEY.format(COLUMN_NAME_DICT[key]['verbose_name'],
                                        COLUMN_NAME_DICT[key]['column_name'],
                                        row[key])


class TaskResource(resources.ModelResource):
    type_task = CustomFieldImportExport(column_name='type_task', attribute='type_task',
                                        widget=UnaccentForeignKeyWidget(TypeTask, 'name'), saves_null_values=False,
                                        column_name_dict=COLUMN_NAME_DICT)
    movement = CustomFieldImportExport(column_name='movement', attribute='movement_id', saves_null_values=False,
                                       column_name_dict=COLUMN_NAME_DICT)
    person_asked_by = CustomFieldImportExport(column_name='person_asked_by', attribute='person_asked_by',
                                              widget=PersonAskedByWidget(Person, 'legal_name'), saves_null_values=False,
                                              column_name_dict=COLUMN_NAME_DICT)
    person_executed_by = CustomFieldImportExport(column_name='person_executed_by', attribute='person_executed_by',
                                                 widget=UnaccentForeignKeyWidget(Person, 'legal_name'),
                                                 column_name_dict=COLUMN_NAME_DICT)
    person_distributed_by = CustomFieldImportExport(column_name='person_distributed_by',
                                                    attribute='person_distributed_by',
                                                    widget=UnaccentForeignKeyWidget(Person, 'legal_name'),
                                                    column_name_dict=COLUMN_NAME_DICT)
    final_deadline_date = CustomFieldImportExport(column_name='final_deadline_date', attribute='final_deadline_date',
                                                  widget=DateTimeWidgetMixin(), saves_null_values=False,
                                                  column_name_dict=COLUMN_NAME_DICT)
    delegation_date = CustomFieldImportExport(column_name='delegation_date', attribute='delegation_date',
                                              widget=DateTimeWidgetMixin(), column_name_dict=COLUMN_NAME_DICT)
    acceptance_date = CustomFieldImportExport(column_name='acceptance_date', attribute='acceptance_date',
                                              widget=DateTimeWidgetMixin(), column_name_dict=COLUMN_NAME_DICT)
    execution_date = CustomFieldImportExport(column_name='execution_date', attribute='execution_date',
                                             widget=DateTimeWidgetMixin(), column_name_dict=COLUMN_NAME_DICT)
    requested_date = CustomFieldImportExport(column_name='requested_date', attribute='requested_date',
                                             widget=DateTimeWidgetMixin(), default=timezone.now(),
                                             column_name_dict=COLUMN_NAME_DICT)
    acceptance_service_date = CustomFieldImportExport(column_name='acceptance_service_date',
                                                      attribute='acceptance_service_date', widget=DateTimeWidgetMixin(),
                                                      column_name_dict=COLUMN_NAME_DICT)
    refused_service_date = CustomFieldImportExport(column_name='refused_service_date', attribute='refused_service_date',
                                                   widget=DateTimeWidgetMixin(), column_name_dict=COLUMN_NAME_DICT)
    refused_date = CustomFieldImportExport(column_name='refused_date', attribute='refused_date',
                                           widget=DateTimeWidgetMixin(), column_name_dict=COLUMN_NAME_DICT)
    return_date = CustomFieldImportExport(column_name='return_date', attribute='return_date',
                                          widget=DateTimeWidgetMixin(), column_name_dict=COLUMN_NAME_DICT)
    blocked_payment_date = CustomFieldImportExport(column_name='blocked_payment_date', attribute='blocked_payment_date',
                                                   widget=DateTimeWidgetMixin(), column_name_dict=COLUMN_NAME_DICT)
    finished_date = CustomFieldImportExport(column_name='finished_date', attribute='finished_date',
                                            widget=DateTimeWidgetMixin(), column_name_dict=COLUMN_NAME_DICT)
    receipt_date = CustomFieldImportExport(column_name='receipt_date', attribute='receipt_date',
                                           widget=DateTimeWidgetMixin(), column_name_dict=COLUMN_NAME_DICT)
    billing_date = CustomFieldImportExport(column_name='billing_date', attribute='billing_date',
                                           widget=DateTimeWidgetMixin(), column_name_dict=COLUMN_NAME_DICT)
    task_status = CustomFieldImportExport(column_name='task_status', attribute='task_status', widget=TaskStatusWidget(),
                                          column_name_dict=COLUMN_NAME_DICT)
    amount = CustomFieldImportExport(column_name='amount', attribute='amount', widget=DecimalWidget(),
                                     default=Decimal('0.00'), column_name_dict=COLUMN_NAME_DICT)
    performance_place = CustomFieldImportExport(column_name='performance_place', attribute='performance_place',
                                                saves_null_values=False, column_name_dict=COLUMN_NAME_DICT)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.office = None
        self.create_user = None
        self.office_id = None
        self.default_type_movement = None
        self._meta.instance_loader_class = TaskModelInstanceLoader
        self.folder = None
        self.lawsuit = None
        self.movement = None

    class Meta:
        model = Task
        import_id_fields = ('legacy_code', )

    def validate_folder(self, row, row_errors):
        folder_number = int(
            row['folder_number']) if row['folder_number'] else ''
        folder_legacy_code = row['folder_legacy_code']
        cost_center = row['folder_cost_center']
        if cost_center:
            cost_center = CostCenter.objects.get_queryset(office=[self.office_id]).filter(
                name__unaccent__icontains=cost_center).first()
            if not cost_center:
                row_errors.append(insert_incorrect_natural_key_message(row, 'folder_cost_center'))
        folder = None
        if not row['folder_person_customer']:
            row_errors.append(REQUIRED_COLUMN.format(COLUMN_NAME_DICT['folder_person_customer']['column_name']))
        else:
            person_customer = Person.objects.filter(legal_name__unaccent__icontains=row['folder_person_customer'],
                                                    is_customer=True).first()
            if not person_customer:
                row_errors.append(insert_incorrect_natural_key_message(row, 'folder_person_customer'))
            else:
                if not (folder_legacy_code or folder_number):
                    folder, created = Folder.objects.get_or_create(
                        person_customer=person_customer,
                        is_default=True,
                        office=self.office,
                        defaults={'create_user': self.create_user})
                else:
                    if folder_legacy_code:
                        folder, created = Folder.objects.get_or_create(
                            legacy_code=folder_legacy_code,
                            person_customer=person_customer,
                            office=self.office,
                            defaults={'create_user': self.create_user,
                                      'folder_number': folder_number,
                                      'cost_center': cost_center})
                    if not folder and folder_number:
                        folder, created = Folder.objects.get_or_create(
                            folder_number=folder_number,
                            person_customer=person_customer,
                            office=self.office,
                            defaults={'create_user': self.create_user,
                                      'legacy_code': folder_legacy_code,
                                      'cost_center': cost_center})
        if not folder:
            row_errors.append(RECORD_NOT_FOUND.format(Folder._meta.verbose_name))
        return folder

    def validate_lawsuit(self, row, row_errors):
        lawsuit_number = str(row['law_suit_number'])
        lawsuit_legacy_code = row['lawsuit_legacy_code']
        lawsuit = None
        type_lawsuit = row['type_lawsuit']
        if not lawsuit_legacy_code and not (lawsuit_number and type_lawsuit):
            row_errors.append(REQUIRED_ONE_IN_GROUP.format('identificação do processo',
                                                           [COLUMN_NAME_DICT['law_suit_number']['column_name'],
                                                            COLUMN_NAME_DICT['type_lawsuit']['column_name'],
                                                            COLUMN_NAME_DICT['lawsuit_legacy_code']['column_name']]))
        else:
            if lawsuit_legacy_code:
                lawsuit = LawSuit.objects.filter(
                    legacy_code=lawsuit_legacy_code,
                    folder=self.folder,
                    office_id=self.office_id).first()
            if not lawsuit and lawsuit_number:
                lawsuit = LawSuit.objects.filter(
                    law_suit_number=lawsuit_number,
                    folder=self.folder,
                    office_id=self.office_id).first()
            if not lawsuit:
                instance = None
                if row['instance']:
                    instance = Instance.objects.filter(name=row['instance'], office=self.office).first()
                    if not instance:
                        row_errors.append(insert_incorrect_natural_key_message(row, 'instance'))
                is_current_instance = TRUE_FALSE_DICT.get(row['lawsuit_is_current_instance'], False)
                person_lawyer = row.get('lawsuit_person_lawyer', '')
                if person_lawyer:
                    person_lawyer = Person.objects.filter(legal_name__unaccent__icontains=person_lawyer,
                                                          is_lawyer=True,
                                                          offices=self.office).first()
                    if not person_lawyer:
                        row_errors.append(insert_incorrect_natural_key_message(row, 'lawsuit_person_lawyer'))
                court_district = row.get('lawsuit_court_district', '')
                if court_district:
                    court_district = CourtDistrict.objects.filter(name=court_district).first()
                    if not court_district:
                        row_errors.append(insert_incorrect_natural_key_message(row, 'lawsuit_court_district'))
                court_district_complement = row.get('lawsuit_court_district_complement', '')
                if court_district_complement:
                    court_district_complement = CourtDistrictComplement.objects.filter(
                        name=court_district_complement).first()
                    if not court_district_complement:
                        row_errors.append(insert_incorrect_natural_key_message(row,
                                                                               'lawsuit_court_district_complement'))
                city = row.get('lawsuit_city', '')
                if city:
                    city = City.objects.filter(name=city).first()
                    if not city:
                        row_errors.append(insert_incorrect_natural_key_message(row, 'lawsuit_city'))
                court_division = row.get('lawsuit_court_division', '')
                if court_division:
                    court_division = CourtDivision.objects.filter(name=court_division,
                                                                  office=self.office).first()
                    if not court_division:
                        row_errors.append(insert_incorrect_natural_key_message(row, 'lawsuit_court_division'))
                organ = row.get('lawsuit_organ', '')
                if organ:
                    organ = Organ.objects.get_queryset(office=[self.office_id]).filter(legal_name=organ).first()
                    if not organ:
                        row_errors.append(insert_incorrect_natural_key_message(row, 'lawsuit_organ'))
                opposing_party = row.get('lawsuit_opposing_party', '')
                if not row_errors:
                    lawsuit = LawSuit.objects.create(type_lawsuit=TypeLawsuit(type_lawsuit).name,
                                                     person_lawyer=self_or_none(person_lawyer),
                                                     folder=self.folder,
                                                     instance=self_or_none(instance),
                                                     court_district=self_or_none(court_district),
                                                     court_district_complement=self_or_none(court_district_complement),
                                                     city=self_or_none(city),
                                                     organ=self_or_none(organ),
                                                     court_division=self_or_none(court_division),
                                                     law_suit_number=lawsuit_number,
                                                     is_current_instance=is_current_instance,
                                                     opposing_party=self_or_none(opposing_party),
                                                     create_user=self.create_user,
                                                     office=self.office,
                                                     legacy_code=lawsuit_legacy_code)
        if not lawsuit:
            row_errors.append(RECORD_NOT_FOUND.format(LawSuit._meta.verbose_name))
        return lawsuit

    def validate_movement(self, row, row_errors):
        type_movement_name = row['type_movement']
        movement_legacy_code = row['movement_legacy_code']
        movement = None
        if not (type_movement_name or movement_legacy_code):
            movement, created = Movement.objects.get_or_create(
                folder=self.folder,
                law_suit=self.lawsuit,
                type_movement=self.default_type_movement,
                office=self.office,
                defaults={'create_user': self.create_user})
        else:
            type_movement = TypeMovement.objects.filter(name=type_movement_name).first()
            if movement_legacy_code:
                movement, created = Movement.objects.get_or_create(
                    legacy_code=movement_legacy_code,
                    office_id=self.office_id,
                    defaults={'folder': self.folder,
                              'law_suit': self.lawsuit,
                              'type_movement': type_movement})
            if not movement and (type_movement and self.folder
                                 and self.lawsuit):
                movement, created = Movement.objects.get_or_create(
                    folder=self.folder,
                    law_suit=self.lawsuit,
                    office_id=self.office_id,
                    defaults={'folder': self.folder,
                              'law_suit': self.lawsuit,
                              'type_movement': type_movement,
                              'legacy_code': movement_legacy_code})
        if not movement:
            row_errors.append(RECORD_NOT_FOUND.format(Movement._meta.verbose_name))
        return movement

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        self.office = kwargs['office']
        self.create_user = kwargs['create_user']
        self.office_id = self.office.id
        for k, v in COLUMN_NAME_DICT.items():
            if v['column_name'] in dataset.headers:
                headers_index = dataset.headers.index(v['column_name'])
                dataset.headers[headers_index] = k

        if 'id' not in dataset._Dataset__headers:
            dataset.insert_col(
                0, col=[
                    "",
                ] * dataset.height, header="id")
        else:
            self.__setattr__('import_id_fields', ('id', ))

        self.default_type_movement, created = TypeMovement.objects.get_or_create(
            is_default=True,
            office=self.office,
            defaults={
                'name': 'OS Avulsa',
                'create_user': self.create_user
            })
        dataset.insert_col(1, col=[int("{}".format(self.office.id)), ] * dataset.height, header="office")
        dataset.insert_col(1, col=[int("{}".format(self.create_user.id)), ] * dataset.height, header="create_user")
        dataset.insert_col(3, col=["", ] * dataset.height, header="movement")

    def before_import_row(self, row, **kwargs):
        row_errors = []
        self.folder = self.validate_folder(row, row_errors)
        self.lawsuit = self.validate_lawsuit(row, row_errors) if self.folder else None
        self.movement = self.validate_movement(row, row_errors) if self.lawsuit else None

        if self.movement:
            row['movement'] = self.movement.id
        if row_errors:
            raise Exception(row_errors)
        row['is_active'] = TRUE_FALSE_DICT.get('is_active', True)
