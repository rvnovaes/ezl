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
    ret = {'totals': 0}
    try:
        xls_file = ImportXlsFile.objects.get(pk=file_id)
        task_resource = TaskResource()
        dataset = Dataset()

        imported_data = dataset.load(xls_file.file_xls.read())
        params = {'create_user': xls_file.create_user,'office': xls_file.office}
        result = task_resource.import_data(imported_data, dry_run=False, **params)
        ret['totals'] = result.totals
        if result.has_errors():
            ret['errors'] = list(map(lambda i: {'line': i[0], 'errors': list(map(lambda j: j.error.__str__(), i[1]))},
                                     result.row_errors()))
        return ret
    except Exception as e:
        ret['errors'] = '{} - {}'.format(e, traceback.format_exc())
        return ret
