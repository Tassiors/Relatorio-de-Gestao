<template>
  <div class="space-y-6 max-w-6xl mx-auto pb-10">
    <!-- Header e Controles de Seleção -->
    <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 space-y-4">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div class="flex items-center gap-2">
            <router-link :to="podeVerMatriz ? '/matriz' : '/'" class="text-blue-600 hover:text-blue-800 text-xs font-bold flex items-center gap-1 transition">
              ← {{ podeVerMatriz ? 'Voltar para Matriz' : 'Voltar para Início' }}
            </router-link>
          </div>
          <h1 class="text-2xl font-black text-gray-900 mt-1 flex flex-wrap items-center gap-2">
            <span>Relatório Bimestral</span>
            <span class="text-xs font-extrabold px-2.5 py-1 rounded-full" :class="getStatusBadgeClass(relatorio.status)">
              {{ getStatusLabel(relatorio.status) }}
            </span>
            <span
              v-if="relatorio.feedbacks && relatorio.feedbacks.length > 0"
              class="inline-flex items-center gap-1.5 text-xs font-black px-3 py-1 rounded-full bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-sm ring-2 ring-amber-200 animate-pulse"
            >
              <span>🏛️</span>
              <span>Feedback Institucional Recebido ({{ relatorio.feedbacks.length }})</span>
            </span>
          </h1>
          <p class="text-xs text-gray-500 mt-0.5 font-medium">
            {{ relatorio.uorg_sigla }} — {{ relatorio.uorg_nome }} | {{ relatorio.bimestre_nome }}
          </p>
        </div>

        <!-- Indicador de Autosave e Ações Rápidas -->
        <div class="flex flex-wrap items-center gap-2.5">
          <div class="text-xs text-gray-500 flex items-center gap-1.5 bg-gray-50 px-3 py-1.5 rounded-lg border border-gray-200">
            <span v-if="salvando" class="w-2 h-2 rounded-full bg-amber-500 animate-ping"></span>
            <span v-else class="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span>{{ statusSalvoTexto }}</span>
          </div>

          <button
            v-if="relatorio.id"
            @click="baixarExcel"
            class="px-3 py-1.5 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 text-xs font-bold rounded-lg border border-emerald-200 transition cursor-pointer"
          >
            📊 Excel
          </button>

          <button
            v-if="relatorio.id"
            @click="baixarPdf"
            class="px-3 py-1.5 bg-red-50 text-red-700 hover:bg-red-100 text-xs font-bold rounded-lg border border-red-200 transition cursor-pointer"
          >
            📄 PDF
          </button>

          <button
            @click="salvarRascunhoManual"
            :disabled="salvando"
            class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-bold rounded-lg transition cursor-pointer"
          >
            Salvar Rascunho
          </button>

          <button
            @click="abrirModalEnvio"
            class="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-lg shadow-sm transition cursor-pointer"
          >
            Enviar Relatório
          </button>
        </div>
      </div>

      <!-- Barra Rápida de Seleção de UORG e Bimestre -->
      <div class="pt-4 border-t border-gray-100 flex flex-col lg:flex-row lg:items-center justify-between gap-3">
        <div v-if="isAdmin" class="flex flex-wrap items-center gap-2">
          <label for="seletorUorgPreenchimento" class="text-xs font-extrabold text-gray-600 uppercase tracking-wider">
            Unidade (UORG):
          </label>
          <select
            id="seletorUorgPreenchimento"
            v-model="uorgSelecionadaId"
            @change="trocarFiltroRelatorio"
            class="text-xs font-bold text-gray-800 bg-gray-50 hover:bg-white border border-gray-200 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 transition max-w-md"
          >
            <optgroup v-for="grp in uorgsAgrupadas" :key="grp.gerencia" :label="grp.gerencia">
              <option v-for="u in grp.itens" :key="u.id" :value="u.id">
                {{ u.sigla }} — {{ u.nome }}
              </option>
            </optgroup>
          </select>
        </div>
        <div v-else class="flex items-center gap-2 bg-indigo-50 border border-indigo-200 px-3.5 py-2 rounded-xl text-xs font-extrabold text-indigo-950">
          <span class="w-2 h-2 rounded-full bg-indigo-600"></span>
          <span>Unidade Vinculada: {{ relatorio.uorg_sigla }} — {{ relatorio.uorg_nome }}</span>
        </div>

        <div class="flex flex-wrap items-center gap-1.5">
          <span class="text-xs font-extrabold text-gray-600 uppercase tracking-wider mr-1">Bimestre:</span>
          <button
            v-for="b in listaBimestres"
            :key="b.id"
            type="button"
            @click="selecionarBimestre(b.id)"
            class="px-3 py-1.5 rounded-lg text-xs font-bold border transition cursor-pointer flex items-center gap-1"
            :class="bimestreSelecionadoId === b.id
              ? 'bg-blue-600 text-white border-blue-600 shadow-xs'
              : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'"
          >
            <span>{{ b.numero }}º BI</span>
            <span
              class="w-1.5 h-1.5 rounded-full"
              :class="b.status === 'ABERTO'
                ? (bimestreSelecionadoId === b.id ? 'bg-emerald-300' : 'bg-emerald-500')
                : 'bg-gray-400'"
              :title="b.status === 'ABERTO' ? 'Bimestre Aberto' : 'Bimestre Fechado'"
            ></span>
          </button>
        </div>
      </div>
    </div>

    <!-- Destaque Executivo de Parecer / Feedback Institucional Recebido -->
    <div
      v-if="relatorio.feedbacks && relatorio.feedbacks.length > 0"
      class="bg-gradient-to-r from-amber-50 via-yellow-50 to-orange-50 border-2 border-amber-400 p-5 rounded-2xl shadow-md space-y-3"
    >
      <div class="flex items-center justify-between flex-wrap gap-2">
        <div class="flex items-center gap-2.5">
          <div class="w-10 h-10 rounded-xl bg-amber-500 text-white flex items-center justify-center text-lg shadow-xs">
            🏛️
          </div>
          <div>
            <span class="text-[10px] font-black uppercase tracking-widest text-amber-800 bg-amber-200/70 px-2 py-0.5 rounded-full">
              Avaliação da Alta Gestão
            </span>
            <h3 class="text-sm font-black text-amber-950 mt-0.5">
              Este Relatório Obteve Parecer / Feedback Institucional
            </h3>
          </div>
        </div>
        <router-link
          :to="`/consolidado?bimestre=${relatorio.bimestre_id}&uorg=${relatorio.uorg_id}`"
          class="px-3.5 py-1.5 bg-amber-600 hover:bg-amber-700 text-white text-xs font-extrabold rounded-xl shadow-xs transition"
        >
          Ver na Visão Consolidada &rarr;
        </router-link>
      </div>
      <div class="space-y-2">
        <div
          v-for="fb in relatorio.feedbacks"
          :key="fb.id"
          class="bg-white/90 border border-amber-300 rounded-xl p-3.5 text-xs space-y-1 shadow-2xs"
        >
          <div class="flex items-center justify-between font-bold text-amber-900">
            <span>{{ fb.autor_nome }} ({{ fb.autor_perfil }})</span>
            <span class="text-[11px] text-amber-700">{{ fb.data ? formatarDataHora(fb.data) : '' }}</span>
          </div>
          <p class="text-gray-800 font-medium leading-relaxed whitespace-pre-wrap">{{ fb.texto }}</p>
        </div>
      </div>
    </div>

    <!-- Alerta de Prazo Excepcional -->
    <div v-if="relatorio.prazo_excepcional" class="bg-blue-50 border-l-4 border-blue-600 p-4 rounded-r-xl shadow-sm">
      <div class="flex items-start gap-3">
        <span class="text-xl">⏱</span>
        <div>
          <h4 class="font-bold text-sm text-blue-900">Prazo Excepcional Concedido para esta Unidade</h4>
          <p class="text-xs text-blue-700 mt-0.5">
            <b>Data Limite:</b> {{ formatarDataHora(relatorio.prazo_excepcional.data_fim) }}
            <template v-if="relatorio.prazo_excepcional.motivo">
              | <b>Justificativa Administrativa:</b> {{ relatorio.prazo_excepcional.motivo }}
            </template>
          </p>
        </div>
      </div>
    </div>

    <!-- Seção 1: Entregas Planejadas (Com Efeito Cascata) -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-4">
      <div class="border-b border-gray-100 pb-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h2 class="text-lg font-black text-gray-900 flex items-center gap-2">
            <span class="w-2.5 h-5 bg-indigo-600 rounded-full"></span>
            1. Entregas Planejadas Pactuadas
          </h2>
          <p class="text-xs text-gray-500 mt-0.5">
            Marque as entregas concluídas neste bimestre. Entregas concluídas propagam-se automaticamente para os bimestres seguintes (efeito cascata), evitando retrabalho.
          </p>
        </div>
        <div v-if="relatorio.itens_entrega?.length" class="flex items-center gap-2 shrink-0">
          <span class="px-3 py-1 rounded-full text-xs font-extrabold bg-emerald-50 text-emerald-800 border border-emerald-200">
            {{ totalEntregasConcluidas }}/{{ relatorio.itens_entrega.length }} concluídas
          </span>
        </div>
      </div>

      <div v-if="relatorio.itens_entrega && relatorio.itens_entrega.length > 0" class="space-y-3">
        <div
          v-for="(entrega, idx) in relatorio.itens_entrega"
          :key="entrega.entrega_id"
          class="p-4 rounded-xl border transition-all duration-200"
          :class="entrega.concluida_anteriormente
            ? 'bg-gradient-to-r from-emerald-50/90 to-teal-50/70 border-emerald-300 shadow-xs'
            : entrega.concluida
              ? 'bg-emerald-50/50 border-emerald-200'
              : 'bg-gray-50/50 border-gray-200 hover:border-indigo-200'"
        >
          <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
            <div class="flex items-start gap-3 flex-1">
              <input
                type="checkbox"
                :id="'ent_' + entrega.entrega_id"
                v-model="entrega.concluida"
                :disabled="Boolean(entrega.concluida_anteriormente)"
                @change="agendarAutosave"
                class="mt-1 w-4 h-4 text-emerald-600 rounded border-gray-300 focus:ring-emerald-500 disabled:opacity-75 disabled:cursor-not-allowed"
              />
              <div class="flex-1 space-y-2">
                <div class="flex flex-wrap items-center gap-2">
                  <label
                    :for="'ent_' + entrega.entrega_id"
                    class="text-sm font-bold text-gray-900"
                    :class="entrega.concluida_anteriormente ? 'cursor-default' : 'cursor-pointer'"
                  >
                    {{ idx + 1 }}. {{ entrega.titulo }}
                  </label>
                </div>

                <p
                  v-if="entrega.concluida_anteriormente"
                  class="text-xs text-emerald-800 font-medium bg-white/80 px-3 py-1.5 rounded-lg border border-emerald-200 inline-flex items-center gap-1.5"
                >
                  <span>🎉</span>
                  <span>
                    Ciclo de conquista registrado no <b>{{ entrega.bimestre_conclusao_nome || 'bimestre anterior' }}</b> — propagado automaticamente sem necessidade de retrabalho.
                  </span>
                </p>

                <div>
                  <input
                    type="text"
                    v-model="entrega.observacoes"
                    :disabled="Boolean(entrega.concluida_anteriormente)"
                    @input="agendarAutosave"
                    :placeholder="entrega.concluida_anteriormente
                      ? 'Concluída em bimestre anterior (observações bloqueadas para evitar retrabalho)'
                      : 'Observações complementares sobre o andamento ou conclusão da entrega (opcional)...'"
                    class="w-full text-xs p-2.5 bg-white rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:outline-none disabled:bg-gray-100 disabled:text-gray-500"
                  />
                </div>
              </div>
            </div>

            <!-- Badges de Status da Entrega -->
            <div class="shrink-0">
              <span
                v-if="entrega.concluida_anteriormente"
                class="inline-flex items-center gap-1 text-xs font-extrabold text-emerald-900 bg-emerald-200/80 border border-emerald-300 px-3 py-1 rounded-full"
              >
                🏆 Concluída no {{ entrega.bimestre_conclusao_nome || 'Ciclo Anterior' }}
              </span>
              <span
                v-else-if="entrega.concluida"
                class="inline-flex items-center gap-1 text-xs font-bold text-emerald-800 bg-emerald-100 border border-emerald-200 px-3 py-1 rounded-full"
              >
                🚀 Concluída neste Bimestre
              </span>
              <span
                v-else
                class="inline-flex items-center gap-1 text-xs font-semibold text-gray-600 bg-gray-100 border border-gray-200 px-3 py-1 rounded-full"
              >
                ⏳ Em Andamento
              </span>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="text-sm text-gray-400 italic py-4">
        Nenhuma entrega planejada cadastrada para esta UORG.
      </div>
    </div>

    <!-- Seção 2: Indicadores de Gestão (Motor de Periodicidade e Orientações Contextuais) -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-4">
      <div class="border-b border-gray-100 pb-3">
        <h2 class="text-lg font-black text-gray-900 flex items-center gap-2">
          <span class="w-2.5 h-5 bg-blue-600 rounded-full"></span>
          2. Indicadores de Gestão e Metas Pactuadas
        </h2>
        <p class="text-xs text-gray-500 mt-0.5">
          Os campos abaixo adaptam-se automaticamente à periodicidade de cada indicador (mensal, bimestral, trimestral, quadrimestral ou semestral) no {{ relatorio.bimestre_nome }}.
        </p>
      </div>

      <div v-if="gruposIndicadores.length === 0" class="text-sm text-gray-400 italic py-4">
        Nenhum indicador anual cadastrado para esta UORG.
      </div>

      <div v-else class="space-y-5">
        <div
          v-for="grupo in gruposIndicadores"
          :key="grupo.indicador_id"
          class="p-5 rounded-2xl border transition-all space-y-4"
          :class="grupo.aplicavel
            ? 'border-gray-200 bg-slate-50/40'
            : 'border-slate-200 bg-slate-50/80 opacity-90'"
        >
          <!-- Cabeçalho do Indicador -->
          <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2">
            <div>
              <div class="flex items-center gap-2">
                <h3 class="text-sm font-black text-gray-900">{{ grupo.nome }}</h3>
                <span
                  v-if="!grupo.aplicavel"
                  class="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase bg-slate-200 text-slate-700 border border-slate-300"
                >
                  Não aplicável a este bimestre
                </span>
              </div>
              <p v-if="grupo.descricao" class="text-xs text-gray-500 mt-0.5">{{ grupo.descricao }}</p>
            </div>

            <!-- Badges de Meta e Periodicidade -->
            <div class="flex flex-wrap items-center gap-2 text-xs shrink-0">
              <span class="px-2.5 py-1 bg-blue-50 text-blue-800 font-bold rounded-lg border border-blue-200">
                Meta: {{ formatarMeta(grupo.itens[0]) }}
              </span>
              <span class="px-2.5 py-1 bg-indigo-50 text-indigo-800 font-bold rounded-lg border border-indigo-200">
                Periodicidade: {{ grupo.periodicidade }}
              </span>
            </div>
          </div>

          <!-- Mensagem Orientativa Contextual da Periodicidade -->
          <div
            class="p-3 rounded-xl border text-xs flex items-start gap-2.5"
            :class="grupo.aplicavel
              ? 'bg-blue-50/70 border-blue-200 text-blue-900'
              : 'bg-slate-100 border-slate-200 text-slate-700'"
          >
            <span class="text-sm shrink-0">{{ grupo.aplicavel ? '💡' : '📅' }}</span>
            <p class="leading-relaxed font-medium">
              {{ grupo.orientacao }}
            </p>
          </div>

          <!-- Caso APLICÁVEL ao Bimestre: Renderiza 1 ou 2 Campos de Competência (ex: Mensal = 2 meses) -->
          <div v-if="grupo.aplicavel" class="grid grid-cols-1 gap-4" :class="grupo.itens.length > 1 ? 'md:grid-cols-2' : ''">
            <div
              v-for="(ind, cIdx) in grupo.itens"
              :key="`${ind.indicador_id}_${ind.competencia}_${cIdx}`"
              class="bg-white p-4 rounded-xl border border-gray-200 shadow-2xs space-y-3"
            >
              <div class="flex items-center justify-between border-b border-gray-100 pb-2">
                <span class="text-xs font-extrabold text-indigo-900 uppercase tracking-wider flex items-center gap-1.5">
                  <span class="w-2 h-2 rounded-full bg-indigo-600"></span>
                  Competência: {{ ind.competencia }}
                </span>

                <label class="inline-flex items-center gap-1.5 cursor-pointer text-xs text-gray-600">
                  <input
                    type="checkbox"
                    v-model="ind.resultado_indisponivel"
                    @change="onIndisponivelToggle(ind)"
                    class="rounded text-amber-600 focus:ring-amber-500 w-3.5 h-3.5"
                  />
                  <span class="font-semibold text-[11px]">Resultado indisponível</span>
                </label>
              </div>

              <!-- Entrada Numérica + Status da Meta -->
              <div v-if="!ind.resultado_indisponivel" class="flex flex-col sm:flex-row sm:items-center gap-3">
                <div class="flex-1">
                  <label class="block text-[11px] font-bold text-gray-600 mb-1">
                    Valor Apurado ({{ ind.competencia }}) *
                  </label>
                  <div class="relative">
                    <input
                      type="number"
                      step="any"
                      v-model.number="ind.valor_apurado"
                      @input="onValorApuradoChange(ind)"
                      placeholder="Informe o resultado numérico..."
                      class="w-full text-sm font-bold p-2.5 bg-slate-50 focus:bg-white rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    />
                    <span class="absolute right-3 top-2.5 text-xs text-gray-500 font-bold">
                      {{ ind.unidade_medida === 'PERCENTUAL' ? '%' : ind.unidade_medida }}
                    </span>
                  </div>
                </div>

                <div class="sm:pt-5 shrink-0">
                  <span
                    v-if="ind.meta_atingida === true"
                    class="inline-flex items-center gap-1.5 px-3 py-2 bg-emerald-100 text-emerald-800 border border-emerald-200 text-xs font-extrabold rounded-lg"
                  >
                    ✓ Meta Atingida
                  </span>
                  <span
                    v-else-if="ind.meta_atingida === false"
                    class="inline-flex items-center gap-1.5 px-3 py-2 bg-rose-100 text-rose-800 border border-rose-200 text-xs font-extrabold rounded-lg"
                  >
                    ✕ Meta Não Atingida
                  </span>
                  <span v-else class="inline-flex items-center px-3 py-2 bg-gray-100 text-gray-500 text-xs font-medium rounded-lg">
                    Aguardando valor
                  </span>
                </div>
              </div>

              <!-- Justificativa de Indisponibilidade -->
              <div v-else class="bg-amber-50/80 p-3 rounded-lg border border-amber-200 space-y-1.5">
                <div class="flex items-center justify-between">
                  <label class="text-xs font-bold text-amber-900">
                    Justificativa de Indisponibilidade ({{ ind.competencia }}) *
                  </label>
                  <span
                    class="text-[10px] font-bold"
                    :class="(ind.justificativa_indisponibilidade || '').trim().length >= 5 ? 'text-emerald-700' : 'text-amber-700'"
                  >
                    {{ (ind.justificativa_indisponibilidade || '').trim().length }} caracteres
                  </span>
                </div>
                <input
                  type="text"
                  v-model="ind.justificativa_indisponibilidade"
                  @input="agendarAutosave"
                  placeholder="Explique sucintamente por que o indicador ainda não está disponível neste período..."
                  class="w-full text-xs p-2.5 bg-white rounded-lg border border-amber-300 focus:ring-2 focus:ring-amber-500 focus:outline-none"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Seções 3 e 4: Destaques e Dificuldades (Design Lúdico, Acolhedor e Inspirador) -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Item 3: Destaques e Conquistas da Equipe -->
      <div class="bg-gradient-to-br from-emerald-50/80 via-white to-teal-50/60 rounded-2xl shadow-sm border border-emerald-200 p-6 space-y-4 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200">
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-2xl bg-emerald-100 border border-emerald-200 flex items-center justify-center text-2xl shadow-2xs shrink-0">
              🏆
            </div>
            <div>
              <span class="text-[10px] font-black uppercase tracking-widest text-emerald-700 bg-emerald-100/80 px-2 py-0.5 rounded-full">
                Celebre as Conquistas
              </span>
              <h2 class="text-base font-black text-gray-900 mt-0.5 flex items-center gap-1.5">
                <span>3. Destaques e Avanços do Bimestre</span>
                <span>🚀</span>
              </h2>
            </div>
          </div>

          <span
            class="px-2.5 py-1 rounded-full text-xs font-extrabold border shrink-0 transition"
            :class="(relatorio.destaques || '').trim().length >= 5
              ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
              : 'bg-gray-100 text-gray-500 border-gray-200'"
          >
            {{ (relatorio.destaques || '').length }} caracteres
          </span>
        </div>

        <p class="text-xs text-emerald-950/80 leading-relaxed bg-emerald-100/40 p-3 rounded-xl border border-emerald-200/60">
          ✨ <b>Espaço de valorização da sua equipe!</b> Compartilhe boas práticas implantadas, melhorias no cuidado ao paciente, otimização de processos ou conquistas que merecem reconhecimento institucional.
        </p>

        <!-- Chips de inspiração rápida -->
        <div class="flex flex-wrap gap-1.5">
          <button
            v-for="dica in dicasDestaques"
            :key="dica"
            type="button"
            @click="inserirTopico('destaques', dica)"
            class="text-[11px] font-semibold px-2.5 py-1 rounded-full bg-white hover:bg-emerald-100 text-emerald-800 border border-emerald-200 transition cursor-pointer"
          >
            + {{ dica }}
          </button>
        </div>

        <textarea
          v-model="relatorio.destaques"
          @input="agendarAutosave"
          rows="5"
          placeholder="Conte aqui os avanços, resultados positivos, humanização, mutirões ou projetos de destaque alcançados pela equipe neste bimestre..."
          class="w-full text-sm p-3.5 bg-white rounded-xl border border-emerald-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 focus:outline-none shadow-2xs transition"
        ></textarea>
      </div>

      <!-- Item 4: Dificuldades, Aprendizados e Apoio Institucional -->
      <div class="bg-gradient-to-br from-amber-50/70 via-white to-sky-50/60 rounded-2xl shadow-sm border border-amber-200 p-6 space-y-4 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200">
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-2xl bg-amber-100 border border-amber-200 flex items-center justify-center text-2xl shadow-2xs shrink-0">
              🧭
            </div>
            <div>
              <span class="text-[10px] font-black uppercase tracking-widest text-amber-800 bg-amber-100/80 px-2 py-0.5 rounded-full">
                Bússola de Melhoria e Apoio
              </span>
              <h2 class="text-base font-black text-gray-900 mt-0.5 flex items-center gap-1.5">
                <span>4. Desafios e Oportunidades de Apoio</span>
                <span>🎯</span>
              </h2>
            </div>
          </div>

          <span
            class="px-2.5 py-1 rounded-full text-xs font-extrabold border shrink-0 transition"
            :class="(relatorio.dificuldades || '').trim().length >= 5
              ? 'bg-amber-100 text-amber-900 border-amber-300'
              : 'bg-gray-100 text-gray-500 border-gray-200'"
          >
            {{ (relatorio.dificuldades || '').length }} caracteres
          </span>
        </div>

        <p class="text-xs text-amber-950/80 leading-relaxed bg-amber-100/40 p-3 rounded-xl border border-amber-200/60">
          🛟 <b>Transparência construtiva para apoiar sua unidade!</b> Relate gargalos operacionais, necessidades de infraestrutura, insumos ou articulações em que a Gerência e a Superintendência possam atuar juntas.
        </p>

        <!-- Chips de inspiração rápida -->
        <div class="flex flex-wrap gap-1.5">
          <button
            v-for="dica in dicasDificuldades"
            :key="dica"
            type="button"
            @click="inserirTopico('dificuldades', dica)"
            class="text-[11px] font-semibold px-2.5 py-1 rounded-full bg-white hover:bg-amber-100 text-amber-900 border border-amber-200 transition cursor-pointer"
          >
            + {{ dica }}
          </button>
        </div>

        <textarea
          v-model="relatorio.dificuldades"
          @input="agendarAutosave"
          rows="5"
          placeholder="Descreva com tranquilidade os desafios vivenciados no período e quais encaminhamentos ou apoios institucionais podem destravar esses processos..."
          class="w-full text-sm p-3.5 bg-white rounded-xl border border-amber-200 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 focus:outline-none shadow-2xs transition"
        ></textarea>
      </div>
    </div>

    <!-- Seção 5: Pareceres / Feedbacks da Gestão -->
    <div v-if="relatorio.feedbacks && relatorio.feedbacks.length > 0" class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-3">
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
            class="px-4 py-2 text-xs font-bold text-gray-600 hover:bg-gray-100 rounded-lg transition cursor-pointer"
          >
            Voltar
          </button>
          <button 
            v-if="pendenciasEnvio.length === 0"
            @click="confirmarEnvio" 
            class="px-5 py-2 text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow-sm transition cursor-pointer"
          >
            Confirmar e Enviar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { gestaoApi, type RelatorioDetalhe, type IndicadorItem } from '../services/gestaoApi';
import {
  obterConfiguracaoPeriodicidade,
  normalizarItensIndicadorParaBimestre
} from '../utils/indicadorHelper';

interface UorgAcessivelItem {
  id: number;
  sigla: string;
  nome: string;
  gerencia_id?: number;
  gerencia_sigla?: string;
  gerencia_nome?: string;
}

const route = useRoute();
const router = useRouter();

const relatorio = ref<RelatorioDetalhe>({
  exercicio_id: 1,
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

const exercicioIdAtual = ref<number>(1);
const bimestreSelecionadoId = ref<number>(1);
const uorgSelecionadaId = ref<number>(1);
const listaBimestres = ref<any[]>([]);
const uorgsAcessiveis = ref<UorgAcessivelItem[]>([]);
const usuarioLogado = ref<any>(null);

const isAdmin = computed(() => (usuarioLogado.value?.perfil || '').toUpperCase() === 'ADMINISTRADOR');
const podeVerMatriz = computed(() => {
  const p = (usuarioLogado.value?.perfil || '').toUpperCase();
  const t = (usuarioLogado.value?.tipo_uorg || 'SETOR').toUpperCase();
  return ['ADMINISTRADOR', 'SUPERINTENDENTE', 'GERENTE'].includes(p) || (['CHEFE', 'CHEFE_UORG'].includes(p) && t === 'DIVISAO');
});

const uorgsAgrupadas = computed(() => {
  const grupos = new Map<string, UorgAcessivelItem[]>();
  for (const u of uorgsAcessiveis.value) {
    const label = u.gerencia_sigla ? `${u.gerencia_sigla} — ${u.gerencia_nome || ''}` : 'Unidades Organizacionais';
    if (!grupos.has(label)) {
      grupos.set(label, []);
    }
    grupos.get(label)!.push(u);
  }
  return Array.from(grupos.entries()).map(([gerencia, itens]) => ({ gerencia, itens }));
});

const salvando = ref(false);
const statusSalvoTexto = ref('Rascunho atualizado');
const modalEnvioAberto = ref(false);
const pendenciasEnvio = ref<string[]>([]);
let timerAutosave: any = null;

const dicasDestaques = [
  'Inovação no fluxo assistencial',
  'Meta superada pela equipe',
  'Capacitação concluída',
  'Integração multiprofissional'
];

const dicasDificuldades = [
  'Necessidade de reposição de insumos',
  'Adequação de infraestrutura',
  'Apoio em sistemas/TI',
  'Dimensionamento de equipe'
];

const bimestreNumeroAtual = computed(() => {
  const m = (relatorio.value.bimestre_nome || '').match(/(\d+)/);
  if (m) return Number(m[1]);
  return relatorio.value.bimestre_id || 1;
});

const totalEntregasConcluidas = computed(() => {
  return (relatorio.value.itens_entrega || []).filter((e) => e.concluida).length;
});

interface GrupoIndicadorUI {
  indicador_id: number;
  nome: string;
  descricao?: string;
  periodicidade: string;
  aplicavel: boolean;
  orientacao: string;
  itens: IndicadorItem[];
}

const gruposIndicadores = computed<GrupoIndicadorUI[]>(() => {
  const mapa = new Map<number, GrupoIndicadorUI>();
  const bimNum = bimestreNumeroAtual.value;

  for (const item of relatorio.value.itens_indicador || []) {
    const cfg = obterConfiguracaoPeriodicidade(item.periodicidade, bimNum);
    if (!mapa.has(item.indicador_id)) {
      mapa.set(item.indicador_id, {
        indicador_id: item.indicador_id,
        nome: item.nome,
        descricao: item.descricao,
        periodicidade: cfg.periodicidade,
        aplicavel: cfg.aplicavel,
        orientacao: item.orientacao_periodicidade || cfg.orientacao,
        itens: []
      });
    }
    mapa.get(item.indicador_id)!.itens.push(item);
  }
  return Array.from(mapa.values());
});

function inserirTopico(campo: 'destaques' | 'dificuldades', topico: string) {
  const atual = (relatorio.value[campo] || '').trim();
  relatorio.value[campo] = atual ? `${atual}\n• ${topico}: ` : `• ${topico}: `;
  agendarAutosave();
}

async function buscarDadosRelatorio(exId: number, bId: number, uId: number) {
  const data = await gestaoApi.obterRelatorio(exId, bId, uId);
  const m = (data.bimestre_nome || '').match(/(\d+)/);
  const bimNum = m ? Number(m[1]) : bId;

  data.itens_indicador = normalizarItensIndicadorParaBimestre(data.itens_indicador || [], bimNum);
  relatorio.value = data;

  relatorio.value.itens_indicador.forEach((ind) => {
    calcularMetaIndicador(ind);
  });
}

async function trocarFiltroRelatorio() {
  if (!uorgSelecionadaId.value || !bimestreSelecionadoId.value) return;
  try {
    router.replace({
      query: {
        exercicio: String(exercicioIdAtual.value),
        bimestre: String(bimestreSelecionadoId.value),
        uorg: String(uorgSelecionadaId.value)
      }
    });
    await buscarDadosRelatorio(exercicioIdAtual.value, bimestreSelecionadoId.value, uorgSelecionadaId.value);
    statusSalvoTexto.value = 'Dados carregados';
  } catch (err) {
    console.error('Erro ao alternar relatório:', err);
  }
}

async function selecionarBimestre(bId: number) {
  bimestreSelecionadoId.value = bId;
  await trocarFiltroRelatorio();
}

async function carregarRelatorio() {
  try {
    const [ex, me, uorgsDisp] = await Promise.all([
      gestaoApi.obterExercicioAtivo(),
      gestaoApi.obterUsuarioLogado(),
      gestaoApi.obterUorgsAcessiveisDashboard()
    ]);

    usuarioLogado.value = me;
    // Para Chefe de Divisão ou Setor, Preenchimento Bimestral é restrito apenas à própria UORG
    if (me?.perfil === 'ADMINISTRADOR') {
      uorgsAcessiveis.value = uorgsDisp || [];
    } else if (me?.uorg_id) {
      const propria = (uorgsDisp || []).filter((u: any) => Number(u.id) === Number(me.uorg_id));
      uorgsAcessiveis.value = propria.length ? propria : (uorgsDisp || []);
    } else {
      uorgsAcessiveis.value = uorgsDisp || [];
    }
    listaBimestres.value = ex?.bimestres || [];

    const exId = Number(route.query.exercicio) || ex?.id || 1;
    const bId = Number(route.query.bimestre) || ex?.bimestres?.[0]?.id || 1;

    let uId = Number(route.query.uorg) || 0;
    if (me?.perfil !== 'ADMINISTRADOR' && me?.uorg_id) {
      // Chefia de Divisão ou Setor preenche exclusivamente o relatório da própria UORG
      uId = me.uorg_id;
    } else if (!uId) {
      uId = me?.uorg_id || uorgsDisp?.[0]?.id || 1;
    }

    exercicioIdAtual.value = exId;
    bimestreSelecionadoId.value = bId;
    uorgSelecionadaId.value = uId;

    await buscarDadosRelatorio(exId, bId, uId);
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
  const bimNum = bimestreNumeroAtual.value;

  for (const ind of relatorio.value.itens_indicador) {
    const cfg = obterConfiguracaoPeriodicidade(ind.periodicidade, bimNum);
    if (!cfg.aplicavel || ind.nao_aplicavel) continue;

    const label = ind.competencia ? `${ind.nome} (${ind.competencia})` : ind.nome;
    if (ind.resultado_indisponivel) {
      if (!ind.justificativa_indisponibilidade || ind.justificativa_indisponibilidade.trim().length < 5) {
        pendenciasEnvio.value.push(`Indicador "${label}": informe uma justificativa para a indisponibilidade (mín. 5 caracteres).`);
      }
    } else {
      if (ind.valor_apurado === null || ind.valor_apurado === undefined || Number.isNaN(ind.valor_apurado)) {
        pendenciasEnvio.value.push(`Indicador "${label}": valor apurado não foi preenchido.`);
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
    const bimNum = bimestreNumeroAtual.value;
    res.itens_indicador = normalizarItensIndicadorParaBimestre(res.itens_indicador || [], bimNum);
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
  if (!ind) return '';
  const op = ind.meta_operador || 'MAIOR_IGUAL';
  const un = ind.unidade_medida === 'PERCENTUAL' ? '%' : (ind.unidade_medida || '');
  if (op === 'ENTRE') return `${ind.meta_valor} a ${ind.meta_valor_max} ${un}`;
  const opSym = op === 'MAIOR_IGUAL' ? '≥' : (op === 'MENOR_IGUAL' ? '≤' : '=');
  return `${opSym} ${ind.meta_valor} ${un}`;
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
