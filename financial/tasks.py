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

IMPORTED_IMPORT_SERVICE_TABLE = 'imported_ispt_'
PROCESS_PERCENT_IMPORT_SERVICE_PRICE_TABLE = 'process_percent_ispt_'

# lista para montar log de erros da importação
logger = get_task_logger('ezl.financial')

@shared_task
def import_xls_service_price_table(file_id):        
    xls_file = ImportServicePriceTable.objects.get(pk = file_id)
    cache.set(IMPORTED_IMPORT_SERVICE_TABLE + str(xls_file.pk), False, timeout=None)
    
    user_session = User.objects.get(pk=xls_file.create_user.pk)
    office_session = Office.objects.get(pk=xls_file.office.pk)
    contact_mechanism_type = ContactMechanismType.objects.filter(type_contact_mechanism_type=EMAIL).first()
    
    wb = load_workbook(xls_file.file_xls.file, data_only=True)
    
    total = len(wb.worksheets)
    i = 0

    for sheet in wb.worksheets:
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
                    logger.info('Escritório correspondente %s não encontrado' % office_name)                    
                    importar = False                    
                
            # serviço            
            nome_servico = str(row[1].value).strip()
            nome_servico = remove_caracter_especial(nome_servico)
            if nome_servico == 'none':
                nome_servico = ''
            if nome_servico != '':
                type_task = TypeTask.objects.filter(name__unaccent__iexact=nome_servico).first()

                if type_task is None:
                    logger.info('Tipo de serviço %s não encontrado' % nome_servico)
                    importar = False                    

            # uf            
            sigla_uf = str(row[3].value).strip()
            sigla_uf = remove_caracter_especial(sigla_uf)
            if sigla_uf != '':
                state = State.objects.filter(initials__iexact=sigla_uf).first()
                if state is None:
                    logger.info('UF %s não encontrada' % sigla_uf)                    
                    importar = False
            
            # Comarca
            court_district = None
            court_district_name = str(row[2].value).strip()
            court_district_name = remove_caracter_especial(court_district_name)
            if court_district_name == 'None':
                court_district_name = ''
            if court_district_name != '':
                court_district = CourtDistrict.objects.filter(name__unaccent__iexact=court_district_name, state=state.pk).first()                
                # if court_district is None:
                #     errors.append('Comarca {} pertencente ao estado {} não encontrada'.format(court_district_name, sigla_uf))
                #     importar = False                    
            
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
                    logger.info('Valor {} inválido. Verificar escritório {}, comarca {}, estado {}.'.format(
                        row[4].value, office_correspondent, court_district, state))                                
                
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

        process_percent = int(100 * float(i) / float(total))
        i = i + 1
        cache.set(PROCESS_PERCENT_IMPORT_SERVICE_PRICE_TABLE + str(xls_file.pk), process_percent, timeout=None)            
    
    cache.set(IMPORTED_IMPORT_SERVICE_TABLE + str(xls_file.pk), True, timeout=None)


def remove_caracter_especial(texto):
    d = {'À': 'A', 'Á': 'A', 'Ä': 'A', 'Â': 'A', 'Ã': 'A',
         'È': 'E', 'É': 'E', 'Ë': 'E', 'Ê': 'E',
         'Ì': 'I', 'Í': 'I', 'Ï': 'I', 'Î': 'I',
         'Ò': 'O', 'Ó': 'O', 'Ö': 'O', 'Ô': 'O', 'Õ': 'O',
         'Ù': 'U', 'Ú': 'U', 'Ü': 'U', 'Û': 'U',
         'à': 'a', 'á': 'a', 'ä': 'a', 'â': 'a', 'ã': 'a', 'ª': 'a',
         'è': 'e', 'é': 'e', 'ë': 'e', 'ê': 'e',
         'ì': 'i', 'í': 'i', 'ï': 'i', 'î': 'i',
         'ò': 'o', 'ó': 'o', 'ö': 'o', 'ô': 'o', 'õ': 'o', 'º': 'o', '°': 'o',
         'ù': 'u', 'ú': 'u', 'ü': 'u', 'û': 'u',
         'Ç': 'C', 'ç': 'c'}
    novo_texto = ''

    for c in range(0, len(texto)):
        novo_caracter = texto[c]
        try:
            novo_caracter = d[texto[c]]
        except KeyError:
            pass

        novo_texto = novo_texto + novo_caracter

    return novo_texto