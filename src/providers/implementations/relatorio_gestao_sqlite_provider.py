# src/providers/implementations/relatorio_gestao_sqlite_provider.py
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.orm import selectinload

from ..interfaces.relatorio_gestao_provider_interface import RelatorioGestaoProviderInterface
from ...models import (
    Gerencia, Uorg, Exercicio, Bimestre, EntregaPlanejada, Indicador,
    RelatorioBimestral, ItemEntregaRelatorio, ItemIndicadorRelatorio,
    FeedbackRelatorio, PrazoExcepcional, Notificacao
)

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
            "itens_entrega": [
                {
                    "id": ie.id,
                    "entrega_id": ie.entrega_id,
                    "titulo": ie.entrega.titulo if ie.entrega else "",
                    "concluida": ie.concluida,
                    "observacoes": ie.observacoes or ""
                }
                for ie in rel.itens_entrega
            ],
            "itens_indicador": [
                {
                    "id": ii.id,
                    "indicador_id": ii.indicador_id,
                    "nome": ii.indicador.nome if ii.indicador else "",
                    "descricao": ii.indicador.descricao if ii.indicador else "",
                    "periodicidade": ii.indicador.periodicidade if ii.indicador else "BIMESTRAL",
                    "unidade_medida": ii.indicador.unidade_medida if ii.indicador else "PERCENTUAL",
                    "meta_operador": ii.indicador.meta_operador if ii.indicador else "MAIOR_IGUAL",
                    "meta_valor": ii.indicador.meta_valor if ii.indicador else None,
                    "meta_valor_max": ii.indicador.meta_valor_max if ii.indicador else None,
                    "competencia": ii.competencia,
                    "valor_apurado": ii.valor_apurado,
                    "meta_atingida": ii.meta_atingida,
                    "resultado_indisponivel": ii.resultado_indisponivel,
                    "justificativa_indisponibilidade": ii.justificativa_indisponibilidade or "",
                    "nao_aplicavel": ii.nao_aplicavel
                }
                for ii in rel.itens_indicador
            ],
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

        # Atualizar itens de entrega
        for item_data in dados.get("itens_entrega", []):
            e_id = item_data.get("entrega_id")
            concluida = item_data.get("concluida", False)
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

        # Atualizar itens de indicador
        for ind_data in dados.get("itens_indicador", []):
            i_id = ind_data.get("indicador_id")
            val = ind_data.get("valor_apurado")
            indisp = ind_data.get("resultado_indisponivel", False)
            just = ind_data.get("justificativa_indisponibilidade", "")
            comp = ind_data.get("competencia", "Bimestre")
            atingida = ind_data.get("meta_atingida")

            if i_id in itens_ind_map:
                item = itens_ind_map[i_id]
                item.valor_apurado = val
                item.resultado_indisponivel = indisp
                item.justificativa_indisponibilidade = just
                item.meta_atingida = atingida
            else:
                novo_ind = ItemIndicadorRelatorio(
                    relatorio_id=rel.id,
                    indicador_id=i_id,
                    competencia=comp,
                    valor_apurado=val,
                    meta_atingida=atingida,
                    resultado_indisponivel=indisp,
                    justificativa_indisponibilidade=just
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
        self, exercicio_id: int, bimestre_id: int, uorg_id: int, motivo: str, data_fim: str, usuario: str
    ) -> Dict[str, Any]:
        # Converter data_fim para datetime
        fim_dt = datetime.fromisoformat(data_fim.replace("Z", "+00:00")) if "T" in data_fim else datetime.strptime(data_fim, "%Y-%m-%d")

        pex = PrazoExcepcional(
            exercicio_id=exercicio_id,
            bimestre_id=bimestre_id,
            uorg_id=uorg_id,
            motivo=motivo,
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
        notif = Notificacao(
            uorg_id=uorg_id,
            destinatario_perfil="CHEFE_UORG",
            tipo="PRAZO_EXCEPCIONAL",
            titulo="Prazo Excepcional Concedido",
            mensagem=f"Foi concedido prazo excepcional para submissão até {fim_dt.strftime('%d/%m/%Y')}. Motivo: {motivo}",
            link=f"/preenchimento?bimestre={bimestre_id}&uorg={uorg_id}"
        )
        self.session.add(notif)
        await self.session.commit()

        return {
            "id": pex.id,
            "uorg_id": uorg_id,
            "bimestre_id": bimestre_id,
            "motivo": motivo,
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
                    "data_envio": rel.data_envio.isoformat() if rel and rel.data_envio else None
                })

            linhas.append({
                "uorg_id": u.id,
                "uorg_sigla": u.sigla,
                "uorg_nome": u.nome,
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
