from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
import sendgrid
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


class TaskMail(object):
    def __init__(self, task):
        self.sg = sendgrid.SendGridAPIClient(apikey='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')
        self.task = task
        self.data = {
          "personalizations": [
            {
              "to": [
                {
                  "email": "thiago.ar17@gmail.com"
                }
              ],
              "subject": "Sending with SendGrid is Fun", 
              "dynamic_template_data": {
                "task": "http://localhost:8000/providencias/external-task/{}/".format(task.task_hash.hex)
              }
            }
          ],
          "from": {
            "email": "mttech.ezl@gmail.com"
          },
          "template_id": "d-a9f3606fb333406c9b907fee244e30a4"
        }

    def send_mail(self):
        response = self.sg.client.mail.send.post(request_body=self.data)
        print(response.status_code)
        print(response.body)
        print(response.headers)        