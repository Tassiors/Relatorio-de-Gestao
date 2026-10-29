# dashboard-inicio Specification

## Purpose
Fornece um painel inicial dinâmico com métricas consolidadas de entregas, atalhos operacionais inteligentes orientados a perfil e visualização hierárquica de entregas e metas de indicadores por UORG.

## Requirements

### Requirement: Cards resumidos e indicadores de progresso
O sistema SHALL exibir no dashboard inicial os cards consolidados de Entregas e Bimestre Vigente, eliminando cards obsoletos de UORGs e Gerências. O card de Entregas deve apresentar o total e o percentual de entregas concluídas. O card de Bimestre Vigente deve funcionar como atalho interativo para a tela de gestão do exercício exclusivamente para Administradores.

#### Scenario: Visualização do card de entregas com percentual
- **WHEN** qualquer usuário autenticado acessa a tela de início
- **THEN** o card de Entregas exibe o total cadastrado, o total concluído e a porcentagem calculada de conclusão (ex: 75%)

#### Scenario: Administrador clica no card de Bimestre Vigente
- **WHEN** um usuário com perfil ADMINISTRADOR clica no card do Bimestre Vigente
- **THEN** o sistema redireciona a navegação para a tela de Gestão do Exercício

#### Scenario: Usuário comum visualiza card de Bimestre Vigente
- **WHEN** um usuário não-administrador visualiza o card de Bimestre Vigente
- **THEN** o card é exibido apenas como informação estática de leitura, sem comportamento ou cursor de link de navegação

### Requirement: Atalhos operacionais orientados a perfis
O sistema SHALL disponibilizar botões de atalho rápido para as funcionalidades centrais do sistema, exibindo cada atalho conforme as permissões do perfil do usuário autenticado.

#### Scenario: Exibição de atalhos para perfil Administrador
- **WHEN** o usuário com perfil ADMINISTRADOR acessa a tela de início
- **THEN** o sistema exibe os atalhos para "Matriz de Acompanhamento Anual", "Preenchimento Bimestral", "Visão Consolidada e Feedback" e "Gestão do Exercício e Prazos"

#### Scenario: Exibição de atalhos para perfil Chefe de Unidade
- **WHEN** o usuário com perfil CHEFE acessa a tela de início
- **THEN** o sistema exibe atalhos para "Preenchimento Bimestral" e "Matriz de Acompanhamento Anual", ocultando o atalho de "Gestão do Exercício e Prazos"

### Requirement: Seletor hierárquico de UORG e painel integrado
O sistema SHALL disponibilizar no dashboard um dropdown de seleção de UORG respeitando a hierarquia institucional (Superintendente pode selecionar qualquer UORG; demais usuários apenas unidades subordinadas ou a própria). Ao selecionar, o painel deve renderizar o status das entregas e gráficos com as metas dos indicadores.

#### Scenario: Superintendente seleciona qualquer UORG
- **WHEN** o usuário com perfil SUPERINTENDENTE abre o dropdown de UORGs
- **THEN** o sistema lista todas as unidades organizacionais do hospital para livre seleção e análise

#### Scenario: Gestor visualiza apenas unidades subordinadas
- **WHEN** um usuário com perfil GERENTE ou CHEFE abre o dropdown de UORGs
- **THEN** o sistema lista estritamente a sua UORG e as unidades sob sua subordinação hierárquica

#### Scenario: Painel atualiza entregas e gráficos após seleção de UORG
- **WHEN** o usuário seleciona uma UORG válida no dropdown
- **THEN** o sistema carrega e exibe as entregas cadastradas com seus respectivos status, além de gráficos individuais para cada indicador anual com sua linha de meta

