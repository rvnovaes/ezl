from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
import sendgrid
from django.conf import settings
from datetime import datetime
from core.models import EMAIL, PHONE


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
    def __init__(self, email, task, template_id, template_class):
        self.sg = sendgrid.SendGridAPIClient(apikey='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')
        self.task = task
        self.email = email
        self.template_id = template_id
        self.template_class = template_class(task=self.task)
        self.data = {
          "personalizations": [
            {
              "to": [
                {
                  "email": self.email
                }
              ],
              "subject": "Sending with SendGrid is Fun", 
              "dynamic_template_data": self.template_class.get_dynamic_template_data()
            }
          ],
          "from": {
            "email": "mttech.ezl@gmail.com"
          },
          "template_id": self.template_id
        }

    def send_mail(self):
        response = self.sg.client.mail.send.post(request_body=self.data)
        print(response.status_code)
        print(response.body)
        print(response.headers)        


class TaskOpenMailTemplate(object):
  def __init__(self, task):
    self.task = task

  def get_dynamic_template_data(self):
    return {
      "task_number": self.task.task_number, 
      "description": self.task.description, 
      "final_deadline_date": datetime.strftime(self.task.final_deadline_date, '%d/%m/%Y %H:%M'), 
      "opposing_party": self.task.opposing_party, 
      "delegation_date": datetime.strftime(self.task.delegation_date, '%d/%m/%Y %H:%M'), 
      "court_division": str(self.task.court_division), 
      "organ": str(self.task.movement.law_suit.organ),
      "address": self.task.address, 
      "lawsuit_number": self.task.lawsuit_number, 
      "client": str(self.task.client), 
      "uf": str(self.task.movement.law_suit.court_district.state), 
      "court_district": str(self.task.movement.law_suit.court_district),  
      "office_name": self.task.parent.office.legal_name, 
      "office_phone": self.task.parent.office.contactmechanism_set.filter(contact_mechanism_type=PHONE).first(),
      "office_email": self.task.parent.office.contactmechanism_set.filter(contact_mechanism_type=EMAIL).first(),
      "office_address": self.task.parent.office.address_set.first(), 
      "office_correspondent_name": self.task.office.legal_name, 
      "office_correspondent_phone": self.task.office.contactmechanism_set.filter(contact_mechanism_type=PHONE).first(),
      "office_correspondent_email": self.task.office.contactmechanism_set.filter(contact_mechanism_type=EMAIL).first(),
      "office_correspondent_address": self.task.parent.office.address_set.first(), 
      "task_url": "http://localhost:8000/providencias/external-task/ACCEPTED/{}/".format(self.task.task_hash.hex), 
      "btn_accpeted": "http://localhost:8000/providencias/external-task/ACCEPTED/{}/".format(self.task.task_hash.hex), 
      "btn_refused": "http://localhost:8000/providencias/external-task/REFUSED/{}/".format(self.task.task_hash.hex)
    }