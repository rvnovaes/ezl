from core.models import Person
from financial.models import CostCenter
from lawsuit.models import Folder, LawSuit, CourtDistrict
from task.utils import get_default_customer, self_or_none
from task.messages import *
from task.models import Task, Movement

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


class ImportFolder(object):

    def __init__(self, row, row_errors, office, create_user):
        self.row = row,
        self.row_errors = row_errors or [],
        self.create_user = create_user
        self.office = office
        self._office_id = self.office.id
        self._cost_center = None
        self._cost_center_update = False
        self.folder = None
        self._filter_args = {}

    def _get_person_customer(self, row):
        if not row.get('folder_person_customer'):
            return get_default_customer(self.office)
        else:
            return Person.objects.filter(legal_name__unaccent__iexact=str(row.get('folder_person_customer')),
                                         officemembership__office=self.office,
                                         s_customer=True).first()

    def _filter_folder(self, **kwargs):
        folder = Folder.objects.get_queryset(office=[self._office_id]).filter(**kwargs).first()
        self._set_folder(folder)
        return folder

    def _set_folder(self, folder):
        self.folder = folder

    def _get_create_folder(self, defaults, **kwargs):
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

    def _set_filter_args(self, filter_args={}):
        self._filter_args = filter_args

    def validate_folder(self):
        """
        Faz a validacao do grupo de colunas referente ao folder
        :return: True or False
        """
        row = self.row
        folder_errors = []
        folder_number = int(row.get('folder_number')) if self_or_none(row.get('folder_number', '')) else None
        folder_legacy_code = row.get('folder_legacy_code', '')
        cost_center = row.get('folder_cost_center', '')
        system_prefix = row.get('system_prefix')
        if cost_center:
            cost_center = self._get_cost_center(**{'name__unaccent__iexact': cost_center})
            if not cost_center:
                key = 'folder_cost_center'
                folder_errors.append(insert_incorrect_natural_key_message(COLUMN_NAME_DICT[key]['verbose_name'],
                                                                          COLUMN_NAME_DICT[key]['column_name'],
                                                                          row[key]))
            else:
                self._set_cost_center(cost_center)
                if isinstance(cost_center, CostCenter):
                    self._cost_center_update = True
        folder = None
        filter_args = {}
        person_customer = self._get_person_customer(row)

        if not (folder_legacy_code or folder_number) and person_customer:
            filter_args = {'person_customer': person_customer,
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
                filter_args = {'person_customer': person_customer,
                               'office': self.office,
                               'legacy_code': folder_legacy_code,
                               'folder_number': folder_number,
                               'system_prefix': system_prefix}
        if row.get('folder_person_customer') and not person_customer:
            folder_errors.append(RECORD_NOT_FOUND.format(
                COLUMN_NAME_DICT['folder_person_customer']['verbose_name']))

        if not folder and filter_args:
            self._set_filter_args(filter_args)

        self.row_errors.append(folder_errors)

        return folder_errors == []

    def get_folder(self):
        valid = self.validate_folder()
        if valid:
            try:
                if not self.folder:
                    data = {'create_user': self.create_user}
                    if self._cost_center_update and self._cost_center:
                        data['cost_center'] = self._cost_center
                    folder = self._get_create_folder(defaults=data, **self._filter_args)
                elif self._cost_center_update and self._cost_center:
                    self._update_cost_center(self.folder, self._cost_center, self._cost_center_update)
            except Exception:
                self.row_errors.append(RECORD_NOT_FOUND.format(Folder._meta.verbose_name))

        return self.folder, self.row_errors


class ImportLawSuit(object):

    def __init__(self, row, row_errors, office, create_user, folder):
        self.row = row,
        self.row_errors = row_errors or [],
        self.create_user = create_user
        self.office = office
        self._office_id = self.office.id
        self.folder = folder
        self.lawsuit = None

    def validate_lawsuit(self):
        """
        Faz a validacao do grupo de colunas referente ao lawsuit
        :param row: dict com os dados da linha que está sendo processada no momento
        :param row_errors: lista de erros do processo de importação. Lista cumulativa dos processos de validação de
        folder, lawsuit e movement
        :return: Lawsuit instance or None
        """
        row = self.row
        row_errors = self.row_errors
        lawsuit_number = str(row.get('law_suit_number', ''))
        lawsuit_legacy_code = row.get('lawsuit_legacy_code', '')
        state = row.get('lawsuit_state', '')
        court_district = row.get('lawsuit_court_district', '')
        city = row.get('lawsuit_city', '')
        lawsuit = None
        type_lawsuit = row.get('type_lawsuit', 'Judicial')
        system_prefix = row.get('system_prefix')
        if not lawsuit_legacy_code and not lawsuit_number:
            row_errors.append(REQUIRED_ONE_IN_GROUP.format('identificação do processo',
                                                           [COLUMN_NAME_DICT['law_suit_number']['column_name'],
                                                            COLUMN_NAME_DICT['lawsuit_legacy_code']['column_name']]))
        if not state:
            row_errors.append(REQUIRED_COLUMN.format(COLUMN_NAME_DICT['lawsuit_state']['column_name']))
        if not (court_district or city):
            row_errors.append(REQUIRED_ONE_IN_GROUP.format('local de execução',
                                                           [COLUMN_NAME_DICT['lawsuit_court_district']['column_name'],
                                                            COLUMN_NAME_DICT['lawsuit_city']['column_name']]))
        if not row_errors:
            if lawsuit_legacy_code:
                lawsuit = LawSuit.objects.filter(
                    legacy_code=lawsuit_legacy_code,
                    system_prefix=system_prefix,
                    folder=self.folder,
                    office_id=self.office_id).first()
            if not lawsuit and lawsuit_number:
                lawsuit = LawSuit.objects.filter(
                    law_suit_number=lawsuit_number,
                    folder=self.folder,
                    office_id=self.office_id).first()
            instance = None
            if row.get('instance'):
                instance = Instance.objects.filter(name__unaccent__iexact=row.get('instance'),
                                                   office=self.office).first()
                if not instance:
                    row.get('warnings', []).append([insert_incorrect_natural_key_message(row, 'instance')])
            is_current_instance = TRUE_FALSE_DICT.get(row.get('lawsuit_is_current_instance'), False)
            person_lawyer = row.get('lawsuit_person_lawyer', '')

            # Validacao de person_lawyer
            if person_lawyer:
                person_lawyer = Person.objects.filter(legal_name__unaccent__iexact=person_lawyer,
                                                      is_lawyer=True,
                                                      offices=self.office).first()
                if not person_lawyer:
                    row.get('warnings', []).append([insert_incorrect_natural_key_message(row, 'lawsuit_person_lawyer')])

            # Validacao de state
            if state:
                state = State.objects.filter(Q(name__unaccent__iexact=state) |
                                             Q(initials__unaccent__iexact=state)).first()
                if not state:
                    row_errors.append([insert_incorrect_natural_key_message(row, 'lawsuit_person_lawyer')])

            # Validacao de court_district
            if court_district:
                if not state:
                    row_errors.append(REQUIRED_COLUMN_RELATED.format(
                        COLUMN_NAME_DICT['lawsuit_state']['column_name'],
                        COLUMN_NAME_DICT['lawsuit_court_district']['column_name']))
                else:
                    court_district = CourtDistrict.objects.filter(name__unaccent__iexact=court_district,
                                                                  state=state).first()
                    if not court_district:
                        row.get('warnings', []).append([insert_incorrect_natural_key_message(row, 'lawsuit_court_district')])

            # Validacao de court_district_complement
            court_district_complement = row.get('lawsuit_court_district_complement', '')
            if court_district_complement:
                if not court_district:
                    row_errors.append(REQUIRED_COLUMN_RELATED.format(
                        COLUMN_NAME_DICT['lawsuit_court_district']['column_name'],
                        COLUMN_NAME_DICT['lawsuit_court_district_complement']['column_name']))
                else:
                    court_district_complement = CourtDistrictComplement.objects.filter(
                        court_district=court_district,
                        name__unaccent__iexact=court_district_complement,
                        office=self.office).first()
                    if not court_district_complement:
                        row.get('warnings', []).append([insert_incorrect_natural_key_message(
                            row, 'lawsuit_court_district_complement')])

            # Validacao de city
            if city:
                if not state:
                    row_errors.append(REQUIRED_COLUMN_RELATED.format(
                        COLUMN_NAME_DICT['lawsuit_state']['column_name'],
                        COLUMN_NAME_DICT['lawsuit_city']['column_name']))
                else:
                    city = City.objects.filter(name__unaccent__iexact=city,
                                               state=state).first()
                    if not city:
                        row.get('warnings', []).append([insert_incorrect_natural_key_message(row, 'lawsuit_city')])

            # Validacao de court_division
            court_division = row.get('lawsuit_court_division', '')
            if court_division:
                court_division = CourtDivision.objects.filter(name__unaccent__iexact=court_division,
                                                              office=self.office).first()
                if not court_division:
                    row.get('warnings', []).append([insert_incorrect_natural_key_message(row, 'lawsuit_court_division')])

            # Validacao de organ
            organ = row.get('lawsuit_organ', '')
            if organ:
                organ = Organ.objects.get_queryset(office=[self.office_id]).filter(
                    legal_name__unaccent__iexact=organ).first()
                if not organ:
                    row.get('warnings', []).append([insert_incorrect_natural_key_message(row, 'lawsuit_organ')])

            opposing_party = row.get('lawsuit_opposing_party', '')

            if not (city or court_district):
                REQUIRED_ONE_IN_GROUP.format('local de execução',
                                             [COLUMN_NAME_DICT['lawsuit_court_district']['column_name'],
                                              COLUMN_NAME_DICT['lawsuit_city']['column_name']])
            if not row_errors:
                if not lawsuit:
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
                                                     legacy_code=lawsuit_legacy_code,
                                                     system_prefix=system_prefix,)
                else:
                    if instance:
                        lawsuit.instance = instance
                    if person_lawyer:
                        lawsuit.person_lawyer = person_lawyer
                    if court_district:
                        lawsuit.court_district = court_district
                    if court_district_complement:
                        lawsuit.court_district_complement = court_district_complement
                    if city:
                        lawsuit.city = city
                    if court_division:
                        lawsuit.court_division = court_division
                    if organ:
                        lawsuit.organ = organ
                    if opposing_party:
                        lawsuit.opposing_party = opposing_party
                    lawsuit.is_current_instance = is_current_instance
                    lawsuit.save()
        if not lawsuit:
            row_errors.append(RECORD_NOT_FOUND.format(LawSuit._meta.verbose_name))
        return lawsuit
