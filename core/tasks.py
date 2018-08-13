from django.template.loader import render_to_string
from task.mail import SendMail
from celery import shared_task
from advwin_models.tasks import MAX_RETRIES, BASE_COUNTDOWN


@shared_task(bind=True, max_retries=MAX_RETRIES)
def send_mail(self, recipient_list, subject, mail_body):
    mail = SendMail()
    mail.subject = subject
    mail.message = render_to_string('mail/send_mail.html',
                                    {'body': mail_body, })
    mail.to_mail = recipient_list
    try:
        mail.send()
    except Exception as e:
        self.retry(countdown=(BASE_COUNTDOWN ** self.request.retries), exc=e)
        print(e)
        print('Você tentou mandar um e-mail')
        raise e
