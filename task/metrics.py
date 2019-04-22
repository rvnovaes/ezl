from django.db.models import Avg, Q
from .models import TaskFeedback
from task.models import Task, TaskStatus
from django.utils import timezone
from datetime import timedelta


def get_correspondent_metrics(correspondent):
    start_date = timezone.now() - timedelta(days=90)
    feedbacks = TaskFeedback.objects.filter(
        feedback_date__gte=start_date, task__person_executed_by=correspondent)
    if feedbacks.exists():
        average_rating = feedbacks.aggregate(average=Avg('rating'))['average']
        rating = "{0:.2f}".format(average_rating)
    else:
        rating = None

    tasks = correspondent.task_executed_by.all()
    if tasks.exists():
        refused_tasks = tasks.filter(return_date__isnull=False).count()
        returned_os_rate = "{0:.2f}".format(
            refused_tasks / (tasks.count() / 100))
    else:
        returned_os_rate = None

    return {
        'rating': rating,
        'returned_os_rate': returned_os_rate,
    }


def get_office_rating(office_correspondent):
    start_date = timezone.now() - timedelta(days=90)
    feedbacks = TaskFeedback.objects.filter(
        feedback_date__gte=start_date,
        task__child__office=office_correspondent)
    if feedbacks.exists():
        average_rating = feedbacks.aggregate(average=Avg('rating'))['average']
        rating = "{0:.2f}".format(average_rating)
    else:
        rating = None
    return rating


def get_office_returned_os_rate(office_correspondent):
    start_date = timezone.now() - timedelta(days=90)
    tasks = Task.objects.filter(
        child__isnull=False,
        child__office=office_correspondent,
        requested_date__gte=start_date).all()
    if tasks.exists():
        refused_tasks = tasks.filter(return_date__isnull=False).count()
        returned_os_rate = "{0:.2f}".format(
            refused_tasks / (tasks.count() / 100))
    else:
        returned_os_rate = None
    return returned_os_rate


def get_office_finished_by_rate(office_correspondent, state=None, court_district=None):
    start_date = timezone.now() - timedelta(days=90)
    tasks = Task.objects.filter(
        task_status=TaskStatus.FINISHED,
        office=office_correspondent,
        finished_date__gte=start_date).all()
    if court_district:
        tasks = tasks.filter(movement__law_suit__court_district=court_district)
    elif state:
        tasks = tasks.filter(movement__law_suit__court_district__state=state)

    return tasks.count()
