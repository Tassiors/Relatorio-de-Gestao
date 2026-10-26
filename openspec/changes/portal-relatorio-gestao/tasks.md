# Tasks

## 1. Banco de Dados e Carga Inicial do REDCap

- [x] 1.1 Criar modelos SQLAlchemy em `src/models/` para organizacao (gerencias, uorgs), exercicio, entregas, indicadores, relatorios bimestrais, feedback institucional, prazos excepcionais e notificacoes, verificando importaÃ§Ãµes no Alembic.
- [x] 1.2 Gerar e aplicar migraÃ§Ã£o Alembic criando as tabelas relacionais em `data/app.db` e verificar integridade do schema.
- [x] 1.3 Desenvolver e executar script `src/scripts/seed_from_redcap.py` para carregar as 4 GerÃªncias, 23 UORGs, 84 entregas e 20 indicadores extraÃ­dos do REDCap para o ExercÃ­cio 2026, verificando contagem de registros carregados.

## 2. Camada de DomÃ­nio, Regras de NegÃ³cio e ExportaÃ§Ã£o

- [ ] 2.1 Implementar Providers assÃ­ncronos e templates SQL para gestÃ£o de UORGs, ExercÃ­cios, Entregas e Indicadores, verificando execuÃ§Ã£o das queries.
- [ ] 2.2 Implementar Controllers com validaÃ§Ã£o de regras de negÃ³cio: cÃ¡lculo de meta (>=, <=, =, entre/faixa), indisponibilidade justificada, conclusÃ£o Ãºnica de entrega e obrigatoriedade de motivo para prazo excepcional, verificando validaÃ§Ãµes com testes.
- [ ] 2.3 Implementar Controller e Provider para o RelatÃ³rio Bimestral com suporte a salvamento de rascunho automÃ¡tico, validaÃ§Ã£o prÃ©-envio e reenvio no prazo, verificando alternÃ¢ncia de status.
- [ ] 2.4 Implementar lÃ³gica de Feedback Institucional permitido a Superintendente e Administrador, e central de notificaÃ§Ãµes internas.
- [ ] 2.5 Implementar exportador de relatÃ³rios e consolidados em formatos Excel (.xlsx) e PDF, verificando geraÃ§Ã£o e download dos arquivos.

## 3. Routers FastAPI e Trilha de Auditoria

- [ ] 3.1 Criar routers FastAPI protegidos por padrÃ£o (`Default-Private Router Pattern`) para `/api/exercicios`, `/api/uorgs`, `/api/entregas`, `/api/indicadores`, `/api/relatorios`, `/api/prazos-excepcionais` e `/api/notificacoes`.
- [ ] 3.2 Integrar helper `registrar_auditoria()` em todas as operaÃ§Ãµes de mutaÃ§Ã£o, verificando inserÃ§Ã£o de logs com IP e dados anteriores/novos em `audit_logs`.
- [ ] 3.3 Executar auditoria arquitetural `python audit_framework.py .` e verificar aprovaÃ§Ã£o de 100% (11/11).

## 4. Frontend Vue 3 (Vite + Tailwind + Pinia)

- [ ] 4.1 Criar serviÃ§os de API (`src/services/`) e stores Pinia para gestÃ£o do estado de relatÃ³rios, unidades e notificaÃ§Ãµes.
- [ ] 4.2 Desenvolver a tela principal com a Matriz UORG x Bimestre, exibindo status operacional por cores, filtros por GerÃªncia e indicadores resumidos de Home.
- [ ] 4.3 Desenvolver a tela de preenchimento do formulÃ¡rio bimestral com autosave, checklist de entregas, preenchimento de indicadores com operador de faixa e campos de Destaques/Dificuldades.
- [ ] 4.4 Desenvolver a tela de visualizaÃ§Ã£o consolidada com navegaÃ§Ã£o sequencial entre relatÃ³rios e painel de feedback institucional.
- [ ] 4.5 Desenvolver tela administrativa para configuraÃ§Ã£o do calendÃ¡rio anual e concessÃ£o de prazo excepcional com formulÃ¡rio exigindo justificativa obrigatÃ³ria.
- [ ] 4.6 Gerar build de produÃ§Ã£o do frontend (`npm run build`) para `src/static/dist` e validar carregamento integrado no FastAPI.

## 5. Testes Automatizados e Fechamento

- [ ] 5.1 Criar suÃ­te de testes com pytest cobrindo as regras funcionais (RN-ORG-01 a RN-NFR-02) e verificar aprovaÃ§Ã£o completa dos testes.
- [ ] 5.2 Executar validaÃ§Ã£o final do OpenSpec (`openspec validate portal-relatorio-gestao`) e `python audit_framework.py .`, garantindo conformidade e estabilidade.