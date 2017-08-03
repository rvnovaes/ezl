from sqlalchemy import Column, VARCHAR, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

AlchemyBaseModel = declarative_base()


#
# table Jurid_Correspondente_Hist
# (
# 	codigo int identity
# 		constraint PK_Jurid_Correspondente_Hist
# 			primary key,
# 	codigo_adv_correspondente varchar(70),
# 	ident_agenda int not null,
# 	status int not null,
# 	data_operacao datetime,
# 	justificativa varchar(1000),
# 	usuario varchar(20),
# 	codigo_adv_solicitante varchar(14),
# 	codigo_adv_origem varchar(14),
# 	ident_agenda_anterior int,
# 	SubStatus int,
# 	descricao varchar(200)
# )


# INSERT INTO Jurid_Correspondente_Hist
#         (codigo_adv_correspondente,
#          usuario,
#          ident_agenda,
#          status,
#          SubStatus,
#          data_operacao,
#          descricao,
#          justificativa)
# VALUES
#         ('cp.cp',
#          'WEB: cp.cp',
#          2254239,
#            0,
#            50,
#            GETDATE(),
#            'Aceita por Correspondente: cp.cp',
#          'aceita iasmini')
#
# UPDATE Jurid_Agenda_Table SET
#         Status_correspondente = 0,
#         prazo_lido = 1,
#         envio_alerta = 0,
#         Ag_statusExecucao ='Em Execucao',
#         data_correspondente = GETDATE(),
#         SubStatus = 50
# WHERE ident = 2254239


# table Jurid_agenda_table
# (
# 	status_correspondente int,
# 	prazo_lido bit default 0 not null,
# 	envio_alerta bit default 0,
# 	Ag_statusExecucao varchar(25),
#   data_correspondente datetime,
#   SubStatus
class CorrespondentHistory(AlchemyBaseModel):
    __tablename__ = 'jurid_Correspondente_Hist'
    person_correspondent = Column('codigo_adv_correspondente', VARCHAR(length=70))
    user = Column('usuario', VARCHAR(length=20))
    task = Column('ident_agenda', Integer, nullable=False)
    status = Column('status', Integer, nullable=False)
    substatus = Column('SubStatus', Integer)
    operation_date = Column('data_operacao', DateTime(True))
    description = Column('descricao', VARCHAR(200))
    justificative = Column('justificativa', VARCHAR(1000))
