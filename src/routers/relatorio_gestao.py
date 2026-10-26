# src/routers/relatorio_gestao.py
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.auth import auth_handler
from ..dependencies import get_relatorio_gestao_provider, get_current_user_profile
from ..providers.interfaces.relatorio_gestao_provider_interface import RelatorioGestaoProviderInterface
from ..controllers import relatorio_gestao_controller as controller
from ..schemas.relatorio_gestao import (
    SalvarRascunhoSchema,
    EnviarRelatorioSchema,
    RegistrarFeedbackSchema,
    PrazoExcepcionalSchema
)
from ..helpers.audit_helper import registrar_auditoria
from ..helpers.export_helper import gerar_excel_relatorio, gerar_excel_matriz, gerar_pdf_relatorio
from ..resources.database import get_app_db_session

# Default-Private Router Pattern: todas as rotas deste módulo são autenticadas por padrão
router = APIRouter(
    prefix="/api/gestao",
    tags=["Portal Relatório de Gestão"],
    dependencies=[Depends(auth_handler.decode_token)]
)

@router.get("/me", response_model=Dict[str, Any])
async def obter_usuario_logado(
    usuario: Dict[str, Any] = Depends(get_current_user_profile)
):
    """Retorna os dados cadastrais e o perfil de acesso do usuário autenticado."""
    return usuario

@router.get("/estrutura", response_model=List[Dict[str, Any]])
async def obter_estrutura_organizacional(
    provider: RelatorioGestaoProviderInterface = Depends(get_relatorio_gestao_provider)
):
    """Lista as Gerências e UORGs ativas do HC-UFPE."""
    return await controller.obter_estrutura(provider)

@router.get("/exercicios/ativo", response_model=Dict[str, Any])
async def obter_exercicio_ativo(
    provider: RelatorioGestaoProviderInterface = Depends(get_relatorio_gestao_provider)
):
    """Retorna o exercício corrente com os 6 bimestres parametrizados."""
    return await controller.obter_exercicio_ativo(provider)

@router.get("/matriz", response_model=Dict[str, Any])
async def obter_matriz_acompanhamento(
    exercicio_id: Optional[int] = None,
    provider: RelatorioGestaoProviderInterface = Depends(get_relatorio_gestao_provider)
):
    """Retorna a Matriz UORG x Bimestre para o dashboard executivo e operacional."""
    if not exercicio_id:
        ex = await provider.obter_exercicio_ativo()
        if not ex:
            raise HTTPException(status_code=404, detail="Nenhum exercício ativo encontrado.")
        exercicio_id = ex["id"]
    return await controller.obter_matriz(exercicio_id, provider)

@router.get("/relatorios", response_model=Dict[str, Any])
async def obter_relatorio(
    exercicio_id: int,
    bimestre_id: int,
    uorg_id: int,
    provider: RelatorioGestaoProviderInterface = Depends(get_relatorio_gestao_provider)
):
    """Recupera ou inicializa o relatório bimestral da UORG para preenchimento ou consulta."""
    return await controller.obter_relatorio(exercicio_id, bimestre_id, uorg_id, provider)

@router.post("/relatorios/rascunho", response_model=Dict[str, Any])
async def salvar_rascunho_relatorio(
    payload: SalvarRascunhoSchema,
    request: Request,
    usuario: Dict[str, Any] = Depends(get_current_user_profile),
    provider: RelatorioGestaoProviderInterface = Depends(get_relatorio_gestao_provider),
    db: AsyncSession = Depends(get_app_db_session)
):
    """Salva automaticamente o rascunho em andamento sem bloqueios de validação (Autosave)."""
    rel = await controller.salvar_rascunho(
        exercicio_id=payload.exercicio_id,
        bimestre_id=payload.bimestre_id,
        uorg_id=payload.uorg_id,
        dados=payload.model_dump(),
        usuario=usuario["username"],
        provider=provider
    )

    # Auditoria de salvamento
    await registrar_auditoria(
        db=db,
        usuario=usuario["username"],
        categoria="NEGOCIO_CLINICO",
        acao="SALVAR_RASCUNHO_RELATORIO",
        recurso=f"relatorio:{rel.get('id')}",
        dados_novos={"status": "RASCUNHO", "uorg_id": payload.uorg_id, "bimestre_id": payload.bimestre_id},
        ip_origem=request.client.host if request.client else "127.0.0.1"
    )

    return rel

@router.post("/relatorios/enviar", response_model=Dict[str, Any])
async def enviar_relatorio_bimestral(
    payload: EnviarRelatorioSchema,
    request: Request,
    usuario: Dict[str, Any] = Depends(get_current_user_profile),
    provider: RelatorioGestaoProviderInterface = Depends(get_relatorio_gestao_provider),
    db: AsyncSession = Depends(get_app_db_session)
):
    """Realiza o envio formal do relatório bimestral com validação estrita de obrigatoriedade."""
    rel = await controller.enviar_relatorio(
        relatorio_id=payload.relatorio_id,
        dados_finais=payload.model_dump(),
        usuario=usuario["username"],
        provider=provider
    )

    # Auditoria de envio
    await registrar_auditoria(
        db=db,
        usuario=usuario["username"],
        categoria="NEGOCIO_CLINICO",
        acao="ENVIAR_RELATORIO_BIMESTRAL",
        recurso=f"relatorio:{rel.get('id')}",
        dados_novos={"status": "ENVIADO", "versao": rel.get("versao"), "usuario_envio": usuario["username"]},
        ip_origem=request.client.host if request.client else "127.0.0.1"
    )

    return rel

@router.post("/relatorios/{relatorio_id}/feedback", response_model=Dict[str, Any])
async def registrar_feedback_institucional(
    relatorio_id: int,
    payload: RegistrarFeedbackSchema,
    request: Request,
    usuario: Dict[str, Any] = Depends(get_current_user_profile),
    provider: RelatorioGestaoProviderInterface = Depends(get_relatorio_gestao_provider),
    db: AsyncSession = Depends(get_app_db_session)
):
    """Registra parecer e feedback institucional (permitido a Superintendente e Administrador)."""
    fb = await controller.registrar_feedback(
        relatorio_id=relatorio_id,
        texto=payload.texto,
        usuario_logado=usuario,
        provider=provider
    )

    # Auditoria de feedback
    await registrar_auditoria(
        db=db,
        usuario=usuario["username"],
        categoria="NEGOCIO_CLINICO",
        acao="REGISTRAR_FEEDBACK_INSTITUCIONAL",
        recurso=f"relatorio:{relatorio_id}",
        dados_novos={"feedback_id": fb.get("id"), "autor": usuario["username"], "perfil": usuario["perfil"]},
        ip_origem=request.client.host if request.client else "127.0.0.1"
    )

    return fb

@router.post("/prazos-excepcionais", response_model=Dict[str, Any])
async def conceder_prazo_excepcional(
    payload: PrazoExcepcionalSchema,
    request: Request,
    usuario: Dict[str, Any] = Depends(get_current_user_profile),
    provider: RelatorioGestaoProviderInterface = Depends(get_relatorio_gestao_provider),
    db: AsyncSession = Depends(get_app_db_session)
):
    """Concede reabertura com prazo excepcional por UORG exigindo justificativa obrigatória."""
    pex = await controller.conceder_prazo_excepcional(
        exercicio_id=payload.exercicio_id,
        bimestre_id=payload.bimestre_id,
        uorg_id=payload.uorg_id,
        motivo=payload.motivo,
        data_fim=payload.data_fim,
        usuario_logado=usuario,
        provider=provider
    )

    # Auditoria de prazo excepcional
    await registrar_auditoria(
        db=db,
        usuario=usuario["username"],
        categoria="CONFIGURACAO",
        acao="CONCEDER_PRAZO_EXCEPCIONAL",
        recurso=f"uorg:{payload.uorg_id}:bimestre:{payload.bimestre_id}",
        dados_novos={"motivo": payload.motivo, "data_fim": payload.data_fim, "concedido_por": usuario["username"]},
        ip_origem=request.client.host if request.client else "127.0.0.1"
    )

    return pex

@router.get("/notificacoes", response_model=List[Dict[str, Any]])
async def listar_notificacoes_usuario(
    usuario: Dict[str, Any] = Depends(get_current_user_profile),
    provider: RelatorioGestaoProviderInterface = Depends(get_relatorio_gestao_provider)
):
    """Retorna as notificações internas direcionadas ao usuário ou seu setor."""
    return await controller.listar_notificacoes(usuario, provider)

@router.post("/notificacoes/{notificacao_id}/lida", response_model=Dict[str, Any])
async def marcar_notificacao_lida(
    notificacao_id: int,
    provider: RelatorioGestaoProviderInterface = Depends(get_relatorio_gestao_provider)
):
    """Marca notificação como lida."""
    return await controller.marcar_notificacao_lida(notificacao_id, provider)

@router.get("/relatorios/{relatorio_id}/export/excel")
async def exportar_relatorio_excel(
    relatorio_id: int,
    provider: RelatorioGestaoProviderInterface = Depends(get_relatorio_gestao_provider),
    db: AsyncSession = Depends(get_app_db_session)
):
    """Gera e faz download da planilha Excel (.xlsx) formatada do relatório bimestral."""
    # provider handled via Depends
    # Buscar dados do relatório
    from sqlalchemy import select
    from ..models.relatorio import RelatorioBimestral
    stmt = select(RelatorioBimestral).filter(RelatorioBimestral.id == relatorio_id)
    res = await db.execute(stmt)
    rel_db = res.scalars().first()
    if not rel_db:
        raise HTTPException(status_code=404, detail="Relatório não encontrado.")

    rel_dict = await provider.obter_relatorio(rel_db.exercicio_id, rel_db.bimestre_id, rel_db.uorg_id)
    excel_bytes = gerar_excel_relatorio(rel_dict)

    filename = f"Relatorio_Gestao_{rel_dict.get('uorg_sigla')}_Bimestre_{rel_dict.get('bimestre_id')}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/relatorios/{relatorio_id}/export/pdf")
async def exportar_relatorio_pdf(
    relatorio_id: int,
    provider: RelatorioGestaoProviderInterface = Depends(get_relatorio_gestao_provider),
    db: AsyncSession = Depends(get_app_db_session)
):
    """Gera e faz download do arquivo PDF formatado do relatório bimestral."""
    # provider handled via Depends
    from sqlalchemy import select
    from ..models.relatorio import RelatorioBimestral
    stmt = select(RelatorioBimestral).filter(RelatorioBimestral.id == relatorio_id)
    res = await db.execute(stmt)
    rel_db = res.scalars().first()
    if not rel_db:
        raise HTTPException(status_code=404, detail="Relatório não encontrado.")

    rel_dict = await provider.obter_relatorio(rel_db.exercicio_id, rel_db.bimestre_id, rel_db.uorg_id)
    pdf_bytes = gerar_pdf_relatorio(rel_dict)

    filename = f"Relatorio_Gestao_{rel_dict.get('uorg_sigla')}_Bimestre_{rel_dict.get('bimestre_id')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/matriz/export/excel")
async def exportar_matriz_excel(
    exercicio_id: Optional[int] = None,
    provider: RelatorioGestaoProviderInterface = Depends(get_relatorio_gestao_provider)
):
    """Gera e faz download da Matriz consolidada UORG x Bimestre em formato Excel."""
    if not exercicio_id:
        ex = await provider.obter_exercicio_ativo()
        if not ex:
            raise HTTPException(status_code=404, detail="Nenhum exercício ativo encontrado.")
        exercicio_id = ex["id"]

    matriz = await provider.obter_matriz_acompanhamento(exercicio_id)
    excel_bytes = gerar_excel_matriz(matriz)
    filename = f"Matriz_Consolidada_Gestao_{exercicio_id}.xlsx"

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
