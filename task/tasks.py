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
# from .utils import remove_caracter_especial, clearCache
import time


def int_formatter(cell_value):
    return int(cell_value)


@shared_task(bind=True)
def import_xls_task_list(self, file_id):
    try:
        xls_file = ImportXlsFile.objects.get(pk=file_id)
        task_resource = TaskResource()
        dataset = Dataset()

        imported_data = dataset.load(xls_file.file_xls.read())
        imported_data.add_formater
        params = {'create_user': xls_file.create_user,
                  'office': xls_file.office}
        result = task_resource.import_data(imported_data, dry_run=True, **params)
        if not result.has_errors():
            result = task_resource.import_data(imported_data, dry_run=False, **params)
        else:
            ret = list(map(lambda i: {'line': i[0], 'errors': set(map(lambda j: j.error, i[1]))}, result.row_errors()))
            return ret
    except Exception as e:
        pass
