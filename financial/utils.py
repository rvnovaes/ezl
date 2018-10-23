from django.core.cache import cache
from lawsuit.models import CourtDistrict
from django.db.models import Q
from .models import ServicePriceTable


def clearCache(key_list):
    for key in key_list:
        cache.delete(key)


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


def valid_court_district(court_district, state):
    if court_district.state != state:
        return False
    return True


def check_service_price_table_unique(pk, office, office_correspondent, state, court_district, type_task, client,
                                     court_district_complement):
    office_q = Q(office=office)
    office_correspondent_q = Q(office_correspondent=office_correspondent) if office_correspondent \
        else Q(office_correspondent__isnull=True)
    state_q = Q(state=state) if state else Q(state__isnull=True)
    court_district_q = Q(court_district=court_district) if court_district else Q(court_district__isnull=True)
    court_district_complement_q = Q(court_district_complement=court_district_complement) if court_district_complement \
        else Q(court_district_complement__isnull=True)
    type_task_q = Q(type_task=type_task) if type_task else Q(type_task__isnull=True)
    client_q = Q(client=client) if client else Q(client__isnull=True)
    if ServicePriceTable.objects.filter(~Q(pk=pk), office_q, office_correspondent_q, state_q, court_district_q,
                                        type_task_q, client_q, court_district_complement_q):
        return False
    return True


def check_office_correspondent_relation(office, office_correspondent):
    return office_correspondent in office.offices.active_offices()