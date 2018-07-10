from django.core.cache import cache
from lawsuit.models import CourtDistrict


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
