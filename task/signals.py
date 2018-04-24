from django.contrib.auth.models import User
from django.db.models.signals import post_init, pre_save, post_save
from django.dispatch import receiver, Signal
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Q
from advwin_models.tasks import export_ecm, export_task, export_task_history
from core.models import ContactMechanism, ContactMechanismType, Person
from django.conf import settings
from task.mail import SendMail
from task.models import Task, TaskStatus, TaskHistory, Ecm
from task.workflow import get_parent_status, get_child_status
from chat.models import Chat, UserByChat
from lawsuit.models import CourtDistrict

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
    notes = 'Nova providência' if created else getattr(instance, '__notes', '')
    user = instance.alter_user if instance.alter_user else instance.create_user
    if not getattr(instance, '_skip_signal'):
        TaskHistory.objects.create(task=instance,
                                   create_user=user,
                                   status=instance.task_status,
                                   create_date=instance.create_date, notes=notes)
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
        if new_status is TaskStatus.ACCEPTED_SERVICE:
            instance.acceptance_service_date = now_date
        if new_status is TaskStatus.REFUSED_SERVICE:
            instance.refused_service_date = now_date
        if new_status is TaskStatus.OPEN:
            instance.delegation_date = now_date
        if new_status is TaskStatus.ACCEPTED:
            instance.acceptance_date = now_date
        elif new_status is TaskStatus.REFUSED:
            instance.refused_date = now_date
        elif new_status is TaskStatus.DONE:
            instance.return_date = None
        elif new_status is TaskStatus.RETURN:
            instance.execution_date = None
            instance.return_date = now_date
        elif new_status is TaskStatus.BLOCKEDPAYMENT:
            instance.blocked_payment_date = now_date
        elif new_status is TaskStatus.FINISHED:
            instance.finished_date = now_date

        if new_status is TaskStatus.DONE and previous_status is TaskStatus.OPEN and instance.get_child:
            instance.execution_date = now_date

        instance.alter_date = now_date

        # instance.__previous_status = instance.task_status


@receiver(post_save, sender=Task)
def ezl_export_task_to_advwin(sender, instance, **kwargs):
    if not getattr(instance, '_skip_signal'):
        export_task.delay(instance.pk)


@receiver(post_save, sender=TaskHistory)
def ezl_export_taskhistory_to_advwin(sender, instance, **kwargs):
    if not getattr(instance, '_skip_signal'):
        export_task_history.delay(instance.pk)


# update parent task
@receiver(pre_save, sender=Task)
def update_status_parent_task(sender, instance, **kwargs):
    """
    Responsavel por alterar o status da OS pai, quando o status da OS filha e modificado
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    if instance.parent and not instance.task_status == TaskStatus.REQUESTED:
        instance.parent.task_status = get_parent_status(instance.status)
        instance.parent.save()


@receiver(pre_save, sender=Task)
def update_status_child_task(sender, instance, **kwargs):
    """
    Responsavel por atualizar o status da os filha se a o estatus da OS pai e modificado
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    status = get_child_status(instance.status)
    if instance.get_child and status:
        instance.child.latest('pk').task_status = status
        instance.child.latest('pk').save()


def create_or_update_user_by_chat(task, fields):
    users = []
    for field in fields:
        user = None
        if getattr(task, field):
            user = getattr(getattr(task, field), 'auth_user')
        if user:
            user, created = UserByChat.objects.get_or_create(user_by_chat=user, chat=task.chat, defaults={
                'create_user': user, 'user_by_chat': user, 'chat': task.chat
            })
            user = user.user_by_chat
        users.append(user)

@receiver(post_save, sender=Task)
def create_or_update_chat(sender, instance, created, **kwargs):
    opposing_party = ''
    if instance.movement and instance.movement.law_suit:
        opposing_party = instance.movement.law_suit.opposing_party
    state = ''
    if isinstance(instance.court_district, CourtDistrict):
        state = instance.court_district.state
    description = """
    Parte adversa: {opposing_party}, Cliente: {client},
    {court_district} - {state}, Prazo: {final_deadline_date}
    """.format(opposing_party=opposing_party, client=instance.client,
               court_district=instance.court_district, state=state,
               final_deadline_date=instance.final_deadline_date.strftime('%d/%m/%Y %H:%M'))
    label = 'task-{}'.format(instance.pk)
    title = """#{task_number} - {type_task}""".format(
                    task_number=instance.task_number, type_task=instance.type_task)
    chat, chat_created = Chat.objects.update_or_create(
        label=label, defaults={
            'create_user': instance.create_user,
            'description': description,
            'title': title,
            'back_url': '/dashboard/{}'.format(instance.pk),
        }
    )
    instance.chat = chat
    instance.chat.offices.add(instance.office)
    create_or_update_user_by_chat(instance,[
        'person_asked_by', 'person_executed_by', 'person_distributed_by'])
    if instance.parent:
        instance.chat.offices.add(instance.parent.office)
        create_or_update_user_by_chat(instance.parent, [
            'person_asked_by', 'person_executed_by', 'person_distributed_by'
        ])
    post_save.disconnect(create_or_update_chat, sender=sender)
    instance.save()
    post_save.connect(create_or_update_chat, sender=sender)
