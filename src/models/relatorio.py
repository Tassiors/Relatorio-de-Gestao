# src/models/relatorio.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.resources.database import Base

class RelatorioBimestral(Base):
    __tablename__ = 'relatorios_bimestrais'

    id = Column(Integer, primary_key=True, autoincrement=True)
    exercicio_id = Column(Integer, ForeignKey('exercicios.id'), nullable=False)
    bimestre_id = Column(Integer, ForeignKey('bimestres.id'), nullable=False)
    uorg_id = Column(Integer, ForeignKey('uorgs.id'), nullable=False)
    status = Column(String(50), default='RASCUNHO')
    versao = Column(Integer, default=1)
    data_envio = Column(DateTime, nullable=True)
    usuario_envio = Column(String(100), nullable=True)
    destaques = Column(Text, nullable=True)
    dificuldades = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    exercicio = relationship('Exercicio', back_populates='relatorios')
    bimestre = relationship('Bimestre', back_populates='relatorios')
    uorg = relationship('Uorg', back_populates='relatorios')
    itens_entrega = relationship('ItemEntregaRelatorio', back_populates='relatorio', cascade='all, delete-orphan')
    itens_indicador = relationship('ItemIndicadorRelatorio', back_populates='relatorio', cascade='all, delete-orphan')
    feedbacks = relationship('FeedbackRelatorio', back_populates='relatorio', cascade='all, delete-orphan')

class ItemEntregaRelatorio(Base):
    __tablename__ = 'itens_entrega_relatorio'

    id = Column(Integer, primary_key=True, autoincrement=True)
    relatorio_id = Column(Integer, ForeignKey('relatorios_bimestrais.id'), nullable=False)
    entrega_id = Column(Integer, ForeignKey('entregas_planejadas.id'), nullable=False)
    concluida = Column(Boolean, default=False)
    observacoes = Column(String(1000), nullable=True)

    relatorio = relationship('RelatorioBimestral', back_populates='itens_entrega')
    entrega = relationship('EntregaPlanejada')

class ItemIndicadorRelatorio(Base):
    __tablename__ = 'itens_indicador_relatorio'

    id = Column(Integer, primary_key=True, autoincrement=True)
    relatorio_id = Column(Integer, ForeignKey('relatorios_bimestrais.id'), nullable=False)
    indicador_id = Column(Integer, ForeignKey('indicadores.id'), nullable=False)
    competencia = Column(String(100), nullable=False)
    valor_apurado = Column(Float, nullable=True)
    meta_atingida = Column(Boolean, nullable=True)
    resultado_indisponivel = Column(Boolean, default=False)
    justificativa_indisponibilidade = Column(String(1000), nullable=True)
    nao_aplicavel = Column(Boolean, default=False)

    relatorio = relationship('RelatorioBimestral', back_populates='itens_indicador')
    indicador = relationship('Indicador')

class FeedbackRelatorio(Base):
    __tablename__ = 'feedbacks_relatorio'

    id = Column(Integer, primary_key=True, autoincrement=True)
    relatorio_id = Column(Integer, ForeignKey('relatorios_bimestrais.id'), nullable=False)
    autor_username = Column(String(100), nullable=False)
    autor_perfil = Column(String(50), nullable=False)
    autor_nome = Column(String(255), nullable=False)
    texto_feedback = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    relatorio = relationship('RelatorioBimestral', back_populates='feedbacks')

class PrazoExcepcional(Base):
    __tablename__ = 'prazos_excepcionais'

    id = Column(Integer, primary_key=True, autoincrement=True)
    exercicio_id = Column(Integer, ForeignKey('exercicios.id'), nullable=False)
    bimestre_id = Column(Integer, ForeignKey('bimestres.id'), nullable=False)
    uorg_id = Column(Integer, ForeignKey('uorgs.id'), nullable=False)
    motivo = Column(String(1000), nullable=True)
    data_inicio = Column(DateTime, nullable=False, default=datetime.utcnow)
    data_fim = Column(DateTime, nullable=False)
    concedido_por_username = Column(String(100), nullable=False)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
