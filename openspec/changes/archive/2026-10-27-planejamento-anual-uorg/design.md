# Design

## Context

A arquitetura do Portal segue o padrão do **Framework SETISD-HC-UFPE** em camadas estritas (`Router -> Controller -> Provider -> Resource`).
Os modelos `EntregaPlanejada`, `Indicador`, `Exercicio` e `Uorg` já existem no banco relacional SQLite local (`data/app.db`).
Esta extensão implementa a gestão completa do ciclo de planejamento anual (Fase 4 da especificação oficial), permitindo que o Chefe de UORG cadastre e edite entregas e indicadores antes do início da coleta bimestral.

## Goals / Non-Goals

**Goals:**
- Implementar endpoints RESTful em `src/routers/relatorio_gestao.py` para gerenciamento de entregas e indicadores do planejamento.
- Aplicar validações de escopo de acesso (RBAC): o Chefe só opera sobre a UORG associada ao seu perfil; o Administrador opera sobre qualquer UORG.
- Validar se o exercício está com o status `PLANEJAMENTO` para permitir alterações operacionais pelo Chefe (RN-EXE-01, RF-ENT-02, RF-IND-01).
- Garantir a regra de limite de 1 a 3 indicadores ativos por UORG (RF-IND-01).
- Proteger contra remoções destrutivas com soft delete (`ativo = False`), preservando a integridade histórica de relatórios (RN-ENT-03 e RN-IND-06).
- Criar a interface reativa `PlanejamentoAnual.vue` com modais estilizados com Tailwind CSS e integração transparente ao Pinia e Axios.

**Non-Goals:**
- Permitir edição de entregas/indicadores por Gerentes ou Superintendente (estritamente não permitido pela Matriz de Permissões da Seção 5.3 do documento funcional).
- Permitir alteração de dados de exercícios anteriores encerrados.

## Decisions

### 1. Reutilização dos Modelos e Soft Delete
- **Decisão**: Utilizar os campos `ativo` existentes em `EntregaPlanejada` e `Indicador`. A remoção lógica seta `ativo = False`, impedindo que o item apareça em novos planejamentos, mas mantendo referências íntegras em relatórios já concluídos.
- **Alternativa rejeitada**: Exclusão física (`DELETE FROM`). Rejeitada porque quebraria a integridade referencial dos relatórios anteriores já enviados (RN-ENT-03, RN-IND-06).

### 2. Validação Centralizada no Controller e Provider
- **Decisão**: Toda checagem de regras de negócio (limite de 3 indicadores, status do exercício em `PLANEJAMENTO`, validação de escopo de UORG do usuário logado) é executada no backend (`relatorio_gestao_controller.py` e `relatorio_gestao_sqlite_provider.py`), nunca delegada apenas ao frontend.
- **Alternativa rejeitada**: Apenas desabilitar botões na interface. Violaria a regra RN-ACL-02 ("Autorização no servidor").

### 3. Schemas Pydantic Dedicados
- **Decisão**: Criar schemas específicos em `src/schemas/relatorio_gestao.py`:
  - `CriarEntregaSchema` (uorg_id, exercicio_id, titulo, descricao, ordem)
  - `EditarEntregaSchema` (titulo, descricao)
  - `CriarIndicadorSchema` (uorg_id, exercicio_id, nome, descricao, periodicidade, unidade_medida, meta_operador, meta_valor, meta_valor_max, ordem)
  - `EditarIndicadorSchema` (nome, descricao, periodicidade, unidade_medida, meta_operador, meta_valor, meta_valor_max)
- **Alternativa rejeitada**: Reutilizar payloads genéricos sem validação de tipos.

### 4. Interface Intuitiva e Reativa no Vue 3
- **Decisão**: A tela `PlanejamentoAnual.vue` exibe um banner indicativo do status do planejamento ("Planejamento Aberto para Edição" em verde ou "Planejamento Fechado" em cinza/âmbar), cartões resumidos de contagem de entregas e indicadores cadastrados (ex: "2 de 3 indicadores cadastrados"), e botões de ação com modais acessíveis.

## Risks / Trade-offs

- **[Risco: Concorrência entre múltiplos usuários da mesma UORG]** → Mitigação: Auditoria detalhada de cada criação/alteração com timestamp e username em `audit_logs`.
- **[Risco: Inativação acidental de indicador em uso]** → Mitigação: Modal de confirmação explícito no frontend e soft delete no backend.

## Migration Plan

1. Nenhuma migração de schema estrutural é necessária, pois as tabelas relacionais já contêm os campos necessários (`ativo`, `uorg_id`, `exercicio_id`).
2. Adicionar novos métodos ao Provider e Controller.
3. Registrar rotas no Router FastAPI e validar conformidade com `audit_framework.py`.
4. Implementar a tela no Vue 3 e compilar o frontend com `npm run build`.
5. Executar suíte de testes com `pytest`.
