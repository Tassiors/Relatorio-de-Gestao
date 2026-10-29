# Proposal

## Why

Durante o ciclo de validação e uso preliminar do Portal de Relatórios de Gestão do HC-UFPE, foram identificadas necessidades de evolução na experiência do usuário (UX), maior dinamismo no painel de abertura (Home), suporte rigoroso às regras de periodicidade dos indicadores (mensal, bimestral, trimestral, quadrimestral, semestral) e flexibilização operacional na gestão dos bimestres e prazos pela gestão/administração. Essas melhorias tornam a coleta bimestral mais lúdica e engajadora para os gestores, eliminam ambiguidades nos dados de indicadores e dão autonomia ao administrador do exercício.

## What Changes

### 1. Tela de Início (Dashboard Principal)
- **Remoção de Cards Obsoletos:** Remoção dos cards estáticos "UORGS" e "GERÊNCIAS".
- **Evolução do Card de Entregas:** Exibição do total e do percentual consolidado de entregas concluídas pela UORG/instituição.
- **Card de Bimestre Vigente Interativo:** Funcionamento como atalho direto para a tela de Gestão do Exercício (exclusivo para perfil Administrador).
- **Atalhos Operacionais por Perfil:** Transformação dos blocos funcionais ("Matriz de Acompanhamento Anual", "Preenchimento Bimestral", "Visão Consolidada e Feedback", "Gestão do Exercício e Prazos") em botões de atalho modernos, com controle de visibilidade baseado no perfil do usuário logado.
- **Seletor Hierárquico de UORG & Painel Integrado:** Inclusão de dropdown de seleção de UORG (Superintendente visualiza todas as UORGs; demais perfis visualizam apenas sua própria UORG e unidades subordinadas). Ao selecionar, renderiza dashboard com status das entregas e gráficos específicos de indicadores com suas metas.

### 2. Tela de Planejamento Anual da Unidade
- **Padronização da Unidade de Medida:** Substituição do campo de texto livre de "Unidade de Medida" por um dropdown com opções pré-definidas (%, R$, dias, horas, pacientes, procedimentos, unidades, etc.) tanto no modal de criação quanto no de edição de indicador.
- **Controle de Acesso da Janela de Planejamento:** Validação estrita para assegurar que apenas usuários com perfil ADMINISTRADOR visualizem e executem as ações de abrir e fechar o planejamento anual.

### 3. Tela de Preenchimento Bimestral
- **Efeito Cascata em Entregas Concluídas (Item 1):** Ao marcar uma entrega como "CONCLUÍDA" em um bimestre, o sistema automaticamente propaga o status de conclusão para os bimestres subsequentes do exercício.
- **Motor de Periodicidade e Validação de Indicadores (Item 2):** Implementação da regra funcional da especificação onde indicadores mensais (solicitam 2 valores por bimestre), trimestrais (solicitam nos 2º, 3º, 5º e 6º bimestres), quadrimestrais (solicitam nos 2º, 4º e 6º bimestres) e semestrais (solicitam nos 3º e 6º bimestres) exibem a quantidade exata de campos, orientações contextuais explicativas claras e validação de indisponibilidade justificada.
- **Redesign Visual, Lúdico e Inspirador (Itens 3 e 4):** Reformulação visual das seções de Destaques e Dificuldades com ícones temáticos, microinterações, cartões visuais acolhedores e contadores de caracteres para tornar o preenchimento fluido e agradável ao gestor.

### 4. Tela de Gestão de Exercício
- **Controle Manual do Bimestre Aberto/Fechado:** O administrador pode abrir e fechar manualmente qualquer bimestre do exercício.
- **Parametrização Manual de Data de Fechamento:** Fim do bloqueio automático cego às 23h59 da data pré-calculada; o administrador informa manualmente a data limite de fechamento para o bimestre aberto.
- **Flexibilização de Justificativa de Prazo Excepcional:** O campo de justificativa/motivo na concessão de prazo excepcional torna-se opcional.
- **Reposicionamento de Texto Explicativo:** Movimentação do texto de orientação para a seção correspondente de concessão de prazo excepcional.

## Capabilities

### New Capabilities
- `dashboard-inicio`: Painel inicial enriquecido com atalhos orientados a perfis, seletor hierárquico de UORG e visualização gráfica de metas e entregas.
- `preenchimento-bimestral`: Formulário bimestral lúdico e resiliente, com efeito cascata de entregas concluídas, motor de periodicidade de indicadores e orientações contextuais dinâmicas.
- `gestao-exercicio`: Painel administrativo flexível para controle manual de abertura e encerramento de bimestres, datas de corte e concessão ágil de prazos excepcionais.

### Modified Capabilities
- `planejamento-anual`: Restrição de digitação livre de unidades de medida para seleção padronizada em dropdown e garantia de exclusividade administrativa na janela de planejamento.

## Impact

- **Frontend:** Atualização das views `HomeView.vue`, `PlanejamentoAnualView.vue`, `RelatorioGestaoFormView.vue`, `ExercicioAdminView.vue` e componentes auxiliares (`SidebarNav.vue`, modais e componentes gráficos).
- **Backend:** Ajustes no `relatorio_gestao_controller.py`, `relatorio_gestao_sqlite_provider.py`, schemas Pydantic e regras de negócio para cascata de entregas, periodicidade de indicadores e flexibilização de prazos.
- **Auditoria & Segurança:** Manutenção dos 11 pilares mandatórios do framework e trilhas de auditoria imutáveis.
