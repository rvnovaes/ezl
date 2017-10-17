from json import loads
from os import linesep

from celery import shared_task
from celery.utils.log import get_task_logger
from raven.contrib.django.raven_compat.models import client
from sqlalchemy import cast, String

from advwin_models.advwin import JuridFMAudienciaCorrespondente, JuridFMAlvaraCorrespondente, \
    JuridFMProtocoloCorrespondente, JuridFMDiligenciaCorrespondente, JuridAgendaTable, \
    JuridCorrespondenteHist
from task.models import Task, TaskStatus, TaskHistory


LOGGER = get_task_logger(__name__)

DO_SOMETHING_SUCCESS_MESSAGE = 'Do Something successful!'

DO_SOMETHING_ERROR_MESSAGE = 'ERROR during do something: {}'

SURVEY_TABLES_MAPPING = {
    'Courthearing': JuridFMAudienciaCorrespondente,
    'Diligence': JuridFMDiligenciaCorrespondente,
    'Protocol': JuridFMProtocoloCorrespondente,
    'Operationlicense': JuridFMAlvaraCorrespondente,
}


def get_task_survey_values(task):
    values = loads(task.survey_result)
    values['agenda_id'] = task.legacy_code
    values['versao'] = 1
    return values


def get_task_observation(task, message, date_field):
    casting = cast(JuridAgendaTable.Obs, String())
    last_taskhistory_notes = task.taskhistory_set.filter(status=task.task_status).last().notes
    dt = getattr(task, date_field)
    date = dt.strftime('%d/%m/%Y') if dt else ''
    s = '{}{} *** {} {}: {} em {}'.format(
        casting,
        linesep,
        message,
        task.person_executed_by,
        last_taskhistory_notes,
        date)
    return s


@shared_task()
def export_task_history(task_history_id, task_history=None):
    if task_history is None:
        task_history = TaskHistory.objects.get(pk=task_history_id)

    table = JuridCorrespondenteHist.__table__

    task = task_history.task

    if task_history.status == TaskStatus.ACCEPTED:
        values = {
            'codigo_adv_correspondente': str(task_history.create_user),
            'ident_agenda': task.legacy_code,
            'status': 0,
            'SubStatus': 50,
            'data_operacao': task_history.create_date,
            'justificativa': task_history.notes,
            'usuario': task.person_executed_by.auth_user.username,
            'descricao': 'Aceita por correspondente: {}'.format(
                task.person_executed_by.legal_name),
        }

        stmt = table.insert().values(**values)
        return stmt

    elif task_history.status == TaskStatus.DONE:
        values = {
            'codigo_adv_correspondente': str(task_history.create_user),
            'ident_agenda': task.legacy_code,
            'status': 0,
            'SubStatus': 70,
            'data_operacao': task_history.create_date,
            'justificativa': task_history.notes,
            'usuario': task.person_executed_by.auth_user.username,
            'descricao': 'Cumprida por correspondente: {}'.format(
                task.person_executed_by.legal_name),
        }

        stmt = table.insert().values(**values)
        return stmt

    elif task_history.status == TaskStatus.REFUSED:
        values = {
            'codigo_adv_correspondente': str(task_history.create_user),
            'ident_agenda': task.legacy_code,
            'status': 0,
            'SubStatus': 20,
            'data_operacao': task_history.create_date,
            'justificativa': task_history.notes,
            'usuario': task.person_executed_by.auth_user.username,
            'descricao': 'Recusada por correspondente: {}'.format(
                task.person_executed_by.legal_name),
        }

        stmt = table.insert().values(**values)
        return stmt


@shared_task()
def export_task(task_id, task=None):
    if task is None:
        task = Task.objects.get(pk=task_id)

    table = JuridAgendaTable.__table__

    if task.task_status == TaskStatus.ACCEPTED:

        values = {
            'SubStatus': 50,
            'status_correspondente': 0,
            'prazo_lido': 0,
            'envio_alerta': 0,
            'Ag_StatusExecucao': 'Em execucao',
            'Data_correspondente': task.execution_date,
            'Obs': get_task_observation(task, 'Ordem de serviço aceita por', 'acceptance_date'),
        }

        stmt = table.update().where(table.c.Ident == task.legacy_code).values(**values)
        return stmt

    elif task.task_status == TaskStatus.DONE:

        values = {
            'SubStatus': 70,
            'Status': 2,
            'Data_Fech': task.execution_date,
            'prazo_lido': 1,
            'Prazo_Interm': 1,
            'Ag_StatusExecucao': '',
            'Data_cumprimento': task.execution_date,
            'Obs': get_task_observation(task, 'Ordem de serviço cumprida por', 'execution_date'),
        }

        update = table.update().where(table.c.Ident == task.legacy_code).values(**values)
        stmts = [update]

        if task.survey_result:
            table = SURVEY_TABLES_MAPPING.get(task.type_task.survey_type)
            insert = table.insert().values(**get_task_survey_values(task))
            stmts.append(insert)
        return stmts

    elif task.task_status == TaskStatus.REFUSED:

        values = {
            'SubStatus': 20,
            'Status': 1,
            'prazo_lido': 1,
            'Prazo_Interm': 1,
            'Data_correspondente': task.refused_date,
            'Ag_StatusExecucao': '',
            'Data_cumprimento': task.execution_date,
            'Obs': get_task_observation(task, 'Ordem de serviço recusada por', 'refused_date'),
        }

        stmt = table.update().where(table.c.Ident == task.legacy_code).values(**values)
        return stmt

    try:
        print('something')
        LOGGER.info(DO_SOMETHING_SUCCESS_MESSAGE)
    except Exception as exc:
        LOGGER.error(DO_SOMETHING_ERROR_MESSAGE, exc)
        client.captureException()
