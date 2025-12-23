from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Date, Numeric, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json

Base = declarative_base()

class FonteAutorizadaSQL(Base):
    __tablename__ = 'fontes_autorizadas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(200), nullable=False)
    email_remetente = Column(String(200), nullable=False)
    palavras_assunto = Column(Text, nullable=False)
    palavras_corpo = Column(Text, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    criado_em = Column(DateTime, default=datetime.now, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    cobrancas = relationship("CobrancaSQL", back_populates="fonte")

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email_remetente': self.email_remetente,
            'palavras_assunto': json.loads(self.palavras_assunto) if isinstance(self.palavras_assunto, str) else self.palavras_assunto,
            'palavras_corpo': json.loads(self.palavras_corpo) if isinstance(self.palavras_corpo, str) else self.palavras_corpo,
            'ativo': self.ativo,
            'criado_em': self.criado_em,
            'atualizado_em': self.atualizado_em
        }

class CobrancaSQL(Base):
    __tablename__ = 'cobrancas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fonte_id = Column(Integer, ForeignKey('fontes_autorizadas.id'), nullable=False)
    email_id = Column(String(200), nullable=False, unique=True)
    hash_unico = Column(String(64), nullable=False, unique=True, index=True)
    valor = Column(Numeric(10, 2), nullable=False)
    data_vencimento = Column(Date, nullable=False, index=True)
    tipo_pagamento = Column(String(20), nullable=False)
    codigo_pix = Column(Text, nullable=True)
    codigo_barras = Column(String(100), nullable=True)
    link_boleto = Column(Text, nullable=True)
    descricao = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, index=True)
    erro_mensagem = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=datetime.now, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    fonte = relationship("FonteAutorizadaSQL", back_populates="cobrancas")
    agendamento = relationship("AgendamentoSQL", back_populates="cobranca", uselist=False)
    tentativas = relationship("TentativaPagamentoSQL", back_populates="cobranca")

class AgendamentoSQL(Base):
    __tablename__ = 'agendamentos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cobranca_id = Column(Integer, ForeignKey('cobrancas.id'), nullable=False, unique=True, index=True)
    data_execucao = Column(Date, nullable=False, index=True)
    executado = Column(Boolean, default=False, nullable=False, index=True)
    data_execucao_real = Column(DateTime, nullable=True)
    criado_em = Column(DateTime, default=datetime.now, nullable=False)

    cobranca = relationship("CobrancaSQL", back_populates="agendamento")

class ControleExecucaoSQL(Base):
    __tablename__ = 'controle_execucoes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_rotina = Column(String(100), nullable=False, unique=True, index=True)
    ultima_execucao = Column(DateTime, nullable=True)
    intervalo_minutos = Column(Integer, nullable=False)
    ultimo_status = Column(String(50), nullable=False)
    ultima_mensagem = Column(Text, nullable=True)
    atualizado_em = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

class TentativaPagamentoSQL(Base):
    __tablename__ = 'tentativas_pagamento'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cobranca_id = Column(Integer, ForeignKey('cobrancas.id'), nullable=False, index=True)
    tentativa_em = Column(DateTime, default=datetime.now, nullable=False)
    sucesso = Column(Boolean, nullable=False)
    mensagem_retorno = Column(Text, nullable=False)
    codigo_transacao = Column(String(200), nullable=True)
    criado_em = Column(DateTime, default=datetime.now, nullable=False)

    cobranca = relationship("CobrancaSQL", back_populates="tentativas")

def criar_engine(database_path: str):
    return create_engine(f'sqlite:///{database_path}', echo=False)

def criar_session_factory(engine):
    return sessionmaker(bind=engine)

def criar_todas_tabelas(engine):
    Base.metadata.create_all(engine)

def obter_session(session_factory):
    return session_factory()
