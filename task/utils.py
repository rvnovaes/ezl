import copy
from django import forms
from django.template.loader import render_to_string
from ecm.models import DefaultAttachmentRule, Attachment
from financial.models import ServicePriceTable
from financial.tables import ServicePriceTableTaskTable
from task.models import *
from task.mail import SendMail
from task.rules import RuleViewTask
from core.utils import get_office_session
from core.tasks import send_mail
from django.db.models import Q, Count
from django.core.files.base import ContentFile
from django.conf import settings
from retrying import retry
import traceback


def get_task_attachment(self, form):
    attachmentrules = DefaultAttachmentRule.objects.filter(
        Q(office=get_office_session(self.request)),
        Q(Q(type_task=form.instance.type_task) | Q(type_task=None)),
        Q(Q(person_customer=form.instance.client) | Q(person_customer=None)),
        Q(Q(state=form.instance.court_district.state) | Q(state=None)),
        Q(Q(court_district=form.instance.court_district) | Q(court_district=None)),
        Q(Q(city=(form.instance.movement.law_suit.organ.address_set.first().city if
                  form.instance.movement and
                  form.instance.movement.law_suit and
                  form.instance.movement.law_suit.organ and
                  form.instance.movement.law_suit.organ.address_set.first() else None)) | Q(city=None)))

    for rule in attachmentrules:
        attachments = Attachment.objects.filter(
            model_name='ecm.defaultattachmentrule').filter(object_id=rule.id)
        for attachment in attachments:
            if os.path.isfile(attachment.file.path):
                file_name = os.path.basename(attachment.file.name)
                new_file = ContentFile(attachment.file.read())
                new_file.name = file_name
                if not Ecm.objects.filter(exhibition_name=file_name, task_id=form.instance.id):
                    obj = Ecm(path=new_file,
                              task=Task.objects.get(id=form.instance.id),
                              create_user_id=self.request.user.id,
                              create_date=timezone.now(),
                              exhibition_name=file_name
                              )
                    obj.save()


@retry(stop_max_attempt_number=4, wait_fixed=1000)
def copy_ecm(ecm, task):
    try:
        file_name = os.path.basename(ecm.path.name)
        ecm_related = ecm.ecm_related
        if not ecm_related:
            ecm_related = ecm
        if not Ecm.objects.filter(Q(task=task), Q(ecm_related=ecm_related)) \
                and not task == ecm_related.task:
            new_ecm = copy.copy(ecm)
            new_ecm.pk = None
            new_ecm.task = task
            new_file = ContentFile(ecm.path.read())
            new_file.name = file_name
            new_ecm.path = new_file
            new_ecm.exhibition_name = file_name
            new_ecm.ecm_related = ecm_related
            new_ecm.save()
    except Exception as e:
        subject = 'Erro ao copiar ECM {}'.format(ecm.id)
        body = """Erro ao copiar ECM {} para a OS {}:
        {}
        {}""".format(ecm.id, task.id, e, traceback.format_exc())
        recipients = [admin[1] for admin in settings.ADMINS]
        # Nessario converter para unicode pois o celery usa python 2.7
        body = u'{}'.format(body)
        send_mail.delay(recipients, subject, body)


def task_send_mail(instance, number, project_link, short_message, custom_text, mail_list):
    mail = SendMail()
    mail.subject = 'Easy Lawyer - OS {} - {} - Prazo: {} - {}'.format(number, str(instance.type_task).title(),
                                                                      instance.final_deadline_date.strftime(
                                                                          '%d/%m/%Y'),
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


def get_dashboard_tasks(request, office_session, checker, person):
    rule_view = RuleViewTask(request=request)
    dynamic_query = rule_view.get_dynamic_query(person, checker)
    data = Task.objects.none()
    exclude_status = []

    if not office_session:
        return data, office_session
    # NOTE: Quando o usuário é superusuário ou não possui permissão é retornado um objeto Q vazio
    if dynamic_query or checker.has_perm('group_admin', office_session):
        # filtra as OS de acordo com a pessoa (correspondente, solicitante e contratante) preenchido na OS
        if office_session:
            if not office_session.use_service:
                exclude_status.append(TaskStatus.ACCEPTED_SERVICE.value)
                exclude_status.append(TaskStatus.REFUSED_SERVICE.value)
            if not office_session.use_etl:
                exclude_status.append(TaskStatus.ERROR.value)
            data = Task.objects.filter(dynamic_query).filter(is_active=True, office_id=office_session.id).filter(
                ~Q(task_status__in=exclude_status))

    return data, exclude_status


class CorrespondentsTable(object):

    def __init__(self, task, office_session, type_task_qs=None, type_task=None):
        self.task = task
        self.office_session = office_session
        self.type_task_qs = type_task_qs
        if not type_task:
            self.type_task, self.type_task_main = self.get_type_task(task)
        else:
            self.type_task = type_task
            self.type_task_main = type_task.main_tasks

    def get_correspondents_table(self):
        task = self.task
        type_task = self.type_task
        type_task_main = self.type_task_main

        if type_task:
            court_district = task.movement.law_suit.court_district
            state = task.movement.law_suit.court_district.state
            client = task.movement.law_suit.folder.person_customer
            offices_related = task.office.offices.all()
            correspondents_table = ServicePriceTableTaskTable(
                ServicePriceTable.objects.filter(Q(Q(office=task.office) |
                                                   Q(Q(office__public_office=True), ~Q(office=task.office))),
                                                 Q(
                                                     Q(type_task=type_task) |
                                                     Q(type_task=None) |
                                                     Q(type_task__type_task_main__in=type_task_main)
                                                 ),
                                                 Q(
                                                     Q(office_correspondent__in=offices_related) |
                                                     Q(Q(office_correspondent__public_office=True),
                                                       ~Q(office_correspondent=task.office))
                                                 ),
                                                 Q(office_correspondent__is_active=True),
                                                 Q(Q(court_district=court_district) | Q(court_district=None)),
                                                 Q(Q(state=state) | Q(state=None)),
                                                 Q(Q(client=client) | Q(client=None)),
                                                 Q(is_active=True))
            )
        else:
            correspondents_table = ServicePriceTableTaskTable(ServicePriceTable.objects.none())

        return correspondents_table

    def get_type_task(self, task):
        type_task = task.type_task
        type_task_main = task.type_task.main_tasks
        if type_task.office != self.office_session:
            self.type_task_qs = TypeTask.objects.filter(office=self.office_session, type_task_main__in=type_task_main)
            if self.type_task_qs.count() == 1:
                type_task = self.type_task_qs.first()
                type_task_main = type_task.main_tasks
            else:
                type_task = None
        return type_task, type_task_main

    def get_type_task_field(self):
        if not self.type_task_qs:
            type_task_field = None
        else:
            type_task_field = forms.ModelChoiceField(
                queryset=self.type_task_qs,
                empty_label='',
                required=True,
                label=u'Selecione o tipo de serviço',
            )
            if self.type_task_qs.count() == 1:
                type_task_field.initial = self.type_task_qs.first()

        return type_task_field

    def update_type_task(self, type_task):
        self.task.type_task = type_task
        self.task.save(**{'skip_signal': True, 'skip_mail': True})
        self.type_task = type_task

        return type_task
