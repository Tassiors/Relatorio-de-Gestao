# Spec Delta

## ADDED Requirements

### Requirement: Sinalização de bimestres respondidos para Chefe de Setor
O sistema SHALL exibir no dashboard da tela de Início do Chefe de Setor um painel sinalizando quais bimestres do exercício vigente já foram respondidos (enviados ou avaliados) e quais estão pendentes ou em rascunho.

#### Scenario: Chefe de Setor visualiza bimestres respondidos no dashboard
- **WHEN** um usuário Chefe de Setor acessa a tela de Início
- **THEN** o dashboard exibe os 6 bimestres do ano com sinalização visual clara para os bimestres já respondidos pela sua unidade

### Requirement: Linha de cards compactos de entregas por UORG quando nenhuma unidade está selecionada
O sistema SHALL suprimir o card maior de listagem detalhada de entregas quando nenhuma UORG específica estiver selecionada no filtro do dashboard e exibir, em seu lugar, uma linha organizada de cards menores contendo apenas a sigla de cada UORG no contexto e o respectivo número de entregas concluídas no formato `X/Y` (onde `X` é o total concluído e `Y` é o total de entregas da UORG).

#### Scenario: Visualização sem UORG selecionada por Chefe de Divisão, Gerente, Superintendente ou Administrador
- **WHEN** um usuário com perfil Chefe de Divisão, Gerente, Superintendente ou Administrador acessa o dashboard sem selecionar uma UORG específica no dropdown
- **THEN** o sistema oculta o card maior de entregas e renderiza uma linha organizada de cards compactos exibindo a sigla de cada UORG do contexto filtrado e a fração `X/Y` de entregas concluídas

#### Scenario: Seleção de UORG específica restaura o card detalhado de entregas
- **WHEN** o usuário seleciona uma UORG específica no filtro ou clica em um dos cards compactos de sigla da UORG
- **THEN** o sistema exibe o card detalhado com a lista de entregas planejadas e os gráficos de indicadores daquela UORG

### Requirement: Eixo X por temporalidade e alinhamento exato da linha de meta nos gráficos
O sistema SHALL organizar o eixo X de cada gráfico de indicador no dashboard estritamente de acordo com a temporalidade cadastrada do indicador (Mensal, Bimestral, Trimestral, Quadrimestral ou Semestral) e posicionar a linha horizontal tracejada da meta na mesma escala geométrica das barras para que uma coluna cujo valor apurado seja igual à meta fique perfeitamente alinhada com a linha da meta.

#### Scenario: Exibição do eixo X conforme a temporalidade do indicador
- **WHEN** o dashboard renderiza gráficos de indicadores com periodicidades distintas (ex: Mensal e Trimestral)
- **THEN** o gráfico do indicador mensal exibe os pontos mensais no eixo X (Jan a Dez) e o gráfico do indicador trimestral exibe os pontos trimestrais (1ºT a 4ºT)

#### Scenario: Alinhamento exato entre o topo da coluna e a linha da meta
- **WHEN** um indicador possui meta igual a 3 e o valor apurado em determinado período (ex: mês de janeiro na DMED) é igual a 3
- **THEN** o topo da coluna referente a janeiro fica perfeitamente alinhado com a linha horizontal tracejada da meta, sem ultrapassá-la ou ficar abaixo dela

## MODIFIED Requirements

### Requirement: Seletor hierárquico de UORG e painel integrado
O sistema SHALL disponibilizar no dashboard filtros de UORG respeitando o perfil e a hierarquia institucional: botões de filtro rápido com as siglas das gerências (`SUP`, `GAS`, `GAD`, `GEP`) combinados com dropdown de qualquer UORG para Superintendente e Administrador; dropdown com a própria gerência, divisões e setores subordinados para Gerente; e dropdown com a própria divisão e setores subordinados para Chefe de Divisão.

#### Scenario: Superintendente seleciona qualquer UORG
- **WHEN** o usuário com perfil SUPERINTENDENTE ou ADMINISTRADOR acessa a tela de Início
- **THEN** o dashboard exibe botões de filtro para `SUP`, `GAS`, `GAD` e `GEP` e um dropdown listando todas as unidades organizacionais do hospital para livre seleção

#### Scenario: Gestor visualiza apenas unidades subordinadas
- **WHEN** um usuário com perfil GERENTE ou CHEFE de Divisão abre o dropdown de UORGs no dashboard
- **THEN** o sistema lista estritamente a sua própria unidade e as divisões/setores sob sua subordinação hierárquica

#### Scenario: Painel atualiza entregas e gráficos após seleção de UORG
- **WHEN** o usuário seleciona uma UORG válida no dropdown
- **THEN** o sistema carrega e exibe as entregas cadastradas com seus respectivos status, além de gráficos individuais para cada indicador anual com eixo X na temporalidade do indicador e linha de meta alinhada

## REMOVED Requirements

### Requirement: Atalhos operacionais orientados a perfis
**Reason**: A navegação principal já está permanentemente acessível e filtrada por perfil no menu lateral, tornando a seção de atalhos rápidos na tela de Início redundante e ocupando espaço nobre do dashboard analítico.
**Migration**: Utilizar os links diretos disponíveis no menu lateral esquerdo conforme o perfil do usuário autenticado.
