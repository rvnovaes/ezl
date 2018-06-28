from django import template
from django.conf import settings
from task.models import TaskStatus


register = template.Library()


@register.filter
def valid_status(status):
    if status:
        return TaskStatus(status) in [TaskStatus.REQUESTED, TaskStatus.ACCEPTED_SERVICE, TaskStatus.OPEN,
                                      TaskStatus.ACCEPTED]
    return False


@register.filter
def get_refused_action(user, task):
    refused_action = None
    if task.status.name == 'OPEN' or task.status.name == 'ACCEPTED':
        if task.person_executed_by == user.person:
            if task.status.name == 'OPEN':
                refused_action = 'REFUSED'
        elif not task.get_child:
            refused_action = 'REQUESTED'
        elif task.get_child:
            refused_action = 'REQUESTED' if valid_status(task.get_child.task_status) else 'INVALID_CHILD_STATUS'
    return refused_action
