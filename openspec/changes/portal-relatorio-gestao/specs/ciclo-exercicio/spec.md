# Spec Delta

## Purpose

Controla o ciclo de vida anual do exercício de gestão, parametrização do calendário de 6 bimestres e regras de planejamento.

## ADDED Requirements

### Requirement: Criação e configuração de exercício anual
O sistema SHALL permitir que o Administrador crie um novo exercício anual definindo datas de início e fim, participantes e regras gerais.

#### Scenario: Administrador cadastra exercício 2026
- **WHEN** o Administrador cria o exercício 2026 com 6 bimestres
- **THEN** o sistema inicializa o calendário operacional e disponibiliza a janela de planejamento

### Requirement: Isolamento de dados por exercício
O sistema SHALL garantir isolamento completo entre exercícios, impedindo que um novo ano sobrescreva dados históricos (RN-EXE-01).

#### Scenario: Acesso a exercícios anteriores
- **WHEN** qualquer usuário consulta relatórios de anos anteriores
- **THEN** os dados são exibidos em modo somente leitura correspondendo exatamente ao estado arquivado
