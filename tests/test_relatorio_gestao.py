# tests/test_relatorio_gestao.py
import pytest
from src.controllers.relatorio_gestao_controller import calcular_atingimento_meta
from src.helpers.indicador_helper import obter_configuracao_periodicidade, validar_itens_indicador_bimestre

@pytest.fixture
def auth_headers(client):
    """Obtém token JWT de autenticação mock para testes."""
    response = client.post(
        "/api/login",
        data={"username": "admin", "password": "admin"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_calcular_atingimento_meta_maior_igual():
    assert calcular_atingimento_meta("MAIOR_IGUAL", 80.0, None, 85.0) is True
    assert calcular_atingimento_meta("MAIOR_IGUAL", 80.0, None, 80.0) is True
    assert calcular_atingimento_meta("MAIOR_IGUAL", 80.0, None, 75.0) is False

def test_calcular_atingimento_meta_menor_igual():
    assert calcular_atingimento_meta("MENOR_IGUAL", 5.0, None, 4.0) is True
    assert calcular_atingimento_meta("MENOR_IGUAL", 5.0, None, 5.0) is True
    assert calcular_atingimento_meta("MENOR_IGUAL", 5.0, None, 6.0) is False

def test_calcular_atingimento_meta_igual():
    assert calcular_atingimento_meta("IGUAL", 10.0, None, 10.0) is True
    assert calcular_atingimento_meta("IGUAL", 10.0, None, 9.9) is False

def test_calcular_atingimento_meta_entre_faixa():
    # Validação do operador de faixa validado pelo usuário
    assert calcular_atingimento_meta("ENTRE", 80.0, 90.0, 85.0) is True
    assert calcular_atingimento_meta("ENTRE", 80.0, 90.0, 80.0) is True
    assert calcular_atingimento_meta("ENTRE", 80.0, 90.0, 90.0) is True
    assert calcular_atingimento_meta("ENTRE", 80.0, 90.0, 79.9) is False
    assert calcular_atingimento_meta("ENTRE", 80.0, 90.0, 90.1) is False

def test_obter_estrutura_organizacional(client, auth_headers):
    response = client.get("/api/gestao/estrutura", headers=auth_headers)
    assert response.status_code == 200
    gerencias = response.json()
    assert len(gerencias) == 4
    total_uorgs = sum(len(g["uorgs"]) for g in gerencias)
    assert total_uorgs == 23

def test_obter_exercicio_ativo(client, auth_headers):
    response = client.get("/api/gestao/exercicios/ativo", headers=auth_headers)
    assert response.status_code == 200
    ex = response.json()
    assert ex["ano"] == 2026
    assert len(ex["bimestres"]) == 6
    assert ex["bimestres"][0]["status"] == "ABERTO"

def test_obter_matriz_acompanhamento(client, auth_headers):
    response = client.get("/api/gestao/matriz", headers=auth_headers)
    assert response.status_code == 200
    matriz = response.json()
    assert "linhas" in matriz
    assert len(matriz["linhas"]) == 23
    assert len(matriz["bimestres"]) == 6

def test_salvar_rascunho_e_buscar_relatorio(client, auth_headers):
    # Buscar exercício e UORG
    ex_res = client.get("/api/gestao/exercicios/ativo", headers=auth_headers)
    ex = ex_res.json()
    b1_id = ex["bimestres"][0]["id"]

    est_res = client.get("/api/gestao/estrutura", headers=auth_headers)
    uorg_id = est_res.json()[0]["uorgs"][0]["id"]

    # Obter inicial
    get_res = client.get(
        f"/api/gestao/relatorios?exercicio_id={ex['id']}&bimestre_id={b1_id}&uorg_id={uorg_id}",
        headers=auth_headers
    )
    assert get_res.status_code == 200
    rel_inicial = get_res.json()

    # Salvar rascunho
    payload = {
        "exercicio_id": ex["id"],
        "bimestre_id": b1_id,
        "uorg_id": uorg_id,
        "destaques": "Destaque de teste automatizado",
        "dificuldades": "Dificuldade de teste automatizado",
        "itens_entrega": [],
        "itens_indicador": []
    }
    post_res = client.post("/api/gestao/relatorios/rascunho", json=payload, headers=auth_headers)
    assert post_res.status_code == 200
    rel_salvo = post_res.json()
    assert rel_salvo["destaques"] == "Destaque de teste automatizado"
    assert rel_salvo["status"] in ("RASCUNHO", "EM_EDICAO")

def test_prazo_excepcional_motivo_opcional_e_atualizar_bimestre(client, auth_headers):
    ex_res = client.get("/api/gestao/exercicios/ativo", headers=auth_headers)
    ex = ex_res.json()
    b1_id = ex["bimestres"][0]["id"]
    b2_id = ex["bimestres"][1]["id"]
    est_res = client.get("/api/gestao/estrutura", headers=auth_headers)
    uorg_id = est_res.json()[0]["uorgs"][0]["id"]

    # Concessão válida sem motivo (motivo opcional)
    payload_sem_motivo = {
        "exercicio_id": ex["id"],
        "bimestre_id": b1_id,
        "uorg_id": uorg_id,
        "data_fim": "2026-04-15"
    }
    res_sem_motivo = client.post("/api/gestao/prazos-excepcionais", json=payload_sem_motivo, headers=auth_headers)
    assert res_sem_motivo.status_code == 200
    assert res_sem_motivo.json()["ativo"] is True
    assert res_sem_motivo.json()["motivo"] is None

    # Concessão válida com motivo formal
    payload_valido = {
        "exercicio_id": ex["id"],
        "bimestre_id": b1_id,
        "uorg_id": uorg_id,
        "motivo": "Solicitação formal da chefia com atraso justificado por greve",
        "data_fim": "2026-04-15"
    }
    res_valido = client.post("/api/gestao/prazos-excepcionais", json=payload_valido, headers=auth_headers)
    assert res_valido.status_code == 200
    assert res_valido.json()["ativo"] is True

    # Atualização manual de status e data de fechamento de bimestre
    res_bim = client.put(
        f"/api/gestao/bimestres/{b2_id}",
        json={"status": "ABERTO", "data_fechamento_regular": "2026-05-20"},
        headers=auth_headers
    )
    assert res_bim.status_code == 200
    bim_data = res_bim.json()
    assert bim_data["status"] == "ABERTO"
    assert bim_data["data_fechamento_regular"].startswith("2026-05-20")

def test_exportar_relatorio_excel_e_matriz(client, auth_headers):
    # Buscar relatório salvo
    ex_res = client.get("/api/gestao/exercicios/ativo", headers=auth_headers)
    ex = ex_res.json()
    b1_id = ex["bimestres"][0]["id"]
    est_res = client.get("/api/gestao/estrutura", headers=auth_headers)
    uorg_id = est_res.json()[0]["uorgs"][0]["id"]

    rel_res = client.get(
        f"/api/gestao/relatorios?exercicio_id={ex['id']}&bimestre_id={b1_id}&uorg_id={uorg_id}",
        headers=auth_headers
    )
    rel_id = rel_res.json()["id"]

    if rel_id:
        res_excel = client.get(f"/api/gestao/relatorios/{rel_id}/export/excel", headers=auth_headers)
        assert res_excel.status_code == 200
        assert len(res_excel.content) > 1000

        res_pdf = client.get(f"/api/gestao/relatorios/{rel_id}/export/pdf", headers=auth_headers)
        assert res_pdf.status_code == 200
        assert res_pdf.content.startswith(b"%PDF")

    # Matriz consolidada
    res_matriz_excel = client.get("/api/gestao/matriz/export/excel", headers=auth_headers)
    assert res_matriz_excel.status_code == 200
    assert len(res_matriz_excel.content) > 1000


def test_efeito_cascata_entrega_concluida(client, auth_headers):
    ex_res = client.get("/api/gestao/exercicios/ativo", headers=auth_headers)
    ex = ex_res.json()
    b1_id = ex["bimestres"][0]["id"]
    b2_id = ex["bimestres"][1]["id"]
    b3_id = ex["bimestres"][2]["id"]
    est_res = client.get("/api/gestao/estrutura", headers=auth_headers)
    uorg_id = est_res.json()[0]["uorgs"][0]["id"]

    # Criar entrega planejada para a UORG
    ent_res = client.post(
        "/api/gestao/planejamento/entregas",
        json={"uorg_id": uorg_id, "exercicio_id": ex["id"], "titulo": "Entrega Cascata Teste"},
        headers=auth_headers
    )
    assert ent_res.status_code == 200
    entrega_id = ent_res.json()["id"]

    # Marcar como concluída no 1º Bimestre
    payload_b1 = {
        "exercicio_id": ex["id"],
        "bimestre_id": b1_id,
        "uorg_id": uorg_id,
        "destaques": "Entrega concluída no B1",
        "dificuldades": "Nenhuma dificuldade",
        "itens_entrega": [{"entrega_id": entrega_id, "concluida": True, "observacoes": "Feito no B1"}],
        "itens_indicador": []
    }
    res_save = client.post("/api/gestao/relatorios/rascunho", json=payload_b1, headers=auth_headers)
    assert res_save.status_code == 200

    # Consultar 2º e 3º Bimestres e verificar propagação em cascata
    for b_next in [b2_id, b3_id]:
        res_next = client.get(
            f"/api/gestao/relatorios?exercicio_id={ex['id']}&bimestre_id={b_next}&uorg_id={uorg_id}",
            headers=auth_headers
        )
        assert res_next.status_code == 200
        rel_next = res_next.json()
        item_cascata = next((i for i in rel_next["itens_entrega"] if i["entrega_id"] == entrega_id), None)
        assert item_cascata is not None
        assert item_cascata["concluida"] is True
        assert item_cascata["concluida_anteriormente"] is True
        assert item_cascata["bimestre_conclusao_id"] == b1_id


def test_motor_periodicidade_indicadores():
    # Mensal: sempre aplicável, 2 campos (ex: 2º BI -> Março e Abril)
    cfg_mensal = obter_configuracao_periodicidade("MENSAL", 2)
    assert cfg_mensal["aplicavel"] is True
    assert cfg_mensal["quantidade_campos"] == 2
    assert cfg_mensal["competencias"] == ["Março", "Abril"]

    # Trimestral: aplicável apenas nos bimestres 2, 3, 5, 6
    assert obter_configuracao_periodicidade("TRIMESTRAL", 1)["aplicavel"] is False
    assert obter_configuracao_periodicidade("TRIMESTRAL", 2)["aplicavel"] is True
    assert obter_configuracao_periodicidade("TRIMESTRAL", 3)["aplicavel"] is True
    assert obter_configuracao_periodicidade("TRIMESTRAL", 4)["aplicavel"] is False
    assert obter_configuracao_periodicidade("TRIMESTRAL", 5)["aplicavel"] is True
    assert obter_configuracao_periodicidade("TRIMESTRAL", 6)["aplicavel"] is True

    # Quadrimestral: aplicável apenas nos bimestres 2, 4, 6
    assert obter_configuracao_periodicidade("QUADRIMESTRAL", 1)["aplicavel"] is False
    assert obter_configuracao_periodicidade("QUADRIMESTRAL", 2)["aplicavel"] is True
    assert obter_configuracao_periodicidade("QUADRIMESTRAL", 3)["aplicavel"] is False
    assert obter_configuracao_periodicidade("QUADRIMESTRAL", 4)["aplicavel"] is True

    # Semestral: aplicável apenas nos bimestres 3 e 6
    assert obter_configuracao_periodicidade("SEMESTRAL", 1)["aplicavel"] is False
    assert obter_configuracao_periodicidade("SEMESTRAL", 2)["aplicavel"] is False
    assert obter_configuracao_periodicidade("SEMESTRAL", 3)["aplicavel"] is True
    assert obter_configuracao_periodicidade("SEMESTRAL", 6)["aplicavel"] is True

    # Validação de indisponibilidade justificada vs não aplicável
    pendencias_ok = validar_itens_indicador_bimestre([
        {"nome": "Ind Semestral", "periodicidade": "SEMESTRAL", "valor_apurado": None, "nao_aplicavel": True},
        {"nome": "Ind Mensal", "periodicidade": "MENSAL", "competencia": "Janeiro", "resultado_indisponivel": True, "justificativa_indisponibilidade": "Dados aguardando fechamento do AGHU"}
    ], 1)
    assert len(pendencias_ok) == 0

    pendencias_erro = validar_itens_indicador_bimestre([
        {"nome": "Ind Bimestral", "periodicidade": "BIMESTRAL", "valor_apurado": None, "resultado_indisponivel": False}
    ], 1)
    assert len(pendencias_erro) == 1


def test_dashboard_uorgs_acessiveis_e_metricas(client, auth_headers):
    res_uorgs = client.get("/api/relatorios-gestao/dashboard/uorgs-acessiveis", headers=auth_headers)
    assert res_uorgs.status_code == 200
    uorgs = res_uorgs.json()
    assert len(uorgs) == 23
    # Verificar metadados hierárquicos e resumo X/Y
    assert "tipo_uorg" in uorgs[0]
    assert "concluidas" in uorgs[0]
    assert "total" in uorgs[0]

    primeira_uorg_id = uorgs[0]["id"]
    res_metricas = client.get(f"/api/relatorios-gestao/dashboard/metricas/{primeira_uorg_id}", headers=auth_headers)
    assert res_metricas.status_code == 200
    dados = res_metricas.json()
    assert "resumo_entregas" in dados
    assert "total" in dados["resumo_entregas"]
    assert "concluidas" in dados["resumo_entregas"]
    assert "percentual_conclusao" in dados["resumo_entregas"]
    assert "bimestres_respondidos" in dados
    assert len(dados["bimestres_respondidos"]) == 6
    assert "resumo_uorgs_contexto" in dados
    assert "entregas" in dados
    assert "indicadores" in dados


def test_rbac_hierarquia_divisao_setor_gerente_e_feedback(client, auth_headers):
    # 1. Login como Chefe de Setor (SETISD)
    login_setor = client.post("/api/login", data={"username": "chefe.setisd", "password": "123"})
    assert login_setor.status_code == 200
    headers_setor = {"Authorization": f"Bearer {login_setor.json()['access_token']}"}

    me_setor = client.get("/api/gestao/me", headers=headers_setor).json()
    assert me_setor["tipo_uorg"] == "SETOR"
    assert me_setor["uorg_sigla"] == "SETISD"

    uorgs_setor = client.get("/api/relatorios-gestao/uorgs", headers=headers_setor).json()
    assert len(uorgs_setor) == 1
    assert uorgs_setor[0]["sigla"] == "SETISD"

    # 2. Login como Chefe de Divisão (DAF -> DAF, SAD, SGOF, SCONT)
    login_div = client.post("/api/login", data={"username": "chefe.daf", "password": "123"})
    assert login_div.status_code == 200
    headers_div = {"Authorization": f"Bearer {login_div.json()['access_token']}"}

    me_div = client.get("/api/gestao/me", headers=headers_div).json()
    assert me_div["tipo_uorg"] == "DIVISAO"
    assert me_div["uorg_sigla"] == "DAF"
    assert set(me_div["subordinados_siglas"]) == {"SAD", "SGOF", "SCONT"}

    uorgs_div = client.get("/api/relatorios-gestao/uorgs", headers=headers_div).json()
    siglas_div = {u["sigla"] for u in uorgs_div}
    assert siglas_div == {"DAF", "SAD", "SGOF", "SCONT"}

    # Chefe de Divisão NÃO pode editar rascunho de Setor subordinado (ex: SAD)
    sad_uorg = next(u for u in uorgs_div if u["sigla"] == "SAD")
    ex = client.get("/api/gestao/exercicios/ativo", headers=headers_div).json()
    b1_id = ex["bimestres"][0]["id"]
    res_forb = client.post(
        "/api/gestao/relatorios/rascunho",
        json={
            "exercicio_id": ex["id"],
            "bimestre_id": b1_id,
            "uorg_id": sad_uorg["id"],
            "destaques": "Tentativa indevida",
            "dificuldades": "Tentativa indevida",
            "itens_entrega": [],
            "itens_indicador": []
        },
        headers=headers_div
    )
    assert res_forb.status_code == 403

    # 3. Login como Gerente (GAD) -> NÃO pode registrar feedback institucional (HTTP 403)
    login_ger = client.post("/api/login", data={"username": "gerente.gad", "password": "123"})
    assert login_ger.status_code == 200
    headers_ger = {"Authorization": f"Bearer {login_ger.json()['access_token']}"}

    matriz_ger = client.get("/api/gestao/matriz", headers=headers_ger).json()
    # Todas as linhas da matriz do gerente.gad pertencem à GAD
    assert all(l["gerencia_sigla"] == "GAD" for l in matriz_ger["linhas"])
    rel_id_gad = next(
        (b["relatorio_id"] for l in matriz_ger["linhas"] for b in l["bimestres"] if b["relatorio_id"]),
        None
    )
    assert rel_id_gad is not None

    fb_ger = client.post(
        f"/api/gestao/relatorios/{rel_id_gad}/feedback",
        json={"texto": "Tentativa de parecer pelo gerente"},
        headers=headers_ger
    )
    assert fb_ger.status_code == 403

    # 4. Login como Superintendente -> PODE registrar feedback institucional (HTTP 200)
    login_sup = client.post("/api/login", data={"username": "superintendente", "password": "123"})
    assert login_sup.status_code == 200
    headers_sup = {"Authorization": f"Bearer {login_sup.json()['access_token']}"}

    fb_sup = client.post(
        f"/api/gestao/relatorios/{rel_id_gad}/feedback",
        json={"texto": "Parecer institucional validado pela Superintendência."},
        headers=headers_sup
    )
    assert fb_sup.status_code == 200
    assert fb_sup.json()["autor_perfil"] == "SUPERINTENDENTE"




