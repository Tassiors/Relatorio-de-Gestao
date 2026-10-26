# Proposal

## Why

O processo atual de coleta e consolidação dos Relatórios de Gestão do HC-UFPE foi prototipado no REDCap (arquivo `RelatriosDeGesto2026_2026-10-26_1600.REDCap.xml`), resultando em uma estrutura monolítica e plana de mais de 720 campos desnormalizados, sem tabelas relacionais, sem ciclo de vida controlado de versões e com alto acoplamento às 23 Unidades Organizacionais (UORGs).
Esta mudança implementa o **Portal de Relatórios de Gestão do HC-UFPE** sobre o **Framework SETISD (FastAPI + Vue 3)**, em total conformidade com a especificação funcional `Especificacao_Funcional_Relatorio_Gestao_HC_UFPE_v1.0.docx`, substituindo o REDCap por uma arquitetura relacional assíncrona, segura (AD + RBAC local), auditável e com alta usabilidade para chefias, gerentes e superintendência.

## What Changes

- **Substituição da estrutura plana do REDCap** por modelo de dados relacional (Exercício, Gerência, UORG, Usuário, EntregaPlanejada, Indicador, RelatorioBimestral, FeedbackSuperintendente, PrazoExcepcional e AuditLog).
- **Carga inicial de dados organizacionais e catálogo base**: importação das 4 Gerências, 23 UORGs, 84 entregas planejadas e 20 indicadores mapeados a partir do REDCap para o Exercício 2026.
- **Ciclo Anual e Janela de Planejamento**: módulo para criar exercícios, configurar calendário de 6 bimestres e definir entregas e indicadores esperados por UORG.
- **Gestão de Entregas e Indicadores**: cadastro flexível de indicadores com periodicidades (mensal, bimestral, trimestral, semestral, anual), metas com operadores (>=, <=, =), unidades de medida, justificativa de indisponibilidade e marcação de conclusão única de entregas.
- **Relatório Bimestral Operacional**: fluxo de preenchimento, autosave (rascunho), validação de obrigatoriedade, envio formal, histórico de reenvios e edição controlada dentro da janela aberta.
- **Prazo Excepcional e Reabertura**: mecanismo administrativo para reabertura pontual por UORG com registro compulsório de justificativa e expiração programada.
- **Painel Executivo e Dashboard Matriz UORG x Bimestre**: matriz visual de acompanhamento de status de preenchimento em tempo real, visualização consolidada com navegação sequencial e central de notificações.
- **Governança e Auditoria**: trilha imutável no banco com `audit_logs` registrando usuário, IP, timestamp e dados anteriores/novos de cada mutação, mantendo conformidade de 100% no `audit_framework.py`.

## Capabilities

### New Capabilities
- `estrutura-organizacional`: Gestão e persistência de Gerências e UORGs, suportando carga inicial e evolução sem quebra de histórico (RN-ORG-01).
- `ciclo-exercicio`: Configuração do exercício anual, calendário dos 6 bimestres e regras de planejamento (RF-EXE-01 a 04, RN-EXE-01).
- `entregas-planejadas`: Cadastro anual e ciclo de vida de entregas pactuadas, com conclusão única e integridade histórica (RF-ENT-01 a 05, RN-ENT-01 a 03).
- `indicadores-gestao`: Cadastro, regras de periodicidade, cálculo de atingimento de metas e tratamento de indisponibilidade justificada (RF-IND-01 a 09, RN-IND-01 a 06).
- `relatorio-bimestral`: Preenchimento bimestral, salvamento de rascunho, envio formal e edição posterior pelo Chefe da UORG (RF-REL-01 a 11, RN-REL-01 a 03).
- `prazo-excepcional`: Concessão, justificativa, isolamento e encerramento de prazos excepcionais pós-fechamento do bimestre (RF-PEX-01 a 07, RN-PEX-01 a 02).
- `destaques-dificuldades`: Registro de texto estruturado para conquistas e gargalos operacionais por bimestre (RF-TXT-01 a 04).
- `feedback-superintendente`: Registro e consulta de parecer institucional pela Superintendência com bloqueio de edição por chefias (RF-FBK-01 a 04, RN-FBK-01).
- `dashboard-acompanhamento`: Matriz UORG x Bimestre, indicadores resumidos na Home e visualização consolidada (RF-DSH-01 a 03, RF-VIS-01 a 03).
- `notificacoes-internas`: Central interna de alertas sobre abertura/fechamento de prazos e feedbacks recebidos (RF-NTF-01 a 02).

### Modified Capabilities
*(Nenhuma capacidade existente modificada - projeto inicial sobre o Framework SETISD)*

## Impact

- **Backend (`src/`)**: Criação de novos routers (`relatorio.py`, `exercicio.py`, `indicador.py`, `uorg.py`), controllers, providers assíncronos e modelos SQLAlchemy em `src/models/`.
- **Banco de Dados (`data/app.db` & `alembic/`)**: Novas migrações Alembic estruturando as tabelas relacionais do Portal de Relatórios de Gestão.
- **Frontend (`frontend/src/`)**: Novas telas e componentes Vue 3 (Dashboard Matriz, Formulário Bimestral, Configuração de Exercício, Visualização Consolidada) respeitando o layout padrão (SidebarNav à esquerda, marca e SemVer no rodapé).
- **Conformidade**: Execução de `python audit_framework.py .` mantendo 100% de aprovação nos 11 pilares mandatórios.