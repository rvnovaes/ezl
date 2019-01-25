from django.core.management.base import BaseCommand
from task.models import TaskStatus, Task
from advwin_models.tasks import export_task


class Command(BaseCommand):
    help = ('Exporta novamente as OS para o advwin, de acordo com o status selecionado')

    def add_arguments(self, parser):
        parser.add_argument('task_status', choices=[status.value for status in TaskStatus])

    def handle(self, *args, **options):
        task_status = options['task_status']
        tasks = Task.objects.filter(task_status=task_status, legacy_code__isnull=False)
        for task in tasks:
            export_task.delay(task.id)
        print('Total de OS exportadas: {}'.format(tasks.count()))
