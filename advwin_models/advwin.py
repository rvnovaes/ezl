# coding: utf-8
from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, LargeBinary, SmallInteger, String, Text, \
    text
from sqlalchemy.dialects.mssql.base import BIT, MONEY
from sqlalchemy.ext.declarative import declarative_base

# http://stackoverflow.com/questions/34675604/sqlacodegen-generates-mixed-models-and-tables --> Para gerar as classes é preciso comentar algumas linhas
# do sqlacodegen conforme explicado acima, uma vez que ele não gera mapas para tabelas sem PK
# sqlacodegen.exe - -noinflect mssql+pymssql://Rvnovaes:password@172.27.155.22:1433/Advwin > models_sqlacodegen_advwin_hack.py
Base = declarative_base()
metadata = Base.metadata


class JuridDistribuicao(Base):
    __tablename__ = 'Jurid_Distribuicao'
    __table_args__ = (Index(
        'D_Distribuicao',
        'Codigo_Comp',
        'D_Codigo_Inst',
        'D_NumPrc',
        unique=True), )

    # http://docs.sqlalchemy.org/en/latest/faq/ormconfiguration.html#how-do-i-map-a-table-that-has-no-primary-key
    # Declarei esta coluna como PK uma vez que é a melhor candidata por não se repetir e ser unique
    D_Codigo = Column(Integer, nullable=False, unique=True, primary_key=True)
    Codigo_Comp = Column(
        String(20, 'Latin1_General_CI_AS'), nullable=False, index=True)
    D_Codigo_Inst = Column(String(10, 'Latin1_General_CI_AS'), nullable=False)
    D_NumPrc = Column(String(50, 'Latin1_General_CI_AS'), index=True)
    D_Data_Ent = Column(DateTime)
    D_Data_Sai = Column(DateTime)
    D_Atual = Column(BIT, nullable=False, server_default=text("(0)"))
    D_Tribunal = Column(String(30, 'Latin1_General_CI_AS'))
    D_Vara = Column(String(5, 'Latin1_General_CI_AS'))
    D_Obs = Column(String(254, 'Latin1_General_CI_AS'))
    D_UF = Column(String(2, 'Latin1_General_CI_AS'))
    D_Comarca = Column(String(40, 'Latin1_General_CI_AS'))
    D_Protocolo = Column(String(30, 'Latin1_General_CI_AS'), index=True)
    hectares = Column(Float(53))
    d_ultimo_evento = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    d_data_ult_evento = Column(DateTime)
    cod_vara = Column(String(2, 'Latin1_General_CI_AS'))
    num_vara = Column(Integer)
    SiglaIsisRobot = Column(String(10, 'Latin1_General_CI_AS'))
    D_NumPrc_Sonumeros = Column(String(50, 'Latin1_General_CI_AS'), index=True)
    D_Protocolo_Sonumeros = Column(
        String(30, 'Latin1_General_CI_AS'), index=True)
    IsisRobotID = Column(Integer)
    IsisDataUlt = Column(DateTime)
    ChaveIsisRobot = Column(String(100, 'Latin1_General_CI_AS'))
    chaveSync = Column(String(200, 'Latin1_General_CI_AS'))
    id_pasta = Column(Integer, index=True)
    Situacao = Column(String(60, 'Latin1_General_CI_AS'))
    IsisErro = Column(BIT, server_default=text("((0))"))
    IsisMsg = Column(String(200, 'Latin1_General_CI_AS'))
    CodMov = Column(String(20, 'Latin1_General_CI_AS'))


class JuridGedMain(Base):
    # SEM PK - usei ID_doc por ser unique, not null e sequencial

    __tablename__ = 'Jurid_Ged_Main'
    __table_args__ = (Index('IX_Jurid_Ged_Main_Responsavel', 'Responsavel',
                            'Link', 'ID_doc', 'Arq_Versao'), {
                                'implicit_returning': False
                            })
    Tabela_OR = Column(String(60, 'Latin1_General_CI_AS'))
    Codigo_OR = Column(String(50, 'Latin1_General_CI_AS'), index=True)
    Id_OR = Column(Integer)
    Descricao = Column(String(255, 'Latin1_General_CI_AS'))
    Link = Column(String(450, 'Latin1_General_CI_AS'))
    ID_doc = Column(Integer, nullable=False, unique=True, primary_key=True)
    Data = Column(DateTime)
    Nome = Column(String(255, 'Latin1_General_CI_AS'))
    Responsavel = Column(String(50, 'Latin1_General_CI_AS'), nullable=False)
    Unidade = Column(String(50, 'Latin1_General_CI_AS'))
    Seguranca = Column(String(50, 'Latin1_General_CI_AS'))
    Arquivo = Column(LargeBinary)
    Arq_tipo = Column(String(40, 'Latin1_General_CI_AS'))
    Arq_Versao = Column(Integer, nullable=False, server_default=text("(0)"))
    Arq_Status = Column(
        String(30, 'Latin1_General_CI_AS'),
        nullable=False,
        server_default=text("('N_Processado')"))
    Arq_usuario = Column(String(100, 'Latin1_General_CI_AS'))
    Arq_nick = Column(String(500, 'Latin1_General_CI_AS'))
    Data_morto = Column(DateTime)
    PagIni = Column(Integer)
    PagFim = Column(Integer)
    Texto = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    Obs = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    chaveSync = Column(String(200, 'Latin1_General_CI_AS'))
    id_pasta = Column(Integer)


class JuridGEDLig(Base):
    __tablename__ = 'Jurid_GEDLig'
    __table_args__ = ({'implicit_returning': False}, )
    ID_lig = Column(Integer, nullable=False, unique=True, primary_key=True)
    Id_tabela_or = Column(String(60, 'Latin1_General_CI_AS'))
    Id_codigo_or = Column(String(60, 'Latin1_General_CI_AS'))
    Id_id_doc = Column(Integer)
    id_ID_or = Column(Integer)
    dt_inserido = Column(DateTime)
    usuario_insercao = Column(String(60, 'Latin1_General_CI_AS'))


class JuridPastas(Base):
    # SEM PK - USEI Codigo_Comp por ser unique

    __tablename__ = 'Jurid_Pastas'
    __table_args__ = (Index(
        'IDX_Jurid_Pastas_001', 'Cliente', 'Unidade', 'Codigo_Comp', 'Dt_Cad',
        'Status', 'Comarca', 'UF', 'Tribunal', 'NumPrc1', 'ValorCausa',
        'ValorPCausa', 'Dt_Saida', 'TipoP', 'FaseP', 'PRConta', 'Planta',
        'Varas', 'RefCliente', 'Config3', 'Dt_RefValor', 'id_pasta',
        'PA_Workflowstatus', 'PA_WSub_Descricao', 'PA_DT_INSERIDO'),
                      Index('IX_Jurid_Pastas_Advogado_id_pasta', 'Advogado',
                            'id_pasta'),
                      Index('IX_Jurid_Pastas_Cliente_id_pasta', 'Cliente',
                            'id_pasta'))

    Codigo = Column(String(10, 'Latin1_General_CI_AS'), nullable=False)
    Numero = Column(String(15, 'Latin1_General_CI_AS'), nullable=False)
    # http://docs.sqlalchemy.org/en/latest/faq/ormconfiguration.html#how-do-i-map-a-table-that-has-no-primary-key
    # Declarei esta coluna como PK uma vez que é a melhor candidata por não se repetir e ser unique
    Codigo_Comp = Column(
        String(20, 'Latin1_General_CI_AS'), unique=True, primary_key=True)
    Dt_Cad = Column(DateTime)
    Cliente = Column(
        String(14, 'Latin1_General_CI_AS'), nullable=False, index=True)
    Descricao = Column(String(90, 'Latin1_General_CI_AS'))
    Advogado = Column(String(14, 'Latin1_General_CI_AS'))
    Filer = Column(String(55, 'Latin1_General_CI_AS'))
    Obs = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    Status = Column(
        String(15, 'Latin1_General_CI_AS'),
        index=True,
        server_default=text("('Ativa')"))
    Local = Column(String(35, 'Latin1_General_CI_AS'))
    Cad_Por = Column(String(8, 'Latin1_General_CI_AS'))
    Comarca = Column(String(40, 'Latin1_General_CI_AS'))
    UF = Column(String(2, 'Latin1_General_CI_AS'))
    Instancia = Column(String(10, 'Latin1_General_CI_AS'))
    Tribunal = Column(String(30, 'Latin1_General_CI_AS'))
    Unidade = Column(String(20, 'Latin1_General_CI_AS'))
    StatusPrc = Column(
        String(15, 'Latin1_General_CI_AS'), server_default=text("('Ativo')"))
    NumPrc1 = Column(String(40, 'Latin1_General_CI_AS'), index=True)
    NumPrc2 = Column(String(40, 'Latin1_General_CI_AS'))
    NumPrc3 = Column(String(40, 'Latin1_General_CI_AS'))
    DataPrazo = Column(DateTime)
    Psucesso = Column(String(50, 'Latin1_General_CI_AS'))
    ValorCausa = Column(MONEY)
    ValorPCausa = Column(MONEY)
    OutraParte = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    Setor = Column(String(10, 'Latin1_General_CI_AS'))
    Volumes = Column(Integer)
    GeraFt = Column(Integer, server_default=text("(0)"))
    GeraDb = Column(Integer, server_default=text("(0)"))
    GeraPz = Column(Integer, server_default=text("(0)"))
    Escritorio = Column(String(14, 'Latin1_General_CI_AS'))
    Dt_distr_1 = Column(DateTime)
    Dt_distr_2 = Column(DateTime)
    Dt_distr_3 = Column(DateTime)
    Tribunal_1 = Column(String(30, 'Latin1_General_CI_AS'))
    Tribunal_2 = Column(String(30, 'Latin1_General_CI_AS'))
    Tribunal_3 = Column(String(30, 'Latin1_General_CI_AS'))
    Dt_Saida = Column(DateTime)
    Dtv_Num_1 = Column(String(40, 'Latin1_General_CI_AS'))
    Dtv_Num_2 = Column(String(40, 'Latin1_General_CI_AS'))
    Dtv_Num_3 = Column(String(40, 'Latin1_General_CI_AS'))
    Dtv_ChecaP_1 = Column(Integer)
    Dtv_ChecaP_2 = Column(Integer)
    Dtv_ChecaP_3 = Column(Integer)
    Dt_UltCheck = Column(DateTime)
    Moeda = Column(String(5, 'Latin1_General_CI_AS'))
    TipoP = Column(String(25, 'Latin1_General_CI_AS'))
    FaseP = Column(String(25, 'Latin1_General_CI_AS'))
    PRConta = Column(String(50, 'Latin1_General_CI_AS'))
    ValorCond = Column(MONEY)
    ValorFinal = Column(MONEY)
    Juiz = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    TipoDemanda = Column(String(20, 'Latin1_General_CI_AS'))
    Contrato = Column(String(30, 'Latin1_General_CI_AS'))
    Moeda_Correcao = Column(String(5, 'Latin1_General_CI_AS'))
    ADV_OUTRAPARTE = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    Planta = Column(String(80, 'Latin1_General_CI_AS'))
    Varas = Column(String(5, 'Latin1_General_CI_AS'))
    Varas_1 = Column(String(5, 'Latin1_General_CI_AS'))
    Varas_2 = Column(String(5, 'Latin1_General_CI_AS'))
    Varas_3 = Column(String(5, 'Latin1_General_CI_AS'))
    Cod_Migra = Column(String(30, 'Latin1_General_CI_AS'))
    Rito = Column(String(80, 'Latin1_General_CI_AS'))
    Dt_CalcArbitrado = Column(DateTime)
    Dt_CalcPrevisto = Column(DateTime)
    Litis = Column(BIT, nullable=False, server_default=text("(0)"))
    RefCliente = Column(String(35, 'Latin1_General_CI_AS'), index=True)
    esfera = Column(String(20, 'Latin1_General_CI_AS'))
    NumPrc4 = Column(String(40, 'Latin1_General_CI_AS'))
    Dt_Distr_4 = Column(DateTime)
    Tribunal_4 = Column(String(30, 'Latin1_General_CI_AS'))
    Varas_4 = Column(String(5, 'Latin1_General_CI_AS'))
    NumProto_4 = Column(String(30, 'Latin1_General_CI_AS'))
    NumProto_3 = Column(String(30, 'Latin1_General_CI_AS'))
    Status_Arquivo = Column(String(15, 'Latin1_General_CI_AS'))
    VolumePasta = Column(String(20, 'Latin1_General_CI_AS'))
    OutraParte_Tab = Column(
        String(15, 'Latin1_General_CI_AS'), server_default=text("(null)"))
    AdvogadoSocio = Column(String(14, 'Latin1_General_CI_AS'))
    Config1 = Column(String(100, 'Latin1_General_CI_AS'))
    Config2 = Column(String(100, 'Latin1_General_CI_AS'))
    Config3 = Column(String(100, 'Latin1_General_CI_AS'))
    Documento = Column(String(255, 'Latin1_General_CI_AS'))
    Estrategia = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    InfComplementares = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    codigo_formato = Column(SmallInteger)
    valor_formato_1 = Column(String(255, 'Latin1_General_CI_AS'))
    valor_formato_2 = Column(String(255, 'Latin1_General_CI_AS'))
    valor_formato_3 = Column(String(255, 'Latin1_General_CI_AS'))
    valor_formato_4 = Column(String(255, 'Latin1_General_CI_AS'))
    valor_formato_5 = Column(String(255, 'Latin1_General_CI_AS'))
    valor_formato_6 = Column(String(255, 'Latin1_General_CI_AS'))
    valor_formato_7 = Column(String(255, 'Latin1_General_CI_AS'))
    valor_formato_8 = Column(String(255, 'Latin1_General_CI_AS'))
    valor_formato_9 = Column(String(255, 'Latin1_General_CI_AS'))
    valor_formato_10 = Column(String(255, 'Latin1_General_CI_AS'))
    valor_formato_11 = Column(String(255, 'Latin1_General_CI_AS'))
    valor_formato_12 = Column(String(255, 'Latin1_General_CI_AS'))
    valor_formato_13 = Column(String(255, 'Latin1_General_CI_AS'))
    valor_formato_14 = Column(String(255, 'Latin1_General_CI_AS'))
    valor_formato_15 = Column(String(255, 'Latin1_General_CI_AS'))
    tributo = Column(String(15, 'Latin1_General_CI_AS'))
    polo = Column(Integer)
    Dt_RefValor = Column(DateTime)
    vedado_substabelecimento = Column(BIT, server_default=text("(0)"))
    cod_varas = Column(String(2, 'Latin1_General_CI_AS'))
    num_varas = Column(Integer)
    cod_varas_1 = Column(String(2, 'Latin1_General_CI_AS'))
    num_varas_1 = Column(Integer)
    cod_varas_2 = Column(String(2, 'Latin1_General_CI_AS'))
    num_varas_2 = Column(Integer)
    cod_varas_3 = Column(String(2, 'Latin1_General_CI_AS'))
    num_varas_3 = Column(Integer)
    cod_varas_4 = Column(String(2, 'Latin1_General_CI_AS'))
    num_varas_4 = Column(Integer)
    status_emprestimo = Column(String(20, 'Latin1_General_CI_AS'))
    ativopassivo = Column(String(20, 'Latin1_General_CI_AS'))
    sintese_processo = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    objeto_desc = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    naocobra = Column(BIT, server_default=text("(0)"))
    litisconsorcio = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    emprestada = Column(BIT)
    sinistro = Column(String(100, 'Latin1_General_CI_AS'))
    estipulante = Column(String(250, 'Latin1_General_CI_AS'))
    risco1 = Column(MONEY)
    risco2 = Column(MONEY)
    Anotacao_relatorio = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    pasta_confidencial = Column(BIT)
    AdvCorresp = Column(String(14, 'Latin1_General_CI_AS'))
    TipoCaso = Column(String(25, 'Latin1_General_CI_AS'))
    ContratoPUC = Column(String(30, 'Latin1_General_CI_AS'))
    DataVencimentoPUC = Column(DateTime)
    NumPrc1_Sonumeros = Column(String(40, 'Latin1_General_CI_AS'), index=True)
    UsaISIS = Column(BIT, server_default=text("((0))"))
    chaveSync = Column(String(200, 'Latin1_General_CI_AS'))
    UltSincronia = Column(DateTime)
    Cod_Regra = Column(Integer)
    id_pasta = Column(Integer, nullable=False, index=True)
    PA_Workflowstatus = Column(
        Integer, nullable=False, index=True, server_default=text("((0))"))
    PA_WSub_Descricao = Column(
        ForeignKey('Jurid_pastas_Workflow_subStatus.WSub_descricao'))
    PA_Work_datalimite = Column(DateTime)
    PA_DT_INSERIDO = Column(DateTime, server_default=text("(getdate())"))
    PrcDigital = Column(BIT, server_default=text("((0))"))
    PrcEstrategico = Column(BIT, server_default=text("((0))"))
    nr_pasta_temp = Column(String(20, 'Latin1_General_CI_AS'))

    def __repr__(self):
        return "Pasta: Codigo_Comp={0}, Status={1}".format(
            self.Codigo_Comp, self.Status)

        # Jurid_pastas_Workflow_subStatus = relationship('JuridPastasWorkflowSubStatus')


class JuridProcMov(Base):
    # Sem PK - Usei Ident por ser IDENTITY
    __tablename__ = 'Jurid_ProcMov'
    __table_args__ = (Index('IX_Jurid_ProcMov_Ident', 'Ident', 'CodMov'),
                      Index('IX_Jurid_ProcMov_CodMov_Data_Mov2', 'CodMov',
                            'Data_Mov', 'Codigo_Comp'),
                      Index('Idx_Ordem', 'Codigo_Comp', 'Data', 'Ident'),
                      Index('IX_Jurid_ProcMov_Ident1', 'Ident', 'CodMov'))

    Codigo_Comp = Column(
        String(20, 'Latin1_General_CI_AS'), nullable=False, index=True)
    Data = Column(DateTime, nullable=False, index=True)
    Advogado = Column(String(14, 'Latin1_General_CI_AS'), index=True)
    CodMov = Column(
        String(15, 'Latin1_General_CI_AS'), nullable=False, index=True)
    Valor = Column(MONEY)
    Documento = Column(String(400, 'Latin1_General_CI_AS'))
    MCliente = Column(BIT, nullable=False, server_default=text("(1)"))
    Descricao = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    Prazo = Column(DateTime)
    Descisao = Column(String(15, 'Latin1_General_CI_AS'))
    Debite = Column(Integer)
    FichaT = Column(Integer)
    Ident = Column(Integer, primary_key=True, nullable=False)
    Tribunal = Column(String(30, 'Latin1_General_CI_AS'))
    Arquivado = Column(BIT, nullable=False, server_default=text("(0)"))
    Exportado = Column(String(2, 'Latin1_General_CI_AS'), index=True)
    M_Distribuicao = Column(Integer)
    Data_Mov = Column(DateTime, server_default=text("(getdate())"))
    Obs_expl = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    moeda_correcao = Column(String(5, 'Latin1_General_CI_AS'))
    documento_criado = Column(BIT, nullable=False, server_default=text("(0)"))
    faturada = Column(BIT, nullable=False, server_default=text("(0)"))
    fatura = Column(String(12, 'Latin1_General_CI_AS'))
    D_Codigo = Column(Integer, index=True)
    codigo_hist_isis = Column(Integer)
    chaveSync = Column(String(200, 'Latin1_General_CI_AS'))
    id_pasta = Column(Integer)
    prazo_origem = Column(Integer)
    regraHist = Column(BIT)


class JuridAgendaTable(Base):
    __tablename__ = 'Jurid_agenda_table'
    __table_args__ = (Index('IX_Jurid_agenda_table_Advogado_Status',
                            'Advogado', 'Status'), )

    Pasta = Column(String(70, 'Latin1_General_CI_AS'), index=True)
    Mov = Column(Integer)
    Advogado = Column(String(14, 'Latin1_General_CI_AS'), index=True)
    Data = Column(DateTime, nullable=False, server_default=text("(getdate())"))
    Data_Prazo = Column(DateTime, nullable=False, index=True)
    CodMov = Column(String(15, 'Latin1_General_CI_AS'))
    Obs = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    Status = Column(Integer, index=True, server_default=text("(0)"))
    Ident = Column(Integer, nullable=False, index=True, primary_key=True)
    Advogado_or = Column(String(14, 'Latin1_General_CI_AS'), index=True)
    Data_Fech = Column(DateTime)
    Aviso_dias = Column(Integer)
    Unidade = Column(String(20, 'Latin1_General_CI_AS'))
    valor_agenda = Column(MONEY)
    prazo_lido = Column(BIT, nullable=False, server_default=text("(0)"))
    prazo_fatal = Column(DateTime)
    Prazo_Interm = Column(BIT, nullable=False, server_default=text("(0)"))
    AG_tipo = Column(Integer, nullable=False, server_default=text("(0)"))
    AG_Setor = Column(String(10, 'Latin1_General_CI_AS'))
    Ag_Prioridade = Column(Integer, server_default=text("(5)"))
    Ag_StatusExecucao = Column(String(25, 'Latin1_General_CI_AS'))
    Data_prazoFim = Column(DateTime)
    Ag_EOS = Column(Integer, nullable=False, server_default=text("(0)"))
    Fatura = Column(String(20, 'Latin1_General_CI_AS'))
    P_Cliente = Column(String(50, 'Latin1_General_CI_AS'))
    CodAdvogadoEMail = Column(String(14, 'Latin1_General_CI_AS'))
    chaveSync = Column(String(200, 'Latin1_General_CI_AS'))
    id_pasta = Column(Integer)
    status_correspondente = Column(Integer)
    checkin_codigo_advogado = Column(String(14, 'Latin1_General_CI_AS'))
    checkout_codigo_advogado = Column(String(14, 'Latin1_General_CI_AS'))
    foto_a = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    foto_b = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    foto_c = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    Advogado_sol = Column(String(14, 'Latin1_General_CI_AS'))
    SubStatus = Column(Integer)
    BackOffice = Column(BIT)
    formulario_id = Column(String(40, 'Latin1_General_CI_AS'))
    valor_faturado = Column(MONEY)
    Data_delegacao = Column(DateTime)
    Data_correspondente = Column(DateTime)
    Data_cumprimento = Column(DateTime)
    Data_criacao = Column(DateTime)
    Data_backoffice = Column(DateTime)
    Data_confirmacao = Column(DateTime)
    envio_alerta = Column(BIT, server_default=text("((0))"))
    lat_cumpri_prazo = Column(
        Float(24), nullable=False, server_default=text("((0))"))
    lon_cumpri_prazo = Column(
        Float(24), nullable=False, server_default=text("((0))"))


class JuridCorrespondenteHist(Base):
    __tablename__ = 'Jurid_Correspondente_Hist'
    __table_args__ = {
        'implicit_returning': False
    }  # Não remover cancela o OUTPUT devido a trigger para envio de email do advwin
    codigo = Column(Integer, primary_key=True, autoincrement=True)
    codigo_adv_correspondente = Column(String(70, 'Latin1_General_CI_AS'))
    ident_agenda = Column(Integer)
    status = Column(Integer, nullable=False)
    data_operacao = Column(DateTime)
    justificativa = Column(String(1000, 'Latin1_General_CI_AS'))
    usuario = Column(String(20, 'Latin1_General_CI_AS'))
    codigo_adv_solicitante = Column(String(14, 'Latin1_General_CI_AS'))
    codigo_adv_origem = Column(String(14, 'Latin1_General_CI_AS'))
    ident_agenda_anterior = Column(Integer)
    SubStatus = Column(Integer)
    descricao = Column(String(200, 'Latin1_General_CI_AS'))


class JuridFMAlvaraCorrespondente(Base):
    __tablename__ = 'Jurid_FM_alvaraCorrespondente'

    id = Column(Integer, primary_key=True, autoincrement=True)
    versao = Column(String(10, 'Latin1_General_CI_AS'), nullable=False)
    agenda_id = Column(Integer, nullable=False)
    alvaraRetiradoAutos = Column(String(255, 'Latin1_General_CI_AS'))
    viaOriginalEnviada = Column(String(255, 'Latin1_General_CI_AS'))
    dataRetiradoAutos = Column(DateTime)
    justAlvaraNRetirado = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    alvaraLevadoBanco = Column(String(255, 'Latin1_General_CI_AS'))
    vlrLevantadoBanco = Column(MONEY)
    contaLevantamento = Column(String(255, 'Latin1_General_CI_AS'))
    justAlvaraNLevantado = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    despReembolsaveis = Column(String(255, 'Latin1_General_CI_AS'))
    obsRelevantes = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    status = Column(Integer)
    paginas = Column(String(255, 'Latin1_General_CI_AS'))


class JuridFMAudienciaCorrespondente(Base):
    __tablename__ = 'Jurid_FM_audienciaCorrespondente'

    id = Column(Integer, primary_key=True, autoincrement=True)
    versao = Column(String(10, 'Latin1_General_CI_AS'), nullable=False)
    agenda_id = Column(Integer, nullable=False)
    comparecimentoAudiencia = Column(String(255, 'Latin1_General_CI_AS'))
    audienciaRealizada = Column(String(255, 'Latin1_General_CI_AS'))
    tipoComparecimento = Column(String(255, 'Latin1_General_CI_AS'))
    orientacaoAcordo = Column(String(255, 'Latin1_General_CI_AS'))
    acordoRealizado = Column(String(255, 'Latin1_General_CI_AS'))
    valorDanoMoral = Column(MONEY)
    valorDanoMaterial = Column(MONEY)
    devolucaoProduto = Column(String(255, 'Latin1_General_CI_AS'))
    reparo = Column(String(255, 'Latin1_General_CI_AS'))
    trocaProduto = Column(String(255, 'Latin1_General_CI_AS'))
    justificativaNAcordo = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    tipoProcesso = Column(String(255, 'Latin1_General_CI_AS'))
    temAdvHabilitado = Column(String(255, 'Latin1_General_CI_AS'))
    advHabilitado = Column(String(255, 'Latin1_General_CI_AS'))
    obsRelevantes = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    despReembolsaveis = Column(String(255, 'Latin1_General_CI_AS'))
    justNCompAudiencia = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    status = Column(Integer)
    paginas = Column(String(255, 'Latin1_General_CI_AS'))


class JuridFMDiligenciaCorrespondente(Base):
    __tablename__ = 'Jurid_FM_diligenciaCorrespondente'

    id = Column(Integer, primary_key=True, autoincrement=True)
    versao = Column(String(10, 'Latin1_General_CI_AS'))
    agenda_id = Column(Integer, nullable=False)
    cumprimento = Column(String(255, 'Latin1_General_CI_AS'))
    docLegivel = Column(String(255, 'Latin1_General_CI_AS'))
    despReembolsaveis = Column(String(255, 'Latin1_General_CI_AS'))
    obsRelevantes = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    motivoCumprimentoParcial = Column(String(255, 'Latin1_General_CI_AS'))
    justificativaNCumprimento = Column(
        Text(2147483647, 'Latin1_General_CI_AS'))
    status = Column(Integer)
    paginas = Column(String(255, 'Latin1_General_CI_AS'))


class JuridFMProtocoloCorrespondente(Base):
    __tablename__ = 'Jurid_FM_protocoloCorrespondente'

    id = Column(Integer, primary_key=True, autoincrement=True)
    versao = Column(String(10, 'Latin1_General_CI_AS'))
    agenda_id = Column(Integer, nullable=False)
    protocoloRealizado = Column(String(255, 'Latin1_General_CI_AS'))
    dataProtocolo = Column(DateTime)
    despReembolsaveis = Column(String(255, 'Latin1_General_CI_AS'))
    obsRelevantes = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    justificativaNProtocolo = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    status = Column(Integer)
    paginas = Column(String(255, 'Latin1_General_CI_AS'))
