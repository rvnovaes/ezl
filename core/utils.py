from enum import Enum
from django.db.models import Q

# enumerador usado para integracao entre sistemas
class LegacySystem(Enum):
    ADVWIN = u"Advwin"


def filter_valid_choice_form(queryset):
    """
    Este metedo e responsavel por remover os registros invalidos
    gerados pela ETL e é utilizado nos forms na chamada do queryset do
    ModelChoiceField.

    :return: Retorna o queryset passado como parametro sem o registro invalido
    :rtype: QuerySet
    """
    try:
        model = queryset.model
        class_verbose_name_invalid = model._meta.verbose_name.upper() + '-INVÁLIDO'
        try:
            invalid_registry = queryset.filter(name=class_verbose_name_invalid).first()
        except:
            invalid_registry = queryset.filter(legacy_code='REGISTRO-INVÁLIDO').first()
        return queryset.filter(~Q(pk=invalid_registry.pk))
    except:
        return queryset
