<template>
  <div class="space-y-6">
    <!-- Banner de Boas-Vindas Executivo -->
    <div class="bg-gradient-to-r from-blue-900 via-indigo-900 to-blue-950 text-white p-6 sm:p-8 rounded-2xl shadow-md relative overflow-hidden">
      <div class="relative z-10 max-w-3xl space-y-3">
        <div class="inline-flex items-center gap-2 px-3 py-1 bg-white/10 backdrop-blur-md rounded-full text-xs font-semibold tracking-wide text-blue-200 border border-white/20">
          <span>Exercício 2026 em Andamento</span>
          <span>•</span>
          <span>HC-UFPE / EBSERH</span>
        </div>
        <h1 class="text-3xl sm:text-4xl font-black tracking-tight leading-tight">
          Portal de Relatórios de Gestão
        </h1>
        <p class="text-sm sm:text-base text-blue-100 font-normal leading-relaxed">
          Plataforma corporativa de governança institucional para acompanhamento bimestral das metas, entregas planejadas e indicadores estratégicos das unidades organizacionais do Hospital das Clínicas da UFPE.
        </p>
      </div>
      <div class="absolute -right-10 -bottom-10 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>
    </div>

    <!-- Indicadores Resumidos de Governança -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
        <div>
          <span class="text-xs font-bold text-gray-500 uppercase tracking-wider">UORGs</span>
          <p class="text-3xl font-black text-gray-900 mt-1">23</p>
          <span class="text-[11px] text-gray-400 mt-0.5 block">Todas as unidades ativas</span>
        </div>
        <div class="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
          <BuildingOffice2Icon class="w-6 h-6" />
        </div>
      </div>

      <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
        <div>
          <span class="text-xs font-bold text-gray-500 uppercase tracking-wider">Gerências</span>
          <p class="text-3xl font-black text-indigo-600 mt-1">4</p>
          <span class="text-[11px] text-gray-400 mt-0.5 block">GAD, GEPE, GAT, SUP</span>
        </div>
        <div class="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold">
          <Squares2X2Icon class="w-6 h-6" />
        </div>
      </div>

      <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
        <div>
          <span class="text-xs font-bold text-gray-500 uppercase tracking-wider">Entregas</span>
          <p class="text-3xl font-black text-emerald-600 mt-1">84</p>
          <span class="text-[11px] text-gray-400 mt-0.5 block">Plano Operacional 2026</span>
        </div>
        <div class="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
          <CheckCircleIcon class="w-6 h-6" />
        </div>
      </div>

      <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
        <div>
          <span class="text-xs font-bold text-gray-500 uppercase tracking-wider">Bimestre Vigente</span>
          <p class="text-2xl font-black text-blue-700 mt-1">1º Bimestre</p>
          <span class="text-[11px] text-emerald-600 font-bold mt-0.5 block">ABERTO PARA ENVIO</span>
        </div>
        <div class="w-12 h-12 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center font-bold">
          <CalendarDaysIcon class="w-6 h-6" />
        </div>
      </div>
    </div>

    <!-- Módulos Principais do Sistema -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Card Matriz de Acompanhamento -->
      <router-link 
        to="/matriz" 
        class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:border-blue-300 hover:shadow-md transition-all duration-200 group flex flex-col justify-between"
      >
        <div class="space-y-3">
          <div class="w-12 h-12 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center group-hover:scale-105 transition-transform">
            <TableCellsIcon class="w-6 h-6" />
          </div>
          <h2 class="text-xl font-bold text-gray-900 group-hover:text-blue-700 transition-colors flex items-center gap-2">
            Matriz de Acompanhamento Anual
            <ArrowRightIcon class="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
          </h2>
          <p class="text-sm text-gray-600 leading-relaxed">
            Visão gerencial consolidada em grade matricial de todas as 23 UORGs pelos 6 bimestres. Visualize status por cores, filtre por Gerência e exporte a planilha em Excel.
          </p>
        </div>
        <div class="mt-4 pt-4 border-t border-gray-100 flex items-center text-xs font-semibold text-blue-600">
          Acessar Matriz Executiva &rarr;
        </div>
      </router-link>

      <!-- Card Preenchimento Bimestral -->
      <router-link 
        to="/preenchimento"
        class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:border-emerald-300 hover:shadow-md transition-all duration-200 group flex flex-col justify-between"
      >
        <div class="space-y-3">
          <div class="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center group-hover:scale-105 transition-transform">
            <PencilSquareIcon class="w-6 h-6" />
          </div>
          <h2 class="text-xl font-bold text-gray-900 group-hover:text-emerald-700 transition-colors flex items-center gap-2">
            Preenchimento Bimestral
            <ArrowRightIcon class="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
          </h2>
          <p class="text-sm text-gray-600 leading-relaxed">
            Formulário operacional com salvamento automático de rascunho (autosave), checklist de entregas concluídas, apuração de indicadores com metas e justificativas.
          </p>
        </div>
        <div class="mt-4 pt-4 border-t border-gray-100 flex items-center text-xs font-semibold text-emerald-600">
          Preencher Relatório da Unidade &rarr;
        </div>
      </router-link>

      <!-- Card Visão Consolidada -->
      <router-link 
        to="/consolidado"
        class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:border-indigo-300 hover:shadow-md transition-all duration-200 group flex flex-col justify-between"
      >
        <div class="space-y-3">
          <div class="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-700 flex items-center justify-center group-hover:scale-105 transition-transform">
            <DocumentChartBarIcon class="w-6 h-6" />
          </div>
          <h2 class="text-xl font-bold text-gray-900 group-hover:text-indigo-700 transition-colors flex items-center gap-2">
            Visão Consolidada e Feedback
            <ArrowRightIcon class="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
          </h2>
          <p class="text-sm text-gray-600 leading-relaxed">
            Navegue sequencialmente entre os relatórios homologados das UORGs, consulte histórico de versões, visualize alertas e emita feedbacks institucionais.
          </p>
        </div>
        <div class="mt-4 pt-4 border-t border-gray-100 flex items-center text-xs font-semibold text-indigo-600">
          Consultar Relatórios &rarr;
        </div>
      </router-link>

      <!-- Card Gestão de Prazos -->
      <router-link 
        to="/gestao-exercicio"
        class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:border-amber-300 hover:shadow-md transition-all duration-200 group flex flex-col justify-between"
      >
        <div class="space-y-3">
          <div class="w-12 h-12 rounded-xl bg-amber-50 text-amber-700 flex items-center justify-center group-hover:scale-105 transition-transform">
            <CalendarDaysIcon class="w-6 h-6" />
          </div>
          <h2 class="text-xl font-bold text-gray-900 group-hover:text-amber-700 transition-colors flex items-center gap-2">
            Gestão do Exercício e Prazos
            <ArrowRightIcon class="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
          </h2>
          <p class="text-sm text-gray-600 leading-relaxed">
            Monitore o cronograma anual de fechamentos regulares e utilize o módulo de concessão de prazo excepcional com justificativa obrigatória.
          </p>
        </div>
        <div class="mt-4 pt-4 border-t border-gray-100 flex items-center text-xs font-semibold text-amber-600">
          Gerenciar Calendário &rarr;
        </div>
      </router-link>
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
import { 
  BuildingOffice2Icon, 
  Squares2X2Icon, 
  CheckCircleIcon, 
  CalendarDaysIcon,
  TableCellsIcon,
  PencilSquareIcon,
  DocumentChartBarIcon,
  ArrowRightIcon 
} from '@heroicons/vue/24/outline';
</script>
