# src/models/planejamento.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.resources.database import Base

class EntregaPlanejada(Base):
    __tablename__ = 'entregas_planejadas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    exercicio_id = Column(Integer, ForeignKey('exercicios.id'), nullable=False)
    uorg_id = Column(Integer, ForeignKey('uorgs.id'), nullable=False)
    titulo = Column(String(500), nullable=False)
    descricao = Column(String(2000), nullable=True)
    ordem = Column(Integer, default=0)
    concluida = Column(Boolean, default=False)
    bimestre_conclusao_id = Column(Integer, ForeignKey('bimestres.id'), nullable=True)
    data_conclusao = Column(DateTime, nullable=True)
    usuario_conclusao = Column(String(100), nullable=True)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    exercicio = relationship('Exercicio', back_populates='entregas')
    uorg = relationship('Uorg', back_populates='entregas')

class Indicador(Base):
    __tablename__ = 'indicadores'

    id = Column(Integer, primary_key=True, autoincrement=True)
    exercicio_id = Column(Integer, ForeignKey('exercicios.id'), nullable=False)
    uorg_id = Column(Integer, ForeignKey('uorgs.id'), nullable=False)
    nome = Column(String(255), nullable=False)
    descricao = Column(String(2000), nullable=True)
    periodicidade = Column(String(50), default='BIMESTRAL')
    unidade_medida = Column(String(50), default='PERCENTUAL')
    meta_operador = Column(String(50), default='MAIOR_IGUAL')
    meta_valor = Column(Float, nullable=True)
    meta_valor_max = Column(Float, nullable=True)
    ordem = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    exercicio = relationship('Exercicio', back_populates='indicadores')
    uorg = relationship('Uorg', back_populates='indicadores')
