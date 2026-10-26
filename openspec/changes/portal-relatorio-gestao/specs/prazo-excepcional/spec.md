# Spec Delta

## Purpose

Permite a concessão administrativa de prazo excepcional para UORGs após encerramento do bimestre regular, com obrigatoriedade de justificativa.

## ADDED Requirements

### Requirement: Concessão com justificativa formal obrigatória
O sistema SHALL exigir o preenchimento compulsório do motivo ao conceder prazo excepcional a uma UORG (decisão validada / Seção 22).

#### Scenario: Tentativa de concessão sem motivo
- **WHEN** o Administrador tenta liberar prazo excepcional sem preencher o motivo
- **THEN** o sistema rejeita a operação com erro de validação informando que a justificativa é obrigatória

### Requirement: Escopo restrito e encerramento automático
O sistema SHALL liberar edição exclusivamente para a UORG contemplada, mantendo o bimestre fechado para as demais (RF-PEX-03/06).

#### Scenario: UORG com prazo excepcional ativo
- **WHEN** a UORG contemplada acessa o portal durante a vigência do prazo excepcional
- **THEN** a interface habilita edição do relatório específico exibindo banner de aviso do prazo
