<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <div>
        <h1 class="text-2xl font-black text-gray-900 tracking-tight flex items-center gap-2">
          <span class="inline-block w-2.5 h-6 bg-blue-600 rounded-full"></span>
          Matriz de Acompanhamento Anual
        </h1>
        <p class="text-sm text-gray-500 mt-1">
          Acompanhamento em tempo real das submissões dos relatórios bimestrais por Unidade Organizacional (UORG).
        </p>
      </div>

      <div class="flex items-center gap-3">
        <a 
          :href="excelMatrizUrl" 
          download
          class="inline-flex items-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold rounded-lg shadow-sm transition"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          Exportar Matriz (Excel)
        </a>
      </div>
    </div>

    <!-- Cards de Métricas Consolidadas -->
    <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
      <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
        <div>
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Enviados</span>
          <p class="text-2xl font-black text-emerald-600 mt-1">{{ totais.enviados || 0 }}</p>
        </div>
        <div class="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">✓</div>
      </div>
      <div class="bg-gradient-to-br from-amber-50 via-yellow-50 to-orange-50 p-4 rounded-xl shadow-sm border-2 border-amber-300 flex items-center justify-between">
        <div>
          <span class="text-xs font-black text-amber-900 uppercase tracking-wider">Com Feedback</span>
          <p class="text-2xl font-black text-amber-700 mt-1">{{ totalComFeedback }}</p>
        </div>
        <div class="w-10 h-10 rounded-lg bg-amber-500 text-white flex items-center justify-center font-bold shadow-xs">🏛️</div>
      </div>
      <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
        <div>
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Pendentes</span>
          <p class="text-2xl font-black text-amber-600 mt-1">{{ totais.pendentes || 0 }}</p>
        </div>
        <div class="w-10 h-10 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center font-bold">!</div>
      </div>
      <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
        <div>
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Em Edição</span>
          <p class="text-2xl font-black text-orange-600 mt-1">{{ totais.em_edicao || 0 }}</p>
        </div>
        <div class="w-10 h-10 rounded-lg bg-orange-50 text-orange-600 flex items-center justify-center font-bold">✎</div>
      </div>
      <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
        <div>
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Prazo Excepcional</span>
          <p class="text-2xl font-black text-blue-600 mt-1">{{ totais.prazo_excepcional || 0 }}</p>
        </div>
        <div class="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold">⏱</div>
      </div>
    </div>

    <!-- Filtros -->
    <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-wrap items-center justify-between gap-4">
      <div class="flex flex-wrap items-center gap-2">
        <template v-if="gerenciasUnicas.length > 1">
          <span class="text-xs font-bold text-gray-500 uppercase">Filtrar por Gerência:</span>
          <button
            @click="filtroGerencia = ''"
            :class="filtroGerencia === '' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
            class="px-3 py-1.5 rounded-lg text-xs font-semibold transition"
          >
            Todas ({{ linhas.length }})
          </button>
          <button
            v-for="sigla in gerenciasUnicas"
            :key="sigla"
            @click="filtroGerencia = sigla"
            :class="filtroGerencia === sigla ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
            class="px-3 py-1.5 rounded-lg text-xs font-semibold transition"
          >
            {{ sigla }}
          </button>
        </template>

        <button
          @click="apenasComFeedback = !apenasComFeedback"
          :class="apenasComFeedback
            ? 'bg-amber-500 text-white border-amber-600 shadow-sm'
            : 'bg-amber-50 text-amber-900 border-amber-300 hover:bg-amber-100'"
          class="px-3 py-1.5 rounded-lg text-xs font-extrabold border transition flex items-center gap-1.5"
        >
          <span>🏛️</span>
          <span>Apenas com Feedback Institucional ({{ totalUorgsComFeedback }})</span>
        </button>
      </div>

      <div class="text-xs text-gray-500 flex flex-wrap items-center gap-4">
        <span class="flex items-center gap-1.5 font-bold text-amber-800 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-300">
          <span>🏛️</span> Feedback Institucional Emitido
        </span>
        <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-emerald-500"></span> Enviado</span>
        <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-amber-400"></span> Pendente</span>
        <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-orange-400"></span> Em Edição</span>
        <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-blue-500"></span> Prazo Excepcional</span>
        <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-gray-300"></span> Não Aberto</span>
      </div>
    </div>

    <!-- Tabela / Matriz Anual -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm border-collapse">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-200 text-xs font-bold text-gray-600 uppercase tracking-wider">
              <th class="p-4 w-28">Gerência</th>
              <th class="p-4 min-w-[200px]">Unidade Organizacional (UORG)</th>
              <th v-for="b in bimestres" :key="b.id" class="p-4 text-center min-w-[140px]">
                {{ b.nome }}
                <span class="block text-[10px] font-normal text-gray-400">
                  {{ b.status === 'ABERTO' ? '● Aberto' : '○ Fechado' }}
                </span>
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="linha in linhasFiltradas" :key="linha.uorg_id" class="hover:bg-gray-50/70 transition">
              <td class="p-4 font-bold text-gray-800 text-xs">
                <span class="px-2 py-1 bg-gray-100 rounded text-gray-700">{{ linha.gerencia_sigla }}</span>
              </td>
              <td class="p-4 font-medium text-gray-900">
                <div class="flex items-center gap-1.5">
                  <span class="font-bold text-sm text-gray-800">{{ linha.uorg_sigla }}</span>
                  <span
                    v-if="linha.tipo_uorg === 'DIVISAO'"
                    class="text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200"
                  >
                    Divisão
                  </span>
                </div>
                <div class="text-xs text-gray-500 truncate max-w-xs">{{ linha.uorg_nome }}</div>
              </td>

              <!-- Células de Bimestres -->
              <td v-for="celula in linha.bimestres" :key="celula.bimestre_id" class="p-3 text-center">
                <router-link
                  :to="getDestinoCelula(linha, celula)"
                  class="inline-flex flex-col items-center justify-center w-full px-2.5 py-2 rounded-xl border text-xs font-bold transition group relative"
                  :class="getCelulaClass(celula)"
                  :title="`Abrir ${linha.uorg_sigla} - ${celula.bimestre_numero}º Bimestre`"
                >
                  <span class="flex items-center gap-1">
                    {{ getStatusLabel(celula.status) }}
                  </span>
                  <span
                    v-if="celula.tem_feedback"
                    class="mt-1 inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-black bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-xs"
                    title="Relatório avaliado com Parecer / Feedback Institucional"
                  >
                    <span>🏛️</span>
                    <span>Parecer Emitido</span>
                  </span>
                  <span v-if="celula.data_envio" class="text-[9px] font-normal opacity-80 mt-0.5">
                    {{ formatarData(celula.data_envio) }}
                  </span>
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { gestaoApi } from '../services/gestaoApi';

const bimestres = ref<any[]>([]);
const linhas = ref<any[]>([]);
const totais = ref<any>({});
const filtroGerencia = ref('');
const apenasComFeedback = ref(false);
const exercicioAtivoId = ref<number | null>(null);
const usuarioLogado = ref<any>(null);

const excelMatrizUrl = computed(() => {
  return gestaoApi.getExcelMatrizUrl(exercicioAtivoId.value || undefined);
});

const totalComFeedback = computed(() => {
  let count = 0;
  for (const l of linhas.value) {
    for (const b of l.bimestres || []) {
      if (b.tem_feedback) count++;
    }
  }
  return count;
});

const totalUorgsComFeedback = computed(() => {
  return linhas.value.filter(l => (l.bimestres || []).some((b: any) => b.tem_feedback)).length;
});

const gerenciasUnicas = computed(() => {
  const set = new Set<string>();
  linhas.value.forEach(l => {
    if (l.gerencia_sigla) set.add(l.gerencia_sigla);
  });
  return Array.from(set).sort();
});

const linhasFiltradas = computed(() => {
  return linhas.value.filter(l => {
    if (filtroGerencia.value && l.gerencia_sigla !== filtroGerencia.value) return false;
    if (apenasComFeedback.value && !(l.bimestres || []).some((b: any) => b.tem_feedback)) return false;
    return true;
  });
});

function getDestinoCelula(linha: any, celula: any): string {
  const perfil = (usuarioLogado.value?.perfil || '').toUpperCase();
  if (perfil === 'ADMINISTRADOR') {
    return `/consolidado?bimestre=${celula.bimestre_id}&uorg=${linha.uorg_id}`;
  }
  if (['CHEFE', 'CHEFE_UORG'].includes(perfil) && Number(linha.uorg_id) === Number(usuarioLogado.value?.uorg_id)) {
    return `/preenchimento?bimestre=${celula.bimestre_id}&uorg=${linha.uorg_id}`;
  }
  return `/consolidado?bimestre=${celula.bimestre_id}&uorg=${linha.uorg_id}`;
}

async function carregarMatriz() {
  try {
    const [me, data] = await Promise.all([
      gestaoApi.obterUsuarioLogado(),
      gestaoApi.obterMatriz()
    ]);
    usuarioLogado.value = me;
    exercicioAtivoId.value = data.exercicio_id;
    bimestres.value = data.bimestres;
    linhas.value = data.linhas;
    totais.value = data.totais;
  } catch (err) {
    console.error('Erro ao carregar matriz:', err);
  }
}

function getCelulaClass(celula: any) {
  if (celula.tem_feedback) {
    return 'bg-gradient-to-br from-amber-50 via-yellow-50 to-emerald-50 text-emerald-900 border-2 border-amber-400 ring-2 ring-amber-200/70 shadow-sm hover:shadow-md';
  }
  switch (celula.status) {
    case 'ENVIADO':
      return 'bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100 hover:border-emerald-300';
    case 'PENDENTE':
      return 'bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100 hover:border-amber-300';
    case 'EM_EDICAO':
      return 'bg-orange-50 text-orange-700 border-orange-200 hover:bg-orange-100 hover:border-orange-300';
    case 'PRAZO_EXCEPCIONAL':
      return 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100 hover:border-blue-300';
    default:
      return 'bg-gray-50 text-gray-400 border-gray-200 hover:bg-gray-100 hover:text-gray-600';
  }
}

function getStatusLabel(status: string) {
  switch (status) {
    case 'ENVIADO': return 'Enviado';
    case 'PENDENTE': return 'Pendente';
    case 'EM_EDICAO': return 'Em Edição';
    case 'PRAZO_EXCEPCIONAL': return 'P. Excepcional';
    default: return 'Fechado';
  }
}

function formatarData(isoStr: string) {
  if (!isoStr) return '';
  const dt = new Date(isoStr);
  return dt.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
}

onMounted(() => {
  carregarMatriz();
});
</script>
