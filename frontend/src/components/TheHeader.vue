/**
 * Header Component
 */

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useMeritsStore } from '@/stores/merits';
import { useAirportStore } from '@/stores/airport';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const meritsStore = useMeritsStore();
const airportStore = useAirportStore();

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: '🏠', auth: true },
  { path: '/merits', label: 'Méritos', icon: '🏆', auth: true, minLevel: 2 },
  { path: '/selecting-front', label: 'Selecting Front', icon: '📦', auth: true, minLevel: 2 },
  { path: '/quests', label: 'Quests', icon: '🚶', auth: true, minLevel: 2 },
  { path: '/veeduria', label: 'Veeduría', icon: '📋', auth: true, minLevel: 2 },
  { path: '/governance', label: 'Gobernanza', icon: '⚖️', auth: true, minLevel: 3 },
  { path: '/airport', label: 'Easy Pass', icon: '✈️', auth: true, minLevel: 1 },
  { path: '/wallet', label: 'Billetera', icon: '💳', auth: true, minLevel: 2 },
];

const filteredNavItems = computed(() => {
  return navItems.filter(item => {
    if (item.auth && !authStore.isAuthenticated) return false;
    if (item.minLevel && authStore.identityLevel < item.minLevel) return false;
    return true;
  });
});

const identityLabels = [
  'Anónimo', 'Email Verificado', 'Méritos Vinculados',
  'Biométrico', 'Confiable', 'Autorizado/Soeberano'
];

const identityColors = [
  'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
  'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
  'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
  'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300',
  'bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300',
  'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
];

async function handleLogout() {
  await authStore.logout();
  router.push('/');
}
</script>

<template>
  <header class="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
    <nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" aria-label="Main navigation">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <div class="flex items-center">
          <router-link to="/" class="flex items-center space-x-2" aria-label="DOM.gov Home">
            <span class="text-2xl">🇩🇴</span>
            <span class="text-xl font-bold text-gray-900 dark:text-white">DOM.gov</span>
            <span class="text-xs bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300 px-2 py-0.5 rounded-full">
              Society 5.0
            </span>
          </router-link>
        </div>

        <!-- Desktop Navigation -->
        <div class="hidden md:flex items-center space-x-1">
          <template v-for="item in filteredNavItems" :key="item.path">
            <router-link
              :to="item.path"
              class="flex items-center space-x-1 px-3 py-2 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              :class="{ 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400': route.path === item.path }"
            >
              <span :aria-hidden="true">{{ item.icon }}</span>
              <span>{{ item.label }}</span>
            </router-link>
          </template>
        </div>

        <!-- Right Side: User Info & Actions -->
        <div class="flex items-center space-x-4">
          <!-- Merit Balance (when authenticated) -->
          <div v-if="authStore.isAuthenticated" class="hidden sm:flex items-center space-x-2 px-3 py-1.5 bg-amber-50 dark:bg-amber-900/30 rounded-lg">
            <span class="text-amber-600 dark:text-amber-400" aria-hidden="true">🏆</span>
            <span class="text-sm font-semibold text-amber-800 dark:text-amber-300">
              {{ meritsStore.balance.toLocaleString() }}
            </span>
            <span class="text-xs text-amber-600 dark:text-amber-400">méritos</span>
          </div>

          <!-- Active Flight Badge -->
          <div v-if="authStore.isAuthenticated && airportStore.nextFlight" class="hidden sm:flex items-center space-x-2 px-3 py-1.5 bg-blue-50 dark:bg-blue-900/30 rounded-lg border border-blue-200 dark:border-blue-700">
            <span class="text-blue-600 dark:text-blue-400" aria-hidden="true">✈️</span>
            <span class="text-xs font-medium text-blue-800 dark:text-blue-300">
              {{ airportStore.nextFlight.flight_number }} · {{ airportStore.nextFlight.airport_code }}
            </span>
          </div>

          <!-- Identity Level Badge -->
          <div v-if="authStore.isAuthenticated" class="flex items-center">
            <span
              :class="['inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium', identityColors[authStore.identityLevel]]"
            >
              <span class="mr-1" aria-hidden="true">{{ ['👤','✉️','🏆','🔐','⭐','👑'][authStore.identityLevel] }}</span>
              {{ identityLabels[authStore.identityLevel] }}
            </span>
          </div>

          <!-- Auth Buttons -->
          <div v-if="!authStore.isAuthenticated" class="flex items-center space-x-2">
            <router-link
              to="/login"
              class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              Iniciar Sesión
            </router-link>
            <router-link
              to="/login"
              class="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors"
            >
              Registrarse
            </router-link>
          </div>

          <div v-else class="flex items-center space-x-2">
            <router-link
              to="/settings"
              class="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              aria-label="Configuración"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
            </router-link>
            <button
              @click="handleLogout"
              class="px-4 py-2 text-sm font-medium text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 transition-colors"
            >
              Cerrar Sesión
            </button>
          </div>

          <!-- Mobile Menu Button -->
          <button
            class="md:hidden p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors rounded-lg"
            aria-label="Menú de navegación"
            aria-expanded="false"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" /></svg>
          </button>
        </div>
      </div>

      <!-- Mobile Navigation -->
      <div class="md:hidden py-4 border-t border-gray-200 dark:border-gray-700">
        <div class="flex flex-wrap gap-2">
          <template v-for="item in filteredNavItems" :key="item.path">
            <router-link
              :to="item.path"
              class="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              :class="{ 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400': route.path === item.path }"
            >
              <span :aria-hidden="true">{{ item.icon }}</span>
              <span>{{ item.label }}</span>
            </router-link>
          </template>
        </div>
      </div>
    </nav>
  </header>
</template>