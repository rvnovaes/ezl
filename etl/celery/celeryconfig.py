from datetime import timedelta

# Change this to your settings
BROKER_URL = 'amqp://gsnasc:mta@2017@localhost:5672/myvhost'
CELERY_RESULT_BACKEND = "db+postgresql://gsnasc:nacigi-2@localhost/gsnasc"
CELERY_RESULT_DBURI = 'postgresql://gsnasc:nacigi-2@localhost/gsnasc'
CELERY_SEND_TASK_SENT_EVENT=True

#CELERYBEAT_SCHEDULE = {
#'every-minute': {
#'task': 'tasks.add',
#'schedule': timedelta(seconds=10),
#'args': (1,2),
#},
#}
