# tests/test_planejamento_anual.py
import pytest

def get_auth_token(client, username, password):
    res = client.post("/api/login", data={"username": username, "password": password})
    assert res.status_code == 200, f"Falha no login com {username}: {res.text}"
    return res.json()["access_token"]

@pytest.fixture
def admin_headers(client):
    token = get_auth_token(client, "admin", "admin")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def chefe_setisd_headers(client):
    token = get_auth_token(client, "chefe.setisd", "chefe123")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def chefe_stgq_headers(client):
    token = get_auth_token(client, "chefe.stgq", "chefe123")
    return {"Authorization": f"Bearer {token}"}


def test_rbac_consulta_planejamento(client, admin_headers, chefe_setisd_headers):
    """
    Testa regras de controle de acesso (RBAC):
    - Chefe consulta sua própria UORG com sucesso.
    - Chefe é bloqueado com 403 ao tentar consultar UORG alheia.
    - Administrador pode consultar qualquer UORG.
    """
    # 1. Obter dados do usuário chefe.setisd para saber seu uorg_id
    me_res = client.get("/api/gestao/me", headers=chefe_setisd_headers)
    assert me_res.status_code == 200
    setisd_uorg_id = me_res.json()["uorg_id"]
    assert setisd_uorg_id is not None

    # Obter outra UORG (ex: STGQ ou primeira diferente)
    est_res = client.get("/api/gestao/estrutura", headers=admin_headers)
    assert est_res.status_code == 200
    all_uorgs = [u for g in est_res.json() for u in g["uorgs"]]
    outra_uorg = next(u for u in all_uorgs if u["id"] != setisd_uorg_id)
    outra_uorg_id = outra_uorg["id"]

    # 2. Chefe SETISD consulta própria UORG -> 200 OK
    res_propria = client.get(f"/api/gestao/planejamento/uorg/{setisd_uorg_id}", headers=chefe_setisd_headers)
    assert res_propria.status_code == 200
    dados = res_propria.json()
    assert "entregas" in dados
    assert "indicadores" in dados
    assert "planejamento_aberto" in dados

    # 3. Chefe SETISD tenta consultar outra UORG -> 403 Forbidden
    res_alheia = client.get(f"/api/gestao/planejamento/uorg/{outra_uorg_id}", headers=chefe_setisd_headers)
    assert res_alheia.status_code == 403
    assert "Acesso não autorizado" in res_alheia.json()["detail"]

    # 4. Administrador consulta outra UORG -> 200 OK
    res_admin = client.get(f"/api/gestao/planejamento/uorg/{outra_uorg_id}", headers=admin_headers)
    assert res_admin.status_code == 200


def test_controle_janela_planejamento(client, admin_headers, chefe_setisd_headers):
    """
    Testa o controle da janela de planejamento:
    - Chefe não tem permissão para alterar status do exercício (403 Forbidden).
    - Administrador abre a janela de planejamento com sucesso.
    """
    ex_res = client.get("/api/gestao/exercicios/ativo", headers=admin_headers)
    assert ex_res.status_code == 200
    exercicio_id = ex_res.json()["id"]

    # Chefe tenta abrir planejamento -> 403 Forbidden
    res_chefe = client.post(
        f"/api/gestao/planejamento/exercicio/{exercicio_id}/abrir-planejamento",
        headers=chefe_setisd_headers
    )
    assert res_chefe.status_code == 403

    # Administrador abre planejamento -> 200 OK
    res_admin = client.post(
        f"/api/gestao/planejamento/exercicio/{exercicio_id}/abrir-planejamento",
        headers=admin_headers
    )
    assert res_admin.status_code == 200
    assert res_admin.json()["status"] == "PLANEJAMENTO"


def test_ciclo_entregas_planejadas(client, admin_headers, chefe_setisd_headers):
    """
    Testa inclusão, edição e inativação de entrega planejada:
    - Inclusão com sucesso na janela aberta.
    - Edição de título/descrição.
    - Inativação lógica (soft delete).
    """
    ex_res = client.get("/api/gestao/exercicios/ativo", headers=admin_headers)
    exercicio_id = ex_res.json()["id"]

    me_res = client.get("/api/gestao/me", headers=chefe_setisd_headers)
    uorg_id = me_res.json()["uorg_id"]

    # Garantir janela aberta
    client.post(f"/api/gestao/planejamento/exercicio/{exercicio_id}/abrir-planejamento", headers=admin_headers)

    # 1. Cadastrar entrega
    payload_criar = {
        "uorg_id": uorg_id,
        "exercicio_id": exercicio_id,
        "titulo": "Implementar Módulo de Auditoria Automatizada",
        "descricao": "Entrega anual planejada do SETISD para 2026",
        "ordem": 99
    }
    res_criar = client.post("/api/gestao/planejamento/entregas", json=payload_criar, headers=chefe_setisd_headers)
    assert res_criar.status_code == 200, res_criar.text
    entrega = res_criar.json()
    entrega_id = entrega["id"]
    assert entrega["titulo"] == payload_criar["titulo"]

    # 2. Editar entrega
    payload_editar = {
        "titulo": "Implementar Módulo de Auditoria Automatizada (Revisado)",
        "descricao": "Descrição atualizada da entrega anual"
    }
    res_editar = client.put(f"/api/gestao/planejamento/entregas/{entrega_id}", json=payload_editar, headers=chefe_setisd_headers)
    assert res_editar.status_code == 200
    assert res_editar.json()["titulo"] == payload_editar["titulo"]

    # 3. Inativar entrega (soft delete)
    res_inativar = client.delete(f"/api/gestao/planejamento/entregas/{entrega_id}", headers=chefe_setisd_headers)
    assert res_inativar.status_code == 200
    assert res_inativar.json()["sucesso"] is True

    # 4. Verificar que a entrega inativada não aparece na lista ativa
    plan_res = client.get(f"/api/gestao/planejamento/uorg/{uorg_id}", headers=chefe_setisd_headers)
    assert plan_res.status_code == 200
    entregas_ativas_ids = [e["id"] for e in plan_res.json()["entregas"]]
    assert entrega_id not in entregas_ativas_ids


def test_bloqueio_cadastro_com_janela_fechada(client, admin_headers, chefe_setisd_headers):
    """
    Testa bloqueio de alterações quando o planejamento anual estiver fechado:
    - Chefe recebe 400 ao tentar cadastrar entrega com status EM_ANDAMENTO.
    """
    ex_res = client.get("/api/gestao/exercicios/ativo", headers=admin_headers)
    exercicio_id = ex_res.json()["id"]

    me_res = client.get("/api/gestao/me", headers=chefe_setisd_headers)
    uorg_id = me_res.json()["uorg_id"]

    # Fechar janela de planejamento
    client.post(f"/api/gestao/planejamento/exercicio/{exercicio_id}/fechar-planejamento", headers=admin_headers)

    # Chefe tenta cadastrar entrega com planejamento fechado -> 400 Bad Request
    payload = {
        "uorg_id": uorg_id,
        "exercicio_id": exercicio_id,
        "titulo": "Tentativa de entrega com janela fechada",
        "ordem": 1
    }
    res = client.post("/api/gestao/planejamento/entregas", json=payload, headers=chefe_setisd_headers)
    assert res.status_code == 400
    assert "janela de planejamento" in res.json()["detail"].lower()

    # Reabrir janela para não interferir em outros testes
    client.post(f"/api/gestao/planejamento/exercicio/{exercicio_id}/abrir-planejamento", headers=admin_headers)


def test_limite_e_ciclo_indicadores(client, admin_headers, chefe_setisd_headers):
    """
    Testa cadastro, validação de limites (máx. 3 indicadores) e edição/inativação de indicador:
    - Respeita o limite de 1 a 3 indicadores ativos por UORG.
    - Rejeita o 4º indicador com código 400.
    - Permite inativação e posterior inclusão mantendo o teto de 3.
    """
    ex_res = client.get("/api/gestao/exercicios/ativo", headers=admin_headers)
    exercicio_id = ex_res.json()["id"]

    me_res = client.get("/api/gestao/me", headers=chefe_setisd_headers)
    uorg_id = me_res.json()["uorg_id"]

    # Garantir janela aberta
    client.post(f"/api/gestao/planejamento/exercicio/{exercicio_id}/abrir-planejamento", headers=admin_headers)

    # Obter indicadores atuais da UORG
    plan_res = client.get(f"/api/gestao/planejamento/uorg/{uorg_id}", headers=chefe_setisd_headers)
    inds_existentes = plan_res.json()["indicadores"]
    qtd_atual = len(inds_existentes)

    novos_ids = []
    # Preencher até atingir 3 indicadores
    for i in range(qtd_atual, 3):
        payload_ind = {
            "uorg_id": uorg_id,
            "exercicio_id": exercicio_id,
            "nome": f"Indicador Teste {i+1}",
            "descricao": "Descrição do indicador anual",
            "periodicidade": "BIMESTRAL",
            "unidade_medida": "%",
            "meta_operador": "MAIOR_IGUAL",
            "meta_valor": 80.0 + i
        }
        res_ind = client.post("/api/gestao/planejamento/indicadores", json=payload_ind, headers=chefe_setisd_headers)
        assert res_ind.status_code == 200, res_ind.text
        novos_ids.append(res_ind.json()["id"])

    # Tentativa de cadastrar o 4º indicador -> Deve falhar com 400
    payload_excedente = {
        "uorg_id": uorg_id,
        "exercicio_id": exercicio_id,
        "nome": "Indicador Excedente Quarto",
        "unidade_medida": "%",
        "meta_operador": "MAIOR_IGUAL",
        "meta_valor": 95.0
    }
    res_excedente = client.post("/api/gestao/planejamento/indicadores", json=payload_excedente, headers=chefe_setisd_headers)
    assert res_excedente.status_code == 400
    assert "limite máximo de 3 indicadores" in res_excedente.json()["detail"].lower()

    # Inativar um indicador recém-criado
    ind_para_inativar = novos_ids[-1] if novos_ids else inds_existentes[0]["id"]
    res_inativar = client.delete(f"/api/gestao/planejamento/indicadores/{ind_para_inativar}", headers=chefe_setisd_headers)
    assert res_inativar.status_code == 200
    assert res_inativar.json()["sucesso"] is True

    # Agora deve permitir cadastrar novamente pois o total ativo é < 3
    res_repor = client.post("/api/gestao/planejamento/indicadores", json=payload_excedente, headers=chefe_setisd_headers)
    assert res_repor.status_code == 200
    novo_criado_id = res_repor.json()["id"]

    # Editar indicador
    payload_edit_ind = {
        "nome": "Indicador Quarto Atualizado",
        "periodicidade": "SEMESTRAL",
        "unidade_medida": "UNIDADES",
        "meta_operador": "IGUAL",
        "meta_valor": 100.0
    }
    res_edit_ind = client.put(f"/api/gestao/planejamento/indicadores/{novo_criado_id}", json=payload_edit_ind, headers=chefe_setisd_headers)
    assert res_edit_ind.status_code == 200
    assert res_edit_ind.json()["nome"] == payload_edit_ind["nome"]
    assert res_edit_ind.json()["periodicidade"] == "SEMESTRAL"
