from itertools import chain
from json import loads
from os import linesep

import pytz
from django.db.models import Q
from django.utils import timezone
from sqlalchemy import update, cast, String, insert

from advwin_models.advwin import JuridAgendaTable, JuridCorrespondenteHist, JuridFMAudienciaCorrespondente, \
    JuridFMAlvaraCorrespondente, JuridFMProtocoloCorrespondente, JuridFMDiligenciaCorrespondente
from core.utils import LegacySystem
from etl.advwin_ezl.advwin_ezl import GenericETL, validate_import
from etl.advwin_ezl.factory import InvalidObjectFactory
from ezl import settings
from lawsuit.models import Movement
from task.models import Task, TypeTask, TaskStatus, TaskHistory

default_justify = 'Aceita por Correspondente: %s'

"'Função para converter uma instância de um objeto sqlachemy para dicionário, utilizada na inserção do survey result'"


def to_dict(model_instance, query_instance=None):
    if hasattr(model_instance, '__table__'):
        return {c.name: str(getattr(model_instance, c.name) if getattr(model_instance, c.name) else '') for c in
                model_instance.__table__.columns if c.name is not 'id'}
    else:
        cols = query_instance.column_descriptions
        return {cols[i]['name']: model_instance[i] for i in range(len(cols))}


def parse_survey_result(survey, agenda_id):
    json = loads(survey)
    json['agenda_id'] = agenda_id
    json['versao'] = 1
    return json


survey_tables = {'Courthearing': JuridFMAudienciaCorrespondente, 'Diligence'
: JuridFMDiligenciaCorrespondente, 'Protocol': JuridFMProtocoloCorrespondente,
                 'Operationlicense': JuridFMAlvaraCorrespondente}


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
    import_query = """

            SELECT
                a.Data_confirmacao AS blocked_or_finished_date,
                a.Status,
                a.SubStatus AS status_code_advwin,
                a.ident AS legacy_code,
                a.Mov AS movement_legacy_code,
                a.Advogado_sol AS person_asked_by_legacy_code,
                a.Advogado AS person_executed_by_legacy_code,
                a.CodMov AS type_task_legacy_code,
                a.Advogado_or AS person_distributed_by_legacy_code,
                a.OBS AS description,

                CASE WHEN (a.Data_delegacao IS NULL) THEN
                    a.Data ELSE a.Data_delegacao END AS delegation_date,
                    a.prazo_fatal AS final_deadline_date

                FROM Jurid_agenda_table AS a

                INNER JOIN Jurid_Pastas AS p ON
                    a.Pasta = p.Codigo_Comp

                INNER JOIN Jurid_CodMov AS cm ON
                     a.CodMov = cm.Codigo

                WHERE
                    (cm.UsarOS = 1) AND
                    p.Status = 'Ativa' AND
                    ((a.prazo_lido = 0 AND a.SubStatus = 30) OR
                    (a.SubStatus = 80) OR (a.SubStatus = 10) OR 
                    (a.SubStatus = 11) OR (a.SubStatus = 20)) AND a.Status = '0' -- STATUS ATIVO
                    -- AND a.Advogado IN ('12157458697', '12197627686', '13281750656', '11744024000171') -- marcio.batista, nagila e claudia (Em teste)
    """
    model = Task
    advwin_table = 'Jurid_agenda_table'
    advwin_model = JuridAgendaTable
    has_status = False

    @validate_import
    def config_import(self, rows, user, rows_count):
        from core.models import Person
        for row in rows:

            try:
                legacy_code = row['legacy_code']
                movement_legacy_code = row['movement_legacy_code']
                person_asked_by_legacy_code = row['person_asked_by_legacy_code']
                person_executed_by_legacy_code = row['person_executed_by_legacy_code']
                person_distributed_by_legacy_code = row['person_distributed_by_legacy_code']
                type_task_legacy_code = row['type_task_legacy_code']

                if row['delegation_date']:
                    delegation_date = pytz.timezone(settings.TIME_ZONE).localize(
                        row['delegation_date'])
                else:
                    delegation_date = None

                status_code_advwin = get_status_by_substatus(row['status_code_advwin'])

                if row['final_deadline_date']:
                    final_deadline_date = pytz.timezone(settings.TIME_ZONE).localize(
                        row['final_deadline_date'])
                else:
                    final_deadline_date = None

                description = row['description']
                blocked_or_finished_date = row['blocked_or_finished_date']

                task = Task.objects.filter(legacy_code=legacy_code,
                                           system_prefix=LegacySystem.ADVWIN.value).first()

                movement = Movement.objects.filter(
                    legacy_code=movement_legacy_code).first() or InvalidObjectFactory.get_invalid_model(
                    Movement)
                person_asked_by = Person.objects.filter(Q(
                    legacy_code=person_asked_by_legacy_code), ~Q(legacy_code=None),
                    ~Q(legacy_code='')).first() or InvalidObjectFactory.get_invalid_model(Person)
                person_executed_by = Person.objects.filter(
                    Q(legacy_code=person_executed_by_legacy_code), ~Q(legacy_code=None),
                    ~Q(legacy_code='')).first() or InvalidObjectFactory.get_invalid_model(Person)
                person_distributed_by = Person.objects.filter(Q(
                    legacy_code=person_distributed_by_legacy_code), ~Q(legacy_code=None),
                    ~Q(legacy_code='')).first() or InvalidObjectFactory.get_invalid_model(Person)
                type_task = TypeTask.objects.filter(
                    legacy_code=type_task_legacy_code).first() or InvalidObjectFactory.get_invalid_model(
                    TypeTask)

                # 30   Open
                # 80   Refused
                # atualizar o status_task somente se for diferente de OPEN

                # É necessário fazer com que as datas abaixo sejam nula, senão na execução da ETL
                # será originado erro de variável sem valor
                refused_date = execution_date = blocked_payment_date = finished_date = None

                if status_code_advwin == TaskStatus.REFUSED:
                    refused_date = timezone.now()
                    execution_date = None
                elif status_code_advwin == TaskStatus.BLOCKEDPAYMENT:
                    blocked_payment_date = blocked_or_finished_date
                elif status_code_advwin == TaskStatus.FINISHED:
                    finished_date = blocked_or_finished_date

                if task:
                    task.delegation_date = delegation_date
                    task.final_deadline_date = final_deadline_date
                    task.description = description
                    task.task_status = status_code_advwin
                    task.refused_date = refused_date
                    task.execution_date = execution_date
                    task.blocked_payment_date = blocked_payment_date
                    task.finished_date = finished_date

                    update_fields = ['delegation_date', 'final_deadline_date', 'description',
                                     'task_status', 'refused_date', 'execution_date',
                                     'blocked_payment_date',
                                     'finished_date']

                    task.save(update_fields=update_fields)

                else:
                    self.model.objects.create(movement=movement,
                                              legacy_code=legacy_code,
                                              system_prefix=LegacySystem.ADVWIN.value,
                                              create_user=user,
                                              alter_user=user,
                                              person_asked_by=person_asked_by,
                                              person_executed_by=person_executed_by,
                                              person_distributed_by=person_distributed_by,
                                              type_task=type_task,
                                              delegation_date=delegation_date,
                                              final_deadline_date=final_deadline_date,
                                              description=description,
                                              refused_date=refused_date,
                                              execution_date=execution_date,
                                              blocked_payment_date=blocked_payment_date,
                                              finished_date=finished_date,
                                              task_status=status_code_advwin)
                self.debug_logger.debug(
                    "Task,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (
                        str(movement.id), str(legacy_code), str(LegacySystem.ADVWIN.value),
                        str(user.id), str(user.id), str(person_asked_by.id),
                        str(person_executed_by.id), str(person_distributed_by.id),
                        str(type_task.id), str(delegation_date), str(final_deadline_date),
                        str(description), str(refused_date), str(execution_date),
                        str(blocked_payment_date), str(finished_date),
                        str(status_code_advwin), self.timestr))

            except Exception as e:
                self.error_logger.error(
                    "Ocorreu o seguinte erro na importacao de Task: " + str(rows_count) + "," + str(
                        e) + "," + self.timestr)

    def config_export(self):
        accepted_tasks = self.model.objects.filter(legacy_code__isnull=False,
                                                   task_status=TaskStatus.ACCEPTED)

        done_tasks = self.model.objects.filter(legacy_code__isnull=False,
                                               task_status=TaskStatus.DONE)

        refused_tasks = self.model.objects.filter(legacy_code__isnull=False,
                                                  task_status=TaskStatus.REFUSED)

        survey_result = done_tasks.filter(Q(survey_result__isnull=False) & ~Q(survey_result=''))

        survey_result = map(lambda x: (
            insert(survey_tables.get(x.type_task.survey_type).__table__).values(to_dict(
                survey_tables.get(x.type_task.survey_type)(**parse_survey_result(x.survey_result, x.legacy_code))))
        ), survey_result)

        accepeted_history = TaskHistory.objects.filter(task_id__in=accepted_tasks.values('id'),
                                                       status=TaskStatus.ACCEPTED.value)

        done_history = TaskHistory.objects.filter(task_id__in=done_tasks.values('id'), status=TaskStatus.DONE.value)

        refused_history = TaskHistory.objects.filter(task_id__in=refused_tasks.values('id'),
                                                     status=TaskStatus.REFUSED.value)

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
                                               ' em ' + x.refused_date.strftime('%d/%m/%Y') if x.refused_date else'')
                     }).where(JuridAgendaTable.Ident == x.legacy_code)), refused_tasks)

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

        self.export_query_set = chain(accepted_tasks_query, done_tasks_query, refused_tasks_query,
                                      accepeted_history_query,
                                      done_history_query, refused_history_query, survey_result)


if __name__ == '__main__':
    TaskETL().import_data()
