# Spec Delta

## Purpose

Centraliza alertas e notificações internas aos usuários sobre abertura de bimestres, prazos excepcionais, pendências e feedbacks registrados.

## ADDED Requirements

### Requirement: Central de notificações no portal
O sistema SHALL exibir um painel com notificações não lidas no cabeçalho e marcar como lidas após visualização (RF-NTF-01).

#### Scenario: Usuário recebe aviso de feedback
- **WHEN** um feedback é registrado para sua UORG
- **THEN** o ícone de sino exibe indicador de nova notificação com link direto para o relatório
