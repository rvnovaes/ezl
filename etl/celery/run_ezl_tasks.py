from celery import Celery

app = Celery('tasks')
app.config_from_object('etl.celery.celeryconfig')
from etl.advwin_ezl import luigi_jobs


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10, run_advwin_etl.s())
    # sender.add_periodic_task(10, sub.s(6,6))
    # sender.add_periodic_task(
    #    #Qual o periodo
    #    crontab(hour=7, minute=30, day_of_week=1),
    #    run_advwin_etl.s(),
    # )


@app.task
def run_advwin_etl():
    luigi_jobs.main()


@app.task
def run_advwin_task_etl():
    luigi_jobs.export_tasks()
