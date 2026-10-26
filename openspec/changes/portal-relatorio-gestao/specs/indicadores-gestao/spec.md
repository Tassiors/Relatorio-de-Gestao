# Spec Delta

## Purpose

Padroniza o cadastro de indicadores de gestão por UORG, suportando múltiplas periodicidades, metas numéricas com operadores e indisponibilidade justificada.

## ADDED Requirements

### Requirement: Cadastro de indicador com operador de meta flexível
O sistema SHALL permitir cadastro de indicadores com operadores de meta >=, <=, = e operador de faixa/intervalo min-max (decisão validada).

#### Scenario: Indicador com meta de faixa
- **WHEN** o indicador é cadastrado com operador de faixa entre 80% e 90%
- **THEN** o sistema valida o atingimento quando o resultado informado estiver contido no intervalo inclusivo

### Requirement: Registro de resultado com indisponibilidade justificada
O sistema SHALL permitir que a UORG registre ausência de resultado para o período apenas mediante preenchimento de justificativa formal (RF-IND-08/09).

#### Scenario: Resultado pendente justificado
- **WHEN** o Chefe sinaliza resultado indisponível e preenche a justificativa
- **THEN** o sistema aceita o envio classificando o indicador como indisponibilidade justificada e não como omissão
