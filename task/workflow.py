from task.models import TaskStatus

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
    TaskStatus.ACCEPTED_SERVICE: {'persons_to_receive': ['person_distributed_by'],
                                  'short_message': 'foi aceita ',
                                  'office': 'child'},
    TaskStatus.REFUSED_SERVICE: {'persons_to_receive': ['person_distributed_by'],
                                 'short_message': 'foi recusada ',
                                 'office': 'child'},
    TaskStatus.ACCEPTED: {'persons_to_receive': ['person_distributed_by'],
                          'short_message': 'foi aceita ',
                          'office': 'child'},
    TaskStatus.REFUSED: {'persons_to_receive': ['person_distributed_by'],
                         'short_message': 'foi recusada ',
                         'office': 'child'},
    TaskStatus.BLOCKEDPAYMENT: {'persons_to_receive': ['person_distributed_by'],
                                'short_message': 'foi finalizada ',
                                'office': 'child'},
    TaskStatus.DONE: {'persons_to_receive': [],
                      'short_message': '',
                      'office': ''},
    TaskStatus.FINISHED: {'persons_to_receive': ['person_distributed_by'],
                          'short_message': 'foi cumprida ',
                          'office': 'child'},
}

CHILD_RECIPIENTS = {
    TaskStatus.OPEN: {'persons_to_receive': ['office'],
                      'short_message': 'foi solicitada ',
                      'office': 'parent'},
    TaskStatus.RETURN: {'persons_to_receive': ['office'],
                        'short_message': 'foi retornada ',
                        'office': 'parent'},
    TaskStatus.BLOCKEDPAYMENT: {'persons_to_receive': ['office'],
                                'short_message': 'foi glosada ',
                                'office': 'parent'},
    TaskStatus.FINISHED: {'persons_to_receive': ['office'],
                          'short_message': 'foi finalizada ',
                          'office': 'parent'},
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
