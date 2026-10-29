# Design

## Context

O Portal de Relatórios de Gestão do HC-UFPE/EBSERH opera sobre a arquitetura em 5 camadas do Framework SETISD (FastAPI + SQLite/PostgreSQL + Vue 3/Pinia/Tailwind). Atualmente, o sistema trata todo usuário com perfil `CHEFE` de maneira uniforme (restrito apenas à própria UORG), sem distinguir **Chefe de Divisão** (que supervisiona Setores subordinados) de **Chefe de Setor**. Além disso, no Dashboard (`Home.vue`), a linha tracejada de meta e as barras dos gráficos usam referenciais de altura distintos (container com `pt-6 pb-2` + texto no fluxo flex vs. posicionamento absoluto `bottom: X%`), causando desalinhamento visual quando o valor apurado é idêntico à meta (ex.: `DMED` — Transplantes de Córnea em Janeiro = `3`, Meta = `3`).

Consulte `proposal.md` para a motivação completa e `specs/` para os contratos de comportamento.

## Goals / Non-Goals

**Goals:**
- Implementar a distinção hierárquica entre **Divisão** e **Setor**, mapeando os Setores subordinados a cada Divisão do HC-UFPE sem necessidade de migração destrutiva do banco SQLite já populado com dados do REDCap.
- Adequar o menu lateral (`DefaultLayout.vue`), as rotas (`router/index.ts`) e os filtros de escopo no backend/frontend para os 5 papéis operacionais: Chefe de Setor, Chefe de Divisão, Gerente, Superintendente e Administrador.
- Restringir o registro de Pareceres e Feedbacks Institucionais exclusivamente aos perfis `SUPERINTENDENTE` e `ADMINISTRADOR`.
- Reformular o Dashboard (`Home.vue`): remover atalhos rápidos, adicionar filtros de gerência (`SUP`, `GAS`, `GAD`, `GEP`), exibir linha de cards compactos `SIGLA` (`X/Y`) quando nenhuma UORG estiver selecionada, sinalizar bimestres respondidos para Chefe de Setor, estruturar o eixo X de cada gráfico segundo a temporalidade do indicador e alinhar geometricamente a linha de meta com o topo das barras.
- Elevar o padrão visual executivo da Visão Consolidada (`ConsolidadoGestao.vue`) com suporte nativo à impressão de relatório (`window.print()` + `@media print`) e destacar relatórios com Feedback Institucional em todo o sistema.

**Non-Goals:**
- Alterar o motor de autenticação AD/LDAP ou os endpoints públicos de saúde (`/api/health`).
- Introduzir bibliotecas pesadas de geração de PDF no backend (a impressão utilizará a engine vetorial nativa do navegador via CSS `@media print` de alta precisão).

## Decisions

### 1. Mapeamento Hierárquico Divisão → Setores Subordinados
- **Decisão**: Definir no backend (`src/providers/implementations/relatorio_gestao_sqlite_provider.py` e helper compartilhado) o mapeamento canônico da estrutura organizacional do HC-UFPE/EBSERH, enriquecendo os objetos de UORG retornados pela API com:
  - `tipo_uorg`: `"DIVISAO"` (quando `sigla` pertence a `{"DAF", "DLI", "DIVGP", "DADT", "DGC", "DMED", "DENF"}` ou `nome` inicia com `"Divisão"`) ou `"SETOR"` (demais unidades).
  - `uorg_pai_sigla` e lista de `subordinados_ids`:
    - `DAF` → `["SAD", "SGOF", "SCONT"]`
    - `DLI` → `["STEC", "STIF", "SAFS", "STHH"]`
    - `DIVGP` → `[]`
    - `DADT` → `["STFH", "SADT"]`
    - `DGC` → `["STPC"]`
    - `DMED` → `[]`
    - `DENF` → `[]`
- **Alternativas consideradas**: Adicionar coluna `uorg_pai_id` via migração Alembic obrigatória. Descartada como dependência bloqueante porque o mapa canônico em código funciona imediatamente sobre bancos existentes e testes em memória, mantendo total determinismo.

### 2. Escopo de Dados por Perfil e Operação (Leitura vs. Escrita)
- **Decisão**: Separar no `RelatorioGestaoController` a validação de escopo em dois níveis:
  1. **Escopo de Escrita (`Planejamento Anual` e `Preenchimento Bimestral`)**:
     - `CHEFE` (seja de Setor ou de Divisão): pode editar **apenas** a sua própria UORG (`user_uorg_id`).
     - `ADMINISTRADOR`: pode editar qualquer UORG.
     - `GERENTE` e `SUPERINTENDENTE`: não realizam preenchimento ou planejamento de UORG (somente leitura/acompanhamento).
  2. **Escopo de Leitura (`Dashboard`, `Visão Consolidada`, `Matriz de Acompanhamento`)**:
     - `CHEFE` de Setor: apenas o próprio Setor.
     - `CHEFE` de Divisão: a própria Divisão + Setores subordinados a ela.
     - `GERENTE`: todas as UORGs (Divisões e Setores) vinculadas à sua Gerência.
     - `SUPERINTENDENTE` e `ADMINISTRADOR`: todas as UORGs do hospital.
  3. **Escopo de Feedback Institucional (`POST /api/relatorios-gestao/relatorio/feedback`)**:
     - Permitido **exclusivamente** para `SUPERINTENDENTE` e `ADMINISTRADOR` (retornando HTTP 403 para `GERENTE` e `CHEFE`).

### 3. Alinhamento Geométrico da Linha de Meta e Eixo X Temporal nos Gráficos (`Home.vue`)
- **Decisão**:
  - **Referencial Único de Altura (0% a 100%)**: Construir a área de plotagem do gráfico dentro de um container dedicado `<div class="relative h-32 w-full">` **sem padding vertical** (`py-0`), reservando uma faixa superior externa (`pt-6`) apenas para que os rótulos flutuantes acima de `100%` não sejam cortados. Dentro do container `h-32`:
    - O valor máximo da escala é `maxScale = Math.max(meta_valor * 1.25, max(valores_apurados) * 1.15, 1)`.
    - A função `calcularPercentualEscala(valor, ind)` retorna exatamente `Math.min(100, Math.max(0, (valor / maxScale) * 100))` **sem piso artificial de 10%** para valores positivos (usando `min-h-[2px]` apenas quando `valor == 0`).
    - A linha horizontal tracejada da meta é posicionada com `style="{ bottom: `${calcularPercentualEscala(ind.meta_valor, ind)}%` }"` e `border-t-2 border-dashed`, de modo que a borda da meta fique exatamente na coordenada `Y = pct%`.
    - Cada barra é posicionada na base (`bottom: 0`) com `style="{ height: `${calcularPercentualEscala(ponto.valor_apurado, ind)}%` }"`, e o rótulo do valor apurado é posicionado absolutamente acima da barra (`bottom: ${pct}%`). Assim, quando `valor_apurado == meta_valor`, o topo da coluna coincide exatamente com a linha tracejada da meta.
  - **Série Temporal no Eixo X conforme `periodicidade`**:
    - O endpoint `/api/relatorios-gestao/dashboard` retornará para cada indicador os pontos estruturados conforme a sua `periodicidade`:
      - `MENSAL`: 12 pontos (`Jan`, `Fev`, `Mar`, `Abr`, `Mai`, `Jun`, `Jul`, `Ago`, `Set`, `Out`, `Nov`, `Dez`) extraídos de `valor_mes_1` e `valor_mes_2` de cada um dos 6 bimestres.
      - `BIMESTRAL`: 6 pontos (`1ºB`, `2ºB`, `3ºB`, `4ºB`, `5ºB`, `6ºB`).
      - `TRIMESTRAL`: 4 pontos (`1ºT`, `2ºT`, `3ºT`, `4ºT`, correspondentes aos bimestres 2, 3, 5 e 6).
      - `QUADRIMESTRAL`: 3 pontos (`1ºQ`, `2ºQ`, `3ºQ`, correspondentes aos bimestres 2, 4 e 6).
      - `SEMESTRAL`: 2 pontos (`1ºS`, `2ºS`, correspondentes aos bimestres 3 e 6).

### 4. Cards Compactos `SIGLA (X/Y)` quando Nenhuma UORG está Selecionada
- **Decisão**: O payload de `/api/relatorios-gestao/dashboard` incluirá a lista `resumo_uorgs_contexto: [{ uorg_id, sigla, nome, gerencia_sigla, concluidas, total }]` respeitando o filtro de gerência/contexto ativo. Quando `uorgSelecionada` for vazia (`""`), `Home.vue` ocultará o card grande de listagem de entregas e exibirá uma grade/linha organizada de cards compactos clicáveis mostrando a `sigla` da UORG e o badge `X/Y` de entregas concluídas.

### 5. Redesign da Visão Consolidada e Impressão de Relatório
- **Decisão**: Em `ConsolidadoGestao.vue`, adicionar cabeçalho executivo com KPIs do relatório (Entregas Concluídas `X/Y`, Indicadores Dentro da Meta, Status de Envio e Selo de Feedback Institucional) e botão **"Imprimir Relatório"** que aciona `window.print()`. Uma folha de estilos `@media print` ocultará a sidebar, topbar, seletores de filtro e botões de ação, formatando o documento em padrão A4 institucional do HC-UFPE/EBSERH.

## Risks / Trade-offs

- **[Risk] Chefe de Divisão com subordinação implícita em UORGs assistenciais (`DGC`, `DMED`, `DENF`)** → **Mitigation**: Na `GAS`, `DADT` possui `STFH` e `SADT` claramente subordinados; `DGC`, `DMED` e `DENF` terão `STPC`, `SADT` e `STFH` mapeados conforme a hierarquia assistencial da `GAS` para que qualquer Chefe de Divisão tenha setores subordinados disponíveis para filtro e acompanhamento.
- **[Risk] Gráficos mensais com 12 colunas em telas menores** → **Mitigation**: Ajustar a largura e o espaçamento das colunas (`gap-1.5` para 12 meses vs. `gap-3` para períodos menores) garantindo legibilidade perfeita de `Jan` a `Dez`.

