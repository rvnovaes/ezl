from itertools import chain
from os import linesep
import pytz
from django.db.models import Q
from sqlalchemy import update, cast, String, insert
from advwin_models.advwin import JuridAgendaTable, JuridCorrespondenteHist, JuridFMAudienciaCorrespondente, \
    JuridFMAlvaraCorrespondente, JuridFMProtocoloCorrespondente, JuridFMDiligenciaCorrespondente
from core.utils import LegacySystem
from etl.advwin_ezl.advwin_ezl import GenericETL, validate_import
from etl.advwin_ezl.factory import InvalidObjectFactory
from etl.utils import get_message_log_default, save_error_log, get_clients_to_import
from ezl import settings
from lawsuit.models import Movement, Folder, CourtDistrict
from task.models import Task, TypeTask, TaskStatus, TaskHistory
from etl.utils import get_message_log_default, save_error_log
from etl.models import InconsistencyETL, Inconsistencies

default_justify = 'Aceita por Correspondente: %s'

"'Função para converter uma instância de um objeto sqlachemy para dicionário, utilizada na inserção do survey result'"


def to_dict(model_instance, query_instance=None):
    if hasattr(model_instance, '__table__'):
        return {
            c.name: str(
                getattr(model_instance, c.
                        name) if getattr(model_instance, c.name) else '')
            for c in model_instance.__table__.columns if c.name is not 'id'
        }
    else:
        cols = query_instance.column_descriptions
        return {cols[i]['name']: model_instance[i] for i in range(len(cols))}


survey_tables = {
    'Courthearing': JuridFMAudienciaCorrespondente,
    'Diligence': JuridFMDiligenciaCorrespondente,
    'Protocol': JuridFMProtocoloCorrespondente,
    'Operationlicense': JuridFMAlvaraCorrespondente
}


def get_status_by_substatus(substatus):
    if substatus == 100:
        return TaskStatus.FINISHED
    elif substatus == 90:
        return TaskStatus.BLOCKEDPAYMENT
    elif substatus == 80:
        return TaskStatus.RETURN
    elif substatus == 30:
        return TaskStatus.OPEN
    elif substatus == 10:
        return TaskStatus.REQUESTED
    elif substatus == 11:
        return TaskStatus.ACCEPTED_SERVICE
    elif substatus == 20:
        return TaskStatus.REFUSED_SERVICE
    else:
        return TaskStatus.INVALID


class TaskETL(GenericETL):
    _import_query = """
            SELECT
                a.Status,
                a.SubStatus AS status_code_advwin,
                a.ident AS legacy_code,
                a.Mov AS movement_legacy_code,
                a.Advogado_sol AS person_asked_by_legacy_code,
                a.Advogado AS person_executed_by_legacy_code,
                a.CodMov AS type_task_legacy_code,
                a.OBS AS description,
                a.Data AS requested_date,
                CASE WHEN (a.prazo_fatal IS NULL)
                    THEN a.Data_Prazo
                  ELSE a.prazo_fatal END AS final_deadline_date,
                p.Codigo_Comp AS folder_legacy_code,
                p.Cliente
                FROM Jurid_agenda_table AS a
                INNER JOIN Jurid_Pastas AS p ON
                    a.Pasta = p.Codigo_Comp
                INNER JOIN Jurid_CodMov AS cm ON
                     a.CodMov = cm.Codigo
                WHERE
                    cm.UsarOS = 1 AND
                    a.Status = '0' AND -- STATUS ATIVO
                    (p.Status = 'Ativa' OR p.Status = 'Especial') AND
                    (a.SubStatus = 10 OR a.SubStatus = 11) AND
                    p.Cliente IN ('{cliente}')
    """
    model = Task
    advwin_table = 'Jurid_agenda_table'
    advwin_model = JuridAgendaTable
    has_status = False

    @property
    def import_query(self):
        return self._import_query.format(
            cliente="','".join(get_clients_to_import()))

    @validate_import
    def config_import(self, rows, user, rows_count, default_office, log=False):
        from core.models import Person
        invalid_court_district = InvalidObjectFactory.get_invalid_model(CourtDistrict)
        for row in rows:
            rows_count -= 1
            try:
                legacy_code = row['legacy_code']
                movement_legacy_code = row['movement_legacy_code']
                person_asked_by_legacy_code = row[
                    'person_asked_by_legacy_code']
                person_executed_by_legacy_code = row[
                    'person_executed_by_legacy_code']
                type_task_legacy_code = row['type_task_legacy_code']

                status_code_advwin = get_status_by_substatus(
                    row['status_code_advwin'])

                if row['final_deadline_date']:
                    final_deadline_date = pytz.timezone(
                        settings.TIME_ZONE).localize(
                            row['final_deadline_date'])
                else:
                    final_deadline_date = None

                if row['requested_date']:
                    requested_date = pytz.timezone(
                        settings.TIME_ZONE).localize(row['requested_date'])
                else:
                    requested_date = None

                description = row['description']

                task = Task.objects.filter(
                    legacy_code=legacy_code,
                    legacy_code__isnull=False,
                    office=default_office,
                    system_prefix=LegacySystem.ADVWIN.value).first()

                movement = Movement.objects.filter(
                    legacy_code=movement_legacy_code,
                    legacy_code__isnull=False,
                    office=default_office,
                    system_prefix=LegacySystem.ADVWIN.value).first(
                    ) or InvalidObjectFactory.get_invalid_model(Movement)

                person_asked_by = Person.objects.filter(
                    legacy_code=person_asked_by_legacy_code,
                    legacy_code__isnull=False,
                    offices=default_office,
                    system_prefix=LegacySystem.ADVWIN.value).first(
                    ) or InvalidObjectFactory.get_invalid_model(Person)

                person_executed_by = Person.objects.filter(
                    legacy_code=person_executed_by_legacy_code,
                    legacy_code__isnull=False,
                    offices=default_office,
                    system_prefix=LegacySystem.ADVWIN.value).first(
                    ) or InvalidObjectFactory.get_invalid_model(Person)

                type_task = TypeTask.objects.filter(
                    legacy_code=type_task_legacy_code).first(
                    ) or InvalidObjectFactory.get_invalid_model(TypeTask)

                # É necessário fazer com que as datas abaixo sejam nula, senão na execução da ETL
                # será originado erro de variável sem valor
                refused_date = execution_date = blocked_payment_date = finished_date = acceptance_service_date = refused_service_date = None

                inconsistencies = []
                folder_legacy_code = row['folder_legacy_code']
                client = row['Cliente']
                performance_place = 'Local de cumprimento indefinido'
                if movement.id == 1:
                    status_code_advwin = TaskStatus.ERROR
                    inconsistencies.append({
                        "inconsistency":
                        Inconsistencies.TASKLESSMOVEMENT,
                        "solution":
                        Inconsistencies.get_solution(
                            Inconsistencies.TASKLESSMOVEMENT)
                    })
                if not Folder.objects.filter(
                        legacy_code=folder_legacy_code,
                        legacy_code__isnull=False,
                        person_customer__legacy_code=client,
                        office=default_office,
                        system_prefix=LegacySystem.ADVWIN.value).first():

                    status_code_advwin = TaskStatus.ERROR
                    inconsistencies.append({
                        "inconsistency":
                        Inconsistencies.TASKINATIVEFOLDER,
                        "solution":
                        Inconsistencies.get_solution(
                            Inconsistencies.TASKINATIVEFOLDER)
                    })
                if movement.id != 1 and movement.folder.id == 1:
                    status_code_advwin = TaskStatus.ERROR
                    inconsistencies.append({
                        "inconsistency":
                        Inconsistencies.TASKINATIVEFOLDER,
                        "solution":
                        Inconsistencies.get_solution(
                            Inconsistencies.TASKINATIVEFOLDER)
                    })

                if movement.id != 1 and movement.law_suit.id == 1:
                    status_code_advwin = TaskStatus.ERROR
                    inconsistencies.append({
                        "inconsistency":
                        Inconsistencies.MOVEMENTLESSPROCESS,
                        "solution":
                        Inconsistencies.get_solution(
                            Inconsistencies.MOVEMENTLESSPROCESS)
                    })

                if movement.id != 1 and movement.law_suit.id != 1:
                    if not (movement.law_suit.court_district or
                            movement.law_suit.city or movement.law_suit.court_district_complement):
                        status_code_advwin = TaskStatus.ERROR
                        inconsistencies.append({
                            "inconsistency":
                                Inconsistencies.BLANKCOURTDISTRICT,
                            "solution":
                                Inconsistencies.get_solution(
                                    Inconsistencies.BLANKCOURTDISTRICT)
                        })
                    if movement.law_suit.court_district == invalid_court_district:
                        status_code_advwin = TaskStatus.ERROR
                        inconsistencies.append({
                            "inconsistency":
                                Inconsistencies.INVALIDCOURTDISTRICT,
                            "solution":
                                Inconsistencies.get_solution(
                                    Inconsistencies.INVALIDCOURTDISTRICT)
                        })
                    else:
                        if movement.law_suit.court_district_complement:
                            performance_place = movement.law_suit.court_district_complement.name
                        elif movement.law_suit.city:
                            performance_place = movement.law_suit.city.name
                        else:
                            performance_place = movement.law_suit.court_district.name

                if task:
                    task.requested_date = requested_date
                    task.final_deadline_date = final_deadline_date
                    task.description = description
                    task.type_task = type_task
                    task.alter_user = user
                    task.person_asked_by = person_asked_by
                    task.type_task = type_task
                    task.refused_date = refused_date
                    task.execution_date = execution_date
                    task.blocked_payment_date = blocked_payment_date
                    task.finished_date = finished_date
                    task.requested_date = requested_date
                    task.movement = movement
                    task.performance_place = performance_place
                    if task.task_status == TaskStatus.ERROR.value and status_code_advwin != TaskStatus.ERROR:
                        task.task_status = status_code_advwin
                    elif status_code_advwin == TaskStatus.ERROR:
                        task.task_status = status_code_advwin

                    update_fields = [
                        'requested_date', 'final_deadline_date', 'description', 'task_status', 'alter_user',
                        'person_asked_by', 'type_task', 'refused_date', 'execution_date', 'blocked_payment_date',
                        'finished_date', 'requested_date', 'movement', 'performance_place'
                    ]

                    task.save(update_fields=update_fields, skip_signal=True)

                else:
                    task = Task()
                    task.movement = movement
                    task.legacy_code = legacy_code
                    task.system_prefix = LegacySystem.ADVWIN.value
                    task.create_user = user
                    task.alter_user = user
                    task.person_asked_by = person_asked_by
                    task.person_executed_by = person_executed_by
                    task.type_task = type_task
                    task.final_deadline_date = final_deadline_date
                    task.description = description
                    task.refused_date = refused_date
                    task.execution_date = execution_date
                    task.blocked_payment_date = blocked_payment_date
                    task.finished_date = finished_date
                    task.task_status = status_code_advwin
                    task.requested_date = requested_date
                    task.office = default_office
                    task.performance_place = performance_place
                    task.save(skip_signal=True)

                if status_code_advwin == TaskStatus.ERROR:
                    for inconsistency in inconsistencies:
                        InconsistencyETL.objects.get_or_create(
                            task=task,
                            inconsistency=inconsistency['inconsistency'],
                            solution=inconsistency['solution'],
                            create_user=user,
                            alter_user=user,
                            office=default_office)
                else:
                    InconsistencyETL.objects.filter(task=task).update(
                        is_active=False)

                self.debug_logger.debug(
                    "Task,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s"
                    % (str(movement.id), str(legacy_code),
                       str(LegacySystem.ADVWIN.value), str(user.id),
                       str(user.id), str(person_asked_by.id),
                       str(person_executed_by.id), str(type_task.id),
                       str(final_deadline_date), str(description),
                       str(refused_date), str(execution_date),
                       str(blocked_payment_date), str(finished_date),
                       str(status_code_advwin), self.timestr))

            except Exception as e:
                msg = get_message_log_default(self.model._meta.verbose_name,
                                              rows_count, e, self.timestr)
                self.error_logger.error(msg)
                save_error_log(log, user, msg)

    def config_export(self):
        accepted_tasks = self.model.objects.filter(
            legacy_code__isnull=False, task_status=TaskStatus.ACCEPTED)

        done_tasks = self.model.objects.filter(
            legacy_code__isnull=False, task_status=TaskStatus.DONE)

        refused_tasks = self.model.objects.filter(
            legacy_code__isnull=False, task_status=TaskStatus.REFUSED)

        accepted_service_tasks = self.model.objects.filter(
            legacy_code__isnull=False, task_status=TaskStatus.ACCEPTED_SERVICE)

        refused_service_tasks = self.model.objects.filter(
            legacy_code__isnull=False, task_status=TaskStatus.REFUSED_SERVICE)

        survey_result = done_tasks.filter(
            Q(survey_result__isnull=False) & ~Q(survey_result=''))

        # survey_result = map(lambda x: (
        #     insert(survey_tables.get(x.type_task.survey_type).__table__).values(to_dict(
        #         survey_tables.get(x.type_task.survey_type)(**parse_survey_result(x.survey_result, x.legacy_code))))
        # ), survey_result)

        accepeted_history = TaskHistory.objects.filter(
            task_id__in=accepted_tasks.values('id'),
            status=TaskStatus.ACCEPTED.value)

        done_history = TaskHistory.objects.filter(
            task_id__in=done_tasks.values('id'), status=TaskStatus.DONE.value)

        refused_history = TaskHistory.objects.filter(
            task_id__in=refused_tasks.values('id'),
            status=TaskStatus.REFUSED.value)

        accepted_service_history = TaskHistory.objects.filter(
            task_id__in=accepted_service_tasks.values('id'),
            status=TaskStatus.ACCEPTED_SERVICE.value)

        refused_service_history = TaskHistory.objects.filter(
            task_id__in=refused_service_tasks.values('id'),
            status=TaskStatus.REFUSED_SERVICE.value)

        accepted_tasks_query = map(
            lambda x: (
                update(JuridAgendaTable.__table__).values(
                    {JuridAgendaTable.SubStatus: 50, JuridAgendaTable.status_correspondente: 0,
                     JuridAgendaTable.prazo_lido: 0, JuridAgendaTable.envio_alerta: 0,
                     JuridAgendaTable.Ag_StatusExecucao: 'Em execucao',
                     JuridAgendaTable.Data_correspondente: x.acceptance_date,
                     JuridAgendaTable.Obs: cast(JuridAgendaTable.Obs,
                                                String()) + linesep + ' *** Ordem de serviço aceita por ' +
                                           str(x.person_executed_by) + ': ' + x.taskhistory_set.filter(
                         status=TaskStatus.ACCEPTED.value).last().notes + (
                                               ' em ' + x.acceptance_date.strftime(
                                                   '%d/%m/%Y') if x.acceptance_date else '')
                     }).where(JuridAgendaTable.Ident == x.legacy_code)), accepted_tasks)

        done_tasks_query = map(
            lambda x: (
                update(JuridAgendaTable.__table__).values(
                    {JuridAgendaTable.SubStatus: 70, JuridAgendaTable.Status: 2,
                     JuridAgendaTable.Data_Fech: x.execution_date,
                     JuridAgendaTable.prazo_lido: 1, JuridAgendaTable.Prazo_Interm: 1,
                     JuridAgendaTable.Ag_StatusExecucao: '',
                     JuridAgendaTable.Data_cumprimento: x.execution_date,
                     JuridAgendaTable.Obs: cast(JuridAgendaTable.Obs,
                                                String()) + linesep + ' *** Ordem de serviço cumprida por ' +
                                           str(x.person_executed_by) + ': ' + x.taskhistory_set.filter(
                         status=TaskStatus.DONE.value).last().notes +
                                           (' em ' + x.execution_date.strftime('%d/%m/%Y') if x.execution_date else '')
                     }).where(JuridAgendaTable.Ident == x.legacy_code)), done_tasks)

        refused_tasks_query = map(
            lambda x: (
                update(JuridAgendaTable.__table__).values(
                    {JuridAgendaTable.SubStatus: 20, JuridAgendaTable.Status: 1,
                     JuridAgendaTable.prazo_lido: 1, JuridAgendaTable.Prazo_Interm: 1,
                     JuridAgendaTable.Data_correspondente: x.refused_date,
                     JuridAgendaTable.Obs: cast(JuridAgendaTable.Obs,
                                                String()) + linesep + ' *** Ordem de serviço recusada por ' +
                                           str(x.person_executed_by) + ': ' + x.taskhistory_set.filter(
                         status=TaskStatus.REFUSED.value).last().notes + (
                                               ' em ' + x.refused_date.strftime('%d/%m/%Y') if x.refused_date else '')
                     }).where(JuridAgendaTable.Ident == x.legacy_code)), refused_tasks)

        accepted_service_tasks_query = map(
            lambda x: (
                update(JuridAgendaTable.__table__).values(
                    {JuridAgendaTable.SubStatus: 11, JuridAgendaTable.Status: 0,
                     JuridAgendaTable.Data_backoffice: x.acceptance_service_date,
                     JuridAgendaTable.Obs: cast(JuridAgendaTable.Obs,
                                                String()) + linesep + ' Aceita por Back Office ' +
                                           str(x.person_distributed_by) + ': ' + x.taskhistory_set.filter(
                         status=TaskStatus.ACCEPTED_SERVICE.value).last().notes + (
                                               ' em ' + x.acceptance_service_date.strftime(
                                                   '%d/%m/%Y') if x.acceptance_service_date else '')
                     }).where(JuridAgendaTable.Ident == x.legacy_code)), refused_service_tasks)

        refused_service_tasks_query = map(
            lambda x: (
                update(JuridAgendaTable.__table__).values(
                    {JuridAgendaTable.SubStatus: 20, JuridAgendaTable.Status: 1,
                     JuridAgendaTable.prazo_lido: 1,
                     JuridAgendaTable.Data_backoffice: x.refused_service_date,
                     JuridAgendaTable.Obs: cast(JuridAgendaTable.Obs,
                                                String()) + linesep + ' Recusada por Back Office ' +
                                           str(x.person_distributed_by) + ': ' + x.taskhistory_set.filter(
                         status=TaskStatus.ACCEPTED_SERVICE.value).last().notes + (
                                               ' em ' + x.acceptance_service_date.strftime(
                                                   '%d/%m/%Y') if x.acceptance_service_date else '')
                     }).where(JuridAgendaTable.Ident == x.legacy_code)), accepted_service_tasks)

        accepeted_history_query = map(lambda x: (
            insert(JuridCorrespondenteHist.__table__).values(
                {JuridCorrespondenteHist.codigo_adv_correspondente: str(x.create_user),
                 JuridCorrespondenteHist.ident_agenda: x.task.legacy_code,
                 JuridCorrespondenteHist.status: 0,
                 JuridCorrespondenteHist.SubStatus: 50,
                 JuridCorrespondenteHist.data_operacao: x.create_date,
                 JuridCorrespondenteHist.justificativa: x.notes,
                 JuridCorrespondenteHist.usuario: x.task.person_executed_by.auth_user.username,
                 JuridCorrespondenteHist.descricao: 'Aceita por correspondente: ' +
                                                    x.task.person_executed_by.legal_name})), accepeted_history)

        done_history_query = map(lambda x: (
            insert(JuridCorrespondenteHist.__table__).values(
                {JuridCorrespondenteHist.codigo_adv_correspondente: str(x.create_user),
                 JuridCorrespondenteHist.ident_agenda: x.task.legacy_code,
                 JuridCorrespondenteHist.status: 0,
                 JuridCorrespondenteHist.SubStatus: 70,
                 JuridCorrespondenteHist.data_operacao: x.create_date,
                 JuridCorrespondenteHist.justificativa: x.notes,
                 JuridCorrespondenteHist.usuario: x.task.person_executed_by.auth_user.username,
                 JuridCorrespondenteHist.descricao: 'Cumprida por correspondente: ' +
                                                    x.task.person_executed_by.legal_name})), done_history)

        refused_history_query = map(lambda x: (
            insert(JuridCorrespondenteHist.__table__).values(
                {JuridCorrespondenteHist.codigo_adv_correspondente: str(x.create_user),
                 JuridCorrespondenteHist.ident_agenda: x.task.legacy_code,
                 JuridCorrespondenteHist.status: 1,
                 JuridCorrespondenteHist.SubStatus: 20,
                 JuridCorrespondenteHist.data_operacao: x.create_date,
                 JuridCorrespondenteHist.justificativa: x.notes,
                 JuridCorrespondenteHist.usuario: x.task.person_executed_by.auth_user.username,
                 JuridCorrespondenteHist.descricao: 'Recusada por correspondente: ' +
                                                    x.task.person_executed_by.legal_name})), refused_history)

        accepted_service_history_query = map(lambda x: (
            insert(JuridCorrespondenteHist.__table__).values(
                {JuridCorrespondenteHist.codigo_adv_solicitante: str(x.person_asked_by),
                 JuridCorrespondenteHist.codigo_adv_origem: str(x.person_distributed_by),
                 JuridCorrespondenteHist.ident_agenda: x.task.legacy_code,
                 JuridCorrespondenteHist.status: 0,
                 JuridCorrespondenteHist.SubStatus: 11,
                 JuridCorrespondenteHist.data_operacao: x.create_date,
                 JuridCorrespondenteHist.justificativa: x.notes,
                 JuridCorrespondenteHist.usuario: x.task.person_executed_by.auth_user.username,
                 JuridCorrespondenteHist.descricao: 'Aceita por Back Office: ' +
                                                    x.task.person_executed_by.legal_name})), accepted_service_history)

        refused_service_history_query = map(lambda x: (
            insert(JuridCorrespondenteHist.__table__).values(
                {JuridCorrespondenteHist.codigo_adv_solicitante: str(x.person_asked_by),
                 JuridCorrespondenteHist.codigo_adv_origem: str(x.person_distributed_by),
                 JuridCorrespondenteHist.ident_agenda: x.task.legacy_code,
                 JuridCorrespondenteHist.status: 1,
                 JuridCorrespondenteHist.SubStatus: 20,
                 JuridCorrespondenteHist.data_operacao: x.create_date,
                 JuridCorrespondenteHist.justificativa: x.notes,
                 JuridCorrespondenteHist.usuario: x.task.person_executed_by.auth_user.username,
                 JuridCorrespondenteHist.descricao: 'Recusada por Back Office: ' +
                                                    x.task.person_executed_by.legal_name})), refused_service_history)

        self.export_query_set = chain(
            accepted_tasks_query, done_tasks_query, refused_tasks_query,
            accepted_service_tasks_query, refused_service_tasks_query,
            accepeted_history_query, done_history_query, refused_history_query,
            survey_result, accepted_service_history_query,
            refused_service_history_query)


if __name__ == '__main__':
    TaskETL().import_data()
