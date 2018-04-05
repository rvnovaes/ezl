from django.db.models import Avg
from .models import TaskFeedback
from django.utils import timezone
from datetime import timedelta


def get_correspondent_metrics(correspondent):
    start_date = timezone.now() - timedelta(days=90)
    feedbacks = TaskFeedback.objects.filter(
        feedback_date__gte=start_date,
        task__person_executed_by=correspondent
    )
    count = feedbacks.count()
    average_rating = feedbacks.aggregate(average=Avg('rating'))['average']
    return {
        'rating': "{0:.2f}".format(average_rating),
        'returned_os_rate': '2',
    }