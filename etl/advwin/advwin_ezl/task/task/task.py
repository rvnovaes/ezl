from django.utils import timezone

from core.models import Person
from core.utils import LegacySystem
from etl.advwin.advwin_ezl.advwin_ezl import GenericETL
from etl.advwin.advwin_ezl.factory import InvalidObjectFactory
from lawsuit.models import Movement
from task.models import Task, TypeTask, TaskStatus


class TaskETL(GenericETL):
    query = "SELECT top 10 " \
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
            "and a.Data BETWEEN '2017-07-18 00:00' and '2017-07-19 23:59:59'"
    model = Task
    advwin_table = 'Jurid_agenda_table'
    has_status = False

    # movement = models.ForeignKey(Movement, on_delete=models.PROTECT, blank=False, null=False,
    #                              verbose_name="Movimentação")
    # person_asked_by = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False,
    #                                     related_name='%(class)s_asked_by',
    #                                     verbose_name="Solicitante")
    # person_executed_by = models.ForeignKey(Person, on_delete=models.PROTECT, blank=False, null=False,
    #                                        related_name='%(class)s_executed_by',
    #                                        verbose_name="Correspondente")
    # type_task = models.ForeignKey(TypeTask, on_delete=models.PROTECT, blank=False, null=False,
    #                               verbose_name="Tipo de Serviço")
    # delegation_date = models.DateTimeField(default=timezone.now, verbose_name="Data de Delegação")
    # acceptance_date = models.DateTimeField(null=True, verbose_name="Data de Aceitação")
    # reminder_deadline_date = models.DateTimeField(null=True, verbose_name="Primeiro Prazo")
    # final_deadline_date = models.DateTimeField(null=True, verbose_name="Segundo Prazo")
    # execution_date = models.DateTimeField(null=True, verbose_name="Data de Cumprimento")
    #
    # return_date = models.DateTimeField(null=True, verbose_name="Data de Retorno")
    # refused_date = models.DateTimeField(null=True, verbose_name="Data de Recusa")
    #
    # description = models.TextField(null=True, blank=True, verbose_name=u"Descrição do serviço")
    #
    # task_status = models.CharField(null=False, verbose_name=u"", max_length=30,
    #                                choices=((x.value, x.name.title()) for x in TaskStatus),
    #                                default=TaskStatus.OPEN)
    def load_etl(self, rows, user):
        for row in rows:
            print(row)
            legacy_code = row['legacy_code']
            movement_legacy_code = row['movement_legacy_code']
            person_asked_by_legacy_code = row['person_asked_by_legacy_code']
            person_executed_by_legacy_code = row['person_executed_by_legacy_code']
            type_task_legacy_code = row['type_task_legacy_code']
            delegation_date = row['delegation_date']
            status_code_advwin = row['status_code_advwin']
            reminder_deadline_date = row['reminder_deadline_date']
            final_deadline_date = row['final_deadline_date']

            description = row['description']

            task = Task.objects.filter(legacy_code=legacy_code, system_prefix=LegacySystem.ADVWIN.value).first()

            movement = Movement.objects.filter(
                movement_legacy_code=movement_legacy_code).first() or InvalidObjectFactory.get_invalid_model(
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
                                          person_asked_by=person_asked_by,
                                          person_executed_by=person_executed_by,
                                          type_task=type_task,
                                          delegation_date=delegation_date,
                                          reminder_deadline_date=reminder_deadline_date,
                                          final_deadline_date=final_deadline_date,
                                          description=description,
                                          task_status=TaskStatus.OPEN)
        super(TaskETL, self).load_etl(rows, user)


if __name__ == '__main__':
    TaskETL().import_data()
