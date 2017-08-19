from django.db.models.signals import post_init, pre_save, post_save
from django.dispatch import receiver, Signal
from django.template.loader import render_to_string
from django.utils import timezone

from core.models import ContactMechanism, ContactMechanismType
from ezl import settings
from task.mail import SendMail, MailTaskSubject
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


@receiver(post_save, sender=Task)
def new_task(sender, instance, **kwargs):
    # Envia email para o correspondente na abertura da Task
    if instance.status == TaskStatus.OPEN:
        contact_mechanism = ContactMechanismType.objects.filter(name__iexact='email').first()
        if contact_mechanism:
            mails = ContactMechanism.objects.filter(contact_mechanism=contact_mechanism,
                                                person=instance.person_executed_by_id)
            mail_list = []

            for mail in mails:
                mail_list.append(mail.description)

            mail = SendMail()
            mail.subject = MailTaskSubject.subject_task_open
            mail.message = render_to_string('mail/task_open.html',
                                            {'server': settings.PROJECT_LINK, 'pk': instance.pk,
                                             'project_name': settings.PROJECT_NAME})
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
                instance.execution_date = None
                instance.refused_date = now_date

            instance.alter_date = now_date

            TaskHistory.objects.create(task=instance, create_user=instance.alter_user, status=instance.task_status,
                                       create_date=now_date, notes=instance.__notes)
            instance.__previous_status = instance.task_status

            # Envia email para o Correspondente
            if new_status is TaskStatus.RETURN or new_status is TaskStatus.BLOCKEDPAYMENT:
                if instance.person_executed_by:
                    id_email = ContactMechanismType.objects.get(name__iexact='email').id
                    mails = ContactMechanism.objects.filter(contact_mechanism_type_id=id_email,
                                                            person=instance.person_executed_by_id)
                    mail_list = []

                    for mail in mails:
                        mail_list.append(mail.description)

                    if new_status is TaskStatus.RETURN:
                        mail = SendMail()
                        mail.subject = MailTaskSubject.subject_task_return
                        mail.message = render_to_string('mail/task_return.html',
                                                        {'server': settings.PROJECT_LINK, 'pk': instance.pk,
                                                         'project_name': settings.PROJECT_NAME})
                        mail.to_mail = mail_list
                        mail.send()

                    if new_status is TaskStatus.BLOCKEDPAYMENT:
                        mail = SendMail()
                        mail.subject = MailTaskSubject.subject_task_blocked_payment
                        mail.message = render_to_string('mail/task_bocked_payment.html',
                                                        {'server': settings.PROJECT_LINK, 'pk': instance.pk,
                                                         'project_name': settings.PROJECT_NAME})
                        mail.to_mail = mail_list
                        mail.send()

            # Envia email para o Solicitante
            elif new_status is TaskStatus.DONE or new_status is TaskStatus.FINISHED:
                if instance.person_asked_by:
                    id_email = ContactMechanismType.objects.get(name__iexact='email').id
                    mails = ContactMechanism.objects.filter(contact_mechanism_type_id=id_email,
                                                            person=instance.person_asked_by_id)
                    mail_list = []

                    for mail in mails:
                        mail_list.append(mail.description)

                    if new_status is TaskStatus.DONE:
                        mail = SendMail()
                        mail.subject = MailTaskSubject.subject_task_done
                        mail.message = render_to_string('mail/task_done.html',
                                                        {'server': settings.PROJECT_LINK, 'pk': instance.pk,
                                                         'project_name': settings.PROJECT_NAME})
                        mail.to_mail = mail_list
                        mail.send()

                    if new_status is TaskStatus.FINISHED:
                        mail = SendMail()
                        mail.subject = MailTaskSubject.subject_task_finished
                        mail.message = render_to_string('mail/task_finished.html',
                                                        {'server': settings.PROJECT_LINK, 'pk': instance.pk,
                                                         'project_name': settings.PROJECT_NAME})
                        mail.to_mail = mail_list
                        mail.send()


            # Envia email para o Service
            elif new_status is TaskStatus.ACCEPTED or new_status is TaskStatus.REFUSED:

                if instance.person_distributed_by:
                    id_email = ContactMechanismType.objects.get(name__iexact='email').id
                    mails = ContactMechanism.objects.filter(contact_mechanism_type_id=id_email,
                                                            person=instance.person_distributed_by_id)
                    mail_list = []

                    for mail in mails:
                        mail_list.append(mail.description)

                    if new_status is TaskStatus.ACCEPTED:
                        mail = SendMail()
                        mail.subject = MailTaskSubject.subject_task_accepted
                        mail.message = render_to_string('mail/task_accepted.html',
                                                        {'server': settings.PROJECT_LINK, 'pk': instance.pk,
                                                         'project_name': settings.PROJECT_NAME})
                        mail.to_mail = mail_list
                        mail.send()

                    if new_status is TaskStatus.REFUSED:
                        mail = SendMail()
                        mail.subject = MailTaskSubject.subject_task_refused
                        mail.message = render_to_string('mail/task_refused.html',
                                                        {'server': settings.PROJECT_LINK, 'pk': instance.pk,
                                                         'project_name': settings.PROJECT_NAME})
                        mail.to_mail = mail_list
                        mail.send()

    except Exception as e:
        print(e)
        pass  # TODO melhorar este tratamento
