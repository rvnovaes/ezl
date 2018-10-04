from django.db.models import Avg, Q
from .models import TaskFeedback
from task.models import Task
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


def get_office_correspondent_metrics(office_correspondent):
    start_date = timezone.now() - timedelta(days=90)
    feedbacks = TaskFeedback.objects.filter(
        feedback_date__gte=start_date,
        task__child__office=office_correspondent)
    if feedbacks.exists():
        average_rating = feedbacks.aggregate(average=Avg('rating'))['average']
        rating = "{0:.2f}".format(average_rating)
    else:
        rating = None

    tasks = Task.objects.filter(
        child__isnull=False, child__office=office_correspondent).all()
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
