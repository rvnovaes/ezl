from django import template
from django.conf import settings
from task.models import Task, TaskStatus, CheckPointType


register = template.Library()


@register.filter
def valid_status(status):
    if status:
        return TaskStatus(status) in [TaskStatus.REQUESTED, TaskStatus.ACCEPTED_SERVICE, TaskStatus.OPEN,
                                      TaskStatus.ACCEPTED]
    return False


@register.filter
def show_company_representative_buttons(status):
    if status:
        return str(TaskStatus(status)) in [str(TaskStatus.RETURN), str(TaskStatus.OPEN), str(TaskStatus.ACCEPTED),
                                      str(TaskStatus.DONE)]
    return False


@register.simple_tag
def get_refused_action(user, task, office_session_perms):
    refused_action = None
    if task.status.name == 'OPEN' or task.status.name == 'ACCEPTED':
        if task.person_executed_by == user.person:
            if task.status.name == 'OPEN':
                refused_action = 'REFUSED'
        elif not task.get_child:
            refused_action = 'REQUESTED'
        elif task.get_child:
            refused_action = 'REQUESTED' if valid_status(task.get_child.task_status) else 'INVALID_CHILD_STATUS'
    if 'can_distribute_tasks' in office_session_perms and task.status.name == 'ERROR':
        if task.office.use_service:
            refused_action = 'REFUSED_SERVICE'
        else:
            refused_action = 'REFUSED'
    return refused_action


@register.filter
def remove_spaces_lower(status):
    try:
        ret = status.value
    except:
        ret = status
    return ret.replace(' ', '_').lower()


@register.simple_tag
def get_checkin(geolocation):
    if geolocation:
        return geolocation.filter(checkpointtype='Checkin')
    return ''


@register.simple_tag
def get_checkout(geolocation):
    if geolocation:
        return geolocation.filter(checkpointtype='Checkout')
    return ''


@register.filter
def get_checkpoint_type(geolocation, user):
    checkin_exist = geolocation.filter(create_user=user, checkpointtype=CheckPointType.CHECKIN).exists()
    checkout_exist = geolocation.filter(create_user=user, checkpointtype=CheckPointType.CHECKOUT).exists()
    if all([checkin_exist, checkout_exist]):
        return ''
    if (checkin_exist):
        return 'CHECKOUT'
    return 'CHECKIN'

@register.filter
def get_checkpoint_type_by_task(dashboard_task, user):
    checkin_exist = Task.objects.get(pk=dashboard_task.pk).geolocation.filter(
        create_user=user, checkpointtype=CheckPointType.CHECKIN).exists()
    checkout_exist = Task.objects.get(pk=dashboard_task.pk).geolocation.filter(
        create_user=user, checkpointtype=CheckPointType.CHECKOUT).exists()
    if all([checkin_exist, checkout_exist]) or dashboard_task.task_status not in [str(TaskStatus.RETURN),
                                                                                  str(TaskStatus.OPEN),
                                                                                  str(TaskStatus.ACCEPTED),
                                                                                  str(TaskStatus.DONE)]:
        return ''
    if checkin_exist:
        return 'CHECKOUT'
    return 'CHECKIN'


@register.filter
def show_delegation_modal(task):
    return task.status.name == 'ACCEPTED_SERVICE' or (not task.office.use_service and task.status.name == 'REQUESTED')


@register.filter
def show_edit_amount(task):
    if task.status.name in ['RETURN', 'OPEN', 'ACCEPTED', 'DONE']:
        return True
    return False