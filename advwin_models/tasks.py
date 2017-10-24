from enum import Enum
from json import loads
from os import linesep

from celery import shared_task
from celery.utils.log import get_task_logger
# from sqlalchemy.sql.expression import cast
from sqlalchemy import String, cast
import dateutil.parser


from advwin_models.advwin import JuridFMAudienciaCorrespondente, JuridFMAlvaraCorrespondente, \
    JuridFMProtocoloCorrespondente, JuridFMDiligenciaCorrespondente, JuridAgendaTable, \
    JuridGedMain, JuridCorrespondenteHist
from connections.db_connection import get_advwin_engine
from etl.utils import ecm_path_ezl2advwin
from task.models import Task, TaskStatus, TaskHistory, Ecm, SurveyType


LOGGER = get_task_logger(__name__)

DO_SOMETHING_SUCCESS_MESSAGE = 'Do Something successful!'

DO_SOMETHING_ERROR_MESSAGE = 'ERROR during do something: {}'

SURVEY_TABLES_MAPPING = {
    SurveyType.COURTHEARING.name.title(): JuridFMAudienciaCorrespondente,
    SurveyType.DILIGENCE.name.title(): JuridFMDiligenciaCorrespondente,
    SurveyType.PROTOCOL.name.title(): JuridFMProtocoloCorrespondente,
    SurveyType.OPERATIONLICENSE.name.title(): JuridFMAlvaraCorrespondente,
}


class TaskObservation(Enum):
    DONE = 'Ordem de serviço cumprida por'


@shared_task()
def export_ecm(ecm_id, ecm=None, execute=True):
    if ecm is None:
        ecm = Ecm.objects.get(pk=ecm_id)

    new_path = ecm_path_ezl2advwin(ecm.path.name)

    stmt = JuridGedMain.__table__.update()\
        .where(JuridGedMain.__table__.c.ID_doc == ecm.legacy_code)\
        .values(Link=new_path)

    if execute:
        LOGGER.debug('Exportando ECM %d-%s ', ecm.id, ecm)
        try:
            result = get_advwin_engine().execute(stmt)
        except Exception as exc:
            result = None
            LOGGER.warning('Não foi possíve exportar ECM: %d-%s\n%s',
                           ecm.id,
                           ecm,
                           exc,
                           exc_info=(type(exc), exc, exc.__traceback__))
        else:
            LOGGER.info('ECM %s: exportado', ecm)
            return result
    else:
        return stmt


def get_task_survey_values(task):
    values = loads(task.survey_result)
    values['agenda_id'] = task.legacy_code
    values['versao'] = 1

    if 'question1' in values:
        del values['question1']

    for key in values:
        if key.startswith('data'):
            if values[key]:
                values[key] = dateutil.parser.parse(values[key])

    return values


def get_task_observation(task, message, date_field):
    last_taskhistory = task.taskhistory_set.filter(status=task.task_status).last()
    last_taskhistory_notes = last_taskhistory.notes if last_taskhistory else ''
    dt = getattr(task, date_field)
    date = dt.strftime('%d/%m/%Y') if dt else ''
    s = '{} *** {} {}: {} em {}'.format(
        linesep,
        message,
        task.person_executed_by,
        last_taskhistory_notes,
        date)
    return cast(JuridAgendaTable.Obs, String()) + s


@shared_task()
def export_task_history(task_history_id, task_history=None, execute=True):
    if task_history is None:
        task_history = TaskHistory.objects.get(pk=task_history_id)

    table = JuridCorrespondenteHist.__table__

    task = task_history.task

    if task_history.status == TaskStatus.ACCEPTED.value:
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

    elif task_history.status == TaskStatus.DONE.value:
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

    elif task_history.status == TaskStatus.REFUSED.value:
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


def update_advwin_task(task, values, execute=True):
    stmt = JuridAgendaTable.__table__.update()\
        .where(JuridAgendaTable.__table__.c.Ident == task.legacy_code)\
        .values(**values)

    if execute:
        LOGGER.debug('Exportando OS %d-%s ', task.id, task)
        try:
            result = get_advwin_engine().execute(stmt)
        except Exception as exc:
            result = None
            LOGGER.warning('Não foi possíve exportar OS: %d-%s com status %s\n%s',
                           task.id,
                           task,
                           task.task_status,
                           exc,
                           exc_info=(type(exc), exc, exc.__traceback__))
        else:
            LOGGER.info('OS %s: exportada com  status %s', task, task.task_status)
        finally:
            return result
    else:
        return stmt


@shared_task()
def export_task(task_id, task=None, execute=True):
    if task is None:
        task = Task.objects.get(pk=task_id)

    table = JuridAgendaTable.__table__

    if task.task_status == TaskStatus.ACCEPTED.value:

        values = {
            'SubStatus': 50,
            'status_correspondente': 0,
            'prazo_lido': 0,
            'envio_alerta': 0,
            'Ag_StatusExecucao': 'Em execucao',
            'Data_correspondente': task.execution_date,
            'Obs': get_task_observation(task, 'Ordem de serviço aceita por', 'acceptance_date'),
        }

        return update_advwin_task(task, values, execute)

    elif task.task_status == TaskStatus.DONE.value:

        values = {
            'SubStatus': 70,
            'Status': 2,
            'Data_Fech': task.execution_date,
            'prazo_lido': 1,
            'Prazo_Interm': 1,
            'Ag_StatusExecucao': '',
            'Data_cumprimento': task.execution_date,
            'Obs': get_task_observation(task, TaskObservation.DONE.value, 'execution_date'),
        }

        result = update_advwin_task(task, values, execute)

        stmts = result

        if task.survey_result:
            table = SURVEY_TABLES_MAPPING[task.type_task.survey_type].__table__
            stmt = table.insert().values(**get_task_survey_values(task))

            if execute:
                LOGGER.debug('Exportando formulário da OS %d-%s', task.id, task)
                try:
                    result = get_advwin_engine().execute(stmt)
                except Exception as exc:
                    result = None
                    LOGGER.warning(
                        'Não foi possíve exportar formulário da OS: %d-%s com status %s\n%s',
                        task.id,
                        task,
                        task.task_status,
                        exc,
                        exc_info=(type(exc), exc, exc.__traceback__))
                else:
                    LOGGER.info('Formulário da OS %d-%s: exportada com  status %s',
                                task.id,
                                task,
                                task.task_status)
                finally:
                    return result

            stmts.append(stmt)

        if execute:
            return result

        return stmts

    elif task.task_status == TaskStatus.REFUSED.value:

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

        return update_advwin_task(task, values, execute)
