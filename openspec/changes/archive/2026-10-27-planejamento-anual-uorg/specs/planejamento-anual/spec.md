# Spec Delta

## Purpose

Permite que as Chefias de Unidades Organizacionais (UORGs) e Administradores cadastrem e gerenciem anualmente as entregas e indicadores estratégicos durante a janela de planejamento do exercício.

## ADDED Requirements

### Requirement: Consulta de planejamento da UORG
O sistema SHALL permitir consultar todas as entregas e indicadores cadastrados para a UORG no exercício, incluindo status da janela de planejamento.

#### Scenario: Chefe consulta planejamento de sua UORG
- **WHEN** o usuário com perfil CHEFE autenticado consulta o planejamento de sua própria UORG
- **THEN** o sistema retorna a lista de entregas e indicadores ativos e o status da janela de planejamento anual

#### Scenario: Chefe tenta consultar UORG alheia
- **WHEN** o usuário com perfil CHEFE tenta consultar o planejamento de uma UORG diferente da sua
- **THEN** o sistema SHALL rejeitar a requisição com código HTTP 403 Forbidden

### Requirement: Cadastro de nova entrega planejada
O sistema SHALL permitir o cadastro de novas entregas planejadas para a UORG quando a janela de planejamento anual estiver aberta.

#### Scenario: Inclusão de entrega com sucesso
- **WHEN** o Chefe da UORG ou Administrador submete título e descrição de nova entrega durante a janela de planejamento aberta
- **THEN** o sistema cadastra a entrega associada à UORG e ao exercício ativo, registrando auditoria imutável

#### Scenario: Tentativa de cadastro com janela fechada
- **WHEN** o Chefe da UORG tenta cadastrar uma entrega com o exercício em status de execução normal ou encerrado
- **THEN** o sistema SHALL bloquear o cadastro e retornar erro HTTP 400 informando que o planejamento anual está encerrado

### Requirement: Edição e inativação de entregas
O sistema SHALL permitir a edição do título e a inativação lógica de entregas planejadas que ainda não tenham sido concluídas em relatórios passados.

#### Scenario: Edição de entrega na janela aberta
- **WHEN** o usuário autorizado altera o texto da entrega enquanto a janela estiver aberta
- **THEN** o sistema atualiza os dados e registra auditoria com dados anteriores e novos

#### Scenario: Inativação de entrega (soft delete)
- **WHEN** o usuário solicita a remoção de uma entrega planejada
- **THEN** o sistema marca o registro como inativo (ativo = False) preservando a integridade histórica

### Requirement: Cadastro de indicadores com validação de limites
O sistema SHALL permitir o cadastro de no mínimo 1 e no máximo 3 indicadores ativos por UORG, validando nome, meta numérica, operador, unidade e periodicidade.

#### Scenario: Inclusão válida de indicador
- **WHEN** o Chefe cadastra indicador com meta numérica, operador válido (>=, <=, =, ENTRE) e periodicidade
- **THEN** o sistema grava o indicador vinculado à UORG com sucesso

#### Scenario: Limite máximo de indicadores excedido
- **WHEN** a UORG já possui 3 indicadores ativos e o usuário tenta cadastrar o quarto indicador
- **THEN** o sistema SHALL rejeitar o cadastro com HTTP 400 informando que o limite de 3 indicadores foi atingido

### Requirement: Controle da janela de planejamento pelo Administrador
O sistema SHALL permitir que apenas usuários com perfil ADMINISTRADOR abram ou encerrem a janela de planejamento anual do exercício.

#### Scenario: Administrador abre janela de planejamento
- **WHEN** o Administrador altera o status do exercício para PLANEJAMENTO
- **THEN** o sistema atualiza o status do exercício e libera o cadastro para todas as UORGs

#### Scenario: Usuário comum tenta alterar status do exercício
- **WHEN** um usuário com perfil CHEFE ou GERENTE tenta alterar o status do exercício
- **THEN** o sistema SHALL negar a ação com HTTP 403 Forbidden
