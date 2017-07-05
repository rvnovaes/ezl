import datetime
import json
import sys

from sqlalchemy.orm import sessionmaker

from connections.db_connection import connect_db
from etl.advwin.models import Base, City, State, CourtDistrict


def trataCidade(linha, session):
    comarca_id = None

    nome_estado = linha['state_name']
    nome_cidade = linha['name']
    state_query = session.query(State).filter(State.name == nome_estado).first()
    estado_id = state_query.id

    courtdist_query = session.query(CourtDistrict).filter(CourtDistrict.name == nome_cidade).first()
    if courtdist_query:
        comarca_id = courtdist_query.id

    return {
        'create_date': datetime.datetime.now(),
        'alter_date': None,
        'active': True,
        'name': nome_cidade,
        'alter_user_id': None,
        'court_district_id': comarca_id,
        'create_user_id': 2,
        'state_id': estado_id
    }


def insere_cidade(session, linha):
    cidade_linha = City(**linha)
    session.add(cidade_linha)
    session.commit()


ezl_file_path = sys.argv[1]
engine_ezl = connect_db(ezl_file_path)  # conexao com o banco aleteia --usar configparser

Base.metadata.create_all(engine_ezl)
session_ezl = sessionmaker(bind=engine_ezl)()

cities_file_path = sys.argv[2]

with open(cities_file_path) as data_file:
    data = json.load(data_file)

for i in data:
    cidade = trataCidade(i, session_ezl)
    print("cidade:", cidade)
    insere_cidade(session_ezl, cidade)
