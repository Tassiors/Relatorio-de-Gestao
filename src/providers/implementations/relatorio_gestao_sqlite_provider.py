# src/providers/implementations/relatorio_gestao_sqlite_provider.py
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.orm import selectinload

from ..interfaces.relatorio_gestao_provider_interface import RelatorioGestaoProviderInterface
from ...helpers.indicador_helper import obter_configuracao_periodicidade
from ...models import (
    Gerencia, Uorg, Exercicio, Bimestre, EntregaPlanejada, Indicador,
    RelatorioBimestral, ItemEntregaRelatorio, ItemIndicadorRelatorio,
    FeedbackRelatorio, PrazoExcepcional, Notificacao
)

DIVISOES_SIGLAS = {"DAF", "DLI", "DIVGP", "DADT", "DGC", "DMED", "DENF"}

DIVISAO_SUBORDINADAS_MAP: Dict[str, List[str]] = {
    "DAF": ["DAF", "SAD", "SGOF", "SCONT"],
    "DLI": ["DLI", "STEC", "STIF", "SAFS", "STHH"],
    "DIVGP": ["DIVGP"],
    "DADT": ["DADT", "STFH", "SADT"],
    "DGC": ["DGC", "STPC"],
    "DMED": ["DMED", "STPC"],
    "DENF": ["DENF", "STPC"],
}

SETOR_PAI_MAP: Dict[str, str] = {
    "SAD": "DAF",
    "SGOF": "DAF",
    "SCONT": "DAF",
    "STEC": "DLI",
    "STIF": "DLI",
    "SAFS": "DLI",
    "STHH": "DLI",
    "STFH": "DADT",
    "SADT": "DADT",
    "STPC": "DGC",
}

MESES_CURTOS_MAP: Dict[str, str] = {
    "Janeiro": "Jan",
    "Fevereiro": "Fev",
    "Março": "Mar",
    "Abril": "Abr",
    "Maio": "Mai",
    "Junho": "Jun",
    "Julho": "Jul",
    "Agosto": "Ago",
    "Setembro": "Set",
    "Outubro": "Out",
    "Novembro": "Nov",
    "Dezembro": "Dez",
}


def obter_tipo_uorg(sigla: Optional[str], nome: Optional[str] = None) -> str:
    """Identifica se a UORG é uma DIVISAO ou um SETOR conforme a estrutura do HC-UFPE/EBSERH."""
    sigla_up = (sigla or "").upper()
    nome_str = (nome or "").strip().lower()
    if sigla_up in DIVISOES_SIGLAS or nome_str.startswith("divisão") or nome_str.startswith("divisao"):
        return "DIVISAO"
    return "SETOR"


def obter_subordinados_siglas(sigla: Optional[str]) -> List[str]:
    """Retorna as siglas dos setores subordinados a uma Divisão (excluindo a própria sigla)."""
    sigla_up = (sigla or "").upper()
    return [s for s in DIVISAO_SUBORDINADAS_MAP.get(sigla_up, []) if s != sigla_up]


def formatar_rotulo_temporal(periodicidade: str, competencia: str, bimestre_numero: int) -> str:
    """Formata o rótulo do eixo X de acordo com a temporalidade (periodicidade) do indicador."""
    per = (periodicidade or "BIMESTRAL").upper()
    comp = (competencia or "").strip()
    if per == "MENSAL":
        return MESES_CURTOS_MAP.get(comp, comp[:3] if comp else f"{bimestre_numero}ºB")
    if per == "BIMESTRAL":
        return f"{bimestre_numero}ºB"
    if per == "TRIMESTRAL":
        trim_map = {2: "1ºT", 3: "2ºT", 5: "3ºT", 6: "4ºT"}
        return trim_map.get(bimestre_numero, comp[:3] if comp else f"{bimestre_numero}ºB")
    if per == "QUADRIMESTRAL":
        quad_map = {2: "1ºQ", 4: "2ºQ", 6: "3ºQ"}
        return quad_map.get(bimestre_numero, comp[:3] if comp else f"{bimestre_numero}ºB")
    if per == "SEMESTRAL":
        sem_map = {3: "1ºS", 6: "2ºS"}
        return sem_map.get(bimestre_numero, comp[:3] if comp else f"{bimestre_numero}ºB")
    return comp[:8] if comp else f"{bimestre_numero}ºB"


class RelatorioGestaoSqliteProvider(RelatorioGestaoProviderInterface):
    """Provedor assíncrono para o banco de dados SQLite local da aplicação."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def listar_gerencias_com_uorgs(self) -> List[Dict[str, Any]]:
        stmt = (
            select(Gerencia)
            .options(selectinload(Gerencia.uorgs))
            .filter(Gerencia.ativo == True)
            .order_by(Gerencia.ordem)
        )
        result = await self.session.execute(stmt)
        gerencias = result.scalars().all()

        output = []
        for g in gerencias:
            output.append({
                "id": g.id,
                "sigla": g.sigla,
                "nome": g.nome,
                "ordem": g.ordem,
                "uorgs": [
                    {
                        "id": u.id,
                        "sigla": u.sigla,
                        "nome": u.nome,
                        "codigo_redcap": u.codigo_redcap,
                        "tipo_uorg": obter_tipo_uorg(u.sigla, u.nome),
                        "uorg_pai_sigla": SETOR_PAI_MAP.get((u.sigla or "").upper()),
                        "subordinados_siglas": obter_subordinados_siglas(u.sigla),
                        "ordem": u.ordem,
                        "ativo": u.ativo
                    }
                    for u in sorted(g.uorgs, key=lambda x: x.ordem)
                    if u.ativo
                ]
            })
        return output

    async def obter_uorg_por_id(self, uorg_id: int) -> Optional[Dict[str, Any]]:
        stmt = select(Uorg).options(selectinload(Uorg.gerencia)).filter(Uorg.id == uorg_id)
        result = await self.session.execute(stmt)
        uorg = result.scalars().first()
        if not uorg:
            return None
        return {
            "id": uorg.id,
            "sigla": uorg.sigla,
            "nome": uorg.nome,
            "codigo_redcap": uorg.codigo_redcap,
            "tipo_uorg": obter_tipo_uorg(uorg.sigla, uorg.nome),
            "uorg_pai_sigla": SETOR_PAI_MAP.get((uorg.sigla or "").upper()),
            "subordinados_siglas": obter_subordinados_siglas(uorg.sigla),
            "gerencia_id": uorg.gerencia_id,
            "gerencia_sigla": uorg.gerencia.sigla if uorg.gerencia else None,
            "gerencia_nome": uorg.gerencia.nome if uorg.gerencia else None
        }

    async def obter_exercicio_ativo(self) -> Optional[Dict[str, Any]]:
        stmt = (
            select(Exercicio)
            .options(selectinload(Exercicio.bimestres))
            .filter(Exercicio.status.in_(["EM_ANDAMENTO", "PLANEJAMENTO"]))
            .order_by(desc(Exercicio.ano))
        )
        result = await self.session.execute(stmt)
        ex = result.scalars().first()
        if not ex:
            return None
        return {
            "id": ex.id,
            "ano": ex.ano,
            "descricao": ex.descricao,
            "status": ex.status,
            "bimestres": [
                {
                    "id": b.id,
                    "numero": b.numero,
                    "nome": b.nome,
                    "status": b.status,
                    "data_abertura": b.data_abertura.isoformat() if b.data_abertura else None,
                    "data_fechamento_regular": b.data_fechamento_regular.isoformat() if b.data_fechamento_regular else None
                }
                for b in sorted(ex.bimestres, key=lambda x: x.numero)
            ]
        }

    async def listar_exercicios(self) -> List[Dict[str, Any]]:
        stmt = select(Exercicio).order_by(desc(Exercicio.ano))
        result = await self.session.execute(stmt)
        exs = result.scalars().all()
        return [
            {"id": e.id, "ano": e.ano, "descricao": e.descricao, "status": e.status}
            for e in exs
        ]

    async def obter_exercicio_por_id(self, exercicio_id: int) -> Optional[Dict[str, Any]]:
        stmt = select(Exercicio).options(selectinload(Exercicio.bimestres)).filter(Exercicio.id == exercicio_id)
        result = await self.session.execute(stmt)
        ex = result.scalars().first()
        if not ex:
            return None
        return {
            "id": ex.id,
            "ano": ex.ano,
            "descricao": ex.descricao,
            "status": ex.status,
            "bimestres": [
                {
                    "id": b.id,
                    "numero": b.numero,
                    "nome": b.nome,
                    "status": b.status,
                    "data_abertura": b.data_abertura.isoformat() if b.data_abertura else None,
                    "data_fechamento_regular": b.data_fechamento_regular.isoformat() if b.data_fechamento_regular else None
                }
                for b in sorted(ex.bimestres, key=lambda x: x.numero)
            ]
        }

    async def obter_bimestres(self, exercicio_id: int) -> List[Dict[str, Any]]:
        stmt = select(Bimestre).filter(Bimestre.exercicio_id == exercicio_id).order_by(Bimestre.numero)
        result = await self.session.execute(stmt)
        bims = result.scalars().all()
        return [
            {
                "id": b.id,
                "numero": b.numero,
                "nome": b.nome,
                "status": b.status,
                "data_abertura": b.data_abertura.isoformat() if b.data_abertura else None,
                "data_fechamento_regular": b.data_fechamento_regular.isoformat() if b.data_fechamento_regular else None
            }
            for b in bims
        ]

    async def listar_entregas_uorg(self, exercicio_id: int, uorg_id: int) -> List[Dict[str, Any]]:
        stmt = (
            select(EntregaPlanejada)
            .filter(
                EntregaPlanejada.exercicio_id == exercicio_id,
                EntregaPlanejada.uorg_id == uorg_id,
                EntregaPlanejada.ativo == True
            )
            .order_by(EntregaPlanejada.ordem)
        )
        result = await self.session.execute(stmt)
        ents = result.scalars().all()
        return [
            {
                "id": ent.id,
                "titulo": ent.titulo,
                "descricao": ent.descricao,
                "concluida": ent.concluida,
                "bimestre_conclusao_id": ent.bimestre_conclusao_id,
                "data_conclusao": ent.data_conclusao.isoformat() if ent.data_conclusao else None,
                "usuario_conclusao": ent.usuario_conclusao,
                "ordem": ent.ordem
            }
            for ent in ents
        ]

    async def listar_indicadores_uorg(self, exercicio_id: int, uorg_id: int) -> List[Dict[str, Any]]:
        stmt = (
            select(Indicador)
            .filter(
                Indicador.exercicio_id == exercicio_id,
                Indicador.uorg_id == uorg_id,
                Indicador.ativo == True
            )
            .order_by(Indicador.ordem)
        )
        result = await self.session.execute(stmt)
        inds = result.scalars().all()
        return [
            {
                "id": ind.id,
                "nome": ind.nome,
                "descricao": ind.descricao,
                "periodicidade": ind.periodicidade,
                "unidade_medida": ind.unidade_medida,
                "meta_operador": ind.meta_operador,
                "meta_valor": ind.meta_valor,
                "meta_valor_max": ind.meta_valor_max,
                "ordem": ind.ordem
            }
            for ind in inds
        ]

    async def obter_relatorio(
        self, exercicio_id: int, bimestre_id: int, uorg_id: int
    ) -> Optional[Dict[str, Any]]:
        stmt = (
            select(RelatorioBimestral)
            .options(
                selectinload(RelatorioBimestral.itens_entrega).selectinload(ItemEntregaRelatorio.entrega),
                selectinload(RelatorioBimestral.itens_indicador).selectinload(ItemIndicadorRelatorio.indicador),
                selectinload(RelatorioBimestral.feedbacks),
                selectinload(RelatorioBimestral.bimestre),
                selectinload(RelatorioBimestral.uorg)
            )
            .filter(
                RelatorioBimestral.exercicio_id == exercicio_id,
                RelatorioBimestral.bimestre_id == bimestre_id,
                RelatorioBimestral.uorg_id == uorg_id
            )
        )
        result = await self.session.execute(stmt)
        rel = result.scalars().first()
        if not rel:
            return None

        # Verificar se há prazo excepcional ativo
        stmt_pex = (
            select(PrazoExcepcional)
            .filter(
                PrazoExcepcional.exercicio_id == exercicio_id,
                PrazoExcepcional.bimestre_id == bimestre_id,
                PrazoExcepcional.uorg_id == uorg_id,
                PrazoExcepcional.ativo == True,
                PrazoExcepcional.data_fim >= datetime.utcnow()
            )
            .order_by(desc(PrazoExcepcional.id))
        )
        res_pex = await self.session.execute(stmt_pex)
        pex = res_pex.scalars().first()

        # Mapa de bimestres do exercício para rastreabilidade de conclusão em cascata
        stmt_bims = select(Bimestre).filter(Bimestre.exercicio_id == exercicio_id)
        res_bims = await self.session.execute(stmt_bims)
        bims_map = {b.id: b for b in res_bims.scalars().all()}
        bim_atual_num = rel.bimestre.numero if rel.bimestre else (bims_map[bimestre_id].numero if bimestre_id in bims_map else bimestre_id)

        itens_entrega_out = []
        entregas_vistas = set()
        for ie in rel.itens_entrega:
            ent = ie.entrega
            entregas_vistas.add(ie.entrega_id)
            bim_conc_id = ent.bimestre_conclusao_id if ent else None
            bim_conc = bims_map.get(bim_conc_id) if bim_conc_id else None
            bim_conc_num = bim_conc.numero if bim_conc else None
            concluida_ant = bool(ent and ent.concluida and bim_conc_num is not None and bim_conc_num < bim_atual_num)
            concluida_efetiva = True if concluida_ant else bool(ie.concluida)
            itens_entrega_out.append({
                "id": ie.id,
                "entrega_id": ie.entrega_id,
                "titulo": ent.titulo if ent else "",
                "concluida": concluida_efetiva,
                "concluida_anteriormente": concluida_ant,
                "bimestre_conclusao_id": bim_conc_id,
                "bimestre_conclusao_nome": bim_conc.nome if bim_conc else None,
                "observacoes": ie.observacoes or ""
            })

        # Garantir que entregas ativas da UORG que não estavam no relatório (ex: criadas depois ou concluídas antes) apareçam
        stmt_ents = select(EntregaPlanejada).filter(
            EntregaPlanejada.exercicio_id == exercicio_id,
            EntregaPlanejada.uorg_id == uorg_id,
            EntregaPlanejada.ativo == True
        ).order_by(EntregaPlanejada.ordem)
        res_ents = await self.session.execute(stmt_ents)
        for ent in res_ents.scalars().all():
            if ent.id not in entregas_vistas:
                bim_conc_id = ent.bimestre_conclusao_id
                bim_conc = bims_map.get(bim_conc_id) if bim_conc_id else None
                bim_conc_num = bim_conc.numero if bim_conc else None
                concluida_ant = bool(ent.concluida and bim_conc_num is not None and bim_conc_num < bim_atual_num)
                itens_entrega_out.append({
                    "id": None,
                    "entrega_id": ent.id,
                    "titulo": ent.titulo,
                    "concluida": concluida_ant,
                    "concluida_anteriormente": concluida_ant,
                    "bimestre_conclusao_id": bim_conc_id,
                    "bimestre_conclusao_nome": bim_conc.nome if bim_conc else None,
                    "observacoes": ""
                })

        itens_indicador_out = []
        inds_vistos = set()
        for ii in rel.itens_indicador:
            ind = ii.indicador
            per = ind.periodicidade if ind else "BIMESTRAL"
            cfg = obter_configuracao_periodicidade(per, bim_atual_num)
            inds_vistos.add(ii.indicador_id)
            itens_indicador_out.append({
                "id": ii.id,
                "indicador_id": ii.indicador_id,
                "nome": ind.nome if ind else "",
                "descricao": ind.descricao if ind else "",
                "periodicidade": per,
                "unidade_medida": ind.unidade_medida if ind else "PERCENTUAL",
                "meta_operador": ind.meta_operador if ind else "MAIOR_IGUAL",
                "meta_valor": ind.meta_valor if ind else None,
                "meta_valor_max": ind.meta_valor_max if ind else None,
                "competencia": ii.competencia,
                "valor_apurado": ii.valor_apurado,
                "meta_atingida": ii.meta_atingida,
                "resultado_indisponivel": ii.resultado_indisponivel,
                "justificativa_indisponibilidade": ii.justificativa_indisponibilidade or "",
                "nao_aplicavel": ii.nao_aplicavel or not cfg["aplicavel"],
                "orientacao_periodicidade": cfg["orientacao"]
            })

        stmt_inds = select(Indicador).filter(
            Indicador.exercicio_id == exercicio_id,
            Indicador.uorg_id == uorg_id,
            Indicador.ativo == True
        ).order_by(Indicador.ordem)
        res_inds = await self.session.execute(stmt_inds)
        for ind in res_inds.scalars().all():
            if ind.id not in inds_vistos:
                cfg = obter_configuracao_periodicidade(ind.periodicidade, bim_atual_num)
                for comp in cfg["competencias"]:
                    itens_indicador_out.append({
                        "id": None,
                        "indicador_id": ind.id,
                        "nome": ind.nome,
                        "descricao": ind.descricao,
                        "periodicidade": ind.periodicidade,
                        "unidade_medida": ind.unidade_medida,
                        "meta_operador": ind.meta_operador,
                        "meta_valor": ind.meta_valor,
                        "meta_valor_max": ind.meta_valor_max,
                        "competencia": comp,
                        "valor_apurado": None,
                        "meta_atingida": None,
                        "resultado_indisponivel": False,
                        "justificativa_indisponibilidade": "",
                        "nao_aplicavel": not cfg["aplicavel"],
                        "orientacao_periodicidade": cfg["orientacao"]
                    })

        return {
            "id": rel.id,
            "exercicio_id": rel.exercicio_id,
            "bimestre_id": rel.bimestre_id,
            "bimestre_nome": rel.bimestre.nome if rel.bimestre else None,
            "bimestre_status": rel.bimestre.status if rel.bimestre else None,
            "uorg_id": rel.uorg_id,
            "uorg_sigla": rel.uorg.sigla if rel.uorg else None,
            "uorg_nome": rel.uorg.nome if rel.uorg else None,
            "status": rel.status,
            "versao": rel.versao,
            "data_envio": rel.data_envio.isoformat() if rel.data_envio else None,
            "usuario_envio": rel.usuario_envio,
            "destaques": rel.destaques or "",
            "dificuldades": rel.dificuldades or "",
            "prazo_excepcional": {
                "ativo": True,
                "data_fim": pex.data_fim.isoformat(),
                "motivo": pex.motivo
            } if pex else None,
            "itens_entrega": itens_entrega_out,
            "itens_indicador": itens_indicador_out,
            "feedbacks": [
                {
                    "id": fb.id,
                    "autor_username": fb.autor_username,
                    "autor_perfil": fb.autor_perfil,
                    "autor_nome": fb.autor_nome,
                    "texto": fb.texto_feedback,
                    "data": fb.created_at.isoformat() if fb.created_at else None
                }
                for fb in sorted(rel.feedbacks, key=lambda x: x.created_at or datetime.min)
            ]
        }

    async def salvar_rascunho(
        self, exercicio_id: int, bimestre_id: int, uorg_id: int, dados: Dict[str, Any], usuario: str
    ) -> Dict[str, Any]:
        stmt = (
            select(RelatorioBimestral)
            .options(
                selectinload(RelatorioBimestral.itens_entrega),
                selectinload(RelatorioBimestral.itens_indicador)
            )
            .filter(
                RelatorioBimestral.exercicio_id == exercicio_id,
                RelatorioBimestral.bimestre_id == bimestre_id,
                RelatorioBimestral.uorg_id == uorg_id
            )
        )
        result = await self.session.execute(stmt)
        rel = result.scalars().first()

        if not rel:
            rel = RelatorioBimestral(
                exercicio_id=exercicio_id,
                bimestre_id=bimestre_id,
                uorg_id=uorg_id,
                status="RASCUNHO",
                versao=1,
                destaques=dados.get("destaques", ""),
                dificuldades=dados.get("dificuldades", "")
            )
            self.session.add(rel)
            await self.session.flush()
            itens_entrega_map = {}
            itens_ind_map = {}
        else:
            rel.destaques = dados.get("destaques", rel.destaques)
            rel.dificuldades = dados.get("dificuldades", rel.dificuldades)
            if rel.status == "ENVIADO":
                rel.status = "EM_EDICAO"
            rel.updated_at = datetime.utcnow()
            itens_entrega_map = {ie.entrega_id: ie for ie in (rel.itens_entrega or [])}
            itens_ind_map = {ii.indicador_id: ii for ii in (rel.itens_indicador or [])}

        # Obter bimestres do exercício para propagação em cascata
        stmt_bims = select(Bimestre).filter(Bimestre.exercicio_id == exercicio_id).order_by(Bimestre.numero)
        res_bims = await self.session.execute(stmt_bims)
        todos_bims = res_bims.scalars().all()
        bims_by_id = {b.id: b for b in todos_bims}
        bim_atual = bims_by_id.get(bimestre_id)
        bim_atual_num = bim_atual.numero if bim_atual else bimestre_id
        bims_posteriores_ids = [b.id for b in todos_bims if b.numero > bim_atual_num]

        # Atualizar itens de entrega e propagar efeito cascata
        for item_data in dados.get("itens_entrega", []):
            e_id = item_data.get("entrega_id")
            concluida = bool(item_data.get("concluida", False))
            obs = item_data.get("observacoes", "")
            if e_id in itens_entrega_map:
                itens_entrega_map[e_id].concluida = concluida
                itens_entrega_map[e_id].observacoes = obs
            else:
                novo_item = ItemEntregaRelatorio(
                    relatorio_id=rel.id,
                    entrega_id=e_id,
                    concluida=concluida,
                    observacoes=obs
                )
                self.session.add(novo_item)

            # Buscar EntregaPlanejada para atualizar status anual e cascata nos bimestres seguintes
            stmt_ent = select(EntregaPlanejada).filter(EntregaPlanejada.id == e_id)
            res_ent = await self.session.execute(stmt_ent)
            ent = res_ent.scalars().first()
            if ent:
                bim_conc = bims_by_id.get(ent.bimestre_conclusao_id) if ent.bimestre_conclusao_id else None
                bim_conc_num = bim_conc.numero if bim_conc else None

                if concluida:
                    if not ent.concluida or bim_conc_num is None or bim_conc_num >= bim_atual_num:
                        ent.concluida = True
                        ent.bimestre_conclusao_id = bimestre_id
                        ent.data_conclusao = datetime.utcnow()
                        ent.usuario_conclusao = usuario

                    # Propagar status CONCLUIDA para relatórios já existentes em bimestres subsequentes
                    if bims_posteriores_ids:
                        stmt_rels_post = (
                            select(RelatorioBimestral)
                            .options(selectinload(RelatorioBimestral.itens_entrega))
                            .filter(
                                RelatorioBimestral.exercicio_id == exercicio_id,
                                RelatorioBimestral.uorg_id == uorg_id,
                                RelatorioBimestral.bimestre_id.in_(bims_posteriores_ids)
                            )
                        )
                        res_rels_post = await self.session.execute(stmt_rels_post)
                        for rel_post in res_rels_post.scalars().all():
                            ie_post = next((x for x in rel_post.itens_entrega if x.entrega_id == e_id), None)
                            if ie_post:
                                ie_post.concluida = True
                            else:
                                self.session.add(ItemEntregaRelatorio(
                                    relatorio_id=rel_post.id,
                                    entrega_id=e_id,
                                    concluida=True,
                                    observacoes=obs
                                ))
                else:
                    # Se foi desmarcada no próprio bimestre em que havia sido concluída, reverte a cascata
                    if ent.concluida and (ent.bimestre_conclusao_id == bimestre_id or bim_conc_num is None):
                        ent.concluida = False
                        ent.bimestre_conclusao_id = None
                        ent.data_conclusao = None
                        ent.usuario_conclusao = None
                        if bims_posteriores_ids:
                            stmt_rels_post = (
                                select(RelatorioBimestral)
                                .options(selectinload(RelatorioBimestral.itens_entrega))
                                .filter(
                                    RelatorioBimestral.exercicio_id == exercicio_id,
                                    RelatorioBimestral.uorg_id == uorg_id,
                                    RelatorioBimestral.bimestre_id.in_(bims_posteriores_ids)
                                )
                            )
                            res_rels_post = await self.session.execute(stmt_rels_post)
                            for rel_post in res_rels_post.scalars().all():
                                ie_post = next((x for x in rel_post.itens_entrega if x.entrega_id == e_id), None)
                                if ie_post:
                                    ie_post.concluida = False

        # Atualizar itens de indicador (suportando múltiplas competências para indicadores MENSAL)
        itens_ind_por_chave = {(ii.indicador_id, ii.competencia): ii for ii in (rel.itens_indicador or [])}
        usados_ids = set()

        for ind_data in dados.get("itens_indicador", []):
            i_id = ind_data.get("indicador_id")
            val = ind_data.get("valor_apurado")
            indisp = bool(ind_data.get("resultado_indisponivel", False))
            just = ind_data.get("justificativa_indisponibilidade", "")
            comp = ind_data.get("competencia", "Bimestre")
            atingida = ind_data.get("meta_atingida")
            nao_aplic = bool(ind_data.get("nao_aplicavel", False))

            item = itens_ind_por_chave.get((i_id, comp))
            if not item and i_id in itens_ind_map and itens_ind_map[i_id].id not in usados_ids:
                # Fallback caso tenha apenas 1 registro prévio com outra descrição de competência
                candidatos = [x for x in (rel.itens_indicador or []) if x.indicador_id == i_id and x.id not in usados_ids]
                if len(candidatos) == 1:
                    item = candidatos[0]

            if item:
                usados_ids.add(item.id)
                item.competencia = comp
                item.valor_apurado = val
                item.resultado_indisponivel = indisp
                item.justificativa_indisponibilidade = just
                item.meta_atingida = atingida
                item.nao_aplicavel = nao_aplic
            else:
                novo_ind = ItemIndicadorRelatorio(
                    relatorio_id=rel.id,
                    indicador_id=i_id,
                    competencia=comp,
                    valor_apurado=val,
                    meta_atingida=atingida,
                    resultado_indisponivel=indisp,
                    justificativa_indisponibilidade=just,
                    nao_aplicavel=nao_aplic
                )
                self.session.add(novo_ind)

        await self.session.commit()
        return await self.obter_relatorio(exercicio_id, bimestre_id, uorg_id)

    async def enviar_relatorio(self, relatorio_id: int, usuario: str) -> Dict[str, Any]:
        stmt = (
            select(RelatorioBimestral)
            .options(
                selectinload(RelatorioBimestral.itens_entrega).selectinload(ItemEntregaRelatorio.entrega)
            )
            .filter(RelatorioBimestral.id == relatorio_id)
        )
        result = await self.session.execute(stmt)
        rel = result.scalars().first()
        if not rel:
            raise ValueError("Relatório não encontrado.")

        rel.status = "ENVIADO"
        rel.data_envio = datetime.utcnow()
        rel.usuario_envio = usuario
        rel.versao += 1

        # Atualizar status das entregas concluídas no cadastro anual
        for ie in rel.itens_entrega:
            if ie.concluida and ie.entrega and not ie.entrega.concluida:
                ie.entrega.concluida = True
                ie.entrega.bimestre_conclusao_id = rel.bimestre_id
                ie.entrega.data_conclusao = datetime.utcnow()
                ie.entrega.usuario_conclusao = usuario

        # Se havia prazo excepcional ativo, inativa
        stmt_pex = select(PrazoExcepcional).filter(
            PrazoExcepcional.exercicio_id == rel.exercicio_id,
            PrazoExcepcional.bimestre_id == rel.bimestre_id,
            PrazoExcepcional.uorg_id == rel.uorg_id,
            PrazoExcepcional.ativo == True
        )
        res_pex = await self.session.execute(stmt_pex)
        for p in res_pex.scalars().all():
            p.ativo = False

        await self.session.commit()
        return await self.obter_relatorio(rel.exercicio_id, rel.bimestre_id, rel.uorg_id)

    async def registrar_feedback(
        self, relatorio_id: int, usuario: str, perfil: str, nome: str, texto: str
    ) -> Dict[str, Any]:
        stmt = select(RelatorioBimestral).filter(RelatorioBimestral.id == relatorio_id)
        result = await self.session.execute(stmt)
        rel = result.scalars().first()
        if not rel:
            raise ValueError("Relatório não encontrado.")

        fb = FeedbackRelatorio(
            relatorio_id=relatorio_id,
            autor_username=usuario,
            autor_perfil=perfil,
            autor_nome=nome,
            texto_feedback=texto
        )
        self.session.add(fb)

        # Criar notificação para a UORG
        notif = Notificacao(
            uorg_id=rel.uorg_id,
            destinatario_perfil="CHEFE_UORG",
            tipo="FEEDBACK_RECEBIDO",
            titulo=f"Parecer Institucional Recebido",
            mensagem=f"O {nome} ({perfil}) emitiu parecer sobre o relatório do {rel.bimestre_id}º Bimestre.",
            link=f"/relatorio/{rel.id}"
        )
        self.session.add(notif)
        await self.session.commit()

        return {
            "id": fb.id,
            "relatorio_id": relatorio_id,
            "autor_nome": nome,
            "autor_perfil": perfil,
            "texto": texto,
            "data": fb.created_at.isoformat() if fb.created_at else None
        }

    async def conceder_prazo_excepcional(
        self, exercicio_id: int, bimestre_id: int, uorg_id: int, motivo: Optional[str], data_fim: str, usuario: str
    ) -> Dict[str, Any]:
        # Converter data_fim para datetime
        fim_dt = datetime.fromisoformat(data_fim.replace("Z", "+00:00")) if "T" in data_fim else datetime.strptime(data_fim, "%Y-%m-%d")
        motivo_limpo = motivo.strip() if motivo else None

        pex = PrazoExcepcional(
            exercicio_id=exercicio_id,
            bimestre_id=bimestre_id,
            uorg_id=uorg_id,
            motivo=motivo_limpo or "",
            data_inicio=datetime.utcnow(),
            data_fim=fim_dt,
            concedido_por_username=usuario,
            ativo=True
        )
        self.session.add(pex)

        # Atualizar status do relatório se existir
        stmt = select(RelatorioBimestral).filter(
            RelatorioBimestral.exercicio_id == exercicio_id,
            RelatorioBimestral.bimestre_id == bimestre_id,
            RelatorioBimestral.uorg_id == uorg_id
        )
        res_rel = await self.session.execute(stmt)
        rel = res_rel.scalars().first()
        if rel and rel.status == "ENVIADO":
            rel.status = "PRAZO_EXCEPCIONAL"

        # Notificar UORG
        msg_motivo = f" Motivo: {motivo_limpo}" if motivo_limpo else ""
        notif = Notificacao(
            uorg_id=uorg_id,
            destinatario_perfil="CHEFE_UORG",
            tipo="PRAZO_EXCEPCIONAL",
            titulo="Prazo Excepcional Concedido",
            mensagem=f"Foi concedido prazo excepcional para submissão até {fim_dt.strftime('%d/%m/%Y')}.{msg_motivo}",
            link=f"/preenchimento?bimestre={bimestre_id}&uorg={uorg_id}"
        )
        self.session.add(notif)
        await self.session.commit()

        return {
            "id": pex.id,
            "uorg_id": uorg_id,
            "bimestre_id": bimestre_id,
            "motivo": motivo_limpo,
            "data_fim": pex.data_fim.isoformat(),
            "ativo": True
        }

    async def obter_matriz_acompanhamento(self, exercicio_id: int) -> Dict[str, Any]:
        # Buscar UORGs com Gerências
        stmt_uorgs = (
            select(Uorg)
            .options(selectinload(Uorg.gerencia))
            .filter(Uorg.ativo == True)
            .order_by(Uorg.gerencia_id, Uorg.ordem)
        )
        res_uorgs = await self.session.execute(stmt_uorgs)
        uorgs = res_uorgs.scalars().all()

        # Buscar Bimestres
        stmt_bims = select(Bimestre).filter(Bimestre.exercicio_id == exercicio_id).order_by(Bimestre.numero)
        res_bims = await self.session.execute(stmt_bims)
        bimestres = res_bims.scalars().all()

        # Buscar Relatórios
        stmt_rels = select(RelatorioBimestral).options(selectinload(RelatorioBimestral.feedbacks)).filter(RelatorioBimestral.exercicio_id == exercicio_id)
        res_rels = await self.session.execute(stmt_rels)
        relatorios = res_rels.scalars().all()
        rels_map = {(r.uorg_id, r.bimestre_id): r for r in relatorios}

        # Buscar Prazos Excepcionais Ativos
        stmt_pex = select(PrazoExcepcional).filter(
            PrazoExcepcional.exercicio_id == exercicio_id,
            PrazoExcepcional.ativo == True,
            PrazoExcepcional.data_fim >= datetime.utcnow()
        )
        res_pex = await self.session.execute(stmt_pex)
        pex_map = {(p.uorg_id, p.bimestre_id): p for p in res_pex.scalars().all()}

        linhas = []
        totais = {"enviados": 0, "pendentes": 0, "em_edicao": 0, "prazo_excepcional": 0}

        for u in uorgs:
            colunas = []
            for b in bimestres:
                rel = rels_map.get((u.id, b.id))
                pex = pex_map.get((u.id, b.id))

                if pex:
                    status_celula = "PRAZO_EXCEPCIONAL"
                    totais["prazo_excepcional"] += 1
                elif rel:
                    status_celula = rel.status
                    if rel.status == "ENVIADO":
                        totais["enviados"] += 1
                    elif rel.status == "EM_EDICAO":
                        totais["em_edicao"] += 1
                    else:
                        totais["pendentes"] += 1
                else:
                    if b.status == "ABERTO":
                        status_celula = "PENDENTE"
                        totais["pendentes"] += 1
                    else:
                        status_celula = "NAO_INICIADO"

                colunas.append({
                    "bimestre_id": b.id,
                    "bimestre_numero": b.numero,
                    "bimestre_status": b.status,
                    "relatorio_id": rel.id if rel else None,
                    "status": status_celula,
                    "tem_feedback": len(rel.feedbacks) > 0 if rel else False,
                    "feedbacks_count": len(rel.feedbacks) if rel else 0,
                    "data_envio": rel.data_envio.isoformat() if rel and rel.data_envio else None
                })

            linhas.append({
                "uorg_id": u.id,
                "uorg_sigla": u.sigla,
                "uorg_nome": u.nome,
                "tipo_uorg": obter_tipo_uorg(u.sigla, u.nome),
                "uorg_pai_sigla": SETOR_PAI_MAP.get((u.sigla or "").upper()),
                "subordinados_siglas": obter_subordinados_siglas(u.sigla),
                "gerencia_id": u.gerencia_id,
                "gerencia_sigla": u.gerencia.sigla if u.gerencia else "",
                "bimestres": colunas
            })

        return {
            "exercicio_id": exercicio_id,
            "bimestres": [{"id": b.id, "numero": b.numero, "nome": b.nome, "status": b.status} for b in bimestres],
            "linhas": linhas,
            "totais": totais
        }

    async def listar_notificacoes(
        self, username: str, perfil: Optional[str] = None, uorg_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        conditions = [
            Notificacao.destinatario_username == username,
            Notificacao.destinatario_username == None
        ]
        if perfil:
            conditions.append(Notificacao.destinatario_perfil == perfil)
        if uorg_id:
            conditions.append(Notificacao.uorg_id == uorg_id)

        stmt = select(Notificacao).filter(or_(*conditions)).order_by(desc(Notificacao.created_at)).limit(50)
        result = await self.session.execute(stmt)
        notifs = result.scalars().all()
        return [
            {
                "id": n.id,
                "tipo": n.tipo,
                "titulo": n.titulo,
                "mensagem": n.mensagem,
                "link": n.link,
                "lida": n.lida,
                "data": n.created_at.isoformat() if n.created_at else None
            }
            for n in notifs
        ]

    async def marcar_notificacao_lida(self, notificacao_id: int) -> bool:
        stmt = select(Notificacao).filter(Notificacao.id == notificacao_id)
        result = await self.session.execute(stmt)
        notif = result.scalars().first()
        if notif:
            notif.lida = True
            await self.session.commit()
            return True
        return False

    async def criar_entrega(
        self, uorg_id: int, exercicio_id: int, titulo: str, descricao: Optional[str] = None, ordem: int = 1
    ) -> Dict[str, Any]:
        entrega = EntregaPlanejada(
            uorg_id=uorg_id,
            exercicio_id=exercicio_id,
            titulo=titulo,
            descricao=descricao,
            ordem=ordem,
            concluida=False,
            ativo=True
        )
        self.session.add(entrega)
        await self.session.commit()
        await self.session.refresh(entrega)
        return {
            "id": entrega.id,
            "uorg_id": entrega.uorg_id,
            "exercicio_id": entrega.exercicio_id,
            "titulo": entrega.titulo,
            "descricao": entrega.descricao,
            "concluida": entrega.concluida,
            "ordem": entrega.ordem,
            "ativo": entrega.ativo
        }

    async def obter_entrega(self, entrega_id: int) -> Optional[Dict[str, Any]]:
        stmt = select(EntregaPlanejada).filter(EntregaPlanejada.id == entrega_id)
        result = await self.session.execute(stmt)
        ent = result.scalars().first()
        if not ent:
            return None
        return {
            "id": ent.id,
            "uorg_id": ent.uorg_id,
            "exercicio_id": ent.exercicio_id,
            "titulo": ent.titulo,
            "descricao": ent.descricao,
            "concluida": ent.concluida,
            "ordem": ent.ordem,
            "ativo": ent.ativo
        }

    async def editar_entrega(
        self, entrega_id: int, titulo: str, descricao: Optional[str] = None
    ) -> Dict[str, Any]:
        stmt = select(EntregaPlanejada).filter(EntregaPlanejada.id == entrega_id)
        result = await self.session.execute(stmt)
        ent = result.scalars().first()
        if not ent:
            raise ValueError("Entrega planejada não encontrada.")
        ent.titulo = titulo
        if descricao is not None:
            ent.descricao = descricao
        await self.session.commit()
        await self.session.refresh(ent)
        return {
            "id": ent.id,
            "uorg_id": ent.uorg_id,
            "exercicio_id": ent.exercicio_id,
            "titulo": ent.titulo,
            "descricao": ent.descricao,
            "concluida": ent.concluida,
            "ordem": ent.ordem,
            "ativo": ent.ativo
        }

    async def inativar_entrega(self, entrega_id: int) -> bool:
        stmt = select(EntregaPlanejada).filter(EntregaPlanejada.id == entrega_id)
        result = await self.session.execute(stmt)
        ent = result.scalars().first()
        if not ent:
            return False
        ent.ativo = False
        await self.session.commit()
        return True

    async def criar_indicador(
        self, uorg_id: int, exercicio_id: int, nome: str, descricao: Optional[str],
        periodicidade: str, unidade_medida: str, meta_operador: str,
        meta_valor: float, meta_valor_max: Optional[float] = None, ordem: int = 1
    ) -> Dict[str, Any]:
        ind = Indicador(
            uorg_id=uorg_id,
            exercicio_id=exercicio_id,
            nome=nome,
            descricao=descricao,
            periodicidade=periodicidade,
            unidade_medida=unidade_medida,
            meta_operador=meta_operador,
            meta_valor=meta_valor,
            meta_valor_max=meta_valor_max,
            ordem=ordem,
            ativo=True
        )
        self.session.add(ind)
        await self.session.commit()
        await self.session.refresh(ind)
        return {
            "id": ind.id,
            "uorg_id": ind.uorg_id,
            "exercicio_id": ind.exercicio_id,
            "nome": ind.nome,
            "descricao": ind.descricao,
            "periodicidade": ind.periodicidade,
            "unidade_medida": ind.unidade_medida,
            "meta_operador": ind.meta_operador,
            "meta_valor": ind.meta_valor,
            "meta_valor_max": ind.meta_valor_max,
            "ordem": ind.ordem,
            "ativo": ind.ativo
        }

    async def obter_indicador(self, indicador_id: int) -> Optional[Dict[str, Any]]:
        stmt = select(Indicador).filter(Indicador.id == indicador_id)
        result = await self.session.execute(stmt)
        ind = result.scalars().first()
        if not ind:
            return None
        return {
            "id": ind.id,
            "uorg_id": ind.uorg_id,
            "exercicio_id": ind.exercicio_id,
            "nome": ind.nome,
            "descricao": ind.descricao,
            "periodicidade": ind.periodicidade,
            "unidade_medida": ind.unidade_medida,
            "meta_operador": ind.meta_operador,
            "meta_valor": ind.meta_valor,
            "meta_valor_max": ind.meta_valor_max,
            "ordem": ind.ordem,
            "ativo": ind.ativo
        }

    async def editar_indicador(
        self, indicador_id: int, dados: Dict[str, Any]
    ) -> Dict[str, Any]:
        stmt = select(Indicador).filter(Indicador.id == indicador_id)
        result = await self.session.execute(stmt)
        ind = result.scalars().first()
        if not ind:
            raise ValueError("Indicador não encontrado.")
        for campo in ["nome", "descricao", "periodicidade", "unidade_medida", "meta_operador", "meta_valor", "meta_valor_max"]:
            if campo in dados and dados[campo] is not None:
                setattr(ind, campo, dados[campo])
        await self.session.commit()
        await self.session.refresh(ind)
        return {
            "id": ind.id,
            "uorg_id": ind.uorg_id,
            "exercicio_id": ind.exercicio_id,
            "nome": ind.nome,
            "descricao": ind.descricao,
            "periodicidade": ind.periodicidade,
            "unidade_medida": ind.unidade_medida,
            "meta_operador": ind.meta_operador,
            "meta_valor": ind.meta_valor,
            "meta_valor_max": ind.meta_valor_max,
            "ordem": ind.ordem,
            "ativo": ind.ativo
        }

    async def inativar_indicador(self, indicador_id: int) -> bool:
        stmt = select(Indicador).filter(Indicador.id == indicador_id)
        result = await self.session.execute(stmt)
        ind = result.scalars().first()
        if not ind:
            return False
        ind.ativo = False
        await self.session.commit()
        return True

    async def atualizar_status_exercicio(
        self, exercicio_id: int, status: str
    ) -> Dict[str, Any]:
        stmt = select(Exercicio).filter(Exercicio.id == exercicio_id)
        result = await self.session.execute(stmt)
        ex = result.scalars().first()
        if not ex:
            raise ValueError("Exercício não encontrado.")
        ex.status = status
        await self.session.commit()
        await self.session.refresh(ex)
        return {
            "id": ex.id,
            "ano": ex.ano,
            "descricao": ex.descricao,
            "status": ex.status
        }

    async def atualizar_bimestre(
        self, bimestre_id: int, status: Optional[str] = None, data_fechamento_regular: Optional[str] = None
    ) -> Dict[str, Any]:
        stmt = select(Bimestre).filter(Bimestre.id == bimestre_id)
        result = await self.session.execute(stmt)
        bim = result.scalars().first()
        if not bim:
            raise ValueError("Bimestre não encontrado.")

        if status is not None:
            bim.status = status
            if status == "ABERTO" and not bim.data_abertura:
                bim.data_abertura = datetime.utcnow()

        if data_fechamento_regular is not None:
            if data_fechamento_regular == "":
                bim.data_fechamento_regular = None
            else:
                dt_str = data_fechamento_regular.split("T")[0]
                bim.data_fechamento_regular = datetime.strptime(dt_str, "%Y-%m-%d")

        await self.session.commit()
        await self.session.refresh(bim)
        return {
            "id": bim.id,
            "exercicio_id": bim.exercicio_id,
            "numero": bim.numero,
            "nome": bim.nome,
            "status": bim.status,
            "data_abertura": bim.data_abertura.isoformat() if bim.data_abertura else None,
            "data_fechamento_regular": bim.data_fechamento_regular.isoformat() if bim.data_fechamento_regular else None
        }

    async def obter_metricas_dashboard_uorg(
        self, exercicio_id: int, uorg_id: int
    ) -> Dict[str, Any]:
        uorg_info = await self.obter_uorg_por_id(uorg_id)
        bimestres = await self.obter_bimestres(exercicio_id)
        bims_map = {b["id"]: b for b in bimestres}

        # Entregas da UORG selecionada
        entregas = await self.listar_entregas_uorg(exercicio_id, uorg_id)
        for ent in entregas:
            bim_conc_id = ent.get("bimestre_conclusao_id")
            ent["bimestre_conclusao_nome"] = bims_map[bim_conc_id]["nome"] if bim_conc_id in bims_map else None

        total_entregas = len(entregas)
        entregas_concluidas = sum(1 for e in entregas if e.get("concluida"))
        pct_conclusao = round((entregas_concluidas / total_entregas) * 100, 1) if total_entregas > 0 else 0.0

        # Resumo global de entregas do exercício (todas as UORGs)
        stmt_global = select(EntregaPlanejada).filter(
            EntregaPlanejada.exercicio_id == exercicio_id,
            EntregaPlanejada.ativo == True
        )
        res_global = await self.session.execute(stmt_global)
        ents_globais = res_global.scalars().all()
        total_global = len(ents_globais)
        concluidas_global = sum(1 for e in ents_globais if e.concluida)
        pct_global = round((concluidas_global / total_global) * 100, 1) if total_global > 0 else 0.0

        # Indicadores da UORG e série histórica por bimestre/temporalidade
        indicadores = await self.listar_indicadores_uorg(exercicio_id, uorg_id)
        stmt_rels = (
            select(RelatorioBimestral)
            .options(
                selectinload(RelatorioBimestral.itens_indicador),
                selectinload(RelatorioBimestral.feedbacks)
            )
            .filter(
                RelatorioBimestral.exercicio_id == exercicio_id,
                RelatorioBimestral.uorg_id == uorg_id
            )
        )
        res_rels = await self.session.execute(stmt_rels)
        rels_uorg = res_rels.scalars().all()
        rels_by_bim = {r.bimestre_id: r for r in rels_uorg}

        # Bimestres respondidos pela UORG (para sinalização no dashboard do Chefe de Setor e destaque de feedback)
        bimestres_respondidos = []
        for bim in bimestres:
            rel_b = rels_by_bim.get(bim["id"])
            status_rel = rel_b.status if rel_b else ("PENDENTE" if bim["status"] == "ABERTO" else "NAO_INICIADO")
            tem_fb = (len(rel_b.feedbacks) > 0) if rel_b else False
            bimestres_respondidos.append({
                "bimestre_id": bim["id"],
                "bimestre_numero": bim["numero"],
                "bimestre_nome": bim["nome"],
                "bimestre_status": bim["status"],
                "relatorio_id": rel_b.id if rel_b else None,
                "status_relatorio": status_rel,
                "respondido": status_rel == "ENVIADO",
                "tem_feedback": tem_fb,
                "feedbacks_count": len(rel_b.feedbacks) if rel_b else 0,
                "data_envio": rel_b.data_envio.isoformat() if (rel_b and rel_b.data_envio) else None
            })

        indicadores_com_serie = []
        for ind in indicadores:
            serie = []
            for bim in bimestres:
                cfg = obter_configuracao_periodicidade(ind["periodicidade"], bim["numero"])
                # Eixo X estritamente de acordo com a temporalidade do indicador (omite bimestres não aplicáveis)
                if not cfg["aplicavel"]:
                    continue

                rel_b = rels_by_bim.get(bim["id"])
                if rel_b:
                    itens_ind_b = [
                        ii for ii in rel_b.itens_indicador
                        if ii.indicador_id == ind["id"] and not ii.nao_aplicavel
                    ]
                else:
                    itens_ind_b = []

                if itens_ind_b:
                    # Ordenar para preservar a ordem das competências esperadas (ex: Janeiro, Fevereiro)
                    comp_order = {c: idx for idx, c in enumerate(cfg["competencias"])}
                    itens_ind_b_sorted = sorted(itens_ind_b, key=lambda x: comp_order.get(x.competencia, 99))
                    for ii in itens_ind_b_sorted:
                        rotulo_x = formatar_rotulo_temporal(ind["periodicidade"], ii.competencia, bim["numero"])
                        serie.append({
                            "bimestre_id": bim["id"],
                            "bimestre_numero": bim["numero"],
                            "bimestre_nome": bim["nome"],
                            "competencia": ii.competencia,
                            "rotulo_eixo_x": rotulo_x,
                            "valor_apurado": ii.valor_apurado,
                            "meta_atingida": ii.meta_atingida,
                            "resultado_indisponivel": ii.resultado_indisponivel,
                            "nao_aplicavel": False
                        })
                else:
                    for comp in cfg["competencias"]:
                        rotulo_x = formatar_rotulo_temporal(ind["periodicidade"], comp, bim["numero"])
                        serie.append({
                            "bimestre_id": bim["id"],
                            "bimestre_numero": bim["numero"],
                            "bimestre_nome": bim["nome"],
                            "competencia": comp,
                            "rotulo_eixo_x": rotulo_x,
                            "valor_apurado": None,
                            "meta_atingida": None,
                            "resultado_indisponivel": False,
                            "nao_aplicavel": False
                        })

            indicadores_com_serie.append({
                **ind,
                "serie_historica": serie
            })

        return {
            "uorg": uorg_info,
            "resumo_entregas": {
                "total": total_entregas,
                "concluidas": entregas_concluidas,
                "pendentes": total_entregas - entregas_concluidas,
                "percentual_conclusao": pct_conclusao
            },
            "resumo_entregas_institucional": {
                "total": total_global,
                "concluidas": concluidas_global,
                "pendentes": total_global - concluidas_global,
                "percentual_conclusao": pct_global
            },
            "bimestres_respondidos": bimestres_respondidos,
            "entregas": entregas,
            "indicadores": indicadores_com_serie
        }

    async def obter_resumo_entregas_por_uorgs(
        self, exercicio_id: int, uorgs_ids: List[int]
    ) -> Dict[int, Dict[str, Any]]:
        if not uorgs_ids:
            return {}

        stmt_ents = select(EntregaPlanejada).filter(
            EntregaPlanejada.exercicio_id == exercicio_id,
            EntregaPlanejada.uorg_id.in_(uorgs_ids),
            EntregaPlanejada.ativo == True
        )
        res_ents = await self.session.execute(stmt_ents)
        ents = res_ents.scalars().all()

        stmt_rels = (
            select(RelatorioBimestral)
            .options(selectinload(RelatorioBimestral.feedbacks))
            .filter(
                RelatorioBimestral.exercicio_id == exercicio_id,
                RelatorioBimestral.uorg_id.in_(uorgs_ids)
            )
        )
        res_rels = await self.session.execute(stmt_rels)
        rels = res_rels.scalars().all()

        resumo_map: Dict[int, Dict[str, Any]] = {
            uid: {
                "total": 0,
                "concluidas": 0,
                "pendentes": 0,
                "percentual_conclusao": 0.0,
                "relatorios_enviados": 0,
                "relatorios_com_feedback": 0,
                "tem_feedback": False
            }
            for uid in uorgs_ids
        }

        for e in ents:
            info = resumo_map.get(e.uorg_id)
            if info is not None:
                info["total"] += 1
                if e.concluida:
                    info["concluidas"] += 1

        for r in rels:
            info = resumo_map.get(r.uorg_id)
            if info is not None:
                if r.status == "ENVIADO":
                    info["relatorios_enviados"] += 1
                if r.feedbacks and len(r.feedbacks) > 0:
                    info["relatorios_com_feedback"] += 1
                    info["tem_feedback"] = True

        for uid, info in resumo_map.items():
            tot = info["total"]
            conc = info["concluidas"]
            info["pendentes"] = tot - conc
            info["percentual_conclusao"] = round((conc / tot) * 100, 1) if tot > 0 else 0.0

        return resumo_map




