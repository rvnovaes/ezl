from core.models import Person
from decimal import Decimal
from django.db.models.fields import NOT_PROVIDED
from django.utils import timezone
from import_export import resources
from import_export.fields import Field
from import_export.widgets import DecimalWidget
from lawsuit.models import Folder, LawSuit, Movement, TypeMovement, CourtDistrict, CourtDivision, Organ, Instance, \
    TypeLawsuit, CourtDistrictComplement, City
from task.instance_loaders import TaskModelInstanceLoader
from task.models import Task, TypeTask
from task.widgets import PersonAskedByWidget, UnaccentForeignKeyWidget, TaskStatusWidget, DateTimeWidgetMixin

TRUE_FALSE_DICT = {'V': True, 'F': False}

COLUMN_NAME_DICT = {
    'system_prefix': {
        'column_name': 'sistema',
        'attribute': 'system_prefix',
        'required': True
    },
    'folder_number': {
        'column_name': 'pasta.numero',
        'attribute': 'folder_number',
        'required': False
    },
    'folder_legacy_code': {
        'column_name': 'pasta.codigo_legado',
        'attribute': 'movement__folder__legacy_code',
        'required': False
    },
    'folder_person_customer': {
        'column_name': 'pasta.cliente',
        'attribute': 'movement__folder__person_customer',
        'required': True
    },
    'folder_cost_center': {
        'column_name': 'pasta.centro_custo',
        'attribute': 'movement__folder__legacy_code',
        'required': False
    },
    'law_suit_number': {
        'column_name': 'processo.numero',
        'attribute': 'movement__law_suit__law_suit_number',
        'required': True
    },
    'type_lawsuit': {
        'column_name': 'processo.tipo',
        'attribute': 'movement__law_suit__type_lawsuit',
        'required': True
    },
    'instance': {
        'column_name': 'processo.instancia',
        'attribute': 'movement__law_suit__instance__name',
        'required': False
    },
    'lawsuit_is_current_instance': {
        'column_name': 'processo.instancia_atual',
        'attribute': 'movement__law_suit__is_current_instance',
        'required': True
    },
    'lawsuit_person_lawyer': {
        'column_name': 'processo.advogado',
        'attribute': 'movement__law_suit__person_lawyer',
        'required': False
    },
    'lawsuit_court_district': {
        'column_name': 'processo.comarca',
        'attribute': 'movement__law_suit__court_district',
        'required': False
    },
    'lawsuit_court_district_complement': {
        'column_name': 'processo.complemento_comarca',
        'attribute': 'movement__law_suit__court_district_complement',
        'required': False
    },
    'lawsuit_city': {
        'column_name': 'processo.cidade',
        'attribute': 'movement__law_suit__city',
        'required': False
    },
    'lawsuit_court_division': {
        'column_name': 'processo.vara',
        'attribute': 'movement__law_suit__court_division',
        'required': False
    },
    'lawsuit_organ': {
        'column_name': 'processo.orgao',
        'attribute': 'movement__law_suit__organ',
        'required': False
    },
    'lawsuit_opposing_party': {
        'column_name': 'processo.parte_adversa',
        'attribute': 'movement__law_suit__opposing_party',
        'required': False
    },
    'lawsuit_legacy_code': {
        'column_name': 'processo.codigo_legado',
        'attribute': 'movement__law_suit__legacy_code',
        'required': False
    },
    'type_movement': {
        'column_name': 'movimentacao.tipo',
        'attribute': 'movement__type_movement__name',
        'required': True
    },
    'movement_legacy_code': {
        'column_name': 'movimentacao.codigo_legado',
        'attribute': 'movement__legacy_code',
        'required': False
    },
    'person_asked_by': {
        'column_name': 'os.solicitante',
        'attribute': 'person_asked_by',
        'required': True
    },
    'type_task': {
        'column_name': 'os.tipo_servico',
        'attribute': 'type_task',
        'required': True
    },
    'final_deadline_date': {
        'column_name': 'os.prazo_fatal',
        'attribute': 'final_deadline_date',
        'required': True
    },
    'performance_place': {
        'column_name': 'os.local_cumprimento',
        'attribute': 'billing_date',
        'required': True
    },
    'description': {
        'column_name': 'os.descricao',
        'attribute': 'description',
        'required': False
    },
    'person_executed_by': {
        'column_name': 'os.correspondente',
        'attribute': 'person_executed_by',
        'required': False
    },
    'person_distributed_by': {
        'column_name': 'os.contratante',
        'attribute': 'person_distributed_by',
        'required': False
    },
    'delegation_date': {
        'column_name': 'os.data_delegacao',
        'attribute': 'delegation_date',
        'required': False
    },
    'execution_date': {
        'column_name': 'os.data_cumprimento',
        'attribute': 'execution_date',
        'required': False
    },
    'requested_date': {
        'column_name': 'os.data_solicitacao',
        'attribute': 'requested_date',
        'required': False
    },
    'acceptance_date': {
        'column_name': 'os.data_aceite',
        'attribute': 'acceptance_date',
        'required': False
    },
    'task_status': {
        'column_name': 'os.status',
        'attribute': 'task_status',
        'required': True
    },
    'amount': {
        'column_name': 'os.valor',
        'attribute': 'amount',
        'required': False
    },
    'is_active': {
        'column_name': 'os.ativa',
        'attribute': 'is_active',
        'required': False
    },
    'acceptance_service_date': {
        'column_name': 'os.data_aceite_service',
        'attribute': 'acceptance_service_date',
        'required': False
    },
    'refused_service_date': {
        'column_name': 'os.data_recusa_service',
        'attribute': 'refused_service_date',
        'required': False
    },
    'refused_date': {
        'column_name': 'os.data_recusa_correspondente',
        'attribute': 'refused_date',
        'required': False
    },
    'return_date': {
        'column_name': 'os.data_retorno',
        'attribute': 'return_date',
        'required': False
    },
    'blocked_payment_date': {
        'column_name': 'os.data_glosa',
        'attribute': 'blocked_payment_date',
        'required': False
    },
    'finished_date': {
        'column_name': 'os.data_finalizacao',
        'attribute': 'finished_date',
        'required': False
    },
    'receipt_date': {
        'column_name': 'os.data_recebimento',
        'attribute': 'receipt_date',
        'required': False
    },
    'billing_date': {
        'column_name': 'os.data_pagamento',
        'attribute': 'billing_date',
        'required': False
    },
    'legacy_code': {
        'column_name': 'os.codigo_legado',
        'attribute': 'legacy_code',
        'required': False
    },
}


def self_or_none(obj):
    return obj if obj else None


class CustomFieldImportExport(Field):
    def clean(self, data):
        """
        Translates the value stored in the imported datasource to an
        appropriate Python object and returns it.
        """
        try:
            value = data[self.column_name]
        except KeyError:
            raise KeyError("Column '%s' not found in dataset. Available "
                           "columns are: %s" % (self.column_name, list(data)))

        try:
            value = self.widget.clean(value, row=data)
        except ValueError as e:
            column_name = COLUMN_NAME_DICT.get(self.column_name,
                                               self.column_name)
            if not column_name == self.column_name:
                column_name = column_name.get('column_name')
            raise ValueError("Coluna '%s': %s" % (column_name, e))

        if value in self.empty_values and self.default != NOT_PROVIDED:
            if callable(self.default):
                return self.default()
            return self.default

        return value


class TaskResource(resources.ModelResource):
    type_task = CustomFieldImportExport(column_name='type_task', attribute='type_task',
                                        widget=UnaccentForeignKeyWidget(TypeTask, 'name'), saves_null_values=False)
    person_asked_by = CustomFieldImportExport(column_name='person_asked_by', attribute='person_asked_by',
                                              widget=PersonAskedByWidget(Person, 'legal_name'), saves_null_values=False)
    person_executed_by = CustomFieldImportExport(column_name='person_executed_by', attribute='person_executed_by',
                                                 widget=UnaccentForeignKeyWidget(Person, 'legal_name'))
    person_distributed_by = CustomFieldImportExport(column_name='person_distributed_by',
                                                    attribute='person_distributed_by',
                                                    widget=UnaccentForeignKeyWidget(Person, 'legal_name'))
    final_deadline_date = CustomFieldImportExport(column_name='final_deadline_date', attribute='final_deadline_date',
                                                  widget=DateTimeWidgetMixin(), saves_null_values=False)
    delegation_date = CustomFieldImportExport(column_name='delegation_date', attribute='delegation_date',
                                              widget=DateTimeWidgetMixin())
    acceptance_date = CustomFieldImportExport(column_name='acceptance_date', attribute='acceptance_date',
                                              widget=DateTimeWidgetMixin())
    execution_date = CustomFieldImportExport(column_name='execution_date', attribute='execution_date',
                                             widget=DateTimeWidgetMixin())
    requested_date = CustomFieldImportExport(column_name='requested_date', attribute='requested_date',
                                             widget=DateTimeWidgetMixin(), default=timezone.now())
    acceptance_service_date = CustomFieldImportExport(column_name='acceptance_service_date',
                                                      attribute='acceptance_service_date', widget=DateTimeWidgetMixin())
    refused_service_date = CustomFieldImportExport(column_name='refused_service_date', attribute='refused_service_date',
                                                   widget=DateTimeWidgetMixin())
    refused_date = CustomFieldImportExport(column_name='refused_date', attribute='refused_date',
                                           widget=DateTimeWidgetMixin())
    return_date = CustomFieldImportExport(column_name='return_date', attribute='return_date',
                                          widget=DateTimeWidgetMixin())
    blocked_payment_date = CustomFieldImportExport(column_name='blocked_payment_date', attribute='blocked_payment_date',
                                                   widget=DateTimeWidgetMixin())
    finished_date = CustomFieldImportExport(column_name='finished_date', attribute='finished_date',
                                            widget=DateTimeWidgetMixin())
    receipt_date = CustomFieldImportExport(column_name='receipt_date', attribute='receipt_date',
                                           widget=DateTimeWidgetMixin())
    billing_date = CustomFieldImportExport(column_name='billing_date', attribute='billing_date',
                                           widget=DateTimeWidgetMixin())
    task_status = CustomFieldImportExport(column_name='task_status', attribute='task_status', widget=TaskStatusWidget())
    amount = CustomFieldImportExport(column_name='amount', attribute='amount', widget=DecimalWidget(),
                                     default=Decimal('0.00'))
    performance_place = CustomFieldImportExport(column_name='performance_place', attribute='performance_place',
                                                saves_null_values=False)

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
        person_customer = Person.objects.filter(
            legal_name__unaccent__icontains=row['folder_person_customer'],
            is_customer=True).first()
        folder = None
        if not person_customer:
            row_errors.append(
                "É obrigatório o preenchimento do cliente ({});".format(
                    COLUMN_NAME_DICT['folder_person_customer']['column_name']))
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
                                  'folder_number': folder_number})
                if not folder and folder_number:
                    folder, created = Folder.objects.get_or_create(
                        folder_number=folder_number,
                        person_customer=person_customer,
                        office=self.office,
                        defaults={'create_user': self.create_user,
                                  'legacy_code': folder_legacy_code})
                if not folder:
                    row_errors.append(
                        'Não foi encontrado registro de pasta correspondente aos valores informados;'
                    )
        return folder

    def validate_lawsuit(self, row, row_errors):
        lawsuit_number = row['law_suit_number']
        lawsuit_legacy_code = row['lawsuit_legacy_code']
        lawsuit = None
        type_lawsuit = row['type_lawsuit']
        instance = row['instance']
        if instance:
            instance = Instance.objects.filter(name=instance, office=self.office).first()
        if not lawsuit_number or not type_lawsuit:
            row_errors.append(
                "É obrigatório o preenchimento dos campos de identificação do processo "
                "({} e {});".format(
                    COLUMN_NAME_DICT['law_suit_number']['column_name'],
                    COLUMN_NAME_DICT['type_lawsuit']['column_name']))
        else:
            if lawsuit_legacy_code:
                lawsuit = LawSuit.objects.filter(
                    legacy_code=lawsuit_legacy_code,
                    folder=self.folder,
                    instance=self_or_none(instance),
                    office_id=self.office_id).first()
            if not lawsuit and lawsuit_number:
                lawsuit = LawSuit.objects.filter(
                    law_suit_number=lawsuit_number,
                    folder=self.folder,
                    instance=self_or_none(instance),
                    office_id=self.office_id).first()
            if not lawsuit:
                is_current_instance = TRUE_FALSE_DICT.get(
                    row['lawsuit_is_current_instance'], False)
                person_lawyer = row.get('lawsuit_person_lawyer', '')
                if person_lawyer:
                    person_lawyer = Person.objects.filter(legal_name__unaccent__icontains=person_lawyer,
                                                          is_lawyer=True,
                                                          offices=self.office).first()
                court_district = row.get('lawsuit_court_district', '')
                if court_district:
                    court_district = CourtDistrict.objects.filter(name=court_district).first()
                court_district_complement = row.get('lawsuit_court_district_complement', '')
                if court_district_complement:
                    court_district_complement = CourtDistrictComplement.objects.filter(
                        name=court_district_complement).first()
                city = row.get('lawsuit_city', '')
                if city:
                    city = City.objects.filter(name=city).first()
                court_division = row.get('lawsuit_court_division', '')
                if court_division:
                    court_division = CourtDivision.objects.filter(name=court_division,
                                                                  office=self.office).first()
                organ = row.get('lawsuit_organ', '')
                if organ:
                    organ = Organ.objects.filter(legal_name=organ,
                                                 offices=self.office).first()
                opposing_party = row.get('opposing_party', '')
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
                                                 office=self.office)
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
                row_errors.append(
                    'Não foi encontrado registro de movimentação com os valores informados;'
                )
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
        import pdb;pdb.set_trace()
        self.lawsuit = self.validate_lawsuit(row, row_errors) if self.folder else None
        self.movement = self.validate_movement(row, row_errors) if self.lawsuit else None

        if self.movement:
            row['movement'] = self.movement.id
        if row_errors:
            raise Exception(row_errors)
        import pdb;pdb.set_trace()
        row['is_active'] = TRUE_FALSE_DICT.get('is_active', True)
