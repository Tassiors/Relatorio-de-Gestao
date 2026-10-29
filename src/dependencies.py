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
from .models.organizacao import UsuarioUorg, Uorg, Gerencia
from .providers.implementations.relatorio_gestao_sqlite_provider import (
    obter_tipo_uorg,
    SETOR_PAI_MAP,
    obter_subordinados_siglas,
)

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
        uorg_sigla = None
        uorg_nome = None
        tipo_uorg = None
        subordinados_siglas = []
        gerencia_sigla = None

        if u_user.uorg_id:
            res_u = await session.execute(select(Uorg).filter(Uorg.id == u_user.uorg_id))
            u_obj = res_u.scalars().first()
            if u_obj:
                uorg_sigla = u_obj.sigla
                uorg_nome = u_obj.nome
                tipo_uorg = obter_tipo_uorg(u_obj.sigla, u_obj.nome)
                subordinados_siglas = obter_subordinados_siglas(u_obj.sigla)

        if u_user.gerencia_id:
            res_g = await session.execute(select(Gerencia).filter(Gerencia.id == u_user.gerencia_id))
            g_obj = res_g.scalars().first()
            if g_obj:
                gerencia_sigla = g_obj.sigla

        return {
            "username": u_user.username,
            "nome_completo": u_user.nome_completo,
            "email": u_user.email,
            "perfil": u_user.perfil,
            "gerencia_id": u_user.gerencia_id,
            "gerencia_sigla": gerencia_sigla,
            "uorg_id": u_user.uorg_id,
            "uorg_sigla": uorg_sigla,
            "uorg_nome": uorg_nome,
            "tipo_uorg": tipo_uorg,
            "subordinados_siglas": subordinados_siglas
        }
    if username == "admin":
        return {
            "username": "admin",
            "nome_completo": "Administrador do Sistema",
            "email": "admin@ebserh.gov.br",
            "perfil": "ADMINISTRADOR",
            "gerencia_id": None,
            "gerencia_sigla": None,
            "uorg_id": None,
            "uorg_sigla": None,
            "uorg_nome": None,
            "tipo_uorg": None,
            "subordinados_siglas": []
        }
    return {
        "username": username,
        "nome_completo": token_payload.get("displayName") or username,
        "email": token_payload.get("email"),
        "perfil": "CONSULTA",
        "gerencia_id": None,
        "gerencia_sigla": None,
        "uorg_id": None,
        "uorg_sigla": None,
        "uorg_nome": None,
        "tipo_uorg": None,
        "subordinados_siglas": []
    }
