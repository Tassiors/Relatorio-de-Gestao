# Spec Delta

## Purpose

Permite o registro e acompanhamento de fatos relevantes (Destaques) e entraves operacionais (Dificuldades) em cada relatório bimestral.

## ADDED Requirements

### Requirement: Registro de campos textuais estruturados
O sistema SHALL disponibilizar campos textuais dedicados para Destaques e Dificuldades do bimestre com suporte a rascunho e validação de tamanho.

#### Scenario: Chefe preenche destaques e dificuldades
- **WHEN** o Chefe insere os textos no relatório bimestral
- **THEN** as informações são persistidas no rascunho e vinculadas ao envio da competência

### Requirement: Visualização na linha do tempo
O sistema SHALL permitir a consulta cronológica dos destaques e dificuldades reportados pela UORG ao longo de todos os bimestres.

#### Scenario: Gestor consulta histórico de entraves
- **WHEN** o Superintendente ou Gerente visualiza o painel da UORG
- **THEN** o sistema exibe os destaques e dificuldades organizados por ordem cronológica de bimestre
