from django import forms
from django.db.models import Q
from financial.models import ServicePriceTable
from financial.tables import ServicePriceTableTaskTable
from task.models import TaskStatus, TypeTask

PARENT_STATUS = {
    TaskStatus.REQUESTED: TaskStatus.OPEN,
    TaskStatus.ACCEPTED_SERVICE: TaskStatus.ACCEPTED,
    TaskStatus.REFUSED_SERVICE: TaskStatus.REQUESTED,
    TaskStatus.OPEN: TaskStatus.ACCEPTED,
    TaskStatus.ACCEPTED: TaskStatus.ACCEPTED,
    TaskStatus.REFUSED: TaskStatus.REQUESTED,
    TaskStatus.DONE: TaskStatus.ACCEPTED,
    TaskStatus.RETURN: TaskStatus.ACCEPTED,
    TaskStatus.BLOCKEDPAYMENT: TaskStatus.DONE,
    TaskStatus.FINISHED: TaskStatus.DONE,
}

CHILD_STATUS = {
    TaskStatus.REQUESTED: TaskStatus.REFUSED,
    TaskStatus.OPEN: TaskStatus.REQUESTED,
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
    :param child_status:vou liberar o código agora
￼￼￼￼￼
11:03 AM
que já da pra delegar pro ezlog
11:03 AM
porém ainda tem que criar a tabela de preços na mão
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

    def get_correspondents_table(self):
        task = self.task
        type_task = self.type_task
        type_task_main = self.type_task_main

        if type_task:
            court_district = task.movement.law_suit.court_district
            state = task.movement.law_suit.court_district.state
            client = task.movement.law_suit.folder.person_customer
            offices_related = task.office.offices.all()
            qs = ServicePriceTable.objects.filter(
                Q(
                    Q(office=task.office)
                    | Q(Q(
                        office__public_office=True), ~Q(office=task.office))),
                Q(
                    Q(
                        Q(  # para escritorios nao publicos seleciona os precos que
                            # estao vinculados aos tipos de servico da tabaela do
                            # proprio escritorio
                            Q(type_task=type_task) | Q(type_task=None)),
                        Q(office=task.office)) |
                    Q(  # para escritorios publicos seleciona os precos que estao
                        # vinculados aos tipos de servico vinculados ao tipo de
                        # servico padrao
                        Q(type_task__type_task_main__in=type_task_main),
                        Q(office__public_office=True))),
                Q(
                    Q(office_correspondent__in=offices_related) | Q(
                        Q(office_correspondent__public_office=True), ~Q(
                            office_correspondent=task.office))),
                Q(office_correspondent__is_active=True),
                Q(Q(court_district=court_district) | Q(court_district=None)),
                Q(Q(state=state) | Q(state=None)),
                Q(Q(client=client) | Q(client=None)),
                Q(is_active=True))
            qs_values = qs.values('pk', 'office_id', 'type_task__office_id',
                                  'type_task')
            ignore_list = [
                v['pk'] for v in qs_values
                if (v['type_task']
                    and v['office_id'] != v['type_task__office_id'])
            ]
            if ignore_list:
                qs = qs.filter(~Q(id__in=ignore_list))
            correspondents_table = ServicePriceTableTaskTable(set(qs))
        else:
            correspondents_table = ServicePriceTableTaskTable(
                ServicePriceTable.objects.none())

        return correspondents_table

    def get_type_task(self, task):
        type_task = task.type_task
        type_task_main = task.type_task.main_tasks
        if task.parent:
            self.type_task_qs = TypeTask.objects.filter(office=self.office_session, type_task_main__in=type_task_main)
            if type_task.office != self.office_session:
                if self.type_task_qs.count() == 1:
                    type_task = self.type_task_qs.first()
                    type_task_main = type_task.main_tasks
                else:
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

    def update_type_task(self, type_task):
        self.task.type_task = type_task
        self.task.save(**{'skip_signal': True, 'skip_mail': True})
        self.type_task = type_task

        return type_task
