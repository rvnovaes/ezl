from django.template.loader import render_to_string
import os
import copy
from ecm.models import DefaultAttachmentRule, Attachment
from task.models import *
from task.mail import SendMail
from core.utils import get_office_session
from django.db.models import Q
from django.core.files.base import ContentFile



def get_task_attachment(self, form):
    attachmentrules = DefaultAttachmentRule.objects.filter(
        Q(office=get_office_session(self.request)),
        Q(Q(type_task=form.instance.type_task) | Q(type_task=None)),
        Q(Q(person_customer=form.instance.client) | Q(person_customer=None)),
        Q(Q(state=form.instance.court_district.state) | Q(state=None)),
        Q(Q(court_district=form.instance.court_district) | Q(court_district=None)),
        Q(Q(city=(form.instance.movement.law_suit.organ.address_set.first().city if
                  form.instance.movement.law_suit.organ.address_set.first() else None)) | Q(city=None)))

    for rule in attachmentrules:
        attachments = Attachment.objects.filter(model_name='ecm.defaultattachmentrule').filter(object_id=rule.id)
        for attachment in attachments:
            obj = Ecm(path=attachment.file,
                      task=Task.objects.get(id=form.instance.id),
                      create_user_id=self.request.user.id,
                      create_date=timezone.now())
            obj.save()


def copy_ecm(ecm, task):
    file_name = os.path.basename(ecm.path.name)
    if not Ecm.objects.filter(task=task, exhibition_name=file_name):
        new_ecm = copy.copy(ecm)
        new_ecm.pk = None
        new_ecm.task = task
        new_file = ContentFile(ecm.path.read())
        new_file.name = file_name
        new_ecm.path = new_file
        new_ecm.exhibition_name = file_name
        new_ecm.save()


def task_send_mail(instance, number, project_link, short_message, custom_text, mail_list):
    mail = SendMail()
    mail.subject = 'Easy Lawyer - OS {} - {} - Prazo: {} - {}'.format(number, str(instance.type_task).title(),
                                                                      instance.final_deadline_date.strftime('%d/%m/%Y'),
                                                                      instance.task_status)
    mail.message = render_to_string('mail/base.html',
                                    {'server': project_link,
                                     'pk': instance.pk,
                                     'project_name': settings.PROJECT_NAME,
                                     'number': str(number),
                                     'short_message': short_message,
                                     'custom_text': custom_text,
                                     'task': instance
                                     })
    mail.to_mail = list(set(mail_list))
    try:
        mail.send()
    except Exception as e:
        print(e)
        print('Você tentou mandar um e-mail')