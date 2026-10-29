# Spec Delta

## Purpose

Proporciona um layout executivo de alta atratividade para a Visão Consolidada com suporte a impressão de relatório gerencial e aplica destaque visual proeminente aos relatórios que receberam Feedback Institucional em todo o sistema.

## ADDED Requirements

### Requirement: Layout executivo da Visão Consolidada
O sistema SHALL apresentar a página de Visão Consolidada com um design executivo estruturado em resumo gerencial de KPIs, barra de progresso das entregas, cartões comparativos de indicadores com cumprimento de meta e blocos destacados para narrativas de Destaques e Dificuldades.

#### Scenario: Gestor acessa a Visão Consolidada de uma UORG e bimestre
- **WHEN** o usuário seleciona uma UORG e um bimestre na página de Visão Consolidada
- **THEN** o sistema renderiza o cabeçalho executivo da unidade, cartões de resumo do ciclo (taxa de conclusão de entregas, atingimento de metas e status do parecer), lista detalhada de entregas, tabela/cartões de indicadores e seções de Destaques e Dificuldades

### Requirement: Impressão da Visão Consolidada em formato de relatório
O sistema SHALL disponibilizar na página de Visão Consolidada um botão "Imprimir Relatório" que aciona a formatação limpa de impressão institucional contendo cabeçalho oficial do HC-UFPE/EBSERH, dados consolidados da UORG, entregas, indicadores, narrativas e parecer institucional, ocultando menus e controles de navegação.

#### Scenario: Usuário aciona a impressão do relatório consolidado
- **WHEN** o usuário clica no botão "Imprimir Relatório" na página de Visão Consolidada
- **THEN** o sistema aplica o layout de relatório impresso sem elementos de navegação ou botões de formulário e abre a janela de impressão do navegador

### Requirement: Destaque visual para relatórios com Feedback Institucional
O sistema SHALL aplicar destaque visual acentuado (selo de "Parecer Emitido", borda diferenciada e card de destaque executivo) em todos os relatórios bimestrais que possuam Feedback Institucional registrado nas telas de Matriz de Acompanhamento, Visão Consolidada, Preenchimento Bimestral e Dashboard Inicial.

#### Scenario: Visualização de relatório avaliado na Matriz de Acompanhamento e Visão Consolidada
- **WHEN** um relatório bimestral possui parecer institucional registrado
- **THEN** a célula correspondente na Matriz de Acompanhamento e o painel da Visão Consolidada exibem um selo de destaque visual diferenciado dos relatórios apenas enviados sem parecer

