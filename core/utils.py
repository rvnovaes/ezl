from enum import Enum
from config.config import get_parser
from django.db.models import Q
import logging
from functools import wraps
from openpyxl import load_workbook
import os
from functools import wraps

EZL_LOGGER = logging.getLogger('ezl')


def check_environ(f):    
    @wraps(f)
    def wrapper(*args, **kwargs):        
        parser = get_parser()
        source = dict(parser.items('etl'))
        connection_name = source['connection_name']        
        if  connection_name == 'advwin_connection' and os.environ['ENV'] == 'development':
            return 'NAO E PERMITIDO EXECUTAR ESTA OPERACAO NO BANCO ADVWIN DE PRODUCAO COM O AMBIENTE DEVELOPMENT'
        return f(*args, **kwargs)
    return wrapper

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


def login_log(f):
    """
    Metodo decorator para gerar log mostrando o usuario e o momento que foi realizado o login
    :param f:
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        res = f(*args, **kwargs)
        try:
            username = args[1].data.get('login')
            msg = 'LOGIN realizado por: {user}'.format(user=username)
            EZL_LOGGER.info(msg)
        except Exception as e:
            EZL_LOGGER.error(str(e))
        return res

    return wrapper


def logout_log(f):
    """
    Metodo decorator para gerar log mostrando o usuario e o momento que foi realizado o logout
    :param f:
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            request = args[0]
            username = request.user.username
            msg = 'LOGOUT realizado por: {user}'.format(user=username)
            EZL_LOGGER.info(msg)
        except Exception as e:
            EZL_LOGGER.error(str(e))
        return f(*args, **kwargs)

    return wrapper


def get_office_field(request, profile=None):
    """
    Método para montar o campo de office, de acordo com a variável de sessão custom_session_user
    :param request:
    :param profile:
    :return: forms.ModelChoiceField
    """
    from core.models import Office, DefaultOffice
    from django import forms
    try:
        if profile:
            queryset = profile.person.offices.active_offices()
            initial = DefaultOffice.objects.filter(auth_user=profile).first().office if \
                DefaultOffice.objects.filter(auth_user=profile).first() else None
        elif request.session.get('custom_session_user'):
            custom_session_user = list(request.session.get('custom_session_user').values())
            queryset = Office.objects.filter(pk=custom_session_user[0]['current_office'])
            initial = queryset.first().id
        else:
            queryset = request.user.person.offices.active_offices()
            initial = None
    except Exception as e:
        queryset = Office.objects.none()
        initial = None

    return forms.ModelChoiceField(
        queryset=queryset,
        empty_label='',
        required=True,
        label=u'Escritório',
        initial=initial
    )


def get_office_related_office_field(request):
    from core.models import Office, DefaultOffice
    from django import forms
    queryset = Office.objects.none()
    initial = None
    office = get_office_session(request)
    if office:
        if office.public_office:
            queryset = office.offices.all().order_by('legal_name') | Office.objects.filter(public_office=True)
        else:
            queryset = office.offices.all().order_by('legal_name')


    return forms.ModelChoiceField(
        queryset=queryset,
        empty_label='',
        required=True,
        label=u'Escritório',
        initial=initial
    )

def get_office_session(request):
    """
    Retorna o objeto Office de acordo com a sessão atual do usuário; Ou False caso não tenha selecionado escritório
    :param request:
    :return: Office object or False
    """
    from core.models import Office
    office = Office.objects.none()    
    if request:
        if request.session.get('custom_session_user'):
            custom_session_user = list(request.session.get('custom_session_user').values())
            office = Office.objects.filter(pk=custom_session_user[0]['current_office']).first()
        else:
            office = False

    return office


def get_domain(request):
    try:
        if request.META.get('HTTP_X_FORWARDED_HOST') or request.META.get('HTTP_HOST'):
            return '{}://{}'.format(request.scheme, request.META.get('HTTP_X_FORWARDED_HOST', request.META.get('HTTP_HOST')))
        return request.META.get('HTTP_REFERER')[:-1]
    except:
        return '{}://{}'.format(request.scheme, request.get_host())


def validate_xlsx_header(xls_file, headers):
    header_is_valid = False
    if headers:
        wb = load_workbook(xls_file, data_only=True)
        headers_in_file = list(map(lambda header:header.value, [list(sheet.rows)[0] for sheet in wb.worksheets][0]))
        header_is_valid = set(headers).issubset(set(headers_in_file))
    return header_is_valid
