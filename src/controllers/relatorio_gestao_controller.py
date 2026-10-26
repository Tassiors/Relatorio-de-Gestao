# src/controllers/relatorio_gestao_controller.py
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from ..providers.interfaces.relatorio_gestao_provider_interface import RelatorioGestaoProviderInterface

def calcular_atingimento_meta(
    operador: str,
    meta_valor: Optional[float],
    meta_valor_max: Optional[float],
    valor_apurado: Optional[float]
) -> Optional[bool]:
    """
    Calcula automaticamente se a meta do indicador foi atingida (RN-IND-01 & Decisão validada).
    Suporta: MAIOR_IGUAL, MENOR_IGUAL, IGUAL e ENTRE.
    """
    if valor_apurado is None or meta_valor is None:
        return None

    op = (operador or "MAIOR_IGUAL").upper()

    if op in ["MAIOR_IGUAL", ">="]:
        return valor_apurado >= meta_valor
    elif op in ["MENOR_IGUAL", "<="]:
        return valor_apurado <= meta_valor
    elif op in ["IGUAL", "="]:
        return abs(valor_apurado - meta_valor) < 1e-6
    elif op in ["ENTRE", "FAIXA"]:
        if meta_valor_max is None:
            return valor_apurado >= meta_valor
        return meta_valor <= valor_apurado <= meta_valor_max
    return False

async def obter_estrutura(provider: RelatorioGestaoProviderInterface) -> List[Dict[str, Any]]:
    return await provider.listar_gerencias_com_uorgs()

async def obter_exercicio_ativo(provider: RelatorioGestaoProviderInterface) -> Dict[str, Any]:
    ex = await provider.obter_exercicio_ativo()
    if not ex:
        raise HTTPException(status_code=404, detail="Nenhum exercício ativo encontrado.")
    return ex

async def obter_matriz(exercicio_id: int, provider: RelatorioGestaoProviderInterface) -> Dict[str, Any]:
    return await provider.obter_matriz_acompanhamento(exercicio_id)

async def obter_relatorio(
    exercicio_id: int, bimestre_id: int, uorg_id: int, provider: RelatorioGestaoProviderInterface
) -> Dict[str, Any]:
    rel = await provider.obter_relatorio(exercicio_id, bimestre_id, uorg_id)
    if rel:
        return rel

    # Se ainda não existe relatório, carregar catálogo base de entregas e indicadores
    entregas = await provider.listar_entregas_uorg(exercicio_id, uorg_id)
    indicadores = await provider.listar_indicadores_uorg(exercicio_id, uorg_id)
    uorg = await provider.obter_uorg_por_id(uorg_id)
    bimestres = await provider.obter_bimestres(exercicio_id)
    bimestre_atual = next((b for b in bimestres if b["id"] == bimestre_id), None)

    # Filtrar apenas entregas ainda pendentes (RN-ENT-01)
    entregas_pendentes = [e for e in entregas if not e["concluida"]]

    return {
        "id": None,
        "exercicio_id": exercicio_id,
        "bimestre_id": bimestre_id,
        "bimestre_nome": bimestre_atual["nome"] if bimestre_atual else f"{bimestre_id}º Bimestre",
        "bimestre_status": bimestre_atual["status"] if bimestre_atual else "FECHADO",
        "uorg_id": uorg_id,
        "uorg_sigla": uorg["sigla"] if uorg else "",
        "uorg_nome": uorg["nome"] if uorg else "",
        "status": "RASCUNHO",
        "versao": 0,
        "data_envio": None,
        "usuario_envio": None,
        "destaques": "",
        "dificuldades": "",
        "prazo_excepcional": None,
        "itens_entrega": [
            {
                "id": None,
                "entrega_id": e["id"],
                "titulo": e["titulo"],
                "concluida": False,
                "observacoes": ""
            }
            for e in entregas_pendentes
        ],
        "itens_indicador": [
            {
                "id": None,
                "indicador_id": i["id"],
                "nome": i["nome"],
                "descricao": i["descricao"],
                "periodicidade": i["periodicidade"],
                "unidade_medida": i["unidade_medida"],
                "meta_operador": i["meta_operador"],
                "meta_valor": i["meta_valor"],
                "meta_valor_max": i["meta_valor_max"],
                "competencia": bimestre_atual["nome"] if bimestre_atual else "Bimestre",
                "valor_apurado": None,
                "meta_atingida": None,
                "resultado_indisponivel": False,
                "justificativa_indisponibilidade": "",
                "nao_aplicavel": False
            }
            for i in indicadores
        ],
        "feedbacks": []
    }

async def salvar_rascunho(
    exercicio_id: int,
    bimestre_id: int,
    uorg_id: int,
    dados: Dict[str, Any],
    usuario: str,
    provider: RelatorioGestaoProviderInterface
) -> Dict[str, Any]:
    """Salva o progresso do relatório sem validação rígida de envio formal (RF-REL-05/06)."""
    # Calcular automaticamente atingimento de metas para os valores informados
    for item in dados.get("itens_indicador", []):
        if not item.get("resultado_indisponivel") and not item.get("nao_aplicavel"):
            val = item.get("valor_apurado")
            op = item.get("meta_operador", "MAIOR_IGUAL")
            meta = item.get("meta_valor")
            meta_max = item.get("meta_valor_max")
            item["meta_atingida"] = calcular_atingimento_meta(op, meta, meta_max, val)

    return await provider.salvar_rascunho(exercicio_id, bimestre_id, uorg_id, dados, usuario)

async def enviar_relatorio(
    relatorio_id: int,
    dados_finais: Dict[str, Any],
    usuario: str,
    provider: RelatorioGestaoProviderInterface
) -> Dict[str, Any]:
    """
    Realiza o envio formal do relatório bimestral validando requisitos obrigatórios (RF-REL-03/07).
    """
    # 1. Salvar antes do envio para garantir estado atualizado
    rel_atualizado = await provider.salvar_rascunho(
        dados_finais["exercicio_id"],
        dados_finais["bimestre_id"],
        dados_finais["uorg_id"],
        dados_finais,
        usuario
    )

    # 2. Validações pré-envio
    pendencias = []

    # Validar indicadores
    for item in rel_atualizado.get("itens_indicador", []):
        if item.get("nao_aplicavel"):
            continue
        if item.get("resultado_indisponivel"):
            just = (item.get("justificativa_indisponibilidade") or "").strip()
            if len(just) < 10:
                pendencias.append(
                    f"Indicador '{item.get('nome')}': justificativa de indisponibilidade deve conter no mínimo 10 caracteres."
                )
        else:
            if item.get("valor_apurado") is None:
                pendencias.append(f"Indicador '{item.get('nome')}': valor apurado não foi informado.")

    # Validar Destaques e Dificuldades
    destaques = (rel_atualizado.get("destaques") or "").strip()
    dificuldades = (rel_atualizado.get("dificuldades") or "").strip()
    if len(destaques) < 5:
        pendencias.append("Campo 'Destaques' é obrigatório para envio do relatório.")
    if len(dificuldades) < 5:
        pendencias.append("Campo 'Dificuldades' é obrigatório para envio do relatório.")

    if pendencias:
        raise HTTPException(
            status_code=400,
            detail={
                "mensagem": "Não foi possível enviar o relatório. Existem pendências obrigatórias:",
                "pendencias": pendencias
            }
        )

    # 3. Confirmar envio
    return await provider.enviar_relatorio(rel_atualizado["id"], usuario)

async def registrar_feedback(
    relatorio_id: int,
    texto: str,
    usuario_logado: Dict[str, Any],
    provider: RelatorioGestaoProviderInterface
) -> Dict[str, Any]:
    """
    Registra parecer institucional (RF-FBK-01).
    Permitido a SUPERINTENDENTE e ADMINISTRADOR (Decisão validada).
    """
    perfil = usuario_logado.get("perfil", "")
    if perfil not in ["SUPERINTENDENTE", "ADMINISTRADOR"]:
        raise HTTPException(
            status_code=403,
            detail="Apenas o Superintendente ou o Administrador podem registrar feedback institucional."
        )

    if not texto or len(texto.strip()) < 5:
        raise HTTPException(status_code=400, detail="O texto do feedback deve conter ao menos 5 caracteres.")

    return await provider.registrar_feedback(
        relatorio_id=relatorio_id,
        usuario=usuario_logado.get("username", "admin"),
        perfil=perfil,
        nome=usuario_logado.get("nome_completo", "Gestor"),
        texto=texto.strip()
    )

async def conceder_prazo_excepcional(
    exercicio_id: int,
    bimestre_id: int,
    uorg_id: int,
    motivo: str,
    data_fim: str,
    usuario_logado: Dict[str, Any],
    provider: RelatorioGestaoProviderInterface
) -> Dict[str, Any]:
    """
    Concede prazo excepcional com motivo estritamente obrigatório (RF-PEX-01/02 & Decisão validada).
    """
    perfil = usuario_logado.get("perfil", "")
    if perfil not in ["ADMINISTRADOR", "SUPERINTENDENTE"]:
        raise HTTPException(status_code=403, detail="Apenas o Administrador pode conceder prazo excepcional.")

    if not motivo or len(motivo.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="O motivo da concessão de prazo excepcional é obrigatório e deve ter no mínimo 10 caracteres."
        )

    return await provider.conceder_prazo_excepcional(
        exercicio_id=exercicio_id,
        bimestre_id=bimestre_id,
        uorg_id=uorg_id,
        motivo=motivo.strip(),
        data_fim=data_fim,
        usuario=usuario_logado.get("username", "admin")
    )

async def listar_notificacoes(
    usuario_logado: Dict[str, Any],
    provider: RelatorioGestaoProviderInterface
) -> List[Dict[str, Any]]:
    return await provider.listar_notificacoes(
        username=usuario_logado.get("username", ""),
        perfil=usuario_logado.get("perfil"),
        uorg_id=usuario_logado.get("uorg_id")
    )

async def marcar_notificacao_lida(
    notificacao_id: int,
    provider: RelatorioGestaoProviderInterface
) -> Dict[str, Any]:
    ok = await provider.marcar_notificacao_lida(notificacao_id)
    return {"sucesso": ok}
