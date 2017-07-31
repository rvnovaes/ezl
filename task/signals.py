from django.db.models.signals import post_init, pre_save
from django.dispatch import receiver, Signal
from django.utils import timezone

from task.models import Task, TaskStatus, TaskHistory

send_notes_execution_date = Signal(providing_args=["notes", "instance", "execution_date"])


@receiver(post_init, sender=Task)
def load_previous_status(sender, instance, **kwargs):
    instance.__previous_status = TaskStatus(instance.task_status) if instance.task_status else TaskStatus.INVALID


@receiver(send_notes_execution_date)
def receive_notes_execution_date(notes, instance, execution_date, survey_result, **kwargs):
    instance.__notes = notes if notes else ''
    instance.execution_date = execution_date if execution_date else None
    instance.survey_result = survey_result if survey_result else None


@receiver(pre_save, sender=Task)
def change_status(sender, instance, **kwargs):
    now_date = timezone.now()
    new_status = TaskStatus(instance.task_status) or TaskStatus.INVALID
    previous_status = TaskStatus(instance.__previous_status) or TaskStatus.INVALID
    try:
        if new_status is not previous_status:
            if new_status is TaskStatus.ACCEPTED:
                instance.acceptance_date = now_date
            elif new_status is TaskStatus.REFUSED:
                instance.refused_date = now_date
            elif new_status is TaskStatus.DONE:
                instance.return_date = None
            elif new_status is TaskStatus.RETURN:
                instance.execution_date = None
                instance.refused_date = now_date

            instance.alter_date = now_date

            TaskHistory.objects.create(task=instance, create_user=instance.alter_user, status=instance.task_status,
                                       create_date=now_date, notes=instance.__notes)
            instance.__previous_status = instance.task_status
    except Exception:
        print(Exception)
        pass  # TODO melhorar este tratamento
