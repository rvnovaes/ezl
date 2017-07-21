from django.utils import timezone

from core.models import Person
from core.utils import LegacySystem
from etl.advwin_ezl.advwin_ezl import GenericETL
from etl.advwin_ezl.factory import InvalidObjectFactory
from lawsuit.models import Movement
from task.models import Task, TypeTask, TaskStatus


class TaskETL(GenericETL):
    query = "SELECT TOP 1000" \
            "a.SubStatus AS status_code_advwin, " \
            "a.ident AS legacy_code, " \
            "a.Mov AS movement_legacy_code, " \
            "a.Advogado_sol AS person_asked_by_legacy_code, " \
            "a.Advogado AS person_executed_by_legacy_code, " \
            "a.CodMov AS type_task_legacy_code, " \
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
            "((a.prazo_lido = 0 AND a.SubStatus = 30) OR (a.SubStatus = 80 AND a.Status = 0)) " \
            "ORDER BY a.ident DESC "
    # "and a.Data BETWEEN '2017-07-18 00:00' and '2017-07-19 23:59:59'"
    model = Task
    advwin_table = 'Jurid_agenda_table'
    has_status = False

    def load_etl(self, rows, user, rows_count):
        for row in rows:
            print(rows_count, 'type_task:', row['type_task_legacy_code'])
            rows_count -= 1

            legacy_code = row['legacy_code']
            movement_legacy_code = row['movement_legacy_code']
            person_asked_by_legacy_code = row['person_asked_by_legacy_code']
            person_executed_by_legacy_code = row['person_executed_by_legacy_code']
            type_task_legacy_code = row['type_task_legacy_code']
            delegation_date = timezone.make_aware(row['delegation_date'], timezone.get_current_timezone()) if row[
                'delegation_date'] else None
            status_code_advwin = row['status_code_advwin']
            reminder_deadline_date = timezone.make_aware(row['reminder_deadline_date'],
                                                         timezone.get_current_timezone()) if row[
                'reminder_deadline_date'] else None
            final_deadline_date = timezone.make_aware(row['final_deadline_date'], timezone.get_current_timezone()) if \
                row['final_deadline_date'] else None

            description = row['description']

            task = Task.objects.filter(legacy_code=legacy_code, system_prefix=LegacySystem.ADVWIN.value).first()

            movement = Movement.objects.filter(
                legacy_code=movement_legacy_code).first() or InvalidObjectFactory.get_invalid_model(
                Movement)
            person_asked_by = Person.objects.filter(
                legacy_code=person_asked_by_legacy_code).first() or InvalidObjectFactory.get_invalid_model(Person)
            person_executed_by = Person.objects.filter(
                legacy_code=person_executed_by_legacy_code).first() or InvalidObjectFactory.get_invalid_model(Person)
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

                update_fields = ['delegation_date', 'reminder_deadline_date', 'final_deadline_date', 'description',
                                 'task_status']
                if status_code_advwin == 80:
                    task.refused_date = timezone.now()
                    task.execution_date = None
                    task.task_status = TaskStatus.REFUSED
                    update_fields.append('refused_date')
                    update_fields.append('execution_date')
                elif status_code_advwin == 30:
                    task.task_status = TaskStatus.OPEN
                    task.save(update_fields=update_fields)
            else:
                self.model.objects.create(movement=movement,
                                          legacy_code=legacy_code,
                                          system_prefix=LegacySystem.ADVWIN.value,
                                          create_user=user,
                                          alter_user=user,
                                          person_asked_by=person_asked_by,
                                          person_executed_by=person_executed_by,
                                          type_task=type_task,
                                          delegation_date=delegation_date,
                                          reminder_deadline_date=reminder_deadline_date,
                                          final_deadline_date=final_deadline_date,
                                          description=description,
                                          task_status=TaskStatus.OPEN)
        super(TaskETL, self).load_etl(rows, user, rows_count)


if __name__ == '__main__':
    TaskETL().import_data()
