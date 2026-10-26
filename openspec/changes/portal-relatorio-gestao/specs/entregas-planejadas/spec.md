# Spec Delta

## Purpose

Gerencia as entregas institucionais pactuadas no início do exercício por cada UORG e controla a sua conclusão única ao longo dos bimestres.

## ADDED Requirements

### Requirement: Cadastro de entregas durante planejamento
O sistema SHALL permitir que o Chefe da UORG cadastre a quantidade pactuada de entregas durante a janela de planejamento do exercício.

#### Scenario: Chefe cadastra meta de entregas
- **WHEN** o Chefe submete as entregas planejadas no período de planejamento
- **THEN** as entregas ficam associadas à sua UORG para o exercício em questão

### Requirement: Conclusão única de entrega em relatório bimestral
O sistema SHALL permitir marcar a entrega como concluída apenas uma vez, registrando competência, data e usuário responsável (RN-ENT-01/02).

#### Scenario: Entrega concluída não reaparece em bimestres futuros
- **WHEN** o Chefe conclui uma entrega no 2º Bimestre
- **THEN** essa entrega deixa de ser ofertada como pendente para os bimestres subsequentes do mesmo exercício
