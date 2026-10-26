<template>
  <div class="space-y-6 max-w-5xl mx-auto">
    <!-- Header de Navegação Sequencial -->
    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-black text-gray-900 flex items-center gap-2">
          <span class="w-2.5 h-6 bg-purple-600 rounded-full"></span>
          Visualização Consolidada dos Relatórios
        </h1>
        <p class="text-xs text-gray-500 mt-0.5">
          Navegação sequencial entre relatórios de diferentes setores para auditoria e parecer institucional.
        </p>
      </div>

      <!-- Navegação Sequencial: Anterior / Próximo (RF-VIS-01) -->
      <div class="flex items-center gap-2">
        <button
          @click="navegarRelatorio(-1)"
          :disabled="indiceUorgAtual <= 0"
          class="px-4 py-2 bg-gray-100 hover:bg-gray-200 disabled:opacity-40 text-gray-700 text-xs font-bold rounded-lg transition flex items-center gap-1.5"
        >
          ← Anterior
        </button>

        <span class="text-xs text-gray-500 font-semibold px-2">
          {{ indiceUorgAtual + 1 }} de {{ todasUorgs.length }}
        </span>

        <button
          @click="navegarRelatorio(1)"
          :disabled="indiceUorgAtual >= todasUorgs.length - 1"
          class="px-4 py-2 bg-gray-100 hover:bg-gray-200 disabled:opacity-40 text-gray-700 text-xs font-bold rounded-lg transition flex items-center gap-1.5"
        >
          Próximo →
        </button>
      </div>
    </div>

    <!-- Controles de Filtro -->
    <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-wrap items-center gap-4">
      <div class="flex items-center gap-2">
        <label class="text-xs font-bold text-gray-600">Bimestre:</label>
        <select 
          v-model="bimestreSelecionadoId" 
          @change="carregarRelatorioAtual"
          class="text-xs font-bold p-2 bg-gray-50 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option v-for="b in bimestres" :key="b.id" :value="b.id">{{ b.nome }}</option>
        </select>
      </div>

      <div class="flex items-center gap-2">
        <label class="text-xs font-bold text-gray-600">Unidade (UORG):</label>
        <select 
          v-model="uorgSelecionadaId" 
          @change="onUorgSelectChange"
          class="text-xs font-bold p-2 bg-gray-50 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-purple-500 max-w-xs"
        >
          <option v-for="u in todasUorgs" :key="u.id" :value="u.id">
            [{{ u.sigla }}] {{ u.nome }}
          </option>
        </select>
      </div>

      <div class="ml-auto flex items-center gap-2">
        <a 
          v-if="relatorio.id"
          :href="gestaoApi.getExcelRelatorioUrl(relatorio.id)" 
          download
          class="px-3 py-1.5 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 text-xs font-bold rounded-lg border border-emerald-200 transition"
        >
          Excel
        </a>
        <a 
          v-if="relatorio.id"
          :href="gestaoApi.getPdfRelatorioUrl(relatorio.id)" 
          download
          class="px-3 py-1.5 bg-red-50 text-red-700 hover:bg-red-100 text-xs font-bold rounded-lg border border-red-200 transition"
        >
          PDF
        </a>
      </div>
    </div>

    <!-- Conteúdo do Relatório Formatado -->
    <div v-if="carregando" class="text-center py-12 text-gray-400">
      Carregando relatório...
    </div>

    <div v-else class="space-y-6">
      <!-- Card Principal: Status e Identificação -->
      <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b pb-4">
          <div>
            <h2 class="text-xl font-bold text-gray-900">{{ relatorio.uorg_sigla }} - {{ relatorio.uorg_nome }}</h2>
            <p class="text-xs text-gray-500 mt-0.5">Competência: {{ relatorio.bimestre_nome }} | Versão {{ relatorio.versao }}</p>
          </div>
          <span class="text-xs font-bold px-3 py-1 rounded-full w-fit" :class="getStatusBadgeClass(relatorio.status)">
            Status: {{ relatorio.status }}
          </span>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 text-xs">
          <div>
            <span class="text-gray-400 block font-semibold">Submetido em:</span>
            <span class="font-bold text-gray-800">{{ relatorio.data_envio ? formatarData(relatorio.data_envio) : 'Não submetido' }}</span>
          </div>
          <div>
            <span class="text-gray-400 block font-semibold">Responsável:</span>
            <span class="font-bold text-gray-800">{{ relatorio.usuario_envio || '—' }}</span>
          </div>
          <div>
            <span class="text-gray-400 block font-semibold">Entregas Concluídas:</span>
            <span class="font-bold text-emerald-600">{{ entregasConcluidasCount }} de {{ (relatorio.itens_entrega || []).length }}</span>
          </div>
          <div>
            <span class="text-gray-400 block font-semibold">Metas Atingidas:</span>
            <span class="font-bold text-blue-600">{{ metasAtingidasCount }} de {{ (relatorio.itens_indicador || []).length }}</span>
          </div>
        </div>
      </div>

      <!-- Entregas Pactuadas -->
      <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 space-y-3">
        <h3 class="text-md font-bold text-gray-900">1. Entregas Planejadas</h3>
        <div v-if="relatorio.itens_entrega && relatorio.itens_entrega.length > 0" class="space-y-2">
          <div 
            v-for="ent in relatorio.itens_entrega" 
            :key="ent.entrega_id"
            class="flex items-start justify-between p-3 rounded-lg border text-xs"
            :class="ent.concluida ? 'bg-emerald-50/50 border-emerald-200' : 'bg-gray-50 border-gray-200'"
          >
            <div>
              <span class="font-bold text-gray-800">{{ ent.titulo }}</span>
              <p v-if="ent.observacoes" class="text-gray-500 mt-1 italic">Obs: {{ ent.observacoes }}</p>
            </div>
            <span class="font-bold px-2.5 py-1 rounded-full text-[11px]" :class="ent.concluida ? 'bg-emerald-100 text-emerald-800' : 'bg-gray-200 text-gray-600'">
              {{ ent.concluida ? 'Concluída' : 'Pendente' }}
            </span>
          </div>
        </div>
        <p v-else class="text-xs text-gray-400 italic">Nenhuma entrega cadastrada.</p>
      </div>

      <!-- Indicadores de Gestão -->
      <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 space-y-3">
        <h3 class="text-md font-bold text-gray-900">2. Indicadores de Gestão</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead>
              <tr class="bg-gray-50 text-gray-500 font-bold border-b">
                <th class="p-3">Indicador</th>
                <th class="p-3 text-center">Meta Pactuada</th>
                <th class="p-3 text-center">Valor Apurado</th>
                <th class="p-3 text-center">Atingimento</th>
                <th class="p-3">Observações / Justificativa</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="ind in relatorio.itens_indicador" :key="ind.indicador_id" class="hover:bg-gray-50/50">
                <td class="p-3 font-semibold text-gray-800">{{ ind.nome }}</td>
                <td class="p-3 text-center font-bold text-blue-700">{{ formatarMeta(ind) }}</td>
                <td class="p-3 text-center font-bold">
                  {{ ind.resultado_indisponivel ? 'Indisponível' : (ind.valor_apurado !== null ? ind.valor_apurado : '—') }}
                </td>
                <td class="p-3 text-center">
                  <span v-if="ind.meta_atingida === true" class="px-2 py-0.5 bg-emerald-100 text-emerald-800 font-extrabold rounded">
                    Atingida
                  </span>
                  <span v-else-if="ind.meta_atingida === false" class="px-2 py-0.5 bg-red-100 text-red-800 font-extrabold rounded">
                    Não Atingida
                  </span>
                  <span v-else class="text-gray-400">
                    {{ ind.resultado_indisponivel ? 'Justificado' : '—' }}
                  </span>
                </td>
                <td class="p-3 text-gray-500 italic">
                  {{ ind.justificativa_indisponibilidade || '—' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Destaques e Dificuldades -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100 space-y-2">
          <h4 class="font-bold text-sm text-emerald-800">3. Destaques Operacionais</h4>
          <p class="text-xs text-gray-700 leading-relaxed whitespace-pre-wrap">
            {{ relatorio.destaques || 'Nenhum destaque informado.' }}
          </p>
        </div>
        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100 space-y-2">
          <h4 class="font-bold text-sm text-red-800">4. Principais Dificuldades</h4>
          <p class="text-xs text-gray-700 leading-relaxed whitespace-pre-wrap">
            {{ relatorio.dificuldades || 'Nenhuma dificuldade informada.' }}
          </p>
        </div>
      </div>

      <!-- Parecer Institucional / Feedbacks Registrados -->
      <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 space-y-4">
        <h3 class="text-md font-bold text-gray-900">5. Pareceres e Feedbacks Institucionais</h3>
        
        <div v-if="relatorio.feedbacks && relatorio.feedbacks.length > 0" class="space-y-3">
          <div 
            v-for="fb in relatorio.feedbacks" 
            :key="fb.id"
            class="p-4 rounded-xl bg-purple-50/50 border border-purple-100 space-y-1"
          >
            <div class="flex items-center justify-between text-xs">
              <span class="font-bold text-purple-900">{{ fb.autor_nome }} ({{ fb.autor_perfil }})</span>
              <span class="text-gray-400">{{ fb.data ? formatarData(fb.data) : '' }}</span>
            </div>
            <p class="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">{{ fb.texto }}</p>
          </div>
        </div>
        <p v-else class="text-xs text-gray-400 italic">Nenhum feedback registrado até o momento.</p>

        <!-- Formulário para Emissão de Novo Feedback (Superintendente e Administrador) -->
        <div class="mt-4 pt-4 border-t border-gray-100 space-y-2 bg-gray-50/60 p-4 rounded-xl">
          <h4 class="text-xs font-bold text-gray-700 uppercase">Emitir Parecer / Feedback Institucional:</h4>
          <textarea
            v-model="novoFeedbackTexto"
            rows="3"
            placeholder="Digite aqui o feedback institucional para a chefia desta unidade..."
            class="w-full text-xs p-3 bg-white rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-purple-500"
          ></textarea>
          <div class="flex justify-end">
            <button
              @click="salvarFeedback"
              :disabled="enviandoFeedback || !novoFeedbackTexto.trim()"
              class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold rounded-lg shadow-sm transition disabled:opacity-50"
            >
              {{ enviandoFeedback ? 'Registrando...' : 'Registrar Parecer' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { gestaoApi, RelatorioDetalhe } from '../services/gestaoApi';

const bimestres = ref<any[]>([]);
const todasUorgs = ref<any[]>([]);
const bimestreSelecionadoId = ref<number>(1);
const uorgSelecionadaId = ref<number>(1);
const carregando = ref(false);
const enviandoFeedback = ref(false);
const novoFeedbackTexto = ref('');

const relatorio = ref<RelatorioDetalhe>({
  exercicio_id: 2026,
  bimestre_id: 1,
  bimestre_nome: '1º Bimestre',
  bimestre_status: 'ABERTO',
  uorg_id: 1,
  uorg_sigla: '',
  uorg_nome: '',
  status: 'RASCUNHO',
  versao: 0,
  destaques: '',
  dificuldades: '',
  itens_entrega: [],
  itens_indicador: [],
  feedbacks: []
});

const indiceUorgAtual = computed(() => {
  return todasUorgs.value.findIndex(u => u.id === uorgSelecionadaId.value);
});

const entregasConcluidasCount = computed(() => {
  return (relatorio.value.itens_entrega || []).filter(e => e.concluida).length;
});

const metasAtingidasCount = computed(() => {
  return (relatorio.value.itens_indicador || []).filter(i => i.meta_atingida === true).length;
});

async function carregarEstruturaEBimestres() {
  try {
    const ex = await gestaoApi.obterExercicioAtivo();
    bimestres.value = ex.bimestres;
    if (ex.bimestres.length > 0) {
      bimestreSelecionadoId.value = ex.bimestres[0].id;
    }

    const est = await gestaoApi.obterEstrutura();
    const uList: any[] = [];
    est.forEach((g: any) => {
      g.uorgs.forEach((u: any) => {
        uList.push({ ...u, gerencia_sigla: g.sigla });
      });
    });
    todasUorgs.value = uList;
    if (uList.length > 0) {
      uorgSelecionadaId.value = uList[0].id;
    }

    await carregarRelatorioAtual();
  } catch (err) {
    console.error('Erro na inicialização:', err);
  }
}

async function carregarRelatorioAtual() {
  carregando.value = true;
  try {
    const data = await gestaoApi.obterRelatorio(2026, bimestreSelecionadoId.value, uorgSelecionadaId.value);
    relatorio.value = data;
  } catch (err) {
    console.error('Erro ao carregar relatório:', err);
  } finally {
    carregando.value = false;
  }
}

function onUorgSelectChange() {
  carregarRelatorioAtual();
}

function navegarRelatorio(delta: number) {
  const novoIdx = indiceUorgAtual.value + delta;
  if (novoIdx >= 0 && novoIdx < todasUorgs.value.length) {
    uorgSelecionadaId.value = todasUorgs.value[novoIdx].id;
    carregarRelatorioAtual();
  }
}

async function salvarFeedback() {
  if (!novoFeedbackTexto.value.trim()) return;
  if (!relatorio.value.id) {
    alert('Relatório ainda não foi iniciado pela UORG.');
    return;
  }
  enviandoFeedback.value = true;
  try {
    const fb = await gestaoApi.registrarFeedback(relatorio.value.id, novoFeedbackTexto.value.trim());
    relatorio.value.feedbacks.push(fb);
    novoFeedbackTexto.value = '';
    alert('Parecer institucional registrado com sucesso!');
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Erro ao registrar parecer.');
  } finally {
    enviandoFeedback.value = false;
  }
}

function formatarMeta(ind: any) {
  const op = ind.meta_operador || '>=';
  if (op === 'ENTRE') return `${ind.meta_valor} a ${ind.meta_valor_max}`;
  const opSym = op === 'MAIOR_IGUAL' ? '≥' : (op === 'MENOR_IGUAL' ? '≤' : '=');
  return `${opSym} ${ind.meta_valor}${ind.unidade_medida === 'PERCENTUAL' ? '%' : ''}`;
}

function getStatusBadgeClass(status: string) {
  switch (status) {
    case 'ENVIADO': return 'bg-emerald-100 text-emerald-800';
    case 'EM_EDICAO': return 'bg-orange-100 text-orange-800';
    case 'PRAZO_EXCEPCIONAL': return 'bg-blue-100 text-blue-800';
    default: return 'bg-amber-100 text-amber-800';
  }
}

function formatarData(isoStr: string) {
  if (!isoStr) return '';
  const dt = new Date(isoStr);
  return dt.toLocaleDateString('pt-BR');
}

onMounted(() => {
  carregarEstruturaEBimestres();
});
</script>
