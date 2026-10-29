# preenchimento-bimestral Specification

## Purpose
Garante uma experiência de preenchimento bimestral lúdica, inspiradora e orientada por regras automáticas de cascata em entregas e aderência estrita à periodicidade de indicadores.

## Requirements

### Requirement: Efeito cascata para entregas concluídas
O sistema SHALL propagar automaticamente o status "CONCLUÍDA" de uma entrega planejada para todos os bimestres subsequentes do mesmo exercício quando ela for reportada como concluída em um ciclo anterior ou atual.

#### Scenario: Gestor marca entrega como concluída
- **WHEN** o gestor define o status de uma entrega como CONCLUIDA no 2º bimestre e salva o relatório
- **THEN** o sistema marca a entrega como concluída nos bimestres subsequentes (3º, 4º, 5º e 6º bimestres), mantendo a rastreabilidade do ciclo de conclusão

#### Scenario: Visualização de entrega concluída em ciclo posterior
- **WHEN** o gestor acessa o formulário de preenchimento do 3º bimestre com entrega concluída no 2º bimestre
- **THEN** a entrega aparece com indicação visual de concluída previamente, dispensando reavaliação ou preenchimento redundante

### Requirement: Motor de periodicidade e orientações contextuais de indicadores
O sistema SHALL exibir campos de preenchimento de indicadores estritamente conforme sua periodicidade cadastrada (mensal, bimestral, trimestral, quadrimestral, semestral), apresentando orientações textuais claras sobre competência e quantidade de valores esperados.

#### Scenario: Preenchimento de indicador mensal
- **WHEN** o formulário é carregado para um bimestre (ex: 2º BI) contendo indicador com periodicidade mensal
- **THEN** o sistema exibe dois campos de valores distintos (ex: março e abril) acompanhados de mensagem instrutiva clara

#### Scenario: Preenchimento de indicador trimestral nos bimestres de fechamento
- **WHEN** o usuário abre o relatório de um bimestre de encerramento trimestral (2º, 3º, 5º ou 6º BI)
- **THEN** o sistema exibe o campo para inserção do resultado do trimestre correspondente com instrução contextualizada

#### Scenario: Indicador não aplicável ao bimestre vigente
- **WHEN** o indicador possui periodicidade semestral e o formulário aberto é o 1º ou 2º bimestre
- **THEN** o sistema exibe o indicador como "Não aplicável a este bimestre", sem sinalizar pendência impeditiva de envio

#### Scenario: Registro de resultado indisponível justificado
- **WHEN** o gestor seleciona a opção de resultado ainda não disponível para um indicador aplicável
- **THEN** o sistema exige justificativa textual sucinta e não bloqueia a finalização do relatório por ausência de valor numérico

### Requirement: Interface inspiradora e lúdica para destaques e dificuldades
O sistema SHALL apresentar as seções de Destaques e Dificuldades com visual moderno, acolhedor e dinâmico, incorporando ícones expressivos, orientações inspiradoras e contadores de caracteres para valorizar a reflexão de gestão da unidade.

#### Scenario: Gestor interage com seção de Destaques
- **WHEN** o gestor acessa o item de Destaques do formulário
- **THEN** a interface exibe card lúdico com ícone positivo, texto motivador sobre conquistas da equipe e campo de texto com contador de caracteres

#### Scenario: Gestor interage com seção de Dificuldades
- **WHEN** o gestor acessa o item de Dificuldades do formulário
- **THEN** a interface exibe card focado em oportunidades de melhoria e apoio institucional com ícone de alerta construtivo e contadores dinâmicos

