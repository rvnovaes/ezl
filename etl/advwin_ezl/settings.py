# indica se apaga todos os registros da tabela antes de importar (*apaga as dependencias tambem)
# TRUNCATE_ALL_TABLES = True
# usuário usado para create e alter user
USER = 2

# informações para uso do SFTP para importar GED
host_sftp = "172.27.155.11"
port_sftp = 22
password_sftp = "mta@2017"
username_sftp = "admin.ezl"
local_path = '/opt/files_easy_lawyer/GEDs/'
log_file = '/tmp/etl_ged.log'

# Utilização na importação EZL -> Advwin

# nome de usuário utilizado na exportação EZL -> Advwin
create_user = 'six'
config_file = 'advwin_ho.cfg'

# Configuracoes do Luigi

# PARA CONFIGURAR UMA PORTA DIFERENTE DA 8082 QUE E PADRAO DO LUIGI, E NECESSARIO CRIAR O ARQUIVO
# luigi.cfg DENTRO DE /etc/luigi/ exemplo: http://luigi.readthedocs.io/en/stable/configuration.html
# PARA A CONFIGURACAO DA PORTA O ARTRIBUTO NO luigi.cfg deve ser default-scheduler-port=porta
LUIGI_PORT = 8082
