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
          Controle operacional manual dos bimestres (abertura/fechamento e datas limite) e concessão de prazos excepcionais.
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
      <!-- Calendário Anual de Bimestres (Controle Manual pelo Administrador) -->
      <div class="lg:col-span-2 space-y-6">
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="p-5 border-b border-gray-100 flex items-center justify-between">
            <div>
              <h2 class="text-base font-bold text-gray-900 flex items-center gap-2">
                <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Calendário Bimestral de Acompanhamento ({{ exercicio?.ano }})
              </h2>
              <p class="text-xs text-gray-500 mt-0.5">
                Altere manualmente o status de abertura/fechamento e defina a data limite operacional de cada bimestre.
              </p>
            </div>
            <span class="text-xs text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-full font-bold">Gestão Manual</span>
          </div>

          <div v-if="mensagemBimestre" class="mx-5 mt-4 p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs font-semibold flex items-center justify-between">
            <span>✓ {{ mensagemBimestre }}</span>
            <button @click="mensagemBimestre = ''" class="text-emerald-700 font-bold">✕</button>
          </div>

          <div class="divide-y divide-gray-100">
            <div 
              v-for="bim in exercicio?.bimestres" 
              :key="bim.id"
              class="p-4 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-gray-50/80 transition"
            >
              <div class="flex items-center gap-3">
                <div 
                  class="w-11 h-11 rounded-xl flex items-center justify-center font-black text-sm shrink-0"
                  :class="{
                    'bg-emerald-100 text-emerald-800 border border-emerald-300': bim.status === 'ABERTO',
                    'bg-gray-100 text-gray-600 border border-gray-200': bim.status === 'FECHADO',
                    'bg-amber-50 text-amber-700 border border-amber-200': bim.status === 'AGUARDANDO'
                  }"
                >
                  {{ bim.numero }}ºB
                </div>
                <div>
                  <div class="flex items-center gap-2">
                    <h3 class="text-sm font-bold text-gray-900">{{ bim.nome }}</h3>
                    <span 
                      class="px-2 py-0.5 text-[10px] font-bold rounded-full uppercase tracking-wider"
                      :class="{
                        'bg-emerald-100 text-emerald-800 border border-emerald-200': bim.status === 'ABERTO',
                        'bg-gray-100 text-gray-700 border border-gray-200': bim.status === 'FECHADO',
                        'bg-amber-100 text-amber-800 border border-amber-200': bim.status === 'AGUARDANDO'
                      }"
                    >
                      {{ bim.status }}
                    </span>
                  </div>
                  <p class="text-xs text-gray-500 mt-0.5">
                    Abertura: <span class="font-medium text-gray-700">{{ formatarData(bim.data_abertura) }}</span> | 
                    Data Limite Atual: <span class="font-semibold text-indigo-700">{{ formatarData(bim.data_fechamento_regular) }}</span>
                  </p>
                </div>
              </div>

              <!-- Controles Manuais do Administrador por Bimestre -->
              <div class="flex flex-wrap items-center gap-2">
                <div class="flex items-center gap-1.5">
                  <label class="text-[11px] font-bold text-gray-500 uppercase">Status:</label>
                  <select
                    v-model="edicaoBimestres[bim.id].status"
                    class="text-xs font-semibold border border-gray-300 rounded-lg px-2.5 py-1.5 bg-white focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="ABERTO">ABERTO</option>
                    <option value="FECHADO">FECHADO</option>
                  </select>
                </div>

                <div class="flex items-center gap-1.5">
                  <label class="text-[11px] font-bold text-gray-500 uppercase">Fechamento:</label>
                  <input
                    v-model="edicaoBimestres[bim.id].data_fechamento_regular"
                    type="date"
                    class="text-xs border border-gray-300 rounded-lg px-2.5 py-1.5 bg-white focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <button
                  type="button"
                  @click="salvarConfiguracaoBimestre(bim.id)"
                  :disabled="salvandoBimestreId === bim.id"
                  class="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-xs font-bold rounded-lg shadow-sm transition cursor-pointer"
                >
                  {{ salvandoBimestreId === bim.id ? 'Salvando...' : 'Salvar' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Formulário de Prazo Excepcional + Texto Explicativo Integrado -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 space-y-4">
        <div class="border-b border-gray-100 pb-3">
          <h2 class="text-base font-bold text-gray-900 flex items-center gap-2">
            <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Conceder Prazo Excepcional
          </h2>
          <p class="text-xs text-gray-500 mt-1">
            Habilite a reabertura individual do formulário para uma UORG específica.
          </p>
        </div>

        <!-- Texto Explicativo Integrado na Seção de Concessão de Prazo Excepcional -->
        <div class="bg-blue-50 border border-blue-200 rounded-xl p-3.5 text-xs text-blue-900 space-y-1.5">
          <div class="flex items-center gap-1.5 font-bold text-blue-950">
            <svg class="w-4 h-4 text-blue-700 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Sobre a Concessão de Prazo Excepcional
          </div>
          <p class="leading-relaxed text-blue-800">
            A concessão de prazo excepcional libera pontualmente o preenchimento e reenvio do relatório bimestral para a UORG selecionada até a nova data limite informada, registrando a liberação na trilha de auditoria do sistema.
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

          <!-- Motivo Opcional -->
          <div>
            <div class="flex justify-between items-center mb-1">
              <label class="text-xs font-bold text-gray-700 uppercase tracking-wider">Justificativa / Observação (Opcional)</label>
              <span class="text-[11px] text-gray-400">Opcional</span>
            </div>
            <textarea 
              v-model="formPrazo.motivo" 
              rows="3" 
              placeholder="Se desejar, registre uma justificativa ou observação para a concessão do prazo excepcional..."
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            ></textarea>
          </div>

          <button 
            type="submit" 
            :disabled="enviando || !formPrazo.bimestre_id || !formPrazo.uorg_id || !formPrazo.data_fim"
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
const salvandoBimestreId = ref<number | null>(null);
const exercicio = ref<any>(null);
const estrutura = ref<any[]>([]);
const mensagemSucesso = ref('');
const mensagemErro = ref('');
const mensagemBimestre = ref('');

const edicaoBimestres = ref<Record<number, { status: string; data_fechamento_regular: string }>>({});

const formPrazo = ref({
  bimestre_id: null as number | null,
  uorg_id: null as number | null,
  data_fim: '',
  motivo: ''
});

const formatarData = (dtStr?: string | null) => {
  if (!dtStr) return 'Não definida';
  const clean = dtStr.split('T')[0];
  const p = clean.split('-');
  if (p.length === 3) return `${p[2]}/${p[1]}/${p[0]}`;
  return dtStr;
};

const inicializarEdicaoBimestres = (bims: any[]) => {
  const mapa: Record<number, { status: string; data_fechamento_regular: string }> = {};
  for (const b of bims || []) {
    mapa[b.id] = {
      status: b.status === 'ABERTO' ? 'ABERTO' : 'FECHADO',
      data_fechamento_regular: b.data_fechamento_regular ? b.data_fechamento_regular.split('T')[0] : ''
    };
  }
  edicaoBimestres.value = mapa;
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
    inicializarEdicaoBimestres(exData?.bimestres || []);
  } catch (err: any) {
    mensagemErro.value = 'Erro ao carregar exercício e estrutura: ' + (err.response?.data?.detail || err.message);
  } finally {
    carregando.value = false;
  }
};

const salvarConfiguracaoBimestre = async (bimestreId: number) => {
  const cfg = edicaoBimestres.value[bimestreId];
  if (!cfg) return;
  try {
    salvandoBimestreId.value = bimestreId;
    mensagemBimestre.value = '';
    mensagemErro.value = '';
    const atualizado = await gestaoApi.atualizarBimestre(bimestreId, {
      status: cfg.status,
      data_fechamento_regular: cfg.data_fechamento_regular || ''
    });
    if (exercicio.value?.bimestres) {
      const idx = exercicio.value.bimestres.findIndex((b: any) => b.id === bimestreId);
      if (idx !== -1) {
        exercicio.value.bimestres[idx] = {
          ...exercicio.value.bimestres[idx],
          status: atualizado.status,
          data_abertura: atualizado.data_abertura,
          data_fechamento_regular: atualizado.data_fechamento_regular
        };
      }
    }
    mensagemBimestre.value = `${atualizado.nome} atualizado com sucesso (${atualizado.status})!`;
  } catch (err: any) {
    mensagemErro.value = 'Erro ao atualizar bimestre: ' + (err.response?.data?.detail || err.message);
  } finally {
    salvandoBimestreId.value = null;
  }
};

const solicitarPrazoExcepcional = async () => {
  if (!exercicio.value || !formPrazo.value.bimestre_id || !formPrazo.value.uorg_id || !formPrazo.value.data_fim) {
    mensagemErro.value = 'Preencha todos os campos obrigatórios.';
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
      motivo: formPrazo.value.motivo.trim() || undefined
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
