from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string

from django.conf import settings



class SendMail:
    subject = None
    message = None
    from_mail = settings.DEFAULT_FROM_EMAIL
    to_mail = [None]

    class Meta:
        abstract = True

    def send(self):
        msg = EmailMultiAlternatives(self.subject, 'teste', self.from_mail, self.to_mail)
        msg.attach_alternative(self.message, "text/html")
        msg.send()
