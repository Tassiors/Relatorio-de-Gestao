# Tasks

## 1. Banco de Dados e Carga Inicial do REDCap

- [x] 1.1 Criar modelos SQLAlchemy em `src/models/` para organizacao (gerencias, uorgs), exercicio, entregas, indicadores, relatorios bimestrais, feedback institucional, prazos excepcionais e notificacoes, verificando importaÃƒÂ§ÃƒÂµes no Alembic.
- [x] 1.2 Gerar e aplicar migraÃƒÂ§ÃƒÂ£o Alembic criando as tabelas relacionais em `data/app.db` e verificar integridade do schema.
- [x] 1.3 Desenvolver e executar script `src/scripts/seed_from_redcap.py` para carregar as 4 GerÃƒÂªncias, 23 UORGs, 84 entregas e 20 indicadores extraÃƒÂ­dos do REDCap para o ExercÃƒÂ­cio 2026, verificando contagem de registros carregados.

## 2. Camada de DomÃƒÂ­nio, Regras de NegÃƒÂ³cio e ExportaÃƒÂ§ÃƒÂ£o

- [x] 2.1 Implementar Providers assÃƒÂ­ncronos e templates SQL para gestÃƒÂ£o de UORGs, ExercÃƒÂ­cios, Entregas e Indicadores, verificando execuÃƒÂ§ÃƒÂ£o das queries.
- [x] 2.2 Implementar Controllers com validaÃƒÂ§ÃƒÂ£o de regras de negÃƒÂ³cio: cÃƒÂ¡lculo de meta (>=, <=, =, entre/faixa), indisponibilidade justificada, conclusÃƒÂ£o ÃƒÂºnica de entrega e obrigatoriedade de motivo para prazo excepcional, verificando validaÃƒÂ§ÃƒÂµes com testes.
- [x] 2.3 Implementar Controller e Provider para o RelatÃƒÂ³rio Bimestral com suporte a salvamento de rascunho automÃƒÂ¡tico, validaÃƒÂ§ÃƒÂ£o prÃƒÂ©-envio e reenvio no prazo, verificando alternÃƒÂ¢ncia de status.
- [x] 2.4 Implementar lÃƒÂ³gica de Feedback Institucional permitido a Superintendente e Administrador, e central de notificaÃƒÂ§ÃƒÂµes internas.
- [x] 2.5 Implementar exportador de relatÃƒÂ³rios e consolidados em formatos Excel (.xlsx) e PDF, verificando geraÃƒÂ§ÃƒÂ£o e download dos arquivos.

## 3. Routers FastAPI e Trilha de Auditoria

- [x] 3.1 Criar routers FastAPI protegidos por padrÃƒÂ£o (`Default-Private Router Pattern`) para `/api/exercicios`, `/api/uorgs`, `/api/entregas`, `/api/indicadores`, `/api/relatorios`, `/api/prazos-excepcionais` e `/api/notificacoes`.
- [x] 3.2 Integrar helper `registrar_auditoria()` em todas as operaÃƒÂ§ÃƒÂµes de mutaÃƒÂ§ÃƒÂ£o, verificando inserÃƒÂ§ÃƒÂ£o de logs com IP e dados anteriores/novos em `audit_logs`.
- [x] 3.3 Executar auditoria arquitetural `python audit_framework.py .` e verificar aprovaÃƒÂ§ÃƒÂ£o de 100% (11/11).

## 4. Frontend Vue 3 (Vite + Tailwind + Pinia)

- [ ] 4.1 Criar serviÃƒÂ§os de API (`src/services/`) e stores Pinia para gestÃƒÂ£o do estado de relatÃƒÂ³rios, unidades e notificaÃƒÂ§ÃƒÂµes.
- [ ] 4.2 Desenvolver a tela principal com a Matriz UORG x Bimestre, exibindo status operacional por cores, filtros por GerÃƒÂªncia e indicadores resumidos de Home.
- [ ] 4.3 Desenvolver a tela de preenchimento do formulÃƒÂ¡rio bimestral com autosave, checklist de entregas, preenchimento de indicadores com operador de faixa e campos de Destaques/Dificuldades.
- [ ] 4.4 Desenvolver a tela de visualizaÃƒÂ§ÃƒÂ£o consolidada com navegaÃƒÂ§ÃƒÂ£o sequencial entre relatÃƒÂ³rios e painel de feedback institucional.
- [ ] 4.5 Desenvolver tela administrativa para configuraÃƒÂ§ÃƒÂ£o do calendÃƒÂ¡rio anual e concessÃƒÂ£o de prazo excepcional com formulÃƒÂ¡rio exigindo justificativa obrigatÃƒÂ³ria.
- [ ] 4.6 Gerar build de produÃƒÂ§ÃƒÂ£o do frontend (`npm run build`) para `src/static/dist` e validar carregamento integrado no FastAPI.

## 5. Testes Automatizados e Fechamento

- [x] 5.1 Criar suÃƒÂ­te de testes com pytest cobrindo as regras funcionais (RN-ORG-01 a RN-NFR-02) e verificar aprovaÃƒÂ§ÃƒÂ£o completa dos testes.
- [ ] 5.2 Executar validaÃƒÂ§ÃƒÂ£o final do OpenSpec (`openspec validate portal-relatorio-gestao`) e `python audit_framework.py .`, garantindo conformidade e estabilidade.