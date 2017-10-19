#!/usr/bin/env bash
# O que faz este script?
#    - Clona o código
#    - Instala as dependencias utilizando um ambiente no virtualenv
#    - Cria um banco de teste
#    - Instala o a extensão unnacent no banco
#    - Roda as migrations
#    - Chama a execução da ETL com o sistema ADVWin_HO
#
# O que preciso para rodar este script?
#    - É nescessário ter instalado em uma máquina com Ubuntu ou derivados do Debian
#      - PostgresSQL
#      - Um usuário no banco com o nome ezl
#      - Python3.5
#    - Ter o usuário cadastrado no repositório
#
# Como rodar este script²
#    - Basta entrar no diretório onde ele se encontra
#    - Digitar o comando ./install_base_etl_dev.sh
#    - É necessário dar permissão de execução no script caso ele não tenha
#      - O comando é: sudo chmod +x install_base_etl_dev.sh
#
# Porque rodar este script?
#    - A realização bem-sucedida deste script permite a automatização deste processo e garantia que o básico
#    - para acesso ao sistema e importacao dos dados do ADVWin esta funcionando.
#
# Quando rodar este script?
#    - Em ambientes de desenvolvimento (Através deste será criado novos scripts para ambientes de demo e produção)
#
# Observações:
#    - Este script funciona na rede interna da empresa
#    - Para rodar em redes externas, é necessário configurar o tunelamento
#      da conexao com o servidor do advwin e alterar neste script
#   -  na sessão 'Configurando ETL' o valor server = 172.27.155.9 para server = 127.0.0.1:2000


# Update ubuntu
echo "Atualizando o ubuntu..."
sudo apt-get update -y

# Instalando mercurial
echo "Checando o mercurial..."
sudo apt-get install mercurial -y


# Checando postgres
sudo apt-get install postgresql -y

# Configurando pg_hba.conf

# Configurando postgres.conf

# Checando python dev
sudo apt-get install python-setuptools -y
sudo apt-get install python3-setuptools -y
sudo apt-get install python-dev -y
sudo apt-get install python3-dev -y
sudo apt-get install python3-pip -y


# Criando diretorio de logs
cd /var/log
logs_dir='etl/ezl'
sudo mkdir -p ${logs_dir}
sudo chmod 755 ${logs_dir}
sudo chown `whoami` ${logs_dir}
# Criando diretorio padrao do projeto
base_dir='/opt/fonts'
cd '/opt/'
if [ ! -d "$base_dir" ]; then
    echo "Criando diretorio ${base_dir}..."
    sudo mkdir -p ${base_dir}
    sudo chmod 777 ${base_dir}
    sudo chown `whoami` ${base_dir}
fi
cd ${base_dir}

# Criando diretorio para arquivos de media
dir_media='/opt/files_easy_lawyer/'
if [ ! -d "$dir_media" ]; then
    echo "Criando /opt/files_easy_lawyer/..."
    sudo mkdir -p ${dir_media}
    sudo chmod 777 ${dir_media}
fi

# Verificando se o repositorio existe
repositorio='easy_lawyer_django'
if [ ! -d "$repositorio" ]; then
    echo "Clonando repositorio..."
    hg clone https://bitbucket.org/marcelotostes/easy_lawyer_django
else
    echo "Repositorio já existe! Deseja remover e clonar novamente"
    read -p "y/n: " op
    if [ "$op" = "y" ]; then
        echo "Removendo diretorio"
        sudo rm -rf ${repositorio}
        echo "Clonando repositorio novamente..."
        hg clone https://bitbucket.org/marcelotostes/easy_lawyer_django
    else
        echo "Saindo..."
        exit
    fi
fi

# Criando virutal env
sudo apt-get install python-virtualenv -y
virtual_env_instalado=`dpkg -l | grep -i python3-virtualenv | awk '{print $1}'`
if [ "$virtual_env_instalado" != "ii" ]; then
    echo "Instalando python-virtualenv..."
    sudo apt-get install python3-virtualenv -y
fi
virtualenv_dir='/opt/venvs'
if [ ! -d "$virtualenv_dir" ]; then
    echo "Criando o diretrio $virtualenv_dir"
    sudo mkdir -p $virtualenv_dir
    sudo chmod 777 $virtualenv_dir
fi
cd ${virtualenv_dir}
if [ ! -d "$repositorio" ]; then
    echo ""
    echo "Criando virtual env para $repositorio"
    virtualenv -p python3.5 ${repositorio}
fi
echo "Ativando virtualenv..."
cd ${repositorio}
source bin/activate

# Instalando pacotes requeridos

cd ${base_dir}/${repositorio}
pip3.5 install -r requirements.txt

# Criando usuario postgres
echo "criando usuario postgres..."
sudo -H -u postgres bash -c 'psql --command="CREATE USER ezl SUPERUSER INHERIT CREATEDB CREATEROLE;"' >> /dev/null 2>&1
sudo -H -u postgres psql --command="ALTER USER ezl PASSWORD 'ezl';"

# Criando banco de dados
read -p "Nome do DB que sera criado: " db
db_exist=`psql -Uezl --command="SELECT datname FROM pg_database WHERE datname='${db}';"`
db_exist=`echo ${db_exist} | awk '{print $3}'`
if [ ${db_exist} = ${db} ]; then
    echo "Banco ${db_exist} existe. Deseja excluir e criar novamente o banco ${db}"
    read -p "y/n: " op
    if [ "$op" = "y" ]; then
        read -p "Atencao!!! Tem certeza que quer excluir o banco ${db}?: y/s: " op
        if [ "$op" = "y" ]; then
            echo "Excluindo banco ${db}..."
            dropdb -U ezl ${db}
            echo "Criando banco ${db}..."
            createdb -U ezl ${db}
        else
            echo "O banco ${db} sera mantido"
        fi
    fi
else
    echo "Criando banco ${db}..."
    createdb -U ezl ${db}
    psql --username=ezl --dbname=${db} --command="CREATE EXTENSION unaccent;"
fi

# Gerando configuracao general.ini
echo "Gerando arquivo de configuracao"
msg="Informe a senha do usuario `whoami`"
echo ${msg}
read -s -p "senha: " user_passwd
echo "
; Django Web Application Configuration
[django_application]
; Connection Configurations
engine = django.db.backends.postgresql
database = ${db}
user = ezl
password = ezl
host = 127.0.0.1
port = 5432

; used in password_validator and debug mode
; password_validator: development (validates only min lenght = 1) or production (full validation)
; debug mode = True if development, else False
environment = development

; E-mail configurations
email_use_ssl = True
email_host = 'smtp.zoho.com'
email_port = 465
email_host_user = 'ezlawyer@mttech.com.br'
email_host_password = 'ezlmta@578'

[etl]
; indica se apaga todos os registros da tabela antes de importar (*apaga as dependencias tambem)
truncate_all_tables = False
; usuario e senha do do usuario linux responsavel por executar a etl. Este deve estar no grupo sudoers.
linux_user = mttech
linux_password = ${user_passwd}
; usuario admin do django para realizar a importacao
user=2
; conexao com o advwin, devera ser o nome da secessao de configuracao que deseja utilizar
connection_name = advwin_ho_connection

# nome de usuário utilizado na exportação EZL -> Advwin
create_user = 'six'

; informações para uso do SFTP para importar GED
host_sftp = "172.27.155.11"
port_sftp = 22
password_sftp = "mta@2017"
username_sftp = "admin.ezl"
local_path = '/opt/files_easy_lawyer/ECM/'
log_file = '/tmp/etl_ged.log'


luigi_port = 8082

[advwin_connection]
server = 172.27.155.9
user = Rvnovaes
password = libertas
database = Advwin
# postgresql ou sql_server
db_type = sql_server

[advwin_ho_connection]
server = 172.27.155.9
user = Rvnovaes
password = libertas
database = Advwin_ho
# postgresql ou sql_server
db_type = sql_server

[advwin_tunel_ho_connection]
server = 127.0.0.1:2000
user = Rvnovaes
password = libertas
database = Advwin_ho
# postgresql ou sql_server
db_type = sql_server

" > config/general.ini

echo "INFORME UMA DAS OPCOES DE AMBIENTE"
valid_op=0
cd ${base_dir}/${repositorio}
while [ ${valid_op} -eq 0 ]
do
    echo "1-Demo               2-ETL"
    read -p "Opcao: " op
    valid_op=1
    if [ "${op}" = "1" ]; then
        echo "Rodando migrations..."
        python3.5 manage.py migrate
        echo "Rodando - factory"
        echo `pwd`
        echo "Rodando fixtures..."
        python3.5 manage.py loaddata permission
        python3.5 manage.py loaddata group
        python3.5 manage.py loaddata group_permissions
        python3.5 manage.py loaddata auth_user
        python3.5 manage.py loaddata country
        python3.5 manage.py loaddata state
        python3.5 manage.py loaddata court_district
        python3.5 manage.py loaddata court_division
        python3.5 manage.py loaddata city
        python3.5 manage.py loaddata type_movement
        python3.5 manage.py loaddata type_task
        echo "Aplicacao rodando em 127.0.0.1:8000"
        python3.5 manage.py runserver 0.0.0.0:8000
    elif [ "${op}" = "2" ]; then
        echo "Rodando ETL..."
        sudo pip3 install
        python3.5 etl/advwin_ezl/luigi_jobs.py
    else
        valid_op=0
        echo "Opcao invalida!"
    fi
done

