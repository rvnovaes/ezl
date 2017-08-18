from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string

from ezl import settings


class MailTaskSubject:
    subject_task_open = "Providência: Em aberto - " + settings.PROJECT_NAME
    subject_task_accepted = "Providência: A cumprir - " + settings.PROJECT_NAME
    subject_task_refused = "Providência: Recusada - " + settings.PROJECT_NAME
    subject_task_done = "Providencia: Cumprida - " + settings.PROJECT_NAME
    subject_task_return = "Providência: Em retorno - " + settings.PROJECT_NAME
    subject_task_blocked_payment = "Providência: Glosada - " + settings.PROJECT_NAME
    subject_task_finished = "Providência: Finalizada - " + settings.PROJECT_NAME


class SendMail:
    subject = None
    message = None
    from_mail = settings.EMAIL_HOST_USER
    to_mail = [None]

    class Meta:
        abstract = True

    def send(self):
        msg = EmailMultiAlternatives(self.subject, 'teste', self.from_mail, self.to_mail)
        msg.attach_alternative(self.message, "text/html")
        msg.send()

        # send_mail(
        #     self.subject,
        #     self.from_mail,
        #     self.to_mail,
        #     html_message=True,
        #     fail_silently=False,
        # )
