from django.contrib.auth.models import User, Group
from django.conf import settings
from django.db import models
from django.db.models.signals import post_init, pre_save, post_save, post_delete

from core.models import Person, Invite, Office, OfficeMembership, CustomSettings, EmailTemplate
from django.dispatch import receiver, Signal
from task.mail import SendMail
from task.utils import create_default_type_tasks
from django.template.loader import render_to_string
from core.permissions import create_permission
from guardian.shortcuts import get_groups_with_perms
from task.models import TaskShowStatus, TaskWorkflow, TaskStatus
from core.utils import create_office_template_value, add_create_user_to_admin_group
from manager.utils import get_template_by_key, create_template_value
from manager.enums import TemplateKeys
from manager.template_values import ListTemplateValues


def create_office_setting_default_user(office):
    template = get_template_by_key(TemplateKeys.DEFAULT_USER.name)
    value = office.create_user_id
    create_template_value(template, office, value)


def create_office_setting_i_work_alone(office):
    i_work_alone = getattr(office, '_i_work_alone', False)
    template = get_template_by_key(TemplateKeys.I_WORK_ALONE.name)
    value = i_work_alone
    create_template_value(template, office, value)


def create_office_setting_default_customer(office):
    default_customer = Person.objects.filter(legal_name=office.legal_name,
                                             name=office.legal_name,
                                             is_customer=True).first()
    if not default_customer:
        default_customer, created = Person.objects.get_or_create(legal_name=office.legal_name,
                                                                 name=office.legal_name,
                                                                 is_customer=True,
                                                                 defaults={"create_user_id": office.create_user.id,
                                                                           "is_active": True})
        if created:
            OfficeMembership.objects.create(person=default_customer,
                                            office_id=office.id,
                                            create_user_id=office.create_user.id,
                                            is_active=True)

    template = get_template_by_key(TemplateKeys.DEFAULT_CUSTOMER.name)
    value = default_customer.id
    create_template_value(template, office, value)


def create_membership_and_groups(office):
    member, created = OfficeMembership.objects.get_or_create(
        person=office.create_user.person,
        office=office,
        defaults={
            'create_user': office.create_user,
            'is_active': True
        })
    if not created:
        # Caso o relacionamento esteja apenas inativo
        member.is_active = True
        member.save()
    else:
        for super_user in User.objects.filter(is_superuser=True).all():
            member, created = OfficeMembership.objects.update_or_create(
                person=super_user.person,
                office=office,
                defaults={
                    'create_user': office.create_user,
                    'is_active': True
                })
    add_create_user_to_admin_group(office)
    create_default_type_tasks(office)


def create_person(instance, sender, **kwargs):
    if not getattr(instance, 'person', None):
        Person.objects.create(
            legal_name=instance.first_name + ' ' + instance.last_name,
            name=instance.first_name + ' ' + instance.last_name,
            is_lawyer=False,
            legal_type='F',
            alter_user=instance,
            auth_user=instance,
            create_user=instance,
            is_active=True,
            is_customer=False,
            is_supplier=False,
            import_from_legacy=False,
            legacy_code='')
    else:
        person = instance.person
        person.auth_user = instance
        person.save()


@receiver(post_save, sender=Invite)
def send_invite_email(instance, sender, **kwargs):
    project_link = settings.PROJECT_LINK
    if hasattr(instance, '_InviteCreateView__host'):
        project_link = instance._InviteCreateView__host
    mail = SendMail()
    mail.subject = 'Easy Lawyer - Convite para cadastro'
    mail.message = render_to_string(
        'core/mail/base.html', {
            'server': project_link,
            'pk': instance.pk,
            'project_name': settings.PROJECT_NAME,
            'invite': instance
        })
    mail.to_mail = [instance.email]

    # TODO: tratar corretamente a excecao

    try:
        mail.send()
    except Exception as e:
        print(e)
        print('Você tentou mandar um e-mail')


models.signals.post_save.connect(
    create_person, sender=User, dispatch_uid='create_person')


@receiver(post_save, sender=Office)
def office_post_save(sender, instance, created, **kwargs):
    if created:
        create_membership_and_groups(instance)
        create_office_template_value(instance)
        create_office_setting_default_customer(instance)
        create_office_setting_i_work_alone(instance)
        create_office_setting_default_user(instance)

        # TODO: Retirar metodo a seguir depois de eliminar a relacao entre CustomSettings e TaskWorkflow e
        #  TaskStatusToShow
        CustomSettings.objects.create(
            create_user_id=instance.create_user_id,
            is_active=True
        )
    if created or not get_groups_with_perms(instance):
        create_permission(instance)
        add_create_user_to_admin_group(instance)
    else:
        for group in get_groups_with_perms(instance):
            group.name = '{}-{}'.format(group.name.split('-')[0], instance.pk)
            group.save()


@receiver(post_delete, sender=Office)
def office_post_delete(sender, instance, **kwargs):
    for group in get_groups_with_perms(instance):
        group.delete()


@receiver(post_save, sender=CustomSettings)
def custom_settings_post_save(sender, instance, created, **kwargs):
    manager = ListTemplateValues(instance.office)
    i_work_alone = manager.get_value_by_key(TemplateKeys.I_WORK_ALONE.name)
    if i_work_alone:
        status_to_show = [
            TaskShowStatus(custtom_settings_id=instance.id, create_user=instance.create_user,
                           status_to_show=TaskStatus.OPEN, send_mail_template=EmailTemplate.objects.filter(
                    template_id='d-a9f3606fb333406c9b907fee244e30a4').first(), mail_recipients=['NONE']),
            TaskShowStatus(custtom_settings_id=instance.id, create_user=instance.create_user,
                           status_to_show=TaskStatus.RETURN, mail_recipients=['NONE']),
            TaskShowStatus(custtom_settings_id=instance.id, create_user=instance.create_user,
                           status_to_show=TaskStatus.REFUSED, mail_recipients=['NONE']),
            TaskShowStatus(custtom_settings_id=instance.id, create_user=instance.create_user,
                           status_to_show=TaskStatus.ACCEPTED, send_mail_template=EmailTemplate.objects.filter(
                    template_id='d-ae35cc53722345eaa4a4adf521c3bd81').first(), mail_recipients=['NONE']),
            TaskShowStatus(custtom_settings_id=instance.id, create_user=instance.create_user,
                           status_to_show=TaskStatus.FINISHED, send_mail_template=EmailTemplate.objects.filter(
                    template_id='d-7af22ba0396943729cdcb87e2e9f787c').first(), mail_recipients=['NONE']),
        ]
    else:
        status_to_show = [
            TaskShowStatus(custtom_settings_id=instance.id, create_user=instance.create_user,
                           status_to_show=TaskStatus.REQUESTED, mail_recipients=['NONE']),
            TaskShowStatus(custtom_settings_id=instance.id, create_user=instance.create_user,
                           status_to_show=TaskStatus.ACCEPTED_SERVICE, mail_recipients=['NONE']),
            TaskShowStatus(custtom_settings_id=instance.id, create_user=instance.create_user,
                           status_to_show=TaskStatus.OPEN, send_mail_template=EmailTemplate.objects.filter(
                    template_id='d-9233ece106b743c08074d1eb5efac1f3').first(),
                           mail_recipients=['PERSON_EXECUTED_BY', 'GET_CHILD__OFFICE']),
            TaskShowStatus(custtom_settings_id=instance.id, create_user=instance.create_user,
                           status_to_show=TaskStatus.ACCEPTED, mail_recipients=['NONE']),
            TaskShowStatus(custtom_settings_id=instance.id, create_user=instance.create_user,
                           status_to_show=TaskStatus.DONE, mail_recipients=['NONE']),
            TaskShowStatus(custtom_settings_id=instance.id, create_user=instance.create_user,
                           status_to_show=TaskStatus.RETURN, send_mail_template=EmailTemplate.objects.filter(
                    template_id='d-5c0f201b780a4b7ea6d3adfc7eae4e49').first(),
                           mail_recipients=['PERSON_EXECUTED_BY', 'PERSON_DISTRIBUTED_BY', 'GET_CHILD__OFFICE']),
            TaskShowStatus(custtom_settings_id=instance.id, create_user=instance.create_user,
                           status_to_show=TaskStatus.FINISHED, mail_recipients=['NONE']),
            TaskShowStatus(custtom_settings_id=instance.id, create_user=instance.create_user,
                           status_to_show=TaskStatus.REFUSED_SERVICE, send_mail_template=EmailTemplate.objects.filter(
                    template_id='d-a0687119152c4396894274fcf33c94bc').first(),
                           mail_recipients=['PERSON_ASKED_BY', 'PARENT__PERSON_DISTRIBUTED_BY']),
            TaskShowStatus(custtom_settings_id=instance.id, create_user=instance.create_user,
                           status_to_show=TaskStatus.REFUSED, send_mail_template=EmailTemplate.objects.filter(
                    template_id='d-f6188c1006af4193aa66f99af71d070b').first(),
                           mail_recipients=['PERSON_DISTRIBUTED_BY', 'PARENT__PERSON_DISTRIBUTED_BY']),
            TaskShowStatus(custtom_settings_id=instance.id, create_user=instance.create_user,
                           status_to_show=TaskStatus.BLOCKEDPAYMENT, mail_recipients=['NONE']),
        ]
        if instance.office.use_etl:
            status_to_show.append(TaskShowStatus(custtom_settings_id=instance.id, create_user=instance.create_user,
                                                 status_to_show=TaskStatus.ERROR), )
    if created:
        instance.task_status_show.bulk_create(status_to_show)
        if i_work_alone:
            instance.office.use_etl = False
            instance.office.use_service = False
            default_user = manager.get_value_by_key(TemplateKeys.DEFAULT_USER.name)
            default_user.groups.add(
                Group.objects.filter(
                    name='Correspondente-{}'.format(instance.office.pk)).first())
            task_workflows = [
                TaskWorkflow(
                    custtom_settings_id=instance.id,
                    create_user=instance.create_user,
                    task_from=TaskStatus.REQUESTED,
                    task_to=TaskStatus.ACCEPTED_SERVICE,
                    responsible_user=default_user),
                TaskWorkflow(
                    custtom_settings_id=instance.id,
                    create_user=instance.create_user,
                    task_from=TaskStatus.ACCEPTED_SERVICE,
                    task_to=TaskStatus.OPEN,
                    responsible_user=default_user),
            ]
            instance.task_workflows.bulk_create(task_workflows)
        instance.save()
