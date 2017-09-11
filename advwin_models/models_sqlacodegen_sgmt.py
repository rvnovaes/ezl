# coding: utf-8
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Table, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
metadata = Base.metadata


class Afastamento(Base):
    __tablename__ = 'afastamento'

    id = Column(Integer, primary_key=True)
    funcionario_id = Column(ForeignKey('funcionario.id'))
    tipoafastamento_id = Column(ForeignKey('tipoafastamento.id'))
    datainicio = Column(Date)
    datafim = Column(Date)

    funcionario = relationship('Funcionario')
    tipoafastamento = relationship('Tipoafastamento')


class Banco(Base):
    __tablename__ = 'banco'

    id = Column(Integer, primary_key=True)
    nome = Column(String(250, 'Latin1_General_CI_AS'))
    created = Column(DateTime)
    modified = Column(DateTime)


class Cargo(Base):
    __tablename__ = 'cargo'

    id = Column(Integer, primary_key=True)
    nome = Column(String(250, 'Latin1_General_CI_AS'))
    created = Column(DateTime)
    modified = Column(DateTime)


class Centrocusto(Base):
    __tablename__ = 'centrocusto'

    id = Column(Integer, primary_key=True)
    nome = Column(String(250, 'Latin1_General_CI_AS'))
    created = Column(DateTime)
    modified = Column(DateTime)


class Cliente(Base):
    __tablename__ = 'cliente'

    id = Column(Integer, primary_key=True)
    nome = Column(String(250, 'Latin1_General_CI_AS'))
    codigo = Column(String(14, 'Latin1_General_CI_AS'))
    created = Column(DateTime)
    modified = Column(DateTime)


class Conexao(Base):
    __tablename__ = 'conexao'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100, 'Latin1_General_CI_AS'))
    sgbd = Column(String(50, 'Latin1_General_CI_AS'))
    host = Column(String(50, 'Latin1_General_CI_AS'))
    porta = Column(String(50, 'Latin1_General_CI_AS'))
    banco = Column(String(50, 'Latin1_General_CI_AS'))
    usuario = Column(String(50, 'Latin1_General_CI_AS'))
    senha = Column(String(50, 'Latin1_General_CI_AS'))
    status = Column(String(1, 'Latin1_General_CI_AS'))
    created = Column(DateTime)
    modified = Column(DateTime)


class Contabancaria(Base):
    __tablename__ = 'contabancaria'

    id = Column(Integer, primary_key=True)
    funcionario_id = Column(ForeignKey('funcionario.id'))
    agencia = Column(String(20, 'Latin1_General_CI_AS'))
    conta = Column(String(20, 'Latin1_General_CI_AS'))
    tipopagamento_id = Column(ForeignKey('tipopagamento.id'))
    natureza = Column(String(500, 'Latin1_General_CI_AS'))
    principal = Column(String(1, 'Latin1_General_CI_AS'))
    banco_id = Column(ForeignKey('banco.id'))

    banco = relationship('Banco')
    funcionario = relationship('Funcionario')
    tipopagamento = relationship('Tipopagamento')


class Contratacao(Base):
    __tablename__ = 'contratacao'

    id = Column(Integer, primary_key=True)
    funcionario_id = Column(ForeignKey('funcionario.id'))
    dataadmissao = Column(Date)
    coordenador_id = Column(ForeignKey('funcionario.id'))
    tipojornada_id = Column(ForeignKey('tipojornada.id'))
    auxiliotransporte = Column(Numeric(18, 2))
    auxiliorefeicao = Column(Numeric(18, 2))
    planosaude_id = Column(ForeignKey('tipoplanosaude.id'))
    planosaudevalor = Column(Numeric(18, 2))
    segurovida_id = Column(ForeignKey('tiposegurovida.id'))
    segurovidavalor = Column(Numeric(18, 2))
    ajudacusto = Column(Numeric(18, 2))
    previdenciavalor = Column(Numeric(18, 2))
    status = Column(String(50, 'Latin1_General_CI_AS'))
    substituicao_id = Column(ForeignKey('funcionario.id'))
    resposavelvalidacaovaga_id = Column(ForeignKey('funcionario.id'))
    observacoes = Column(String(500, 'Latin1_General_CI_AS'))

    coordenador = relationship('Funcionario', primaryjoin='Contratacao.coordenador_id == Funcionario.id')
    funcionario = relationship('Funcionario', primaryjoin='Contratacao.funcionario_id == Funcionario.id')
    planosaude = relationship('Tipoplanosaude')
    resposavelvalidacaovaga = relationship('Funcionario',
                                           primaryjoin='Contratacao.resposavelvalidacaovaga_id == Funcionario.id')
    segurovida = relationship('Tiposegurovida')
    substituicao = relationship('Funcionario', primaryjoin='Contratacao.substituicao_id == Funcionario.id')
    tipojornada = relationship('Tipojornada')


class Contrato(Base):
    __tablename__ = 'contrato'

    id = Column(Integer, primary_key=True)
    funcionario_id = Column(ForeignKey('funcionario.id'), nullable=False)
    tipocontrato_id = Column(ForeignKey('tipocontrato.id'))
    datainicio = Column(Date)
    prazo = Column(Integer)
    datavencimento = Column(Date)

    funcionario = relationship('Funcionario')
    tipocontrato = relationship('Tipocontrato')


class Curso(Base):
    __tablename__ = 'curso'

    id = Column(Integer, primary_key=True)
    funcionario_id = Column(ForeignKey('funcionario.id'))
    nome = Column(String(200, 'Latin1_General_CI_AS'))
    tipo = Column(String(50, 'Latin1_General_CI_AS'))
    instituicao = Column(String(200, 'Latin1_General_CI_AS'))
    treinamentointerno = Column(String(1, 'Latin1_General_CI_AS'))
    pagoempresa = Column(String(1, 'Latin1_General_CI_AS'))
    datainicio = Column(Date)
    datafim = Column(Date)
    valor = Column(Numeric(18, 2))
    observacoes = Column(String(5000, 'Latin1_General_CI_AS'))
    tipocurso_id = Column(ForeignKey('tipocurso.id'))

    funcionario = relationship('Funcionario')
    tipocurso = relationship('Tipocurso')


class Departamento(Base):
    __tablename__ = 'departamento'

    id = Column(Integer, primary_key=True)
    nome = Column(String(250, 'Latin1_General_CI_AS'))
    created = Column(DateTime)
    modified = Column(DateTime)


class Empresa(Base):
    __tablename__ = 'empresa'

    id = Column(Integer, primary_key=True)
    nome = Column(String(250, 'Latin1_General_CI_AS'))
    cnpj = Column(String(20, 'Latin1_General_CI_AS'))
    created = Column(DateTime)
    modified = Column(DateTime)


class Feria(Base):
    __tablename__ = 'ferias'

    id = Column(Integer, primary_key=True)
    funcionario_id = Column(ForeignKey('funcionario.id'))
    anoexercicio = Column(Integer)
    prazoinicio = Column(Date)
    prazofim = Column(Date)
    datainicio = Column(Date)
    datafim = Column(Date)
    dias = Column(Integer)
    abono = Column(String(1, 'Latin1_General_CI_AS'))
    limitegozo = Column(Date)

    funcionario = relationship('Funcionario')


class Funcionario(Base):
    __tablename__ = 'funcionario'

    id = Column(Integer, primary_key=True)
    foto = Column(String(250, 'Latin1_General_CI_AS'))
    empresa_id = Column(ForeignKey('empresa.id'))
    unidade_id = Column(ForeignKey('unidade.id'))
    emailempresarial = Column(String(500, 'Latin1_General_CI_AS'))
    nome = Column(String(500, 'Latin1_General_CI_AS'))
    emailpessoal = Column(String(500, 'Latin1_General_CI_AS'))
    sexo = Column(String(1, 'Latin1_General_CI_AS'))
    datanascimento = Column(Date)
    naturalidade = Column(String(500, 'Latin1_General_CI_AS'))
    nacionalidade = Column(String(500, 'Latin1_General_CI_AS'))
    estadocivil = Column(String(100, 'Latin1_General_CI_AS'))
    filhos = Column(Integer)
    cpf = Column(String(14, 'Latin1_General_CI_AS'))
    rg = Column(String(100, 'Latin1_General_CI_AS'))
    pai = Column(String(500, 'Latin1_General_CI_AS'))
    mae = Column(String(500, 'Latin1_General_CI_AS'))
    cep = Column(String(9, 'Latin1_General_CI_AS'))
    logradouro = Column(String(500, 'Latin1_General_CI_AS'))
    numero = Column(String(100, 'Latin1_General_CI_AS'))
    bairro = Column(String(500, 'Latin1_General_CI_AS'))
    cidade = Column(String(500, 'Latin1_General_CI_AS'))
    uf = Column(String(2, 'Latin1_General_CI_AS'))
    complemento = Column(String(250, 'Latin1_General_CI_AS'))
    telefone = Column(String(15, 'Latin1_General_CI_AS'))
    celular = Column(String(15, 'Latin1_General_CI_AS'))
    telefoneurgencia = Column(String(15, 'Latin1_General_CI_AS'))
    nomeurgencia = Column(String(250, 'Latin1_General_CI_AS'))
    parentescourgencia = Column(String(250, 'Latin1_General_CI_AS'))
    observacoes = Column(String(5000, 'Latin1_General_CI_AS'))
    datadesligamento = Column(Date)
    tipodesligamento_id = Column(Integer)
    observacoesdesligamento = Column(String(5000, 'Latin1_General_CI_AS'))
    created = Column(DateTime)
    modified = Column(DateTime)
    rescisao = Column(Numeric(18, 2))
    tituloeleitoral = Column(String(50, 'Latin1_General_CI_AS'))
    zonaeleitoral = Column(String(50, 'Latin1_General_CI_AS'))
    secaoeleitoral = Column(String(50, 'Latin1_General_CI_AS'))
    pis = Column(String(50, 'Latin1_General_CI_AS'))
    ctps = Column(String(50, 'Latin1_General_CI_AS'))
    seriectps = Column(String(50, 'Latin1_General_CI_AS'))
    grauescolaridade_id = Column(ForeignKey('grauescolaridade.id'))

    empresa = relationship('Empresa')
    grauescolaridade = relationship('Grauescolaridade')
    unidade = relationship('Unidade')


class Grafico(Base):
    __tablename__ = 'grafico'

    id = Column(Integer, primary_key=True)
    nome = Column(String(200, 'Latin1_General_CI_AS'))
    sql = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    tipo = Column(String(20, 'Latin1_General_CI_AS'))
    ordem = Column(Integer)
    tamanho = Column(Integer)
    grupografico_id = Column(ForeignKey('grupografico.id'))
    conexao_id = Column(ForeignKey('conexao.id'))
    created = Column(DateTime)
    modified = Column(DateTime)
    cor = Column(String(200, 'Latin1_General_CI_AS'))
    icone = Column(String(50, 'Latin1_General_CI_AS'))

    conexao = relationship('Conexao')
    grupografico = relationship('Grupografico')


class Grauescolaridade(Base):
    __tablename__ = 'grauescolaridade'

    id = Column(Integer, primary_key=True)
    nome = Column(String(250, 'Latin1_General_CI_AS'))
    created = Column(DateTime)
    modified = Column(DateTime)


class Grupografico(Base):
    __tablename__ = 'grupografico'

    id = Column(Integer, primary_key=True)
    nome = Column(String(250, 'Latin1_General_CI_AS'))
    descricao = Column(String(500, 'Latin1_General_CI_AS'))


class Idioma(Base):
    __tablename__ = 'idioma'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100, 'Latin1_General_CI_AS'))
    nivel = Column(String(100, 'Latin1_General_CI_AS'))
    funcionario_id = Column(ForeignKey('funcionario.id'))

    funcionario = relationship('Funcionario')


class Indicador(Base):
    __tablename__ = 'indicador'

    id = Column(Integer, primary_key=True)
    nome = Column(String(200, 'Latin1_General_CI_AS'))
    sql = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    ordem = Column(Integer)
    grupografico_id = Column(ForeignKey('grupografico.id'))
    conexao_id = Column(ForeignKey('conexao.id'))
    created = Column(DateTime)
    modified = Column(DateTime)
    cor = Column(String(20, 'Latin1_General_CI_AS'))
    icone = Column(String(50, 'Latin1_General_CI_AS'))
    tamanho = Column(Integer)

    conexao = relationship('Conexao')
    grupografico = relationship('Grupografico')


class Oab(Base):
    __tablename__ = 'oab'

    id = Column(Integer, primary_key=True)
    numero = Column(String(100, 'Latin1_General_CI_AS'))
    dataexpedicao = Column(Date)
    funcionario_id = Column(ForeignKey('funcionario.id'))
    tipo = Column(String(100, 'Latin1_General_CI_AS'))

    funcionario = relationship('Funcionario')


t_papel = Table(
    'papel', metadata,
    Column('id', Integer, nullable=False),
    Column('nome', String(100, 'Latin1_General_CI_AS')),
    Column('descricao', String(500, 'Latin1_General_CI_AS'))
)


class Tipoafastamento(Base):
    __tablename__ = 'tipoafastamento'

    id = Column(Integer, primary_key=True)
    nome = Column(String(250, 'Latin1_General_CI_AS'))
    created = Column(DateTime)
    modified = Column(DateTime)


class Tipocontrato(Base):
    __tablename__ = 'tipocontrato'

    id = Column(Integer, primary_key=True)
    nome = Column(String(250, 'Latin1_General_CI_AS'))
    created = Column(DateTime)
    modified = Column(DateTime)


class Tipocurso(Base):
    __tablename__ = 'tipocurso'

    id = Column(Integer, primary_key=True)
    nome = Column(String(250, 'Latin1_General_CI_AS'))
    created = Column(DateTime)
    modified = Column(DateTime)


class Tipodesligamento(Base):
    __tablename__ = 'tipodesligamento'

    id = Column(Integer, primary_key=True)
    nome = Column(String(500, 'Latin1_General_CI_AS'))
    created = Column(DateTime)
    modified = Column(DateTime)


class Tipojornada(Base):
    __tablename__ = 'tipojornada'

    id = Column(Integer, primary_key=True)
    nome = Column(String(250, 'Latin1_General_CI_AS'))
    created = Column(DateTime)
    modified = Column(DateTime)


class Tipopagamento(Base):
    __tablename__ = 'tipopagamento'

    id = Column(Integer, primary_key=True)
    nome = Column(String(250, 'Latin1_General_CI_AS'))
    created = Column(DateTime)
    modified = Column(DateTime)


class Tipoplanosaude(Base):
    __tablename__ = 'tipoplanosaude'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100, 'Latin1_General_CI_AS'))
    created = Column(DateTime)
    modified = Column(DateTime)


class Tiposegurovida(Base):
    __tablename__ = 'tiposegurovida'

    id = Column(Integer, primary_key=True)
    nome = Column(String(250, 'Latin1_General_CI_AS'))
    created = Column(DateTime)
    modified = Column(DateTime)


class Tipovinculo(Base):
    __tablename__ = 'tipovinculo'

    id = Column(Integer, primary_key=True)
    nome = Column(String(250, 'Latin1_General_CI_AS'))
    created = Column(DateTime)
    modified = Column(DateTime)


class Unidade(Base):
    __tablename__ = 'unidade'

    id = Column(Integer, primary_key=True)
    nome = Column(String(250, 'Latin1_General_CI_AS'))
    created = Column(DateTime)
    modified = Column(DateTime)


class Usuario(Base):
    __tablename__ = 'usuario'

    id = Column(Integer, primary_key=True)
    nome = Column(String(250, 'Latin1_General_CI_AS'), nullable=False)
    email = Column(String(500, 'Latin1_General_CI_AS'), nullable=False)
    senha = Column(String(500, 'Latin1_General_CI_AS'), nullable=False)
    status = Column(String(1, 'Latin1_General_CI_AS'), nullable=False)
    papel_id = Column(Integer, nullable=False)
    created = Column(DateTime, nullable=False)
    modified = Column(DateTime)


class UsuarioCliente(Base):
    __tablename__ = 'usuario_cliente'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(ForeignKey('usuario.id'))
    cliente_id = Column(ForeignKey('cliente.id'))

    cliente = relationship('Cliente')
    usuario = relationship('Usuario')


class UsuarioUnidade(Base):
    __tablename__ = 'usuario_unidade'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(ForeignKey('usuario.id'))
    unidade_id = Column(ForeignKey('unidade.id'))

    unidade = relationship('Unidade')
    usuario = relationship('Usuario')


class Vinculo(Base):
    __tablename__ = 'vinculo'

    id = Column(Integer, primary_key=True)
    cargo_id = Column(ForeignKey('cargo.id'))
    tipovinculo_id = Column(Integer)
    salario = Column(Numeric(18, 2))
    centrocusto_id = Column(ForeignKey('centrocusto.id'))
    unidade_id = Column(ForeignKey('unidade.id'))
    departamento_id = Column(ForeignKey('departamento.id'))
    datainicio = Column(Date)
    datafim = Column(Date)
    funcionario_id = Column(ForeignKey('funcionario.id'))
    motivoreajuste = Column(String(100, 'Latin1_General_CI_AS'))

    cargo = relationship('Cargo')
    centrocusto = relationship('Centrocusto')
    departamento = relationship('Departamento')
    funcionario = relationship('Funcionario')
    unidade = relationship('Unidade')
