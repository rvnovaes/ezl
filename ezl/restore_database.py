import subprocess
from ezl import settings
import os

current_db_name = settings.DATABASES['default']['NAME']
current_user_db = settings.DATABASES['default']['USER']
path_dump_db = '/opt/ezl.dump'

print('<br><br>')
print('A aplicação EZL Demo irá ficar indisponível durante este processo')
print('<br><br>')
# Para o serviço (demo) do Django e reinicia o serviço do Postgres para limpar as sessões ativas
subprocess.call('sudo supervisorctl stop demo_uwsgi', shell=True)
subprocess.call('sudo /etc/init.d/postgresql restart', shell=True)

# Limpa os dados de todas as tabelas do EZL
db_name = settings.DATABASES['default']['NAME']
print('Limpando o banco ' + current_db_name + '....')
print('<br><br>')
subprocess.call('sudo python3 manage.py flush --noinput', shell=True)
print('Banco ' + db_name + ' limpado com sucesso')
print('<br><br>')

# Realiza o restore do banco

print('Realizando pg_restore no banco ' + current_db_name + ' ...')
print('<br><br>')
pg_restore = 'pg_restore -a -U ezl --disable-triggers -d ' + current_db_name + ' ' + path_dump_db
# pg_restore = 'psql -U ezl demo < /opt/ezl.dump'

subprocess.call(pg_restore, shell=True)
print('Processo  concluído !')
print('<br><br>')

# Inicia o serviço (demo) do Django para disponibilizar a aplicacao novamente ao  usuário
subprocess.call('sudo supervisorctl start demo_uwsgi', shell=True)
print('A aplicação EZL Demo já disponível para acesso !')
