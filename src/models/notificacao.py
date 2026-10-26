# src/models/notificacao.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from src.resources.database import Base

class Notificacao(Base):
    __tablename__ = 'notificacoes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    destinatario_username = Column(String(100), nullable=True)
    destinatario_perfil = Column(String(50), nullable=True)
    uorg_id = Column(Integer, ForeignKey('uorgs.id'), nullable=True)
    tipo = Column(String(50), nullable=False)
    titulo = Column(String(255), nullable=False)
    mensagem = Column(String(1000), nullable=False)
    link = Column(String(255), nullable=True)
    lida = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
