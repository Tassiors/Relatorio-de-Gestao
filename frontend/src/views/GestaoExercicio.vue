<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-black text-gray-900 tracking-tight flex items-center gap-2">
          <span class="inline-block w-2.5 h-6 bg-indigo-600 rounded-full"></span>
          Gestão do Exercício e Prazos
        </h1>
        <p class="text-sm text-gray-500 mt-1">
          Monitoramento do calendário anual, períodos de preenchimento e concessão de prazos excepcionais.
        </p>
      </div>
      <div v-if="exercicio" class="flex items-center gap-2 bg-indigo-50 border border-indigo-200 text-indigo-800 px-4 py-2 rounded-lg text-sm font-semibold">
        <span>Exercício Ativo:</span>
        <span class="text-indigo-900 font-extrabold">{{ exercicio.ano }}</span>
        <span class="px-2 py-0.5 text-xs rounded bg-indigo-200 text-indigo-900">{{ exercicio.status }}</span>
      </div>
    </div>

    <div v-if="carregando" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-600 border-t-transparent"></div>
      <p class="text-sm text-gray-500 mt-2 font-medium">Carregando calendário do exercício...</p>
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Calendário Anual de Bimestres -->
      <div class="lg:col-span-2 space-y-6">
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="p-5 border-b border-gray-100 flex items-center justify-between">
            <h2 class="text-base font-bold text-gray-900 flex items-center gap-2">
              <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Calendário Bimestral de Acompanhamento ({{ exercicio?.ano }})
            </h2>
            <span class="text-xs text-gray-400 font-medium">RN-CAD-01 a RN-CAD-03</span>
          </div>

          <div class="divide-y divide-gray-100">
            <div 
              v-for="bim in exercicio?.bimestres" 
              :key="bim.id"
              class="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-gray-50 transition"
            >
              <div class="flex items-center gap-3">
                <div 
                  class="w-10 h-10 rounded-lg flex items-center justify-center font-black text-sm shrink-0"
                  :class="{
                    'bg-emerald-100 text-emerald-800 border border-emerald-300': bim.status === 'ABERTO',
                    'bg-gray-100 text-gray-600 border border-gray-200': bim.status === 'FECHADO',
                    'bg-amber-50 text-amber-700 border border-amber-200': bim.status === 'AGUARDANDO'
                  }"
                >
                  {{ bim.numero }}ªB
                </div>
                <div>
                  <h3 class="text-sm font-bold text-gray-900">{{ bim.nome }}</h3>
                  <p class="text-xs text-gray-500 mt-0.5">
                   Abertura: <span class="font-medium text-gray-700">{{ formatarData(bim.data_abertura) }}</span> | 
                    Fechamento Regular: <span class="font-medium text-gray-700">{{ formatarData(bim.data_fechamento_regular) }}</span>
                  </p>
                </div>
              </div>

              <div class="flex items-center gap-2">
                <span 
                  class="px-2.5 py-1 text-xs font-bold rounded-full uppercase tracking-wider"
                  :class="{
                    'bg-emerald-100 text-emerald-800 border border-emerald-200': bim.status === 'ABERTO',
                    'bg-gray-100 text-gray-700 border border-gray-200': bim.status === 'FECHADO',
                    'bg-amber-100 text-amber-800 border border-amber-200': bim.status === 'AGUARDANDO'
                  }"
                >
                  {{ bim.status }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Orientações Institucionais -->
        <div class="bg-blue-50 border border-blue-200 rounded-xl p-5 text-sm text-blue-900 space-y-2">
          <div class="flex items-center gap-2 font-bold text-blue-950">
            <svg class="w-5 h-5 text-blue-700 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 111-18 0 9 9 0 0118 0z" />
            </svg>
            Regras de Governança de Prazos (RN-CAD-04)
          </div>
          <p class="text-xs leading-relaxed text-blue-800">
            1. <strong>Bloqueio Automático:</strong> Às 23h59 da data regular de fechamento de cada bimestre, o sistema bloqueia novos envios para as UORGs que não enviaram o relatório bimestral.
          </p>
          <p class="text-xs leading-relaxed text-blue-800">
            2. <strong>Prazo Excepcional:</strong> A concessão reabre individualmente o formulário de preenchimento para a UORG selecionada. O motivo detalhado é obrigatório (mënimo de 10 caracteres) e fica permanentemente registrado na trilha de auditoria do sistema.
          </p>
        </div>
      </div>

      <!-- Formulário de Prazo Excepcional -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 space-y-4">
        <div class="border-b border-gray-100 pb-3">
          <h2 class="text-base font-bold text-gray-900 flex items-center gap-2">
            <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Conceder Prazo Excepcional
          </h2>
          <p class="text-xs text-gray-500 mt-1">
            Habilite a reabertura de envio de relatório para uma UORG específica.
          </p>
        </div>

        <div v-if="mensagemSucesso" class="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs font-semibold flex items-center gap-2">
          <svg class="w-4 h-4 text-emerald-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          {{ mensagemSucesso }}
        </div>

        <div v-if="mensagemErro" class="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg text-xs font-semibold flex items-center gap-2">
          <svg class="w-4 h-4 text-rose-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
          {{ mensagemErro }}
        </div>

        <form @submit.prevent="solicitarPrazoExcepcional" class="space-y-4">
          <!-- Bimestre -->
          <div>
            <label class="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">Bimestre Alvo *</label>
            <select 
              v-model="formPrazo.bimestre_id" 
              required
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 bg-white"
            >
              <option :value="null" disabled>Selecione o bimestre...</option>
              <option v-for="bim in exercicio?.bimestres" :key="bim.id" :value="bim.id">
                {{ bim.nome }} ({{ bim.status }})
              </option>
            </select>
          </div>

          <!-- UORG -->
          <div>
            <label class="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">Unidade Organizacional (UORG) *</label>
            <select 
              v-model="formPrazo.uorg_id" 
              required
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 bg-white"
            >
              <option :value="null" disabled>Selecione a UORG...</option>
              <optgroup v-for="ger in estrutura" :key="ger.id" :label="ger.sigla + ' - ' + ger.nome">
                <option v-for="uorg in ger.uorgs" :key="uorg.id" :value="uorg.id">
                  {{ uorg.sigla }} - {{ uorg.nome }}
                </option>
              </optgroup>
            </select>
          </div>

          <!-- Data Limite -->
          <div>
            <label class="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">Nova Data Limite de Fechamento *</label>
            <input 
              v-model="formPrazo.data_fim" 
              type="date" 
              required
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <!-- Motivo Obrigatório (RN-CAD-04) -->
          <div>
            <div class="flex justify-between items-center mb-1">
              <label class="text-xs font-bold text-gray-700 uppercase tracking-wider">Justificativa Obrigatória *</label>
              <span class="text-[11px]" :class="formPrazo.motivo.length >= 10 ? 'text-emerald-600' : 'text-amber-600'">
                {{ formPrazo.motivo.length }}/10 caracteres mín.
              </span>
            </div>
            <textarea 
              v-model="formPrazo.motivo" 
              rows="3" 
              required
              placeholder="Informe detalhadamente a justificativa para concessão do prazo excepcional à unidade..."
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            ></textarea>
          </div>

          <button 
            type="submit" 
            :disabled="enviando || formPrazo.motivo.trim().length < 10 || !formPrazo.bimestre_id || !formPrazo.uorg_id || !formPrazo.data_fim"
            class="w-full py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-bold rounded-lg text-sm shadow-sm transition flex items-center justify-center gap-2 cursor-pointer disabled:cursor-not-allowed"
          >
            <svg v-if="enviando" class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
            </svg>
            <span>{{ enviando ? 'Gravando...' : 'Conceder Prazo Excepcional' }}</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { gestaoApi } from '../services/gestaoApi';

const carregando = ref(true);
const enviando = ref(false);
const exercicio = ref<any>(null);
const estrutura = ref<any[]>([]);
const mensagemSucesso = ref('');
const mensagemErro = ref('');

const formPrazo = ref({
  bimestre_id: null as number | null,
  uorg_id: null as number | null,
  data_fim: '',
  motivo: ''
});

const formatarData = (dtStr?: string | null) => {
  if (!dtStr) return 'Não definida';
  const p = dtStr.split('-');
  if (p.length === 3) return `${p[2]}/${p[1]}/${p[0]}`;
  return dtStr;
};

const carregarDados = async () => {
  try {
    carregando.value = true;
    const [exData, estData] = await Promise.all([
      gestaoApi.obterExercicioAtivo(),
      gestaoApi.obterEstrutura()
    ]);
    exercicio.value = exData;
    estrutura.value = estData;
  } catch (err: any) {
    mensagemErro.value = 'Erro ao carregar exercício e estrutura: ' + (err.response?.data?.detail || err.message);
  } finally {
    carregando.value = false;
  }
};

const solicitarPrazoExcepcional = async () => {
  if (!exercicio.value || !formPrazo.value.bimestre_id || !formPrazo.value.uorg_id || !formPrazo.value.data_fim) {
    mensagemErro.value = 'Preencha todos os campos obrigatórios.';
    return;
  }
  if (formPrazo.value.motivo.trim().length < 10) {
    mensagemErro.value = 'A justificativa deve conter no mínimo 10 caracteres.';
    return;
  }

  try {
    enviando.value = true;
    mensagemSucesso.value = '';
    mensagemErro.value = '';

    await gestaoApi.concederPrazoExcepcional({
      exercicio_id: exercicio.value.id,
      bimestre_id: formPrazo.value.bimestre_id,
      uorg_id: formPrazo.value.uorg_id,
      data_fim: formPrazo.value.data_fim,
      motivo: formPrazo.value.motivo.trim()
    });

    mensagemSucesso.value = 'Prazo excepcional concedido com sucesso para a unidade!';
    formPrazo.value = {
      bimestre_id: null,
      uorg_id: null,
      data_fim: '',
      motivo: ''
    };
  } catch (err: any) {
    mensagemErro.value = 'Erro ao conceder prazo: ' + (err.response?.data?.detail || err.message);
  } finally {
    enviando.value = false;
  }
};

onMounted(() => {
  carregarDados();
});
</script>
