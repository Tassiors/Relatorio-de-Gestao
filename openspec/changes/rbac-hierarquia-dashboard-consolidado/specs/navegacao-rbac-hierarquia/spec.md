# Spec Delta

## Purpose

Define as regras de visibilidade do menu lateral, o escopo hierárquico de UORGs por tipo de unidade (Setor, Divisão, Gerência, Superintendência e Administrador) e as permissões de escrita e emissão de Feedback Institucional.

## ADDED Requirements

### Requirement: Menu lateral e escopo para Chefe de Setor
O sistema SHALL exibir no menu lateral do usuário Chefe de Setor apenas as opções "Início", "Planejamento Anual", "Preenchimento Bimestral" e "Visão Consolidada", restringindo a visualização e a edição de dados exclusivamente ao seu próprio Setor.

#### Scenario: Chefe de Setor visualiza menu lateral
- **WHEN** um usuário com perfil CHEFE vinculado a uma UORG do tipo Setor autentica-se no sistema
- **THEN** o menu lateral exibe exclusivamente as opções "Início", "Planejamento Anual", "Preenchimento Bimestral" e "Visão Consolidada", ocultando "Matriz de Acompanhamento", "Gestão de Exercício" e "Configurações"

### Requirement: Menu lateral e escopo hierárquico para Chefe de Divisão
O sistema SHALL exibir no menu lateral do Chefe de Divisão apenas "Início", "Planejamento Anual", "Preenchimento Bimestral", "Visão Consolidada" e "Matriz de Acompanhamento", limitando o Planejamento Anual e o Preenchimento Bimestral à própria Divisão e abrangendo a Divisão e os Setores subordinados na Visão Consolidada e na Matriz de Acompanhamento.

#### Scenario: Chefe de Divisão acessa menu lateral e Planejamento ou Preenchimento
- **WHEN** um usuário com perfil CHEFE vinculado a uma Divisão acessa "Planejamento Anual" ou "Preenchimento Bimestral"
- **THEN** o sistema restringe a edição e seleção de UORG exclusivamente à própria Divisão

#### Scenario: Chefe de Divisão consulta Visão Consolidada e Matriz de Acompanhamento
- **WHEN** um usuário com perfil CHEFE vinculado a uma Divisão acessa "Visão Consolidada" ou "Matriz de Acompanhamento"
- **THEN** o sistema lista os dados da própria Divisão e de todos os Setores subordinados a ela

### Requirement: Menu lateral e escopo somente leitura para Gerente
O sistema SHALL exibir no menu lateral do perfil GERENTE apenas as opções "Início", "Matriz de Acompanhamento" e "Visão Consolidada", permitindo na Matriz e na Visão Consolidada a consulta em modo somente leitura das divisões e setores subordinados à sua gerência.

#### Scenario: Gerente visualiza menu lateral
- **WHEN** um usuário com perfil GERENTE autentica-se no sistema
- **THEN** o menu lateral exibe apenas "Início", "Matriz de Acompanhamento" e "Visão Consolidada", ocultando "Planejamento Anual" e "Preenchimento Bimestral"

#### Scenario: Gerente consulta Visão Consolidada e Matriz de Acompanhamento
- **WHEN** um usuário com perfil GERENTE acessa a "Matriz de Acompanhamento" ou a "Visão Consolidada"
- **THEN** o sistema apresenta apenas os relatórios e indicadores das divisões e setores subordinados à sua gerência em modo estritamente de leitura

### Requirement: Menu lateral e escopo global para Superintendente
O sistema SHALL exibir no menu lateral do perfil SUPERINTENDENTE apenas as opções "Início", "Matriz de Acompanhamento" e "Visão Consolidada", garantindo visibilidade integral sobre todas as UORGs do hospital.

#### Scenario: Superintendente visualiza menu lateral e escopo global
- **WHEN** um usuário com perfil SUPERINTENDENTE autentica-se no sistema
- **THEN** o menu lateral exibe apenas "Início", "Matriz de Acompanhamento" e "Visão Consolidada" com acesso a todas as UORGs cadastradas

### Requirement: Restrição de registro de Pareceres e Feedbacks Institucionais
O sistema SHALL permitir o registro e a edição de Pareceres e Feedbacks Institucionais exclusivamente para usuários com perfil SUPERINTENDENTE ou ADMINISTRADOR, bloqueando essa operação para os demais perfis.

#### Scenario: Superintendente ou Administrador registra feedback institucional
- **WHEN** um usuário com perfil SUPERINTENDENTE ou ADMINISTRADOR submete um parecer institucional para um relatório bimestral enviado
- **THEN** o sistema grava o feedback institucional com sucesso e registra a auditoria correspondente

#### Scenario: Gerente ou Chefe tenta registrar feedback institucional
- **WHEN** um usuário com perfil GERENTE ou CHEFE visualiza um relatório bimestral ou tenta enviar uma requisição de registro de feedback
- **THEN** a interface não exibe o botão de gravação de parecer e a API rejeita qualquer tentativa com erro HTTP 403 Forbidden

