#!/usr/bin/env bash

# Criando diretorio padrao do projeto
base_dir='/opt/fonts'
sudo chmod 777 ${base_dir}
if [ ! -d "$base_dir" ]; then
    echo "Criando diretorio /opt/easy_lawyer_django..."
    sudo mkdir -p ${base_dir}
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
virtual_env_instalado=`dpkg -l | grep -i python3-virtualenv | awk '{print $1}'`
if [ "$virtual_env_instalado" != "ii" ]; then
    echo "Instalando python-virtualenv..."
    sudo apt-get install python3-virtualenv
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
psql --command="CREATE USER ezl SUPERUSER INHERIT CREATEDB CREATEROLE;" >> /dev/null 2>&1
psql --command="ALTER USER ezl PASSWORD 'ezl';" >> /dev/null 2>&1
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
; senha do do usuario linux responsavel por executar a etl. Este deve estar no grupo sudoers.
linux_password = ${user_passwd}
; usuario admin do django para realizar a importacao
user=2
" > config/general.ini

sudo echo "
[connection]
server = 172.27.155.9
user = Rvnovaes
password = libertas
database = Advwin_ho

# postgresql ou sql_server
db_type = sql_server
" > connections/advwin_ho.cfg


echo "INFORME UMA DAS OPCOES DE AMBIENTE"
valid_op=0
#fixtures = ['country.xml', 'state.xml', 'court_district.xml', 'city.xml', 'type_movement.xml',
#            'type_task.xml']
while [ ${valid_op} -eq 0 ]
do
    echo "1-Demo               2-ETL"
    read -p "Opcao: " op
    valid_op=1
    if [ "${op}" = "1" ]; then
        echo "Rodando migrateions..."
        python3.5 manage.py migrate
        echo "Rodando - factory"
        python3.5 etl/advwin/factory.py
        echo "Criando usuario admin"
        python3.5 manage.py createsuperuser
        echo "Rodando fixtures..."
        python3.5 manage.py loaddata country.xml
        python3.5 manage.py loaddata state.xml
        python3.5 manage.py loaddata court_district.xml
        python3.5 manage.py loaddata city.xml
        python3.5 manage.py loaddata type_movement.xml
        python3.5 manage.py loaddata type_task.xml
        echo "Aplicacao rodando em 127.0.0.1:8000"
        python3.5 manage.py runserver 0.0.0.0:8000
    elif [ "${op}" = "2" ]; then
        echo "Rodando ETL..."
        python3.5 etl/advwin_ezl/luigi_jobs.py
    else
        valid_op=0
        echo "Opcao invalida!"
    fi
done

