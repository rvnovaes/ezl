from django.core.management.base import BaseCommand
from task.models import Task, TaskHistory, HistoricalTask
import logging

LOGGER = logging.getLogger('migrate_history')


# O queryset dividido para nao consumir muita memoria, devido a quantidade de dados
def batch_qs(qs, batch_size=1000):
    """
    Returns a (start, end, total, queryset) tuple for each batch in the given
    queryset.
    """
    total = qs.count()
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        yield (start, end, total, qs[start:end])


class Command(BaseCommand):
    help = ('Migra os historicos de TaskHistory para HistoricalTask')

    def handle(self, *args, **options):        
        historys = []
        history_qs = TaskHistory.objects.all()
        for start, end, total, qs in batch_qs(history_qs, batch_size=1000):
            LOGGER.info("Now processing %s - %s of %s" % (start + 1, end, total))            
            for task_history in qs:        
                history = HistoricalTask(
                    id=task_history.task.pk, history_date=task_history.create_date, history_office=task_history.task.office,
                    task_status=task_history.status, history_user=task_history.create_user,
                    history_notes=task_history.notes)
                historys.append(history)            
            HistoricalTask.objects.bulk_create(historys, batch_size=1000)
            historys.clear()
