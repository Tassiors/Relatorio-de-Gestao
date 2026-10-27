# Proposal

## Why

Conforme especificado no documento funcional oficial do HC-UFPE (`Especificacao_Funcional_Relatorio_Gestao_HC_UFPE_v1.0.docx`, Seções 5.2, 5.3, 7.1, 8.1 e 20.2), o Chefe / Gestor de Unidade Organizacional (UORG) possui a competência de cadastrar e manter as entregas institucionais da sua unidade e de 1 a 3 indicadores anuais com metas e periodicidades quando a janela de planejamento estiver aberta (`status == 'PLANEJAMENTO'`). 

Atualmente no sistema, as entregas e indicadores do Exercício 2026 foram apenas importados via seed do REDCap, e o sistema só oferece a tela de preenchimento do bimestre. Faltava a tela e os endpoints de API dedicados para o Chefe de UORG e Administrador gerenciarem as entregas e indicadores da unidade na fase de planejamento anual.

## What Changes

- **Backend (API & Domínio):**
  - Criação de endpoints em `/api/gestao/planejamento`:
    - `GET /api/gestao/planejamento/uorg/{uorg_id}`: Lista entregas e indicadores do exercício para a UORG com status da janela de planejamento.
    - `POST /api/gestao/planejamento/entregas`: Cadastra nova entrega da UORG no exercício ativo.
    - `PUT /api/gestao/planejamento/entregas/{entrega_id}`: Edita título e descrição da entrega planejada.
    - `DELETE /api/gestao/planejamento/entregas/{entrega_id}`: Inativa entrega (soft delete se tiver histórico ou remoção lógica conforme RN-ENT-03).
    - `POST /api/gestao/planejamento/indicadores`: Cadastra indicador anual da UORG validando limite de 1 a 3 indicadores (RF-IND-01), meta numérica, operador (`>=`, `<=`, `=`, `ENTRE`) e periodicidade.
    - `PUT /api/gestao/planejamento/indicadores/{indicador_id}`: Edita indicador existente na janela aberta.
    - `DELETE /api/gestao/planejamento/indicadores/{indicador_id}`: Inativa indicador (RN-IND-06).
    - `POST /api/gestao/planejamento/exercicio/{exercicio_id}/abrir-planejamento` e `fechar-planejamento`: Controle do status do exercício pelo Administrador.
  - Validação de regras de negócio:
    - Chefe só acessa e edita sua própria UORG (RN-NFR-01 e RN-ACL-02). Administrador acessa todas.
    - Modificações só são aceitas se o exercício estiver em estado de planejamento aberto (`PLANEJAMENTO`), salvo intervenção administrativa.
    - Quantidade de indicadores entre 1 e 3 ativos por UORG (RF-IND-01).
    - Trilha de auditoria em todas as mutações via `registrar_auditoria()`.

- **Frontend (Interface Vue 3):**
  - Criação da tela `frontend/src/views/PlanejamentoAnual.vue`:
    - Visualização do status do planejamento (Aberto para edição ou Fechado).
    - Seletor de UORG (para Administrador) ou fixo na UORG do usuário autenticado (para Chefe de UORG).
    - Gestão de Entregas: Lista das entregas cadastradas, formulário/modal para adicionar nova entrega, editar ou inativar.
    - Gestão de Indicadores: Lista dos indicadores cadastrados com badge de periodicidade, meta e operador, formulário/modal para incluir indicador com validação de limite (máx. 3).
  - Inclusão da rota `/planejamento` no Vue Router (`frontend/src/router/index.ts`).
  - Adição do item de menu "Planejamento Anual" no menu lateral `DefaultLayout.vue`.

## Capabilities

### New Capabilities
- `planejamento-anual`: Cadastro, manutenção e gestão anual de entregas e indicadores por Unidade Organizacional (UORG) com controle de janela de planejamento anual.

### Modified Capabilities
<!-- Nenhuma capacidade existente teve seus requisitos modificados. -->

## Impact

- **Modelos e Migrações:** Reutilização das entidades `EntregaPlanejada`, `Indicador`, `Exercicio` e `Uorg`.
- **Backend:** `src/routers/relatorio_gestao.py`, `src/controllers/relatorio_gestao_controller.py`, `src/providers/interfaces/relatorio_gestao_provider_interface.py`, `src/providers/implementations/relatorio_gestao_sqlite_provider.py`.
- **Frontend:** `frontend/src/views/PlanejamentoAnual.vue`, `frontend/src/layouts/DefaultLayout.vue`, `frontend/src/router/index.ts`, `frontend/src/services/gestaoService.ts`.
- **Testes:** Nova suíte de testes em `tests/test_planejamento_anual.py`.
