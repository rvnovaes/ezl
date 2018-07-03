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
from task.models import Task, TaskStatus, TaskHistory, Ecm
from sqlalchemy import and_
from django.utils import timezone
from guardian.shortcuts import get_users_with_perms


LOGGER = get_task_logger(__name__)

DO_SOMETHING_SUCCESS_MESSAGE = 'Do Something successful!'

DO_SOMETHING_ERROR_MESSAGE = 'ERROR during do something: {}'

MAX_RETRIES = 10

BASE_COUNTDOWN = 2


class TaskObservation(Enum):
    DONE = 'Ordem de serviço cumprida por'


@shared_task(bind=True, max_retries=MAX_RETRIES)
def export_ecm(self, ecm_id, ecm=None, execute=True):
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
        try:
            result = get_advwin_engine().execute(stmt)
        except Exception as exc:
            self.retry(countdown=(BASE_COUNTDOWN ** self.request.retries), exc=exc)
            LOGGER.warning('Não foi possível exportar ECM: %d-%s\n%s',
                           ecm.id,
                           ecm,
                           exc,
                           exc_info=(type(exc), exc, exc.__traceback__))
            raise exc
        get_related_folder_to_task.delay(ecm.id, ecm.task.legacy_code, file_name)
        LOGGER.info('ECM %s: exportado', ecm)
        return '{} Registros afetados'.format(result.rowcount)
    else:
        return stmt


@shared_task(bind=True, max_retries=MAX_RETRIES)
def get_related_folder_to_task(self, ecm_id, task_legacy_code, file_name):
    stmt = JuridGedMain.__table__.select().where(and_(
        JuridGedMain.__table__.c.Codigo_OR == task_legacy_code,
        JuridGedMain.__table__.c.Nome == file_name)
    )
    try:
        result = get_advwin_engine().execute(stmt)
    except Exception as exc:
        self.retry(countdown=(BASE_COUNTDOWN ** self.request.retries), exc=exc)
        LOGGER.warning('Não foi possível relacionar o ECM entre Agenda e Pasta: %d-%s\n%s',
                       ecm_id,
                       exc,
                       exc_info=(type(exc), exc, exc.__traceback__))
        raise exc
    for row in result:
        id_doc = row['ID_doc']
        export_ecm_related_folder_to_task.delay(ecm_id, id_doc)


@shared_task(bind=True, max_retries=MAX_RETRIES)
def export_ecm_related_folder_to_task(self, ecm_id, id_doc, execute=True):
    ecm = Ecm.objects.get(pk=ecm_id)
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
            LOGGER.info('ECM %s: relacionamento criado entre Pasta e Agenda', ecm)
            return '{} Registros afetados'.format(result.rowcount)
        except Exception as exc:
            self.retry(countdown=(BASE_COUNTDOWN ** self.request.retries), exc=exc)
            LOGGER.warning('Não foi possível relacionar o ECM entre Agenda e Pasta: %d-%s\n%s',
                           ecm.id,
                           ecm,
                           exc,
                           exc_info=(type(exc), exc, exc.__traceback__))
            raise exc


@shared_task(bind=True, max_retries=MAX_RETRIES)
def export_ecm_finished_task(self, ecm_id):
    ecm = Ecm.objects.get(pk=ecm_id)
    id_codigo_or = get_folder_to_related(task=ecm.task)
    stmt = """
           INSERT INTO Jurid_gedlig (id_tabela_or, id_codigo_or, id_id_or, Id_id_doc)
           SELECT 'Pastas','{id_codigo_or}', 0, id_id_doc
           FROM Jurid_gedlig 
           WHERE id_codigo_or = '{task_legacy_code}' 
              AND id_tabela_or = 'Agenda'
              AND Id_id_doc NOT IN (
                SELECT Id_id_doc 
                FROM Jurid_gedlig 
                WHERE id_codigo_or = '{id_codigo_or}' 
                AND id_tabela_or = 'Pastas'
              )  
    """.format(id_codigo_or=id_codigo_or, task_legacy_code=ecm.task.legacy_code)
    result = None
    try:
        result = get_advwin_engine().execute(stmt)
        return '{} Registros afetados'.format(result.rowcount)
    except Exception as exc:
        self.retry(countdown=(BASE_COUNTDOWN ** self.request.retries), exc=exc)
        LOGGER.warning('Não foi possível relacionar o ECM entre Agenda e Pasta: %d-%s\n%s',
                       ecm.id,
                       ecm,
                       exc,
                       exc_info=(type(exc), exc, exc.__traceback__))
        raise exc


@shared_task(bind=True, max_retries=10)
def delete_ecm_related_folder_to_task(self, ecm_id, id_doc, task_id, ecm_create_user, execute=True):
    task = Task.objects.get(pk=task_id)
    values = {
        'Id_tabela_or': 'Pastas',
        'Id_codigo_or': get_folder_to_related(task=task),
        'Id_id_doc': id_doc,
        'id_ID_or': 0,
        'usuario_insercao': ecm_create_user
    }
    stmt = JuridGEDLig.__table__.select().where(and_(
        JuridGEDLig.__table__.c.Id_tabela_or == values['Id_tabela_or'],
        JuridGEDLig.__table__.c.Id_codigo_or == values['Id_codigo_or'],
        JuridGEDLig.__table__.c.Id_id_doc == values['Id_id_doc'],
        JuridGEDLig.__table__.c.id_ID_or == values['id_ID_or'])
    )
    if execute:
        result = None
        try:
            result = get_advwin_engine().execute(stmt)
        except Exception as exc:
            self.retry(countdown=(BASE_COUNTDOWN ** self.request.retries), exc=exc)
            LOGGER.warning('Não foi possível excluir o relacionamento do ECM entre Agenda e Pasta: %d\n%s',
                           ecm_id,
                           exc,
                           exc_info=(type(exc), exc, exc.__traceback__))
            raise exc
        for row in result:
            id_lig = row['ID_lig']
            stmt = JuridGEDLig.__table__.delete().where(JuridGedMain.__table__.c.ID_lig == id_lig)
            deleted_ecm = get_advwin_engine().execute(stmt)
        return '{} Registros afetados'.format(result.rowcount)


@shared_task(bind=True, max_retries=10)
def delete_ecm(self, ecm_id, ecm_path_name, ecm_create_user, task_legacy_code, task_id, execute=True):
    new_path = ecm_path_ezl2advwin(ecm_path_name)
    file_name = get_ecm_file_name(ecm_path_name)
    values = {
        'Tabela_OR': 'Agenda',
        'Codigo_OR': task_legacy_code,
        'Link': new_path,
        'Nome': file_name,
        'Responsavel': ecm_create_user,
        'Arq_Status': 'Guardado',
        'Arq_nick': file_name,
        'Descricao': file_name
    }
    stmt = JuridGedMain.__table__.select().where(and_(
        JuridGedMain.__table__.c.Tabela_OR == values['Tabela_OR'],
        JuridGedMain.__table__.c.Codigo_OR == values['Codigo_OR'],
        JuridGedMain.__table__.c.Link == values['Link'],
        JuridGedMain.__table__.c.Nome == values['Nome'])
    )
    if execute:
        LOGGER.debug('Excluindo ECM %d ', ecm_id)
        try:
            result = get_advwin_engine().execute(stmt)
            for row in result:
                id_doc = row['ID_doc']
                stmt = JuridGedMain.__table__.delete().where(JuridGedMain.__table__.c.ID_doc == id_doc)
                deleted_ecm = get_advwin_engine().execute(stmt)
                delete_ecm_related_folder_to_task.delay(ecm_id, id_doc, task_id, ecm_create_user)
            LOGGER.info('ECM %s: excluído', ecm_id)
            return '{} Registros afetados'.format(result.rowcount)
        except Exception as exc:
            self.retry(countdown=(BASE_COUNTDOWN ** self.request.retries), exc=exc)
            LOGGER.warning('Não foi possível excluir o ECM: %d-%s\n%s',
                           ecm_id,
                           exc,
                           exc_info=(type(exc), exc, exc.__traceback__))
            raise exc
    else:
        return stmt


def get_folder_to_related(task):
    if task.movement.law_suit.folder.legacy_code == 'REGISTRO-INVÁLIDO':
        result = None
        try:
            stmt = JuridAgendaTable.__table__.select().where(and_(
                JuridAgendaTable.__table__.c.Ident == task.legacy_code
            ))
            result = get_advwin_engine().execute(stmt).fetchone()['Pasta']
        except Exception as e:
            LOGGER.warning('Não foi l encontrar pasta para a Providencia: %d-%s\n%s',
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
            LOGGER.info('Histórico de OS %d-%d: exportado com sucesso.',
                        task_history.task.id,
                        task_history.id)
            return '{} Registros afetados'.format(result.rowcount)
        except Exception as exc:
            LOGGER.warning('Não foi possível exportar Histórico de OS: %d-%d\n%s',
                           task_history.task.id,
                           task_history.id,
                           exc,
                           exc_info=(type(exc), exc, exc.__traceback__))
            raise exc
    else:
        return stmt


@shared_task(bind=True, max_retries=10)
def export_task_history(self, task_history_id, task_history=None, execute=True, **kwargs):
    if task_history is None:
        task_history = TaskHistory.objects.get(pk=task_history_id)

    username = ''
    if task_history.create_user:
        username = task_history.create_user.username[:20]

    task = task_history.task
    person_executed_by_legacy_code = None
    person_executed_by_legal_name = None
    values = {}
    if task.get_child:
        person_executed_by_legacy_code = None
        person_executed_by_legal_name = task.get_child.office.legal_name
    elif task.person_executed_by:
        person_executed_by_legacy_code = task.person_executed_by.legacy_code
        person_executed_by_legal_name = task.person_executed_by.legal_name
    if task_history.status == TaskStatus.ACCEPTED.value:
        values = {
            'codigo_adv_correspondente': person_executed_by_legacy_code,
            'ident_agenda': task.legacy_code,
            'status': 0,
            'SubStatus': 50,
            'data_operacao': timezone.localtime(task_history.create_date),
            'justificativa': task_history.notes,
            'usuario': username,
            'descricao': 'Aceita por correspondente: {}'.format(
                person_executed_by_legal_name),
        }
    elif task_history.status == TaskStatus.DONE.value:
        values = {
            'codigo_adv_correspondente': person_executed_by_legacy_code,
            'ident_agenda': task.legacy_code,
            'status': 0,
            'SubStatus': 70,
            'data_operacao': timezone.localtime(task_history.create_date),
            'justificativa': task_history.notes,
            'usuario': username,
            'descricao': 'Cumprida por correspondente: {}'.format(
                person_executed_by_legal_name),
        }
    elif task_history.status == TaskStatus.REFUSED.value:
        values = {
            'codigo_adv_correspondente': person_executed_by_legacy_code,
            'ident_agenda': task.legacy_code,
            'status': 0,
            'SubStatus': 20,
            'data_operacao': timezone.localtime(task_history.create_date),
            'justificativa': task_history.notes,
            'usuario': username,
            'descricao': 'Recusada por correspondente: {}'.format(
                person_executed_by_legal_name),
        }
    elif task_history.status == TaskStatus.FINISHED.value:
        values = {
            'codigo_adv_correspondente': person_executed_by_legacy_code,
            'ident_agenda': task.legacy_code,
            'status': 0,
            'SubStatus': 100,
            'data_operacao': timezone.localtime(task_history.create_date),
            'justificativa': task_history.notes,
            'usuario': username,
            'descricao': 'Diligência devidamente cumprida por: {}'.format(
                person_executed_by_legal_name),
        }
    elif task_history.status == TaskStatus.RETURN.value:
        values = {
            'codigo_adv_correspondente': person_executed_by_legacy_code,
            'ident_agenda': task.legacy_code,
            'status': 0,
            'SubStatus': 80,
            'data_operacao': timezone.localtime(task_history.create_date),
            'justificativa': task_history.notes,
            'usuario': username,
            'descricao': 'Diligência delegada ao correspondente para complementação:'
        }
    elif task_history.status == TaskStatus.BLOCKEDPAYMENT.value:
        values = {
            'codigo_adv_correspondente': person_executed_by_legacy_code,
            'ident_agenda': task.legacy_code,
            'status': 0,
            'SubStatus': 90,
            'data_operacao': timezone.localtime(task_history.create_date),
            'justificativa': task_history.notes,
            'usuario': username,
            'descricao': 'Diligência não cumprida - pagamento glosado'
        }
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
                task.person_distributed_by.legal_name),
        }
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
                task.person_distributed_by.legal_name),
        }
    elif task_history.status == TaskStatus.OPEN.value:
        values = {
            'ident_agenda': task.legacy_code,
            'codigo_adv_solicitante': task.person_asked_by.legacy_code,
            'codigo_adv_origem': task.person_distributed_by.legacy_code,
            'codigo_adv_correspondente': person_executed_by_legacy_code,
            'SubStatus': 30,
            'status': 0,
            'data_operacao': timezone.localtime(task_history.create_date),
            'justificativa': task_history.notes,
            'usuario': username,
            'descricao': 'Solicitada ao correspondente ('+person_executed_by_legal_name +
                         ') por BackOffice: {}'.format(
                task.person_distributed_by.legal_name),
        }
    if values:
        try:
            ret = insert_advwin_history(task_history, values, execute)
            return ret
        except Exception as exc:
            self.retry(countdown=(BASE_COUNTDOWN ** self.request.retries), exc=exc)
            raise exc


def update_advwin_task(task, values, execute=True):
    stmt = JuridAgendaTable.__table__.update()\
        .where(JuridAgendaTable.__table__.c.Ident == task.legacy_code)\
        .values(**values)

    if execute:
        LOGGER.debug('Exportando OS %d-%s ', task.id, task)
        try:
            result = get_advwin_engine().execute(stmt)
            LOGGER.info('OS %s: exportada com  status %s', task, task.task_status)
            return '{} Registros atualizados'.format(result.rowcount)
        except Exception as exc:
            LOGGER.warning('Não foi possível exportar OS: %d-%s com status %s\n%s',
                           task.id,
                           task,
                           task.task_status,
                           exc,
                           exc_info=(type(exc), exc, exc.__traceback__))
            raise exc
    else:
        return stmt


@shared_task(bind=True, max_retries=10)
def export_task(self, task_id, task=None, execute=True):
    if task is None:
        task = Task.objects.get(pk=task_id)

    table = JuridAgendaTable.__table__
    values = {}

    if task.task_status == TaskStatus.ACCEPTED_SERVICE.value:
        values = {
            'SubStatus': 11,
            'Status': 0,
            'Advogado_or': task.person_distributed_by.legacy_code,
            'Data_backoffice': timezone.localtime(task.acceptance_service_date),
            'envio_alerta': 0,
            'Obs': get_task_observation(task, 'Aceita por Back Office:', 'acceptance_service_date'),
        }
    elif task.task_status == TaskStatus.REFUSED_SERVICE.value:
        values = {
            'SubStatus': 20,
            'Status': 1,
            'prazo_lido': 1,
            'Data_backoffice': timezone.localtime(task.refused_service_date),
            'envio_alerta': 0,
            'Obs': get_task_observation(task, 'Recusada por Back Office', 'refused_service_date'),
        }
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
    elif task.task_status == TaskStatus.OPEN.value:
        advwin_advogado = None
        if task.child.exists():
            delegated_to = task.child.latest('pk').office.legal_name
            for user in {user for user, perms in get_users_with_perms(task.child.latest('pk').office, attach_perms=True).items() if
                         'group_admin' in perms}:
                if user.person.legacy_code:
                    advwin_advogado = user.person.legacy_code
                    break
        else:
            advwin_advogado = task.person_executed_by.legacy_code
            delegated_to = task.person_executed_by.auth_user.username

        values = {
            'SubStatus': 30,
            'Advogado': advwin_advogado,
            'Advogado_or': task.person_distributed_by.legacy_code if task.person_distributed_by else None,
            'prazo_lido': 0,
            'Data_delegacao': task.delegation_date,
            'Obs': get_task_observation(task, 'Ordem de Serviço delegada para:' + delegated_to + ' por ', 'delegation_date'),
        }
    elif task.task_status == TaskStatus.ACCEPTED.value:
        values = {
            'SubStatus': 50,
            'status_correspondente': 0,
            'prazo_lido': 0,
            'envio_alerta': 0,
            'Ag_StatusExecucao': 'Em execucao',
            'Data_correspondente': timezone.localtime(task.acceptance_date),
            'Obs': get_task_observation(task, 'Ordem de serviço aceita por', 'acceptance_date'),
        }
    elif task.task_status == TaskStatus.DONE.value:
        values = {
            'SubStatus': 70,
            'Status': 2,
            'Data_Fech': timezone.localtime(task.execution_date),
            'prazo_lido': 1,
            'Prazo_Interm': 1,
            'Ag_StatusExecucao': '',
            'Data_cumprimento': timezone.localtime(task.execution_date),
            'Data_correspondente': timezone.localtime(task.acceptance_date),
            'Obs': get_task_observation(task, TaskObservation.DONE.value, 'execution_date'),
        }
    elif task.task_status == TaskStatus.REFUSED.value:
        values = {
            'SubStatus': 40,
            'status_correspondente': 1,
            'Advogado': task.person_distributed_by.legacy_code,
            'Data_correspondente': task.refused_date,
            'Obs': get_task_observation(task, 'Ordem de serviço recusada por', 'refused_date'),
        }
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
    elif task.task_status == TaskStatus.FINISHED.value:
        values = {
            'SubStatus': 100,
            'Status': 1,
            'prazo_lido': 1,
            'substatus_prazo': 3,
            'Ag_StatusExecucao': 'Em Execucao',
            'Data_confirmacao': timezone.localtime(task.finished_date),
            'Obs': get_task_observation(task, 'Diligência devidamente cumprida por',
                                        'finished_date')
        }
    if values:
        try:
            ret = update_advwin_task(task, values, execute)
            if task.task_status == TaskStatus.FINISHED.value or task.task_status == TaskStatus.BLOCKEDPAYMENT.value:
                for ecm in task.ecm_set.all():
                    if ecm.legacy_code:
                        export_ecm_finished_task.delay(ecm.pk)
            return ret
        except Exception as exc:
            self.retry(countdown=(BASE_COUNTDOWN ** self.request.retries), exc=exc)
            raise exc
