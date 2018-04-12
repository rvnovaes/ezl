from task.models import TaskStatus

PARENT_STATUS = {
    TaskStatus.REQUESTED: TaskStatus.OPEN,
    TaskStatus.ACCEPTED_SERVICE: TaskStatus.ACCEPTED,
    TaskStatus.REFUSED_SERVICE: TaskStatus.REQUESTED,
    TaskStatus.OPEN: TaskStatus.OPEN,
    TaskStatus.ACCEPTED: TaskStatus.OPEN,
    TaskStatus.REFUSED: TaskStatus.OPEN,
    TaskStatus.DONE: TaskStatus.OPEN,
    TaskStatus.RETURN: TaskStatus.OPEN,
    TaskStatus.BLOCKEDPAYMENT: TaskStatus.OPEN,
    TaskStatus.FINISHED: TaskStatus.DONE,
}

CHILD_STATUS = {
    TaskStatus.RETURN: TaskStatus.RETURN,
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
