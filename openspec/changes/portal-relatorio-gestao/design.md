# Design

## Context

O projeto substitui o protótipo desnormalizado do REDCap (arquivo `RelatriosDeGesto2026_2026-10-26_1600.REDCap.xml`), que continha mais de 720 campos espalhados e desprovidos de relacionamento relacional, por uma aplicação web moderna baseada no **Framework SETISD-HC-UFPE** (Python FastAPI + Vue 3 / Vite).
A arquitetura deve respeitar rigorosamente os 11 pilares mandatórios auditados por `audit_framework.py`:
- Separação estrita em camadas (Router -> Controller -> Provider -> Resource/SQL)
- Autenticação corporativa AD/LDAP + RBAC local no SQLite/PostgreSQL
- Roteadores protegidos por padrão (Default-Private Router Pattern)
- Cookies HttpOnly para refresh tokens e JWT efêmero
- Security Headers HTTP no middleware
- Trilha imutável em `audit_logs` registrando usuário, IP, entidade, campos e valores anterior/novo
- Layout Vue 3 com SidebarNav à esquerda, marca no topo e SemVer visível no rodapé

## Goals / Non-Goals

**Goals:**
- Estruturar modelo relacional completo cobrindo Exercício, Gerências, UORGs, Entregas, Indicadores, Relatórios, Prazos Excepcionais, Feedbacks e Notificações.
- Carga de dados inicial das 4 Gerências, 23 UORGs, 84 entregas e 20 indicadores mapeados a partir do REDCap para o Exercício 2026.
- Interface visual interativa com Matriz UORG x Bimestre color-coded por status de preenchimento.
- Formulário bimestral reativo com salvamento automático (rascunho), validação de obrigatoriedade e histórico de reenvios.
- Justificativa formal estritamente obrigatória para concessão de Prazo Excepcional (decisão validada pelo usuário).
- Emissão de feedback institucional por Superintendente e Administrador (decisão validada pelo usuário).
- Operador de intervalo ("entre" / min-max) para metas de indicadores além dos convencionais (decisão validada pelo usuário).
- Exportação nativa de relatórios e consolidados em formatos PDF e Excel (decisão validada pelo usuário).
- Manter 100% de aprovação (11/11) no `audit_framework.py`.

**Non-Goals:**
- Integração transacional direta em tempo real com as tabelas clínicas do AGHU na v1.0 (os dados dos indicadores são informados e justificados pelas UORGs).
- Notificações por WhatsApp/Teams na v1.0 (foco na Central de Notificações interna no portal).

## Decisions

### 1. Modelo Relacional Normalizado
- **Decisão**: Criar tabelas especializadas no banco relacional (`exercicios`, `gerencias`, `uorgs`, `usuarios_uorg`, `entregas_planejadas`, `indicadores`, `relatorios_bimestrais`, `itens_entrega_relatorio`, `itens_indicador_relatorio`, `feedbacks_relatorio`, `prazos_excepcionais`, `notificacoes`, `audit_logs`).
- **Alternativa rejeitada**: Manter tabelas EAV (Entity-Attribute-Value) ou JSON blobs únicos por relatório. O modelo relacional garante integridade referencial, consultas de alta performance na Matriz UORG x Bimestre e isolamento histórico (RN-ORG-01, RN-EXE-01).

### 2. Autenticação e RBAC Híbrido
- **Decisão**: Validação de credenciais no AD/LDAP (com fallback para Mock em ambiente de desenvolvimento local) combinada à checagem de autorização na tabela local de usuários (`src/models/usuario.py`).
- **Perfis implementados**: `ADMINISTRADOR`, `SUPERINTENDENTE`, `GERENTE`, `CHEFE_UORG` e `CONSULTA`. Cada Chefe tem escopo restrito à sua UORG e cada Gerente à sua Gerência (RN-NFR-01/02).

### 3. Prazo Excepcional com Justificativa Compulsória
- **Decisão**: O endpoint de concessão de prazo excepcional exigirá validação Pydantic com `min_length=10` no campo `motivo`. Sem motivo preenchido, a requisição é rejeitada com status HTTP 422.
- **Alternativa rejeitada**: Deixar motivo opcional. A formalização administrativa exige registro do porquê da reabertura fora do calendário regular.

### 4. Permissão para Feedback Institucional
- **Decisão**: A dependência de autorização do endpoint `POST /api/relatorio/{id}/feedback` validará se a role do usuário logado é `SUPERINTENDENTE` ou `ADMINISTRADOR`.
- **Alternativa rejeitada**: Restringir a apenas um perfil. A flexibilidade atende às necessidades de gestão do HC-UFPE.

### 5. Operador de Intervalo (Faixa min-max)
- **Decisão**: Modelar campos `meta_operador` (`MAIOR_IGUAL`, `MENOR_IGUAL`, `IGUAL`, `ENTRE`), `meta_valor` (numérico) e `meta_valor_max` (numérico, preenchido quando operador for `ENTRE`). A função de cálculo verificará `meta_valor <= resultado <= meta_valor_max`.

### 6. Mecanismo de Exportação (PDF e Excel)
- **Decisão**: 
  - Para Excel: uso da biblioteca `openpyxl` gerando arquivos `.xlsx` estilizados institucionalmente com formatação condicional de atingimento de metas.
  - Para PDF: geração estruturada de documento institucional para impressão e arquivo via motor leve de formatação de relatório.

### 7. Governança e Auditoria
- **Decisão**: Toda alteração de estado (salvar rascunho, enviar relatório, conceder prazo, emitir feedback) invocará `registrar_auditoria()` de `src/helpers/audit_helper.py`, persistindo IP de origem, usuário, entidade, dados anteriores e dados novos em formato JSON imutável.

## Risks / Trade-offs

- **[Risco: Concorrência e perda de rascunhos em preenchimentos longos]** → Mitigação: Autosave no frontend com debounce de 1500ms, persistência contínua do rascunho no backend e confirmação visual na tela com timestamp do último salvamento.
- **[Risco: Desempenho no carregamento da Matriz UORG x Bimestre]** → Mitigação: Query SQL única e otimizada via Provider assíncrono agregando o status de todas as 23 UORGs e 6 bimestres, sem queries N+1.
- **[Risco: Exposição acidental de rotas]** → Mitigação: Uso estrito do padrão Default-Private Router Pattern declarado em `APIRouter(dependencies=[Depends(...)])`.

## Migration Plan

1. Gerar migração Alembic para criação das tabelas relacionais do Portal de Relatórios de Gestão.
2. Executar script de seed (`src/scripts/seed_relatorio_gestao.py`) realizando a carga inicial de Gerências, UORGs, Entregas e Indicadores mapeados do REDCap para o Exercício 2026.
3. Executar `python audit_framework.py .` para validar conformidade arquitetural (100%).