# src/models/exercicio.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.resources.database import Base

class Exercicio(Base):
    __tablename__ = 'exercicios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ano = Column(Integer, nullable=False, unique=True)
    descricao = Column(String(255), nullable=True)
    status = Column(String(50), default='PLANEJAMENTO')
    data_inicio = Column(DateTime, nullable=True)
    data_fim = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    bimestres = relationship('Bimestre', back_populates='exercicio', cascade='all, delete-orphan')
    entregas = relationship('EntregaPlanejada', back_populates='exercicio')
    indicadores = relationship('Indicador', back_populates='exercicio')
    relatorios = relationship('RelatorioBimestral', back_populates='exercicio')

class Bimestre(Base):
    __tablename__ = 'bimestres'

    id = Column(Integer, primary_key=True, autoincrement=True)
    exercicio_id = Column(Integer, ForeignKey('exercicios.id'), nullable=False)
    numero = Column(Integer, nullable=False)
    nome = Column(String(100), nullable=False)
    status = Column(String(50), default='FECHADO')
    data_abertura = Column(DateTime, nullable=True)
    data_fechamento_regular = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    exercicio = relationship('Exercicio', back_populates='bimestres')
    relatorios = relationship('RelatorioBimestral', back_populates='bimestre')
