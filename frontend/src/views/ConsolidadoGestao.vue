<template>
  <div class="space-y-6 max-w-6xl mx-auto pb-10 print:max-w-none print:space-y-4 print:pb-0">
    <!-- Cabeçalho Institucional Exclusivo para Impressão (@media print) -->
    <div class="hidden print:flex items-center justify-between border-b-2 border-gray-800 pb-4 mb-4">
      <div>
        <p class="text-[10px] font-black uppercase tracking-widest text-gray-500">
          EBSERH — Hospital das Clínicas da UFPE (HC-UFPE)
        </p>
        <h1 class="text-xl font-black text-gray-900 mt-0.5">
          Relatório Consolidado de Gestão Bimestral
        </h1>
        <p class="text-xs font-bold text-gray-700 mt-0.5">
          Unidade: [{{ relatorio.uorg_sigla }}] {{ relatorio.uorg_nome }} | Competência: {{ relatorio.bimestre_nome }} (Exercício {{ relatorio.exercicio_id || 2026 }})
        </p>
      </div>
      <div class="text-right text-[10px] text-gray-600">
        <p class="font-bold">Status: {{ formatarStatusLabel(relatorio.status) }}</p>
        <p>Versão: v{{ relatorio.versao || 1 }}</p>
        <p>Impresso em: {{ dataHoraImpressao }}</p>
      </div>
    </div>

    <!-- Barra Superior Executiva: Título, Navegação Sequencial e Ações (Oculta na Impressão) -->
    <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 print:hidden">
      <div>
        <div class="flex items-center gap-2">
          <span class="w-3 h-7 bg-gradient-to-b from-purple-600 to-indigo-700 rounded-full"></span>
          <h1 class="text-2xl font-black text-gray-900 tracking-tight">
            Visão Consolidada de Gestão
          </h1>
          <span
            v-if="escopoLabel"
            class="ml-1 text-[10px] font-extrabold uppercase tracking-wider px-2.5 py-1 rounded-full bg-purple-50 text-purple-700 border border-purple-200"
          >
            {{ escopoLabel }}
          </span>
        </div>
        <p class="text-xs text-gray-500 mt-1">
          Acompanhamento executivo de entregas, metas de indicadores, análise crítica e pareceres institucionais.
        </p>
      </div>

      <!-- Ações Executivas: Imprimir Relatório, Exportar Excel/PDF e Navegação Sequencial -->
      <div class="flex flex-wrap items-center gap-2">
        <button
          type="button"
          @click="imprimirRelatorio"
          class="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold rounded-xl shadow-xs transition flex items-center gap-1.5 cursor-pointer"
          title="Imprimir ou salvar esta visão consolidada em formato de relatório executivo"
        >
          <span>🖨️</span>
          <span>Imprimir Relatório</span>
        </button>

        <a
          v-if="relatorio.id"
          :href="gestaoApi.getExcelRelatorioUrl(relatorio.id)"
          download
          class="px-3 py-2 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 text-xs font-bold rounded-xl border border-emerald-200 transition flex items-center gap-1"
        >
          <span>📊</span>
          <span>Excel</span>
        </a>
        <a
          v-if="relatorio.id"
          :href="gestaoApi.getPdfRelatorioUrl(relatorio.id)"
          download
          class="px-3 py-2 bg-rose-50 text-rose-700 hover:bg-rose-100 text-xs font-bold rounded-xl border border-rose-200 transition flex items-center gap-1"
        >
          <span>📄</span>
          <span>PDF Oficial</span>
        </a>

        <!-- Navegação Sequencial: Anterior / Próximo -->
        <div v-if="uorgsFiltradas.length > 1" class="flex items-center gap-1.5 pl-2 border-l border-gray-200">
          <button
            type="button"
            @click="navegarRelatorio(-1)"
            :disabled="indiceUorgAtual <= 0"
            class="px-3 py-2 bg-gray-100 hover:bg-gray-200 disabled:opacity-40 text-gray-700 text-xs font-bold rounded-xl transition cursor-pointer"
          >
            ← Anterior
          </button>

          <span class="text-[11px] text-gray-600 font-extrabold px-2 py-1 bg-gray-50 rounded-lg border border-gray-200">
            {{ indiceUorgAtual + 1 }} / {{ uorgsFiltradas.length }}
          </span>

          <button
            type="button"
            @click="navegarRelatorio(1)"
            :disabled="indiceUorgAtual >= uorgsFiltradas.length - 1"
            class="px-3 py-2 bg-gray-100 hover:bg-gray-200 disabled:opacity-40 text-gray-700 text-xs font-bold rounded-xl transition cursor-pointer"
          >
            Próximo →
          </button>
        </div>
      </div>
    </div>

    <!-- Barra de Filtros: Gerência (SUP/Admin), Unidade (UORG) e Seletor Rápido de Bimestres (Oculta na Impressão) -->
    <div class="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 space-y-3 print:hidden">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <!-- Botões de Gerência (para Superintendente e Administrador) -->
        <div v-if="exibirBotoesGerencia" class="flex flex-wrap items-center gap-1.5">
          <span class="text-[11px] font-extrabold text-gray-400 uppercase tracking-wider mr-1">Gerência:</span>
          <button
            type="button"
            @click="selecionarGerencia('')"
            class="px-2.5 py-1 rounded-lg text-xs font-bold transition cursor-pointer border"
            :class="gerenciaFiltro === ''
              ? 'bg-purple-600 text-white border-purple-600 shadow-xs'
              : 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100'"
          >
            Todas
          </button>
          <button
            v-for="ger in gerenciasPrincipais"
            :key="ger"
            type="button"
            @click="selecionarGerencia(ger)"
            class="px-2.5 py-1 rounded-lg text-xs font-bold transition cursor-pointer border"
            :class="gerenciaFiltro === ger
              ? 'bg-purple-600 text-white border-purple-600 shadow-xs'
              : 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100'"
          >
            {{ ger }}
          </button>
        </div>

        <!-- Seletor de Unidade (UORG) no Escopo do Usuário -->
        <div class="flex items-center gap-2 flex-1 min-w-[260px]">
          <label class="text-xs font-extrabold text-gray-500 uppercase tracking-wider whitespace-nowrap">
            Unidade (UORG):
          </label>
          <select
            v-model="uorgSelecionadaId"
            @change="onUorgSelectChange"
            :disabled="uorgsFiltradas.length <= 1"
            class="flex-1 text-xs font-bold p-2.5 bg-gray-50 rounded-xl border border-gray-200 text-gray-800 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-80"
          >
            <option v-for="u in uorgsFiltradas" :key="u.id" :value="u.id">
              [{{ u.sigla }}] {{ u.nome }} ({{ u.tipo_uorg || 'UORG' }})
            </option>
          </select>
        </div>
      </div>

      <!-- Pílulas de Seleção Rápida de Bimestre -->
      <div class="flex flex-wrap items-center gap-2 pt-2 border-t border-gray-100">
        <span class="text-[11px] font-extrabold text-gray-400 uppercase tracking-wider mr-1">Competência:</span>
        <button
          v-for="b in bimestres"
          :key="b.id"
          type="button"
          @click="selecionarBimestre(b.id)"
          class="px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 cursor-pointer border"
          :class="bimestreSelecionadoId === b.id
            ? 'bg-indigo-600 text-white border-indigo-600 shadow-xs'
            : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'"
        >
          <span>{{ b.nome }}</span>
          <span
            v-if="b.status === 'ABERTO'"
            class="text-[9px] uppercase px-1.5 py-0.2 rounded-full font-extrabold"
            :class="bimestreSelecionadoId === b.id ? 'bg-white/20 text-white' : 'bg-emerald-100 text-emerald-700'"
          >
            Aberto
          </span>
        </button>
      </div>
    </div>

    <!-- Estado de Carregamento -->
    <div v-if="carregando" class="bg-white rounded-2xl p-12 text-center shadow-sm border border-gray-100">
      <div class="inline-block w-8 h-8 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin mb-3"></div>
      <p class="text-sm font-bold text-gray-500">Carregando dados consolidados do relatório...</p>
    </div>

    <!-- Conteúdo Principal do Relatório Executivo -->
    <div v-else class="space-y-6 print:space-y-4">
      <!-- Banner de Destaque Máximo quando o Relatório Possui Feedback Institucional -->
      <div
        v-if="temFeedbackInstitucional"
        class="bg-gradient-to-r from-amber-500 via-orange-500 to-purple-700 p-0.5 rounded-2xl shadow-md print:border-2 print:border-amber-600"
      >
        <div class="bg-gradient-to-r from-amber-50/95 via-white to-purple-50/95 rounded-[14px] px-5 py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div class="flex items-start gap-3.5">
            <div class="w-11 h-11 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 text-white flex items-center justify-center text-xl shadow-sm shrink-0">
              🏛️
            </div>
            <div>
              <div class="flex flex-wrap items-center gap-2">
                <span class="text-[10px] font-black uppercase tracking-widest px-2.5 py-0.5 rounded-full bg-amber-500 text-white shadow-2xs">
                  Parecer Institucional Registrado
                </span>
                <span class="text-xs font-bold text-purple-900">
                  {{ relatorio.feedbacks.length }} {{ relatorio.feedbacks.length === 1 ? 'avaliação emitida' : 'avaliações emitidas' }} pela Alta Gestão
                </span>
              </div>
              <p class="text-xs text-gray-800 font-semibold mt-1 line-clamp-2">
                “{{ relatorio.feedbacks[relatorio.feedbacks.length - 1]?.texto }}”
              </p>
              <p class="text-[11px] text-gray-500 mt-0.5">
                Último parecer por <strong class="text-gray-700">{{ relatorio.feedbacks[relatorio.feedbacks.length - 1]?.autor_nome }}</strong>
                ({{ relatorio.feedbacks[relatorio.feedbacks.length - 1]?.autor_perfil }})
                <span v-if="relatorio.feedbacks[relatorio.feedbacks.length - 1]?.data">
                  em {{ formatarData(relatorio.feedbacks[relatorio.feedbacks.length - 1]?.data || '') }}
                </span>
              </p>
            </div>
          </div>

          <a
            href="#secao-pareceres-institucionais"
            class="px-4 py-2 rounded-xl bg-purple-700 hover:bg-purple-800 text-white text-xs font-extrabold shadow-xs transition shrink-0 text-center print:hidden"
          >
            Ver Parecer Completo ↓
          </a>
        </div>
      </div>

      <!-- Cabeçalho Executivo da Unidade e Cartões de KPI -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden print:border print:border-gray-300 print:shadow-none">
        <!-- Faixa de Identificação da UORG -->
        <div class="bg-gradient-to-r from-slate-900 via-indigo-950 to-purple-950 text-white p-6 print:bg-none print:text-gray-900 print:p-4 print:border-b print:border-gray-200">
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div class="flex flex-wrap items-center gap-2 mb-1.5">
                <span class="px-2.5 py-0.5 rounded-md bg-white/15 text-white text-xs font-black tracking-wider uppercase print:bg-gray-200 print:text-gray-900">
                  {{ relatorio.uorg_sigla }}
                </span>
                <span
                  v-if="uorgAtualInfo?.gerencia_sigla"
                  class="px-2 py-0.5 rounded-md bg-purple-500/30 border border-purple-400/30 text-purple-100 text-[11px] font-bold print:bg-gray-100 print:text-gray-700"
                >
                  Vinculação: {{ uorgAtualInfo.gerencia_sigla }}
                </span>
                <span
                  v-if="uorgAtualInfo?.tipo_uorg"
                  class="px-2 py-0.5 rounded-md bg-indigo-500/30 border border-indigo-400/30 text-indigo-100 text-[11px] font-bold print:bg-gray-100 print:text-gray-700"
                >
                  {{ uorgAtualInfo.tipo_uorg }}
                </span>
              </div>
              <h2 class="text-xl md:text-2xl font-black tracking-tight">
                {{ relatorio.uorg_nome }}
              </h2>
              <p class="text-xs text-slate-300 mt-1 print:text-gray-600">
                Competência: <strong class="text-white print:text-gray-900">{{ relatorio.bimestre_nome }}</strong>
                <span class="mx-2">•</span>
                Exercício: <strong class="text-white print:text-gray-900">{{ relatorio.exercicio_id || 2026 }}</strong>
                <span class="mx-2">•</span>
                Versão do Documento: <strong class="text-white print:text-gray-900">v{{ relatorio.versao || 0 }}</strong>
              </p>
            </div>

            <div class="flex flex-col items-start md:items-end gap-2">
              <span
                class="text-xs font-black px-3.5 py-1.5 rounded-full uppercase tracking-wider shadow-xs"
                :class="getStatusBadgeClass(relatorio.status)"
              >
                {{ formatarStatusLabel(relatorio.status) }}
              </span>
              <span v-if="relatorio.data_envio" class="text-[11px] text-slate-300 print:text-gray-600">
                Enviado em {{ formatarData(relatorio.data_envio) }} por <strong>{{ relatorio.usuario_envio || 'Chefia' }}</strong>
              </span>
              <span v-else class="text-[11px] text-amber-300 font-semibold print:text-gray-600">
                Relatório ainda não submetido oficialmente neste bimestre
              </span>
            </div>
          </div>
        </div>

        <!-- 4 Cartões Executivos de Resumo (KPIs do Bimestre) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 divide-y sm:divide-y-0 sm:divide-x divide-gray-100 bg-white">
          <!-- KPI 1: Entregas -->
          <div class="p-5 flex flex-col justify-between">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-extrabold uppercase tracking-wider text-gray-400">Entregas Concluídas</span>
              <span class="text-xs font-black px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700">
                {{ percentualEntregas }}%
              </span>
            </div>
            <div class="mt-2 flex items-baseline gap-1.5">
              <span class="text-2xl font-black text-gray-900">{{ entregasConcluidasCount }}</span>
              <span class="text-xs font-bold text-gray-400">de {{ totalEntregasCount }} entregas</span>
            </div>
            <div class="mt-3 w-full h-2 bg-gray-100 rounded-full overflow-hidden">
              <div
                class="h-full bg-emerald-500 rounded-full transition-all duration-500"
                :style="{ width: `${percentualEntregas}%` }"
              ></div>
            </div>
          </div>

          <!-- KPI 2: Indicadores -->
          <div class="p-5 flex flex-col justify-between">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-extrabold uppercase tracking-wider text-gray-400">Metas Atingidas</span>
              <span class="text-xs font-black px-2 py-0.5 rounded-md bg-blue-50 text-blue-700">
                {{ percentualMetas }}%
              </span>
            </div>
            <div class="mt-2 flex items-baseline gap-1.5">
              <span class="text-2xl font-black text-gray-900">{{ metasAtingidasCount }}</span>
              <span class="text-xs font-bold text-gray-400">de {{ totalIndicadoresCount }} indicadores</span>
            </div>
            <div class="mt-3 w-full h-2 bg-gray-100 rounded-full overflow-hidden">
              <div
                class="h-full bg-blue-600 rounded-full transition-all duration-500"
                :style="{ width: `${percentualMetas}%` }"
              ></div>
            </div>
          </div>

          <!-- KPI 3: Protocolo / Responsável -->
          <div class="p-5 flex flex-col justify-between">
            <span class="text-[11px] font-extrabold uppercase tracking-wider text-gray-400">Situação de Submissão</span>
            <div class="mt-2">
              <p class="text-sm font-black text-gray-900 truncate">
                {{ relatorio.data_envio ? formatarData(relatorio.data_envio) : 'Pendente de Envio' }}
              </p>
              <p class="text-xs text-gray-500 mt-0.5 truncate">
                Responsável: <strong class="text-gray-700">{{ relatorio.usuario_envio || 'Não registrado' }}</strong>
              </p>
            </div>
            <div class="mt-2">
              <span class="text-[10px] font-bold text-gray-400 uppercase">
                Bimestre {{ relatorio.bimestre_status || 'ABERTO' }}
              </span>
            </div>
          </div>

          <!-- KPI 4: Avaliação Institucional -->
          <div
            class="p-5 flex flex-col justify-between"
            :class="temFeedbackInstitucional ? 'bg-amber-50/40' : ''"
          >
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-extrabold uppercase tracking-wider text-gray-400">Avaliação Institucional</span>
              <span v-if="temFeedbackInstitucional" class="text-sm">🏛️</span>
            </div>
            <div class="mt-2">
              <p
                class="text-sm font-black"
                :class="temFeedbackInstitucional ? 'text-amber-800' : 'text-gray-700'"
              >
                {{ temFeedbackInstitucional ? `${relatorio.feedbacks.length} Parecer(es) Emitido(s)` : 'Sem Parecer Registrado' }}
              </p>
              <p class="text-xs text-gray-500 mt-0.5">
                {{ temFeedbackInstitucional ? 'Avaliado pela Superintendência / Gestão' : 'Aguardando avaliação da Alta Gestão' }}
              </p>
            </div>
            <div class="mt-2">
              <span
                class="inline-block text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full"
                :class="temFeedbackInstitucional ? 'bg-amber-200/80 text-amber-900' : 'bg-gray-100 text-gray-500'"
              >
                {{ temFeedbackInstitucional ? 'Com Feedback Institucional' : 'Em Análise' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Seção 1: Entregas Planejadas -->
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 space-y-4 print:border print:border-gray-300 print:shadow-none print:break-inside-avoid">
        <div class="flex items-center justify-between border-b border-gray-100 pb-3">
          <div class="flex items-center gap-2.5">
            <span class="w-7 h-7 rounded-lg bg-emerald-100 text-emerald-800 font-black text-xs flex items-center justify-center">
              01
            </span>
            <div>
              <h3 class="text-base font-black text-gray-900">Entregas Planejadas para o Exercício</h3>
              <p class="text-[11px] text-gray-500">Acompanhamento físico e qualitativo das entregas pactuadas pela unidade.</p>
            </div>
          </div>
          <span class="text-xs font-extrabold px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
            {{ entregasConcluidasCount }} / {{ totalEntregasCount }} Concluídas
          </span>
        </div>

        <div v-if="relatorio.itens_entrega && relatorio.itens_entrega.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div
            v-for="ent in relatorio.itens_entrega"
            :key="ent.entrega_id"
            class="p-4 rounded-xl border transition flex flex-col justify-between gap-3"
            :class="ent.concluida
              ? 'bg-emerald-50/40 border-emerald-200'
              : 'bg-gray-50/70 border-gray-200'"
          >
            <div class="space-y-1.5">
              <div class="flex items-start justify-between gap-2">
                <div class="flex items-center gap-1.5 flex-wrap">
                  <span class="text-sm font-extrabold text-gray-900">{{ ent.titulo }}</span>
                  <span
                    v-if="ent.concluida_anteriormente && ent.bimestre_conclusao_nome"
                    class="text-[9px] font-black uppercase px-1.5 py-0.5 rounded bg-indigo-100 text-indigo-800"
                  >
                    Concluída no {{ ent.bimestre_conclusao_nome }}
                  </span>
                </div>
                <span
                  class="shrink-0 font-extrabold px-2.5 py-0.5 rounded-full text-[10px] uppercase tracking-wider"
                  :class="ent.concluida ? 'bg-emerald-600 text-white' : 'bg-amber-100 text-amber-800 border border-amber-200'"
                >
                  {{ ent.concluida ? '✓ Concluída' : 'Em Andamento' }}
                </span>
              </div>

              <p v-if="ent.observacoes" class="text-xs text-gray-700 bg-white/80 p-2 rounded-lg border border-gray-200/70 mt-1">
                <strong class="text-gray-900">Andamento / Observações:</strong> {{ ent.observacoes }}
              </p>
            </div>

            <!-- Barra de Status da Entrega -->
            <div class="pt-2 border-t border-gray-200/60 flex items-center justify-between gap-3 text-[11px]">
              <span class="font-bold text-gray-500">Execução Física</span>
              <div class="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full"
                  :class="ent.concluida ? 'bg-emerald-500' : 'bg-amber-400'"
                  :style="{ width: `${ent.concluida ? 100 : 25}%` }"
                ></div>
              </div>
              <span class="font-black text-gray-800">
                {{ ent.concluida ? '100%' : 'Pendente' }}
              </span>
            </div>
          </div>
        </div>
        <p v-else class="text-xs text-gray-400 italic py-4 text-center">
          Nenhuma entrega planejada cadastrada para esta unidade neste exercício.
        </p>
      </div>

      <!-- Seção 2: Indicadores de Gestão e Metas -->
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 space-y-4 print:border print:border-gray-300 print:shadow-none print:break-inside-avoid">
        <div class="flex items-center justify-between border-b border-gray-100 pb-3">
          <div class="flex items-center gap-2.5">
            <span class="w-7 h-7 rounded-lg bg-blue-100 text-blue-800 font-black text-xs flex items-center justify-center">
              02
            </span>
            <div>
              <h3 class="text-base font-black text-gray-900">Indicadores de Desempenho e Metas</h3>
              <p class="text-[11px] text-gray-500">Resultados apurados no bimestre em comparação com as metas pactuadas.</p>
            </div>
          </div>
          <span class="text-xs font-extrabold px-3 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
            {{ metasAtingidasCount }} / {{ totalIndicadoresCount }} Metas Atingidas
          </span>
        </div>

        <div v-if="relatorio.itens_indicador && relatorio.itens_indicador.length > 0" class="overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="bg-slate-50 text-slate-600 font-extrabold uppercase text-[10px] tracking-wider border-y border-gray-200">
                <th class="p-3.5">Indicador</th>
                <th class="p-3.5 text-center">Meta Pactuada</th>
                <th class="p-3.5 text-center">Valor Apurado</th>
                <th class="p-3.5 text-center">Situação da Meta</th>
                <th class="p-3.5">Análise / Justificativa</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr
                v-for="ind in relatorio.itens_indicador"
                :key="ind.indicador_id"
                class="hover:bg-gray-50/70 transition"
              >
                <td class="p-3.5">
                  <div class="font-extrabold text-gray-900">{{ ind.nome }}</div>
                  <div class="text-[10px] text-gray-400 mt-0.5 flex items-center gap-2">
                    <span v-if="ind.periodicidade">Periodicidade: {{ ind.periodicidade }}</span>
                    <span v-if="ind.unidade_medida">• Unidade: {{ ind.unidade_medida }}</span>
                    <span v-if="ind.competencia">• Competência: {{ ind.competencia }}</span>
                  </div>
                </td>
                <td class="p-3.5 text-center">
                  <span class="font-black text-blue-700 bg-blue-50 px-2.5 py-1 rounded-lg border border-blue-100">
                    {{ formatarMeta(ind) }}
                  </span>
                </td>
                <td class="p-3.5 text-center">
                  <span
                    v-if="ind.resultado_indisponivel"
                    class="text-[11px] font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded"
                  >
                    Indisponível
                  </span>
                  <span
                    v-else-if="ind.valor_apurado !== null && ind.valor_apurado !== undefined"
                    class="text-sm font-black text-gray-900"
                  >
                    {{ formatarValorIndicador(ind.valor_apurado, ind.unidade_medida) }}
                  </span>
                  <span v-else class="text-gray-400 font-bold">—</span>
                </td>
                <td class="p-3.5 text-center">
                  <span
                    v-if="ind.meta_atingida === true"
                    class="inline-flex items-center gap-1 px-2.5 py-1 bg-emerald-100 text-emerald-800 font-extrabold rounded-full text-[11px]"
                  >
                    ✓ Atingida
                  </span>
                  <span
                    v-else-if="ind.meta_atingida === false"
                    class="inline-flex items-center gap-1 px-2.5 py-1 bg-rose-100 text-rose-800 font-extrabold rounded-full text-[11px]"
                  >
                    ✕ Não Atingida
                  </span>
                  <span
                    v-else-if="ind.resultado_indisponivel"
                    class="inline-flex items-center gap-1 px-2.5 py-1 bg-amber-100 text-amber-800 font-bold rounded-full text-[11px]"
                  >
                    Justificado
                  </span>
                  <span v-else class="text-gray-400 font-semibold">Não Apurado</span>
                </td>
                <td class="p-3.5 text-gray-600 italic max-w-xs">
                  {{ ind.justificativa_indisponibilidade || 'Sem ressalvas adicionais.' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="text-xs text-gray-400 italic py-4 text-center">
          Nenhum indicador pactuado cadastrado para esta unidade neste exercício.
        </p>
      </div>

      <!-- Seções 3 e 4: Destaques Operacionais e Principais Dificuldades -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 print:grid-cols-2 print:gap-4 print:break-inside-avoid">
        <!-- 3. Destaques Operacionais -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-emerald-100 space-y-3 print:border print:border-gray-300 print:shadow-none">
          <div class="flex items-center gap-2.5 border-b border-emerald-100 pb-3">
            <span class="w-7 h-7 rounded-lg bg-emerald-100 text-emerald-800 font-black text-xs flex items-center justify-center">
              03
            </span>
            <div>
              <h4 class="font-black text-sm text-emerald-950">Destaques Operacionais e Avanços</h4>
              <p class="text-[11px] text-gray-500">Principais conquistas e boas práticas registradas no bimestre.</p>
            </div>
          </div>
          <div class="bg-emerald-50/40 p-4 rounded-xl border border-emerald-100/80 min-h-[110px]">
            <p class="text-xs text-gray-800 leading-relaxed whitespace-pre-wrap">
              {{ relatorio.destaques || 'Nenhum destaque operacional informado neste bimestre.' }}
            </p>
          </div>
        </div>

        <!-- 4. Principais Dificuldades -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-rose-100 space-y-3 print:border print:border-gray-300 print:shadow-none">
          <div class="flex items-center gap-2.5 border-b border-rose-100 pb-3">
            <span class="w-7 h-7 rounded-lg bg-rose-100 text-rose-800 font-black text-xs flex items-center justify-center">
              04
            </span>
            <div>
              <h4 class="font-black text-sm text-rose-950">Principais Dificuldades e Pontos de Atenção</h4>
              <p class="text-[11px] text-gray-500">Gargalos operacionais, riscos e demandas de apoio institucional.</p>
            </div>
          </div>
          <div class="bg-rose-50/40 p-4 rounded-xl border border-rose-100/80 min-h-[110px]">
            <p class="text-xs text-gray-800 leading-relaxed whitespace-pre-wrap">
              {{ relatorio.dificuldades || 'Nenhuma dificuldade operacional informada neste bimestre.' }}
            </p>
          </div>
        </div>
      </div>

      <!-- Seção 5: Pareceres e Feedbacks Institucionais (Com Destaque Visual Reforçado e RBAC) -->
      <div
        id="secao-pareceres-institucionais"
        class="rounded-2xl shadow-sm border p-6 space-y-5 transition print:border print:border-gray-300 print:shadow-none print:break-inside-avoid"
        :class="temFeedbackInstitucional
          ? 'bg-gradient-to-br from-amber-50/60 via-white to-purple-50/60 border-amber-300 ring-1 ring-amber-200/70'
          : 'bg-white border-gray-100'"
      >
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b pb-3"
             :class="temFeedbackInstitucional ? 'border-amber-200/80' : 'border-gray-100'">
          <div class="flex items-center gap-2.5">
            <span
              class="w-8 h-8 rounded-xl font-black text-sm flex items-center justify-center shadow-2xs"
              :class="temFeedbackInstitucional
                ? 'bg-gradient-to-br from-amber-500 to-orange-500 text-white'
                : 'bg-purple-100 text-purple-800'"
            >
              🏛️
            </span>
            <div>
              <div class="flex items-center gap-2">
                <h3 class="text-base font-black text-gray-900">
                  5. Pareceres e Feedbacks Institucionais
                </h3>
                <span
                  v-if="temFeedbackInstitucional"
                  class="text-[10px] font-black uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-amber-500 text-white"
                >
                  Avaliado pela Alta Gestão
                </span>
              </div>
              <p class="text-[11px] text-gray-500">
                Devolutiva oficial da Superintendência e Administração sobre os resultados apresentados pela unidade.
              </p>
            </div>
          </div>

          <span
            v-if="!podeEmitirParecer"
            class="text-[11px] font-bold text-gray-500 bg-gray-100 px-3 py-1 rounded-full print:hidden"
          >
            Modo Leitura (Emissão restrita à Superintendência)
          </span>
        </div>

        <!-- Lista de Pareceres Registrados -->
        <div v-if="temFeedbackInstitucional" class="space-y-3">
          <div
            v-for="fb in relatorio.feedbacks"
            :key="fb.id"
            class="p-5 rounded-2xl bg-white border-l-4 border-l-amber-500 border border-amber-200/80 shadow-xs space-y-2"
          >
            <div class="flex flex-wrap items-center justify-between gap-2 text-xs">
              <div class="flex items-center gap-2">
                <span class="px-2.5 py-0.5 rounded-full bg-purple-100 text-purple-900 font-black text-[11px]">
                  {{ fb.autor_nome }}
                </span>
                <span class="text-[10px] font-extrabold uppercase tracking-wider text-amber-800 bg-amber-100 px-2 py-0.5 rounded">
                  {{ fb.autor_perfil }}
                </span>
              </div>
              <span class="text-[11px] font-semibold text-gray-500">
                {{ fb.data ? `Registrado em ${formatarData(fb.data)}` : '' }}
              </span>
            </div>
            <p class="text-sm text-gray-900 font-medium leading-relaxed whitespace-pre-wrap pl-1">
              {{ fb.texto }}
            </p>
          </div>
        </div>
        <div v-else class="p-6 rounded-xl bg-gray-50 border border-dashed border-gray-200 text-center">
          <p class="text-xs font-semibold text-gray-500">
            Nenhum parecer institucional registrado até o momento para este relatório bimestral.
          </p>
        </div>

        <!-- Formulário para Emissão de Novo Parecer (Exclusivo para SUPERINTENDENTE e ADMINISTRADOR) -->
        <div
          v-if="podeEmitirParecer"
          class="mt-4 pt-4 border-t border-purple-200/60 space-y-3 bg-purple-50/50 p-5 rounded-2xl print:hidden"
        >
          <div class="flex items-center justify-between">
            <h4 class="text-xs font-black text-purple-950 uppercase tracking-wider flex items-center gap-1.5">
              <span>✍️</span>
              <span>Emitir Parecer / Feedback Institucional</span>
            </h4>
            <span class="text-[10px] font-bold text-purple-700 bg-purple-100 px-2.5 py-0.5 rounded-full">
              Perfil Autorizado: {{ perfilUsuario }}
            </span>
          </div>
          <textarea
            v-model="novoFeedbackTexto"
            rows="3"
            placeholder="Registre aqui o parecer institucional, orientações estratégicas ou reconhecimento à chefia desta unidade..."
            class="w-full text-xs p-3.5 bg-white rounded-xl border border-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-600"
          ></textarea>
          <div class="flex items-center justify-between gap-4">
            <span class="text-[11px] text-gray-500">
              O parecer ficará visível em destaque para a chefia da unidade, gerência e matriz de acompanhamento.
            </span>
            <button
              type="button"
              @click="salvarFeedback"
              :disabled="enviandoFeedback || !novoFeedbackTexto.trim()"
              class="px-5 py-2.5 bg-purple-700 hover:bg-purple-800 text-white text-xs font-extrabold rounded-xl shadow-sm transition disabled:opacity-50 cursor-pointer"
            >
              {{ enviandoFeedback ? 'Registrando Parecer...' : 'Registrar Parecer Institucional' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Bloco de Assinaturas Exclusivo para Impressão (@media print) -->
      <div class="hidden print:grid grid-cols-2 gap-12 pt-12 mt-8 border-t border-gray-300 text-center text-xs">
        <div class="space-y-1">
          <div class="border-b border-gray-700 w-3/4 mx-auto pb-6"></div>
          <p class="font-bold text-gray-900">{{ relatorio.usuario_envio || 'Chefia da Unidade' }}</p>
          <p class="text-[10px] text-gray-600">Responsável pela Unidade — [{{ relatorio.uorg_sigla }}] {{ relatorio.uorg_nome }}</p>
        </div>
        <div class="space-y-1">
          <div class="border-b border-gray-700 w-3/4 mx-auto pb-6"></div>
          <p class="font-bold text-gray-900">Superintendência / Gestão Executiva</p>
          <p class="text-[10px] text-gray-600">Hospital das Clínicas da UFPE — HC-UFPE / EBSERH</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { gestaoApi, RelatorioDetalhe } from '../services/gestaoApi';
import { useAuthStore } from '../stores/auth';

const route = useRoute();
const authStore = useAuthStore();

const bimestres = ref<any[]>([]);
const todasUorgs = ref<any[]>([]);
const gerenciaFiltro = ref<string>('');
const bimestreSelecionadoId = ref<number>(1);
const uorgSelecionadaId = ref<number>(1);
const carregando = ref(false);
const enviandoFeedback = ref(false);
const novoFeedbackTexto = ref('');
const usuarioLogado = ref<any>(null);

const gerenciasPrincipais = ['SUP', 'GAS', 'GAD', 'GEP'];

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

const perfilUsuario = computed(() => {
  return (usuarioLogado.value?.perfil || authStore.gestaoProfile?.perfil || '').toUpperCase();
});

const tipoUorgUsuario = computed(() => {
  return (usuarioLogado.value?.tipo_uorg || authStore.gestaoProfile?.tipo_uorg || '').toUpperCase();
});

// Apenas SUPERINTENDENTE e ADMINISTRADOR podem registrar Pareceres e Feedbacks Institucionais
const podeEmitirParecer = computed(() => {
  return ['SUPERINTENDENTE', 'ADMINISTRADOR'].includes(perfilUsuario.value);
});

const exibirBotoesGerencia = computed(() => {
  return ['SUPERINTENDENTE', 'ADMINISTRADOR'].includes(perfilUsuario.value);
});

const escopoLabel = computed(() => {
  if (perfilUsuario.value === 'CHEFE_UORG') {
    if (tipoUorgUsuario.value === 'SETOR') return 'Escopo: Meu Setor';
    if (tipoUorgUsuario.value === 'DIVISAO') return 'Escopo: Divisão e Setores Subordinados';
  }
  if (perfilUsuario.value === 'GERENTE') {
    return 'Escopo: Divisões e Setores Subordinados (Leitura)';
  }
  if (perfilUsuario.value === 'SUPERINTENDENTE' || perfilUsuario.value === 'ADMINISTRADOR') {
    return 'Escopo Institucional: Todas as UORGs';
  }
  return '';
});

const uorgsFiltradas = computed(() => {
  if (!gerenciaFiltro.value) return todasUorgs.value;
  return todasUorgs.value.filter(u => (u.gerencia_sigla || '').toUpperCase() === gerenciaFiltro.value);
});

const uorgAtualInfo = computed(() => {
  return todasUorgs.value.find(u => u.id === uorgSelecionadaId.value) || null;
});

const indiceUorgAtual = computed(() => {
  return uorgsFiltradas.value.findIndex(u => u.id === uorgSelecionadaId.value);
});

const totalEntregasCount = computed(() => {
  return (relatorio.value.itens_entrega || []).length;
});

const entregasConcluidasCount = computed(() => {
  return (relatorio.value.itens_entrega || []).filter(e => e.concluida).length;
});

const percentualEntregas = computed(() => {
  if (totalEntregasCount.value === 0) return 0;
  return Math.round((entregasConcluidasCount.value / totalEntregasCount.value) * 100);
});

const totalIndicadoresCount = computed(() => {
  return (relatorio.value.itens_indicador || []).length;
});

const metasAtingidasCount = computed(() => {
  return (relatorio.value.itens_indicador || []).filter(i => i.meta_atingida === true).length;
});

const percentualMetas = computed(() => {
  if (totalIndicadoresCount.value === 0) return 0;
  return Math.round((metasAtingidasCount.value / totalIndicadoresCount.value) * 100);
});

const temFeedbackInstitucional = computed(() => {
  return Array.isArray(relatorio.value.feedbacks) && relatorio.value.feedbacks.length > 0;
});

const dataHoraImpressao = computed(() => {
  return new Date().toLocaleString('pt-BR');
});

async function carregarEstruturaEBimestres() {
  carregando.value = true;
  try {
    const [ex, user, uorgsScope] = await Promise.all([
      gestaoApi.obterExercicioAtivo(),
      gestaoApi.obterUsuarioLogado(),
      gestaoApi.obterUorgsAcessiveisDashboard()
    ]);

    usuarioLogado.value = user;
    bimestres.value = ex.bimestres || [];
    if (bimestres.value.length > 0) {
      bimestreSelecionadoId.value = bimestres.value[0].id;
    }

    // Para GERENTE na Visão Consolidada: exibe apenas divisões e setores subordinados
    let listaUorgs = Array.isArray(uorgsScope) ? [...uorgsScope] : [];
    if ((user?.perfil || '').toUpperCase() === 'GERENTE') {
      const subUorgs = listaUorgs.filter((u: any) => (u.tipo_uorg || '').toUpperCase() !== 'GERENCIA');
      if (subUorgs.length > 0) {
        listaUorgs = subUorgs;
      }
    }

    todasUorgs.value = listaUorgs;
    if (listaUorgs.length > 0) {
      uorgSelecionadaId.value = listaUorgs[0].id;
    }

    // Respeita parâmetros de query (?bimestre=X&uorg=Y) vindos da Matriz ou do Dashboard
    const qBim = Number(route.query.bimestre);
    if (qBim && bimestres.value.some((b: any) => b.id === qBim)) {
      bimestreSelecionadoId.value = qBim;
    }

    const qUorg = Number(route.query.uorg);
    if (qUorg && listaUorgs.some((u: any) => u.id === qUorg)) {
      uorgSelecionadaId.value = qUorg;
    }

    await carregarRelatorioAtual();
  } catch (err) {
    console.error('Erro na inicialização da Visão Consolidada:', err);
  } finally {
    carregando.value = false;
  }
}

async function carregarRelatorioAtual() {
  if (!uorgSelecionadaId.value || !bimestreSelecionadoId.value) return;
  carregando.value = true;
  try {
    const data = await gestaoApi.obterRelatorio(2026, bimestreSelecionadoId.value, uorgSelecionadaId.value);
    relatorio.value = data;
  } catch (err) {
    console.error('Erro ao carregar relatório consolidado:', err);
  } finally {
    carregando.value = false;
  }
}

function selecionarGerencia(sigla: string) {
  gerenciaFiltro.value = sigla;
  if (uorgsFiltradas.value.length > 0) {
    const existeAtual = uorgsFiltradas.value.some(u => u.id === uorgSelecionadaId.value);
    if (!existeAtual) {
      uorgSelecionadaId.value = uorgsFiltradas.value[0].id;
      carregarRelatorioAtual();
    }
  }
}

function selecionarBimestre(bimId: number) {
  bimestreSelecionadoId.value = bimId;
  carregarRelatorioAtual();
}

function onUorgSelectChange() {
  carregarRelatorioAtual();
}

function navegarRelatorio(delta: number) {
  const novoIdx = indiceUorgAtual.value + delta;
  if (novoIdx >= 0 && novoIdx < uorgsFiltradas.value.length) {
    uorgSelecionadaId.value = uorgsFiltradas.value[novoIdx].id;
    carregarRelatorioAtual();
  }
}

function imprimirRelatorio() {
  window.print();
}

async function salvarFeedback() {
  if (!podeEmitirParecer.value) return;
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
  const op = ind.meta_operador || 'MAIOR_IGUAL';
  const sufixo = ind.unidade_medida === 'PERCENTUAL' ? '%' : '';
  if (op === 'ENTRE') return `${ind.meta_valor} a ${ind.meta_valor_max}${sufixo}`;
  const opSym = op === 'MAIOR_IGUAL' || op === '>=' ? '≥' : (op === 'MENOR_IGUAL' || op === '<=' ? '≤' : '=');
  return `${opSym} ${ind.meta_valor}${sufixo}`;
}

function formatarValorIndicador(valor: number, unidade?: string) {
  if (unidade === 'PERCENTUAL') return `${valor}%`;
  return `${valor}`;
}

function formatarStatusLabel(status: string) {
  switch (status) {
    case 'ENVIADO': return 'Submetido / Enviado';
    case 'EM_EDICAO': return 'Em Preenchimento';
    case 'PRAZO_EXCEPCIONAL': return 'Prazo Excepcional';
    default: return 'Não Iniciado / Rascunho';
  }
}

function getStatusBadgeClass(status: string) {
  switch (status) {
    case 'ENVIADO': return 'bg-emerald-500 text-white';
    case 'EM_EDICAO': return 'bg-amber-400 text-slate-950';
    case 'PRAZO_EXCEPCIONAL': return 'bg-sky-500 text-white';
    default: return 'bg-slate-700 text-slate-200';
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

<style scoped>
@media print {
  @page {
    size: A4 portrait;
    margin: 12mm;
  }
}
</style>
