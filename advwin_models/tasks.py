from enum import Enum
from json import loads
from os import linesep
from celery import shared_task
from celery.utils.log import get_task_logger
from sqlalchemy import String, cast
import dateutil.parser
from advwin_models.advwin import JuridFMAudienciaCorrespondente, JuridFMAlvaraCorrespondente, \
    JuridFMProtocoloCorrespondente, JuridFMDiligenciaCorrespondente, JuridAgendaTable, \
    JuridGedMain, JuridCorrespondenteHist, JuridGEDLig
from connections.db_connection import get_advwin_engine
from etl.utils import ecm_path_ezl2advwin, get_ecm_file_name
from task.models import Task, TaskStatus, TaskHistory, Ecm, SurveyType
from sqlalchemy import and_
from django.utils import timezone


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
    file_name = get_ecm_file_name(ecm.path.name)
    values = {
        'Tabela_OR': 'Agenda',
        'Codigo_OR': ecm.task.legacy_code,
        'Link': new_path,
        'Data': timezone.localtime(ecm.create_date),
        'Nome': file_name,
        'Responsavel': ecm.create_user.username,
        'Arq_Status': 'Guardado',
        'Arq_nick': file_name,
        'Descricao': file_name
    }
    stmt = JuridGedMain.__table__.insert().values(**values)
    if execute:
        LOGGER.debug('Exportando ECM %d-%s ', ecm.id, ecm)
        result = None
        try:
            result = get_advwin_engine().execute(stmt)
            stmt = JuridGedMain.__table__.select().where(and_(
                JuridGedMain.__table__.c.Codigo_OR == ecm.task.legacy_code,
                JuridGedMain.__table__.c.Nome == file_name)
            )
            for row in get_advwin_engine().execute(stmt).fetchall():
                id_doc = row['ID_doc']
                export_ecm_related_folter_to_task(ecm, id_doc)
        except Exception as exc:
            LOGGER.warning('Não foi possíve exportar ECM: %d-%s\n%s',
                           ecm.id,
                           ecm,
                           exc,
                           exc_info=(type(exc), exc, exc.__traceback__))
        finally:
            LOGGER.info('ECM %s: exportado', ecm)
            return result
    else:
        return stmt


def export_ecm_related_folter_to_task(ecm, id_doc, execute=True):
    values = {
        'Id_tabela_or': 'Pastas',
        'Id_codigo_or': get_folder_to_related(task=ecm.task),
        'Id_id_doc': id_doc,
        'id_ID_or': 0,
        'dt_inserido': timezone.localtime(ecm.create_date),
        'usuario_insercao': ecm.create_user.username
    }
    stmt = JuridGEDLig.__table__.insert().values(**values)
    if execute:
        result = None
        try:
            result = get_advwin_engine().execute(stmt)
        except Exception as e:
            LOGGER.warning('Não foi possíve relacionar o ECM entre Agenda e Pasta: %d-%s\n%s',
                           ecm.id,
                           ecm,
                           e,
                           exc_info=(type(e), e, e.__traceback__))
        finally:
            LOGGER.info('ECM %s: relacionamento criado entre Pasta e Agenda', ecm)
            return result


def get_folder_to_related(task):
    if task.movement.law_suit.folder.legacy_code == 'REGISTRO-INVÁLIDO':
        result = None
        try:
            stmt = JuridAgendaTable.__table__.select().where(and_(
                JuridAgendaTable.__table__.c.Ident == task.legacy_code
            ))
            result = get_advwin_engine().execute(stmt).fetchone()['Pasta']
        except Exception as e:
            LOGGER.warning('Não foi possíve encontrar pasta para a Providencia: %d-%s\n%s',
                           task.legacy_code, exc_info=(type(e), e, e.__traceback__))
        finally:
            return result
    return task.movement.law_suit.folder.legacy_code


def get_task_survey_values(task):
    values = loads(task.survey_result)
    values['paginas'] = ',1,2,'
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
        task.alter_user.username,
        last_taskhistory_notes,
        date)
    return cast(JuridAgendaTable.Obs, String()) + s


def insert_advwin_history(task_history, values, execute=True):
    stmt = JuridCorrespondenteHist.__table__.insert().values(**values)

    if execute:
        LOGGER.debug('Exportando Histórico de OS %d-%d ', task_history.task.id, task_history.id)
        try:
            result = get_advwin_engine().execute(stmt)
        except Exception as exc:
            result = None
            LOGGER.warning('Não foi possíve exportar Histórico de OS: %d-%d\n%s',
                           task_history.task.id,
                           task_history.id,
                           exc,
                           exc_info=(type(exc), exc, exc.__traceback__))
        else:
            LOGGER.info('Histórico de OS %d-%d: exportado com sucesso.',
                        task_history.task.id,
                        task_history.id)
        return result
    else:
        return stmt


@shared_task()
def export_task_history(task_history_id, task_history=None, execute=True, **kwargs):
    if task_history is None:
        task_history = TaskHistory.objects.get(pk=task_history_id)

    username = ''
    if task_history.create_user:
        username = task_history.create_user.username[:20]

    task = task_history.task
    if task_history.status == TaskStatus.ACCEPTED.value:
        values = {
            'codigo_adv_correspondente': task.person_executed_by.legacy_code,
            'ident_agenda': task.legacy_code,
            'status': 0,
            'SubStatus': 50,
            'data_operacao': timezone.localtime(task_history.create_date),
            'justificativa': task_history.notes,
            'usuario': username,
            'descricao': 'Aceita por correspondente: {}'.format(
                task.person_executed_by.legal_name),
        }
        return insert_advwin_history(task_history, values, execute)

    elif task_history.status == TaskStatus.DONE.value:
        values = {
            'codigo_adv_correspondente': task.person_executed_by.legacy_code,
            'ident_agenda': task.legacy_code,
            'status': 0,
            'SubStatus': 70,
            'data_operacao': timezone.localtime(task_history.create_date),
            'justificativa': task_history.notes,
            'usuario': username,
            'descricao': 'Cumprida por correspondente: {}'.format(
                task.person_executed_by.legal_name),
        }
        return insert_advwin_history(task_history, values, execute)

    elif task_history.status == TaskStatus.REFUSED.value:
        values = {
            'codigo_adv_correspondente': task.person_executed_by.legacy_code,
            'ident_agenda': task.legacy_code,
            'status': 0,
            'SubStatus': 20,
            'data_operacao': timezone.localtime(task_history.create_date),
            'justificativa': task_history.notes,
            'usuario': username,
            'descricao': 'Recusada por correspondente: {}'.format(
                task.person_executed_by.legal_name),
        }
        return insert_advwin_history(task_history, values, execute)
    elif task_history.status == TaskStatus.FINISHED.value:
        values = {
            'codigo_adv_correspondente': task.person_executed_by.legacy_code,
            'ident_agenda': task.legacy_code,
            'status': 0,
            'SubStatus': 100,
            'data_operacao': timezone.localtime(task_history.create_date),
            'justificativa': task_history.notes,
            'usuario': username,
            'descricao': 'Diligência devidamente cumprida por: {}'.format(
                task.person_executed_by.legal_name),
        }
        return insert_advwin_history(task_history, values, execute)
    elif task_history.status == TaskStatus.RETURN.value:
        values = {
            'codigo_adv_correspondente': task.person_executed_by.legacy_code,
            'ident_agenda': task.legacy_code,
            'status': 0,
            'SubStatus': 80,
            'data_operacao': timezone.localtime(task_history.create_date),
            'justificativa': task_history.notes,
            'usuario': username,
            'descricao': 'Diligência delegada ao correspondente para complementação:'
        }
        return insert_advwin_history(task_history, values, execute)
    elif task_history.status == TaskStatus.BLOCKEDPAYMENT.value:
        values = {
            'codigo_adv_correspondente': task.person_executed_by.legacy_code,
            'ident_agenda': task.legacy_code,
            'status': 0,
            'SubStatus': 90,
            'data_operacao': timezone.localtime(task_history.create_date),
            'justificativa': task_history.notes,
            'usuario': username,
            'descricao': 'Diligência não cumprida - pagamento glosado'
        }
        return insert_advwin_history(task_history, values, execute)
    elif task_history.status == TaskStatus.ACCEPTED_SERVICE.value:
        values = {
            'ident_agenda': task.legacy_code,
            'codigo_adv_solicitante': task.person_asked_by.legacy_code,
            'codigo_adv_origem': task.person_distributed_by.legacy_code,
            'SubStatus': 11,
            'status': 0,
            'data_operacao': timezone.localtime(task_history.create_date),
            'justificativa': task_history.notes,
            'usuario': username,
            'descricao': 'Aceita por Back Office: {}'.format(
                task.person_executed_by.legal_name),
        }
        return insert_advwin_history(task_history, values, execute)
    elif task_history.status == TaskStatus.REFUSED_SERVICE.value:
        values = {
            'ident_agenda': task.legacy_code,
            'codigo_adv_solicitante': task.person_asked_by.legacy_code,
            'codigo_adv_origem': task.person_distributed_by.legacy_code,
            'SubStatus': 20,
            'status': 1,
            'data_operacao': timezone.localtime(task_history.create_date),
            'justificativa': task_history.notes,
            'usuario': username,
            'descricao': 'Recusada por Back Office: {}'.format(
                task.person_executed_by.legal_name),
        }
        return insert_advwin_history(task_history, values, execute)
    elif task_history.status == TaskStatus.OPEN.value:
        values = {
            'ident_agenda': task.legacy_code,
            'codigo_adv_solicitante': task.person_asked_by.legacy_code,
            'codigo_adv_origem': task.person_distributed_by.legacy_code,
            'codigo_adv_correspondente': task.person_executed_by.legacy_code,
            'SubStatus': 30,
            'status': 0,
            'data_operacao': timezone.localtime(task_history.create_date),
            'justificativa': task_history.notes,
            'usuario': username,
            'descricao': 'Solicitada ao correspondente ('+task.person_executed_by.legal_name +
                         ') por BackOffice: {}'.format(
                task.person_distributed_by.legal_name),
        }
        return insert_advwin_history(task_history, values, execute)


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
            'Data_correspondente': timezone.localtime(task.execution_date),
            'Obs': get_task_observation(task, 'Ordem de serviço aceita por', 'acceptance_date'),
        }

        return update_advwin_task(task, values, execute)

    elif task.task_status == TaskStatus.DONE.value:

        values = {
            'SubStatus': 70,
            'Status': 2,
            'Data_Fech': timezone.localtime(task.execution_date),
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
            'SubStatus': 40,
            'status_correspondente': 1,
            'Advogado': task.person_distributed_by.legacy_code,            
            'Data_correspondente': task.refused_date,
            'Obs': get_task_observation(task, 'Ordem de serviço recusada por', 'refused_date'),
        }
        return update_advwin_task(task, values, execute)
    elif task.task_status == TaskStatus.FINISHED.value:
        values = {
            'SubStatus': 100,
            'Status': 1,
            'prazo_lido': 1,
            'Prazo_Interm': 1,
            'Data_correspondente': task.refused_date,
            'Ag_StatusExecucao': '',
            'Data_cumprimento': task.execution_date,
            'Obs': get_task_observation(task, 'Diligência devidamente cumprida por',
                                        'finished_date')
        }
        return update_advwin_task(task, values, execute)
    elif task.task_status == TaskStatus.RETURN.value:
        values = {
            'SubStatus': 80,
            'Status': 0,
            'prazo_lido': 1,
            'Prazo_Interm': 1,
            'Data_correspondente': task.refused_date,
            'Ag_StatusExecucao': '',
            'Data_cumprimento': task.execution_date,
            'Obs': get_task_observation(
                task, 'Diligência delegada ao correspondente para complementação por',
                'return_date')
        }
        return update_advwin_task(task, values, execute)
    elif task.task_status == TaskStatus.BLOCKEDPAYMENT.value:
        values = {
            'SubStatus': 90,
            'Status': 1,
            'prazo_lido': 1,
            'Prazo_Interm': 1,
            'Data_correspondente': task.refused_date,
            'Ag_StatusExecucao': 'Glosado',
            'Data_cumprimento': task.execution_date,
            'Obs': get_task_observation(task,
                                        'Diligência não cumprida - pagamento glosado por',
                                        'blocked_payment_date')
        }
        return update_advwin_task(task, values, execute)
    elif task.task_status == TaskStatus.ACCEPTED_SERVICE.value:

        values = {
            'SubStatus': 11,
            'Status': 0,
            'Advogado_or': task.person_distributed_by.legacy_code,
            'Data_backoffice': timezone.localtime(task.acceptance_service_date),
            'envio_alerta': 0,
            'Obs': get_task_observation(task, 'Aceita por Back Office:', 'acceptance_service_date'),
        }

        return update_advwin_task(task, values, execute)
    elif task.task_status == TaskStatus.REFUSED_SERVICE.value:

        values = {
            'SubStatus': 20,
            'Status': 1,
            'prazo_lido': 1,
            'Data_backoffice': timezone.localtime(task.refused_service_date),
            'envio_alerta': 0,
            'Obs': get_task_observation(task, 'Recusada por Back Office', 'refused_service_date'),
        }

        return update_advwin_task(task, values, execute)
    elif task.task_status == TaskStatus.OPEN.value:

        values = {
            'SubStatus': 30,
            'Advogado': task.person_executed_by.legacy_code,
            'Advogado_or': task.person_distributed_by.legacy_code,
            'prazo_lido': 0,
            'Data_delegacao': task.delegation_date,
            'Obs': get_task_observation(task, 'Ordem de Serviço delegada para:' + task.person_executed_by.auth_user.username + ' por ', 'delegation_date'),
        }

        return update_advwin_task(task, values, execute)
