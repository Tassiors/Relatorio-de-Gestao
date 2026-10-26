<template>
  <div class="space-y-6 max-w-6xl mx-auto">
    <!-- Header e Controles de Seleção -->
    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div>
        <div class="flex items-center gap-2">
          <router-link to="/matriz" class="text-blue-600 hover:text-blue-800 text-xs font-bold flex items-center gap-1">
            ← Voltar para Matriz
          </router-link>
        </div>
        <h1 class="text-2xl font-black text-gray-900 mt-1 flex items-center gap-2">
          <span>Relatório Bimestral</span>
          <span class="text-sm font-bold px-2.5 py-0.5 rounded-full" :class="getStatusBadgeClass(relatorio.status)">
            {{ getStatusLabel(relatorio.status) }}
          </span>
        </h1>
        <p class="text-xs text-gray-500 mt-0.5">
          {{ relatorio.uorg_sigla }} — {{ relatorio.uorg_nome }} | {{ relatorio.bimestre_nome }}
        </p>
      </div>

      <!-- Indicador de Autosave e Ações Rápidas -->
      <div class="flex flex-wrap items-center gap-3">
        <div class="text-xs text-gray-500 flex items-center gap-1.5 bg-gray-50 px-3 py-1.5 rounded-lg border border-gray-200">
          <span v-if="salvando" class="w-2 h-2 rounded-full bg-amber-500 animate-ping"></span>
          <span v-else class="w-2 h-2 rounded-full bg-emerald-500"></span>
          <span>{{ statusSalvoTexto }}</span>
        </div>

        <button
          v-if="relatorio.id"
          @click="baixarExcel"
          class="px-3 py-1.5 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 text-xs font-bold rounded-lg border border-emerald-200 transition"
        >
          📊 Excel
        </button>

        <button
          v-if="relatorio.id"
          @click="baixarPdf"
          class="px-3 py-1.5 bg-red-50 text-red-700 hover:bg-red-100 text-xs font-bold rounded-lg border border-red-200 transition"
        >
          📄 PDF
        </button>

        <button
          @click="salvarRascunhoManual"
          :disabled="salvando"
          class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-bold rounded-lg transition"
        >
          Salvar Rascunho
        </button>

        <button
          @click="abrirModalEnvio"
          class="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-lg shadow-sm transition"
        >
          Enviar Relatório
        </button>
      </div>
    </div>

    <!-- Alerta de Prazo Excepcional -->
    <div v-if="relatorio.prazo_excepcional" class="bg-blue-50 border-l-4 border-blue-600 p-4 rounded-r-xl shadow-sm">
      <div class="flex items-start gap-3">
        <span class="text-xl">⏱</span>
        <div>
          <h4 class="font-bold text-sm text-blue-900">Prazo Excepcional Concedido para esta Unidade</h4>
          <p class="text-xs text-blue-700 mt-0.5">
            <b>Data Limite:</b> {{ formatarDataHora(relatorio.prazo_excepcional.data_fim) }} | 
            <b>Justificativa Administrativa:</b> {{ relatorio.prazo_excepcional.motivo }}
          </p>
        </div>
      </div>
    </div>

    <!-- Seção 1: Entregas Planejadas -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-4">
      <div class="border-b border-gray-100 pb-3">
        <h2 class="text-lg font-bold text-gray-900 flex items-center gap-2">
          <span class="w-2 h-5 bg-indigo-600 rounded-full"></span>
          1. Entregas Planejadas Pactuadas
        </h2>
        <p class="text-xs text-gray-500 mt-0.5">
          Marque as entregas pactuadas no planejamento que foram concluídas neste bimestre (RN-ENT-01: uma vez concluída, a entrega não reaparecerá para preenchimento futuro).
        </p>
      </div>

      <div v-if="relatorio.itens_entrega && relatorio.itens_entrega.length > 0" class="space-y-3">
        <div 
          v-for="(entrega, idx) in relatorio.itens_entrega" 
          :key="entrega.entrega_id"
          class="p-4 rounded-lg border transition"
          :class="entrega.concluida ? 'bg-emerald-50/50 border-emerald-200' : 'bg-gray-50/50 border-gray-200'"
        >
          <div class="flex items-start gap-3">
            <input
              type="checkbox"
              :id="'ent_' + entrega.entrega_id"
              v-model="entrega.concluida"
              @change="agendarAutosave"
              class="mt-1 w-4 h-4 text-emerald-600 rounded border-gray-300 focus:ring-emerald-500"
            />
            <div class="flex-1">
              <label :for="'ent_' + entrega.entrega_id" class="text-sm font-bold text-gray-800 cursor-pointer">
                {{ idx + 1 }}. {{ entrega.titulo }}
              </label>

              <div class="mt-2">
                <input
                  type="text"
                  v-model="entrega.observacoes"
                  @input="agendarAutosave"
                  placeholder="Observações complementares sobre a entrega (opcional)..."
                  class="w-full text-xs p-2 bg-white rounded border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>
            </div>
            <span v-if="entrega.concluida" class="text-xs font-bold text-emerald-700 bg-emerald-100 px-2.5 py-1 rounded-full">
              Concluída no Bimestre
            </span>
          </div>
        </div>
      </div>
      <div v-else class="text-sm text-gray-400 italic py-4">
        Nenhuma entrega pendente cadastrada para esta UORG.
      </div>
    </div>

    <!-- Seção 2: Indicadores de Gestão -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-4">
      <div class="border-b border-gray-100 pb-3">
        <h2 class="text-lg font-bold text-gray-900 flex items-center gap-2">
          <span class="w-2 h-5 bg-blue-600 rounded-full"></span>
          2. Indicadores de Gestão
        </h2>
        <p class="text-xs text-gray-500 mt-0.5">
          Informe os valores apurados para cada indicador pactuado no exercício. O atingimento da meta é calculado em tempo real.
        </p>
      </div>

      <div class="space-y-4">
        <div 
          v-for="ind in relatorio.itens_indicador" 
          :key="ind.indicador_id"
          class="p-4 rounded-xl border border-gray-200 bg-gray-50/40 space-y-3"
        >
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <div>
              <h3 class="text-sm font-bold text-gray-900">{{ ind.nome }}</h3>
              <p v-if="ind.descricao" class="text-xs text-gray-500 mt-0.5">{{ ind.descricao }}</p>
            </div>

            <!-- Badge de Meta Pactuada -->
            <div class="flex items-center gap-2 text-xs">
              <span class="px-2.5 py-1 bg-blue-50 text-blue-700 font-bold rounded-lg border border-blue-200">
                Meta: {{ formatarMeta(ind) }}
              </span>
              <span class="px-2 py-1 bg-gray-100 text-gray-600 rounded text-[11px]">
                {{ ind.periodicidade }}
              </span>
            </div>
          </div>

          <!-- Campos de Entrada -->
          <div class="grid grid-cols-1 md:grid-cols-12 gap-3 items-start pt-2">
            <!-- Valor Apurado -->
            <div class="md:col-span-4" v-if="!ind.resultado_indisponivel">
              <label class="block text-xs font-semibold text-gray-700 mb-1">Valor Apurado:</label>
              <div class="relative">
                <input
                  type="number"
                  step="any"
                  v-model.number="ind.valor_apurado"
                  @input="onValorApuradoChange(ind)"
                  placeholder="Ex: 85.5"
                  class="w-full text-sm font-bold p-2.5 bg-white rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
                <span class="absolute right-3 top-2.5 text-xs text-gray-400 font-bold">
                  {{ ind.unidade_medida === 'PERCENTUAL' ? '%' : '' }}
                </span>
              </div>
            </div>

            <!-- Status do Atingimento -->
            <div class="md:col-span-4 flex items-center pt-6" v-if="!ind.resultado_indisponivel">
              <span 
                v-if="ind.meta_atingida === true" 
                class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-100 text-emerald-800 text-xs font-extrabold rounded-lg"
              >
                ✓ Meta Atingida
              </span>
              <span 
                v-else-if="ind.meta_atingida === false" 
                class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-100 text-red-800 text-xs font-extrabold rounded-lg"
              >
                ✕ Meta Não Atingida
              </span>
              <span v-else class="text-xs text-gray-400 italic">
                Aguardando preenchimento
              </span>
            </div>

            <!-- Checkbox de Indisponibilidade -->
            <div class="md:col-span-4 flex items-center pt-6">
              <label class="inline-flex items-center gap-2 cursor-pointer text-xs text-gray-600">
                <input
                  type="checkbox"
                  v-model="ind.resultado_indisponivel"
                  @change="onIndisponivelToggle(ind)"
                  class="rounded text-amber-600 focus:ring-amber-500 w-4 h-4"
                />
                <span class="font-medium">Resultado ainda não disponível</span>
              </label>
            </div>
          </div>

          <!-- Justificativa de Indisponibilidade -->
          <div v-if="ind.resultado_indisponivel" class="mt-2 bg-amber-50 p-3 rounded-lg border border-amber-200">
            <label class="block text-xs font-bold text-amber-900 mb-1">
              Justificativa de Indisponibilidade (Obrigatória - mín. 10 caracteres):
            </label>
            <input
              type="text"
              v-model="ind.justificativa_indisponibilidade"
              @input="agendarAutosave"
              placeholder="Ex: Dados aguardando consolidação pelo setor de faturamento..."
              class="w-full text-xs p-2.5 bg-white rounded border border-amber-300 focus:ring-2 focus:ring-amber-500 focus:outline-none"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Seção 3: Destaques e Dificuldades -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Destaques -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-3">
        <h2 class="text-md font-bold text-gray-900 flex items-center justify-between">
          <span class="flex items-center gap-2">
            <span class="w-2 h-4 bg-emerald-600 rounded-full"></span>
            3. Destaques do Bimestre
          </span>
          <span class="text-xs font-normal text-gray-400">
            {{ (relatorio.destaques || '').length }} caracteres
          </span>
        </h2>
        <p class="text-xs text-gray-500">
          Descreva as principais conquistas, inovações ou projetos bem-sucedidos do setor.
        </p>
        <textarea
          v-model="relatorio.destaques"
          @input="agendarAutosave"
          rows="5"
          placeholder="Descreva aqui os fatos relevantes e avanços da unidade neste bimestre..."
          class="w-full text-sm p-3 bg-gray-50/50 rounded-lg border border-gray-200 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
        ></textarea>
      </div>

      <!-- Dificuldades -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-3">
        <h2 class="text-md font-bold text-gray-900 flex items-center justify-between">
          <span class="flex items-center gap-2">
            <span class="w-2 h-4 bg-red-600 rounded-full"></span>
            4. Principais Dificuldades e Entraves
          </span>
          <span class="text-xs font-normal text-gray-400">
            {{ (relatorio.dificuldades || '').length }} caracteres
          </span>
        </h2>
        <p class="text-xs text-gray-500">
          Relate os gargalos operacionais, falta de insumos, processos parados ou desafios.
        </p>
        <textarea
          v-model="relatorio.dificuldades"
          @input="agendarAutosave"
          rows="5"
          placeholder="Descreva aqui os obstáculos enfrentados e apoios necessários da gestão..."
          class="w-full text-sm p-3 bg-gray-50/50 rounded-lg border border-gray-200 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
        ></textarea>
      </div>
    </div>

    <!-- Seção 5: Pareceres / Feedbacks da Gestão -->
    <div v-if="relatorio.feedbacks && relatorio.feedbacks.length > 0" class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-3">
      <h2 class="text-md font-bold text-gray-900 flex items-center gap-2">
        <span class="w-2 h-4 bg-purple-600 rounded-full"></span>
        5. Parecer e Feedback Institucional Recebido
      </h2>
      <div class="space-y-3">
        <div 
          v-for="fb in relatorio.feedbacks" 
          :key="fb.id"
          class="p-4 rounded-xl bg-purple-50/40 border border-purple-100 space-y-2"
        >
          <div class="flex items-center justify-between text-xs">
            <span class="font-bold text-purple-900">{{ fb.autor_nome }} ({{ fb.autor_perfil }})</span>
            <span class="text-gray-400">{{ formatarDataHora(fb.data) }}</span>
          </div>
          <p class="text-sm text-gray-800 leading-relaxed">{{ fb.texto }}</p>
        </div>
      </div>
    </div>

    <!-- Modal de Confirmação de Envio com Validação de Pendências -->
    <div v-if="modalEnvioAberto" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div class="bg-white rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
        <h3 class="text-lg font-black text-gray-900 flex items-center gap-2">
          <span>Confirmar Envio do Relatório</span>
        </h3>

        <!-- Se houver pendências impeditivas -->
        <div v-if="pendenciasEnvio.length > 0" class="bg-red-50 border-l-4 border-red-500 p-3 rounded-r-lg space-y-1">
          <p class="text-xs font-bold text-red-800">Não é possível enviar o relatório. Corrija os itens abaixo:</p>
          <ul class="list-disc list-inside text-xs text-red-700 space-y-0.5">
            <li v-for="(p, i) in pendenciasEnvio" :key="i">{{ p }}</li>
          </ul>
        </div>

        <p v-else class="text-sm text-gray-600">
          Você está prestes a submeter formalmente o relatório de gestão do <b>{{ relatorio.bimestre_nome }}</b> para a <b>{{ relatorio.uorg_sigla }}</b>.
          <span class="block text-xs text-gray-500 mt-2">
            Nota: Enquanto a janela do bimestre estiver aberta, você ainda poderá realizar correções e reenviar o relatório.
          </span>
        </p>

        <div class="flex items-center justify-end gap-3 pt-3 border-t">
          <button 
            @click="modalEnvioAberto = false" 
            class="px-4 py-2 text-xs font-bold text-gray-600 hover:bg-gray-100 rounded-lg transition"
          >
            Voltar
          </button>
          <button 
            v-if="pendenciasEnvio.length === 0"
            @click="confirmarEnvio" 
            class="px-5 py-2 text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow-sm transition"
          >
            Confirmar e Enviar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { gestaoApi, RelatorioDetalhe, IndicadorItem } from '../services/gestaoApi';

const route = useRoute();

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

const salvando = ref(false);
const statusSalvoTexto = ref('Rascunho atualizado');
const modalEnvioAberto = ref(false);
const pendenciasEnvio = ref<string[]>([]);
let timerAutosave: any = null;

async function carregarRelatorio() {
  const bId = Number(route.query.bimestre) || 1;
  const uId = Number(route.query.uorg) || 1;
  const exId = 2026;

  try {
    const data = await gestaoApi.obterRelatorio(exId, bId, uId);
    relatorio.value = data;
    // Calcular metas para valores já preenchidos
    relatorio.value.itens_indicador.forEach(ind => {
      calcularMetaIndicador(ind);
    });
  } catch (err) {
    console.error('Erro ao carregar relatório:', err);
  }
}

function calcularMetaIndicador(ind: IndicadorItem) {
  if (ind.valor_apurado === null || ind.valor_apurado === undefined || ind.meta_valor === null || ind.meta_valor === undefined) {
    ind.meta_atingida = null;
    return;
  }
  const val = ind.valor_apurado;
  const meta = ind.meta_valor;
  const max = ind.meta_valor_max;
  const op = ind.meta_operador || 'MAIOR_IGUAL';

  if (op === 'MAIOR_IGUAL') ind.meta_atingida = val >= meta;
  else if (op === 'MENOR_IGUAL') ind.meta_atingida = val <= meta;
  else if (op === 'IGUAL') ind.meta_atingida = Math.abs(val - meta) < 1e-6;
  else if (op === 'ENTRE') ind.meta_atingida = max !== null && max !== undefined ? (meta <= val && val <= max) : (val >= meta);
}

function onValorApuradoChange(ind: IndicadorItem) {
  calcularMetaIndicador(ind);
  agendarAutosave();
}

function onIndisponivelToggle(ind: IndicadorItem) {
  if (ind.resultado_indisponivel) {
    ind.valor_apurado = null;
    ind.meta_atingida = null;
  }
  agendarAutosave();
}

function agendarAutosave() {
  statusSalvoTexto.value = 'Salvando alterações...';
  if (timerAutosave) clearTimeout(timerAutosave);
  timerAutosave = setTimeout(() => {
    salvarRascunhoManual();
  }, 1500);
}

async function salvarRascunhoManual() {
  salvando.value = true;
  try {
    const payload = {
      exercicio_id: relatorio.value.exercicio_id,
      bimestre_id: relatorio.value.bimestre_id,
      uorg_id: relatorio.value.uorg_id,
      destaques: relatorio.value.destaques,
      dificuldades: relatorio.value.dificuldades,
      itens_entrega: relatorio.value.itens_entrega,
      itens_indicador: relatorio.value.itens_indicador
    };
    const res = await gestaoApi.salvarRascunho(payload);
    relatorio.value.id = res.id;
    relatorio.value.status = res.status;
    const now = new Date();
    statusSalvoTexto.value = `Salvo às ${now.toLocaleTimeString('pt-BR')}`;
  } catch (err) {
    statusSalvoTexto.value = 'Erro ao salvar rascunho';
  } finally {
    salvando.value = false;
  }
}

function abrirModalEnvio() {
  pendenciasEnvio.value = [];
  // Validações
  for (const ind of relatorio.value.itens_indicador) {
    if (ind.nao_aplicavel) continue;
    if (ind.resultado_indisponivel) {
      if (!ind.justificativa_indisponibilidade || ind.justificativa_indisponibilidade.trim().length < 10) {
        pendenciasEnvio.value.push(`Indicador "${ind.nome}": Justificativa de indisponibilidade deve ter mín. 10 caracteres.`);
      }
    } else {
      if (ind.valor_apurado === null || ind.valor_apurado === undefined) {
        pendenciasEnvio.value.push(`Indicador "${ind.nome}": Valor apurado não foi preenchido.`);
      }
    }
  }

  if (!relatorio.value.destaques || relatorio.value.destaques.trim().length < 5) {
    pendenciasEnvio.value.push('O campo "Destaques" é obrigatório (mín. 5 caracteres).');
  }
  if (!relatorio.value.dificuldades || relatorio.value.dificuldades.trim().length < 5) {
    pendenciasEnvio.value.push('O campo "Dificuldades" é obrigatório (mín. 5 caracteres).');
  }

  modalEnvioAberto.value = true;
}

async function confirmarEnvio() {
  salvando.value = true;
  try {
    const payload = {
      relatorio_id: relatorio.value.id,
      exercicio_id: relatorio.value.exercicio_id,
      bimestre_id: relatorio.value.bimestre_id,
      uorg_id: relatorio.value.uorg_id,
      destaques: relatorio.value.destaques,
      dificuldades: relatorio.value.dificuldades,
      itens_entrega: relatorio.value.itens_entrega,
      itens_indicador: relatorio.value.itens_indicador
    };
    const res = await gestaoApi.enviarRelatorio(payload);
    relatorio.value = res;
    modalEnvioAberto.value = false;
    alert('Relatório enviado com sucesso!');
  } catch (err: any) {
    alert(err.response?.data?.detail?.mensagem || 'Erro ao submeter relatório.');
  } finally {
    salvando.value = false;
  }
}

function baixarExcel() {
  if (relatorio.value.id) {
    window.open(gestaoApi.getExcelRelatorioUrl(relatorio.value.id), '_blank');
  }
}

function baixarPdf() {
  if (relatorio.value.id) {
    window.open(gestaoApi.getPdfRelatorioUrl(relatorio.value.id), '_blank');
  }
}

function formatarMeta(ind: IndicadorItem) {
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

function getStatusLabel(status: string) {
  switch (status) {
    case 'ENVIADO': return 'Enviado';
    case 'EM_EDICAO': return 'Em Edição';
    case 'PRAZO_EXCEPCIONAL': return 'Prazo Excepcional';
    default: return 'Rascunho';
  }
}

function formatarDataHora(isoStr?: string | null) {
  if (!isoStr) return '';
  const dt = new Date(isoStr);
  return dt.toLocaleString('pt-BR');
}

onMounted(() => {
  carregarRelatorio();
});
</script>
