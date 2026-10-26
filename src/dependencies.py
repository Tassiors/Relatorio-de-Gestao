import os
from typing import Callable, Dict, Any, Optional
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .providers.interfaces.paciente_provider_interface import PacienteProviderInterface
from .providers.implementations.paciente_postgres_provider import PacientePostgresProvider
from .providers.implementations.paciente_csv_provider import PacienteCsvProvider
from .providers.interfaces.relatorio_gestao_provider_interface import RelatorioGestaoProviderInterface
from .providers.implementations.relatorio_gestao_sqlite_provider import RelatorioGestaoSqliteProvider
from .resources.database import get_aghu_db_session, get_app_db_session
from .auth.auth import auth_handler
from .models.organizacao import UsuarioUorg

# Providers de Paciente
def _get_paciente_postgres_provider(
    session: AsyncSession = Depends(get_aghu_db_session)
) -> PacienteProviderInterface:
    return PacientePostgresProvider(session=session)

def _get_paciente_csv_provider() -> PacienteProviderInterface:
    csv_path = os.getenv("PACIENTE_CSV_PATH", "data/pacientes.csv")
    return PacienteCsvProvider(csv_path=csv_path)

def get_paciente_provider(strategy: str) -> Callable[..., PacienteProviderInterface]:
    if strategy.upper() == "POSTGRES":
        return _get_paciente_postgres_provider
    elif strategy.upper() == "CSV":
        return _get_paciente_csv_provider
    else:
        raise ValueError(f"Estratégia de provedor desconhecida: {strategy}")

# Provider de Relatório de Gestão
def get_relatorio_gestao_provider(
    session: AsyncSession = Depends(get_app_db_session)
) -> RelatorioGestaoProviderInterface:
    return RelatorioGestaoSqliteProvider(session=session)

# Obtenção do Perfil Local do Usuário (AD + RBAC Local - RN-ACL-01/02)
async def get_current_user_profile(
    token_payload: dict = Depends(auth_handler.decode_token),
    session: AsyncSession = Depends(get_app_db_session)
) -> Dict[str, Any]:
    username = token_payload.get("sub") or token_payload.get("username")
    stmt = select(UsuarioUorg).filter(UsuarioUorg.username == username, UsuarioUorg.ativo == True)
    res = await session.execute(stmt)
    u_user = res.scalars().first()
    if u_user:
        return {
            "username": u_user.username,
            "nome_completo": u_user.nome_completo,
            "email": u_user.email,
            "perfil": u_user.perfil,
            "gerencia_id": u_user.gerencia_id,
            "uorg_id": u_user.uorg_id
        }
    if username == "admin":
        return {
            "username": "admin",
            "nome_completo": "Administrador do Sistema",
            "email": "admin@ebserh.gov.br",
            "perfil": "ADMINISTRADOR",
            "gerencia_id": None,
            "uorg_id": None
        }
    return {
        "username": username,
        "nome_completo": token_payload.get("displayName") or username,
        "email": token_payload.get("email"),
        "perfil": "CONSULTA",
        "gerencia_id": None,
        "uorg_id": None
    }
