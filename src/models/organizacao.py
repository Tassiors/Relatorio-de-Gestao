# src/models/organizacao.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.resources.database import Base

class Gerencia(Base):
    __tablename__ = 'gerencias'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sigla = Column(String(50), nullable=False, unique=True)
    nome = Column(String(255), nullable=False)
    ordem = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    uorgs = relationship('Uorg', back_populates='gerencia', cascade='all, delete-orphan')

class Uorg(Base):
    __tablename__ = 'uorgs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    gerencia_id = Column(Integer, ForeignKey('gerencias.id'), nullable=False)
    sigla = Column(String(50), nullable=False, unique=True)
    nome = Column(String(255), nullable=False)
    codigo_redcap = Column(String(50), nullable=True)
    ordem = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    gerencia = relationship('Gerencia', back_populates='uorgs')
    usuarios = relationship('UsuarioUorg', back_populates='uorg')
    entregas = relationship('EntregaPlanejada', back_populates='uorg')
    indicadores = relationship('Indicador', back_populates='uorg')
    relatorios = relationship('RelatorioBimestral', back_populates='uorg')

class UsuarioUorg(Base):
    __tablename__ = 'usuarios_uorg'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)
    nome_completo = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    perfil = Column(String(50), nullable=False)
    gerencia_id = Column(Integer, ForeignKey('gerencias.id'), nullable=True)
    uorg_id = Column(Integer, ForeignKey('uorgs.id'), nullable=True)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    uorg = relationship('Uorg', back_populates='usuarios')
