# Spec Delta

## Purpose

Fornece visão executiva e operacional em tempo real do status de preenchimento dos relatórios de todas as UORGs através da Matriz UORG x Bimestre.

## ADDED Requirements

### Requirement: Matriz visual UORG versus Bimestre
O sistema SHALL renderizar a matriz anual com linhas para UORGs e colunas para bimestres, indicando estados por cores (Enviado, Pendente, etc.).

#### Scenario: Visualização do panorama anual
- **WHEN** o usuário acessa o Dashboard de Acompanhamento
- **THEN** a matriz é exibida com filtros por Gerência e status operacional de cada célula

### Requirement: Visualização consolidada com navegação sequencial
O sistema SHALL fornecer tela consolidada permitindo alternar de forma sequencial entre relatórios de diferentes UORGs do mesmo bimestre (RF-VIS-01).

#### Scenario: Navegação sequencial entre setores
- **WHEN** o gestor clica no botão Próximo Relatório
- **THEN** o sistema carrega o relatório da UORG seguinte mantendo a mesma competência bimestral
