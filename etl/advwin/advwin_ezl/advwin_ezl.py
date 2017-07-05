# ordem de importação
# user - inserir id do usuário configurado em etl/advwin/settings.py
# state
# court_district
# city
# todo: acho que tem que ser feito um script que roda todos os scripts de etl na ordem correta pra não dar erro de fk
# todo: ou pode ser usado o luigi com o crontab

from django.contrib.auth.models import User

from core.utils import LegacySystem
from etl.advwin import settings as etl_settings


# apaga registros das tabelas
# tem que ter cascade mesmo que não existam registros associados em outras tabelas
# restart identity - reinica o id da tabela
def truncate_tables(table_list):
    if etl_settings.TRUNCATE_ALL_TABLES:
        for table in table_list:
            table.objects.all().delete()


# inativa todos os registros já existentes para não ter que consultar ativos e inativos do legado
def deactivate_records(table_list):
    if not etl_settings.TRUNCATE_ALL_TABLES:
        for table in table_list:
            records = table.objects.filter(legacy_code=LegacySystem.ADVWIN.value)
            for record in records:
                record.deactivate()


# seleciona o modelo do usuario de acordo com o id configurado no etl.settings
def select_user():
    return User.objects.get(pk=etl_settings.USER)
