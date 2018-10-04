import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ezl.settings')

app = Celery('ezl')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.update(
    task_soft_time_limit=60,
    task_time_limit=90,
    worker_max_tasks_per_child=200,
    task_ignore_result=True)

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
