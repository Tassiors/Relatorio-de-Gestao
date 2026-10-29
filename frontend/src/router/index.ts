import { createRouter, createWebHistory, NavigationGuardNext } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import Configuracoes from '../views/Configuracoes.vue';
import Exemplos from '../views/Exemplos.vue';
import MatrizAcompanhamento from '../views/MatrizAcompanhamento.vue';
import PreenchimentoBimestral from '../views/PreenchimentoBimestral.vue';
import PlanejamentoAnual from '../views/PlanejamentoAnual.vue';
import ConsolidadoGestao from '../views/ConsolidadoGestao.vue';
import GestaoExercicio from '../views/GestaoExercicio.vue';

const routes = [
  {
    path: '/',
    name: 'Início',
    component: Home,
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { layout: 'LoginLayout' },
  },
  {
    path: '/matriz',
    name: 'Matriz de Acompanhamento',
    component: MatrizAcompanhamento,
    meta: { requiresAuth: true },
  },
  {
    path: '/planejamento',
    name: 'Planejamento Anual',
    component: PlanejamentoAnual,
    meta: { requiresAuth: true },
  },
  {
    path: '/preenchimento',
    name: 'Preenchimento Bimestral',
    component: PreenchimentoBimestral,
    meta: { requiresAuth: true },
  },
  {
    path: '/consolidado',
    name: 'Visão Consolidada',
    component: ConsolidadoGestao,
    meta: { requiresAuth: true },
  },
  {
    path: '/gestao-exercicio',
    name: 'Gestão de Exercício e Prazos',
    component: GestaoExercicio,
    meta: { requiresAuth: true },
  },
  {
    path: '/componentes',
    name: 'Componentes',
    component: Exemplos,
  },
  {
    path: '/configuracoes',
    name: 'Configurações',
    component: Configuracoes,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  linkActiveClass: 'bg-paper-active-link',
  linkExactActiveClass: 'bg-paper-active-link',
});

router.beforeEach((to, _from, next: NavigationGuardNext) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login' });
    return;
  }

  const perfil = (authStore.gestaoProfile?.perfil || '').toUpperCase();
  const tipoUorg = (authStore.gestaoProfile?.tipo_uorg || 'SETOR').toUpperCase();

  if (perfil) {
    // Chefe de Setor não acessa Matriz de Acompanhamento
    if (to.path === '/matriz' && ['CHEFE', 'CHEFE_UORG'].includes(perfil) && tipoUorg !== 'DIVISAO') {
      next({ path: '/' });
      return;
    }
    // Gerente e Superintendente não acessam Planejamento Anual nem Preenchimento Bimestral
    if ((to.path === '/planejamento' || to.path === '/preenchimento') && ['GERENTE', 'SUPERINTENDENTE'].includes(perfil)) {
      next({ path: '/consolidado', query: to.query });
      return;
    }
    // Apenas Administrador acessa Gestão de Exercício e Configurações
    if ((to.path === '/gestao-exercicio' || to.path === '/configuracoes') && perfil !== 'ADMINISTRADOR') {
      next({ path: '/' });
      return;
    }
  }

  next();
});

export default router;
