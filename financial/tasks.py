from decimal import Decimal
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone
from celery import shared_task, current_task, chain
from celery.utils.log import get_task_logger
from openpyxl import load_workbook
from djmoney.money import Money
from .models import ServicePriceTable, ImportServicePriceTable
from core.models import Office, State
from task.models import TypeTask
from lawsuit.models import CourtDistrict
from .utils import remove_caracter_especial, clearCache
import time

IMPORTED_IMPORT_SERVICE_PRICE_TABLE = 'imported_ispt_'
IMPORTED_WORKSHEET = 'imported_worksheet_'
PROCESS_PERCENT_IMPORT_SERVICE_PRICE_TABLE = 'process_percent_ispt_'
WORKSHEET_IN_PROCESS = 'worksheet_in_process_'
ERROR_PROCESS = 'ERROR_PROCESS_'


def get_office_correspondent(row, xls_file):
    # escritorio correspondente
    office_correspondent = False    
    if row[0].value:
        office_name = remove_caracter_especial(str(row[0].value).strip())                
        office_correspondent = Office.objects.filter(legal_name__unaccent__iexact=office_name).first()
        if not office_correspondent:                        
            xls_file.log = xls_file.log + ('Escritório correspondente %s não encontrado' % office_name) + ";"
    return office_correspondent


def get_type_task(row, xls_file):
    # serviço
    type_task = False
    if row[1].value:        
        name_service = remove_caracter_especial(str(row[1].value).strip())
        type_task = TypeTask.objects.filter(name__unaccent__iexact=name_service).first()
        if not type_task:
            xls_file.log = xls_file.log + ('Tipo de serviço %s não encontrado' % name_service) + ";"
    return type_task


def get_state(row, xls_file):
    # uf            
    state = False
    if row[3].value:
        uf = remove_caracter_especial(str(row[3].value).strip())
        state = State.objects.filter(initials__iexact=uf).first()
        if not state:
            xls_file.log = xls_file.log + ('UF %s não encontrada' % uf) + ";"                    
    return state


def get_court_district(row, xls_file, state):
    # Comarca
    court_district = False
    if row[2].value and state:
        court_district_name = remove_caracter_especial(str(row[2].value).strip())
        court_district = CourtDistrict.objects.filter(name__unaccent__iexact=court_district_name, state=state.pk).first()
        if not court_district:
            xls_file.log = xls_file.log + ('Comarca %s não encontrada' % court_district_name) + ";"            
    return court_district


def get_service_value(row, xls_file, office_correspondent, court_district, state):
    value = 0
    try:                        
        if type(row[4].value) == str: 
            value = Decimal(row[4].value.replace('R$\xa0', '').replace(',', '.'))
        else:                        
            value = row[4].value
    except:        
        xls_file.log = xls_file.log + ('Valor {} inválido. Verificar escritório {}, comarca {}, estado {}.'.format(
            row[4].value, office_correspondent, court_district, state)) + ";"
    finally:
        return value


def row_is_valid(office_correspondent, type_task, state):
    return all([office_correspondent, type_task, state])


def update_or_create_service_price_table(xls_file, office_session, user_session, office_correspondent, 
        type_task, court_district, state, value):    
    service_price_table = ServicePriceTable.objects.filter(
        office=office_session,
        office_correspondent=office_correspondent.pk,
        type_task=type_task.pk,
        court_district=court_district.pk if court_district else None,
        state=state.pk).first()
    if not service_price_table:                    
        service_price_table = ServicePriceTable.objects.create(
            office=office_session,
            office_correspondent=office_correspondent,
            type_task=type_task,
            court_district=court_district if court_district else None,
            state=state,
            value=value,
            create_user=user_session
        )
    else:                        
        if value != service_price_table.value:
            xls_file.log = xls_file.log + ("Tabela de preço do escritório {}, serviço {} teve seu valor atualizado de "
                                           "{} para {}".format(office_correspondent, type_task,
                                                               service_price_table.value, value)) + ";"
            service_price_table.value = value
            service_price_table.save()


@shared_task(bind=True)
def import_xls_service_price_table(self, file_id):
    try:
        self.update_state(state="PROGRESS")
        xls_file = ImportServicePriceTable.objects.get(pk=file_id)
        xls_file.log = " "
        #chaves para acessar dados em cache
        imported_cache_key = IMPORTED_IMPORT_SERVICE_PRICE_TABLE + str(xls_file.pk)
        imported_worksheet_key = IMPORTED_WORKSHEET + str(xls_file.pk)
        percent_imported_cache_key = PROCESS_PERCENT_IMPORT_SERVICE_PRICE_TABLE + str(xls_file.pk)
        worksheet_in_process_key = WORKSHEET_IN_PROCESS + str(xls_file.pk)
        error_process_key = ERROR_PROCESS + str(xls_file.pk)        
        cache.set(imported_cache_key, False, timeout=None)
        cache.set(error_process_key, False, timeout=None)
        user_session = User.objects.get(pk=xls_file.create_user.pk)
        office_session = Office.objects.get(pk=xls_file.office.pk)       
        wb = load_workbook(xls_file.file_xls.file, data_only=True) 
        i = 0
        for sheet in wb.worksheets:
            total = sheet.max_row
            i = 0
            process_percent = 0
            cache.set(worksheet_in_process_key, sheet.title, timeout=None)
            cache.set(imported_worksheet_key, False, timeout=None)            
            for row in sheet.iter_rows(min_row=2):                       
                office_correspondent = get_office_correspondent(row, xls_file)
                type_task = get_type_task(row, xls_file)
                state = get_state(row, xls_file)
                court_district = get_court_district(row, xls_file, state)                
                if row_is_valid(office_correspondent, type_task, state):
                    value = get_service_value(row, xls_file, office_correspondent, court_district, state)
                    update_or_create_service_price_table(xls_file, office_session, user_session, office_correspondent, 
                        type_task, court_district, state, value)
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
        delete_imported_xls_service_price_table.apply_async(([xls_file.pk]), countdown=60)


@shared_task(bind=True)
def delete_imported_xls_service_price_table(self, xls_file_pk):
    ImportServicePriceTable.objects.filter(pk=xls_file_pk).delete()
