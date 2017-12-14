from django.contrib.auth.models import User
from django.db.models.signals import post_init, pre_save, post_save
from django.dispatch import receiver, Signal
from django.template.loader import render_to_string
from django.utils import timezone

from advwin_models.tasks import export_ecm, export_task, export_task_history
from core.models import ContactMechanism, ContactMechanismType, Person
from django.conf import settings
from task.mail import SendMail
from task.models import Task, TaskStatus, TaskHistory, Ecm


send_notes_execution_date = Signal(providing_args=['notes', 'instance', 'execution_date'])


@receiver(post_save, sender=Ecm)
def export_ecm_path(sender, instance, created, **kwargs):
    if created and instance.legacy_code is None:
        export_ecm.delay(instance.id)


@receiver(post_init, sender=Task)
def load_previous_status(sender, instance, **kwargs):
    instance.__previous_status = \
        TaskStatus(instance.task_status) if instance.task_status else TaskStatus.INVALID


@receiver(send_notes_execution_date)
def receive_notes_execution_date(notes, instance, execution_date, survey_result, **kwargs):
    setattr(instance, '__notes', notes if notes else '')
    if execution_date and not instance.execution_date:
        instance.execution_date = execution_date
    instance.survey_result = survey_result if survey_result else None


@receiver(post_save, sender=Task)
def new_task(sender, instance, created, **kwargs):
    if created:
        TaskHistory.objects.create(task=instance,
                                   create_user=instance.create_user,
                                   status=instance.task_status,
                                   create_date=instance.create_date, notes='Nova providência')

    contact_mechanism_type = ContactMechanismType.objects.filter(name__iexact='email')
    if not contact_mechanism_type:
        return

    id_email = contact_mechanism_type[0].id

    if instance.legacy_code:
        number = instance.legacy_code
    else:
        number = instance.id

    person_to_receive = None
    custom_text = ''
    short_message = {TaskStatus.ACCEPTED: 'foi aceita', TaskStatus.BLOCKEDPAYMENT: 'foi glosada',
                     TaskStatus.DONE: 'foi cumprida', TaskStatus.FINISHED: 'foi finalizada',
                     TaskStatus.OPEN: 'foi aberta', TaskStatus.REFUSED: 'foi recusada',
                     TaskStatus.RETURN: 'foi retornada'}

    if instance.task_status in [TaskStatus.OPEN, TaskStatus.FINISHED]:
        custom_text = ' pelo(a) solicitante ' + str(instance.person_asked_by).title()
        person_to_receive = instance.person_executed_by_id
    elif instance.task_status in [TaskStatus.BLOCKEDPAYMENT, TaskStatus.RETURN]:
        custom_text = ''
        person_to_receive = instance.person_executed_by_id
    elif instance.task_status in [TaskStatus.DONE]:
        custom_text = ' pelo(a) correspondente ' + str(instance.person_executed_by).title()
        person_to_receive = instance.person_asked_by_id
    elif instance.task_status in [TaskStatus.ACCEPTED, TaskStatus.REFUSED]:
        custom_text = ' pelo(a) correspondente ' + str(instance.person_executed_by).title()
        person_to_receive = instance.person_distributed_by_id

    if person_to_receive:
        mails = ContactMechanism.objects.filter(contact_mechanism_type_id=id_email,
                                                person_id=person_to_receive)
        mail_list = []

        for mail in mails:
            mail_list.append(mail.description)

        person = Person.objects.filter(id=person_to_receive).first()
        mail_auth_user = User.objects.filter(id=person.auth_user_id).first()
        if mail_auth_user:
            mail_list.append(mail_auth_user.email)

        if hasattr(instance, '_TaskCreateView__server'):
            project_link = instance._TaskCreateView__server

        elif hasattr(instance, '_TaskUpdateView__server'):
            project_link = instance._TaskUpdateView__server

        elif hasattr(instance, '_TaskDetailView__server'):
            project_link = instance._TaskDetailView__server

        else:
            project_link = settings.PROJECT_LINK

        mail = SendMail()
        mail.subject = 'Easy Lawyer - OS '+str(number) + ' - ' + str(
            instance.type_task).title() + ' - Prazo: ' + \
            instance.final_deadline_date.strftime('%d/%m/%Y')
        mail.message = render_to_string('mail/base.html',
                                        {'server': 'http://' + project_link, 'pk': instance.pk,
                                         'project_name': settings.PROJECT_NAME,
                                         'number': str(number),
                                         'short_message': short_message[instance.status],
                                         'custom_text': custom_text,
                                         'task': instance
                                         })
        mail.to_mail = mail_list

        # TODO: tratar corretamente a excecao

        try:
            mail.send()
        except Exception as e:
            print(e)
            print('Você tentou mandar um e-mail')


@receiver(pre_save, sender=Task)
def change_status(sender, instance, **kwargs):
    now_date = timezone.now()
    new_status = TaskStatus(instance.task_status) or TaskStatus.INVALID
    previous_status = TaskStatus(instance.__previous_status) or TaskStatus.INVALID

    if new_status is not previous_status:
        if new_status is TaskStatus.ACCEPTED:
            instance.acceptance_date = now_date
        elif new_status is TaskStatus.REFUSED:
            instance.refused_date = now_date
        elif new_status is TaskStatus.DONE:
            instance.return_date = None
        elif new_status is TaskStatus.RETURN:
            instance.execution = None
            instance.return_date = now_date
        elif new_status is TaskStatus.BLOCKEDPAYMENT:
            instance.blocked_payment_date = now_date
        elif new_status is TaskStatus.FINISHED:
            instance.finished_date = now_date

        instance.alter_date = now_date

        TaskHistory.objects.create(task=instance, create_user=instance.alter_user,
                                   status=instance.task_status,
                                   create_date=now_date,
                                   notes=getattr(instance, '__notes', ''))
        instance.__previous_status = instance.task_status


@receiver(post_save, sender=Task)
def ezl_export_task_to_advwin(sender, instance, **kwargs):
    if not getattr(instance, '_called_by_etl'):
        export_task.delay(instance.pk)


@receiver(post_save, sender=TaskHistory)
def ezl_export_taskhistory_to_advwin(sender, instance, **kwargs):
    if not getattr(instance, '_called_by_etl'):
        export_task_history.delay(instance.pk)
