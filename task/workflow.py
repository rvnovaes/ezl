from task.models import TaskStatus

PARENT_STATUS = {
    TaskStatus.REQUESTED: TaskStatus.OPEN,
    TaskStatus.ACCEPTED_SERVICE: TaskStatus.ACCEPTED,
    TaskStatus.REFUSED_SERVICE: TaskStatus.ACCEPTED_SERVICE,
    TaskStatus.OPEN: TaskStatus.ACCEPTED,
    TaskStatus.ACCEPTED: TaskStatus.ACCEPTED,
    TaskStatus.REFUSED: TaskStatus.ACCEPTED,
    TaskStatus.DONE: TaskStatus.ACCEPTED,
    TaskStatus.RETURN: TaskStatus.ACCEPTED,
    TaskStatus.BLOCKEDPAYMENT: TaskStatus.DONE,
    TaskStatus.FINISHED: TaskStatus.DONE,
}

CHILD_STATUS = {
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
