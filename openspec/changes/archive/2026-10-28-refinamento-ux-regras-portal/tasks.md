# Tasks

## 1. Backend: Regras de Negócio, Prazos e Periodicidade

- [x] 1.1 Flexibilizar `PrazoExcepcionalCreate` e provider para tornar o campo `motivo` opcional e permitir ao administrador alterar manualmente o status e a data de fechamento dos bimestres. Verificar com `pytest tests/test_relatorio_gestao.py`.
- [x] 1.2 Implementar efeito cascata de status "CONCLUIDA" em entregas planejadas no `relatorio_gestao_sqlite_provider.py` e controller ao salvar/submeter relatório. Verificar com novo teste automatizado em `tests/test_relatorio_gestao.py`.
- [x] 1.3 Criar helper de periodicidade de indicadores em `src/helpers/indicador_helper.py` para mapear bimestres aplicáveis (mensal, bimestral, trimestral, quadrimestral, semestral), validação e orientações contextuais. Verificar com teste unitário no pytest.
- [x] 1.4 Implementar endpoints `/api/relatorios-gestao/dashboard/uorgs-acessiveis` e `/api/relatorios-gestao/dashboard/metricas/{uorg_id}` para fornecer UORGs permitidas conforme hierarquia do usuário e métricas de entregas e indicadores com metas. Verificar via endpoint HTTP de teste.

## 2. Frontend: Planejamento Anual e Gestão de Exercício

- [x] 2.1 Atualizar `PlanejamentoAnualView.vue` substituindo campo de texto livre de "Unidade de Medida" por dropdown com catálogo padronizado (%, R$, dias, horas, pacientes, procedimentos, unidades, etc.) tanto na criação quanto na edição de indicador. Verificar interativamente no formulário.
- [x] 2.2 Certificar e reforçar no frontend e backend que o botão/ação de [abrir/fechar planejamento] é exibido e executado exclusivamente para usuários com perfil ADMINISTRADOR. Verificar validação de interface e controle de visibilidade.
- [x] 2.3 Atualizar `ExercicioAdminView.vue` para permitir definir manualmente qualquer bimestre como aberto/fechado, cadastrar data manual de fechamento e tornar a justificativa de prazo excepcional opcional, movendo o texto explicativo para a seção de concessão de prazo. Verificar layout e submissão.

## 3. Frontend: Redesign e Inteligência da Tela de Início (Dashboard)

- [x] 3.1 Remover cards estáticos de "UORGS" e "GERÊNCIAS" da `HomeView.vue`. Verificar remoção na interface.
- [x] 3.2 Adaptar card "ENTREGAS" para calcular e exibir total de entregas, quantidade concluída e percentual formatado de conclusão. Verificar renderização do cálculo.
- [x] 3.3 Configurar card "BIMESTRE VIGENTE" com ação de clique redirecionando para `/gestao-exercicio` exclusivamente quando o usuário autenticado for Administrador. Verificar navegação.
- [x] 3.4 Transformar blocos funcionais ("Matriz de Acompanhamento Anual", "Preenchimento Bimestral", "Visão Consolidada e Feedback" e "Gestão do Exercício e Prazos") em botões de atalho modernos com visibilidade filtrada por perfil. Verificar renderização conforme perfil ativo.
- [x] 3.5 Implementar dropdown hierárquico de UORGs (Superintendente visualiza todas; demais visualizam apenas sua própria UORG e subordinadas) com painel exibindo status das entregas e gráficos específicos de indicadores com metas. Verificar carregamento e gráficos.

## 4. Frontend: Preenchimento Bimestral Lúdico e Inspirador

- [x] 4.1 Atualizar Item 1 (Entregas) na tela de preenchimento para refletir o efeito cascata de entregas já concluídas em bimestres anteriores, impedindo retrabalho e destacando o ciclo de conquista. Verificar comportamento de cascata.
- [x] 4.2 Integrar no Item 2 (Indicadores) o motor de periodicidade (`indicadorHelper.ts`), solicitando a quantidade correta de campos (mensal = 2 campos, trimestral/quadrimestral/semestral nos bimestres correspondentes ou indicativo de não aplicável) com mensagens orientativas claras e suporte a indisponibilidade justificada. Verificar preenchimento e mensagens de ajuda.
- [x] 4.3 Redesenhar Itens 3 (Destaques) e 4 (Dificuldades) com estética lúdica e acolhedora, utilizando ícones expressivos (troféu/foguete, bússola/alvo), cartões com micro-interações, contadores de caracteres e mensagens inspiradoras. Verificar usabilidade e apelo visual.

## 5. Validação, Conformidade e Testes Integrados

- [x] 5.1 Executar suíte completa de testes automatizados com `pytest` e assegurar 100% de aprovação.
- [x] 5.2 Executar o auditor de conformidade arquitetural `python audit_framework.py .` e garantir manutenção de 100% (11/11 pilares mandatórios).
- [x] 5.3 Validar build de produção do frontend com `npm.cmd run build` em `frontend/` confirmando ausência de erros de compilação TypeScript e Vite.
