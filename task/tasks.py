from decimal import Decimal
from django.core.cache import cache
from django.utils import timezone
from celery import shared_task, current_task, chain
from celery.utils.log import get_task_logger
from openpyxl import load_workbook
from djmoney.money import Money
from core.models import ImportXlsFile, Office, State
from core.tasks import delete_imported_xls
from task.models import TypeTask
from lawsuit.models import CourtDistrict
# from .utils import remove_caracter_especial, clearCache
import time

IMPORTED_IMPORT_SERVICE_PRICE_TABLE = 'imported_ispt_'
IMPORTED_WORKSHEET = 'imported_worksheet_'
PROCESS_PERCENT_IMPORT_SERVICE_PRICE_TABLE = 'process_percent_ispt_'
WORKSHEET_IN_PROCESS = 'worksheet_in_process_'
ERROR_PROCESS = 'ERROR_PROCESS_'


@shared_task(bind=True)
def import_xls_task_list(self, file_id):
    try:
        self.update_state(state="PROGRESS")
        xls_file = ImportXlsFile.objects.get(pk=file_id)
        xls_file.log = " "
        # chaves para acessar dados em cache
        imported_cache_key = IMPORTED_IMPORT_SERVICE_PRICE_TABLE + str(xls_file.pk)
        imported_worksheet_key = IMPORTED_WORKSHEET + str(xls_file.pk)
        percent_imported_cache_key = PROCESS_PERCENT_IMPORT_SERVICE_PRICE_TABLE + str(xls_file.pk)
        worksheet_in_process_key = WORKSHEET_IN_PROCESS + str(xls_file.pk)
        error_process_key = ERROR_PROCESS + str(xls_file.pk)        
        cache.set(imported_cache_key, False, timeout=None)
        cache.set(error_process_key, False, timeout=None)
        user_session = xls_file.create_user
        office_session = xls_file.office
        wb = load_workbook(xls_file.file_xls.file, data_only=True) 
        i = 0
        for sheet in wb.worksheets:
            total = sheet.max_row
            i = 0
            process_percent = 0
            cache.set(worksheet_in_process_key, sheet.title, timeout=None)
            cache.set(imported_worksheet_key, False, timeout=None)            
            for row in sheet.iter_rows(min_row=2):                       
                # office_correspondent = get_office_correspondent(row, xls_file)
                # type_task = get_type_task(row, xls_file)
                # state = get_state(row, xls_file)
                # court_district = get_court_district(row, xls_file, state)
                # if row_is_valid(office_correspondent, type_task, state):
                #     value = get_service_value(row, xls_file, office_correspondent, court_district, state)
                #     update_or_create_service_price_table(xls_file, office_session, user_session, office_correspondent,
                #         type_task, court_district, state, value)
                    i = i + 1
                    process_percent = int(100 * float(i) / float(total))            
                    cache.set(percent_imported_cache_key, process_percent, timeout=None)            
            cache.set(imported_worksheet_key, True, timeout=None)                                
        cache.set(imported_cache_key, True, timeout=None)
    except FileNotFoundError as ex:
        cache.set(error_process_key, True, timeout=None)        
        xls_file.log = xls_file.log + " Planilha não encontrada Erro: " + str(ex.args[0]) + ";"        
    except Exception as ex:        
        cache.set(error_process_key, True, timeout=None)        
        xls_file.log = xls_file.log + " Planilha: " + sheet.title + " Linha " + str(i + 1) + "Erro: " + ex.args[0] + ";"        
    finally:        
        xls_file.end = timezone.now()
        xls_file.save()
        delete_imported_xls.apply_async(([xls_file.pk]), countdown=60)
