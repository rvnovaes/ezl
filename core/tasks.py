from django.contrib.sessions.models import Session
from django.template.loader import render_to_string
from task.mail import SendMail
from celery import shared_task, task
from advwin_models.tasks import MAX_RETRIES, BASE_COUNTDOWN
from core.models import ImportXlsFile
from django.core.management import call_command


@shared_task(bind=True, max_retries=MAX_RETRIES)
def send_mail(self, recipient_list, subject, mail_body):
    mail = SendMail()
    mail.subject = subject
    mail.message = render_to_string('mail/send_mail.html', {
        'body': mail_body,
    })
    mail.to_mail = recipient_list
    try:
        mail.send()
    except Exception as e:
        self.retry(countdown=(BASE_COUNTDOWN**self.request.retries), exc=e)
        print(e)
        print('Você tentou mandar um e-mail')
        raise e


@shared_task(bind=True)
def delete_imported_xls(self, xls_file_pk):
    ImportXlsFile.objects.filter(pk=xls_file_pk).delete()


@task()
def clear_sessions():
    total = Session.objects.all().count()
    call_command("clearsessions")
    total_cleared = Session.objects.all().count()
    ret = {'total_cleared': total_cleared, 'deleted': total - total_cleared}
    return ret
