<template>
  <div class="space-y-6 max-w-7xl mx-auto pb-12">
    <!-- Cabeçalho Principal -->
    <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <div class="flex items-center gap-2">
          <router-link to="/matriz" class="text-indigo-600 hover:text-indigo-800 text-xs font-bold flex items-center gap-1 transition">
            ← Voltar para Matriz
          </router-link>
        </div>
        <h1 class="text-2xl font-black text-slate-900 mt-1 flex items-center gap-2 tracking-tight">
          <span class="inline-block w-2.5 h-6 bg-indigo-600 rounded-full"></span>
          Planejamento Anual da Unidade
        </h1>
        <p class="text-xs text-slate-500 mt-0.5">
          Definição institucional de entregas e indicadores estratégicos para o Exercício {{ exercicio?.ano || 2026 }} (Fase de Planejamento).
        </p>
      </div>

      <!-- Seletor de UORG (Admin / Gestores) ou Badge da UORG da Chefia -->
      <div class="flex flex-wrap items-center gap-3">
        <div v-if="isAdminOuGestor" class="flex items-center gap-2">
          <label for="uorgSelect" class="text-xs font-bold text-slate-600">UORG:</label>
          <select
            id="uorgSelect"
            v-model="uorgSelecionadaId"
            @change="carregarPlanejamento"
            class="text-xs font-medium border border-slate-300 rounded-lg px-3 py-2 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
          >
            <optgroup v-for="g in estrutura" :key="g.id" :label="`${g.sigla} - ${g.nome}`">
              <option v-for="u in g.uorgs" :key="u.id" :value="u.id">
                {{ u.sigla }} — {{ u.nome }}
              </option>
            </optgroup>
          </select>
        </div>

        <div v-else class="bg-indigo-50 border border-indigo-100 px-4 py-2 rounded-xl text-xs font-bold text-indigo-950 flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-indigo-600"></span>
          {{ uorgAtual?.sigla }} — {{ uorgAtual?.nome }}
        </div>

        <!-- Ação Administrativa: Abertura / Encerramento do Planejamento -->
        <div v-if="isAdmin" class="flex items-center gap-2">
          <button
            v-if="!planejamentoAberto"
            @click="abrirJanelaPlanejamento"
            :disabled="salvandoStatus"
            class="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-lg shadow-sm transition flex items-center gap-1.5"
          >
            <span v-if="salvandoStatus" class="inline-block animate-spin w-3 h-3 border-2 border-white border-t-transparent rounded-full"></span>
            <span>🔓 Abrir Planejamento</span>
          </button>
          <button
            v-else
            @click="fecharJanelaPlanejamento"
            :disabled="salvandoStatus"
            class="px-3.5 py-2 bg-slate-700 hover:bg-slate-800 text-white text-xs font-bold rounded-lg shadow-sm transition flex items-center gap-1.5"
          >
            <span v-if="salvandoStatus" class="inline-block animate-spin w-3 h-3 border-2 border-white border-t-transparent rounded-full"></span>
            <span>🔒 Fechar Planejamento</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Banner de Status da Janela de Planejamento -->
    <div
      class="p-5 rounded-2xl border flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition shadow-sm"
      :class="planejamentoAberto 
        ? 'bg-emerald-50/80 border-emerald-200 text-emerald-950' 
        : 'bg-amber-50/80 border-amber-200 text-amber-950'"
    >
      <div class="flex items-start sm:items-center gap-3">
        <div
          class="w-10 h-10 rounded-xl flex items-center justify-center text-lg shrink-0"
          :class="planejamentoAberto ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'"
        >
          {{ planejamentoAberto ? '🟢' : '🔒' }}
        </div>
        <div>
          <h2 class="text-sm font-black tracking-tight">
            {{ planejamentoAberto 
              ? 'Janela de Planejamento Anual Aberta' 
              : 'Janela de Planejamento Anual Encerrada' }}
          </h2>
          <p class="text-xs mt-0.5" :class="planejamentoAberto ? 'text-emerald-800' : 'text-amber-800'">
            {{ planejamentoAberto 
              ? 'As chefias podem cadastrar, alterar e inativar entregas e indicadores estratégicos para o exercício corrente.' 
              : 'O ciclo de planejamento foi homologado. Novas inclusões e alterações operacionais estão bloqueadas.' }}
          </p>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <span
          class="px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider border"
          :class="planejamentoAberto 
            ? 'bg-emerald-100 text-emerald-800 border-emerald-300' 
            : 'bg-amber-100 text-amber-800 border-amber-300'"
        >
          Status: {{ exercicio?.status || 'PLANEJAMENTO' }}
        </span>
      </div>
    </div>

    <!-- Cards de Resumo & Limites -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex items-center justify-between">
        <div>
          <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Entregas Cadastradas</span>
          <div class="text-2xl font-black text-slate-900 mt-1">{{ entregas.length }}</div>
          <span class="text-[11px] text-slate-500 mt-0.5">Metas institucionais anuais</span>
        </div>
        <div class="w-11 h-11 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center text-xl font-bold">
          📦
        </div>
      </div>

      <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex items-center justify-between">
        <div>
          <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Indicadores Ativos</span>
          <div class="text-2xl font-black text-slate-900 mt-1 flex items-baseline gap-1.5">
            <span>{{ indicadores.length }}</span>
            <span class="text-xs font-semibold text-slate-400">/ 3 máx.</span>
          </div>
          <span 
            class="text-[11px] font-bold"
            :class="indicadores.length >= 3 ? 'text-amber-600' : 'text-emerald-600'"
          >
            {{ indicadores.length >= 3 ? 'Limite máximo atingido (RF-IND-01)' : `${3 - indicadores.length} vaga(s) disponível(is)` }}
          </span>
        </div>
        <div 
          class="w-11 h-11 rounded-xl flex items-center justify-center text-xl font-bold"
          :class="indicadores.length >= 3 ? 'bg-amber-50 text-amber-600' : 'bg-emerald-50 text-emerald-600'"
        >
          📈
        </div>
      </div>

      <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex items-center justify-between">
        <div>
          <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Unidade Atual</span>
          <div class="text-lg font-black text-slate-900 mt-1 truncate max-w-[200px]" :title="uorgAtual?.nome">
            {{ uorgAtual?.sigla || '...' }}
          </div>
          <span class="text-[11px] text-slate-500 mt-0.5 truncate block max-w-[200px]">
            {{ uorgAtual?.nome || 'Carregando dados...' }}
          </span>
        </div>
        <div class="w-11 h-11 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center text-xl font-bold">
          🏢
        </div>
      </div>
    </div>

    <!-- Feedback / Mensagem de Alerta -->
    <div
      v-if="mensagemAlerta"
      class="p-4 rounded-xl border text-xs font-bold flex items-center justify-between transition animate-fadeIn"
      :class="mensagemAlerta.tipo === 'sucesso' 
        ? 'bg-emerald-50 text-emerald-800 border-emerald-200' 
        : 'bg-red-50 text-red-800 border-red-200'"
    >
      <div class="flex items-center gap-2">
        <span>{{ mensagemAlerta.tipo === 'sucesso' ? '✅' : '⚠️' }}</span>
        <span>{{ mensagemAlerta.texto }}</span>
      </div>
      <button @click="mensagemAlerta = null" class="text-slate-400 hover:text-slate-600 text-sm font-bold">✕</button>
    </div>

    <!-- Spinner de Carregamento -->
    <div v-if="carregando" class="text-center py-16 bg-white rounded-2xl border border-slate-100">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-600 border-t-transparent"></div>
      <p class="text-xs text-slate-500 mt-3 font-semibold">Carregando catálogo de planejamento da unidade...</p>
    </div>

    <div v-else class="space-y-8">
      <!-- ========================================== -->
      <!-- SEÇÃO 1: ENTREGAS INSTITUCIONAIS           -->
      <!-- ========================================== -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <div class="p-6 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-50/50">
          <div>
            <h2 class="text-base font-black text-slate-900 flex items-center gap-2">
              <span class="text-lg">📦</span>
              Entregas Institucionais Planejadas
            </h2>
            <p class="text-xs text-slate-500 mt-0.5">
              Projetos, ações e metas de impacto da UORG previstas para o ano (RN-ENT-01 a RN-ENT-03).
            </p>
          </div>

          <button
            v-if="podeModificar"
            @click="abrirModalNovaEntrega"
            class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl shadow-sm transition flex items-center gap-1.5 self-start sm:self-auto"
          >
            <span>➕</span>
            <span>Nova Entrega</span>
          </button>
        </div>

        <div v-if="entregas.length === 0" class="p-12 text-center text-slate-400">
          <div class="text-4xl mb-2">📭</div>
          <p class="text-sm font-bold text-slate-600">Nenhuma entrega cadastrada para esta UORG.</p>
          <p class="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            Utilize o botão "Nova Entrega" acima para cadastrar os compromissos institucionais da sua unidade para o exercício.
          </p>
        </div>

        <div v-else class="divide-y divide-slate-100">
          <div
            v-for="(ent, idx) in entregas"
            :key="ent.id"
            class="p-5 hover:bg-slate-50/70 transition flex flex-col md:flex-row md:items-start justify-between gap-4"
          >
            <div class="flex items-start gap-3.5">
              <span class="w-7 h-7 rounded-lg bg-indigo-100 text-indigo-800 text-xs font-black flex items-center justify-center shrink-0 mt-0.5">
                {{ idx + 1 }}
              </span>
              <div>
                <h3 class="text-sm font-bold text-slate-900 leading-snug">{{ ent.titulo }}</h3>
                <p v-if="ent.descricao" class="text-xs text-slate-600 mt-1 whitespace-pre-line leading-relaxed">
                  {{ ent.descricao }}
                </p>
                <div class="flex items-center gap-2 mt-2">
                  <span
                    v-if="ent.concluida"
                    class="px-2 py-0.5 rounded text-[10px] font-black uppercase bg-emerald-100 text-emerald-800 border border-emerald-200"
                  >
                    Concluída
                  </span>
                  <span
                    v-else
                    class="px-2 py-0.5 rounded text-[10px] font-black uppercase bg-slate-100 text-slate-600 border border-slate-200"
                  >
                    Em Andamento
                  </span>
                </div>
              </div>
            </div>

            <!-- Botões de Ação na Entrega -->
            <div v-if="podeModificar" class="flex items-center gap-1.5 shrink-0 self-end md:self-start">
              <button
                @click="abrirModalEditarEntrega(ent)"
                class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-lg transition"
                title="Editar Entrega"
              >
                ✏️ Editar
              </button>
              <button
                @click="confirmarInativarEntrega(ent)"
                class="px-3 py-1.5 bg-red-50 hover:bg-red-100 text-red-700 text-xs font-bold rounded-lg transition"
                title="Inativar Entrega"
              >
                🗑️ Inativar
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ========================================== -->
      <!-- SEÇÃO 2: INDICADORES ESTRATÉGICOS          -->
      <!-- ========================================== -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <div class="p-6 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-50/50">
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-base font-black text-slate-900 flex items-center gap-2">
                <span class="text-lg">📈</span>
                Indicadores Anuais da UORG
              </h2>
              <span class="text-xs px-2 py-0.5 rounded-full font-bold bg-indigo-100 text-indigo-900">
                1 a 3 Indicadores
              </span>
            </div>
            <p class="text-xs text-slate-500 mt-0.5">
              Métricas prioritárias com metas numéricas e periodicidades bem definidas (RF-IND-01 & RN-IND-01 a RN-IND-06).
            </p>
          </div>

          <button
            v-if="podeModificar"
            @click="abrirModalNovoIndicador"
            :disabled="indicadores.length >= 3"
            class="px-4 py-2 text-xs font-bold rounded-xl shadow-sm transition flex items-center gap-1.5 self-start sm:self-auto"
            :class="indicadores.length >= 3 
              ? 'bg-slate-200 text-slate-400 cursor-not-allowed' 
              : 'bg-emerald-600 hover:bg-emerald-700 text-white'"
            :title="indicadores.length >= 3 ? 'Limite máximo de 3 indicadores atingido' : 'Cadastrar Indicador'"
          >
            <span>➕</span>
            <span>Novo Indicador</span>
          </button>
        </div>

        <div v-if="indicadores.length === 0" class="p-12 text-center text-slate-400">
          <div class="text-4xl mb-2">📊</div>
          <p class="text-sm font-bold text-slate-600">Nenhum indicador cadastrado para esta UORG.</p>
          <p class="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            Cadastre de 1 a 3 indicadores para acompanhar o desempenho institucional da sua unidade bimestralmente.
          </p>
        </div>

        <div v-else class="divide-y divide-slate-100">
          <div
            v-for="(ind, idx) in indicadores"
            :key="ind.id"
            class="p-5 hover:bg-slate-50/70 transition flex flex-col md:flex-row md:items-start justify-between gap-4"
          >
            <div class="flex items-start gap-3.5">
              <span class="w-7 h-7 rounded-lg bg-emerald-100 text-emerald-800 text-xs font-black flex items-center justify-center shrink-0 mt-0.5">
                {{ idx + 1 }}
              </span>
              <div>
                <h3 class="text-sm font-bold text-slate-900 leading-snug">{{ ind.nome }}</h3>
                <p v-if="ind.descricao" class="text-xs text-slate-600 mt-1 leading-relaxed">
                  {{ ind.descricao }}
                </p>

                <!-- Badges de Configuração da Meta -->
                <div class="flex flex-wrap items-center gap-2 mt-2.5">
                  <span class="px-2.5 py-0.5 rounded-md text-[11px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
                    Periodicidade: {{ ind.periodicidade }}
                  </span>
                  <span class="px-2.5 py-0.5 rounded-md text-[11px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
                    Unidade: {{ ind.unidade_medida }}
                  </span>
                  <span class="px-2.5 py-0.5 rounded-md text-[11px] font-black bg-indigo-50 text-indigo-900 border border-indigo-200">
                    Meta: {{ formatarMeta(ind) }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Botões de Ação no Indicador -->
            <div v-if="podeModificar" class="flex items-center gap-1.5 shrink-0 self-end md:self-start">
              <button
                @click="abrirModalEditarIndicador(ind)"
                class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-lg transition"
                title="Editar Indicador"
              >
                ✏️ Editar
              </button>
              <button
                @click="confirmarInativarIndicador(ind)"
                class="px-3 py-1.5 bg-red-50 hover:bg-red-100 text-red-700 text-xs font-bold rounded-lg transition"
                title="Inativar Indicador"
              >
                🗑️ Inativar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================================== -->
    <!-- MODAL: NOVA / EDITAR ENTREGA                                   -->
    <!-- ============================================================== -->
    <div
      v-if="modalEntregaAberto"
      class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn"
    >
      <div class="bg-white rounded-2xl shadow-xl border border-slate-200 w-full max-w-lg overflow-hidden animate-scaleUp">
        <div class="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/70">
          <h3 class="text-sm font-black text-slate-900 flex items-center gap-2">
            <span>📦</span>
            <span>{{ entregaEmEdicao?.id ? 'Editar Entrega Planejada' : 'Nova Entrega Planejada' }}</span>
          </h3>
          <button @click="fecharModalEntrega" class="text-slate-400 hover:text-slate-600 text-sm font-bold">✕</button>
        </div>

        <form @submit.prevent="salvarEntrega" class="p-6 space-y-4">
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Título da Entrega *</label>
            <input
              v-model="formEntrega.titulo"
              type="text"
              required
              minlength="3"
              placeholder="Ex: Implantar prontuário eletrônico no ambulatório"
              class="w-full text-xs border border-slate-300 rounded-lg px-3 py-2.5 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Descrição / Detalhes</label>
            <textarea
              v-model="formEntrega.descricao"
              rows="3"
              placeholder="Explique o escopo da entrega, resultados esperados e alinhamento institucional..."
              class="w-full text-xs border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
            ></textarea>
          </div>

          <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
            <button
              type="button"
              @click="fecharModalEntrega"
              class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-lg transition"
            >
              Cancelar
            </button>
            <button
              type="submit"
              :disabled="salvandoItem"
              class="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-lg shadow-sm transition flex items-center gap-1.5"
            >
              <span v-if="salvandoItem" class="inline-block animate-spin w-3 h-3 border-2 border-white border-t-transparent rounded-full"></span>
              <span>Salvar Entrega</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ============================================================== -->
    <!-- MODAL: NOVO / EDITAR INDICADOR                                 -->
    <!-- ============================================================== -->
    <div
      v-if="modalIndicadorAberto"
      class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn"
    >
      <div class="bg-white rounded-2xl shadow-xl border border-slate-200 w-full max-w-lg overflow-hidden animate-scaleUp">
        <div class="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/70">
          <h3 class="text-sm font-black text-slate-900 flex items-center gap-2">
            <span>📈</span>
            <span>{{ indicadorEmEdicao?.id ? 'Editar Indicador Anual' : 'Novo Indicador Anual' }}</span>
          </h3>
          <button @click="fecharModalIndicador" class="text-slate-400 hover:text-slate-600 text-sm font-bold">✕</button>
        </div>

        <form @submit.prevent="salvarIndicador" class="p-6 space-y-4">
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Nome do Indicador *</label>
            <input
              v-model="formIndicador.nome"
              type="text"
              required
              minlength="3"
              placeholder="Ex: Taxa de Ocupação de Leitos Cirúrgicos"
              class="w-full text-xs border border-slate-300 rounded-lg px-3 py-2.5 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Descrição e Fórmula de Cálculo</label>
            <textarea
              v-model="formIndicador.descricao"
              rows="2"
              placeholder="Explique o método de apuração e fonte de dados..."
              class="w-full text-xs border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
            ></textarea>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-bold text-slate-700 mb-1">Periodicidade</label>
              <select
                v-model="formIndicador.periodicidade"
                class="w-full text-xs border border-slate-300 rounded-lg px-3 py-2 bg-white focus:ring-2 focus:ring-indigo-500 outline-none"
              >
                <option value="BIMESTRAL">Bimestral</option>
                <option value="MENSAL">Mensal</option>
                <option value="TRIMESTRAL">Trimestral</option>
                <option value="QUADRIMESTRAL">Quadrimestral</option>
                <option value="SEMESTRAL">Semestral</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-bold text-slate-700 mb-1">Unidade de Medida *</label>
              <input
                v-model="formIndicador.unidade_medida"
                type="text"
                required
                placeholder="Ex: % ou Dias ou Pacientes"
                class="w-full text-xs border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
              />
            </div>
          </div>

          <!-- Configuração da Meta -->
          <div class="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-3">
            <span class="block text-xs font-black text-slate-800">Parâmetros da Meta</span>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-[11px] font-bold text-slate-600 mb-1">Operador</label>
                <select
                  v-model="formIndicador.meta_operador"
                  class="w-full text-xs border border-slate-300 rounded-lg px-3 py-2 bg-white focus:ring-2 focus:ring-indigo-500 outline-none"
                >
                  <option value="MAIOR_IGUAL">Maior ou Igual (≥)</option>
                  <option value="MENOR_IGUAL">Menor ou Igual (≤)</option>
                  <option value="IGUAL">Igual (=)</option>
                  <option value="ENTRE">Faixa (Entre Mín e Máx)</option>
                </select>
              </div>

              <div>
                <label class="block text-[11px] font-bold text-slate-600 mb-1">
                  {{ formIndicador.meta_operador === 'ENTRE' ? 'Valor Mínimo *' : 'Valor da Meta *' }}
                </label>
                <input
                  v-model.number="formIndicador.meta_valor"
                  type="number"
                  step="any"
                  required
                  placeholder="Ex: 85.0"
                  class="w-full text-xs border border-slate-300 rounded-lg px-3 py-2 bg-white focus:ring-2 focus:ring-indigo-500 outline-none"
                />
              </div>
            </div>

            <div v-if="formIndicador.meta_operador === 'ENTRE'">
              <label class="block text-[11px] font-bold text-slate-600 mb-1">Valor Máximo da Faixa *</label>
              <input
                v-model.number="formIndicador.meta_valor_max"
                type="number"
                step="any"
                required
                placeholder="Ex: 95.0"
                class="w-full text-xs border border-slate-300 rounded-lg px-3 py-2 bg-white focus:ring-2 focus:ring-indigo-500 outline-none"
              />
            </div>
          </div>

          <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
            <button
              type="button"
              @click="fecharModalIndicador"
              class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-lg transition"
            >
              Cancelar
            </button>
            <button
              type="submit"
              :disabled="salvandoItem"
              class="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-lg shadow-sm transition flex items-center gap-1.5"
            >
              <span v-if="salvandoItem" class="inline-block animate-spin w-3 h-3 border-2 border-white border-t-transparent rounded-full"></span>
              <span>Salvar Indicador</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ============================================================== -->
    <!-- MODAL DE CONFIRMAÇÃO DE INATIVAÇÃO (SOFT DELETE)               -->
    <!-- ============================================================== -->
    <div
      v-if="modalInativarAberto"
      class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn"
    >
      <div class="bg-white rounded-2xl shadow-xl border border-slate-200 w-full max-w-md overflow-hidden p-6 space-y-4">
        <div class="w-12 h-12 rounded-full bg-red-100 text-red-600 flex items-center justify-center text-2xl mx-auto">
          ⚠️
        </div>
        <div class="text-center">
          <h3 class="text-base font-black text-slate-900">Confirmar Inativação</h3>
          <p class="text-xs text-slate-500 mt-1 leading-relaxed">
            Tem certeza de que deseja inativar {{ itemParaInativar?.tipo === 'entrega' ? 'a entrega' : 'o indicador' }}
            <span class="font-bold text-slate-800">"{{ itemParaInativar?.nome }}"</span>?
          </p>
          <p class="text-[11px] text-slate-400 mt-2 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
            O registro não será excluído fisicamente para preservar a integridade dos relatórios anteriores já concluídos (Soft Delete).
          </p>
        </div>

        <div class="flex items-center justify-center gap-3 pt-2">
          <button
            @click="modalInativarAberto = false"
            class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-lg transition"
          >
            Cancelar
          </button>
          <button
            @click="executarInativacao"
            :disabled="salvandoItem"
            class="px-5 py-2 bg-red-600 hover:bg-red-700 text-white text-xs font-bold rounded-lg shadow-sm transition flex items-center gap-1.5"
          >
            <span v-if="salvandoItem" class="inline-block animate-spin w-3 h-3 border-2 border-white border-t-transparent rounded-full"></span>
            <span>Sim, Inativar</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import {
  gestaoApi,
  type PlanejamentoUorgDetalhe,
  type EntregaPlanejadaItem,
  type IndicadorPlanejadoItem
} from '../services/gestaoApi';

const route = useRoute();

// Estados principais
const carregando = ref(true);
const salvandoStatus = ref(false);
const salvandoItem = ref(false);
const mensagemAlerta = ref<{ tipo: 'sucesso' | 'erro'; texto: string } | null>(null);

const usuario = ref<any>(null);
const estrutura = ref<any[]>([]);
const exercicio = ref<any>(null);
const uorgAtual = ref<any>(null);
const uorgSelecionadaId = ref<number | null>(null);

const planejamentoAberto = ref(false);
const entregas = ref<EntregaPlanejadaItem[]>([]);
const indicadores = ref<IndicadorPlanejadoItem[]>([]);

// Modais
const modalEntregaAberto = ref(false);
const entregaEmEdicao = ref<EntregaPlanejadaItem | null>(null);
const formEntrega = ref({
  titulo: '',
  descricao: ''
});

const modalIndicadorAberto = ref(false);
const indicadorEmEdicao = ref<IndicadorPlanejadoItem | null>(null);
const formIndicador = ref({
  nome: '',
  descricao: '',
  periodicidade: 'BIMESTRAL',
  unidade_medida: '%',
  meta_operador: 'MAIOR_IGUAL',
  meta_valor: 80,
  meta_valor_max: null as number | null
});

const modalInativarAberto = ref(false);
const itemParaInativar = ref<{ id: number; tipo: 'entrega' | 'indicador'; nome: string } | null>(null);

// Computeds de RBAC
const isAdmin = computed(() => usuario.value?.perfil === 'ADMINISTRADOR');
const isAdminOuGestor = computed(() =>
  ['ADMINISTRADOR', 'SUPERINTENDENTE', 'GERENTE'].includes(usuario.value?.perfil)
);
const podeModificar = computed(() => {
  if (isAdmin.value) return true;
  if (!planejamentoAberto.value) return false;
  if (['CHEFE_UORG', 'CHEFE'].includes(usuario.value?.perfil)) {
    return Number(usuario.value?.uorg_id) === Number(uorgSelecionadaId.value);
  }
  return false;
});

function formatarMeta(ind: IndicadorPlanejadoItem): string {
  const op = ind.meta_operador || 'MAIOR_IGUAL';
  if (op === 'MAIOR_IGUAL') return `≥ ${ind.meta_valor} ${ind.unidade_medida}`;
  if (op === 'MENOR_IGUAL') return `≤ ${ind.meta_valor} ${ind.unidade_medida}`;
  if (op === 'IGUAL') return `= ${ind.meta_valor} ${ind.unidade_medida}`;
  if (op === 'ENTRE') return `Entre ${ind.meta_valor} e ${ind.meta_valor_max ?? ''} ${ind.unidade_medida}`;
  return `${ind.meta_valor} ${ind.unidade_medida}`;
}

async function carregarPlanejamento() {
  if (!uorgSelecionadaId.value) return;
  carregando.value = true;
  mensagemAlerta.value = null;

  try {
    const dados: PlanejamentoUorgDetalhe = await gestaoApi.obterPlanejamentoUorg(
      uorgSelecionadaId.value,
      exercicio.value?.id
    );
    exercicio.value = dados.exercicio;
    uorgAtual.value = dados.uorg;
    planejamentoAberto.value = dados.planejamento_aberto;
    entregas.value = dados.entregas || [];
    indicadores.value = dados.indicadores || [];
  } catch (err: any) {
    mensagemAlerta.value = {
      tipo: 'erro',
      texto: err.response?.data?.detail || 'Erro ao carregar planejamento da UORG.'
    };
  } finally {
    carregando.value = false;
  }
}

// Abertura / Fechamento do Planejamento pelo Administrador
async function abrirJanelaPlanejamento() {
  if (!exercicio.value?.id) return;
  salvandoStatus.value = true;
  try {
    const res = await gestaoApi.abrirPlanejamentoExercicio(exercicio.value.id);
    exercicio.value = res;
    planejamentoAberto.value = true;
    mensagemAlerta.value = {
      tipo: 'sucesso',
      texto: 'Janela de planejamento anual reaberta com sucesso!'
    };
  } catch (err: any) {
    mensagemAlerta.value = {
      tipo: 'erro',
      texto: err.response?.data?.detail || 'Falha ao abrir janela de planejamento.'
    };
  } finally {
    salvandoStatus.value = false;
  }
}

async function fecharJanelaPlanejamento() {
  if (!exercicio.value?.id) return;
  salvandoStatus.value = true;
  try {
    const res = await gestaoApi.fecharPlanejamentoExercicio(exercicio.value.id);
    exercicio.value = res;
    planejamentoAberto.value = false;
    mensagemAlerta.value = {
      tipo: 'sucesso',
      texto: 'Janela de planejamento anual encerrada com sucesso!'
    };
  } catch (err: any) {
    mensagemAlerta.value = {
      tipo: 'erro',
      texto: err.response?.data?.detail || 'Falha ao fechar janela de planejamento.'
    };
  } finally {
    salvandoStatus.value = false;
  }
}

// Ações de Entregas
function abrirModalNovaEntrega() {
  entregaEmEdicao.value = null;
  formEntrega.value = { titulo: '', descricao: '' };
  modalEntregaAberto.value = true;
}

function abrirModalEditarEntrega(ent: EntregaPlanejadaItem) {
  entregaEmEdicao.value = ent;
  formEntrega.value = {
    titulo: ent.titulo,
    descricao: ent.descricao || ''
  };
  modalEntregaAberto.value = true;
}

function fecharModalEntrega() {
  modalEntregaAberto.value = false;
  entregaEmEdicao.value = null;
}

async function salvarEntrega() {
  if (!uorgSelecionadaId.value || !exercicio.value?.id) return;
  salvandoItem.value = true;

  try {
    if (entregaEmEdicao.value?.id) {
      await gestaoApi.editarEntregaPlanejada(entregaEmEdicao.value.id, {
        titulo: formEntrega.value.titulo,
        descricao: formEntrega.value.descricao
      });
      mensagemAlerta.value = { tipo: 'sucesso', texto: 'Entrega atualizada com sucesso!' };
    } else {
      await gestaoApi.criarEntregaPlanejada({
        uorg_id: uorgSelecionadaId.value,
        exercicio_id: exercicio.value.id,
        titulo: formEntrega.value.titulo,
        descricao: formEntrega.value.descricao,
        ordem: entregas.value.length + 1
      });
      mensagemAlerta.value = { tipo: 'sucesso', texto: 'Nova entrega cadastrada com sucesso!' };
    }
    fecharModalEntrega();
    await carregarPlanejamento();
  } catch (err: any) {
    mensagemAlerta.value = {
      tipo: 'erro',
      texto: err.response?.data?.detail || 'Erro ao salvar entrega planejada.'
    };
  } finally {
    salvandoItem.value = false;
  }
}

function confirmarInativarEntrega(ent: EntregaPlanejadaItem) {
  itemParaInativar.value = { id: ent.id, tipo: 'entrega', nome: ent.titulo };
  modalInativarAberto.value = true;
}

// Ações de Indicadores
function abrirModalNovoIndicador() {
  indicadorEmEdicao.value = null;
  formIndicador.value = {
    nome: '',
    descricao: '',
    periodicidade: 'BIMESTRAL',
    unidade_medida: '%',
    meta_operador: 'MAIOR_IGUAL',
    meta_valor: 80,
    meta_valor_max: null
  };
  modalIndicadorAberto.value = true;
}

function abrirModalEditarIndicador(ind: IndicadorPlanejadoItem) {
  indicadorEmEdicao.value = ind;
  formIndicador.value = {
    nome: ind.nome,
    descricao: ind.descricao || '',
    periodicidade: ind.periodicidade || 'BIMESTRAL',
    unidade_medida: ind.unidade_medida || '%',
    meta_operador: ind.meta_operador || 'MAIOR_IGUAL',
    meta_valor: ind.meta_valor,
    meta_valor_max: ind.meta_valor_max ?? null
  };
  modalIndicadorAberto.value = true;
}

function fecharModalIndicador() {
  modalIndicadorAberto.value = false;
  indicadorEmEdicao.value = null;
}

async function salvarIndicador() {
  if (!uorgSelecionadaId.value || !exercicio.value?.id) return;
  salvandoItem.value = true;

  try {
    if (indicadorEmEdicao.value?.id) {
      await gestaoApi.editarIndicadorPlanejado(indicadorEmEdicao.value.id, {
        nome: formIndicador.value.nome,
        descricao: formIndicador.value.descricao,
        periodicidade: formIndicador.value.periodicidade,
        unidade_medida: formIndicador.value.unidade_medida,
        meta_operador: formIndicador.value.meta_operador,
        meta_valor: formIndicador.value.meta_valor,
        meta_valor_max: formIndicador.value.meta_valor_max
      });
      mensagemAlerta.value = { tipo: 'sucesso', texto: 'Indicador atualizado com sucesso!' };
    } else {
      await gestaoApi.criarIndicadorPlanejado({
        uorg_id: uorgSelecionadaId.value,
        exercicio_id: exercicio.value.id,
        nome: formIndicador.value.nome,
        descricao: formIndicador.value.descricao,
        periodicidade: formIndicador.value.periodicidade,
        unidade_medida: formIndicador.value.unidade_medida,
        meta_operador: formIndicador.value.meta_operador,
        meta_valor: formIndicador.value.meta_valor,
        meta_valor_max: formIndicador.value.meta_valor_max,
        ordem: indicadores.value.length + 1
      });
      mensagemAlerta.value = { tipo: 'sucesso', texto: 'Novo indicador cadastrado com sucesso!' };
    }
    fecharModalIndicador();
    await carregarPlanejamento();
  } catch (err: any) {
    mensagemAlerta.value = {
      tipo: 'erro',
      texto: err.response?.data?.detail || 'Erro ao salvar indicador anual.'
    };
  } finally {
    salvandoItem.value = false;
  }
}

function confirmarInativarIndicador(ind: IndicadorPlanejadoItem) {
  itemParaInativar.value = { id: ind.id, tipo: 'indicador', nome: ind.nome };
  modalInativarAberto.value = true;
}

async function executarInativacao() {
  if (!itemParaInativar.value) return;
  salvandoItem.value = true;

  try {
    if (itemParaInativar.value.tipo === 'entrega') {
      await gestaoApi.inativarEntregaPlanejada(itemParaInativar.value.id);
      mensagemAlerta.value = { tipo: 'sucesso', texto: 'Entrega inativada com sucesso.' };
    } else {
      await gestaoApi.inativarIndicadorPlanejado(itemParaInativar.value.id);
      mensagemAlerta.value = { tipo: 'sucesso', texto: 'Indicador inativado com sucesso.' };
    }
    modalInativarAberto.value = false;
    itemParaInativar.value = null;
    await carregarPlanejamento();
  } catch (err: any) {
    mensagemAlerta.value = {
      tipo: 'erro',
      texto: err.response?.data?.detail || 'Erro ao inativar registro.'
    };
  } finally {
    salvandoItem.value = false;
  }
}

onMounted(async () => {
  try {
    const [me, est, ex] = await Promise.all([
      gestaoApi.obterUsuarioLogado(),
      gestaoApi.obterEstrutura(),
      gestaoApi.obterExercicioAtivo()
    ]);
    usuario.value = me;
    estrutura.value = est;
    exercicio.value = ex;

    // Determinar UORG inicial
    const uorgQuery = route.query.uorg ? Number(route.query.uorg) : null;
    if (uorgQuery) {
      uorgSelecionadaId.value = uorgQuery;
    } else if (me.uorg_id) {
      uorgSelecionadaId.value = me.uorg_id;
    } else if (est.length > 0 && est[0].uorgs.length > 0) {
      uorgSelecionadaId.value = est[0].uorgs[0].id;
    }

    await carregarPlanejamento();
  } catch (err: any) {
    mensagemAlerta.value = {
      tipo: 'erro',
      texto: 'Falha ao inicializar dados do planejamento.'
    };
    carregando.value = false;
  }
});
</script>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes scaleUp {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.animate-fadeIn {
  animation: fadeIn 0.2s ease-out forwards;
}

.animate-scaleUp {
  animation: scaleUp 0.2s ease-out forwards;
}
</style>
