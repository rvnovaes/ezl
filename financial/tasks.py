from decimal import Decimal
from django.contrib.auth.models import User
from django.core.cache import cache
from celery import shared_task, current_task
from celery.utils.log import get_task_logger
from openpyxl import load_workbook
from djmoney.money import Money
from .models import ServicePriceTable, ImportServicePriceTable
from core.models import Office, State, ContactMechanism, \
    ContactMechanismType, EMAIL
from task.models import TypeTask
from lawsuit.models import CourtDistrict
from .utils import remove_caracter_especial, clearCache

IMPORTED_IMPORT_SERVICE_PRICE_TABLE = 'imported_ispt_'
IMPORTED_WORKSHEET = 'imported_worksheet_'
PROCESS_PERCENT_IMPORT_SERVICE_PRICE_TABLE = 'process_percent_ispt_'
WORKSHEET_IN_PROCESS = 'worksheet_in_process_'
ERROR_PROCESS = 'ERROR_PROCESS_'

@shared_task
def import_xls_service_price_table(file_id):
    try:
        xls_file = ImportServicePriceTable.objects.get(pk = file_id)
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
        contact_mechanism_type = ContactMechanismType.objects.filter(type_contact_mechanism_type=EMAIL).first()
        
        wb = load_workbook(xls_file.file_xls.file, data_only=True)                                

        i = 0
        for sheet in wb.worksheets:
            total = sheet.max_row
            i = 0
            process_percent = 0
            cache.set(worksheet_in_process_key, sheet.title, timeout=None)
            cache.set(imported_worksheet_key, False, timeout=None)
            
            for row in sheet.iter_rows(min_row=2):                       
                importar = True

                # escritorio correspondente            
                office_name = str(row[0].value).strip()
                office_name = remove_caracter_especial(office_name)
                if office_name == 'none':
                    office_name = ''
                if office_name != '':                
                    office_correspondent = Office.objects.filter(legal_name__unaccent__iexact=office_name).first()

                    if office_correspondent is None:                        
                        xls_file.log = xls_file.log + ('Escritório correspondente %s não encontrado' % office_name) + ";"                    
                        importar = False                    
                    
                # serviço            
                nome_servico = str(row[1].value).strip()
                nome_servico = remove_caracter_especial(nome_servico)
                if nome_servico == 'none':
                    nome_servico = ''
                if nome_servico != '':
                    type_task = TypeTask.objects.filter(name__unaccent__iexact=nome_servico).first()

                    if type_task is None:
                        xls_file.log = xls_file.log + ('Tipo de serviço %s não encontrado' % nome_servico) + ";"
                        importar = False                    

                # uf            
                sigla_uf = str(row[3].value).strip()
                sigla_uf = remove_caracter_especial(sigla_uf)
                if sigla_uf != '':
                    state = State.objects.filter(initials__iexact=sigla_uf).first()
                    if state is None:
                        xls_file.log = xls_file.log + ('UF %s não encontrada' % sigla_uf) + ";"                    
                        importar = False
                
                # Comarca
                court_district = None
                court_district_name = str(row[2].value).strip()
                court_district_name = remove_caracter_especial(court_district_name)
                if court_district_name == 'None':
                    court_district_name = ''
                if court_district_name != '':
                    court_district = CourtDistrict.objects.filter(name__unaccent__iexact=court_district_name, state=state.pk).first()                  
                
                if importar:                  
                    service_price_table = ServicePriceTable.objects.filter(
                        office=office_session,
                        office_correspondent = office_correspondent.pk,
                        type_task = type_task.pk,
                        court_district = court_district.pk if court_district else None,
                        state = state.pk).first()
                                    
                    try:
                        
                        if type(row[4].value) == str:
                            value_str = row[4].value.replace('R$\xa0', '').replace(',', '.')
                            value = Decimal(value_str)
                        else:                        
                            value = row[4].value
                    except:
                        value = 0
                        xls_file.log = xls_file.log + ('Valor {} inválido. Verificar escritório {}, comarca {}, estado {}.'.format(
                            row[4].value, office_correspondent, court_district, state)) + ";"                                
                    
                    if service_price_table is None:                    
                        service_price_table = ServicePriceTable.objects.create(
                            office = office_session,
                            office_correspondent = office_correspondent,
                            type_task = type_task,
                            court_district = court_district if court_district else None,
                            state = state,            
                            value = value,
                            create_user=user_session
                        )
                    else:
                        service_price_table.value = value
                        service_price_table.save()
                                        
                    emails = str(row[5].value).strip().lower() + str(row[6].value).strip().lower()
                    for email in emails.split(";"):
                        contact_mechanism = ContactMechanism.objects.filter(
                            office=office_correspondent.pk,
                            description__iexact=email).first()
                        if contact_mechanism is None:                         
                            ContactMechanism.objects.create(
                                contact_mechanism_type = contact_mechanism_type,
                                description = email,
                                office = office_correspondent,
                                create_user=user_session
                            )

                    i = i + 1
                    process_percent = int(100 * float(i) / float(total))            
                    cache.set(percent_imported_cache_key, process_percent, timeout=None)
            
            cache.set(imported_worksheet_key, True, timeout=None)                            
        
        cache.set(imported_cache_key, True, timeout=None)
    except Exception as ex:
        cache.set(error_process_key, True, timeout=None)
        xls_file.log = xls_file.log + " Planilha: " + sheet.title + " Linha " + str(i + 1) + "Erro: " + ex.args[0] + ";"        
    xls_file.save()