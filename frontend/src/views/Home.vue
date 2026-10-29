<template>
  <div class="space-y-6">
    <!-- Banner de Boas-Vindas Executivo -->
    <div class="bg-gradient-to-r from-blue-900 via-indigo-900 to-blue-950 text-white p-6 sm:p-8 rounded-2xl shadow-md relative overflow-hidden">
      <div class="relative z-10 max-w-3xl space-y-2.5">
        <div class="inline-flex items-center gap-2 px-3 py-1 bg-white/10 backdrop-blur-md rounded-full text-xs font-semibold tracking-wide text-blue-200 border border-white/20">
          <span>Exercício {{ exercicio?.ano || 2026 }} • {{ exercicio?.status || 'EM ANDAMENTO' }}</span>
          <span>•</span>
          <span>HC-UFPE / EBSERH</span>
        </div>
        <h1 class="text-2xl sm:text-3xl font-black tracking-tight leading-tight">
          Portal de Relatórios de Gestão
        </h1>
        <p class="text-xs sm:text-sm text-blue-100 font-normal leading-relaxed">
          Acompanhamento estratégico de entregas planejadas e indicadores com metas das Unidades Organizacionais do Hospital das Clínicas da UFPE.
        </p>
      </div>
      <div class="absolute -right-10 -bottom-10 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>
    </div>

    <!-- Cards Resumidos: Entregas (com % de conclusão) e Bimestre Vigente (atalho p/ Admin) -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Card ENTREGAS -->
      <div class="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-between gap-3">
        <div class="flex items-center justify-between">
          <div>
            <span class="text-xs font-bold text-gray-500 uppercase tracking-wider">Entregas ({{ uorgAtualLabel }})</span>
            <div class="flex items-baseline gap-2.5 mt-1">
              <p class="text-3xl font-black text-emerald-600">
                {{ resumoEntregas.concluidas }}<span class="text-lg text-gray-400 font-bold">/{{ resumoEntregas.total }}</span>
              </p>
              <span class="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-emerald-50 text-emerald-700 border border-emerald-200">
                {{ formatarPercentual(resumoEntregas.percentual_conclusao) }}% concluídas
              </span>
            </div>
            <span class="text-[11px] text-gray-400 mt-0.5 block">
              Total no contexto: {{ resumoEntregas.total }} • Concluídas: {{ resumoEntregas.concluidas }} • Pendentes: {{ resumoEntregas.pendentes }}
            </span>
          </div>
          <div class="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold shrink-0">
            <CheckCircleIcon class="w-6 h-6" />
          </div>
        </div>
        <div class="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            class="h-full bg-emerald-500 rounded-full transition-all duration-500"
            :style="{ width: `${Math.min(100, resumoEntregas.percentual_conclusao)}%` }"
          ></div>
        </div>
      </div>

      <!-- Card BIMESTRE VIGENTE (Interativo exclusivamente para Administrador) -->
      <div
        @click="onClickBimestreVigente"
        class="bg-white p-5 rounded-2xl shadow-sm border flex items-center justify-between transition-all"
        :class="isAdmin
          ? 'border-blue-200 hover:border-indigo-400 hover:shadow-md cursor-pointer group'
          : 'border-gray-100 cursor-default'"
      >
        <div>
          <div class="flex items-center gap-2">
            <span class="text-xs font-bold text-gray-500 uppercase tracking-wider">Bimestre Vigente</span>
            <span
              v-if="isAdmin"
              class="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200 group-hover:bg-indigo-600 group-hover:text-white transition"
            >
              Gerenciar Exercício &rarr;
            </span>
          </div>
          <p class="text-2xl font-black text-blue-700 mt-1 group-hover:text-indigo-700 transition">
            {{ bimestreVigente?.nome || '1º Bimestre' }}
          </p>
          <span
            class="text-[11px] font-bold mt-0.5 block"
            :class="bimestreVigente?.status === 'ABERTO' ? 'text-emerald-600' : 'text-amber-600'"
          >
            {{ bimestreVigente?.status === 'ABERTO' ? '● ABERTO PARA ENVIO' : '○ FECHADO' }}
            <template v-if="bimestreVigente?.data_fechamento_regular">
              • Limite: {{ formatarDataCurta(bimestreVigente.data_fechamento_regular) }}
            </template>
          </span>
        </div>
        <div class="w-12 h-12 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center font-bold shrink-0">
          <CalendarDaysIcon class="w-6 h-6" />
        </div>
      </div>
    </div>

    <!-- Sinalização de Bimestres Respondidos (Exibido para Chefe de Setor ou quando uma UORG está selecionada) -->
    <div
      v-if="isChefeSetor || (uorgSelecionadaId && metricasUorg?.bimestres_respondidos?.length)"
      class="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 space-y-3"
    >
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h2 class="text-sm font-black text-gray-900 flex items-center gap-2">
            <span class="w-2 h-4 bg-emerald-600 rounded-full"></span>
            <span>Situação de Resposta dos Bimestres ({{ metricasUorg?.uorg?.sigla || usuario?.uorg_sigla }})</span>
          </h2>
          <p class="text-xs text-gray-500">
            Acompanhe os bimestres já respondidos pela unidade e os relatórios que receberam Parecer Institucional.
          </p>
        </div>
        <span class="text-xs font-extrabold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full w-fit">
          {{ totalBimestresRespondidos }}/6 Bimestres Respondidos
        </span>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
        <div
          v-for="bim in metricasUorg?.bimestres_respondidos || []"
          :key="bim.bimestre_id"
          @click="abrirBimestreCard(bim)"
          class="p-3 rounded-xl border transition cursor-pointer flex flex-col justify-between gap-1.5 relative"
          :class="bim.tem_feedback
            ? 'bg-gradient-to-br from-amber-50 via-yellow-50 to-emerald-50 border-2 border-amber-400 ring-2 ring-amber-200/60 shadow-xs'
            : bim.respondido
              ? 'bg-emerald-50/70 border-emerald-300 hover:bg-emerald-100/70'
              : bim.status_relatorio === 'EM_EDICAO'
                ? 'bg-orange-50/70 border-orange-200 hover:bg-orange-100/70'
                : 'bg-gray-50 border-gray-200 hover:bg-gray-100'"
        >
          <div class="flex items-center justify-between">
            <span class="text-xs font-black text-gray-900">{{ bim.bimestre_numero }}º Bimestre</span>
            <span
              v-if="bim.respondido"
              class="w-5 h-5 rounded-full bg-emerald-600 text-white text-[10px] font-black flex items-center justify-center"
              title="Bimestre Respondido"
            >
              ✓
            </span>
            <span
              v-else-if="bim.status_relatorio === 'EM_EDICAO'"
              class="w-5 h-5 rounded-full bg-orange-500 text-white text-[10px] font-black flex items-center justify-center"
              title="Em Edição"
            >
              ✎
            </span>
            <span
              v-else
              class="w-5 h-5 rounded-full bg-gray-200 text-gray-500 text-[10px] font-bold flex items-center justify-center"
            >
              •
            </span>
          </div>

          <div class="flex flex-wrap items-center gap-1">
            <span
              class="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full"
              :class="bim.respondido
                ? 'bg-emerald-100 text-emerald-800'
                : bim.status_relatorio === 'EM_EDICAO'
                  ? 'bg-orange-100 text-orange-800'
                  : 'bg-gray-200 text-gray-600'"
            >
              {{ bim.respondido ? 'Respondido' : (bim.status_relatorio === 'EM_EDICAO' ? 'Em Edição' : 'Não Respondido') }}
            </span>

            <span
              v-if="bim.tem_feedback"
              class="inline-flex items-center gap-1 text-[10px] font-black px-2 py-0.5 rounded-full bg-amber-500 text-white shadow-2xs"
            >
              🏛️ Parecer
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Painel Analítico de Entregas e Indicadores com Filtros Hierárquicos por Perfil -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="p-5 border-b border-gray-100 bg-slate-50/60 space-y-4">
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <h2 class="text-base font-black text-gray-900 flex items-center gap-2">
              <span class="w-2 h-5 bg-indigo-600 rounded-full"></span>
              Painel Analítico de Entregas e Indicadores
            </h2>
            <p class="text-xs text-gray-500 mt-0.5">
              <template v-if="isChefeSetor">
                Acompanhamento das entregas planejadas e evolução temporal dos indicadores do seu setor.
              </template>
              <template v-else-if="isChefeDivisao">
                Filtre entre a sua Divisão e os Setores subordinados para inspecionar entregas e indicadores.
              </template>
              <template v-else-if="isGerente">
                Filtre entre as Divisões e Setores subordinados à sua Gerência ({{ usuario?.gerencia_sigla }}).
              </template>
              <template v-else>
                Utilize os botões de Gerência (SUP, GAS, GAD, GEP) ou selecione qualquer UORG para análise detalhada.
              </template>
            </p>
          </div>

          <!-- Controles de Filtro (Oculto para Chefe de Setor, que possui apenas 1 UORG) -->
          <div v-if="!isChefeSetor" class="flex flex-wrap items-center gap-2.5">
            <!-- Botões de Filtro com Siglas das Gerências (Exclusivo Superintendente e Administrador) -->
            <div v-if="isSuperintendenteOuAdmin" class="flex items-center gap-1 bg-white p-1 rounded-xl border border-gray-200 shadow-2xs">
              <button
                type="button"
                @click="selecionarFiltroGerencia('')"
                class="px-2.5 py-1.5 rounded-lg text-xs font-extrabold transition cursor-pointer"
                :class="filtroGerenciaSigla === ''
                  ? 'bg-indigo-600 text-white shadow-2xs'
                  : 'text-gray-600 hover:bg-gray-100'"
              >
                Todas
              </button>
              <button
                v-for="gSigla in ['SUP', 'GAS', 'GAD', 'GEP']"
                :key="gSigla"
                type="button"
                @click="selecionarFiltroGerencia(gSigla)"
                class="px-2.5 py-1.5 rounded-lg text-xs font-extrabold transition cursor-pointer"
                :class="filtroGerenciaSigla === gSigla
                  ? 'bg-indigo-600 text-white shadow-2xs'
                  : 'text-gray-600 hover:bg-gray-100'"
              >
                {{ gSigla }}
              </button>
            </div>

            <!-- Dropdown de Seleção de UORG -->
            <div class="flex items-center gap-2">
              <label for="dashboardUorgSelect" class="text-xs font-bold text-gray-700 uppercase tracking-wider shrink-0">
                UORG:
              </label>
              <select
                id="dashboardUorgSelect"
                v-model="uorgSelecionadaId"
                @change="onUorgSelectChange"
                class="text-xs font-semibold border border-gray-300 rounded-xl px-3.5 py-2 bg-white focus:ring-2 focus:ring-indigo-500 outline-none min-w-[260px]"
              >
                <option :value="null">
                  — Nenhuma UORG selecionada (Resumo {{ uorgsNoContextoFiltrado.length }} UORGs) —
                </option>
                <option v-for="u in uorgsNoContextoFiltrado" :key="u.id" :value="u.id">
                  {{ u.gerencia_sigla ? `[${u.gerencia_sigla}] ` : '' }}{{ u.sigla }} — {{ u.nome }} ({{ u.concluidas ?? 0 }}/{{ u.total ?? 0 }})
                </option>
              </select>

              <button
                v-if="uorgSelecionadaId !== null"
                type="button"
                @click="limparSelecaoUorg"
                class="px-2.5 py-2 text-xs font-bold text-gray-600 hover:text-gray-900 bg-white hover:bg-gray-100 border border-gray-300 rounded-xl transition cursor-pointer"
                title="Limpar seleção de UORG e voltar aos cards compactos X/Y"
              >
                ✕ Ver Todas
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- MODO 1: Nenhuma UORG selecionada -> Suprime card maior de entregas e exibe linha organizada com cards menores (SIGLA + X/Y) -->
      <div v-if="!uorgSelecionadaId && !isChefeSetor" class="p-6 space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 class="text-sm font-black text-gray-900 flex items-center gap-2">
              <span>📊</span>
              <span>Entregas Concluídas por UORG no Contexto ({{ filtroGerenciaSigla || 'Visão Geral' }})</span>
            </h3>
            <p class="text-xs text-gray-500">
              Formato <b>X/Y</b> (onde <b>X</b> = entregas concluídas e <b>Y</b> = total de entregas planejadas). Clique em uma sigla para detalhar a unidade.
            </p>
          </div>
          <span class="text-xs font-bold text-indigo-700 bg-indigo-50 border border-indigo-200 px-3 py-1 rounded-full w-fit">
            {{ uorgsNoContextoFiltrado.length }} UORG(s) listada(s)
          </span>
        </div>

        <!-- Linha / Grade Organizada de Cards Compactos com Apenas SIGLA e X/Y -->
        <div class="flex flex-wrap items-stretch gap-3">
          <button
            v-for="u in uorgsNoContextoFiltrado"
            :key="u.id"
            type="button"
            @click="selecionarUorgCard(u.id)"
            class="group min-w-[110px] flex-1 sm:flex-initial px-4 py-3.5 rounded-xl border text-left transition-all cursor-pointer flex flex-col justify-between gap-2 hover:shadow-md hover:-translate-y-0.5"
            :class="u.tem_feedback
              ? 'bg-gradient-to-br from-amber-50/90 via-white to-emerald-50/60 border-2 border-amber-400 ring-1 ring-amber-200'
              : 'bg-slate-50/70 hover:bg-white border-gray-200 hover:border-indigo-400'"
            :title="`${u.sigla} — ${u.nome}: ${u.concluidas ?? 0} de ${u.total ?? 0} entregas concluídas`"
          >
            <div class="flex items-center justify-between gap-2">
              <span class="text-xs font-black text-gray-900 group-hover:text-indigo-700 tracking-tight">
                {{ u.sigla }}
              </span>
              <span
                v-if="u.tem_feedback"
                class="text-[10px] px-1.5 py-0.5 rounded-full bg-amber-500 text-white font-black"
                title="Relatório com Parecer Institucional emitido"
              >
                🏛️
              </span>
            </div>

            <div class="flex items-baseline justify-between gap-2">
              <span class="text-lg font-black text-emerald-600 leading-none">
                {{ u.concluidas ?? 0 }}<span class="text-xs text-gray-400 font-bold">/{{ u.total ?? 0 }}</span>
              </span>
              <span class="text-[10px] font-bold text-gray-400">
                {{ u.total ? Math.round(((u.concluidas || 0) / u.total) * 100) : 0 }}%
              </span>
            </div>

            <div class="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
              <div
                class="h-full bg-emerald-500 rounded-full transition-all"
                :style="{ width: `${u.total ? Math.min(100, Math.round(((u.concluidas || 0) / u.total) * 100)) : 0}%` }"
              ></div>
            </div>
          </button>
        </div>
      </div>

      <!-- MODO 2: UORG Selecionada -> Exibe Card Maior de Entregas + Gráficos de Indicadores com Eixo X por Temporalidade -->
      <div v-else-if="carregandoMetricas" class="p-12 text-center">
        <div class="inline-block animate-spin rounded-full h-7 w-7 border-4 border-indigo-600 border-t-transparent"></div>
        <p class="text-xs text-gray-500 mt-2 font-medium">Carregando indicadores e entregas da UORG...</p>
      </div>

      <div v-else class="p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Coluna 1: Status das Entregas da UORG Selecionada -->
        <div class="lg:col-span-5 space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-black text-gray-900 flex items-center gap-2">
              <span>📦</span>
              <span>Status das Entregas ({{ metricasUorg?.uorg?.sigla }})</span>
            </h3>
            <span class="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
              {{ metricasUorg?.resumo_entregas?.concluidas || 0 }}/{{ metricasUorg?.resumo_entregas?.total || 0 }}
              ({{ formatarPercentual(metricasUorg?.resumo_entregas?.percentual_conclusao || 0) }}%)
            </span>
          </div>

          <div v-if="!metricasUorg?.entregas?.length" class="p-8 rounded-xl bg-gray-50 border border-gray-100 text-center text-xs text-gray-500">
            Nenhuma entrega planejada cadastrada para esta UORG no exercício.
          </div>

          <div v-else class="space-y-2.5 max-h-[520px] overflow-y-auto pr-1">
            <div
              v-for="ent in metricasUorg.entregas"
              :key="ent.id"
              class="p-3.5 rounded-xl border transition flex items-start justify-between gap-3"
              :class="ent.concluida
                ? 'bg-emerald-50/50 border-emerald-200'
                : 'bg-white border-gray-200'"
            >
              <div class="space-y-1">
                <p class="text-xs font-bold text-gray-900 leading-snug">{{ ent.titulo }}</p>
                <p v-if="ent.descricao" class="text-[11px] text-gray-500 line-clamp-2">{{ ent.descricao }}</p>
                <p v-if="ent.concluida && ent.bimestre_conclusao_nome" class="text-[10px] font-semibold text-emerald-700">
                  ✓ Concluída no {{ ent.bimestre_conclusao_nome }}
                </p>
              </div>
              <span
                class="px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase shrink-0 border"
                :class="ent.concluida
                  ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                  : 'bg-amber-50 text-amber-800 border-amber-200'"
              >
                {{ ent.concluida ? 'Concluída' : 'Em Andamento' }}
              </span>
            </div>
          </div>
        </div>

        <!-- Coluna 2: Gráficos Específicos de Indicadores com Eixo X por Temporalidade e Linha de Meta Alinhada -->
        <div class="lg:col-span-7 space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-black text-gray-900 flex items-center gap-2">
              <span>📈</span>
              <span>Indicadores Estratégicos e Metas ({{ metricasUorg?.uorg?.sigla }})</span>
            </h3>
            <span class="text-xs text-gray-400 font-medium">
              {{ metricasUorg?.indicadores?.length || 0 }} indicador(es) ativo(s)
            </span>
          </div>

          <div v-if="!metricasUorg?.indicadores?.length" class="p-8 rounded-xl bg-gray-50 border border-gray-100 text-center text-xs text-gray-500">
            Nenhum indicador anual cadastrado para esta UORG no exercício.
          </div>

          <div v-else class="space-y-4">
            <div
              v-for="ind in metricasUorg.indicadores"
              :key="ind.id"
              class="p-4 rounded-xl border border-gray-200 bg-slate-50/40 space-y-3"
            >
              <div class="flex flex-wrap items-start justify-between gap-2">
                <div>
                  <h4 class="text-xs font-black text-gray-900">{{ ind.nome }}</h4>
                  <p v-if="ind.descricao" class="text-[11px] text-gray-500">{{ ind.descricao }}</p>
                </div>
                <div class="flex items-center gap-1.5">
                  <span class="px-2 py-0.5 text-[10px] font-bold rounded bg-gray-100 text-gray-700 border border-gray-200">
                    Temporalidade: {{ ind.periodicidade }}
                  </span>
                  <span class="px-2.5 py-0.5 text-[10px] font-black rounded bg-indigo-50 text-indigo-900 border border-indigo-200">
                    Meta: {{ formatarMetaIndicador(ind) }}
                  </span>
                </div>
              </div>

              <!-- Gráfico Visual de Barras + Linha de Meta Alinhada Geometricamente -->
              <div class="bg-white p-3.5 rounded-xl border border-gray-100">
                <!-- Faixa superior para acomodar os rótulos flutuantes sem distorcer a escala 0%..100% da área de plotagem -->
                <div class="pt-6 px-2">
                  <!-- Área de Plotagem Pura (0% na base até 100% no topo, sem padding vertical) -->
                  <div class="relative h-36 w-full border-b border-gray-200">
                    <!-- Linha de Meta Horizontal: usa exatamente o mesmo calcularPercentualEscala(valor, ind) da altura das barras -->
                    <div
                      v-if="ind.meta_valor !== null && ind.meta_valor !== undefined"
                      class="absolute left-0 right-0 h-0 border-t-2 border-dashed border-indigo-600 pointer-events-none z-20"
                      :style="{ bottom: `${calcularPercentualEscala(ind.meta_valor, ind)}%` }"
                    >
                      <span class="absolute right-0 -top-5 bg-indigo-600 text-white text-[9px] font-bold px-1.5 py-0.5 rounded shadow-xs whitespace-nowrap">
                        Meta {{ ind.meta_valor }}{{ ind.unidade_medida === '%' ? '%' : '' }}
                      </span>
                    </div>

                    <!-- Colunas por Competência na Temporalidade do Indicador -->
                    <div
                      class="absolute inset-0 flex items-end px-1"
                      :class="(ind.serie_historica?.length || 0) > 6 ? 'gap-1 sm:gap-1.5' : 'gap-2 sm:gap-3'"
                    >
                      <div
                        v-for="(ponto, pIdx) in ind.serie_historica"
                        :key="pIdx"
                        class="flex-1 h-full relative flex justify-center items-end group"
                      >
                        <!-- Valor numérico posicionado exatamente no topo da barra -->
                        <span
                          v-if="ponto.valor_apurado !== null && ponto.valor_apurado !== undefined"
                          class="absolute text-[10px] font-extrabold leading-none pb-1 whitespace-nowrap z-10"
                          :class="ponto.meta_atingida ? 'text-emerald-700' : 'text-rose-600'"
                          :style="{ bottom: `${calcularPercentualEscala(ponto.valor_apurado, ind)}%` }"
                        >
                          {{ ponto.valor_apurado }}{{ ind.unidade_medida === '%' ? '%' : '' }}
                        </span>
                        <span
                          v-else
                          class="absolute bottom-1.5 text-[9px] text-gray-400 leading-none"
                        >
                          —
                        </span>

                        <!-- Barra com altura exata na mesma escala (0%..100%) da linha de meta -->
                        <div
                          class="w-full max-w-[34px] rounded-t-md transition-all duration-300"
                          :class="getCorBarraIndicador(ponto)"
                          :style="{
                            height: ponto.valor_apurado !== null && ponto.valor_apurado !== undefined
                              ? `${calcularPercentualEscala(ponto.valor_apurado, ind)}%`
                              : '4px'
                          }"
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Eixo X (Rótulos organizados segundo a temporalidade de cada indicador) -->
                <div
                  class="flex items-center pt-1.5 px-3"
                  :class="(ind.serie_historica?.length || 0) > 6 ? 'gap-1 sm:gap-1.5' : 'gap-2 sm:gap-3'"
                >
                  <div
                    v-for="(ponto, pIdx) in ind.serie_historica"
                    :key="pIdx"
                    class="flex-1 text-center truncate text-[10px] font-semibold text-gray-600"
                    :title="`${ponto.competencia} (${ponto.bimestre_nome})`"
                  >
                    {{ ponto.rotulo_eixo_x || abreviarCompetencia(ponto, ind.periodicidade) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Rodapé Institucional do Painel -->
    <div class="bg-gray-50 border border-gray-200 rounded-xl p-5 text-xs text-gray-500 flex flex-col sm:flex-row items-center justify-between gap-3">
      <div class="flex items-center gap-2 text-gray-600">
        <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
        <span>Sistema Integrado ao Banco Corporativo SQLite/PostgreSQL e Framework SETISD HC-UFPE</span>
      </div>
      <div class="text-gray-400">Versão 1.0.0 <!-- version --> • EBSERH / MEC</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import {
  CheckCircleIcon,
  CalendarDaysIcon
} from '@heroicons/vue/24/outline';
import { gestaoApi } from '../services/gestaoApi';

const router = useRouter();

const usuario = ref<any>(null);
const exercicio = ref<any>(null);
const uorgsAcessiveis = ref<any[]>([]);
const filtroGerenciaSigla = ref<string>('');
const uorgSelecionadaId = ref<number | null>(null);
const metricasUorg = ref<any>(null);
const carregandoMetricas = ref(false);

const perfilUsuario = computed(() => (usuario.value?.perfil || '').toUpperCase());
const tipoUorgUsuario = computed(() => (usuario.value?.tipo_uorg || 'SETOR').toUpperCase());

const isAdmin = computed(() => perfilUsuario.value === 'ADMINISTRADOR');
const isSuperintendenteOuAdmin = computed(() =>
  ['ADMINISTRADOR', 'SUPERINTENDENTE'].includes(perfilUsuario.value)
);
const isGerente = computed(() => perfilUsuario.value === 'GERENTE');
const isChefeDivisao = computed(() =>
  ['CHEFE', 'CHEFE_UORG'].includes(perfilUsuario.value) && tipoUorgUsuario.value === 'DIVISAO'
);
const isChefeSetor = computed(() =>
  ['CHEFE', 'CHEFE_UORG'].includes(perfilUsuario.value) && tipoUorgUsuario.value !== 'DIVISAO'
);

const uorgsNoContextoFiltrado = computed(() => {
  if (!filtroGerenciaSigla.value) return uorgsAcessiveis.value;
  return uorgsAcessiveis.value.filter(
    (u: any) => (u.gerencia_sigla || '').toUpperCase() === filtroGerenciaSigla.value.toUpperCase()
  );
});

const bimestreVigente = computed(() => {
  const bims = exercicio.value?.bimestres || [];
  return bims.find((b: any) => b.status === 'ABERTO') || bims[0] || null;
});

const uorgAtualLabel = computed(() => {
  if (uorgSelecionadaId.value && metricasUorg.value?.uorg?.sigla) {
    return metricasUorg.value.uorg.sigla;
  }
  if (filtroGerenciaSigla.value) {
    return `Gerência ${filtroGerenciaSigla.value}`;
  }
  if (isChefeDivisao.value && usuario.value?.uorg_sigla) {
    return `${usuario.value.uorg_sigla} + Subordinados`;
  }
  if (isGerente.value && usuario.value?.gerencia_sigla) {
    return `Gerência ${usuario.value.gerencia_sigla}`;
  }
  return 'Todas no Contexto';
});

const resumoEntregas = computed(() => {
  if (uorgSelecionadaId.value && metricasUorg.value?.resumo_entregas) {
    return metricasUorg.value.resumo_entregas;
  }
  const lista = uorgsNoContextoFiltrado.value;
  const total = lista.reduce((acc: number, u: any) => acc + Number(u.total || 0), 0);
  const concluidas = lista.reduce((acc: number, u: any) => acc + Number(u.concluidas || 0), 0);
  const pendentes = Math.max(0, total - concluidas);
  const percentual_conclusao = total > 0 ? Number(((concluidas / total) * 100).toFixed(1)) : 0;
  return { total, concluidas, pendentes, percentual_conclusao };
});

const totalBimestresRespondidos = computed(() => {
  const bims = metricasUorg.value?.bimestres_respondidos || [];
  return bims.filter((b: any) => b.respondido).length;
});

function onClickBimestreVigente() {
  if (isAdmin.value) {
    router.push('/gestao-exercicio');
  }
}

function abrirBimestreCard(bim: any) {
  const uId = metricasUorg.value?.uorg?.id || uorgSelecionadaId.value || usuario.value?.uorg_id;
  if (!uId) return;
  if (isChefeSetor.value || (isChefeDivisao.value && Number(uId) === Number(usuario.value?.uorg_id))) {
    router.push(`/preenchimento?bimestre=${bim.bimestre_id}&uorg=${uId}`);
  } else {
    router.push(`/consolidado?bimestre=${bim.bimestre_id}&uorg=${uId}`);
  }
}

function selecionarFiltroGerencia(sigla: string) {
  filtroGerenciaSigla.value = sigla;
  // Quando muda a gerência no filtro rápido, limpa a UORG selecionada para exibir a linha de cards X/Y daquela gerência
  if (uorgSelecionadaId.value !== null) {
    const pertence = uorgsNoContextoFiltrado.value.some((u: any) => u.id === uorgSelecionadaId.value);
    if (!pertence) {
      uorgSelecionadaId.value = null;
      metricasUorg.value = null;
    }
  }
}

async function selecionarUorgCard(uorgId: number) {
  uorgSelecionadaId.value = uorgId;
  await carregarMetricasUorg();
}

function limparSelecaoUorg() {
  uorgSelecionadaId.value = null;
  metricasUorg.value = null;
}

async function onUorgSelectChange() {
  if (!uorgSelecionadaId.value) {
    metricasUorg.value = null;
    return;
  }
  await carregarMetricasUorg();
}

function formatarPercentual(val: number): string {
  if (!val || isNaN(val)) return '0';
  return Number.isInteger(val) ? String(val) : val.toFixed(1);
}

function formatarDataCurta(dtStr?: string | null): string {
  if (!dtStr) return '';
  const clean = dtStr.split('T')[0];
  const p = clean.split('-');
  if (p.length === 3) return `${p[2]}/${p[1]}/${p[0]}`;
  return dtStr;
}

function formatarMetaIndicador(ind: any): string {
  const op = ind.meta_operador || 'MAIOR_IGUAL';
  const un = ind.unidade_medida || '';
  if (op === 'MAIOR_IGUAL') return `≥ ${ind.meta_valor} ${un}`;
  if (op === 'MENOR_IGUAL') return `≤ ${ind.meta_valor} ${un}`;
  if (op === 'IGUAL') return `= ${ind.meta_valor} ${un}`;
  if (op === 'ENTRE') return `${ind.meta_valor} a ${ind.meta_valor_max ?? ''} ${un}`;
  return `${ind.meta_valor} ${un}`;
}

/**
 * Calcula o teto da escala vertical do gráfico (100% da área de plotagem)
 * usando estritamente os valores do próprio indicador e sua meta (sem forçar 100 para unidades absolutas),
 * garantindo alinhamento geométrico exato entre o topo das barras e a linha da meta.
 */
function obterTetoEscala(ind: any): number {
  const valores = (ind.serie_historica || [])
    .filter((s: any) => s.valor_apurado !== null && s.valor_apurado !== undefined && !isNaN(Number(s.valor_apurado)))
    .map((s: any) => Number(s.valor_apurado));
  const meta = ind.meta_valor !== null && ind.meta_valor !== undefined ? Number(ind.meta_valor) : 0;
  const metaMax = ind.meta_valor_max !== null && ind.meta_valor_max !== undefined ? Number(ind.meta_valor_max) : 0;
  const maiorValor = Math.max(...valores, meta, metaMax, 1);
  return maiorValor * 1.2;
}

function calcularPercentualEscala(valor: number | null | undefined, ind: any): number {
  if (valor === null || valor === undefined || isNaN(Number(valor))) return 0;
  const num = Number(valor);
  if (num <= 0) return 0;
  const teto = obterTetoEscala(ind);
  if (teto <= 0) return 0;
  const pct = (num / teto) * 100;
  return Math.min(100, Math.max(0, Number(pct.toFixed(2))));
}

function getCorBarraIndicador(ponto: any): string {
  if (ponto.nao_aplicavel || ponto.valor_apurado === null || ponto.valor_apurado === undefined) {
    return 'bg-gray-200';
  }
  return ponto.meta_atingida ? 'bg-emerald-500' : 'bg-rose-500';
}

function abreviarCompetencia(ponto: any, periodicidade?: string): string {
  const per = (periodicidade || '').toUpperCase();
  const comp = (ponto.competencia || '').trim();
  const mesesMap: Record<string, string> = {
    Janeiro: 'Jan',
    Fevereiro: 'Fev',
    Março: 'Mar',
    Abril: 'Abr',
    Maio: 'Mai',
    Junho: 'Jun',
    Julho: 'Jul',
    Agosto: 'Ago',
    Setembro: 'Set',
    Outubro: 'Out',
    Novembro: 'Nov',
    Dezembro: 'Dez'
  };
  if (per === 'MENSAL' && mesesMap[comp]) {
    return mesesMap[comp];
  }
  if (per === 'TRIMESTRAL') {
    const tMap: Record<number, string> = { 2: '1ºT', 3: '2ºT', 5: '3ºT', 6: '4ºT' };
    return tMap[ponto.bimestre_numero] || comp.slice(0, 4);
  }
  if (per === 'QUADRIMESTRAL') {
    const qMap: Record<number, string> = { 2: '1ºQ', 4: '2ºQ', 6: '3ºQ' };
    return qMap[ponto.bimestre_numero] || comp.slice(0, 4);
  }
  if (per === 'SEMESTRAL') {
    const sMap: Record<number, string> = { 3: '1ºS', 6: '2ºS' };
    return sMap[ponto.bimestre_numero] || comp.slice(0, 4);
  }
  return `${ponto.bimestre_numero}ºB`;
}

async function carregarMetricasUorg() {
  if (!uorgSelecionadaId.value) return;
  carregandoMetricas.value = true;
  try {
    metricasUorg.value = await gestaoApi.obterMetricasDashboardUorg(
      uorgSelecionadaId.value,
      exercicio.value?.id
    );
  } catch (err) {
    console.error('Erro ao carregar métricas da UORG no dashboard:', err);
  } finally {
    carregandoMetricas.value = false;
  }
}

onMounted(async () => {
  try {
    const [me, ex, uorgs] = await Promise.all([
      gestaoApi.obterUsuarioLogado(),
      gestaoApi.obterExercicioAtivo(),
      gestaoApi.obterUorgsAcessiveisDashboard()
    ]);
    usuario.value = me;
    exercicio.value = ex;
    uorgsAcessiveis.value = uorgs || [];

    // Para Chefe de Setor, seleciona automaticamente o próprio Setor e exibe seus bimestres respondidos e gráficos.
    // Para Chefe de Divisão, Gerente, Superintendente e Administrador, inicia sem UORG selecionada (null)
    // para exibir a linha organizada de cards compactos (SIGLA + X/Y) do contexto!
    const perfil = (me?.perfil || '').toUpperCase();
    const tipoUorg = (me?.tipo_uorg || 'SETOR').toUpperCase();
    if (['CHEFE', 'CHEFE_UORG'].includes(perfil) && tipoUorg !== 'DIVISAO') {
      if (me?.uorg_id && uorgsAcessiveis.value.some((u: any) => u.id === me.uorg_id)) {
        uorgSelecionadaId.value = me.uorg_id;
      } else if (uorgsAcessiveis.value.length > 0) {
        uorgSelecionadaId.value = uorgsAcessiveis.value[0].id;
      }
      await carregarMetricasUorg();
    } else {
      uorgSelecionadaId.value = null;
    }
  } catch (err) {
    console.error('Erro ao inicializar dashboard:', err);
  }
});
</script>
