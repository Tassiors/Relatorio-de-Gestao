# src/scripts/seed_from_redcap.py
import sys
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adicionar raiz ao PYTHONPATH
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT_DIR)

from src.resources.database import Base
from src.models import (
    Gerencia, Uorg, UsuarioUorg, Exercicio, Bimestre,
    EntregaPlanejada, Indicador,
    RelatorioBimestral, ItemEntregaRelatorio, ItemIndicadorRelatorio,
    FeedbackRelatorio, PrazoExcepcional
)
from src.helpers.indicador_helper import obter_configuracao_periodicidade
from src.controllers.relatorio_gestao_controller import calcular_atingimento_meta

# Catálogo detalhado de adaptação dos 51 indicadores do REDCap para o modelo padronizado do Portal
REDCAP_INDICADORES_CONFIG = {
    # SUPERINTENDÊNCIA (SUP)
    "stgq_perc_pain_at": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 90.0,
        "meta_valor_max": None,
        "valores_b1": [92.5],
        "valores_b2": [95.0],
    },
    "stgq_perc_prof_cap": {
        "periodicidade": "TRIMESTRAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 80.0,
        "meta_valor_max": None,
        "valores_b1": [None],
        "valores_b2": [84.0],
    },
    "stgq_perc_doc_inst_at": {
        "periodicidade": "MENSAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 85.0,
        "meta_valor_max": None,
        "valores_b1": [82.0, 86.5],
        "valores_b2": [88.0, 91.0],
    },
    "segov_ind_gover": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 54.0,
        "meta_valor_max": None,
        "valores_b1": [51.2],
        "valores_b2": [56.8],
    },
    "setisd_ind_finep": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 30.0,
        "meta_valor_max": None,
        "valores_b1": [18.5],
        "valores_b2": [32.0],
    },
    "setisd_ind_sist_impl": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "Unidades",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 5.0,
        "meta_valor_max": None,
        "valores_b1": [3.0],
        "valores_b2": [5.0],
    },
    "setisd_ind_num_acor_fin": {
        "periodicidade": "QUADRIMESTRAL",
        "unidade_medida": "Unidades",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 4.0,
        "meta_valor_max": None,
        "valores_b1": [None],
        "valores_b2": [4.0],
    },
    "stcor_ind_cons_cm": {
        "periodicidade": "MENSAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 100.0,
        "meta_valor_max": None,
        "valores_b1": [96.0, 98.5],
        "valores_b2": [100.0, 100.0],
    },
    "stcor_ind_imp_sis": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 100.0,
        "meta_valor_max": None,
        "valores_b1": [75.0],
        "valores_b2": [100.0],
    },
    "stcor_ind_esp_cig": {
        "periodicidade": "SEMESTRAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 100.0,
        "meta_valor_max": None,
        "valores_b1": [None],
        "valores_b2": [None],
    },

    # GERÊNCIA DE ENSINO E PESQUISA (GEP)
    "sgpits_num_proj_cap": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "Processos",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 10.0,
        "meta_valor_max": None,
        "valores_b1": [8.0],
        "valores_b2": [11.0],
    },
    "sgpits_tx_conv_proj": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 50.0,
        "meta_valor_max": None,
        "valores_b1": [48.0],
        "valores_b2": [54.5],
    },
    "sgpits_nov_acord": {
        "periodicidade": "SEMESTRAL",
        "unidade_medida": "Unidades",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 2.0,
        "meta_valor_max": None,
        "valores_b1": [None],
        "valores_b2": [None],
    },
    "sege_prec_cap": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 29.0,
        "meta_valor_max": None,
        "valores_b1": [24.5],
        "valores_b2": [31.0],
    },
    "sege_ade_enare": {
        "periodicidade": "SEMESTRAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 100.0,
        "meta_valor_max": None,
        "valores_b1": [None],
        "valores_b2": [None],
    },
    "sege_cur_ofer": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "Unidades",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 5.0,
        "meta_valor_max": None,
        "valores_b1": [3.0],
        "valores_b2": [5.0],
    },

    # GERÊNCIA ADMINISTRATIVA (GAD)
    "scont_perc_lot_rev": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 70.0,
        "meta_valor_max": None,
        "valores_b1": [65.0],
        "valores_b2": [78.0],
    },
    "divgp_perc_dei": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 100.0,
        "meta_valor_max": None,
        "valores_b1": [80.0],
        "valores_b2": [100.0],
    },
    "divgp_part_pesq": {
        "periodicidade": "SEMESTRAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 50.0,
        "meta_valor_max": None,
        "valores_b1": [None],
        "valores_b2": [None],
    },
    "divgp_tmp_resp_dem": {
        "periodicidade": "MENSAL",
        "unidade_medida": "Dias",
        "meta_operador": "MENOR_IGUAL",
        "meta_valor": 7.0,
        "meta_valor_max": None,
        "valores_b1": [6.5, 5.8],
        "valores_b2": [5.2, 4.9],
    },
    "sthh_ind_seg_res": {
        "periodicidade": "MENSAL",
        "unidade_medida": "Índice",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 0.8,
        "meta_valor_max": None,
        "valores_b1": [0.78, 0.82],
        "valores_b2": [0.85, 0.87],
    },
    "sthh_ind_ref_n_cons": {
        "periodicidade": "MENSAL",
        "unidade_medida": "Índice",
        "meta_operador": "MENOR_IGUAL",
        "meta_valor": 0.005,
        "meta_valor_max": None,
        "valores_b1": [0.006, 0.004],
        "valores_b2": [0.004, 0.003],
    },
    "sthh_ind_ev_roup": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "Índice",
        "meta_operador": "MENOR_IGUAL",
        "meta_valor": 0.10,
        "meta_valor_max": None,
        "valores_b1": [0.09],
        "valores_b2": [0.07],
    },
    "stec_perc_man_cor_2": {
        "periodicidade": "MENSAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 92.0,
        "meta_valor_max": None,
        "valores_b1": [91.0, 93.5],
        "valores_b2": [94.0, 95.2],
    },
    "stec_perc_plan_man": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 90.0,
        "meta_valor_max": None,
        "valores_b1": [92.0],
        "valores_b2": [94.5],
    },
    "stec_perc_plan_trein": {
        "periodicidade": "TRIMESTRAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 100.0,
        "meta_valor_max": None,
        "valores_b1": [None],
        "valores_b2": [100.0],
    },
    "sgof_liq_cust_op": {
        "periodicidade": "TRIMESTRAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 40.0,
        "meta_valor_max": None,
        "valores_b1": [None],
        "valores_b2": [43.5],
    },
    "sgof_acu_val_exe": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "%",
        "meta_operador": "ENTRE",
        "meta_valor": 90.0,
        "meta_valor_max": 110.0,
        "valores_b1": [96.4],
        "valores_b2": [98.2],
    },
    "daf_red_praz_lic": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "Dias",
        "meta_operador": "MENOR_IGUAL",
        "meta_valor": 172.0,
        "meta_valor_max": None,
        "valores_b1": [168.0],
        "valores_b2": [159.0],
    },
    "daf_ren_contr": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 100.0,
        "meta_valor_max": None,
        "valores_b1": [100.0],
        "valores_b2": [100.0],
    },
    "daf_orc_equip_med": {
        "periodicidade": "TRIMESTRAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 35.0,
        "meta_valor_max": None,
        "valores_b1": [None],
        "valores_b2": [38.5],
    },
    "safs_cobert_esto_med": {
        "periodicidade": "MENSAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 100.0,
        "meta_valor_max": None,
        "valores_b1": [97.0, 99.0],
        "valores_b2": [100.0, 100.0],
    },
    "safs_ind_perd_venc": {
        "periodicidade": "MENSAL",
        "unidade_medida": "%",
        "meta_operador": "MENOR_IGUAL",
        "meta_valor": 0.3,
        "meta_valor_max": None,
        "valores_b1": [0.25, 0.22],
        "valores_b2": [0.19, 0.18],
    },
    "sad_perc_med_pesq": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "%",
        "meta_operador": "MENOR_IGUAL",
        "meta_valor": 5.0,
        "meta_valor_max": None,
        "valores_b1": [4.2],
        "valores_b2": [3.8],
    },

    # GERÊNCIA DE ATENÇÃO À SAÚDE (GAS)
    "dmed_transp_corn": {
        "periodicidade": "MENSAL",
        "unidade_medida": "Cirurgias",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 3.0,
        "meta_valor_max": None,
        "valores_b1": [3.0, 4.0],
        "valores_b2": [4.0, 5.0],
    },
    "dmed_pct_psiq": {
        "periodicidade": "MENSAL",
        "unidade_medida": "Pacientes",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 15.0,
        "meta_valor_max": None,
        "valores_b1": [14.0, 16.0],
        "valores_b2": [17.0, 18.0],
    },
    "dmed_pct_indig": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "Pacientes",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 20.0,
        "meta_valor_max": None,
        "valores_b1": [19.0],
        "valores_b2": [24.0],
    },
    "stpc_cir_real": {
        "periodicidade": "MENSAL",
        "unidade_medida": "Cirurgias",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 3.0,
        "meta_valor_max": None,
        "valores_b1": [3.0, 3.0],
        "valores_b2": [4.0, 4.0],
    },
    "stpc_cons_pac_indig": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "Atendimentos",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 40.0,
        "meta_valor_max": None,
        "valores_b1": [38.0],
        "valores_b2": [45.0],
    },
    "denf_perc_imp_dash": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 50.0,
        "meta_valor_max": None,
        "valores_b1": [45.0],
        "valores_b2": [60.0],
    },
    "denf_cons_enf": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 70.0,
        "meta_valor_max": None,
        "valores_b1": [72.0],
        "valores_b2": [76.5],
    },
    "denf_partos_enf": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "Procedimentos",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 50.0,
        "meta_valor_max": None,
        "valores_b1": [48.0],
        "valores_b2": [55.0],
    },
    "stfh_cons_farm": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "Atendimentos",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 720.0,
        "meta_valor_max": None,
        "valores_b1": [710.0],
        "valores_b2": [745.0],
    },
    "stfh_pac_farm_clin": {
        "periodicidade": "MENSAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 10.0,
        "meta_valor_max": None,
        "valores_b1": [9.8, 10.4],
        "valores_b2": [11.2, 11.8],
    },
    "stfh_vid_impact": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "Pacientes",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 290.0,
        "meta_valor_max": None,
        "valores_b1": [285.0],
        "valores_b2": [312.0],
    },
    "dgc_tx_ocup": {
        "periodicidade": "MENSAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 85.0,
        "meta_valor_max": None,
        "valores_b1": [84.2, 86.1],
        "valores_b2": [87.0, 88.4],
    },
    "dgc_proc_amb": {
        "periodicidade": "BIMESTRAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 5.0,
        "meta_valor_max": None,
        "valores_b1": [4.8],
        "valores_b2": [6.2],
    },
    "sadt_perc_exam_tomo": {
        "periodicidade": "MENSAL",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 100.0,
        "meta_valor_max": None,
        "valores_b1": [95.0, 98.0],
        "valores_b2": [100.0, 100.0],
    },
    "sadt_rx_contr": {
        "periodicidade": "MENSAL",
        "unidade_medida": "Exames",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 40.0,
        "meta_valor_max": None,
        "valores_b1": [36.0, 42.0],
        "valores_b2": [45.0, 48.0],
    },
    "sadt_mut_cir": {
        "periodicidade": "MENSAL",
        "unidade_medida": "Unidades",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 1.0,
        "meta_valor_max": None,
        "valores_b1": [1.0, 1.0],
        "valores_b2": [1.0, 2.0],
    },
    "dadt_tx_cir_susp": {
        "periodicidade": "MENSAL",
        "unidade_medida": "%",
        "meta_operador": "MENOR_IGUAL",
        "meta_valor": 10.0,
        "meta_valor_max": None,
        "valores_b1": [10.5, 9.4],
        "valores_b2": [8.8, 8.2],
    },
}

# Entregas e Indicadores adaptados para DLI e STIF (que no REDCap utilizavam os campos abertos entrega_1..4 e ind_1..3)
COMPLEMENTO_UORGS_ABERTAS = {
    "DLI": {
        "entregas": [
            "Plano Diretor de Logística e Infraestrutura Hospitalar 2026 consolidado junto aos setores subordinados",
            "Implantação do painel integrado de acompanhamento de contratos de manutenção, hotelaria e suprimentos",
            "Revisão e padronização dos fluxos logísticos críticos de abastecimento e apoio operacional",
            "Monitoramento da execução física das obras e intervenções estruturais prioritárias do HC-UFPE"
        ],
        "indicadores": [
            {
                "codigo": "dli_ind_1",
                "nome": "Percentual de cumprimento das metas operacionais dos setores vinculados à DLI",
                "descricao": "Variável REDCap: [ind_1 / uorg_gad=5] | Monitoramento consolidado DLI",
                "periodicidade": "BIMESTRAL",
                "unidade_medida": "%",
                "meta_operador": "MAIOR_IGUAL",
                "meta_valor": 85.0,
                "meta_valor_max": None,
                "valores_b1": [83.0],
                "valores_b2": [88.5],
            },
            {
                "codigo": "dli_ind_2",
                "nome": "Índice de atendimento tempestivo às demandas críticas de infraestrutura e logística",
                "descricao": "Variável REDCap: [ind_2 / uorg_gad=5] | Meta pactuada DLI 2026",
                "periodicidade": "MENSAL",
                "unidade_medida": "%",
                "meta_operador": "MAIOR_IGUAL",
                "meta_valor": 90.0,
                "meta_valor_max": None,
                "valores_b1": [88.0, 91.0],
                "valores_b2": [92.5, 94.0],
            }
        ]
    },
    "STIF": {
        "entregas": [
            "Execução do Plano Anual de Manutenção Predial Preventiva e Corretiva nas áreas assistenciais",
            "Adequação das instalações elétricas e climatização das unidades críticas e centro cirúrgico",
            "Atualização dos projetos executivos e laudos técnicos de infraestrutura física hospitalar",
            "Redução do tempo médio de atendimento de ordens de serviço de manutenção predial"
        ],
        "indicadores": [
            {
                "codigo": "stif_ind_1",
                "nome": "Percentual de ordens de serviço de manutenção predial concluídas no prazo",
                "descricao": "Variável REDCap: [ind_1 / uorg_gad=7] | Meta operacional STIF 2026",
                "periodicidade": "MENSAL",
                "unidade_medida": "%",
                "meta_operador": "MAIOR_IGUAL",
                "meta_valor": 85.0,
                "meta_valor_max": None,
                "valores_b1": [84.0, 87.5],
                "valores_b2": [89.0, 91.2],
            },
            {
                "codigo": "stif_ind_2",
                "nome": "Percentual de execução do cronograma de manutenção preventiva predial",
                "descricao": "Variável REDCap: [ind_2 / uorg_gad=7] | Plano Anual de Manutenção Predial",
                "periodicidade": "BIMESTRAL",
                "unidade_medida": "%",
                "meta_operador": "MAIOR_IGUAL",
                "meta_valor": 90.0,
                "meta_valor_max": None,
                "valores_b1": [90.0],
                "valores_b2": [93.0],
            }
        ]
    }
}


def run_seed(target_db_path: str = None):
    db_path = target_db_path or os.path.join(ROOT_DIR, "data", "app.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
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

    print("=== Iniciando Adaptação e Carga Completa dos Dados do REDCap ===")

    # Limpar dados anteriores de relatórios/entregas/indicadores para garantir base limpa e fiel ao REDCap
    session.query(FeedbackRelatorio).delete()
    session.query(ItemIndicadorRelatorio).delete()
    session.query(ItemEntregaRelatorio).delete()
    session.query(RelatorioBimestral).delete()
    session.query(PrazoExcepcional).delete()
    session.query(Indicador).delete()
    session.query(EntregaPlanejada).delete()
    session.flush()

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
        "Divisão de Gestão de Pessoas": ("DivGP", "divgp"),
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

                u = session.query(Uorg).filter(Uorg.codigo_redcap == prefix).first()
                if not u:
                    u = session.query(Uorg).filter(Uorg.sigla == sigla.upper()).first()
                if not u:
                    u = Uorg(
                        gerencia_id=gerencia_objs[g_sigla].id,
                        sigla=sigla.upper(),
                        nome=uorg_name,
                        codigo_redcap=prefix,
                        ordem=order
                    )
                    session.add(u)
                    session.flush()
                else:
                    u.nome = uorg_name
                    u.codigo_redcap = prefix
                    u.gerencia_id = gerencia_objs[g_sigla].id
                    u.ordem = order
                uorg_objs[u.sigla] = u
                prefix_to_uorg[prefix] = u
                order += 1

    # 3. Exercício 2026 e 6 Bimestres
    exercicio_2026 = session.query(Exercicio).filter_by(ano=2026).first()
    if not exercicio_2026:
        exercicio_2026 = Exercicio(
            ano=2026,
            descricao="Exercício de Gestão e Metas Institucionais 2026 (REDCap HC-UFPE)",
            status="PLANEJAMENTO",
            data_inicio=datetime(2026, 1, 1),
            data_fim=datetime(2026, 12, 31)
        )
        session.add(exercicio_2026)
        session.flush()
    else:
        exercicio_2026.status = "PLANEJAMENTO"
        exercicio_2026.descricao = "Exercício de Gestão e Metas Institucionais 2026 (REDCap HC-UFPE)"

    datas_bimestres = {
        1: (datetime(2026, 1, 1), datetime(2026, 3, 15), "ABERTO"),
        2: (datetime(2026, 3, 1), datetime(2026, 5, 15), "ABERTO"),
        3: (datetime(2026, 5, 1), datetime(2026, 7, 15), "FECHADO"),
        4: (datetime(2026, 7, 1), datetime(2026, 9, 15), "FECHADO"),
        5: (datetime(2026, 9, 1), datetime(2026, 11, 15), "FECHADO"),
        6: (datetime(2026, 11, 1), datetime(2027, 1, 15), "FECHADO"),
    }

    bimestres_map = {}
    for b_num in range(1, 7):
        dt_ab, dt_fech, b_st = datas_bimestres[b_num]
        bim = session.query(Bimestre).filter_by(exercicio_id=exercicio_2026.id, numero=b_num).first()
        if not bim:
            bim = Bimestre(
                exercicio_id=exercicio_2026.id,
                numero=b_num,
                nome=f"{b_num}º Bimestre",
                status=b_st,
                data_abertura=dt_ab,
                data_fechamento_regular=dt_fech
            )
            session.add(bim)
            session.flush()
        else:
            bim.nome = f"{b_num}º Bimestre"
            bim.status = b_st
            bim.data_abertura = dt_ab
            bim.data_fechamento_regular = dt_fech
        bimestres_map[b_num] = bim
    session.flush()

    # 4. Extrair TODAS as Entregas e Indicadores do REDCap XML
    items = mdv.findall("odm:ItemDef", ns)
    entregas_por_uorg = {u.id: [] for u in uorg_objs.values()}
    indicadores_por_uorg = {u.id: [] for u in uorg_objs.values()}
    ind_config_by_id = {}

    started_indicadores = False
    entregas_total = 0
    indicadores_total = 0

    for item in items:
        name = item.get("Name", "")
        ft = item.get("{https://projectredcap.org}FieldType", "")
        fn = (item.get("{https://projectredcap.org}FieldNote", "") or "").strip()
        q_elem = item.find("odm:Question/odm:TranslatedText", ns)
        lbl = (q_elem.text or "").strip().replace("\u200b", "").replace("\xa0", " ") if q_elem is not None else ""
        # Limpar quebras de linha múltiplas
        lbl = " ".join(lbl.split())

        if name == "lbl_indicadores":
            started_indicadores = True
            continue
        if name == "destaques":
            started_indicadores = False

        parts = name.split("_")
        prefix = parts[0]
        uorg = prefix_to_uorg.get(prefix)

        # 4.1. Entregas Planejadas do REDCap (<prefix>_entrega_1..4)
        if "_entrega_" in name and not name.endswith("_aux") and "altera" not in name and ft == "descriptive" and lbl and uorg:
            ordem_ent = len(entregas_por_uorg[uorg.id]) + 1
            ent = EntregaPlanejada(
                exercicio_id=exercicio_2026.id,
                uorg_id=uorg.id,
                titulo=lbl,
                descricao=f"Entrega institucional pactuada no REDCap 2026 (Variável: {name}) — {uorg.sigla}",
                ordem=ordem_ent,
                concluida=False,
                ativo=True
            )
            session.add(ent)
            session.flush()
            entregas_por_uorg[uorg.id].append(ent)
            entregas_total += 1

        # 4.2. Indicadores de Gestão do REDCap (Todos os campos de indicadores na seção lbl_indicadores)
        elif started_indicadores and ft == "text" and not name.startswith("ind_") and not name.startswith("meta_ind_") and lbl and uorg:
            cfg = REDCAP_INDICADORES_CONFIG.get(name, {
                "periodicidade": "BIMESTRAL",
                "unidade_medida": "%" if ("Percentual" in lbl or "Taxa" in lbl or "%" in fn) else "Unidades",
                "meta_operador": "MAIOR_IGUAL",
                "meta_valor": 100.0 if ("Percentual" in lbl or "%" in fn) else 10.0,
                "meta_valor_max": None,
                "valores_b1": [90.0],
                "valores_b2": [95.0],
            })
            ordem_ind = len(indicadores_por_uorg[uorg.id]) + 1
            nota_original = fn if fn else "META definida no plano setorial 2026"
            ind = Indicador(
                exercicio_id=exercicio_2026.id,
                uorg_id=uorg.id,
                nome=lbl,
                descricao=f"Origem REDCap [{name}] — {nota_original}",
                periodicidade=cfg["periodicidade"],
                unidade_medida=cfg["unidade_medida"],
                meta_operador=cfg["meta_operador"],
                meta_valor=cfg["meta_valor"],
                meta_valor_max=cfg["meta_valor_max"],
                ordem=ordem_ind,
                ativo=True
            )
            session.add(ind)
            session.flush()
            indicadores_por_uorg[uorg.id].append(ind)
            ind_config_by_id[ind.id] = cfg
            indicadores_total += 1

    # 4.3. Complementar DLI e STIF (que estavam com campos abertos no REDCap)
    for sigla_comp, dados_comp in COMPLEMENTO_UORGS_ABERTAS.items():
        uorg = uorg_objs.get(sigla_comp)
        if not uorg:
            continue
        for idx_e, titulo_ent in enumerate(dados_comp["entregas"], start=1):
            ent = EntregaPlanejada(
                exercicio_id=exercicio_2026.id,
                uorg_id=uorg.id,
                titulo=titulo_ent,
                descricao=f"Entrega institucional adaptada para {uorg.sigla} no Exercício 2026",
                ordem=idx_e,
                concluida=False,
                ativo=True
            )
            session.add(ent)
            session.flush()
            entregas_por_uorg[uorg.id].append(ent)
            entregas_total += 1

        for idx_i, cfg_i in enumerate(dados_comp["indicadores"], start=1):
            ind = Indicador(
                exercicio_id=exercicio_2026.id,
                uorg_id=uorg.id,
                nome=cfg_i["nome"],
                descricao=cfg_i["descricao"],
                periodicidade=cfg_i["periodicidade"],
                unidade_medida=cfg_i["unidade_medida"],
                meta_operador=cfg_i["meta_operador"],
                meta_valor=cfg_i["meta_valor"],
                meta_valor_max=cfg_i["meta_valor_max"],
                ordem=idx_i,
                ativo=True
            )
            session.add(ind)
            session.flush()
            indicadores_por_uorg[uorg.id].append(ind)
            ind_config_by_id[ind.id] = cfg_i
            indicadores_total += 1

    # 5. Popular Relatórios Bimestrais (1º e 2º Bimestres) para todas as 23 UORGs
    # Isso permite interagir imediatamente com Preenchimento Bimestral, Efeito Cascata, Periodicidades,
    # Matriz de Acompanhamento, Visão Consolidada e Gráficos do Dashboard!
    b1 = bimestres_map[1]
    b2 = bimestres_map[2]

    relatorios_criados = 0
    for idx_u, uorg in enumerate(sorted(uorg_objs.values(), key=lambda x: x.id)):
        ents_uorg = entregas_por_uorg.get(uorg.id, [])
        inds_uorg = indicadores_por_uorg.get(uorg.id, [])

        # Definir status variado para demonstrar todos os estados na Matriz e Dashboard
        if idx_u % 5 == 4:
            status_b1 = "EM_EDICAO"
        elif idx_u == 7:
            status_b1 = "PRAZO_EXCEPCIONAL"
        else:
            status_b1 = "ENVIADO"

        # --- RELATÓRIO DO 1º BIMESTRE ---
        rel_b1 = RelatorioBimestral(
            exercicio_id=exercicio_2026.id,
            bimestre_id=b1.id,
            uorg_id=uorg.id,
            status=status_b1,
            versao=1,
            data_envio=datetime(2026, 3, 8, 14, 30) if status_b1 == "ENVIADO" else None,
            usuario_envio=f"chefe.{uorg.codigo_redcap}" if status_b1 == "ENVIADO" else None,
            destaques=(
                f"• Avanço expressivo nas entregas pactuadas pela unidade {uorg.sigla} no 1º Bimestre de 2026.\n"
                f"• Conclusão da primeira entrega prioritária ('{ents_uorg[0].titulo[:80]}...') com engajamento da equipe multiprofissional.\n"
                f"• Monitoramento sistemático dos indicadores do REDCap com alinhamento às metas institucionais do PDE/AOC."
            ) if ents_uorg else f"• Consolidação das rotinas operacionais da {uorg.sigla} no 1º Bimestre.",
            dificuldades=(
                f"• Necessidade de ajustes pontuais em fluxos intersetoriais e integração de sistemas de apoio para acelerar as demais entregas da {uorg.sigla}.\n"
                f"• Acompanhamento de processos administrativos e disponibilidade de agendas técnicas para treinamentos."
            )
        )
        session.add(rel_b1)
        session.flush()
        relatorios_criados += 1

        # Entregas no 1º Bimestre: concluir a 1ª entrega (e a 2ª para algumas UORGs)
        for idx_ent, ent in enumerate(ents_uorg):
            concluida_b1 = (idx_ent == 0) or (idx_ent == 1 and idx_u % 3 == 0)
            if concluida_b1:
                ent.concluida = True
                ent.bimestre_conclusao_id = b1.id
                ent.data_conclusao = datetime(2026, 2, 25, 16, 0)
                ent.usuario_conclusao = f"chefe.{uorg.codigo_redcap}"
                obs = "Entrega concluída integralmente no 1º Bimestre, validada pela chefia e documentada no SEI."
            else:
                obs = "Cronograma em execução dentro do prazo previsto para os próximos bimestres de 2026."

            session.add(ItemEntregaRelatorio(
                relatorio_id=rel_b1.id,
                entrega_id=ent.id,
                concluida=concluida_b1,
                observacoes=obs
            ))

        # Indicadores no 1º Bimestre (respeitando a configuração de periodicidade)
        for ind in inds_uorg:
            cfg_per_b1 = obter_configuracao_periodicidade(ind.periodicidade, 1)
            cfg_seed = ind_config_by_id.get(ind.id, {})
            valores_b1 = cfg_seed.get("valores_b1", [ind.meta_valor])

            for idx_c, comp in enumerate(cfg_per_b1["competencias"]):
                if not cfg_per_b1["aplicavel"]:
                    session.add(ItemIndicadorRelatorio(
                        relatorio_id=rel_b1.id,
                        indicador_id=ind.id,
                        competencia=comp,
                        valor_apurado=None,
                        meta_atingida=None,
                        resultado_indisponivel=False,
                        justificativa_indisponibilidade=None,
                        nao_aplicavel=True
                    ))
                else:
                    val = valores_b1[idx_c] if idx_c < len(valores_b1) else valores_b1[-1]
                    atingida = calcular_atingimento_meta(ind.meta_operador, ind.meta_valor, ind.meta_valor_max, val)
                    session.add(ItemIndicadorRelatorio(
                        relatorio_id=rel_b1.id,
                        indicador_id=ind.id,
                        competencia=comp,
                        valor_apurado=val,
                        meta_atingida=atingida,
                        resultado_indisponivel=False,
                        justificativa_indisponibilidade=None,
                        nao_aplicavel=False
                    ))

        # Adicionar Feedback da Superintendência/Gerência nos relatórios enviados do 1º Bimestre
        if status_b1 == "ENVIADO" and idx_u % 2 == 0:
            session.add(FeedbackRelatorio(
                relatorio_id=rel_b1.id,
                autor_username="superintendente",
                autor_perfil="SUPERINTENDENTE",
                autor_nome="Superintendente do HC-UFPE",
                texto_feedback=(
                    f"Parabéns à equipe da {uorg.sigla} pelos resultados apresentados no 1º Bimestre. "
                    f"Destaca-se a conclusão tempestiva das entregas prioritárias e a aderência aos indicadores pactuados no REDCap."
                )
            ))

        # --- RELATÓRIO DO 2º BIMESTRE (Demonstra Efeito Cascata + Indicadores Trimestrais/Quadrimestrais) ---
        status_b2 = "ENVIADO" if idx_u < 6 else "EM_EDICAO"
        rel_b2 = RelatorioBimestral(
            exercicio_id=exercicio_2026.id,
            bimestre_id=b2.id,
            uorg_id=uorg.id,
            status=status_b2,
            versao=1,
            data_envio=datetime(2026, 5, 5, 11, 15) if status_b2 == "ENVIADO" else None,
            usuario_envio=f"chefe.{uorg.codigo_redcap}" if status_b2 == "ENVIADO" else None,
            destaques=(
                f"• Continuidade da execução do plano de gestão 2026 da {uorg.sigla} no 2º Bimestre.\n"
                f"• Consolidação dos resultados trimestrais/bimestrais com superação das metas pactuadas.\n"
                f"• Nova entrega estruturante concluída neste ciclo bimestral."
            ),
            dificuldades=(
                f"• Acompanhamento de demandas sazonais do 2º Bimestre e alinhamento contínuo com as áreas de suporte."
            )
        )
        session.add(rel_b2)
        session.flush()
        relatorios_criados += 1

        for idx_ent, ent in enumerate(ents_uorg):
            # Se já foi concluída no B1, propaga em cascata; além disso, conclui mais uma entrega no B2 para metade das UORGs
            ja_concluida_b1 = (ent.concluida and ent.bimestre_conclusao_id == b1.id)
            concluir_no_b2 = (not ja_concluida_b1) and (idx_ent == 1 or (idx_ent == 2 and idx_u % 2 == 0))

            if concluir_no_b2:
                ent.concluida = True
                ent.bimestre_conclusao_id = b2.id
                ent.data_conclusao = datetime(2026, 4, 28, 17, 0)
                ent.usuario_conclusao = f"chefe.{uorg.codigo_redcap}"
                obs_b2 = "Concluída no 2º Bimestre após validação dos fluxos operacionais junto à equipe."
            elif ja_concluida_b1:
                obs_b2 = "Entrega concluída no 1º Bimestre (propagada automaticamente por efeito cascata)."
            else:
                obs_b2 = "Em execução conforme planejamento anual da unidade."

            session.add(ItemEntregaRelatorio(
                relatorio_id=rel_b2.id,
                entrega_id=ent.id,
                concluida=(ja_concluida_b1 or concluir_no_b2),
                observacoes=obs_b2
            ))

        for ind in inds_uorg:
            cfg_per_b2 = obter_configuracao_periodicidade(ind.periodicidade, 2)
            cfg_seed = ind_config_by_id.get(ind.id, {})
            valores_b2 = cfg_seed.get("valores_b2", [ind.meta_valor])

            for idx_c, comp in enumerate(cfg_per_b2["competencias"]):
                if not cfg_per_b2["aplicavel"]:
                    session.add(ItemIndicadorRelatorio(
                        relatorio_id=rel_b2.id,
                        indicador_id=ind.id,
                        competencia=comp,
                        valor_apurado=None,
                        meta_atingida=None,
                        resultado_indisponivel=False,
                        justificativa_indisponibilidade=None,
                        nao_aplicavel=True
                    ))
                else:
                    val = valores_b2[idx_c] if idx_c < len(valores_b2) else valores_b2[-1]
                    atingida = calcular_atingimento_meta(ind.meta_operador, ind.meta_valor, ind.meta_valor_max, val)
                    session.add(ItemIndicadorRelatorio(
                        relatorio_id=rel_b2.id,
                        indicador_id=ind.id,
                        competencia=comp,
                        valor_apurado=val,
                        meta_atingida=atingida,
                        resultado_indisponivel=False,
                        justificativa_indisponibilidade=None,
                        nao_aplicavel=False
                    ))

    # 6. Cadastrar Prazo Excepcional de exemplo para SCONT no 1º Bimestre
    scont_uorg = uorg_objs.get("SCONT")
    if scont_uorg:
        session.add(PrazoExcepcional(
            exercicio_id=exercicio_2026.id,
            bimestre_id=b1.id,
            uorg_id=scont_uorg.id,
            motivo="Aguardando consolidação final dos relatórios contábeis do SIAFI/ApuraSUS.",
            data_inicio=datetime.utcnow(),
            data_fim=datetime.utcnow() + timedelta(days=15),
            concedido_por_username="admin",
            ativo=True
        ))

    # 7. Usuários padrão de teste (Mock Auth) para todas as UORGs e Perfis
    usuarios_seed = [
        ("admin", "Administrador do Sistema", "admin@ebserh.gov.br", "ADMINISTRADOR", None, None),
        ("superintendente", "Superintendente do HC-UFPE", "superintendente@ebserh.gov.br", "SUPERINTENDENTE", gerencia_objs["SUP"].id, None),
        ("gerente.gad", "Gerente Administrativo", "gad@ebserh.gov.br", "GERENTE", gerencia_objs["GAD"].id, None),
        ("gerente.gas", "Gerente de Atenção à Saúde", "gas@ebserh.gov.br", "GERENTE", gerencia_objs["GAS"].id, None),
        ("gerente.gep", "Gerente de Ensino e Pesquisa", "gep@ebserh.gov.br", "GERENTE", gerencia_objs["GEP"].id, None),
    ]
    for u in uorg_objs.values():
        usuarios_seed.append((
            f"chefe.{u.codigo_redcap}",
            f"Chefe — {u.sigla} ({u.nome})",
            f"{u.codigo_redcap}@ebserh.gov.br",
            "CHEFE_UORG",
            u.gerencia_id,
            u.id
        ))

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
        else:
            u_user.nome_completo = nome
            u_user.email = email
            u_user.perfil = perfil
            u_user.gerencia_id = g_id
            u_user.uorg_id = u_id

    session.commit()
    print("Carga e adaptação do REDCap finalizada com sucesso!")
    print(f"- Gerências: {len(gerencia_objs)}")
    print(f"- UORGs: {len(uorg_objs)}")
    print(f"- Entregas Planejadas carregadas: {entregas_total}")
    print(f"- Indicadores de Gestão adaptados: {indicadores_total}")
    print(f"- Relatórios Bimestrais pré-populados (1º e 2º BI): {relatorios_criados}")


if __name__ == "__main__":
    run_seed()
