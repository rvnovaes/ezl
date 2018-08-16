from functools import wraps
from dashboard.models import Dashboard
from django.db import transaction
from django.utils import timezone

MONTHS = {
    1: 'Janeiro',
    2: 'Fevereiro',
    3: 'Março',
    4: 'Abril',
    5: 'Maio',
    6: 'Junho',
    7: 'Julho',
    8: 'Agosto',
    9: 'Setembro',
    10: 'Outubro',
    11: 'Novembro',
    12: 'Dezembro'
}


def get_month():
    return MONTHS.get(timezone.now().month)


def no_commit(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        res = False
        with transaction.atomic():
            res = f(*args, **kwargs)
            transaction.set_rollback(True)
        return res
    return wrapper


def set_company(f):
    @wraps(f)
    def wrapper(self, obj, attr):
        try:
            self.company = Dashboard.objects.get(
                **self.context['view'].kwargs).company
        except AttributeError as e:
            pass
        finally:
            return f(self, obj, attr)
    return wrapper


@no_commit
@set_company
def exec_code(self, obj, attr):
    try:
        exec(getattr(obj, attr))
        return locals().get('result')
    except:
        return ''
