# Proposal

## Why

O Portal de Relatórios de Gestão do HC-UFPE precisa refletir fielmente a estrutura organizacional em três níveis da EBSERH (Gerências → Divisões → Setores) tanto na visibilidade do menu lateral quanto no escopo de dados do Dashboard, Matriz de Acompanhamento, Planejamento Anual, Preenchimento Bimestral e Visão Consolidada. Adicionalmente, o Dashboard de Início necessita de melhorias analíticas (cards compactos `X/Y` por UORG quando nenhuma unidade está filtrada, eixo X dos gráficos adaptado à temporalidade de cada indicador e alinhamento exato da linha de meta com o topo das colunas), a Visão Consolidada demanda um layout executivo mais atrativo com funcionalidade de impressão de relatório, e os relatórios com Feedback Institucional precisam de maior destaque visual.

## What Changes

- **Hierarquia Organizacional (Divisão vs. Setor) e Escopo RBAC por Perfil**:
  - **Chefe de Setor**: Menu lateral exibe apenas `Início`, `Planejamento Anual`, `Preenchimento Bimestral` e `Visão Consolidada`. Os bimestres respondidos pela unidade são sinalizados no dashboard da tela de Início.
  - **Chefe de Divisão**: Menu lateral exibe apenas `Início`, `Planejamento Anual` (restrito à própria Divisão), `Preenchimento Bimestral` (restrito à própria Divisão), `Visão Consolidada` (Divisão e Setores subordinados) e `Matriz de Acompanhamento` (Divisão e Setores subordinados).
  - **Gerente**: Menu lateral exibe apenas `Início` (com filtro da própria gerência, divisões e setores subordinados), `Matriz de Acompanhamento` (divisões e setores subordinados) e `Visão Consolidada` (somente leitura dos bimestres submetidos por divisões e setores subordinados).
  - **Superintendente**: Menu lateral exibe apenas `Início`, `Matriz de Acompanhamento` e `Visão Consolidada` de todas as UORGs.
  - **Permissão de Feedback Institucional**: **BREAKING** — Apenas usuários com perfil `SUPERINTENDENTE` e `ADMINISTRADOR` podem registrar Pareceres e Feedbacks Institucionais (removendo a permissão de escrita de feedback do perfil `GERENTE`).
- **Refinamentos na Tela de Início (`Home.vue`)**:
  - **BREAKING** — Remoção da seção de "Atalhos Rápidos de Navegação" da tela de Início.
  - Filtros de contexto por perfil: botões de filtro rápido com siglas das gerências (`SUP`, `GAS`, `GAD`, `GEP`) e dropdown de seleção de qualquer UORG para `SUPERINTENDENTE` e `ADMINISTRADOR`; dropdown com opções da própria gerência/divisão e unidades subordinadas para `GERENTE` e `CHEFE` de Divisão.
  - Quando nenhuma UORG específica estiver selecionada no filtro (visão agregada de contexto para Chefe de Divisão, Gerente, Superintendente e Administrador), suprimir o card maior de listagem de entregas e exibir uma linha/grade organizada de cards compactos contendo apenas a **sigla da UORG** no contexto e o respectivo número de entregas concluídas no formato `X/Y` (`X` = concluídas, `Y` = total de entregas).
  - Organização do eixo X de cada gráfico de indicador de acordo com a sua temporalidade (`MENSAL`, `BIMESTRAL`, `TRIMESTRAL`, `QUADRIMESTRAL`, `SEMESTRAL`).
  - Correção matemática e estrutural do posicionamento da linha horizontal de meta nos gráficos de barras para que o topo da barra cujo valor atinge exatamente a meta fique perfeitamente alinhado com a linha tracejada da meta.
- **Redesign Executivo e Impressão na Visão Consolidada (`ConsolidadoGestao.vue`)**:
  - Reformulação visual da página de Visão Consolidada com cabeçalho executivo, indicadores de desempenho e cartões estruturados para leitura gerencial.
  - Adição da funcionalidade de **Imprimir Relatório** (`window.print()` com folha de estilo `@media print` dedicada e layout de relatório institucional limpo).
- **Destaque Visual para Relatórios com Feedback Institucional**:
  - Realce visual proeminente (badges em destaque, bordas luminosas/âmbar-esmeralda e alertas executivos) para relatórios que receberam Parecer/Feedback Institucional na Matriz de Acompanhamento, Visão Consolidada, Preenchimento Bimestral e Dashboard Inicial.

## Capabilities

### New Capabilities
- `navegacao-rbac-hierarquia`: Governança de itens do menu lateral, vínculo hierárquico Divisão → Setores subordinados, escopo de visualização/edição por perfil (Chefe de Setor, Chefe de Divisão, Gerente, Superintendente, Administrador) e restrição de registro de Pareceres/Feedbacks Institucionais a Superintendente e Administrador.
- `visao-consolidada-feedback`: Layout executivo aprimorado para a Visão Consolidada, exportação/impressão em formato de relatório gerencial e destaque visual reforçado em todo o sistema para relatórios com Feedback Institucional registrado.

### Modified Capabilities
- `dashboard-inicio`: Remoção dos atalhos rápidos de navegação; sinalização de bimestres respondidos para Chefe de Setor; filtros por Gerência (`SUP`, `GAS`, `GAD`, `GEP`) e UORGs subordinadas; substituição do card maior de entregas por linha de cards compactos (`SIGLA` + `X/Y`) quando nenhuma UORG está selecionada; eixo X dos gráficos orientado pela temporalidade do indicador; e alinhamento exato da linha de meta com o topo das barras.

## Impact

- **Backend (`src/`)**:
  - `src/models/relatorio_gestao_models.py` / `src/providers/implementations/relatorio_gestao_sqlite_provider.py`: Mapeamento hierárquico de subordinação entre Divisões e Setores (`uorg_pai_id` ou hierarquia de Divisão → Setores subordinados), retorno de resumo `X/Y` de entregas por UORG no endpoint de dashboard, série histórica completa por temporalidade do indicador e bimestres respondidos pela UORG.
  - `src/controllers/relatorio_gestao_controller.py`: Restrição de `registrar_feedback` exclusivamente para `SUPERINTENDENTE` e `ADMINISTRADOR`; filtragem hierárquica para Chefe de Divisão (própria divisão + setores subordinados em leitura consolidada/matriz, escrita restrita à própria divisão) e Gerente (gerência + divisões + setores subordinados em leitura).
- **Frontend (`frontend/src/`)**:
  - `frontend/src/layouts/DefaultLayout.vue` & `frontend/src/router/index.ts`: Regras de exibição do menu lateral e guardas de rota diferenciando Chefe de Setor, Chefe de Divisão, Gerente, Superintendente e Administrador.
  - `frontend/src/views/Home.vue`: Remoção de atalhos rápidos, adição de botões de gerência (`SUP`, `GAS`, `GAD`, `GEP`), linha de cards compactos `SIGLA` (`X/Y`), sinalizador de bimestres respondidos para Chefe de Setor, eixo X por temporalidade do indicador e correção de alinhamento da linha de meta nos gráficos.
  - `frontend/src/views/ConsolidadoGestao.vue`: Novo layout executivo, botão de impressão de relatório (`Imprimir Relatório`), modo somente-leitura para Gerente/Chefe e destaque visual para feedbacks institucionais.
  - `frontend/src/views/MatrizAcompanhamento.vue`, `frontend/src/views/PlanejamentoAnual.vue`, `frontend/src/views/PreenchimentoBimestral.vue`: Escopo de UORGs conforme hierarquia Divisão/Setor/Gerência e destaque visual acentuado para relatórios com feedback institucional.
- **Testes (`tests/`)**:
  - Atualização e adição de testes automatizados em `tests/test_relatorio_gestao_api.py` cobrindo as novas regras de RBAC hierárquico, restrição de feedback e payload do dashboard.

