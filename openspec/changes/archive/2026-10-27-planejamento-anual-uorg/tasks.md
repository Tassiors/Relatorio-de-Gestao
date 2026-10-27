# Tasks

## 1. Backend: Schemas, Provider e Controller de Planejamento Anual

- [x] 1.1 Criar schemas Pydantic (`CriarEntregaSchema`, `EditarEntregaSchema`, `CriarIndicadorSchema`, `EditarIndicadorSchema`) em `src/schemas/relatorio_gestao.py` e verificar validação de tipos.
- [x] 1.2 Implementar métodos no Provider (`criar_entrega`, `editar_entrega`, `inativar_entrega`, `criar_indicador`, `editar_indicador`, `inativar_indicador`, `atualizar_status_exercicio`) em `src/providers/interfaces/relatorio_gestao_provider_interface.py` e `src/providers/implementations/relatorio_gestao_sqlite_provider.py`.
- [x] 1.3 Implementar regras no Controller (`relatorio_gestao_controller.py`): validação de RBAC/escopo de UORG, verificação do status de planejamento aberto e limite de 1 a 3 indicadores ativos por UORG.

## 2. Backend: Endpoints REST e Trilha de Auditoria

- [x] 2.1 Criar rotas em `src/routers/relatorio_gestao.py` para `/api/gestao/planejamento/*` com injeção de dependências de autorização e registro de auditoria via `registrar_auditoria()`.
- [x] 2.2 Desenvolver suíte de testes automatizados em `tests/test_planejamento_anual.py` cobrindo regras de negócio, limites e permissões, e verificar aprovação com pytest.

## 3. Frontend: Tela de Planejamento Anual e Navegação

- [x] 3.1 Adicionar funções no serviço de API `frontend/src/services/gestaoService.ts` para comunicação com os novos endpoints de planejamento.
- [x] 3.2 Criar a view `frontend/src/views/PlanejamentoAnual.vue` com banner de status, listagem e modais de inclusão/edição/inativação de entregas e indicadores.
- [x] 3.3 Registrar rota `/planejamento` em `frontend/src/router/index.ts` e adicionar item no menu lateral `frontend/src/layouts/DefaultLayout.vue`.
- [x] 3.4 Executar build do frontend (`npm run build`) e validar execução integrada.

## 4. Conformidade e Validação Final

- [x] 4.1 Executar auditoria arquitetural `python audit_framework.py .` e verificar manutenção dos 11 pilares com 100% de conformidade.
- [x] 4.2 Executar validação final do OpenSpec (`openspec validate planejamento-anual-uorg`) e verificar consistência.
