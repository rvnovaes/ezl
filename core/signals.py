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


def post_create_office(office):
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
    if not office.create_user.is_superuser:
        for group in {
                group
                for group, perms in get_groups_with_perms(
                    office, attach_perms=True).items()
                if 'group_admin' in perms
        }:
            office.create_user.groups.add(group)
    create_default_type_tasks(office)


def create_person(instance, sender, **kwargs):
    if not Person.objects.filter(auth_user=instance).first():
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
        post_create_office(instance)
    if created or not get_groups_with_perms(instance):
        create_permission(instance)
        if not instance.create_user.is_superuser:
            for group in {
                    group
                    for group, perms in get_groups_with_perms(
                        instance, attach_perms=True).items()
                    if 'group_admin' in perms
            }:
                instance.create_user.groups.add(group)
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
    if created and instance.i_work_alone:
        instance.office.use_etl = False
        instance.office.use_service = False
        instance.default_user.groups.add(
            Group.objects.filter(
                name='Correspondente-{}'.format(instance.office.pk)).first())
        status_to_show = [
            TaskShowStatus(
                custtom_settings_id=instance.id,
                create_user=instance.create_user,
                status_to_show=TaskStatus.OPEN,
                send_mail_template=EmailTemplate.objects.filter(
                    template_id='d-a9f3606fb333406c9b907fee244e30a4').first()),
            TaskShowStatus(
                custtom_settings_id=instance.id,
                create_user=instance.create_user,
                status_to_show=TaskStatus.RETURN),
            TaskShowStatus(
                custtom_settings_id=instance.id,
                create_user=instance.create_user,
                status_to_show=TaskStatus.REFUSED),
            TaskShowStatus(
                custtom_settings_id=instance.id,
                create_user=instance.create_user,
                status_to_show=TaskStatus.ACCEPTED,
                send_mail_template=EmailTemplate.objects.filter(
                    template_id='d-ae35cc53722345eaa4a4adf521c3bd81').first()),
            TaskShowStatus(
                custtom_settings_id=instance.id,
                create_user=instance.create_user,
                status_to_show=TaskStatus.FINISHED,
                send_mail_template=EmailTemplate.objects.filter(
                    template_id='d-7af22ba0396943729cdcb87e2e9f787c').first()),
        ]
        instance.task_status_show.bulk_create(status_to_show)
        task_workflows = [
            TaskWorkflow(
                custtom_settings_id=instance.id,
                create_user=instance.create_user,
                task_from=TaskStatus.REQUESTED,
                task_to=TaskStatus.ACCEPTED_SERVICE,
                responsible_user=instance.default_user),
            TaskWorkflow(
                custtom_settings_id=instance.id,
                create_user=instance.create_user,
                task_from=TaskStatus.ACCEPTED_SERVICE,
                task_to=TaskStatus.OPEN,
                responsible_user=instance.default_user),
        ]
        instance.task_workflows.bulk_create(task_workflows)
        instance.save()
