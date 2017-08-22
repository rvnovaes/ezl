from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string

from ezl import settings



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
