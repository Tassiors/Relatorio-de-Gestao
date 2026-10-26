# Spec Delta

## Purpose

Gerencia a estrutura hierárquica do HC-UFPE (Gerências e Unidades Organizacionais - UORGs), garantindo isolamento histórico de exercícios.

## ADDED Requirements

### Requirement: Carga inicial e persistência de Gerências e UORGs
O sistema SHALL persistir a árvore organizacional com 4 Gerências e 23 UORGs mapeadas no REDCap e permitir ativação e inativação pelo Administrador.

#### Scenario: Consulta de unidades organizacionais ativas
- **WHEN** usuário autenticado requisita a listagem de UORGs
- **THEN** o sistema retorna as UORGs ativas agrupadas por sua respectiva Gerência

### Requirement: Imutabilidade histórica da estrutura organizacional
O sistema SHALL impedir que alterações estruturais ou renomeações afetem retrospectivamente relatórios e exercícios passados (RN-ORG-01).

#### Scenario: Edição de UORG preserva histórico anterior
- **WHEN** uma UORG é renomeada ou inativada no exercício corrente
- **THEN** relatórios de exercícios anteriores mantêm o vínculo e o nome vigentes à época da submissão
