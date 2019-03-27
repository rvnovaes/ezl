from django.db.models import Q
from core.models import Person, State, City
from financial.models import CostCenter
from lawsuit.models import Folder, LawSuit, CourtDistrict, Instance, CourtDistrictComplement, CourtDivision, Organ, \
    TypeLawsuit, TypeMovement
from task.utils import get_default_customer, self_or_none, validate_final_deadline_date
from task.messages import column_error, incorrect_natural_key, required_one_in_group, record_not_found, \
    required_column, required_column_related, default_customer_missing, min_hour_error
from task.models import Task, Movement, TypeTask
from manager.utils import get_template_value_value
from manager.enums import TemplateKeys
from task.widgets import DateTimeWidgetMixin

TRUE_FALSE_DICT = {'V': True, 'F': False}

COLUMN_NAME_DICT = {
    'system_prefix': {
        'column_name': 'sistema',
        'attribute': 'system_prefix',
        'required': False,
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
        'required': False,
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
        'required': False,
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
    'lawsuit_state': {
        'column_name': 'processo.uf',
        'attribute': 'movement__law_suit__state',
        'required': True,
        'verbose_name': CourtDistrict._meta.get_field('state').verbose_name,
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
    'task_number': {
        'column_name': 'os.numero',
        'attribute': 'task_number',
        'required': False,
        'verbose_name': Task._meta.get_field('task_number').verbose_name,
    },
    'person_asked_by': {
        'column_name': 'os.solicitante',
        'attribute': 'person_asked_by',
        'required': True,
        'verbose_name': Task._meta.get_field('person_asked_by').verbose_name,
    },
    'person_company_representative': {
        'column_name': 'os.preposto',
        'attribute': 'person_company_representative',
        'required': False,
        'verbose_name': Task._meta.get_field('person_company_representative').verbose_name,
    },
    'type_task': {
        'column_name': 'os.tipo_servico',
        'attribute': 'type_task',
        'required': True,
        'verbose_name': Task._meta.get_field('type_task').verbose_name,
    },
    'task_status': {
        'column_name': 'os.status',
        'attribute': 'task_status',
        'required': False,
        'verbose_name': Task._meta.get_field('task_status').verbose_name,
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
        'required': False,
        'verbose_name': Task._meta.get_field('performance_place').verbose_name,
    },
    'description': {
        'column_name': 'os.descricao',
        'attribute': 'description',
        'required': False,
        'verbose_name': Task._meta.get_field('description').verbose_name,
    },
    'legacy_code': {
        'column_name': 'os.codigo_legado',
        'attribute': 'legacy_code',
        'required': False,
        'verbose_name': Task._meta.get_field('legacy_code').verbose_name,
    },
}


class ImportTask(object):

    def __init__(self, row, row_errors, office, create_user):
        self.row = row
        self.row_errors = row_errors or []
        self.create_user = create_user
        self.office = office
        self._office_id = self.office.id
        self._create_args = {}
        self.model = Task

    @staticmethod
    def _filter_queryset(qs, **kwargs):
        return qs.filter(**kwargs)

    def _set_create_args(self, create_args):
        self._create_args = create_args or {}

    def validate_person_asked_by(self, value):
        if not value:
            return True
        else:
            qs = Person.objects.all()
            filter_args = {'legal_name__unaccent__iexact': str(value),
                           'officemembership__office': self.office}
            return True if self._filter_queryset(qs, **filter_args).first() else False

    def validate_person_company_representative(self, value):
        if not value:
            return True
        else:
            qs = Person.objects.all()
            filter_args = {'legal_name__unaccent__iexact': str(value),
                           'officemembership__office': self.office}
            return True if self._filter_queryset(qs, **filter_args).first() else False

    def validate_type_task(self, value):
        if not value:
            return True
        else:
            qs = TypeTask.objects.get_queryset(office=[self._office_id])
            return True if self._filter_queryset(qs, **{'name__unaccent__iexact': str(value)}).first() else False

    def validate_final_deadline_date(self, value):
        date_value = DateTimeWidgetMixin().clean(value)
        return validate_final_deadline_date(date_value, self.office)

    def get_errors(self):
        return self.row_errors

    def _get_formated_error(self, field, value):
        try:
            column_type = self.model._meta.get_field(field).get_internal_type()
        except:
            column_type = 'ForeignKey'

        error_dict = {
            'ForeignKey': incorrect_natural_key(COLUMN_NAME_DICT[field]['verbose_name'],
                                                COLUMN_NAME_DICT[field]['column_name'], value),
            'DateTimeField': min_hour_error(get_template_value_value(self.office, TemplateKeys.MIN_HOUR_OS.name))
        }

        return column_error(COLUMN_NAME_DICT[field]['column_name'], error_dict.get(column_type))

    def validate_task(self):
        """
        Checa se os campos de preenchimento obrigatórios foram preenchidos e se os dados preenchidos são validos
        :return (boolean): True or False
        """

        row = self.row
        row_errors = self.row_errors
        required_fields = ['person_asked_by', 'type_task', 'final_deadline_date']
        check_fields = ['person_asked_by', 'person_company_representative', 'type_task', 'final_deadline_date']

        for field in required_fields:
            if not row.get(field):
                row_errors.append(required_column(COLUMN_NAME_DICT[field]['column_name']))

        for field in check_fields:
            validation_method = getattr(self, 'validate_{}'.format(field))
            value = row.get(field)
            if validation_method and not validation_method(value):
                row_errors.append(self._get_formated_error(field, value))
        return row_errors == []


class ImportFolder(ImportTask):

    def __init__(self, row, row_errors, office, create_user):
        super().__init__(row, row_errors, office, create_user)
        self._cost_center = None
        self._cost_center_update = False
        self.folder = None
        self.model = Folder

    def _get_person_customer(self, row):
        if not row.get('folder_person_customer'):
            return get_default_customer(self.office)
        else:
            return Person.objects.filter(legal_name__unaccent__iexact=str(row.get('folder_person_customer')),
                                         officemembership__office=self.office,
                                         is_customer=True).first()

    def _filter_folder(self, **kwargs):
        folder = Folder.objects.get_queryset(office=[self._office_id]).filter(**kwargs).first()
        self._set_folder(folder)
        return folder

    def _set_folder(self, folder):
        self.folder = folder

    def _get_create_folder(self, defaults, **kwargs):
        folder = Folder.objects.filter(**kwargs).first()
        if not folder:
            folder, created = Folder.objects.get_or_create(defaults=defaults,
                                                           **kwargs)
        self._set_folder(folder)
        return folder

    def _get_cost_center(self, **kwargs):
        return CostCenter.objects.get_queryset(office=[self._office_id]).filter(**kwargs).first()

    def _set_cost_center(self, cost_center):
        self._cost_center = cost_center

    @staticmethod
    def _update_cost_center(folder, cost_center, update_cost_center):
        if getattr(folder, 'cost_center') and update_cost_center:
            folder.cost_center = cost_center
            folder.save()

    def validate_folder(self):
        """
        Faz a validacao do grupo de colunas referente ao folder
        :return: True or False
        """
        row = self.row
        row_errors = self.row_errors
        folder_number = int(row.get('folder_number')) if row.get('folder_number', '') else None
        folder_legacy_code = row.get('folder_legacy_code', '')
        cost_center = row.get('folder_cost_center', '')
        system_prefix = row.get('system_prefix')
        if cost_center:
            cost_center = self._get_cost_center(**{'name__unaccent__iexact': cost_center})
            if not cost_center:
                key = 'folder_cost_center'
                row_errors.append(incorrect_natural_key(COLUMN_NAME_DICT[key]['verbose_name'],
                                                        COLUMN_NAME_DICT[key]['column_name'],
                                                        row.get(key, '')))
            else:
                self._set_cost_center(cost_center)
                if isinstance(cost_center, CostCenter):
                    self._cost_center_update = True
        folder = None
        folder_args = {}
        person_customer = self._get_person_customer(row)

        if not (folder_legacy_code and folder_number) and person_customer:
            folder_args = {'person_customer': person_customer,
                           'is_default': True,
                           'office': self.office}
        else:
            if folder_legacy_code:
                filter_args = {'legacy_code': folder_legacy_code,
                               'system_prefix': system_prefix}
                folder = self._filter_folder(**filter_args)
            if not folder and folder_number:
                filter_args = {'folder_number': folder_number}
                folder = self._filter_folder(**filter_args)
            if not folder and person_customer:
                folder_args = {'person_customer': person_customer,
                               'office': self.office,
                               'legacy_code': folder_legacy_code,
                               'folder_number': folder_number,
                               'system_prefix': system_prefix}
        if row.get('folder_person_customer') and not person_customer:
            row_errors.append(record_not_found(
                COLUMN_NAME_DICT['folder_person_customer']['verbose_name']))
        elif not row.get('folder_person_customer') and not person_customer:
            row_errors.append(default_customer_missing(self.office.legal_name))

        if not folder and folder_args:
            self._set_create_args(folder_args)

        return row_errors == []

    def get_folder(self):
        valid = self.validate_folder()
        if valid:
            try:
                if not self.folder:
                    data = {'create_user': self.create_user}
                    if self._cost_center_update and self._cost_center:
                        data['cost_center'] = self._cost_center
                    if self._create_args:
                        folder = self._get_create_folder(defaults=data, **self._create_args)
                elif self._cost_center_update and self._cost_center:
                    self._update_cost_center(self.folder, self._cost_center, self._cost_center_update)
            except Exception:
                self.row_errors.append(record_not_found(Folder._meta.verbose_name))

        if not self.folder:
            self.row_errors.append(record_not_found(Folder._meta.verbose_name))

        return self.folder, self.row_errors


class ImportLawSuit(ImportTask):

    def __init__(self, row, row_errors, office, create_user, folder):
        super().__init__(row, row_errors, office, create_user)
        self.folder = folder
        self.lawsuit = None
        self.update_lawsuit = False
        self.model = LawSuit

    def _set_lawsuit(self, lawsuit):
        self.lawsuit = lawsuit

    def _filter_lawsuit(self, **kwargs):
        qs = LawSuit.objects.get_queryset(office=[self._office_id])
        lawsuit = self._filter_queryset(qs, **kwargs).first()
        self._set_lawsuit(lawsuit)
        return lawsuit

    def _create_lawsuit(self, **kwargs):
        lawsuit = LawSuit.objects.create(**kwargs)
        self._set_lawsuit(lawsuit)
        return lawsuit

    def _update_lawsuit(self, **kwargs):
        lawsuit = self.lawsuit
        for key, value in kwargs.items():
            if hasattr(lawsuit, key) and value:
                setattr(lawsuit, key, value)
        lawsuit.save()
        self._set_lawsuit(lawsuit)
        return lawsuit

    def _get_instance(self, **kwargs):
        return Instance.objects.get_queryset(office=[self._office_id]).filter(**kwargs).first()

    def _get_person(self, **kwargs):
        qs = Person.objects.all()
        return self._filter_queryset(qs, **kwargs).first()

    @staticmethod
    def _get_state(state):
        return State.objects.filter(Q(name__unaccent__iexact=state) |
                                    Q(initials__unaccent__iexact=state)).first()

    def _get_court_district(self, **kwargs):
        qs = CourtDistrict.objects.all()
        return self._filter_queryset(qs, **kwargs).first()

    def _get_court_district_complement(self, **kwargs):
        qs = CourtDistrictComplement.objects.get_queryset(office=[self._office_id])
        return self._filter_queryset(qs, **kwargs).first()

    def _get_city(self, **kwargs):
        qs = City.objects.all()
        return self._filter_queryset(qs, **kwargs).first()

    def _get_court_division(self, **kwargs):
        qs = CourtDivision.objects.get_queryset(office=[self._office_id])
        return self._filter_queryset(qs, **kwargs).first()

    def _get_organ(self, **kwargs):
        qs = Organ.objects.get_queryset(office=[self._office_id])
        return self._filter_queryset(qs, **kwargs).first()

    def validate_lawsuit(self):
        """
        Faz a validacao do grupo de colunas referente ao lawsuit
        :return (boolean): True or False
        """
        row = self.row
        row_errors = self.row_errors
        lawsuit_number = row.get('law_suit_number', '')
        lawsuit_number = str(int(lawsuit_number)) if isinstance(lawsuit_number, float) else str(lawsuit_number)
        lawsuit_legacy_code = row.get('lawsuit_legacy_code', '')
        state = row.get('lawsuit_state', '')
        court_district = row.get('lawsuit_court_district', '')
        city = row.get('lawsuit_city', '')
        lawsuit = None
        type_lawsuit = row.get('type_lawsuit') or TypeLawsuit.JUDICIAL.value
        system_prefix = row.get('system_prefix')

        if not lawsuit_legacy_code and not lawsuit_number:
            row_errors.append(required_one_in_group('identificação do processo',
                                                    [COLUMN_NAME_DICT['law_suit_number']['column_name'],
                                                     COLUMN_NAME_DICT['lawsuit_legacy_code']['column_name']]))
        if not state:
            row_errors.append(required_column(COLUMN_NAME_DICT['lawsuit_state']['column_name']))
        if not (court_district or city):
            row_errors.append(required_one_in_group('local de execução',
                                                    [COLUMN_NAME_DICT['lawsuit_court_district']['column_name'],
                                                     COLUMN_NAME_DICT['lawsuit_city']['column_name']]))
        if not row_errors:
            if lawsuit_legacy_code:
                filter_args = {'legacy_code': lawsuit_legacy_code,
                               'system_prefix': system_prefix,
                               'folder': self.folder}
                lawsuit = self._filter_lawsuit(**filter_args)

            if not lawsuit and lawsuit_number:
                filter_args = {'law_suit_number': lawsuit_number,
                               'folder': self.folder}
                lawsuit = self._filter_lawsuit(**filter_args)

            instance = None
            if row.get('instance'):
                instance = self._get_instance(**{'name__unaccent__iexact': row.get('instance')})
                if not instance:
                    key = 'instance'
                    row.get('warnings', []).append(incorrect_natural_key(COLUMN_NAME_DICT[key]['verbose_name'],
                                                                         COLUMN_NAME_DICT[key]['column_name'],
                                                                         row.get(key, '')))
            is_current_instance = TRUE_FALSE_DICT.get(row.get('lawsuit_is_current_instance'), False)
            person_lawyer = row.get('lawsuit_person_lawyer', '')

            # Validacao de person_lawyer
            if person_lawyer:
                filter_args = {'legal_name__unaccent__iexact': person_lawyer,
                               'is_lawyer': True,
                               'offices': self.office}
                person_lawyer = self._get_person(**filter_args)
                if not person_lawyer:
                    key = 'lawsuit_person_lawyer'
                    row.get('warnings', []).append(incorrect_natural_key(COLUMN_NAME_DICT[key]['verbose_name'],
                                                                         COLUMN_NAME_DICT[key]['column_name'],
                                                                         row.get(key, '')))

            # Validacao de state
            if state:
                state = self._get_state(state)
                if not state:
                    key = 'lawsuit_state'
                    row_errors.append(incorrect_natural_key(COLUMN_NAME_DICT[key]['verbose_name'],
                                                            COLUMN_NAME_DICT[key]['column_name'],
                                                            row.get(key, '')))

            # Validacao de court_district
            if court_district:
                if not state:
                    row_errors.append(required_column_related(
                        COLUMN_NAME_DICT['lawsuit_state']['column_name'],
                        COLUMN_NAME_DICT['lawsuit_court_district']['column_name']))
                else:
                    filter_args = {'name__unaccent__iexact': court_district,
                                   'state': state}
                    court_district = self._get_court_district(**filter_args)
                    if not court_district:
                        key = 'lawsuit_court_district'
                        row.get('warnings', []).append(incorrect_natural_key(COLUMN_NAME_DICT[key]['verbose_name'],
                                                                             COLUMN_NAME_DICT[key]['column_name'],
                                                                             row.get(key, '')))

            # Validacao de court_district_complement
            court_district_complement = row.get('lawsuit_court_district_complement', '')
            if court_district_complement:
                if not court_district:
                    row_errors.append(required_column_related(
                        COLUMN_NAME_DICT['lawsuit_court_district']['column_name'],
                        COLUMN_NAME_DICT['lawsuit_court_district_complement']['column_name']))
                else:
                    filter_args = {'court_district': court_district,
                                   'name__unaccent__iexact': court_district_complement}
                    court_district_complement = self._get_court_district_complement(**filter_args)
                    if not court_district_complement:
                        key = 'lawsuit_court_district_complement'
                        row.get('warnings', []).append(incorrect_natural_key(COLUMN_NAME_DICT[key]['verbose_name'],
                                                                             COLUMN_NAME_DICT[key]['column_name'],
                                                                             row.get(key, '')))

            # Validacao de city
            if city:
                if not state:
                    row_errors.append(required_column_related(COLUMN_NAME_DICT['lawsuit_state']['column_name'],
                                                              COLUMN_NAME_DICT['lawsuit_city']['column_name']))
                else:
                    filter_args = {'name__unaccent__iexact': city,
                                   'state': state}
                    city = self._get_city(**filter_args)
                    if not city:
                        key = 'lawsuit_city'
                        row.get('warnings', []).append(incorrect_natural_key(COLUMN_NAME_DICT[key]['verbose_name'],
                                                                             COLUMN_NAME_DICT[key]['column_name'],
                                                                             row.get(key, '')))

            # Validacao de court_division
            court_division = row.get('lawsuit_court_division', '')
            if court_division:
                court_division = self._get_court_division(**{'name__unaccent__iexact': court_division}).first()
                if not court_division:
                    key = 'lawsuit_court_division'
                    row.get('warnings', []).append(incorrect_natural_key(COLUMN_NAME_DICT[key]['verbose_name'],
                                                                         COLUMN_NAME_DICT[key]['column_name'],
                                                                         row.get(key, '')))

            # Validacao de organ
            organ = row.get('lawsuit_organ', '')
            if organ:
                organ = self._get_organ(**{'legal_name__unaccent__iexact': organ})
                if not organ:
                    key = 'folder_cost_center'
                    row.get('warnings', []).append(incorrect_natural_key(COLUMN_NAME_DICT[key]['verbose_name'],
                                                                         COLUMN_NAME_DICT[key]['column_name'],
                                                                         row.get(key, '')))

            opposing_party = row.get('lawsuit_opposing_party', '')

            if not (city or court_district):
                required_one_in_group('local de execução',
                                      [COLUMN_NAME_DICT['lawsuit_court_district']['column_name'],
                                       COLUMN_NAME_DICT['lawsuit_city']['column_name']])
            if not row_errors:
                if not lawsuit:
                    create_args = {
                        'type_lawsuit': TypeLawsuit(type_lawsuit).name,
                        'person_lawyer': self_or_none(person_lawyer),
                        'folder': self.folder,
                        'instance': self_or_none(instance),
                        'court_district': self_or_none(court_district),
                        'court_district_complement': self_or_none(court_district_complement),
                        'city': self_or_none(city),
                        'organ': self_or_none(organ),
                        'court_division': self_or_none(court_division),
                        'law_suit_number': lawsuit_number,
                        'is_current_instance': is_current_instance,
                        'opposing_party': self_or_none(opposing_party),
                        'create_user': self.create_user,
                        'office': self.office,
                        'legacy_code': lawsuit_legacy_code,
                        'system_prefix': system_prefix
                    }

                    self._set_create_args(create_args)

                else:
                    self.update_lawsuit = True
                    create_args = {
                        'instance': self_or_none(instance),
                        'person_lawyer': self_or_none(person_lawyer),
                        'court_district': self_or_none(court_district),
                        'court_district_complement': self_or_none(court_district_complement),
                        'city': self_or_none(city),
                        'court_division': self_or_none(court_division),
                        'organ': self_or_none(organ),
                        'oposing_party': opposing_party,
                        'is_current_instance': is_current_instance
                    }
                    self._set_create_args(create_args)

        return self.row_errors == []

    def get_lawsuit(self):
        valid = self.validate_lawsuit()
        if valid:
            try:
                if not self.lawsuit and self._create_args:
                    lawsuit = self._create_lawsuit(**self._create_args)
                elif self.lawsuit and self._create_args:
                    lawsuit = self._update_lawsuit(**self._create_args)
            except Exception:
                self.row_errors.append(record_not_found(LawSuit._meta.verbose_name))
            if not self.lawsuit:
                self.row_errors.append(record_not_found(LawSuit._meta.verbose_name))

        return self.lawsuit, self.row_errors


class ImportMovement(ImportTask):

    def __init__(self, row, row_errors, office, create_user, lawsuit):
        super().__init__(row, row_errors, office, create_user)
        self.default_type_movement = self._get_default_type_movement()
        self.lawsuit = lawsuit
        self.folder = getattr(lawsuit, 'folder', None)
        self.movement = None
        self.update_movement = False
        self.model = Movement

    def _set_movement(self, movement):
        self.movement = movement

    def _filter_movement(self, **kwargs):
        qs = Movement.objects.get_queryset(office=[self._office_id])
        movement = self._filter_queryset(qs, **kwargs).first()
        self._set_movement(movement)
        return movement

    def _get_create_movement(self, defaults, **kwargs):
        movement, created = Movement.objects.get_or_create(defaults=defaults,
                                                           **kwargs)
        self._set_movement(movement)
        return movement

    def _get_type_movement(self, **kwargs):
        qs = TypeMovement.objects.get_queryset(office=[self._office_id])
        return self._filter_queryset(qs, **kwargs).first()

    def _get_default_type_movement(self):
        type_movement, created = TypeMovement.objects.get_or_create(
            is_default=True,
            office=self.office,
            defaults={
                'name': 'OS Avulsa',
                'create_user': self.create_user
            })
        return type_movement

    def validate_movement(self):
        """
        Faz a validacao do grupo de colunas referente ao movement
        :return (boolean): True or False
        """
        row = self.row
        row_errors = self.row_errors
        type_movement_name = row.get('type_movement', '')
        movement_legacy_code = row.get('movement_legacy_code', '')
        system_prefix = row.get('system_prefix', '')
        if type(movement_legacy_code) == float and movement_legacy_code.is_integer():
            movement_legacy_code = str(int(movement_legacy_code))
        if not (type_movement_name or movement_legacy_code):
            create_args = {
                'folder': self.folder,
                'law_suit': self.lawsuit,
                'type_movement': self.default_type_movement,
                'office': self.office
            }
            self._set_create_args(create_args)
        else:
            type_movement = self._get_type_movement(**{'name__unaccent__iexact': type_movement_name})
            movement = None
            if movement_legacy_code:
                filter_args = {'legacy_code': movement_legacy_code,
                               'system_prefix': system_prefix,
                               'folder': self.folder,
                               'law_suit': self.lawsuit}
                movement = self._filter_movement(**filter_args)

            if not movement and type_movement:
                create_args = {
                    'folder': self.folder,
                    'law_suit': self.lawsuit,
                    'office': self.office,
                    'type_movement': type_movement,
                    'legacy_code': movement_legacy_code,
                }
                self._set_create_args(create_args)

            elif not movement and not type_movement:
                key = 'type_movement'
                row_errors.append(incorrect_natural_key(COLUMN_NAME_DICT[key]['verbose_name'],
                                                        COLUMN_NAME_DICT[key]['column_name'],
                                                        row.get(key, '')))

        return self.row_errors == []

    def get_movement(self):
        valid = self.validate_movement()
        if valid:
            try:
                if not self.movement and self._create_args:
                    defaults = {'create_user': self.create_user,
                                'system_prefix': self.row.get('system_prefix', '')}
                    movement = self._get_create_movement(defaults, **self._create_args)
            except Exception:
                self.row_errors.append(record_not_found(Movement._meta.verbose_name))

        return self.movement, self.row_errors
