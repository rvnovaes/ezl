from django import forms
from django.db.models import Q
from financial.models import ServicePriceTable, CategoryPrice
from financial.tables import ServicePriceTableTaskTable
from task.models import TaskStatus, TypeTask
from financial.filters import ServicePriceTableDefaultFilter, ServicePriceTableOfficeFilter, \
    ServicePriceTableTypeTaskFilter

PARENT_STATUS = {
    TaskStatus.ACCEPTED: TaskStatus.ACCEPTED,
    TaskStatus.ACCEPTED_SERVICE: TaskStatus.ACCEPTED,
    TaskStatus.BLOCKEDPAYMENT: TaskStatus.DONE,
    TaskStatus.DONE: TaskStatus.ACCEPTED,
    TaskStatus.FINISHED: TaskStatus.DONE,
    TaskStatus.OPEN: TaskStatus.ACCEPTED,
    TaskStatus.REFUSED: TaskStatus.REQUESTED,
    TaskStatus.REFUSED_SERVICE: TaskStatus.REQUESTED,
    TaskStatus.REQUESTED: TaskStatus.OPEN,
    TaskStatus.RETURN: TaskStatus.ACCEPTED,
}

CHILD_STATUS = {
    TaskStatus.OPEN: TaskStatus.REQUESTED,
    TaskStatus.REFUSED: TaskStatus.REFUSED,
    TaskStatus.REFUSED_SERVICE: TaskStatus.REFUSED,
    TaskStatus.REQUESTED: TaskStatus.REFUSED,
    TaskStatus.RETURN: TaskStatus.RETURN,
}

PARENT_FIELDS = {
    TaskStatus.ACCEPTED_SERVICE: ['acceptance_date'],
    TaskStatus.OPEN: ['acceptance_date'],
    TaskStatus.ACCEPTED: ['acceptance_date'],
    TaskStatus.REFUSED: ['acceptance_date'],
    TaskStatus.DONE: ['acceptance_date'],
    TaskStatus.RETURN: ['acceptance_date'],
    TaskStatus.BLOCKEDPAYMENT: ['execution_date'],
    TaskStatus.FINISHED: ['execution_date'],
}

PARENT_RECIPIENTS = {
    TaskStatus.REFUSED_SERVICE: {
        'persons_to_receive': ['person_distributed_by'],
        'short_message': 'foi recusada ',
        'office': 'child'
    },
    TaskStatus.REFUSED: {
        'persons_to_receive': ['person_distributed_by'],
        'short_message': 'foi recusada ',
        'office': 'child'
    },
}

CHILD_RECIPIENTS = {
    TaskStatus.RETURN: {
        'persons_to_receive': ['office'],
        'short_message': 'foi retornada ',
        'office': 'parent'
    },
}


def get_parent_status(child_status):
    """
    Retorna o status da OS pai de acordo com o status da OS filha informado no parametro
    :param child_status:
    :return:
    """
    return PARENT_STATUS.get(child_status)


def get_child_status(parent_status):
    """
    Retorna o status da OS filha de acordo com o status da OS pa informado no parametro
    :param parent_status:
    :return:
    """
    return CHILD_STATUS.get(parent_status)


def get_parent_fields(child_status):
    """
    Retorna os campos da OS pai que serão atualizados de acordo com o status da OS filha informado no parametro
    :param child_status:
    :return: lista de string com nomes de campos
    """
    return PARENT_FIELDS.get(child_status, [])


def get_parent_recipients(child_status):
    """
    Retorna os destinatários da OS pai que receberam e-mail, de acordo com o status da Os filha
    :param child_status: status da OS filha
    :return:
    """
    return PARENT_RECIPIENTS.get(child_status, {})


def get_child_recipients(parent_status):
    """
    Retorna os destinatários da OS filha que receberam e-mail, de acordo com o status da OS pai
    :param parent_status: status da OS pai
    :return:
    """
    return CHILD_RECIPIENTS.get(parent_status, {})



# Todo: Verificar se esta classe realmente deve estar neste arquivo
class CorrespondentsTable(object):
    def __init__(self, task, office_session, type_task_qs=None,
                 type_task=None):
        self.task = task
        self.office_session = office_session
        self.type_task_qs = type_task_qs        
        if not type_task:
            self.type_task, self.type_task_main = self.get_type_task(task)
        else:
            self.type_task = type_task
            self.type_task_main = type_task.main_tasks
        self.qs = None
        self.correspondents_qs = self.get_correspondents_qs()            

    def get_cheapest_correspondent(self):        
        correspondents = self.correspondents_qs
        if self.qs:
            # Feito desta forma por conta de performance (Nao utilizar o sorted pois aumenta muito o tempo de execucao)
            return max(self.qs.filter(value=self.qs.earliest('value').value),
                       key=lambda k: k.office_rating if k.office_rating else '0.00')
        return None

    def get_correspondents_qs(self):
        task = self.task
        type_task = self.type_task
        type_task_main = self.type_task_main
        if type_task or type_task_main:
            data = {
                'task': task,
                'type_task': type_task,
                'type_task_main': type_task_main,
                'complement': task.movement.law_suit.court_district_complement,
                'city': task.movement.law_suit.city,
                'court_district': task.movement.law_suit.court_district,
                'state': getattr(task.movement.law_suit.court_district, 'state',
                                 None) or getattr(task.movement.law_suit.city, 'state', None),
                'client': task.movement.law_suit.folder.person_customer,
                'offices_related': task.office.offices.all()
            }
            networks = task.office.network_members.all()
            network_office_id_list = []
            for net in networks:
                network_office_id_list.extend([x.id for x in
                                               net.members.all().order_by('id') if x.id != task.office.id])
            network_office_id_list = list(set(network_office_id_list))
            data['networks'] = networks
            data['network_office_id_list'] = network_office_id_list

            qs = None
            for filter_class in [ServicePriceTableDefaultFilter, ServicePriceTableOfficeFilter,
                                 ServicePriceTableTypeTaskFilter]:
                qs = filter_class(data=data, queryset=qs).get_delegation_queryset()

            qs = qs or ServicePriceTable.objects.none()
            qs_values = qs.values('pk', 'office_id', 'type_task__office_id',
                                  'type_task')
            # cria uma lista e ids que tenham tabelas de preço com preços vinculados à tipos de serviço de outros
            # escritórios. Esse filtro é necessário para eliminar preços anteriores à criação do tipo de preços por
            # escritório
            ignore_list = [
                v['pk'] for v in qs_values
                if (v['type_task']
                    and v['office_id'] != v['type_task__office_id'])
            ]
            if ignore_list:
                qs = qs.filter(~Q(id__in=ignore_list))
            self.qs = qs
            return set(qs)
        else:
            return ServicePriceTable.objects.none()

    def get_correspondents_table(self):
        return ServicePriceTableTaskTable(self.correspondents_qs)

    def get_type_task(self, task):
        type_task = task.type_task
        type_task_main = task.type_task.main_tasks
        if task.parent:
            self.type_task_qs = TypeTask.objects.filter(office=self.office_session, type_task_main__in=type_task_main)
            if type_task.office != self.office_session:
                type_task = None
        return type_task, type_task_main

    def get_type_task_field(self):
        if not self.type_task_qs:
            type_task_field = None
        else:
            initial = None
            if self.type_task in self.type_task_qs:
                initial = self.type_task.id
            elif self.type_task_qs.count() == 1:
                initial = self.type_task_qs.first().id
            type_task_field = forms.ModelChoiceField(
                queryset=self.type_task_qs,
                empty_label='',
                required=True,
                label=u'Selecione o tipo de serviço',
                initial=initial,
            )

        return type_task_field
