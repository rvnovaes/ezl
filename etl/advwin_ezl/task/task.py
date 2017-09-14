from etl.advwin_ezl.advwin_ezl import GenericETL
import pytz
from django.db.models.signals import pre_save, post_save
from itertools import chain
from django.utils import timezone
from sqlalchemy import update
from core.models import Person
from core.utils import LegacySystem
from etl.advwin_ezl.factory import InvalidObjectFactory
from advwin_models.advwin import JuridAgendaTable
from ezl import settings
from lawsuit.models import Movement
from task.models import Task, TypeTask, TaskStatus, TaskHistory
from task.signals import new_task, change_status
from django.utils.timezone import localtime

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
    import_query = "SELECT " \
                   "a.Data_confirmacao AS blocked_or_finished_date, " \
                   "a.SubStatus AS status_code_advwin, " \
                   "a.ident AS legacy_code, " \
                   "a.Mov AS movement_legacy_code, " \
                   "a.Advogado_sol AS person_asked_by_legacy_code, " \
                   "a.Advogado AS person_executed_by_legacy_code, " \
                   "a.CodMov AS type_task_legacy_code, " \
                   "a.Advogado_or AS person_distributed_by_legacy_code," \
                   "a.OBS AS description, " \
                   "CASE WHEN (a.Data_delegacao IS NULL) THEN " \
                   "a.Data ELSE a.Data_delegacao END AS delegation_date, " \
                   "a.Data_Prazo AS reminder_deadline_date, " \
                   "a.prazo_fatal AS final_deadline_date " \
                   "FROM Jurid_agenda_table AS a " \
                   "INNER JOIN Jurid_Pastas AS p ON " \
                   "a.Pasta = p.Codigo_Comp " \
                   "WHERE " \
                   "(p.Status = 'Ativa' OR p.Dt_Saida IS NULL) AND " \
                   "(a.prazo_lido = 0 AND a.SubStatus = 30) OR (a.SubStatus = 80 AND a.Status = 0) " \
                   " ORDER BY a.ident DESC "
    # "and a.Data BETWEEN '2017-07-18 00:00' and '2017-07-19 23:59:59'"
    model = Task
    advwin_table = 'Jurid_agenda_table'
    advwin_model = JuridAgendaTable
    has_status = False

    def config_import(self, rows, user, rows_count):
        for row in rows:
            print(rows_count)
            rows_count -= 1
            legacy_code = row['legacy_code']
            movement_legacy_code = row['movement_legacy_code']
            person_asked_by_legacy_code = row['person_asked_by_legacy_code']
            person_executed_by_legacy_code = row['person_executed_by_legacy_code']
            person_distributed_by_legacy_code = row['person_distributed_by_legacy_code']
            type_task_legacy_code = row['type_task_legacy_code']

            if row['delegation_date']:
                delegation_date = pytz.timezone(settings.TIME_ZONE).localize(row['delegation_date'])
            else:
                delegation_date = None

            status_code_advwin = get_status_by_substatus(row['status_code_advwin'])

            if row['reminder_deadline_date']:
                reminder_deadline_date = pytz.timezone(settings.TIME_ZONE).localize(row['reminder_deadline_date'])
            else:
                reminder_deadline_date = None

            if row['final_deadline_date']:
                final_deadline_date = pytz.timezone(settings.TIME_ZONE).localize(row['final_deadline_date'])
            else:
                final_deadline_date = None

            description = row['description']
            blocked_or_finished_date = row['blocked_or_finished_date']

            task = Task.objects.filter(legacy_code=legacy_code, system_prefix=LegacySystem.ADVWIN.value).first()

            movement = Movement.objects.filter(
                legacy_code=movement_legacy_code).first() or InvalidObjectFactory.get_invalid_model(
                Movement)
            person_asked_by = Person.objects.filter(
                legacy_code=person_asked_by_legacy_code).first() or InvalidObjectFactory.get_invalid_model(Person)
            person_executed_by = Person.objects.filter(
                legacy_code=person_executed_by_legacy_code).first() or InvalidObjectFactory.get_invalid_model(Person)
            person_distributed_by = Person.objects.filter(
                legacy_code=person_distributed_by_legacy_code).first() or InvalidObjectFactory.get_invalid_model(Person)
            type_task = TypeTask.objects.filter(
                legacy_code=type_task_legacy_code).first() or InvalidObjectFactory.get_invalid_model(TypeTask)

            # 30   Open
            # 80   returned
            # atualizar o status_task somente se for diferente de OPEN
            if task:
                task.delegation_date = delegation_date
                task.reminder_deadline_date = reminder_deadline_date
                task.final_deadline_date = final_deadline_date
                task.description = description
                task.task_status = status_code_advwin
                update_fields = ['delegation_date', 'reminder_deadline_date', 'final_deadline_date', 'description',
                                 'task_status']
                if status_code_advwin == TaskStatus.RETURN:
                    task.refused_date = timezone.now()
                    task.execution_date = None
                    update_fields.append('return_date')
                    update_fields.append('execution_date')
                elif status_code_advwin == TaskStatus.BLOCKEDPAYMENT:
                    task.blocked_payment_date = blocked_or_finished_date
                    update_fields.append('blocked_payment_date')
                elif status_code_advwin == TaskStatus.FINISHED:
                    task.finished_date = blocked_or_finished_date
                    update_fields.append('finished_date')
                elif status_code_advwin == TaskStatus.OPEN:
                    pass

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
                                          reminder_deadline_date=reminder_deadline_date,
                                          final_deadline_date=final_deadline_date,
                                          description=description,
                                          task_status=status_code_advwin)
        super(TaskETL, self).config_import(rows, user, rows_count)

    def config_export(self):
        accepted_tasks = self.model.objects.filter(legacy_code__isnull=False,
                                                   task_status=TaskStatus.ACCEPTED)

        done_tasks = self.model.objects.filter(legacy_code__isnull=False,
                                               task_status=TaskStatus.DONE)

        refused_tasks = self.model.objects.filter(legacy_code__isnull=False,
                                                  task_status=TaskStatus.REFUSED)

        accepted_tasks = map(
            lambda x: (
                update(JuridAgendaTable.__table__).values(
                    {JuridAgendaTable.SubStatus: 50, JuridAgendaTable.status_correspondente: 0,
                     JuridAgendaTable.prazo_lido: 0, JuridAgendaTable.envio_alerta: 0,
                     JuridAgendaTable.Ag_StatusExecucao: 'Em execucao',
                     JuridAgendaTable.Data_correspondente: x.acceptance_date}).where(
                    JuridAgendaTable.Ident == x.legacy_code)),
            accepted_tasks)

        task_history = TaskHistory.objects.filter()

        done_tasks = map(
            lambda x: (
                update(JuridAgendaTable.__table__).values(
                    {JuridAgendaTable.SubStatus: 70, JuridAgendaTable.Status: 2,
                     JuridAgendaTable.Data_Fech: x.execution_date,
                     JuridAgendaTable.prazo_lido: 1, JuridAgendaTable.Prazo_Interm: 1,
                     JuridAgendaTable.Ag_StatusExecucao: '',
                     JuridAgendaTable.Data_cumprimento: x.execution_date}).where(
                    JuridAgendaTable.Ident == x.legacy_code)),
            done_tasks)

        refused_tasks = map(
            lambda x: (
                update(JuridAgendaTable.__table__).values(
                    {JuridAgendaTable.SubStatus: 20, JuridAgendaTable.Status: 1,
                     JuridAgendaTable.prazo_lido: 1, JuridAgendaTable.Prazo_Interm: 1,
                     JuridAgendaTable.Data_cumprimento: x.execution_date}).where(
                    JuridAgendaTable.Ident == x.legacy_code)),
            refused_tasks)

        tasks = chain(done_tasks, accepted_tasks, refused_tasks)
        for task in tasks:
            print(task)

        self.export_query_set = tasks

if __name__ == '__main__':
    TaskETL().import_data()
