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
from task.models import TaskStatus
import base64
import traceback
import logging


logger = logging.getLogger(__name__)


def to_localtime(date_time=None, format_str='%d/%m/%Y %H:%M'):
    if date_time:
        return localtime(date_time).strftime(format_str)
    else:
        return ''


def get_str_or_blank(obj=None):
    return str(obj) if obj else ''


class SendMail:
    subject = None
    message = None
    from_mail = settings.DEFAULT_FROM_EMAIL
    to_mail = [None]

    class Meta:
        abstract = True

    def send(self):
        msg = EmailMultiAlternatives(
            self.subject, 'teste', self.from_mail, self.to_mail)
        msg.attach_alternative(self.message, "text/html")
        msg.send()


def get_file_base64(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
        f.close()
    return base64.b64encode(data).decode()


class TaskFinishedEmail(object):
    def __init__(self, task):
        self.task = task
        self.custom_settings = CustomSettings.objects.filter(office=self.task.office).first()

    def get_url_change_password(self):
        token_generator = default_token_generator
        temp_key = token_generator.make_token(self.custom_settings.default_user)
        path = reverse("account_reset_password_from_key",
                       kwargs=dict(uidb36=user_pk_to_url_str(self.custom_settings.default_user),
                                   key=temp_key))
        return '{}{}'.format(settings.WORKFLOW_URL_EMAIL, path)

    def get_dynamic_template_data(self):
        if not self.custom_settings.default_user.last_login:
            return {
                "task_number": self.task.task_number,
                "office_correspondent_name": self.task.parent.office.legal_name,
                "username": self.custom_settings.default_user.username,
                "btn_finished": self.get_url_change_password(),
            }
        return False


class TaskOpenMailTemplate(object):
    def __init__(self, task):
        self.task = task

    def get_dynamic_template_data(self):
        return {
            "task_number": self.task.task_number,
            "description": get_str_or_blank(self.task.description),
            "final_deadline_date": to_localtime(self.task.final_deadline_date, '%d/%m/%Y %H:%M'),
            "opposing_party": get_str_or_blank(self.task.opposing_party),
            "delegation_date": to_localtime(self.task.delegation_date, '%d/%m/%Y %H:%M'),
            "court_division": get_str_or_blank(self.task.court_division),
            "organ": get_str_or_blank(self.task.movement.law_suit.organ),
            "address": get_str_or_blank(self.task.address),
            "lawsuit_number": get_str_or_blank(self.task.lawsuit_number),
            "client": get_str_or_blank(self.task.client),
            "state": get_str_or_blank(self.task.movement.law_suit.court_district.state),
            "court_district": get_str_or_blank(self.task.movement.law_suit.court_district),
            "office_name": get_str_or_blank(self.task.parent.office.legal_name),
            "office_phone": get_str_or_blank(self.task.parent.office.contactmechanism_set.filter(
                contact_mechanism_type=PHONE).first()),
            "office_email": get_str_or_blank(self.task.parent.office.contactmechanism_set.filter(
                contact_mechanism_type=EMAIL).first()),
            "office_address": get_str_or_blank(self.task.parent.office.address_set.first()),
            "office_correspondent_name": self.task.office.legal_name,
            "office_correspondent_phone": get_str_or_blank(self.task.office.contactmechanism_set.filter(
                contact_mechanism_type=PHONE).first()),
            "office_correspondent_email": get_str_or_blank(self.task.office.contactmechanism_set.filter(
                contact_mechanism_type=EMAIL).first()),
            "office_correspondent_address": get_str_or_blank(self.task.parent.office.address_set.first()),
            "task_url": "{}/providencias/external-task-detail/{}/".format(settings.WORKFLOW_URL_EMAIL,
                                                                          self.task.task_hash.hex),
            "btn_accpeted": "{}/providencias/external-task/ACCEPTED/{}/".format(settings.WORKFLOW_URL_EMAIL,
                                                                                self.task.task_hash.hex),
            "btn_refused": "{}/providencias/external-task/REFUSED/{}/".format(settings.WORKFLOW_URL_EMAIL,
                                                                              self.task.task_hash.hex)
        }


class TaskAcceptedMailTemplate(object):
    def __init__(self, task):
        self.task = task

    def get_dynamic_template_data(self):
        return {
            "task_number": self.task.task_number,
            "office_name": self.task.parent.office.legal_name,
            "btn_done": "{}/providencias/external-task/FINISHED/{}/".format(settings.WORKFLOW_URL_EMAIL,
                                                                            self.task.task_hash.hex),
            "task_url": "{}/providencias/external-task-detail/{}/".format(settings.WORKFLOW_URL_EMAIL,
                                                                          self.task.task_hash.hex),
        }


class TaskMail(object):
    def __init__(self, email, task, template_id):
        self.sg = sendgrid.SendGridAPIClient(
            apikey='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')
        self.task = task
        self.email = email
        self.template_id = template_id
        self.email_status = {
            TaskStatus.ACCEPTED: TaskAcceptedMailTemplate,
            TaskStatus.OPEN: TaskOpenMailTemplate,
            TaskStatus.FINISHED: TaskFinishedEmail,
        }
        self.template_class = self.email_status.get(self.task.status)(task)
        self.attachments = []
        self.dynamic_template_data = self.template_class.get_dynamic_template_data()
        for ecm in self.task.parent.ecm_set.all():
            try:
                self.attachments.append(self.set_mail_attachment(ecm))
            except:
                pass
        self.data = {
            "personalizations": [
                {
                    "to": [
                        {
                            "email": self.email
                        }
                    ],
                    "subject": "Sending with SendGrid is Fun",
                    "dynamic_template_data": self.dynamic_template_data
                }
            ],
            "from": {
                "email": "contato@ezlawyer.com.br"
            },
            "template_id": self.template_id,
        }

        if self.attachments:
            self.data['attachments'] = self.attachments

    def set_mail_attachment(self, ecm):
        attachment = {
            "content": get_file_base64(str(ecm.path.file)),
            "type": "application/pdf",
            "filename": ecm.filename,
            "disposition": "attachment"
        }
        return attachment

    def send_mail(self):
        if self.dynamic_template_data:
            try:
                response = self.sg.client.mail.send.post(request_body=self.data)
                logging.info('Status do E-MAIL: {}'.format(response.status_code))
                logging.info('Body do E-MAIL: {}'.format(response.body))
                logging.info('Header do E-MAIL: {}'.format(response.headers))
            except Exception as e:
                logging.error(traceback.format_exc())
