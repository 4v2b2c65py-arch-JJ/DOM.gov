/**
 * Vue Router Configuration
 */

import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: 'DOM.gov - GobernanzaRD Platform' },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: 'Login - DOM.gov' },
  },
  {
    path: '/verify',
    name: 'VerifyMagicLink',
    component: () => import('@/views/VerifyView.vue'),
    meta: { title: 'Verify - DOM.gov' },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { title: 'Dashboard - DOM.gov', requiresAuth: true },
  },
  {
    path: '/merits',
    name: 'Merits',
    component: () => import('@/views/MeritsView.vue'),
    meta: { title: 'Merits & Selecting Front - DOM.gov', requiresAuth: true, minIdentityLevel: 2 },
  },
  {
    path: '/selecting-front',
    name: 'SelectingFront',
    component: () => import('@/views/SelectingFrontView.vue'),
    meta: { title: 'Selecting Front - DOM.gov', requiresAuth: true, minIdentityLevel: 2 },
  },
  {
    path: '/quests',
    name: 'Quests',
    component: () => import('@/views/QuestsView.vue'),
    meta: { title: 'Quests - DOM.gov', requiresAuth: true, minIdentityLevel: 2 },
  },
  {
    path: '/veeduria',
    name: 'Veeduria',
    component: () => import('@/views/VeeduriaView.vue'),
    meta: { title: 'Veeduría Ciudadana - DOM.gov', requiresAuth: true, minIdentityLevel: 2 },
  },
  {
    path: '/governance',
    name: 'Governance',
    component: () => import('@/views/GovernanceView.vue'),
    meta: { title: 'Governance - DOM.gov', requiresAuth: true, minIdentityLevel: 3 },
  },
  {
    path: '/airport',
    name: 'Airport',
    component: () => import('@/views/AirportView.vue'),
    meta: { title: 'Airport Easy Pass - DOM.gov', requiresAuth: true, minIdentityLevel: 1 },
  },
  {
    path: '/wallet',
    name: 'Wallet',
    component: () => import('@/views/WalletView.vue'),
    meta: { title: 'Digital Wallet - DOM.gov', requiresAuth: true, minIdentityLevel: 2 },
  },
  {
    path: '/identity',
    name: 'Identity',
    component: () => import('@/views/IdentityView.vue'),
    meta: { title: 'Identity Level - DOM.gov', requiresAuth: true },
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: () => import('@/views/NotificationsView.vue'),
    meta: { title: 'Notifications - DOM.gov', requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/SettingsView.vue'),
    meta: { title: 'Settings - DOM.gov', requiresAuth: true },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { title: '404 - DOM.gov' },
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, _from, savedPosition) {
    if (savedPosition) return savedPosition;
    if (to.hash) return { el: to.hash, behavior: 'smooth' };
    return { top: 0 };
  },
});

router.beforeEach((to, _from, next) => {
  document.title = to.meta.title as string || 'DOM.gov';
  next();
});

export default router;