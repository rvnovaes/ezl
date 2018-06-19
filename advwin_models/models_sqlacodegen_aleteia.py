# coding: utf-8
from sqlalchemy import BigInteger, Boolean, Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class DData(Base):
    __tablename__ = 'd_data'

    data_dim_id = Column(Integer, primary_key=True)
    data = Column(Date, nullable=False, index=True)
    epoch = Column(BigInteger, nullable=False)
    nome_do_dia = Column(String(15), nullable=False)
    dia_da_semana = Column(Integer, nullable=False)
    dia_do_mes = Column(Integer, nullable=False)
    dia_do_trimestre = Column(Integer, nullable=False)
    dia_do_ano = Column(Integer, nullable=False)
    semana_do_mes = Column(Integer, nullable=False)
    semana_do_ano = Column(Integer, nullable=False)
    semana_do_ano_iso = Column(String(10), nullable=False)
    mes = Column(Integer, nullable=False)
    nome_do_mes = Column(String(9), nullable=False)
    nome_do_mes_abreviado = Column(String(3), nullable=False)
    trimestre = Column(Integer, nullable=False)
    nome_do_trimestre = Column(String(9), nullable=False)
    ano = Column(Integer, nullable=False)
    primeiro_dia_da_semana = Column(Date, nullable=False)
    ultimo_dia_da_semana = Column(Date, nullable=False)
    primeiro_dia_do_mes = Column(Date, nullable=False)
    ultimo_dia_do_mes = Column(Date, nullable=False)
    primeiro_dia_do_trimestre = Column(Date, nullable=False)
    ultimo_dia_do_trimestre = Column(Date, nullable=False)
    primeiro_dia_do_ano = Column(Date, nullable=False)
    ultimo_dia_do_ano = Column(Date, nullable=False)
    mmyyyy = Column(String(6), nullable=False)
    ddmmyyyy = Column(String(10), nullable=False)
    indicador_fds = Column(Boolean, nullable=False)
