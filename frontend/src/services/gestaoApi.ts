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
}

export interface EntregaItem {
  id?: number | null;
  entrega_id: number;
  titulo: string;
  concluida: boolean;
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

  async concederPrazoExcepcional(payload: { exercicio_id: number; bimestre_id: number; uorg_id: number; motivo: string; data_fim: string }) {
    const res = await api.post('/api/gestao/prazos-excepcionais', payload);
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
  }
};
