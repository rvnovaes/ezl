import sendgrid
from sendgrid.helpers.mail import Attachment, Mail
from django.conf import settings
import traceback
import logging

logger = logging.getLogger(__name__)

def send_sendgrid_mail(data):    
    sg = sendgrid.SendGridAPIClient(
            apikey=settings.EMAIL_HOST_PASSWORD
        )    
    try:
        response = sg.client.mail.send.post(
            request_body=data)    
        logging.info('Status do E-MAIL: {}'.format(
            response.status_code))
        logging.info('Body do E-MAIL: {}'.format(response.body))
        logging.info('Header do E-MAIL: {}'.format(response.headers))
    except Exception as e:
        logging.error(traceback.format_exc())

def send_mail_sign_up(name, to_email):
    params = {
        'name': name, 
        'url': 'https://ezlawyer.atlassian.net/wiki/spaces/PUB/pages/101597/Manual+do+sistema'
    }
    data = {
            "personalizations": [{
                "to": [{"email": to_email}],
                "subject": "",
                "dynamic_template_data": params
            }],
            "from": {
                "email": "contato@ezlawyer.com.br"
            },
            "template_id": "d-fde3e5edcff54fe5b7feefb6e3271121"                
            }
    send_sendgrid_mail(data)
