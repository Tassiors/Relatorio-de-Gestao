# gestao-exercicio Specification

## Purpose
Disponibiliza ao Administrador controle flexível e manual do ciclo de bimestres, parametrização direta de datas de corte e simplificação da concessão de prazos excepcionais.

## Requirements

### Requirement: Controle manual de status e data de corte de bimestres
O sistema SHALL permitir que o Administrador altere manualmente o status (ABERTO ou FECHADO) de qualquer bimestre do exercício e defina manualmente a data limite de fechamento, sem encerramento automático cego por virada de relógio às 23h59.

#### Scenario: Administrador abre ou fecha bimestre manualmente
- **WHEN** o Administrador altera o status de um bimestre e clica em salvar
- **THEN** o sistema atualiza o status do bimestre e grava o registro na trilha de auditoria

#### Scenario: Administrador ajusta data limite de fechamento
- **WHEN** o Administrador define uma nova data limite para o encerramento das submissões do bimestre aberto
- **THEN** o sistema adota a nova data informada como marco de referência operacional

### Requirement: Concessão de prazo excepcional com justificativa opcional
O sistema SHALL permitir a concessão de prazo excepcional para UORGs sem obrigatoriedade de preenchimento do campo de motivo/justificativa, mantendo o registro auditável da liberação.

#### Scenario: Administrador concede prazo excepcional sem informar motivo
- **WHEN** o Administrador seleciona uma UORG, define a data fim do prazo excepcional e envia o formulário deixando o motivo em branco
- **THEN** o sistema SHALL conceder o prazo excepcional com sucesso, registrando o evento na tabela de auditoria com motivo nulo ou padrão

#### Scenario: Posicionamento do texto orientativo na seção de prazo excepcional
- **WHEN** o usuário visualiza a seção "Conceder Prazo Excepcional" na tela de Gestão do Exercício
- **THEN** a interface exibe o texto explicativo sobre o funcionamento e impacto da concessão diretamente integrado ao bloco de concessão

