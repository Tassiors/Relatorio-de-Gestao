import api from './api';

export interface IndicadorItem {
  id?: number | null;
  indicador_id: number;
  nome: string;
  descricao?: string;
  periodicidade: string;
  unidade_medida: string;
  meta_operador: string;
  meta_valor?: number | null;
  meta_valor_max?: number | null;
  competencia: string;
  valor_apurado?: number | null;
  meta_atingida?: boolean | null;
  resultado_indisponivel: boolean;
  justificativa_indisponibilidade?: string;
  nao_aplicavel: boolean;
  orientacao_periodicidade?: string;
}

export interface EntregaItem {
  id?: number | null;
  entrega_id: number;
  titulo: string;
  concluida: boolean;
  concluida_anteriormente?: boolean;
  bimestre_conclusao_id?: number | null;
  bimestre_conclusao_nome?: string | null;
  observacoes?: string;
}

export interface FeedbackItem {
  id: number;
  autor_nome: string;
  autor_perfil: string;
  texto: string;
  data?: string;
}

export interface RelatorioDetalhe {
  id?: number | null;
  exercicio_id: number;
  bimestre_id: number;
  bimestre_nome: string;
  bimestre_status: string;
  uorg_id: number;
  uorg_sigla: string;
  uorg_nome: string;
  status: string;
  versao: number;
  data_envio?: string | null;
  usuario_envio?: string | null;
  destaques: string;
  dificuldades: string;
  prazo_excepcional?: {
    ativo: boolean;
    data_fim: string;
    motivo: string;
  } | null;
  itens_entrega: EntregaItem[];
  itens_indicador: IndicadorItem[];
  feedbacks: FeedbackItem[];
}

export interface EntregaPlanejadaItem {
  id: number;
  uorg_id: number;
  exercicio_id: number;
  titulo: string;
  descricao?: string;
  concluida: boolean;
  ordem: number;
  ativo: boolean;
}

export interface IndicadorPlanejadoItem {
  id: number;
  uorg_id: number;
  exercicio_id: number;
  nome: string;
  descricao?: string;
  periodicidade: string;
  unidade_medida: string;
  meta_operador: string;
  meta_valor: number;
  meta_valor_max?: number | null;
  ordem: number;
  ativo: boolean;
}

export interface PlanejamentoUorgDetalhe {
  exercicio: {
    id: number;
    ano: number;
    descricao?: string;
    status: string;
    bimestres: any[];
  };
  uorg: {
    id: number;
    sigla: string;
    nome: string;
    gerencia_sigla?: string;
  };
  planejamento_aberto: boolean;
  entregas: EntregaPlanejadaItem[];
  indicadores: IndicadorPlanejadoItem[];
  total_entregas: number;
  total_indicadores: number;
}

export const gestaoApi = {
  async obterUsuarioLogado() {
    const res = await api.get('/api/gestao/me');
    return res.data;
  },

  async obterEstrutura() {
    const res = await api.get('/api/gestao/estrutura');
    return res.data;
  },

  async obterExercicioAtivo() {
    const res = await api.get('/api/gestao/exercicios/ativo');
    return res.data;
  },

  async obterMatriz(exercicioId?: number) {
    const url = exercicioId ? `/api/gestao/matriz?exercicio_id=${exercicioId}` : '/api/gestao/matriz';
    const res = await api.get(url);
    return res.data;
  },

  async obterRelatorio(exercicioId: number, bimestreId: number, uorgId: number): Promise<RelatorioDetalhe> {
    const res = await api.get(`/api/gestao/relatorios?exercicio_id=${exercicioId}&bimestre_id=${bimestreId}&uorg_id=${uorgId}`);
    return res.data;
  },

  async salvarRascunho(payload: any) {
    const res = await api.post('/api/gestao/relatorios/rascunho', payload);
    return res.data;
  },

  async enviarRelatorio(payload: any) {
    const res = await api.post('/api/gestao/relatorios/enviar', payload);
    return res.data;
  },

  async registrarFeedback(relatorioId: number, texto: string) {
    const res = await api.post(`/api/gestao/relatorios/${relatorioId}/feedback`, { texto });
    return res.data;
  },

  async concederPrazoExcepcional(payload: { exercicio_id: number; bimestre_id: number; uorg_id: number; motivo?: string; data_fim: string }) {
    const res = await api.post('/api/gestao/prazos-excepcionais', payload);
    return res.data;
  },

  async atualizarBimestre(bimestreId: number, payload: { status?: string; data_fechamento_regular?: string | null }) {
    const res = await api.put(`/api/gestao/bimestres/${bimestreId}`, payload);
    return res.data;
  },

  async obterUorgsAcessiveisDashboard() {
    const res = await api.get('/api/relatorios-gestao/dashboard/uorgs-acessiveis');
    return res.data;
  },

  async obterMetricasDashboardUorg(uorgId: number, exercicioId?: number) {
    const url = exercicioId
      ? `/api/relatorios-gestao/dashboard/metricas/${uorgId}?exercicio_id=${exercicioId}`
      : `/api/relatorios-gestao/dashboard/metricas/${uorgId}`;
    const res = await api.get(url);
    return res.data;
  },

  async listarNotificacoes() {
    const res = await api.get('/api/gestao/notificacoes');
    return res.data;
  },

  async marcarNotificacaoLida(notificacaoId: number) {
    const res = await api.post(`/api/gestao/notificacoes/${notificacaoId}/lida`);
    return res.data;
  },

  getExcelRelatorioUrl(relatorioId: number) {
    return `/api/gestao/relatorios/${relatorioId}/export/excel`;
  },

  getPdfRelatorioUrl(relatorioId: number) {
    return `/api/gestao/relatorios/${relatorioId}/export/pdf`;
  },

  getExcelMatrizUrl(exercicioId?: number) {
    return exercicioId ? `/api/gestao/matriz/export/excel?exercicio_id=${exercicioId}` : '/api/gestao/matriz/export/excel';
  },

  // Planejamento Anual
  async obterPlanejamentoUorg(uorgId: number, exercicioId?: number): Promise<PlanejamentoUorgDetalhe> {
    const url = exercicioId
      ? `/api/gestao/planejamento/uorg/${uorgId}?exercicio_id=${exercicioId}`
      : `/api/gestao/planejamento/uorg/${uorgId}`;
    const res = await api.get(url);
    return res.data;
  },

  async criarEntregaPlanejada(payload: {
    uorg_id: number;
    exercicio_id: number;
    titulo: string;
    descricao?: string;
    ordem?: number;
  }) {
    const res = await api.post('/api/gestao/planejamento/entregas', payload);
    return res.data;
  },

  async editarEntregaPlanejada(entregaId: number, payload: { titulo: string; descricao?: string }) {
    const res = await api.put(`/api/gestao/planejamento/entregas/${entregaId}`, payload);
    return res.data;
  },

  async inativarEntregaPlanejada(entregaId: number) {
    const res = await api.delete(`/api/gestao/planejamento/entregas/${entregaId}`);
    return res.data;
  },

  async criarIndicadorPlanejado(payload: {
    uorg_id: number;
    exercicio_id: number;
    nome: string;
    descricao?: string;
    periodicidade: string;
    unidade_medida: string;
    meta_operador: string;
    meta_valor: number;
    meta_valor_max?: number | null;
    ordem?: number;
  }) {
    const res = await api.post('/api/gestao/planejamento/indicadores', payload);
    return res.data;
  },

  async editarIndicadorPlanejado(indicadorId: number, payload: {
    nome: string;
    descricao?: string;
    periodicidade: string;
    unidade_medida: string;
    meta_operador: string;
    meta_valor: number;
    meta_valor_max?: number | null;
  }) {
    const res = await api.put(`/api/gestao/planejamento/indicadores/${indicadorId}`, payload);
    return res.data;
  },

  async inativarIndicadorPlanejado(indicadorId: number) {
    const res = await api.delete(`/api/gestao/planejamento/indicadores/${indicadorId}`);
    return res.data;
  },

  async abrirPlanejamentoExercicio(exercicioId: number) {
    const res = await api.post(`/api/gestao/planejamento/exercicio/${exercicioId}/abrir-planejamento`);
    return res.data;
  },

  async fecharPlanejamentoExercicio(exercicioId: number) {
    const res = await api.post(`/api/gestao/planejamento/exercicio/${exercicioId}/fechar-planejamento`);
    return res.data;
  },

  async alterarStatusExercicio(exercicioId: number, status: string) {
    const res = await api.post(`/api/gestao/planejamento/exercicio/${exercicioId}/status`, { status });
    return res.data;
  }
};

