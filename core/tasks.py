from django.contrib.sessions.models import Session
from django.template.loader import render_to_string
from task.mail import SendMail
from celery import shared_task, task
from advwin_models.tasks import MAX_RETRIES, BASE_COUNTDOWN
from core.models import ImportXlsFile
from django.core.management import call_command
from core.resources import CityResource
from tablib import Dataset
import traceback


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


def import_xls_city_list(file_id):
    ret = {'total_rows': 0, 'totals': 0}
    try:
        xls_file = ImportXlsFile.objects.get(pk=file_id)
        city_resource = CityResource()
        dataset = Dataset()

        imported_data = dataset.load(xls_file.file_xls.read())
        params = {
            'create_user': xls_file.create_user,
            'office': xls_file.office,
            'warnings': []
        }
        result = city_resource.import_data(
            imported_data, use_transactions=False, **params)
        ret['total_rows'] = result.total_rows
        ret['totals'] = result.totals
        ret['errors'] = []
        ret['warnings'] = []
        if result.has_errors():
            for line_error in result.row_errors():
                line = line_error[0]
                errors = []
                for error in line_error[1]:
                    error_description = error.error.__str__().replace(
                        '[', '').replace(']', '')
                    errors.append(error_description.split("',"))
                ret['errors'].append({'line': line, 'errors': errors})
        if result.has_warnings():
            for line_warning in result.row_warnings():
                ret['warnings'].append({'line': line_warning[0], 'warnings': line_warning[1]})

    except Exception as e:
        ret['errors'] = '{} - {}'.format(e, traceback.format_exc())

    finally:
        return ret