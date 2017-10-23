import os
import sys
import subprocess
import django
from django.db import connection

# maneira de se chamar o script via terminal: python3 restore_database.py {user_bd} {pass_bd}.
# Para o servidor da Azure: python3 restore_database.py ezl ezl

sys.path.append(os.getcwd())
os.environ['DJANGO_SETTINGS_MODULE'] = 'ezl.settings'
django.setup()

from django.conf import settings

current_db_name = settings.DATABASES['default']['NAME']
current_user_db = settings.DATABASES['default']['USER']
current_password_db = settings.DATABASES['default']['PASSWORD']

username = sys.argv[1]
password = sys.argv[2]

if username == current_user_db and password == current_password_db:
    path_dump_db = '/opt/demo.dump'

    # Para o serviço (demo) do Django e reinicia o serviço do Postgres para limpar as sessões ativas
    subprocess.call('sudo supervisorctl stop demo_uwsgi', stdout=subprocess.PIPE, shell=True)
    subprocess.call('sudo /etc/init.d/postgresql restart', stdout=subprocess.PIPE, shell=True)

    # Limpa os dados de todas as tabelas do EZL
    db_name = settings.DATABASES['default']['NAME']
    subprocess.call('sudo python3 manage.py flush --noinput', stdout=subprocess.PIPE, shell=True)

    # O comando python3 manage.py flush não apaga os dados das tabelas auth_permission, django_content_type, django_migrations, django_site.
    # Assim, é necessário apagar manualmente os dados destas tabelas.

    cursor = connection.cursor()
    cursor.execute("TRUNCATE TABLE auth_permission CASCADE")
    cursor.execute("TRUNCATE TABLE django_content_type CASCADE")
    cursor.execute("TRUNCATE TABLE django_migrations CASCADE")
    cursor.execute("TRUNCATE TABLE django_site CASCADE")
    cursor.execute("SELECT * FROM task")
    quant_after_clear = len(cursor.fetchall())

    # Realiza o restore do banco

    pg_restore = 'pg_restore -a --disable-triggers -U ezl -d ' + current_db_name + ' ' + path_dump_db
    # pg_restore = 'psql -U ezl demo < /opt/ezl.dump'

    subprocess.call(pg_restore, stdout=subprocess.PIPE, shell=True)
    cursor.execute("SELECT * FROM task")
    quant_after_restore = len(cursor.fetchall())

    # Inicia o serviço (demo) do Django para disponibilizar a aplicacao novamente ao  usuário
    subprocess.call('sudo supervisorctl start demo_uwsgi', stdout=subprocess.PIPE, shell=True)

    if quant_after_restore > quant_after_clear:
        print('Recuperação realizada com sucesso !')

    else:
        print('Ocorreu um erro ao recuperar o banco !')


else:
    print('Usuário e/ou senha do banco de dados não estão correto(s).')
