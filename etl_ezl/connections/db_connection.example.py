from enum import Enum
from models.advwin import JuridPastas
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import configparser


class DbType(Enum):
    POSTGRESQL = 1
    SQL_SERVER = 2


def connect_db(config_file):
    parser = configparser.ConfigParser()
    parser.read(config_file)
    source = dict(parser.items('connection'))

    server = source['server']
    user = source['user']
    password = source['password']
    database = source['database']
    db_type = source['db_type']

    driver = ''
    # indica o driver de acordo com o banco configurado
    if db_type == DbType.SQL_SERVER.name.lower():
        driver = 'mssql+pymssql'
    elif db_type == DbType.POSTGRESQL.name.lower():
        driver = 'postgresql'

    # monta string de conexao
    url = driver + '://{0}:{1}@{2}/{3}'.format(user, password, server, database)
    engine = create_engine(url, echo=True)

    Session = sessionmaker(bind=engine)
    session = Session()

    pastas = session.query(JuridPastas).filter_by(Codigo_Comp='00002-009978').all()
    for pasta in pastas:
        print(pasta)
