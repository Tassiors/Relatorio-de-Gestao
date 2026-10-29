# src/controllers/relatorio_gestao_controller.py
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from ..providers.interfaces.relatorio_gestao_provider_interface import RelatorioGestaoProviderInterface
from ..providers.implementations.relatorio_gestao_sqlite_provider import (
    DIVISAO_SUBORDINADAS_MAP,
    SETOR_PAI_MAP,
    obter_tipo_uorg,
    obter_subordinados_siglas,
)
from ..helpers.indicador_helper import obter_configuracao_periodicidade, validar_itens_indicador_bimestre

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

async def obter_matriz(
    exercicio_id: int,
    provider: RelatorioGestaoProviderInterface,
    usuario_logado: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    matriz = await provider.obter_matriz_acompanhamento(exercicio_id)
    if not usuario_logado:
        return matriz

    perfil = (usuario_logado.get("perfil") or "").upper()
    if perfil in ["ADMINISTRADOR", "SUPERINTENDENTE"]:
        return matriz

    uorgs_permitidas = await listar_uorgs_acessiveis_dashboard(usuario_logado, provider)
    ids_permitidos = {int(u["id"]) for u in uorgs_permitidas}

    linhas_filtradas = [l for l in matriz.get("linhas", []) if int(l["uorg_id"]) in ids_permitidos]
    totais = {"enviados": 0, "pendentes": 0, "em_edicao": 0, "prazo_excepcional": 0}
    for l in linhas_filtradas:
        for b in l.get("bimestres", []):
            st = b.get("status")
            if st == "PRAZO_EXCEPCIONAL":
                totais["prazo_excepcional"] += 1
            elif st == "ENVIADO":
                totais["enviados"] += 1
            elif st == "EM_EDICAO":
                totais["em_edicao"] += 1
            elif st in ["PENDENTE", "RASCUNHO"]:
                totais["pendentes"] += 1

    return {
        **matriz,
        "linhas": linhas_filtradas,
        "totais": totais
    }

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
    bims_map = {b["id"]: b for b in bimestres}
    bimestre_atual = bims_map.get(bimestre_id)
    bim_atual_num = bimestre_atual["numero"] if bimestre_atual else bimestre_id

    itens_entrega_inicial = []
    for e in entregas:
        bim_conc_id = e.get("bimestre_conclusao_id")
        bim_conc = bims_map.get(bim_conc_id) if bim_conc_id else None
        bim_conc_num = bim_conc["numero"] if bim_conc else None
        concluida_ant = bool(e.get("concluida") and bim_conc_num is not None and bim_conc_num < bim_atual_num)
        concluida_atual = bool(e.get("concluida") and (bim_conc_id == bimestre_id or concluida_ant))
        itens_entrega_inicial.append({
            "id": None,
            "entrega_id": e["id"],
            "titulo": e["titulo"],
            "concluida": concluida_atual,
            "concluida_anteriormente": concluida_ant,
            "bimestre_conclusao_id": bim_conc_id,
            "bimestre_conclusao_nome": bim_conc["nome"] if bim_conc else None,
            "observacoes": ""
        })

    itens_indicador_inicial = []
    for i in indicadores:
        cfg = obter_configuracao_periodicidade(i["periodicidade"], bim_atual_num)
        for comp in cfg["competencias"]:
            itens_indicador_inicial.append({
                "id": None,
                "indicador_id": i["id"],
                "nome": i["nome"],
                "descricao": i["descricao"],
                "periodicidade": i["periodicidade"],
                "unidade_medida": i["unidade_medida"],
                "meta_operador": i["meta_operador"],
                "meta_valor": i["meta_valor"],
                "meta_valor_max": i["meta_valor_max"],
                "competencia": comp,
                "valor_apurado": None,
                "meta_atingida": None,
                "resultado_indisponivel": False,
                "justificativa_indisponibilidade": "",
                "nao_aplicavel": not cfg["aplicavel"],
                "orientacao_periodicidade": cfg["orientacao"]
            })

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
        "itens_entrega": itens_entrega_inicial,
        "itens_indicador": itens_indicador_inicial,
        "feedbacks": []
    }

async def salvar_rascunho(
    exercicio_id: int,
    bimestre_id: int,
    uorg_id: int,
    dados: Dict[str, Any],
    usuario: str,
    provider: RelatorioGestaoProviderInterface,
    usuario_logado: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Salva o progresso do relatório sem validação rígida de envio formal (RF-REL-05/06)."""
    if usuario_logado:
        validar_escopo_uorg(usuario_logado, uorg_id, apenas_leitura=False)
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
    provider: RelatorioGestaoProviderInterface,
    usuario_logado: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Realiza o envio formal do relatório bimestral validando requisitos obrigatórios (RF-REL-03/07).
    """
    if usuario_logado:
        validar_escopo_uorg(usuario_logado, dados_finais["uorg_id"], apenas_leitura=False)
    # 1. Salvar antes do envio para garantir estado atualizado
    rel_atualizado = await provider.salvar_rascunho(
        dados_finais["exercicio_id"],
        dados_finais["bimestre_id"],
        dados_finais["uorg_id"],
        dados_finais,
        usuario
    )

    # 2. Validações pré-envio
    bimestres = await provider.obter_bimestres(dados_finais["exercicio_id"])
    bim_atual = next((b for b in bimestres if b["id"] == dados_finais["bimestre_id"]), None)
    bim_num = bim_atual["numero"] if bim_atual else dados_finais["bimestre_id"]

    pendencias = validar_itens_indicador_bimestre(
        rel_atualizado.get("itens_indicador", []),
        bim_num
    )

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
    motivo: Optional[str],
    data_fim: str,
    usuario_logado: Dict[str, Any],
    provider: RelatorioGestaoProviderInterface
) -> Dict[str, Any]:
    """
    Concede prazo excepcional com motivo opcional (RF-PEX-01/02 & Refinamento de UX).
    """
    perfil = usuario_logado.get("perfil", "")
    if perfil not in ["ADMINISTRADOR", "SUPERINTENDENTE"]:
        raise HTTPException(status_code=403, detail="Apenas o Administrador pode conceder prazo excepcional.")

    motivo_limpo = motivo.strip() if motivo and motivo.strip() else None

    return await provider.conceder_prazo_excepcional(
        exercicio_id=exercicio_id,
        bimestre_id=bimestre_id,
        uorg_id=uorg_id,
        motivo=motivo_limpo,
        data_fim=data_fim,
        usuario=usuario_logado.get("username", "admin")
    )

async def atualizar_bimestre(
    bimestre_id: int,
    status: Optional[str],
    data_fechamento_regular: Optional[str],
    usuario_logado: Dict[str, Any],
    provider: RelatorioGestaoProviderInterface
) -> Dict[str, Any]:
    """
    Permite ao Administrador alterar manualmente o status (ABERTO/FECHADO) e a data limite de fechamento do bimestre.
    """
    perfil = usuario_logado.get("perfil", "")
    if perfil != "ADMINISTRADOR":
        raise HTTPException(
            status_code=403,
            detail="Apenas o Administrador pode alterar o status ou a data de fechamento de um bimestre."
        )

    if status is not None and status not in ["ABERTO", "FECHADO", "AGUARDANDO"]:
        raise HTTPException(
            status_code=400,
            detail="Status de bimestre inválido. Utilize ABERTO ou FECHADO."
        )

    try:
        bim_atualizado = await provider.atualizar_bimestre(
            bimestre_id=bimestre_id,
            status=status,
            data_fechamento_regular=data_fechamento_regular
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return bim_atualizado

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


# ---------------------------------------------------------
# Planejamento Anual: Regras de Negócio e Validações RBAC
# ---------------------------------------------------------

def validar_escopo_uorg(usuario_logado: Dict[str, Any], uorg_id: int, apenas_leitura: bool = False):
    """
    Valida se o usuário autenticado tem permissão para acessar ou modificar a UORG.
    - ADMINISTRADOR: tem acesso a todas as UORGs.
    - SUPERINTENDENTE / GERENTE: tem permissão de leitura para todas as UORGs, mas não de mutação.
    - CHEFE / CHEFE_UORG: apenas sua própria UORG.
    """
    perfil = usuario_logado.get("perfil", "")
    if perfil == "ADMINISTRADOR":
        return

    user_uorg_id = usuario_logado.get("uorg_id")
    if perfil in ["CHEFE", "CHEFE_UORG"]:
        if user_uorg_id is None or int(user_uorg_id) != int(uorg_id):
            raise HTTPException(
                status_code=403,
                detail="Acesso não autorizado para esta Unidade Organizacional (UORG)."
            )
        return

    if apenas_leitura and perfil in ["SUPERINTENDENTE", "GERENTE"]:
        return

    raise HTTPException(
        status_code=403,
        detail="Perfil não autorizado para esta operação de planejamento."
    )


async def verificar_planejamento_aberto(
    exercicio_id: int,
    usuario_logado: Dict[str, Any],
    provider: RelatorioGestaoProviderInterface
) -> Dict[str, Any]:
    """
    Verifica se o exercício está com o status 'PLANEJAMENTO'.
    Usuários com perfil de Chefia só podem modificar entregas/indicadores com planejamento aberto.
    ADMINISTRADOR tem permissão para intervenção administrativa.
    """
    ex = await provider.obter_exercicio_por_id(exercicio_id)
    if not ex:
        raise HTTPException(status_code=404, detail="Exercício não encontrado.")

    perfil = usuario_logado.get("perfil", "")
    if perfil != "ADMINISTRADOR" and ex.get("status") != "PLANEJAMENTO":
        raise HTTPException(
            status_code=400,
            detail="A janela de planejamento anual está encerrada para este exercício."
        )
    return ex


async def obter_planejamento_uorg(
    uorg_id: int,
    exercicio_id: Optional[int],
    usuario_logado: Dict[str, Any],
    provider: RelatorioGestaoProviderInterface
) -> Dict[str, Any]:
    """
    Consulta o planejamento de entregas e indicadores da UORG para o exercício corrente.
    """
    validar_escopo_uorg(usuario_logado, uorg_id, apenas_leitura=True)

    if not exercicio_id:
        ex = await provider.obter_exercicio_ativo()
        if not ex:
            raise HTTPException(status_code=404, detail="Nenhum exercício ativo encontrado.")
        exercicio_id = ex["id"]
    else:
        ex = await provider.obter_exercicio_por_id(exercicio_id)
        if not ex:
            raise HTTPException(status_code=404, detail="Exercício não encontrado.")

    uorg = await provider.obter_uorg_por_id(uorg_id)
    if not uorg:
        raise HTTPException(status_code=404, detail="UORG não encontrada.")

    entregas = await provider.listar_entregas_uorg(exercicio_id, uorg_id)
    indicadores = await provider.listar_indicadores_uorg(exercicio_id, uorg_id)

    return {
        "exercicio": ex,
        "uorg": uorg,
        "planejamento_aberto": ex.get("status") == "PLANEJAMENTO",
        "entregas": entregas,
        "indicadores": indicadores,
        "total_entregas": len(entregas),
        "total_indicadores": len(indicadores)
    }


async def criar_entrega_planejada(
    dados: Dict[str, Any],
    usuario_logado: Dict[str, Any],
    provider: RelatorioGestaoProviderInterface
) -> Dict[str, Any]:
    uorg_id = dados["uorg_id"]
    exercicio_id = dados["exercicio_id"]

    validar_escopo_uorg(usuario_logado, uorg_id, apenas_leitura=False)
    await verificar_planejamento_aberto(exercicio_id, usuario_logado, provider)

    return await provider.criar_entrega(
        uorg_id=uorg_id,
        exercicio_id=exercicio_id,
        titulo=dados["titulo"].strip(),
        descricao=dados.get("descricao"),
        ordem=dados.get("ordem", 1)
    )


async def editar_entrega_planejada(
    entrega_id: int,
    dados: Dict[str, Any],
    usuario_logado: Dict[str, Any],
    provider: RelatorioGestaoProviderInterface
) -> Dict[str, Any]:
    entrega_antiga = await provider.obter_entrega(entrega_id)
    if not entrega_antiga:
        raise HTTPException(status_code=404, detail="Entrega planejada não encontrada.")

    validar_escopo_uorg(usuario_logado, entrega_antiga["uorg_id"], apenas_leitura=False)
    await verificar_planejamento_aberto(entrega_antiga["exercicio_id"], usuario_logado, provider)

    entrega_atualizada = await provider.editar_entrega(
        entrega_id=entrega_id,
        titulo=dados["titulo"].strip(),
        descricao=dados.get("descricao")
    )
    return {
        "entrega": entrega_atualizada,
        "dados_anteriores": entrega_antiga,
        "dados_novos": entrega_atualizada
    }


async def inativar_entrega_planejada(
    entrega_id: int,
    usuario_logado: Dict[str, Any],
    provider: RelatorioGestaoProviderInterface
) -> Dict[str, Any]:
    entrega_antiga = await provider.obter_entrega(entrega_id)
    if not entrega_antiga:
        raise HTTPException(status_code=404, detail="Entrega planejada não encontrada.")

    validar_escopo_uorg(usuario_logado, entrega_antiga["uorg_id"], apenas_leitura=False)
    await verificar_planejamento_aberto(entrega_antiga["exercicio_id"], usuario_logado, provider)

    sucesso = await provider.inativar_entrega(entrega_id)
    return {
        "sucesso": sucesso,
        "dados_anteriores": entrega_antiga,
        "dados_novos": {"ativo": False}
    }


async def criar_indicador_planejado(
    dados: Dict[str, Any],
    usuario_logado: Dict[str, Any],
    provider: RelatorioGestaoProviderInterface
) -> Dict[str, Any]:
    uorg_id = dados["uorg_id"]
    exercicio_id = dados["exercicio_id"]

    validar_escopo_uorg(usuario_logado, uorg_id, apenas_leitura=False)
    await verificar_planejamento_aberto(exercicio_id, usuario_logado, provider)

    # Validar limite de 1 a 3 indicadores ativos por UORG (RF-IND-01)
    inds_existentes = await provider.listar_indicadores_uorg(exercicio_id, uorg_id)
    if len(inds_existentes) >= 3:
        raise HTTPException(
            status_code=400,
            detail="Limite máximo de 3 indicadores ativos por UORG já foi atingido."
        )

    novo_ind = await provider.criar_indicador(
        uorg_id=uorg_id,
        exercicio_id=exercicio_id,
        nome=dados["nome"].strip(),
        descricao=dados.get("descricao"),
        periodicidade=dados.get("periodicidade", "BIMESTRAL"),
        unidade_medida=dados["unidade_medida"].strip(),
        meta_operador=dados.get("meta_operador", "MAIOR_IGUAL"),
        meta_valor=dados["meta_valor"],
        meta_valor_max=dados.get("meta_valor_max"),
        ordem=dados.get("ordem", len(inds_existentes) + 1)
    )
    return novo_ind


async def editar_indicador_planejado(
    indicador_id: int,
    dados: Dict[str, Any],
    usuario_logado: Dict[str, Any],
    provider: RelatorioGestaoProviderInterface
) -> Dict[str, Any]:
    ind_antigo = await provider.obter_indicador(indicador_id)
    if not ind_antigo:
        raise HTTPException(status_code=404, detail="Indicador não encontrado.")

    validar_escopo_uorg(usuario_logado, ind_antigo["uorg_id"], apenas_leitura=False)
    await verificar_planejamento_aberto(ind_antigo["exercicio_id"], usuario_logado, provider)

    ind_atualizado = await provider.editar_indicador(indicador_id, dados)
    return {
        "indicador": ind_atualizado,
        "dados_anteriores": ind_antigo,
        "dados_novos": ind_atualizado
    }


async def inativar_indicador_planejado(
    indicador_id: int,
    usuario_logado: Dict[str, Any],
    provider: RelatorioGestaoProviderInterface
) -> Dict[str, Any]:
    ind_antigo = await provider.obter_indicador(indicador_id)
    if not ind_antigo:
        raise HTTPException(status_code=404, detail="Indicador não encontrado.")

    validar_escopo_uorg(usuario_logado, ind_antigo["uorg_id"], apenas_leitura=False)
    await verificar_planejamento_aberto(ind_antigo["exercicio_id"], usuario_logado, provider)

    sucesso = await provider.inativar_indicador(indicador_id)
    return {
        "sucesso": sucesso,
        "dados_anteriores": ind_antigo,
        "dados_novos": {"ativo": False}
    }


async def alterar_status_exercicio(
    exercicio_id: int,
    novo_status: str,
    usuario_logado: Dict[str, Any],
    provider: RelatorioGestaoProviderInterface
) -> Dict[str, Any]:
    perfil = usuario_logado.get("perfil", "")
    if perfil != "ADMINISTRADOR":
        raise HTTPException(
            status_code=403,
            detail="Apenas o Administrador pode alterar o status do exercício."
        )

    ex_antigo = await provider.obter_exercicio_por_id(exercicio_id)
    if not ex_antigo:
        raise HTTPException(status_code=404, detail="Exercício não encontrado.")

    ex_atualizado = await provider.atualizar_status_exercicio(exercicio_id, novo_status)
    return {
        "exercicio": ex_atualizado,
        "dados_anteriores": {"status": ex_antigo["status"]},
        "dados_novos": {"status": novo_status}
    }


# ---------------------------------------------------------
# Dashboard: Hierarquia de UORGs e Métricas Consolidadas
# ---------------------------------------------------------

async def listar_uorgs_acessiveis_dashboard(
    usuario_logado: Dict[str, Any],
    provider: RelatorioGestaoProviderInterface
) -> List[Dict[str, Any]]:
    """
    Retorna as UORGs acessíveis ao usuário no seletor do Dashboard respeitando a hierarquia:
    - ADMINISTRADOR / SUPERINTENDENTE: todas as UORGs ativas.
    - GERENTE: UORGs vinculadas à sua Gerência.
    - CHEFE / CHEFE_UORG: sua própria UORG e eventuais setores subordinados (se for Divisão).
    Inclui também o resumo de entregas concluídas (X/Y) de cada UORG para os cards compactos.
    """
    estrutura = await provider.listar_gerencias_com_uorgs()
    todas_uorgs: List[Dict[str, Any]] = []
    for g in estrutura:
        for u in g.get("uorgs", []):
            todas_uorgs.append({
                "id": u["id"],
                "sigla": u["sigla"],
                "nome": u["nome"],
                "tipo_uorg": u.get("tipo_uorg") or obter_tipo_uorg(u["sigla"], u["nome"]),
                "uorg_pai_sigla": u.get("uorg_pai_sigla") or SETOR_PAI_MAP.get((u["sigla"] or "").upper()),
                "subordinados_siglas": u.get("subordinados_siglas") or obter_subordinados_siglas(u["sigla"]),
                "gerencia_id": g["id"],
                "gerencia_sigla": g["sigla"],
                "gerencia_nome": g["nome"]
            })

    perfil = (usuario_logado.get("perfil") or "").upper()
    user_uorg_id = usuario_logado.get("uorg_id")
    user_gerencia_id = usuario_logado.get("gerencia_id")

    filtradas = todas_uorgs
    if perfil in ["ADMINISTRADOR", "SUPERINTENDENTE"]:
        filtradas = todas_uorgs
    elif perfil == "GERENTE":
        if user_gerencia_id:
            por_g = [u for u in todas_uorgs if int(u["gerencia_id"]) == int(user_gerencia_id)]
            if por_g:
                filtradas = por_g
        elif user_uorg_id:
            uorg_propria = next((u for u in todas_uorgs if int(u["id"]) == int(user_uorg_id)), None)
            if uorg_propria:
                filtradas = [u for u in todas_uorgs if int(u["gerencia_id"]) == int(uorg_propria["gerencia_id"])]
    else:
        # CHEFE / CHEFE_UORG / outros
        if user_uorg_id:
            uorg_propria = next((u for u in todas_uorgs if int(u["id"]) == int(user_uorg_id)), None)
            if uorg_propria:
                sigla_prop = (uorg_propria["sigla"] or "").upper()
                siglas_sub = DIVISAO_SUBORDINADAS_MAP.get(sigla_prop, [sigla_prop])
                filtradas = [u for u in todas_uorgs if (u["sigla"] or "").upper() in siglas_sub]
        elif user_gerencia_id:
            filtradas = [u for u in todas_uorgs if int(u["gerencia_id"]) == int(user_gerencia_id)]

    # Enriquecer com métricas resumidas de entregas (X/Y) do exercício ativo
    ex = await provider.obter_exercicio_ativo()
    resumos_map: Dict[int, Dict[str, Any]] = {}
    if ex and filtradas:
        resumos_map = await provider.obter_resumo_entregas_por_uorgs(
            ex["id"], [int(u["id"]) for u in filtradas]
        )

    for u in filtradas:
        r_info = resumos_map.get(int(u["id"]), {})
        u["concluidas"] = r_info.get("concluidas", 0)
        u["total"] = r_info.get("total", 0)
        u["pendentes"] = r_info.get("pendentes", 0)
        u["percentual_conclusao"] = r_info.get("percentual_conclusao", 0.0)
        u["relatorios_enviados"] = r_info.get("relatorios_enviados", 0)
        u["relatorios_com_feedback"] = r_info.get("relatorios_com_feedback", 0)
        u["tem_feedback"] = r_info.get("tem_feedback", False)

    return filtradas


async def obter_metricas_dashboard(
    uorg_id: int,
    exercicio_id: Optional[int],
    usuario_logado: Dict[str, Any],
    provider: RelatorioGestaoProviderInterface
) -> Dict[str, Any]:
    """
    Obtém métricas de entregas e série histórica de indicadores com metas para a UORG selecionada no Dashboard,
    validando se a UORG pertence ao escopo hierárquico do usuário.
    """
    uorgs_permitidas = await listar_uorgs_acessiveis_dashboard(usuario_logado, provider)
    ids_permitidos = {int(u["id"]) for u in uorgs_permitidas}

    if int(uorg_id) not in ids_permitidos:
        raise HTTPException(
            status_code=403,
            detail="Acesso negado: esta UORG não pertence à sua hierarquia de visualização."
        )

    if not exercicio_id:
        ex = await provider.obter_exercicio_ativo()
        if not ex:
            raise HTTPException(status_code=404, detail="Nenhum exercício ativo encontrado.")
        exercicio_id = ex["id"]

    uorg = await provider.obter_uorg_por_id(uorg_id)
    if not uorg:
        raise HTTPException(status_code=404, detail="UORG não encontrada.")

    metricas = await provider.obter_metricas_dashboard_uorg(exercicio_id, uorg_id)
    metricas["resumo_uorgs_contexto"] = uorgs_permitidas
    return metricas


