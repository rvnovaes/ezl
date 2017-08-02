# indica se apaga todos os registros da tabela antes de importar (*apaga as dependencias tambem)
TRUNCATE_ALL_TABLES = False
# usuário usado para create e alter user
USER = 2

# informações para uso do SFTP para importar GED
host_sftp = "172.27.155.11"
port_sftp = 22
password_sftp = "mta@2017"
username_sftp = "admin.ezl"
local_path = '/opt/files_easy_lawyer/GEDs/'
log_file = '/tmp/etl_ged.log'

# nome de usuário utilizado na exportação EZL -> Advwin
create_user = 'six'
