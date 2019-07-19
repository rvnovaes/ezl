from django.core.mail import send_mail, EmailMultiAlternatives
from django.templatetags.tz import localtime
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from allauth.account.utils import user_pk_to_url_str
from django.urls.base import reverse
import sendgrid
from sendgrid.helpers.mail import Attachment, Mail
from django.conf import settings
from datetime import datetime
from core.models import EMAIL, PHONE, CustomSettings
from task import models as task_models
import base64
import traceback
import logging
from django.utils import timezone
from manager.template_values import GetTemplateValue
from manager.enums import TemplateKeys

logger = logging.getLogger(__name__)


def to_localtime(date_time=None, format_str='%d/%m/%Y %H:%M'):
    if date_time:
        return localtime(date_time).strftime(format_str)
    else:
        return ''


def get_str_or_blank(obj=None):
    return str(obj) if obj else ''


def get_project_link(task):
    if hasattr(task, '_TaskCreateView__server'):
        project_link = task._TaskCreateView__server

    elif hasattr(task, '_TaskUpdateView__server'):
        project_link = task._TaskUpdateView__server

    elif hasattr(task, '_TaskDetailView__server'):
        project_link = task._TaskDetailView__server

    else:
        project_link = settings.PROJECT_LINK

    return project_link


class SendMail:
    subject = None
    message = None
    from_mail = settings.DEFAULT_FROM_EMAIL
    to_mail = [None]

    class Meta:
        abstract = True

    def send(self):
        msg = EmailMultiAlternatives(self.subject, 'teste', self.from_mail,
                                     self.to_mail)
        msg.attach_alternative(self.message, "text/html")
        msg.send()


class BaseTemplateEmail(object):
    def __init__(self, task, **kwargs):
        self.task = task


class TaskFinishedEmail(BaseTemplateEmail):
    def __init__(self, task, **kwargs):
        super().__init__(task, **kwargs)
        self.default_user = GetTemplateValue(office=self.task.office,
                                             template_key=TemplateKeys.DEFAULT_USER.name).value

    def get_url_change_password(self):
        token_generator = default_token_generator
        temp_key = token_generator.make_token(self.default_user)
        path = reverse(
            "account_reset_password_from_key",
            kwargs=dict(
                uidb36=user_pk_to_url_str(self.default_user),
                key=temp_key))
        return '{}{}'.format(settings.WORKFLOW_URL_EMAIL, path)

    def get_dynamic_template_data(self):
        if not self.default_user.last_login:
            return {
                "task_number": self.task.task_number,
                "type_task": self.task.type_task.name,
                "title_type_service": "OS {task_number} - {type_task} ".format(task_number=self.task.task_number,
                                                                               type_task=self.task.type_task.name),
                "office_name": self.task.parent.office.legal_name,
                "office_correspondent_name": self.task.parent.office.legal_name,
                "username": self.default_user.username,
                "btn_finished": self.get_url_change_password(),
            }
        return False


class TaskOpenMailTemplate(BaseTemplateEmail):

    def get_dynamic_template_data(self):
        task = self.task if self.task.parent else self.task.get_latest_child_not_refused
        office = self.task.parent.office if self.task.parent else self.task.office
        project_link = '{}{}'.format(get_project_link(self.task), reverse('task_detail', kwargs={'pk': task.pk}))
        return {
            "task_number": task.task_number,
            "title_type_service": "OS {task_number} - {type_task} ".format(task_number=task.task_number,
                                                                           type_task=task.type_task.name),
            "type_task": task.type_task.name,
            "description": get_str_or_blank(task.description),
            "final_deadline_date": to_localtime(task.final_deadline_date, '%d/%m/%Y %H:%M'),
            "opposing_party": get_str_or_blank(task.opposing_party),
            "delegation_date": to_localtime(task.delegation_date, '%d/%m/%Y %H:%M'),
            "court_division": get_str_or_blank(task.court_division),
            "organ": get_str_or_blank(task.movement.law_suit.organ),
            "address": get_str_or_blank(task.address),
            "lawsuit_number": get_str_or_blank(task.lawsuit_number),
            "client": get_str_or_blank(task.client),
            "state": get_str_or_blank(task.movement.law_suit.court_district.state
                                      ) if task.movement.law_suit.court_district else '',
            "court_district": get_str_or_blank(task.movement.law_suit.court_district),
            "city": get_str_or_blank(task.city),
            "court_district_complement": get_str_or_blank(task.court_district_complement),
            "performance_place": get_str_or_blank(task.performance_place),
            "office_name": get_str_or_blank(office.legal_name),
            "office_phone": get_str_or_blank(office.contactmechanism_set.filter(contact_mechanism_type=PHONE).first()),
            "office_email": get_str_or_blank(office.contactmechanism_set.filter(contact_mechanism_type=EMAIL).first()),
            "office_address": get_str_or_blank(office.address_set.first()),
            "office_correspondent_name": task.office.legal_name,
            "office_correspondent_phone": get_str_or_blank(task.office.contactmechanism_set.filter(
                contact_mechanism_type=PHONE).first()),
            "office_correspondent_email": get_str_or_blank(task.office.contactmechanism_set.filter(
                contact_mechanism_type=EMAIL).first()),
            "office_correspondent_address": get_str_or_blank(task.office.address_set.first()),
            "external_task_url": "{}/providencias/external-task-detail/{}/".format(
                settings.WORKFLOW_URL_EMAIL, self.task.task_hash.hex),
            "task_url": project_link,
            "btn_accpeted": "{}/providencias/external-task/ACCEPTED/{}/".format(
                settings.WORKFLOW_URL_EMAIL, self.task.task_hash.hex),
            "btn_refused": "{}/providencias/external-task/REFUSED/{}/".format(
                settings.WORKFLOW_URL_EMAIL, self.task.task_hash.hex)
        }


class TaskAcceptedMailTemplate(BaseTemplateEmail):

    def get_dynamic_template_data(self):
        return {
            "task_number": self.task.task_number,
            "type_task": self.task.type_task.name,
            "title_type_service": "OS {task_number} - {type_task} ".format(task_number=self.task.task_number,
                                                                           type_task=self.task.type_task.name),
            "office_name": self.task.parent.office.legal_name,
            "btn_done": "{}/providencias/external-task/FINISHED/{}/".format(
                settings.WORKFLOW_URL_EMAIL, self.task.task_hash.hex),
            "task_url": "{}/providencias/external-task-detail/{}/".format(
                settings.WORKFLOW_URL_EMAIL, self.task.task_hash.hex),
        }


class TaskRefusedServiceMailTemplate(BaseTemplateEmail):
    def __init__(self, task, **kwargs):
        super().__init__(task, **kwargs)
        self.by_person = kwargs.get('by_person')

    def get_dynamic_template_data(self):
        task_pk = self.task.pk if not self.task.parent else self.task.parent.pk
        project_link = '{}{}'.format(
            get_project_link(self.task),
            reverse('task_detail', kwargs={'pk': task_pk}))
        task_number = self.task.task_number if not self.task.parent else self.task.parent.task_number
        return {
            "task_number":
                task_number,
            "type_task":
                self.task.type_task.name,
            "title_type_service":
                "OS {task_number} - {type_task} ".format(
                    task_number=task_number,
                    type_task=self.task.type_task.name),
            "person_distributed_by":
                str(self.task.person_distributed_by).title(),
            "task_url": project_link,
            "final_deadline_date": timezone.localtime(self.task.final_deadline_date).strftime('%d/%m/%Y %H:%M'),
            "by_person": self.by_person
        }


class TaskRefusedMailTemplate(BaseTemplateEmail):
    def __init__(self, task, **kwargs):
        super().__init__(task, **kwargs)
        self.by_person = kwargs.get('by_person')
        self.task_number = kwargs.get('task_number')

    def get_dynamic_template_data(self):
        project_link = '{}{}'.format(
            get_project_link(self.task),
            reverse('task_detail', kwargs={'pk': self.task.pk}))
        # task_number = self.task.task_number if not self.task.parent else self.task.parent.task_number
        return {
            "task_number":
                self.task_number,
            "type_task":
                self.task.type_task.name,
            "title_type_service":
                "OS {task_number} - {type_task} ".format(
                    task_number=self.task_number,
                    type_task=self.task.type_task.name),
            "person_executed_by":
                str(self.task.person_executed_by).title(),
            "task_url": project_link,
            "final_deadline_date": timezone.localtime(self.task.final_deadline_date).strftime('%d/%m/%Y %H:%M'),
            "by_person": self.by_person
        }


class TaskReturnMailTemplate(object):
    def __init__(self, task, **kwargs):
        super().__init__(task, **kwargs)
        self.by_person = kwargs.get('by_person')

    def get_dynamic_template_data(self):
        project_link = '{}{}'.format(
            get_project_link(self.task),
            reverse('task_detail', kwargs={'pk': self.task.pk}))
        return {
            "task_number":
                self.task.task_number,
            "type_task":
                self.task.type_task.name,
            "title_type_service":
                "OS {task_number} - {type_task} ".format(
                    task_number=self.task.task_number,
                    type_task=self.task.type_task.name),
            "person_distributed_by":
                str(self.task.person_distributed_by).title(),
            "task_url": project_link,
            "final_deadline_date": timezone.localtime(self.task.final_deadline_date).strftime('%d/%m/%Y %H:%M'),
            "by_person": self.by_person
        }


class TaskMail(object):
    def __init__(self,
                 email,
                 task,
                 template_id,
                 by_person=None,
                 task_number=''):
        self.sg = sendgrid.SendGridAPIClient(
            apikey=settings.EMAIL_HOST_PASSWORD
        )
        self.by_person = by_person
        self.task_number = task_number
        self.task = task
        self.email = [{"email": email_address} for email_address in list(set(email))]
        self.template_id = template_id
        self.email_status = {
            task_models.TaskStatus.REQUESTED: TaskOpenMailTemplate,
            task_models.TaskStatus.REFUSED_SERVICE: TaskRefusedServiceMailTemplate,
            task_models.TaskStatus.REFUSED: TaskRefusedMailTemplate,
            task_models.TaskStatus.RETURN: TaskReturnMailTemplate,
            task_models.TaskStatus.ACCEPTED: TaskAcceptedMailTemplate,
            task_models.TaskStatus.OPEN: TaskOpenMailTemplate,
            task_models.TaskStatus.FINISHED: TaskFinishedEmail,
        }
        template_kwargs = {
            'by_person': by_person,
            'task_number': task_number
        }
        self.template_class = self.email_status.get(self.task.status)(task, **template_kwargs)
        self.attachments = self.get_task_attachments()
        self.dynamic_template_data = self.template_class.get_dynamic_template_data(
        )
        to_email = self.email
        original_recipient = None
        if settings.DEFAULT_TO_EMAIL:
            to_email = [{"email": settings.DEFAULT_TO_EMAIL}]
            original_recipient = self.email

        self.data = {
            "personalizations": [{
                "to": to_email,
                "subject":
                    "Sending template e-mail",
                "dynamic_template_data":
                    self.dynamic_template_data
            }],
            "from": {
                "email": "contato@ezlawyer.com.br"
            },
            "template_id":
                self.template_id
        }

        if original_recipient:
            self.data['mail_settings'] = {
                "footer": {
                    "enable": True,
                    "html": "<p>Destinatário(s) originais: {}".format(original_recipient)
                }
            }

        if self.attachments:
            self.data['attachments'] = self.attachments

    def get_task_attachments(self):
        task = self.task.parent if self.task.parent else self.task
        ecm_list = []

        for ecm in task.ecm_set.all():
            try:
                ecm_list.append(self.set_mail_attachment(ecm))
            except:
                pass

        return ecm_list

    def set_mail_attachment(self, ecm):
        attachment = {
            "content": base64.b64encode(ecm.path.read()).decode(),
            "type": "application/pdf",
            "filename": ecm.filename,
            "disposition": "attachment"
        }
        return attachment

    def send_mail(self):
        if self.dynamic_template_data:
            try:
                response = self.sg.client.mail.send.post(
                    request_body=self.data)
                logging.info('Status do E-MAIL: {}'.format(
                    response.status_code))
                logging.info('Body do E-MAIL: {}'.format(response.body))
                logging.info('Header do E-MAIL: {}'.format(response.headers))
            except Exception as e:
                logging.error(traceback.format_exc())


class TaskCompanyRepresentativeChangeMail(object):
    def __init__(self, email, task, template_id):
        self.sg = sendgrid.SendGridAPIClient(
            apikey=settings.EMAIL_HOST_PASSWORD
        )
        self.task = task
        self.email = [{"email": email_address} for email_address in list(set(email))]
        self.template_id = template_id
        self.dynamic_template_data = self.get_dynamic_template_data()
        to_email = self.email
        original_recipient = None
        if settings.DEFAULT_TO_EMAIL:
            to_email = [{"email": settings.DEFAULT_TO_EMAIL}]
            original_recipient = self.email
        self.data = {
            "personalizations": [{
                "to": to_email,
                "subject":
                    "Sending with SendGrid is Fun",
                "dynamic_template_data":
                    self.dynamic_template_data
            }],
            "from": {
                "email": "contato@ezlawyer.com.br"
            },
            "template_id":
                self.template_id
        }

        if original_recipient:
            self.data['mail_settings'] = {
                "footer": {
                    "enable": True,
                    "html": "<p>Destinatário(s) originais: {}".format(original_recipient)
                }
            }

    def get_dynamic_template_data(self):
        project_link = '{}{}'.format(
            get_project_link(self.task),
            reverse('task_detail', kwargs={'pk': self.task.pk}))
        return {
            "task":
                "{task_number} - {type_task} ".format(
                    task_number=self.task.task_number,
                    type_task=self.task.type_task.name),
            "task_url": project_link,
            "name": self.task.person_company_representative.legal_name
        }            

    def send_mail(self):
        if self.dynamic_template_data:
            try:
                response = self.sg.client.mail.send.post(
                    request_body=self.data)
                logging.info('Status do E-MAIL: {}'.format(
                    response.status_code))
                logging.info('Body do E-MAIL: {}'.format(response.body))
                logging.info('Header do E-MAIL: {}'.format(response.headers))
            except Exception as e:
                logging.error(traceback.format_exc())
