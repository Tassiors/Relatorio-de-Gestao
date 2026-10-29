# Design

## Context

O sistema utiliza arquitetura desacoplada com backend em Python 3.12+ (FastAPI, SQLAlchemy 2.0 assíncrono e SQLite local) e frontend em Vue 3, Vite, Pinia e Tailwind CSS. A especificação funcional aprovada prevê ciclos bimestrais como janelas operacionais de coleta e regras de periodicidade distintas para indicadores (mensal, bimestral, trimestral, quadrimestral, semestral). O design a seguir detalha a reestruturação das interfaces, fluxos de permissão hierárquica e regras de consistência dos dados.

## Goals / Non-Goals

**Goals:**
- Simplificar e tornar mais acionável o Dashboard inicial (`HomeView.vue`), com atalhos baseados em papéis (`ADMINISTRADOR`, `SUPERINTENDENTE`, `GERENTE`, `CHEFE`), seletor hierárquico de UORGs e visualização rápida de entregas e indicadores com metas.
- Padronizar o catálogo de unidades de medida no planejamento anual com seleção fechada (dropdown).
- Propagar automaticamente entregas marcadas como `CONCLUÍDA` para os bimestres posteriores do exercício (efeito cascata).
- Implementar o motor de periodicidade de indicadores conforme seções 8.2 e 8.3 da especificação funcional, orientando o usuário com instruções contextuais e suporte a indisponibilidade justificada.
- Conceder autonomia ao administrador para alternar status de bimestres e definir datas de corte, tornando a justificativa de prazo excepcional opcional.

**Non-Goals:**
- Alterar o mecanismo central de autenticação JWT/AD e cookies HttpOnly.
- Alterar os modelos de exportação em PDF e Excel além da acomodação dos dados resultantes das novas regras.

## Decisions

### 1. Hierarquia de UORGs no Seletor do Dashboard
- **Decisão:** A API fornecerá endpoint `/api/relatorios-gestao/dashboard/uorgs-acessiveis` que retorna:
  - Todas as UORGs ativas caso o usuário seja `ADMINISTRADOR` ou `SUPERINTENDENTE`.
  - A UORG do próprio usuário e suas unidades subordinadas caso seja `GERENTE` ou `CHEFE`.
- **Alternativa Rejeitada:** Enviar todas as UORGs e filtrar no frontend (inseguro e não atende ao modelo de menor privilégio).

### 2. Efeito Cascata de Entregas Concluídas
- **Decisão:** Ao salvar ou submeter um relatório bimestral no qual uma entrega planejada é categorizada como `CONCLUIDA`, o backend atualizará (ou pré-carregará) o status `CONCLUIDA` nos registros dos bimestres seguintes para a mesma UORG e exercício. No frontend, caso uma entrega já tenha sido concluída em bimestre anterior, ela é apresentada como concluída previamente com badge distintivo e campo de observação bloqueado para edição redundante.
- **Alternativa Rejeitada:** Deixar que o usuário marque manualmente a cada bimestre (gera retrabalho para as chefias e inconsistência longitudinal).

### 3. Motor Centralizado de Periodicidade de Indicadores
- **Decisão:** Implementação de regra padronizada tanto em helper de validação do backend (`src/helpers/indicador_helper.py`) quanto utilitário de tela no frontend (`frontend/src/utils/indicadorHelper.ts`):
  - `MENSAL`: solicita 2 valores mensais por bimestre (ex: Mês 1 e Mês 2).
  - `BIMESTRAL`: solicita 1 valor correspondente ao período do bimestre.
  - `TRIMESTRAL`: solicita resultado apenas nos bimestres de fechamento de trimestre (2º BI: Jan-Mar; 3º BI: Abr-Jun; 5º BI: Jul-Set; 6º BI: Out-Dez). Nos demais bimestres (1º e 4º BI), é tratado como "Não aplicável ao período".
  - `QUADRIMESTRAL`: solicita resultado nos 2º BI (Jan-Abr), 4º BI (Mai-Ago) e 6º BI (Set-Dez). No 1º, 3º e 5º BI, exibe como "Não aplicável ao período".
  - `SEMESTRAL`: solicita resultado nos 3º BI (Jan-Jun) e 6º BI (Jul-Dez). Nos demais (1º, 2º, 4º e 5º BI), exibe como "Não aplicável ao período".
- **Alternativa Rejeitada:** Tratar todos os indicadores de forma genérica com um único campo numérico fixo.

### 4. Gestão Flexível de Exercício e Prazos Excepcionais
- **Decisão:** O schema Pydantic `PrazoExcepcionalCreate` terá o campo `motivo` com `Optional[str] = None` (sem validação de mínimo de 10 caracteres). O endpoint de atualização do status do bimestre permitirá abrir/fechar qualquer bimestre sob demanda e gravar a nova data de fechamento customizada no modelo `JanelaRelatorio`.
- **Alternativa Rejeitada:** Manter trava automática fixa às 23h59 da data pré-calculada (retirada a pedido do usuário).

### 5. Design Visual Lúdico e Inspirador no Preenchimento
- **Decisão:** Transformar os itens 3 (Destaques) e 4 (Dificuldades) em cartões visualmente estimulantes, com paleta de cores temática (verde/esmeralda com ícone de troféu/foguete para Destaques; âmbar/azul com ícone de bússola/alvo para Dificuldades), cards com micro-interações, dicas contextuais acolhedoras e contadores de caracteres amigáveis.

## Risks / Trade-offs

- **[Risco] Cascata de conclusão caso o gestor tenha marcado concluída por engano:**
  - *Mitigação:* Se o relatório do bimestre anterior for reaberto e o status da entrega for alterado para "EM_ANDAMENTO", o sistema recalculará a cascata desmarcando o avanço indevido.
- **[Risco] Preenchimento de indicadores complexos (ex: bimestres sem coleta):**
  - *Mitigação:* Exibir badges amigáveis de "Não aplicável a este bimestre" e orientações textuais dinâmicas explicando claramente ao gestor quando a próxima medição ocorrerá.

## Migration Plan

1. Atualização dos schemas e endpoints backend (`src/controllers/`, `src/providers/`, `src/routers/`).
2. Ajustes nos testes unitários e de integração (`tests/`).
3. Atualização dos componentes Vue (`frontend/src/views/`, `frontend/src/components/`).
4. Re-execução da suíte completa de testes e auditor de conformidade arquitetural (`audit_framework.py`).
