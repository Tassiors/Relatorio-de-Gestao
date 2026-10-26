<template>
  <div class="relative h-screen overflow-hidden md:flex">
    <!-- Mobile Menu Header -->
    <div class="bg-paper-sidebar text-gray-100 flex justify-between md:hidden shrink-0">
      <router-link to="/" class="block p-4 text-white font-bold">{{ SYSTEM_TITLE }}</router-link>
      <button @click="sidebarOpen = !sidebarOpen" class="p-4 focus:outline-none focus:bg-paper-active-link">
        <Bars3Icon class="h-6 w-6" />
      </button>
    </div>

    <!-- Sidebar (Expansivel / Recolhivel) -->
    <aside 
      :class="[
        sidebarOpen ? 'translate-x-0' : '-translate-x-full',
        isCollapsed ? 'md:w-20' : 'md:w-64'
      ]" 
      class="bg-paper-sidebar text-gray-100 pt-7 pb-2 px-2 absolute inset-y-0 left-0 transform md:relative md:translate-x-0 transition-all duration-300 ease-in-out z-20 h-full shrink-0 flex flex-col justify-between"
    >
      <div>
        <!-- Clique em Nome do Sistema recolhe/expande a barra lateral -->
        <div 
          @click="toggleSidebar" 
          title="Clique para recolher / expandir o menu"
          class="cursor-pointer text-white flex items-center space-x-3 px-3 mb-6 hover:opacity-90 transition duration-150 group"
        >
          <CubeTransparentIcon class="h-8 w-8 shrink-0 group-hover:scale-105 transition-transform" />
          <span v-if="!isCollapsed" class="text-xl font-extrabold leading-snug break-words select-none">
            {{ SYSTEM_TITLE }}
          </span>
        </div>

        <div class="px-3 my-4">
          <div class="border-t border-white border-opacity-20"></div>
        </div>

        <!-- Links de Navegacao -->
        <nav class="space-y-1.5">
          <router-link 
            to="/" 
            :title="isCollapsed ? 'Inicio' : ''"
            :class="[isCollapsed ? 'justify-center px-2' : 'px-4']"
            class="flex items-center space-x-3 py-2.5 rounded transition duration-200 hover:bg-paper-active-link hover:text-white"
          >
            <HomeIcon class="h-5 w-5 shrink-0"/>
            <span v-if="!isCollapsed" class="truncate text-sm font-medium">Inicio</span>
          </router-link>

          <router-link 
            to="/matriz" 
            :title="isCollapsed ? 'Matriz de Acompanhamento' : ''"
            :class="[isCollapsed ? 'justify-center px-2' : 'px-4']"
            class="flex items-center space-x-3 py-2.5 rounded transition duration-200 hover:bg-paper-active-link hover:text-white"
          >
            <TableCellsIcon class="h-5 w-5 shrink-0" />
            <span v-if="!isCollapsed" class="truncate text-sm font-medium">Matriz de Acompanhamento</span>
          </router-link>

          <router-link 
            to="/preenchimento"
            :title="isCollapsed ? 'Preenchimento Bimestral' : ''"
            :class="[isCollapsed ? 'justify-center px-2' : 'px-4']"
            class="flex items-center space-x-3 py-2.5 rounded transition duration-200 hover:bg-paper-active-link hover:text-white"
          >
            <PencilSquareIcon class="h-5 w-5 shrink-0" />
            <span v-if="!isCollapsed" class="truncate text-sm font-medium">Preenchimento Bimestral</span>
          </router-link>

          <router-link 
            to="/consolidado"
            :title="isCollapsed ? 'Visao Consolidada' : ''"
            :class="[isCollapsed ? 'justify-center px-2' : 'px-4']"
            class="flex items-center space-x-3 py-2.5 rounded transition duration-200 hover:bg-paper-active-link hover:text-white"
          >
            <DocumentChartBarIcon class="h-5 w-5 shrink-0" />
            <span v-if="!isCollapsed" class="truncate text-sm font-medium">Visao Consolidada</span>
          </router-link>

          <router-link 
            v-if="authStore.isAuthenticated" 
            to="/gestao-exercicio" 
            :title="isCollapsed ? 'Gestao de Exercicio' : ''"
            :class="[isCollapsed ? 'justify-center px-2' : 'px-4']"
            class="flex items-center space-x-3 py-2.5 rounded transition duration-200 hover:bg-paper-active-link hover:text-white"
          >
            <CalendarDaysIcon class="h-5 w-5 shrink-0" />
            <span v-if="!isCollapsed" class="truncate text-sm font-medium">Gestao de Exercicio</span>
          </router-link>
          
          <router-link 
            v-if="authStore.isAuthenticated" 
            to="/configuracoes" 
            :title="isCollapsed ? 'Configuracoes' : ''"
            :class="[isCollapsed ? 'justify-center px-2' : 'px-4']"
            class="flex items-center space-x-3 py-2.5 rounded transition duration-200 hover:bg-paper-active-link hover:text-white"
          >
            <Cog6ToothIcon class="h-5 w-5 shrink-0"/>
            <span v-if="!isCollapsed" class="truncate text-sm font-medium">Configuracoes</span>
          </router-link>
        </nav>
      </div>

      <!-- Rodape de Versao da Sidebar -->
      <div v-if="!isCollapsed" class="px-4 pt-3 pb-1 border-t border-white/10 text-xs text-gray-400 mt-auto truncate transition-opacity duration-200">
        <p class="font-semibold text-gray-200 truncate">{{ APP_NAME }}</p>
        <p class="text-[11px] text-gray-400 truncate">Versao {{ APP_VERSION }} | HC-UFPE</p>
      </div>
      <div v-else class="px-2 pt-3 pb-1 border-t border-white/10 text-[10px] text-center text-gray-400 mt-auto">
        v{{ APP_VERSION }}
      </div>
    </aside>

    <!-- Content -->
    <div class="flex-1 flex flex-col bg-paper-bg overflow-y-auto h-full">
      <header class="flex justify-between items-center p-6 bg-white/80 backdrop-blur-md border-b border-gray-300 sticky top-0 z-10">
        <div>
          <h1 class="text-2xl font-semibold text-paper-text">{{ $route.name }}</h1>
        </div>
        <div class="flex items-center gap-4">
          <!-- Central de Notificacoes -->
          <div v-if="authStore.isAuthenticated" class="relative">
            <button 
              @click="toggleNotificacoes" 
              class="relative p-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100 transition focus:outline-none"
              title="Notificacoes do Sistema"
            >
              <BellIcon class="h-6 w-6" />
              <span 
                v-if="naoLidasCount > 0" 
                class="absolute top-1 right-1 flex h-4 w-4 items-center justify-center rounded-full bg-rose-600 text-[10px] font-bold text-white ring-2 ring-white"
              >
                {{ naoLidasCount }}
              </span>
            </button>

            <!-- Dropdown de Notificacoes -->
            <div 
              v-if="dropdownNotificacoesAberto" 
              class="absolute right-0 mt-2 w-80 sm:w-96 bg-white rounded-xl shadow-xl border border-gray-200 py-2 z-50 text-gray-800"
            >
              <div class="px-4 py-2 border-b border-gray-100 flex items-center justify-between">
                <span class="font-bold text-sm text-gray-900">Notificacoes do Sistema</span>
                <span class="text-xs text-gray-400 font-medium">{{ notificacoes.length }} registros</span>
              </div>

              <div class="max-h-72 overflow-y-auto divide-y divide-gray-100">
                <div v-if="notificacoes.length === 0" class="p-4 text-center text-xs text-gray-500">
                  Nenhuma notificacao recebida no momento.
                </div>
                <div 
                  v-for="notif in notificacoes" 
                  :key="notif.id" 
                  class="p-3 hover:bg-gray-50 flex items-center justify-between gap-2"
                >
                  <div class="space-y-1">
                    <p class="text-xs font-bold text-gray-900">{{ notif.titulo }}</p>
                    <p class="text-xs text-gray-600 leading-snug">{{ notif.mensagem }}</p>
                    <span class="text-[10px] text-gray-400 block">{{ formatarDataNotif(notif.data_criacao) }}</span>
                  </div>
                  <button 
                    v-if="!notif.lida" 
                    @click="marcarComoLida(notif.id)" 
                    class="px-2 py-1 text-xs bg-blue-50 text-blue-700 rounded font-bold hover:bg-blue-100"
                  >
                    Lida
                  </button>
                </div>
              </div>
            </div>
          </div>

          <router-link v-if="!authStore.isAuthenticated" to="/login">
            <Button variant="primary">
              <template #icon>
                <ArrowRightOnRectangleIcon class="h-5 w-5" />
              </template>
              Login
            </Button>
          </router-link>
          <ProfileDropdown v-else />
        </div>
      </header>
      <main class="flex-1">
        <div class="container py-4 md:py-6">
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import {
  HomeIcon,
  TableCellsIcon,
  PencilSquareIcon,
  DocumentChartBarIcon,
  CalendarDaysIcon,
  Cog6ToothIcon,
  CubeTransparentIcon,
  Bars3Icon,
  BellIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/vue/24/outline';
import ProfileDropdown from '../components/ProfileDropdown.vue';
import Button from '../components/Button.vue';
import { useAuthStore } from '../stores/auth';
import { gestaoApi } from '../services/gestaoApi';
import { APP_VERSION, APP_NAME, SYSTEM_TITLE } from '../config/version';

const sidebarOpen = ref(false);
const isCollapsed = ref(false);
const dropdownNotificacoesAberto = ref(false);
const notificacoes = ref<any[]>([]);

const route = useRoute();
const authStore = useAuthStore();

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
};

const toggleNotificacoes = () => {
  dropdownNotificacoesAberto.value = !dropdownNotificacoesAberto.value;
};

const naoLidasCount = computed(() => {
  return notificacoes.value.filter(n => !n.lida).length;
});

const carregarNotificacoes = async () => {
  if (!authStore.isAuthenticated) return;
  try {
    const data = await gestaoApi.listarNotificacoes();
    notificacoes.value = data || [];
  } catch {
    // Ignora
  }
};

const marcarComoLida = async (id: number) => {
  try {
    await gestaoApi.marcarNotificacaoLida(id);
    const n = notificacoes.value.find(item => item.id === id);
    if (n) n.lida = true;
  } catch (err) {
    console.error('Erro ao marcar lida:', err);
  }
};

const formatarDataNotif = (dtStr?: string) => {
  if (!dtStr) return '';
  try {
    const d = new Date(dtStr);
    return d.toLocaleString('pt-BR');
  } catch {
    return dtStr;
  }
};

watch(() => route.path, () => {
  sidebarOpen.value = false;
  dropdownNotificacoesAberto.value = false;
});

onMounted(() => {
  carregarNotificacoes();
});
</script>
