# src/scripts/seed_from_redcap.py
import sys
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adicionar raiz ao PYTHONPATH
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT_DIR)

from src.models import (
    Gerencia, Uorg, UsuarioUorg, Exercicio, Bimestre,
    EntregaPlanejada, Indicador
)

def run_seed():
    db_path = os.path.join(ROOT_DIR, "data", "app.db")
    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)
    session = Session()

    xml_path = os.path.join(ROOT_DIR, "data", "redcap", "RelatriosDeGesto2026_2026-10-26_1600.REDCap.xml")
    if not os.path.exists(xml_path):
        print(f"Arquivo REDCap não encontrado em {xml_path}")
        return

    tree = ET.parse(xml_path)
    root = tree.getroot()
    ns = {"odm": "http://www.cdisc.org/ns/odm/v1.3", "redcap": "https://projectredcap.org"}
    study = root.find("odm:Study", ns)
    mdv = study.find("odm:MetaDataVersion", ns)

    print("=== Iniciando Carga Inicial do REDCap ===")

    # 1. Gerências
    gerencias_map = {
        "SUP": {"nome": "Superintendência", "ordem": 1, "choices_oid": "uorg_sup.choices"},
        "GAD": {"nome": "Gerência Administrativa", "ordem": 2, "choices_oid": "uorg_gad.choices"},
        "GAS": {"nome": "Gerência de Atenção à Saúde", "ordem": 3, "choices_oid": "uorg_gas.choices"},
        "GEP": {"nome": "Gerência de Ensino e Pesquisa", "ordem": 4, "choices_oid": "uorg_gep.choices"}
    }

    gerencia_objs = {}
    for sigla, info in gerencias_map.items():
        g = session.query(Gerencia).filter_by(sigla=sigla).first()
        if not g:
            g = Gerencia(sigla=sigla, nome=info["nome"], ordem=info["ordem"])
            session.add(g)
            session.flush()
        gerencia_objs[sigla] = g
    print(f"Gerências carregadas: {len(gerencia_objs)}")

    # 2. UORGs a partir das escolhas no REDCap
    uorg_sigla_map = {
        "Setor de Gestão da Qualidade": ("STGQ", "stgq"),
        "Setor de Governança e Estratégia": ("SEGOV", "segov"),
        "Setor de Tecnologia da Informação e Saúde Digital": ("SETISD", "setisd"),
        "Setor de Contratualização e Regulação": ("STCOR", "stcor"),
        "Divisão de Administração e Finanças": ("DAF", "daf"),
        "Setor de Administração": ("SAD", "sad"),
        "Setor de Gestão Orçamentária e Financeira": ("SGOF", "sgof"),
        "Setor de Contabilidade": ("SCONT", "scont"),
        "Divisão de Logística e Infraestrutura": ("DLI", "dli"),
        "Setor de Engenharia Clínica": ("STEC", "stec"),
        "Setor de Infraestrutura Física": ("STIF", "stif"),
        "Setor de Abastecimento Farmacêutico e Suprimentos": ("SAFS", "safs"),
        "Setor de Hotelaria Hospitalar": ("STHH", "sthh"),
        "Divisão de Gestão de Pessoas": ("DIVGP", "divgp"),
        "Divisão de Apoio Diagnóstico e Terapêutico": ("DADT", "dadt"),
        "Setor de Farmácia Hospitalar": ("STFH", "stfh"),
        "Setor de Apoio Diagnóstico e Terapêutico": ("SADT", "sadt"),
        "Divisão de Gestão do Cuidado": ("DGC", "dgc"),
        "Divisão Médica": ("DMED", "dmed"),
        "Setor de Paciente Crítico": ("STPC", "stpc"),
        "Divisão de Enfermagem": ("DENF", "denf"),
        "Setor de Gestão do Ensino": ("SEGE", "sege"),
        "Setor de Gestão da Pesquisa e da Inovação Tecnológica em Saúde": ("SGPITS", "sgpits")
    }

    uorg_objs = {}
    prefix_to_uorg = {}
    for g_sigla, g_info in gerencias_map.items():
        g_elem = mdv.find(f"odm:CodeList[@OID='{g_info['choices_oid']}']", ns)
        if g_elem is not None:
            order = 1
            for cli in g_elem.findall("odm:CodeListItem", ns):
                txt_elem = cli.find("odm:Decode/odm:TranslatedText", ns)
                uorg_name = txt_elem.text.strip() if txt_elem is not None else ""
                if uorg_name in uorg_sigla_map:
                    sigla, prefix = uorg_sigla_map[uorg_name]
                else:
                    sigla = f"{g_sigla}_{order}"
                    prefix = sigla.lower()

                u = session.query(Uorg).filter_by(sigla=sigla).first()
                if not u:
                    u = Uorg(
                        gerencia_id=gerencia_objs[g_sigla].id,
                        sigla=sigla,
                        nome=uorg_name,
                        codigo_redcap=prefix,
                        ordem=order
                    )
                    session.add(u)
                    session.flush()
                uorg_objs[sigla] = u
                prefix_to_uorg[prefix] = u
                order += 1
    print(f"UORGs carregadas: {len(uorg_objs)}")

    # 3. Exercício 2026 e 6 Bimestres
    exercicio_2026 = session.query(Exercicio).filter_by(ano=2026).first()
    if not exercicio_2026:
        exercicio_2026 = Exercicio(
            ano=2026,
            descricao="Exercício de Gestão e Metas Institucionais 2026",
            status="EM_ANDAMENTO",
            data_inicio=datetime(2026, 1, 1),
            data_fim=datetime(2026, 12, 31)
        )
        session.add(exercicio_2026)
        session.flush()

        # Criar os 6 bimestres
        for b_num in range(1, 7):
            b_status = "ABERTO" if b_num == 1 else "FECHADO"
            bim = Bimestre(
                exercicio_id=exercicio_2026.id,
                numero=b_num,
                nome=f"{b_num}º Bimestre",
                status=b_status,
                data_abertura=datetime(2026, 1, 1) if b_num == 1 else None,
                data_fechamento_regular=datetime(2026, 3, 10) if b_num == 1 else None
            )
            session.add(bim)
        session.flush()
    print("Exercício 2026 e Bimestres configurados.")

    # 4. Entregas Planejadas a partir do REDCap
    items = mdv.findall("odm:ItemDef", ns)
    entregas_count = 0
    indicadores_count = 0

    for item in items:
        name = item.get("Name", "")
        ft = item.get("{https://projectredcap.org}FieldType", "")
        q_elem = item.find("odm:Question/odm:TranslatedText", ns)
        lbl = (q_elem.text or "").strip() if q_elem is not None else ""

        # Identificar prefixo da UORG
        parts = name.split("_")
        prefix = parts[0]
        uorg = prefix_to_uorg.get(prefix)

        # Se for entrega descritiva (_entrega_1, _entrega_2, etc.)
        if "_entrega_" in name and not name.endswith("_aux") and ft == "descriptive" and lbl:
            if uorg:
                existing_ent = session.query(EntregaPlanejada).filter_by(
                    exercicio_id=exercicio_2026.id,
                    uorg_id=uorg.id,
                    titulo=lbl
                ).first()
                if not existing_ent:
                    ent = EntregaPlanejada(
                        exercicio_id=exercicio_2026.id,
                        uorg_id=uorg.id,
                        titulo=lbl,
                        ordem=entregas_count + 1
                    )
                    session.add(ent)
                    entregas_count += 1

        # Se for indicador (_ind_)
        elif "_ind_" in name and ft == "text" and lbl:
            if uorg:
                existing_ind = session.query(Indicador).filter_by(
                    exercicio_id=exercicio_2026.id,
                    uorg_id=uorg.id,
                    nome=lbl
                ).first()
                if not existing_ind:
                    # Determinar unidade de medida e operador
                    unidade = "PERCENTUAL" if "Percentual" in lbl or "%" in lbl else "INTEIRO"
                    ind = Indicador(
                        exercicio_id=exercicio_2026.id,
                        uorg_id=uorg.id,
                        nome=lbl,
                        periodicidade="BIMESTRAL",
                        unidade_medida=unidade,
                        meta_operador="MAIOR_IGUAL",
                        meta_valor=100.0 if unidade == "PERCENTUAL" else 1.0,
                        ordem=indicadores_count + 1
                    )
                    session.add(ind)
                    indicadores_count += 1

    # 5. Usuários padrão de teste (Mock Auth)
    usuarios_seed = [
        ("admin", "Administrador do Sistema", "admin@ebserh.gov.br", "ADMINISTRADOR", None, None),
        ("superintendente", "Superintendente do HC-UFPE", "superintendente@ebserh.gov.br", "SUPERINTENDENTE", gerencia_objs["SUP"].id, None),
        ("gerente.gad", "Gerente Administrativo", "gad@ebserh.gov.br", "GERENTE", gerencia_objs["GAD"].id, None),
        ("gerente.gas", "Gerente de Atenção à Saúde", "gas@ebserh.gov.br", "GERENTE", gerencia_objs["GAS"].id, None),
        ("gerente.gep", "Gerente de Ensino e Pesquisa", "gep@ebserh.gov.br", "GERENTE", gerencia_objs["GEP"].id, None),
        ("chefe.setisd", "Chefe do SETISD", "setisd@ebserh.gov.br", "CHEFE_UORG", gerencia_objs["SUP"].id, uorg_objs.get("SETISD").id if "SETISD" in uorg_objs else None),
        ("chefe.stgq", "Chefe da Gestão da Qualidade", "stgq@ebserh.gov.br", "CHEFE_UORG", gerencia_objs["SUP"].id, uorg_objs.get("STGQ").id if "STGQ" in uorg_objs else None)
    ]

    for username, nome, email, perfil, g_id, u_id in usuarios_seed:
        u_user = session.query(UsuarioUorg).filter_by(username=username).first()
        if not u_user:
            u_user = UsuarioUorg(
                username=username,
                nome_completo=nome,
                email=email,
                perfil=perfil,
                gerencia_id=g_id,
                uorg_id=u_id
            )
            session.add(u_user)

    session.commit()
    print(f"Carga finalizada com sucesso!")
    print(f"- Gerências: {len(gerencia_objs)}")
    print(f"- UORGs: {len(uorg_objs)}")
    print(f"- Entregas Planejadas: {entregas_count}")
    print(f"- Indicadores de Gestão: {indicadores_count}")

if __name__ == "__main__":
    run_seed()
