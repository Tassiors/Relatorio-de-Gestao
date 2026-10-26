# Spec Delta

## Purpose

Gerencia a emissão de parecer e feedback institucional aos relatórios bimestrais, com permissão concedida a Superintendente e Administrador.

## ADDED Requirements

### Requirement: Emissão de feedback por Superintendente e Administrador
O sistema SHALL permitir que usuários com perfil Superintendente ou Administrador registrem feedback institucional para a UORG (decisão validada).

#### Scenario: Administrador emite feedback institucional
- **WHEN** o Administrador ou Superintendente insere parecer em relatório enviado
- **THEN** o sistema persiste o feedback, gera notificação para a UORG e bloqueia edição pelo Chefe

### Requirement: Imutabilidade por perfis subordinados
O sistema SHALL impedir estritamente que Chefes de UORG alterem ou excluam qualquer feedback institucional recebido (RN-FBK-01).

#### Scenario: Chefe visualiza feedback recebido
- **WHEN** o Chefe da UORG acessa o relatório com feedback
- **THEN** o parecer é exibido em modo estritamente somente leitura
