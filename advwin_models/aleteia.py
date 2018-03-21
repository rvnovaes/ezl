from sqlalchemy import BigInteger, Boolean, Column, Date, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

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


class AQualidadeBasica(Base):
    __tablename__ = 'a_qualidade_basica'
    id = Column(Integer, primary_key=True)
    date_dim_id = Column(Integer, ForeignKey('d_date.date_dim_id'))
    cod_setor = Column(String(10), nullable=False)
    nome_setor = Column(String(255), nullable=False)
    sem_cliente = Column(Integer, nullable=False)
    sem_outra_parte = Column(Integer, nullable=False)
    sem_setor = Column(Integer, nullable=False)
    sem_numero_processo = Column(Integer, nullable=False)
    sem_comarca = Column(Integer, nullable=False)
    sem_UF = Column(Integer, nullable=False)
    sem_vara = Column(Integer, nullable=False)
    sem_tribunal = Column(Integer, nullable=False)
    sem_fase = Column(Integer, nullable=False)
    sem_valor_causa = Column(Integer, nullable=False)
    data_referencia = relationship('data_referencia', back_populates='qualidade_basica')
