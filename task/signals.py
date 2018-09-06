from django.db import transaction
from django.db.models.signals import post_init, pre_save, post_save, post_delete, pre_delete
from django.dispatch import receiver, Signal
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q
from django.core.exceptions import MultipleObjectsReturned
from advwin_models.tasks import export_ecm, export_task, export_task_history, delete_ecm
from django.conf import settings
from task.models import Task, TaskStatus, TaskHistory, Ecm
from task.utils import task_send_mail, copy_ecm
from task.workflow import get_parent_status, get_child_status, get_parent_fields, get_child_recipients, \
    get_parent_recipients
from chat.models import Chat, UserByChat
from lawsuit.models import CourtDistrict
from core.utils import check_environ
from core.models import CustomSettings
from task.mail import TaskMail



send_notes_execution_date = Signal(providing_args=['notes', 'instance', 'execution_date'])


@receiver(post_save, sender=Ecm)
def export_ecm_path(sender, instance, created, **kwargs):
    if created and instance.legacy_code is None and instance.task.legacy_code:
        export_ecm.delay(instance.id,)


@receiver(post_save, sender=Ecm)
def copy_ecm_related(sender, instance, created, **kwargs):
    if created and instance.path:
        if instance.task.parent:
            transaction.on_commit(lambda: copy_ecm(instance, instance.task.parent))
        if instance.task.get_child:
            transaction.on_commit(lambda: copy_ecm(instance, instance.task.get_child))


@receiver(post_delete, sender=Ecm)
@check_environ
def delete_related_ecm(sender, instance, **kwargs):
    ecm_related = instance.ecm_related_id
    if not ecm_related:
        ecm_related = instance.pk
    if ecm_related:
        transaction.on_commit(lambda: Ecm.objects.filter(Q(pk=ecm_related)
                                                         | Q(ecm_related_id=ecm_related)).delete())


@receiver(pre_delete, sender=Ecm)
@check_environ
def delete_ecm_advwin(sender, instance, **kwargs):
    if not instance.legacy_code and instance.task.legacy_code:
        delete_ecm(instance.id)


@receiver(post_init, sender=Task)
def load_previous_status(sender, instance, **kwargs):
    instance.__previous_status = \
        TaskStatus(instance.task_status) if instance.task_status else TaskStatus.INVALID
    instance._mail_attrs = None


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
    if not getattr(instance, '_skip_signal') or created:
        task_history = TaskHistory()
        skip_signal = True if created else False
        task_history.task = instance
        task_history.create_user = user
        task_history.status = instance.task_status
        task_history.create_date = instance.create_date
        task_history.notes = notes
        task_history.save(skip_signal=skip_signal)


@receiver(pre_save, sender=Task)
def change_status(sender, instance, **kwargs):
    now_date = timezone.now()
    new_status = TaskStatus(instance.task_status) or TaskStatus.INVALID
    previous_status = TaskStatus(instance.__previous_status) or TaskStatus.INVALID

    if new_status is not previous_status:
        if new_status is TaskStatus.REQUESTED:
            instance.requested_date = now_date
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

@receiver(post_save, sender=Task)
@check_environ
def ezl_export_task_to_advwin(sender, instance, **kwargs):
    if not getattr(instance, '_skip_signal', None) and instance.legacy_code:
        export_task.delay(instance.pk)


@receiver(post_save, sender=TaskHistory)
@check_environ
def ezl_export_taskhistory_to_advwin(sender, instance, **kwargs):
    if not getattr(instance, '_skip_signal', None) and instance.task.legacy_code:
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
        if not get_parent_status(instance.status) == TaskStatus(instance.parent.__previous_status) \
                and not getattr(instance, '_from_parent'):
            instance.parent.task_status = get_parent_status(instance.status)
            if instance.parent.task_status == TaskStatus.REQUESTED:
                setattr(instance.parent, '__notes', 'O escritório {} recusou a OS {}. Motivo: {}'.format(instance.office.legal_name,
                                                                                             instance.parent.task_number, getattr(instance, '__notes', '')))
            fields = get_parent_fields(instance.status)
            for field in fields:
                setattr(instance.parent, field, getattr(instance, field)),
            instance.parent._mail_attrs = get_parent_recipients(instance.status)
            setattr(instance.parent, '_TaskDetailView__server', getattr(instance, '_TaskDetailView__server', None))
            instance.parent.save(**{'skip_signal': instance._skip_signal,
                                    'skip_mail': False})


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
    if TaskStatus(instance.task_status) == TaskStatus(instance.__previous_status):
        setattr(instance, '_skip_signal', True)
    if instance.get_child and status:
        child = instance.get_child
        if status == TaskStatus.REFUSED and instance.task_status == TaskStatus.REQUESTED:
            setattr(child, '__notes', 'A OS {} foi recusada pelo escritório contratante {} pelo motivo {}'.format(
                child.task_number, instance.office.legal_name, getattr(instance, '__notes', '')))
        child.task_status = status
        child._mail_attrs = get_child_recipients(instance.task_status)
        setattr(child, '_TaskDetailView__server', getattr(instance, '_TaskDetailView__server', None))
        child.save(** {'skip_signal': instance._skip_signal,
                       'skip_mail': False,
                       'from_parent': True})


@receiver(post_save, sender=Task)
def send_task_emails(sender, instance, created, **kwargs):
    mail_list = []

    if not getattr(instance, '_skip_mail') and instance.__previous_status != instance.task_status:
        number = '{} ({})'.format(instance.task_number, instance.legacy_code) if instance.legacy_code else str(
            instance.task_number)

        if hasattr(instance, '_TaskCreateView__server'):
            project_link = instance._TaskCreateView__server

        elif hasattr(instance, '_TaskUpdateView__server'):
            project_link = instance._TaskUpdateView__server

        elif hasattr(instance, '_TaskDetailView__server'):
            project_link = instance._TaskDetailView__server

        else:
            project_link = '{}{}'.format(settings.PROJECT_LINK, reverse('task_detail', kwargs={'pk': instance.pk}))

        """
        Caso a OS não tenha o status alterado por um signal de um parent (Pai, ou filha), ela chegará aqui sem o atributo 
        '_mail_attrs. Neste caso ela deve seguir o fluxo normal de envio de e-mails.
        """
        if not instance._mail_attrs:
            persons_to_receive = []
            custom_text = ''
            short_message_dict = {TaskStatus.REFUSED_SERVICE: 'foi recusada ',
                                  TaskStatus.REFUSED: 'foi recusada',
                                  TaskStatus.RETURN: 'foi retornada'}
            short_message = short_message_dict.get(instance.status, '')

            if instance.task_status in [TaskStatus.REFUSED_SERVICE]:
                custom_text = ' pelo(a) contratante ' + str(instance.person_distributed_by).title()
                persons_to_receive = [instance.person_asked_by]

            elif instance.task_status in [TaskStatus.REFUSED]:
                custom_text = ' pelo(a) correspondente ' + str(instance.person_executed_by).title()
                persons_to_receive = [instance.person_distributed_by]

            elif instance.task_status in [TaskStatus.RETURN]:
                custom_text = ' pelo(a) contratante ' + str(instance.person_distributed_by).title()
                persons_to_receive = [instance.office, instance.person_distributed_by]
                if instance.person_executed_by:
                    if instance.person_executed_by.emails != '':
                        persons_to_receive = [instance.person_executed_by, instance.person_distributed_by]

            persons_to_receive = [x for x in persons_to_receive if x is not None]
            for person in persons_to_receive:
                mails = person.emails.split(' | ')
                for mail in mails:
                    if mail != '':
                        mail_list.append(mail)
        else:
            mail_attrs = instance._mail_attrs
            persons_to_receive = mail_attrs.get('persons_to_receive', [])
            for person in persons_to_receive:
                recipient = getattr(instance, person, None)
                if recipient:
                    mails = recipient.emails.split(' | ')
                    for mail in mails:
                        mail_list.append(mail)
            short_message = mail_attrs.get('short_message') if mail_list else ''
            if mail_attrs.get('office') == 'parent':
                office = instance.parent.office
            elif mail_attrs.get('office') == 'child' and instance.get_child:
                office = instance.get_child.office
            else:
                office = instance.child.latest('pk').office
            custom_text = ' pelo escritório ' + office.__str__().title() if mail_list else ''

        if mail_list:
            task_send_mail(instance, number, project_link, short_message, custom_text, mail_list)

        instance.__previous_status = TaskStatus(instance.task_status)


def create_or_update_user_by_chat(task, task_to_fields, fields):    
    for field in fields:
        user = None
        if getattr(task_to_fields, field, False):
            user = getattr(getattr(task_to_fields, field), 'auth_user', False)
        if user:
            try:                            
                user, created = UserByChat.objects.get_or_create(user_by_chat=user, chat=task.chat, defaults={
                    'create_user': user, 'user_by_chat': user, 'chat': task.chat
                })
            except MultipleObjectsReturned:
                #Tratamento específico para cenário da tarefa EZL-904
                user = UserByChat.objects.filter(user_by_chat=user, chat=task.chat).first()
            user = user.user_by_chat


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
    create_or_update_user_by_chat(instance, instance, [
        'person_asked_by', 'person_executed_by', 'person_distributed_by'])
    if instance.parent:
        instance.chat.offices.add(instance.parent.office)
        create_or_update_user_by_chat(instance, instance.parent, [
            'person_asked_by', 'person_executed_by', 'person_distributed_by'
        ])
    post_save.disconnect(create_or_update_chat, sender=sender)
    instance.save(**{'skip_signal': True, 'skip_mail': True, 'from_parent': True})
    post_save.connect(create_or_update_chat, sender=sender)



@receiver(post_save, sender=Task)
def workflow_task(sender, instance, created, **kwargs):    
    custom_settings = CustomSettings.objects.filter(office=instance.office).first()
    if custom_settings:
        workflow_status = custom_settings.task_workflows.filter(
            task_from=instance.task_status).first()
        if workflow_status:            
            instance.task_status = workflow_status.task_to
            instance.person_executed_by = workflow_status.responsible_user.person
            instance.person_distributed_by = workflow_status.responsible_user.person
            post_save.disconnect(workflow_task, sender=sender)
            instance.save(**{'skip_signal': True, 'skip_mail': True})
            post_save.connect(workflow_task, sender=sender)


@receiver(post_save, sender=Task)
def workflow_send_mail(sender, instance, created, **kwargs):        
    custom_settings = CustomSettings.objects.filter(office=instance.office).first()
    if custom_settings:
        status_to_show = custom_settings.task_status_show.filter(
                    status_to_show=instance.task_status).first()    
        if status_to_show and status_to_show.send_mail_template:
            email = TaskMail(custom_settings.email_to_notification, instance, 
                status_to_show.send_mail_template.template_id)
            email.send_mail()
    


