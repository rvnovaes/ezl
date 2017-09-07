from django.db.models.signals import post_init, pre_save, post_save
from django.dispatch import receiver, Signal
from django.template.loader import render_to_string
from django.utils import timezone

from core.models import ContactMechanism, ContactMechanismType
from ezl import settings
from task.mail import SendMail
from task.models import Task, TaskStatus, TaskHistory

send_notes_execution_date = Signal(providing_args=["notes", "instance", "execution_date"])


@receiver(post_init, sender=Task)
def load_previous_status(sender, instance, **kwargs):
    instance.__previous_status = TaskStatus(instance.task_status) if instance.task_status else TaskStatus.INVALID


@receiver(send_notes_execution_date)
def receive_notes_execution_date(notes, instance, execution_date, survey_result, **kwargs):
    instance.__notes = notes if notes else ''
    if execution_date and not instance.execution_date:
        instance.execution_date = execution_date
    instance.survey_result = survey_result if survey_result else None


@receiver(post_save, sender=Task)
def new_task(sender, instance, created, **kwargs):
    if created:
        TaskHistory.objects.create(task=instance, create_user=instance.create_user, status=instance.task_status,
                                   create_date=instance.create_date, notes="Nova providência")

    id_email = ContactMechanismType.objects.get(name__iexact='email').id

    if instance.legacy_code:
        number = instance.legacy_code
    else:
        number = instance.id

    # Envia email para o correspondente. Status: Em aberto, retornada e glosada
    if instance.task_status is TaskStatus.OPEN or instance.task_status is TaskStatus.RETURN or instance.task_status is TaskStatus.BLOCKEDPAYMENT:
        if instance.person_executed_by:
            mails = ContactMechanism.objects.filter(contact_mechanism_type_id=id_email,
                                                    person=instance.person_executed_by_id)
            mail_list = []

            for mail in mails:
                mail_list.append(mail.description)

            if instance.task_status is TaskStatus.OPEN:
                mail = SendMail()
                mail.subject = 'Providência ' + str(number) + ': Em aberto - ' + settings.PROJECT_NAME
                mail.message = render_to_string('mail/task_open.html',
                                                {'server': settings.PROJECT_LINK, 'pk': instance.pk,
                                                 'project_name': settings.PROJECT_NAME,
                                                 'number': str(number),
                                                 'person_asked_by': str(instance.person_asked_by).title(),
                                                 })
                mail.to_mail = mail_list
                mail.send()

            elif instance.task_status is TaskStatus.RETURN:
                mail = SendMail()
                mail.subject = 'Providência ' + str(number) + ': Em retorno - ' + settings.PROJECT_NAME
                mail.message = render_to_string('mail/task_return.html',
                                                {'server': settings.PROJECT_LINK, 'pk': instance.pk,
                                                 'project_name': settings.PROJECT_NAME,
                                                 'number': str(number)
                                                 })
                mail.to_mail = mail_list
                mail.send()

            elif instance.task_status is TaskStatus.BLOCKEDPAYMENT:
                mail = SendMail()
                mail.subject = 'Providência ' + str(number) + ': Glosada - ' + settings.PROJECT_NAME
                mail.message = render_to_string('mail/task_bocked_payment.html',
                                                {'server': settings.PROJECT_LINK, 'pk': instance.pk,
                                                 'project_name': settings.PROJECT_NAME,
                                                 'number': str(number)
                                                 })
                mail.to_mail = mail_list
                mail.send()

    # Envia email para o Solicitante. Status: Cumprida e Fechada
    elif instance.task_status is TaskStatus.DONE or instance.task_status is TaskStatus.FINISHED:
        if instance.person_asked_by:
            mails = ContactMechanism.objects.filter(contact_mechanism_type_id=id_email,
                                                    person=instance.person_asked_by_id)
            mail_list = []

            for mail in mails:
                mail_list.append(mail.description)

            if instance.task_status is TaskStatus.DONE:
                mail = SendMail()

                mail.subject = 'Providencia ' + str(number) + ': Cumprida - ' + settings.PROJECT_NAME
                mail.message = render_to_string('mail/task_done.html',
                                                {'server': settings.PROJECT_LINK, 'pk': instance.pk,
                                                 'project_name': settings.PROJECT_NAME,
                                                 'number': str(number),
                                                 'person_executed_by': str(instance.person_executed_by).title(),
                                                 })
                mail.to_mail = mail_list
                mail.send()

            if instance.task_status is TaskStatus.FINISHED:
                mail = SendMail()
                mail.subject = 'Providência' + str(number) + ': Finalizada - ' + settings.PROJECT_NAME
                mail.message = render_to_string('mail/task_finished.html',
                                                {'server': settings.PROJECT_LINK, 'pk': instance.pk,
                                                 'project_name': settings.PROJECT_NAME,
                                                 'number': str(number),
                                                 'person_executed_by': str(instance.person_executed_by).title(),
                                                 })
                mail.to_mail = mail_list
                mail.send()

    # Envia email para o Service. Status: Aceita e Recusada
    elif instance.task_status is TaskStatus.ACCEPTED or instance.task_status is TaskStatus.REFUSED:
        if instance.person_distributed_by:
            mails = ContactMechanism.objects.filter(contact_mechanism_type_id=id_email,
                                                    person=instance.person_distributed_by_id)
            mail_list = []

            for mail in mails:
                mail_list.append(mail.description)

            if instance.task_status is TaskStatus.ACCEPTED:
                mail = SendMail()
                mail.subject = 'Providência ' + str(number) + ' : A cumprir - ' + settings.PROJECT_NAME
                mail.message = render_to_string('mail/task_accepted.html',
                                                {'server': settings.PROJECT_LINK, 'pk': instance.pk,
                                                 'project_name': settings.PROJECT_NAME,
                                                 'person_executed_by': str(instance.person_executed_by).title(),
                                                 'number': str(number)
                                                 })
                mail.to_mail = mail_list
                mail.send()

            if instance.task_status is TaskStatus.REFUSED:
                mail = SendMail()
                mail.subject = 'Providência ' + str(number) + ': Recusada - ' + settings.PROJECT_NAME
                mail.message = render_to_string('mail/task_refused.html',
                                                {'server': settings.PROJECT_LINK, 'pk': instance.pk,
                                                 'project_name': settings.PROJECT_NAME,
                                                 'person_executed_by': str(instance.person_executed_by).title(),
                                                 'number': str(number)
                                                 })
                mail.to_mail = mail_list
                mail.send()


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
                instance.execution = None
                instance.return_date = now_date
            elif new_status is TaskStatus.BLOCKEDPAYMENT:
                instance.blocked_payment_date = now_date
            elif new_status is TaskStatus.FINISHED:
                instance.finished_date = now_date

            instance.alter_date = now_date

            TaskHistory.objects.create(task=instance, create_user=instance.alter_user, status=instance.task_status,
                                       create_date=now_date, notes=instance.__notes)
            instance.__previous_status = instance.task_status

    except Exception as e:
        print(e)
        pass  # TODO melhorar este tratamento
