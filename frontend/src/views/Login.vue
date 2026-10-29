<template>
  <div class="w-full max-w-md">
    <Card>
      <template #header>
        <h1 class="text-xl font-semibold text-center">Login</h1>
      </template>
      <form @submit.prevent="handleLogin">
        <div class="mb-4">
          <label class="block text-sm font-bold mb-2" for="username">
            Usuário
          </label>
          <input v-model="username" class="shadow-inner appearance-none border rounded w-full py-2 px-3 leading-tight focus:outline-none focus:shadow-outline" id="username" type="text" placeholder="E.g., EBSERHNET\\user">
        </div>
        <div class="mb-6">
          <label class="block text-sm font-bold mb-2" for="password">
            Senha
          </label>
          <div class="relative">
            <input v-model="password" class="shadow-inner appearance-none border rounded w-full py-2 px-3 pr-10 leading-tight focus:outline-none focus:shadow-outline" id="password" :type="passwordFieldType" placeholder="******************">
            <button type="button" @click="togglePasswordVisibility" class="absolute inset-y-0 right-0 px-3 flex items-center text-gray-500">
              <component :is="passwordFieldType === 'password' ? EyeIcon : EyeSlashIcon" class="h-5 w-5" />
            </button>
          </div>
        </div>
        <div class="mb-6">
          <label class="flex items-center">
            <input type="checkbox" v-model="rememberMe" class="form-checkbox h-5 w-5 text-orange-600">
            <span class="ml-2 text-sm">Lembrar de mim</span>
          </label>
        </div>
        <div class="flex items-center justify-center space-x-4">
          <Button type="button" variant="secondary" @click="clearForm" class="w-1/2 bg-gray-500 hover:bg-gray-600">
            <template #icon>
              <XCircleIcon class="h-5 w-5" />
            </template>
            Limpar
          </Button>
          <Button type="submit" variant="primary" :disabled="loading" class="w-1/2">
            <template #icon>
              <ArrowRightOnRectangleIcon class="h-5 w-5" />
            </template>
            Entrar
          </Button>
        </div>
      </form>
    </Card>
    <div v-if="error" class="mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
      <strong class="font-bold">Erro: </strong>
      <span class="block sm:inline">{{ error }}</span>
    </div>

    <!-- Atalhos de Login Rápido (Ambiente de Validação/Homologação) -->
    <div class="mt-4 bg-white/95 border border-gray-200 rounded-xl p-3.5 shadow-sm">
      <p class="text-[11px] font-bold text-gray-500 uppercase tracking-wider mb-2 text-center">
        Acesso Rápido por Perfil (1 clique — Senha: 123)
      </p>
      <div class="flex flex-wrap justify-center gap-1.5">
        <button
          v-for="conta in contasTeste"
          :key="conta.user"
          type="button"
          @click="loginRapido(conta.user, conta.pass)"
          class="px-2.5 py-1 text-[11px] font-bold rounded-lg border transition cursor-pointer"
          :class="conta.classe"
        >
          {{ conta.label }}
        </button>
      </div>
    </div>

    <!-- Rodapé de Versão -->
    <div class="mt-6 text-center text-xs text-gray-400 space-y-1">
      <p class="font-semibold text-gray-300">{{ HOSPITAL_NAME }}</p>
      <p class="text-gray-400">{{ DEPARTMENT_NAME }} | Versão {{ APP_VERSION }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import { ArrowRightOnRectangleIcon, EyeIcon, EyeSlashIcon, XCircleIcon } from '@heroicons/vue/24/outline';
import { APP_VERSION, HOSPITAL_NAME, DEPARTMENT_NAME } from '../config/version';

const username = ref('');
const password = ref('');
const rememberMe = ref(false);
const error = ref('');
const loading = ref(false);
const passwordVisible = ref(false);

const router = useRouter();
const authStore = useAuthStore();

const passwordFieldType = computed(() => passwordVisible.value ? 'text' : 'password');

const togglePasswordVisibility = () => {
  passwordVisible.value = !passwordVisible.value;
};

const clearForm = () => {
  username.value = '';
  password.value = '';
  rememberMe.value = false;
  error.value = '';
};

const handleLogin = async () => {
  loading.value = true;
  error.value = '';
  try {
    await authStore.login(username.value, password.value, rememberMe.value);
    await router.push('/');
  } catch (e: any) {
    error.value = e.response?.data?.detail || e.message || 'Credenciais inválidas';
  } finally {
    loading.value = false;
  }
};

const contasTeste = [
  { label: '👑 Admin', user: 'admin', pass: 'admin', classe: 'bg-slate-800 text-white border-slate-800 hover:bg-slate-700' },
  { label: '🏛️ Superintendente', user: 'superintendente', pass: '123', classe: 'bg-purple-50 text-purple-800 border-purple-200 hover:bg-purple-100' },
  { label: '📊 Gerente GAD', user: 'gerente.gad', pass: '123', classe: 'bg-blue-50 text-blue-800 border-blue-200 hover:bg-blue-100' },
  { label: '🏥 Gerente GAS', user: 'gerente.gas', pass: '123', classe: 'bg-blue-50 text-blue-800 border-blue-200 hover:bg-blue-100' },
  { label: '🎓 Gerente GEP', user: 'gerente.gep', pass: '123', classe: 'bg-blue-50 text-blue-800 border-blue-200 hover:bg-blue-100' },
  { label: '📌 Chefe STGQ', user: 'chefe.stgq', pass: '123', classe: 'bg-emerald-50 text-emerald-800 border-emerald-200 hover:bg-emerald-100' },
  { label: '💻 Chefe SETISD', user: 'chefe.setisd', pass: '123', classe: 'bg-emerald-50 text-emerald-800 border-emerald-200 hover:bg-emerald-100' },
  { label: '💰 Chefe SGOF', user: 'chefe.sgof', pass: '123', classe: 'bg-emerald-50 text-emerald-800 border-emerald-200 hover:bg-emerald-100' },
  { label: '⚕️ Chefe DMED', user: 'chefe.dmed', pass: '123', classe: 'bg-emerald-50 text-emerald-800 border-emerald-200 hover:bg-emerald-100' },
  { label: '🩺 Chefe DENF', user: 'chefe.denf', pass: '123', classe: 'bg-emerald-50 text-emerald-800 border-emerald-200 hover:bg-emerald-100' }
];

const loginRapido = async (u: string, p: string) => {
  username.value = u;
  password.value = p;
  await handleLogin();
};
</script>
