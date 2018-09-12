from decimal import Decimal
from django.core.cache import cache
from django.utils import timezone
from celery import shared_task, current_task, chain
from celery.utils.log import get_task_logger
from openpyxl import load_workbook
from djmoney.money import Money
from core.utils import get_office_session
from core.models import ImportXlsFile, Office, State
from core.tasks import delete_imported_xls
from task.models import TypeTask
from task.resources import TaskResource
from lawsuit.models import CourtDistrict
from tablib import Dataset
import traceback


def int_formatter(cell_value):
    try:
        return int(cell_value)
    except:
        return cell_value


@shared_task(bind=True)
def import_xls_task_list(self, file_id):
    ret = {'total_rows': 0, 'totals': 0}
    try:
        xls_file = ImportXlsFile.objects.get(pk=file_id)
        task_resource = TaskResource()
        dataset = Dataset()

        imported_data = dataset.load(xls_file.file_xls.read())
        params = {'create_user': xls_file.create_user,'office': xls_file.office}
        result = task_resource.import_data(imported_data, collect_failed_rows=True, **params)
        ret['total_rows'] = result.total_rows
        ret['totals'] = result.totals
        ret['errors'] = []
        if result.has_errors():
            for line_error in result.row_errors():
                line = line_error[0]
                errors = []
                for error in line_error[1]:
                    error_description = error.error.__str__().replace('[','').replace(']', '')
                    errors.append(error_description.split("',"))
                ret['errors'].append({'line': line, 'errors': errors})

    except Exception as e:
        ret['errors'] = '{} - {}'.format(e, traceback.format_exc())

    finally:
        return ret
