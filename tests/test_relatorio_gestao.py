# tests/test_relatorio_gestao.py
import pytest
from src.controllers.relatorio_gestao_controller import calcular_atingimento_meta

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
    assert rel_salvo["status"] == "RASCUNHO"

def test_prazo_excepcional_motivo_obrigatorio(client, auth_headers):
    ex_res = client.get("/api/gestao/exercicios/ativo", headers=auth_headers)
    ex = ex_res.json()
    b1_id = ex["bimestres"][0]["id"]
    est_res = client.get("/api/gestao/estrutura", headers=auth_headers)
    uorg_id = est_res.json()[0]["uorgs"][0]["id"]

    # Tentativa com motivo curto (menos de 10 caracteres) deve falhar
    payload_invalido = {
        "exercicio_id": ex["id"],
        "bimestre_id": b1_id,
        "uorg_id": uorg_id,
        "motivo": "curto",
        "data_fim": "2026-04-15"
    }
    res_invalido = client.post("/api/gestao/prazos-excepcionais", json=payload_invalido, headers=auth_headers)
    assert res_invalido.status_code in [400, 422]

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
