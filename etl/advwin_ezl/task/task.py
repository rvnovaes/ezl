from etl.advwin_ezl.advwin_ezl import GenericETL, validate_import

import pytz
from itertools import chain
from django.utils import timezone
from sqlalchemy import update
from core.utils import LegacySystem
from etl.advwin_ezl.factory import InvalidObjectFactory
from advwin_models.advwin import JuridAgendaTable
from ezl import settings
from lawsuit.models import Movement
from task.models import Task, TypeTask, TaskStatus, TaskHistory
from django.db.models import Q


default_justify = 'Aceita por Correspondente: %s'


def get_status_by_substatus(substatus):
    if substatus == 100:
        return TaskStatus.FINISHED
    elif substatus == 90:
        return TaskStatus.BLOCKEDPAYMENT
    elif substatus == 80:
        return TaskStatus.REFUSED
    elif substatus == 30:
        return TaskStatus.OPEN
    else:
        return TaskStatus.INVALID


class TaskETL(GenericETL):
    import_query = """

            SELECT
                a.Data_confirmacao AS blocked_or_finished_date,
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

                INNER JOIN Jurid_CodMov as cm ON
                     a.CodMov = cm.Codigo

                WHERE
                    (cm.UsarOS = 1) AND
                    ((p.Status = 'Ativa' OR p.Dt_Saida IS NULL) AND
                    ((a.prazo_lido = 0 AND a.SubStatus = 30) OR
                    (a.SubStatus = 80 AND a.Status = 0)))
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

        task_ids = chain(accepted_tasks.values_list('id', flat=True),
                         refused_tasks.values_list('id', flat=True), done_tasks.values_list('id', flat=True))

        task_history = TaskHistory.objects.filter(task_id__in=task_ids)

        accepted_tasks = map(
            lambda x: (
                update(JuridAgendaTable.__table__).values(
                    {JuridAgendaTable.SubStatus: 50, JuridAgendaTable.status_correspondente: 0,
                     JuridAgendaTable.prazo_lido: 0, JuridAgendaTable.envio_alerta: 0,
                     JuridAgendaTable.Ag_StatusExecucao: 'Em execucao',
                     JuridAgendaTable.Data_correspondente: x.acceptance_date,
                     JuridAgendaTable.Obs: cast(JuridAgendaTable.Obs,
                                                String()) + linesep + ' *** ' + task_history.filter(
                         task_id=x.id).last().notes}).where(
                    JuridAgendaTable.Ident == x.legacy_code)),
            accepted_tasks)

        done_tasks = map(
            lambda x: (
                update(JuridAgendaTable.__table__).values(
                    {JuridAgendaTable.SubStatus: 70, JuridAgendaTable.Status: 2,
                     JuridAgendaTable.Data_Fech: x.execution_date,
                     JuridAgendaTable.prazo_lido: 1, JuridAgendaTable.Prazo_Interm: 1,
                     JuridAgendaTable.Ag_StatusExecucao: '',
                     JuridAgendaTable.Data_cumprimento: x.execution_date,
                     JuridAgendaTable.Obs: cast(JuridAgendaTable.Obs,
                                                String()) + linesep + ' *** ' + task_history.filter(
                         task_id=x.id).last().notes
                     }).where(
                    JuridAgendaTable.Ident == x.legacy_code)),
            done_tasks)

        refused_tasks = map(
            lambda x: (
                update(JuridAgendaTable.__table__).values(
                    {JuridAgendaTable.SubStatus: 20, JuridAgendaTable.Status: 1,
                     JuridAgendaTable.prazo_lido: 1, JuridAgendaTable.Prazo_Interm: 1,
                     JuridAgendaTable.Data_cumprimento: x.execution_date,
                     JuridAgendaTable.Obs: cast(JuridAgendaTable.Obs,
                                                String()) + linesep + ' *** ' + task_history.filter(
                         task_id=x.id).last().notes
                     }).where(
                    JuridAgendaTable.Ident == x.legacy_code)),
            refused_tasks)

        self.export_query_set = chain(done_tasks, accepted_tasks, refused_tasks)


if __name__ == '__main__':
    TaskETL().import_data()
