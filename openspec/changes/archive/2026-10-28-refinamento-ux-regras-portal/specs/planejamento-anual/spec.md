# Spec Delta: planejamento-anual

## MODIFIED Requirements

### Requirement: Cadastro de indicadores com validação de limites
O sistema SHALL permitir o cadastro de no mínimo 1 e no máximo 3 indicadores ativos por UORG, validando nome, meta numérica, operador, unidade de medida selecionada exclusivamente via dropdown com opções padronizadas e periodicidade.

#### Scenario: Inclusão válida de indicador
- **WHEN** o Chefe cadastra indicador selecionando uma unidade de medida válida a partir da lista suspensa (dropdown), informa meta numérica, operador válido (>=, <=, =, ENTRE) e periodicidade
- **THEN** o sistema grava o indicador vinculado à UORG com sucesso

#### Scenario: Limite máximo de indicadores excedido
- **WHEN** a UORG já possui 3 indicadores ativos e o usuário tenta cadastrar o quarto indicador
- **THEN** o sistema SHALL rejeitar o cadastro com HTTP 400 informando que o limite de 3 indicadores foi atingido

### Requirement: Controle da janela de planejamento pelo Administrador
O sistema SHALL permitir que apenas usuários com perfil ADMINISTRADOR visualizem os controles de ação e abram ou encerrem a janela de planejamento anual do exercício.

#### Scenario: Administrador abre janela de planejamento
- **WHEN** o Administrador altera o status do exercício para PLANEJAMENTO
- **THEN** o sistema atualiza o status do exercício e libera o cadastro para todas as UORGs

#### Scenario: Usuário comum tenta alterar status do exercício
- **WHEN** um usuário com perfil CHEFE ou GERENTE tenta alterar o status do exercício
- **THEN** o sistema SHALL negar a ação com HTTP 403 Forbidden
