import logging
import datetime
from django.core.management.base import BaseCommand
from task.models import Task, TaskHistory
from django.db.models import Count


class Command(BaseCommand):
    help = ('Remove repeated history entries from TaskHistory model.')

    def handle(self, *args, **options):
        debug_logger = logging.getLogger('ezl')
        repeated_history = TaskHistory.objects.all().values('notes', 'status', 'task_id').annotate(
            total=Count('id')).order_by('task_id').filter(total__gt=1)
        remove = 0
        for history in repeated_history:
            history_detail = TaskHistory.objects.filter(task_id=history['task_id']).order_by('id')
            control_record = None
            for detail in history_detail:
                if not control_record:
                    control_record = detail
                elif control_record.task == detail.task and \
                    control_record.notes == detail.notes and \
                    control_record.status == detail.status:
                    detail.delete()
                    timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    debug_logger.info(
                        "Registro de historico removido: %s,%s,%s,%s,%s,%s" % (
                            str(detail.create_date), str(detail.notes),
                            str(detail.status), str(detail.create_user_id), str(detail.task_id),
                            timestr))
                    remove += 1

                else:
                    control_record = detail
        print('{} registros removidos'.format(remove))
