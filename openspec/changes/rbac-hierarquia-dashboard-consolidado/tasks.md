# Tasks

## 1. Backend: Hierarquia Organizacional (Divisão vs. Setor), RBAC e Feedback Institucional

- [x] 1.1 Implementar o mapeamento de hierarquia organizacional (`tipo_uorg: "DIVISAO" | "SETOR"`, `uorg_pai_sigla` e setores subordinados por Divisão) em `src/providers/implementations/relatorio_gestao_sqlite_provider.py` e expor esses metadados em `GET /api/relatorios-gestao/uorgs`, verificando que cada UORG retorna seu tipo e vínculo hierárquico.
- [x] 1.2 Atualizar `src/controllers/relatorio_gestao_controller.py` para restringir `registrar_feedback` exclusivamente aos perfis `SUPERINTENDENTE` e `ADMINISTRADOR` (retornando HTTP 403 para `GERENTE` e `CHEFE`) e aplicar o escopo hierárquico de leitura (Divisão + Setores subordinados para Chefe de Divisão; Gerência + Divisões + Setores subordinados para Gerente) e escrita (restrita à própria UORG para Chefe de Divisão/Setor).
- [x] 1.3 Enriquecer o retorno de `obter_resumo_dashboard` em `src/providers/implementations/relatorio_gestao_sqlite_provider.py` com: (a) `resumo_uorgs_contexto` contendo `{ uorg_id, sigla, nome, gerencia_sigla, concluidas, total }` para cada UORG do contexto filtrado; (b) `bimestres_respondidos` da UORG para sinalização no painel do Chefe de Setor; e (c) série histórica de pontos de cada indicador estruturada de acordo com a sua `periodicidade` (`MENSAL` 12 meses, `BIMESTRAL` 6 bimestres, `TRIMESTRAL` 4 trimestres, `QUADRIMESTRAL` 3 quadrimestres, `SEMESTRAL` 2 semestres).
- [x] 1.4 Adicionar e atualizar os testes automatizados em `tests/test_relatorio_gestao_api.py` cobrindo a restrição de feedback para `GERENTE` (HTTP 403), permissão para `SUPERINTENDENTE`, escopo de Chefe de Divisão vs. Chefe de Setor e os novos campos do endpoint de dashboard, verificando que `pytest` passa integralmente.

## 2. Frontend: Menu Lateral, Rotas e Escopo RBAC por Tipo de Chefia e Perfil

- [x] 2.1 Atualizar `frontend/src/layouts/DefaultLayout.vue` e `frontend/src/router/index.ts` para exibir no menu lateral exatamente os itens permitidos por perfil e tipo de UORG: Chefe de Setor (`Início`, `Planejamento Anual`, `Preenchimento Bimestral`, `Visão Consolidada`), Chefe de Divisão (`Início`, `Planejamento Anual`, `Preenchimento Bimestral`, `Visão Consolidada`, `Matriz de Acompanhamento`), Gerente (`Início`, `Matriz de Acompanhamento`, `Visão Consolidada`), Superintendente (`Início`, `Matriz de Acompanhamento`, `Visão Consolidada`) e Administrador (menu completo).
- [x] 2.2 Ajustar os seletores de UORG em `frontend/src/views/PlanejamentoAnual.vue`, `frontend/src/views/PreenchimentoBimestral.vue`, `frontend/src/views/MatrizAcompanhamento.vue` e `frontend/src/views/ConsolidadoGestao.vue` para respeitar o escopo de cada perfil (Chefe de Divisão edita apenas a própria Divisão no Planejamento/Preenchimento e visualiza Divisão + Setores subordinados na Matriz e Visão Consolidada; Gerente visualiza Divisões e Setores subordinados em modo leitura).

## 3. Frontend: Refinamentos da Tela de Início (`Home.vue`)

- [x] 3.1 Remover a seção de "Atalhos Rápidos de Navegação" de `frontend/src/views/Home.vue` e adicionar o painel de sinalização dos bimestres respondidos para o perfil Chefe de Setor.
- [x] 3.2 Implementar em `frontend/src/views/Home.vue` os botões de filtro rápido de Gerência (`SUP`, `GAS`, `GAD`, `GEP`) para Superintendente e Administrador, o filtro dropdown hierárquico de UORG conforme o perfil e a linha organizada de cards compactos (`SIGLA` + entregas concluídas `X/Y`) exibida no lugar do card maior de entregas sempre que nenhuma UORG específica estiver selecionada.
- [x] 3.3 Atualizar os gráficos de indicadores em `frontend/src/views/Home.vue` para renderizar o eixo X de acordo com a temporalidade (`periodicidade`) de cada indicador e alinhar geometricamente a linha horizontal tracejada da meta com o topo das barras na mesma área de plotagem (`0%` a `100%`), verificando que na `DMED` (indicador de transplantes de córnea realizados, Janeiro = 3, Meta = 3) o topo da coluna de janeiro alinha-se perfeitamente com a linha da meta.

## 4. Frontend: Redesign da Visão Consolidada, Impressão de Relatório e Destaque de Feedback

- [x] 4.1 Reformular o layout de `frontend/src/views/ConsolidadoGestao.vue` com visual executivo atraente para o gestor (KPIs resumidos do ciclo, barras de progresso, cartões comparativos de indicadores e blocos executivos de Destaques e Dificuldades), restringindo o formulário de registro de Parecer Institucional exclusivamente aos perfis `SUPERINTENDENTE` e `ADMINISTRADOR`.
- [x] 4.2 Adicionar o botão "Imprimir Relatório" em `frontend/src/views/ConsolidadoGestao.vue` com estilização `@media print` dedicada e cabeçalho institucional do HC-UFPE/EBSERH para impressão limpa do relatório consolidado.
- [x] 4.3 Aplicar destaque visual acentuado (badges de "Parecer Institucional Emitido", bordas destacadas e banners executivos) aos relatórios que obtiveram feedback institucional em `MatrizAcompanhamento.vue`, `ConsolidadoGestao.vue`, `PreenchimentoBimestral.vue` e `Home.vue`, compilando o frontend (`npm run build`) e validando 100% de conformidade com `python audit_framework.py .`.

## Workflow follow-up

- Sincronizar e arquivar a mudança OpenSpec após validação pelo usuário.

