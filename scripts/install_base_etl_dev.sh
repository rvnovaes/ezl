#!/bin/bash

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




# Diretorio padrao para execucao do projeto do zero
base_dir='/opt/easy_lawyer_teste'
dir=$base_dir/teste_`date +'%Y%m%d%H%M%S'`

if [ ! -d "$dir" ]; then
    sudo mkdir -p $dir
fi
sudo chmod 777 $dir
cd $dir

# Clonando o repositorio
hg clone https://thiago_1992@bitbucket.org/marcelotostes/easy_lawyer_django

# Criando ambiente virtual
sudo apt-get install python-virtualenv
virtualenv -p python3.5 venv
source venv/bin/activate
cd $dir/easy_lawyer_django

# Instalando libs indispensaveis ao projeto
pip3.5 install -r requirements.txt

# Criando banco de teste
db=ezl_teste_`date +'%Y%m%d%H%M%S'`
createdb -U ezl $db
psql --username=ezl --dbname=$db --command="CREATE EXTENSION unaccent;"

# Criando local_settings para configuracao local do projeto
sudo touch ezl/local_settings.py
sudo chmod 777 ezl/local_settings.py
sudo echo "
DEBUG = True

DATABASES = {

    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '$db',
        'USER': 'ezl',
        'PASSWORD': 'ezl',
        'HOST': '127.0.0.1',
        'PORT': '5432'
    }
}
# Os password validators sao usados para impor requisitos de seguranca as senhas.
# Na maquina local, nao eh necessario usar nenhum validator alem do MinimumLengthValidator
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 1,
        }
    },
]" > ezl/local_settings.py

# Rodando migrate do banco
python3.5 manage.py migrate

# Matando processos de ETL em execucao
sudo killall luigid
sudo kill -9 `ps -aux | grep -i luigi_jobs.py | awk {'print $2'} | head -1`

# Configurando a ETL
sudo echo "
[connection]
server = 172.27.155.9
user = Rvnovaes
password = libertas
database = Advwin_ho

# postgresql ou sql_server
db_type = sql_server
" > connections/advwin_ho.cfg

# Rodando ETL

msg="Informe a senha do usuario `whoami`"
echo $msg
read -s -p 'senha: ' senha
python3.5 etl/advwin_ezl/luigi_jobs.py -p=$senha

# Rodando o projeto
python3.5 manage.py runserver 0.0.0.0:8004



