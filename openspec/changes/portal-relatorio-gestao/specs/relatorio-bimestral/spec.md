# Spec Delta

## Purpose

Gerencia o ciclo operacional de preenchimento, rascunho automático, validação de integridade, envio formal, reenvio e exportação do relatório.

## ADDED Requirements

### Requirement: Salvamento automático e persistência de rascunho
O sistema SHALL salvar automaticamente o progresso do relatório a cada interação, permitindo que o Chefe retome o preenchimento sem perda de dados.

#### Scenario: Chefe retoma rascunho
- **WHEN** o usuário acessa o relatório em andamento
- **THEN** o sistema carrega o rascunho com os valores salvos e destaca pendências obrigatórias

### Requirement: Envio formal e controle de edição
O sistema SHALL validar todos os campos obrigatórios antes do envio formal e permitir edição enquanto o prazo regular estiver aberto (RF-REL-09/10).

#### Scenario: Reenvio de relatório dentro do prazo
- **WHEN** o Chefe edita um relatório já enviado e clica em reenviar antes do fechamento
- **THEN** o sistema atualiza a versão arquivando histórico de alterações com data e IP

### Requirement: Exportação para PDF e Excel
O sistema SHALL permitir a exportação dos dados do relatório bimestral e consolidados em formatos PDF e planilha Excel (decisão validada).

#### Scenario: Usuário clica em exportar relatório
- **WHEN** o usuário solicita exportação em formato PDF ou Excel
- **THEN** o sistema gera e disponibiliza o download do arquivo formatado institucionalmente
