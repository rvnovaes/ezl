import datetime
import hashlib
import sys

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from connections.db_connection import connect_db
from etl.advwin_ezl.models import Base, Person, AuthUser
from config.config import get_parser

config_parser = get_parser()
source = dict(config_parser.items('etl'))

def return_user_from_auth(key, auth_dict):
    print("Tamanho auth dict:", len(auth_dict))

    for i in auth_dict:

        if key == i['codigo_adv']:
            print("Achou:", key, i['usuarioLogin'])
            return i['usuarioLogin']

    return ' '


def get_or_create(session, model, kwargs):
    instance_lname = session.query(model).filter(model.legal_name == kwargs['legal_name']).first()
    instance_name = session.query(model).filter(model.name == kwargs['name']).first()

    print("args", kwargs, instance_name, instance_lname)

    if instance_lname is None and instance_name is None:
        print("Adicionado!")
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


def trataAuthUser(linha):
    print(linha)

    if linha['status'] == 'I':
        return None

    if linha['usuarioEmail'] is None:
        linha['usuarioEmail'] = ''

    name = linha['usuarioNome']
    first_name = name.split(' ')[0]
    last_name = " ".join(name.split(' ')[1:])

    if len(last_name) > 30:
        last_name = name.split(' ')[-1]

    return {
        'password': hashlib.md5('usuarioezl2017'.encode('utf8')).hexdigest(),
        'last_login': datetime.datetime.now(),
        'is_superuser': False,
        'username': linha['usuarioLogin'],
        'first_name': first_name,
        'last_name': last_name,
        'email': linha['usuarioEmail'],
        'is_staff': True,
        'is_active': True,
        'date_joined': datetime.datetime.now()
    }


def trataPerson(linha, session, person_type='adv', auth_dict=None):
    date_creation = 0
    active = True
    legal_name = ''
    name = ''
    is_lawyer = False
    is_court = False
    legal_type = 'F'
    cpf_cnpj = ''
    auth_user_id = None
    is_customer = False
    is_supplier = False

    print(linha)

    if person_type == 'adv':

        # print(linha['Correspondente'])
        if linha['Dt_cad'] is not None:

            date_creation = linha['Dt_cad']

        else:

            date_creation = datetime.datetime.now()

        name = linha['Nome']

        if linha['Razao'] is not None:
            legal_name = linha['Razao']

        is_lawyer = True

        if linha['Correspondente'] is True:

            authuser_query = session.query(AuthUser).filter(
                AuthUser.username == return_user_from_auth(linha['Codigo'], auth_dict)).first()

            print("auth_user", authuser_query)

            if authuser_query is not None:
                auth_user_id = authuser_query.id

        cpf_cnpj = linha['Codigo']

        if linha['TipoCF'] == 'A':
            is_customer = True

        elif linha['TipoCF'] == 'F':
            is_supplier = True

    if person_type == 'cliente':

        if linha['Dt_cad'] is not None:

            date_creation = linha['Dt_cad']

        else:

            date_creation = datetime.datetime.now()
        name = linha['Nome']
        if linha['Razao'] is not None:
            legal_name = linha['Razao']

        if linha['pessoa_fisica'] is not True:
            legal_type = 'J'

        cpf_cnpj = linha['Codigo']

        if linha['TipoCF'] == 'A':
            is_customer = True

        elif linha['TipoCF'] == 'F':
            is_supplier = True

    if person_type == 'trib':
        date_creation = datetime.datetime.now()
        name = linha['Descricao']
        legal_name = linha['Descricao']
        is_court = True
        legal_type = 'J'

    linha = {
        'create_date': date_creation,
        'alter_date': None,
        'is_active': active,
        'legal_name': legal_name,
        'name': name,
        'is_lawyer': is_lawyer,
        'is_court': is_court,
        'legal_type': legal_type,
        'cpf_cnpj': cpf_cnpj,
        'alter_user_id': None,
        'auth_user_id': auth_user_id,
        'create_user_id': 2,
        'is_customer': is_customer,
        'is_supplier': is_supplier

    }

    return linha


def retorna_campos_consulta(cursor):
    columns = cursor.keys()

    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))

        # print (results)
    return results


def insere_user(session, linha):
    user_linha = AuthUser(**linha)
    # get_or_create(session, AuthUser, linha)
    session.add(user_linha)
    session.commit()


def insere_person(session, linha):
    person_linha = Person(**linha)
    get_or_create(session, Person, linha)

engine_ezl = connect_db(config_parser, 'django_application')  # conexao com o banco aleteia --usar configparser
engine_advwin = connect_db(config_parser, source['connection_name'])  # arquivo de conexao do advwin

Base.metadata.create_all(engine_ezl)
session_ezl = sessionmaker(bind=engine_ezl)()

sql_str_cliente = text(
    'select * from Jurid_Clifor where Status=\'Ativo\' and Codigo not in (select Jurid_CliFor.Codigo from Jurid_CliFor inner join Jurid_advogado on (Jurid_advogado.Codigo = Jurid_Clifor.Codigo));')  # top 1 apenas para testes
sql_str_advogado = text(
    'select Jurid_Advogado.*,Jurid_CliFor.TipoCF from Jurid_Advogado left join Jurid_clifor on (Jurid_advogado.Codigo = Jurid_Clifor.Codigo) where Jurid_Advogado.Status = \'Ativo\';')
sql_str_tribunais = text('select * from Jurid_Tribunais;')
sql_str_advweb = text(
    'select advweb_usuario.* from advweb_usuario inner join Jurid_Advogado on (advweb_usuario.codigo_adv = Jurid_advogado.codigo) where Jurid_Advogado.Correspondente = \'1\' and Jurid_Advogado.Status = \'Ativo\';')

consultas_advwin = [sql_str_advogado, sql_str_cliente, sql_str_tribunais]
consultas_tipo = ['adv', 'cliente', 'trib']

# consultas_advwin = [sql_str_advogado]
# consultas_tipo = ['adv']

cursor = engine_advwin.execute(sql_str_advweb)
result_consulta_usuario = retorna_campos_consulta(cursor)

for i in range(len(consultas_advwin)):

    cursor = engine_advwin.execute(consultas_advwin[i])
    result_consulta = retorna_campos_consulta(cursor)

    print("Criando tabela: ", consultas_tipo[i], len(result_consulta))

    n = 1
    for j in result_consulta:

        if consultas_tipo[i] != 'usuario':

            person = trataPerson(j, session_ezl, consultas_tipo[i], result_consulta_usuario)

            if person is not None:
                print("Adicionado: ", n, "advogados")
                insere_person(session_ezl, person)
                n += 1

        else:

            user = trataAuthUser(j)

            if user is not None:
                insere_user(session_ezl, user)
