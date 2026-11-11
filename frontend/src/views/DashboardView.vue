/**
 * Dashboard View - Main User Dashboard
 */

<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useMeritsStore } from '@/stores/merits';
import { useAirportStore } from '@/stores/airport';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const meritsStore = useMeritsStore();
const airportStore = useAirportStore();
const router = useRouter();

const identityLabels = ['Anónimo', 'Email Verificado', 'Méritos Vinculados', 'Biométrico', 'Confiable', 'Autorizado/Soeberano'];
const identityIcons = ['👤', '✉️', '🏆', '🔐', '⭐', '👑'];

const quickActions = computed(() => [
  { label: 'Ganar Méritos', icon: '🏆', to: '/merits', level: 2, color: 'green' },
  { label: 'Selecting Front', icon: '📦', to: '/selecting-front', level: 2, color: 'blue' },
  { label: 'Nuevo Quest', icon: '🚶', to: '/quests', level: 2, color: 'purple' },
  { label: 'Reportar Veeduría', icon: '📋', to: '/veeduria', level: 2, color: 'orange' },
  { label: 'Easy Pass Aeropuerto', icon: '✈️', to: '/airport', level: 1, color: 'indigo' },
  { label: 'Billetera Digital', icon: '💳', to: '/wallet', level: 2, color: 'amber' },
  { label: 'Gobernanza', icon: '⚖️', to: '/governance', level: 3, color: 'red' },
  { label: 'Identidad', icon: '🔐', to: '/identity', level: 0, color: 'gray' },
]).filter(a => authStore.identityLevel >= a.level);

const nextLevel = computed(() => {
  if (authStore.identityLevel >= 5) return null;
  return {
    level: authStore.identityLevel + 1,
    label: identityLabels[authStore.identityLevel + 1],
    icon: identityIcons[authStore.identityLevel + 1],
  };
});

onMounted(async () => {
  await Promise.all([
    meritsStore.fetchBalance(),
    meritsStore.fetchCatalog(),
    airportStore.fetchMyClearances(),
  ]);
});
</script>

<template>
  <div class="space-y-8">
    <!-- Welcome Header -->
    <div class="bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 rounded-2xl p-6 sm:p-8 text-white relative overflow-hidden">
      <div class="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.05"%3E%3Cpath d="M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 36v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 6V0H4v4H0v2h4v4h2V6h4V4H6z"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-50" />
      
      <div class="relative flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 class="text-2xl sm:text-3xl font-bold mb-1">Bienvenido, {{ authStore.user?.email?.split('@')[0] || 'Ciudadano' }}</h1>
          <p class="text-white/80">Nivel {{ authStore.identityLevel }} · {{ identityLabels[authStore.identityLevel] }}</p>
        </div>
        
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-3 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/20">
            <span class="text-2xl" aria-hidden="true">{{ identityIcons[authStore.identityLevel] }}</span>
            <div class="text-left">
              <div class="text-sm font-medium">{{ identityLabels[authStore.identityLevel] }}</div>
              <div class="text-xs text-white/70">Nivel {{ authStore.identityLevel }} de 5</div>
            </div>
          </div>
          
          <div v-if="nextLevel" class="hidden sm:flex items-center gap-2 px-4 py-2 bg-yellow-400/20 backdrop-blur-sm rounded-full border border-yellow-400/30">
            <span class="text-yellow-300">▲</span>
            <span class="text-sm font-medium text-yellow-300">Próximo: {{ nextLevel.label }} (Nivel {{ nextLevel.level }})</span>
            <router-link :to="'/identity'" class="text-xs text-yellow-300 hover:underline">Subir nivel</router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Key Metrics -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Méritos Disponibles</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-white mt-1">{{ meritsStore.balance.toLocaleString() }}</p>
          </div>
          <div class="w-12 h-12 bg-amber-100 dark:bg-amber-900/30 rounded-xl flex items-center justify-center">
            <span class="text-2xl">🏆</span>
          </div>
        </div>
        <div class="mt-4 flex items-center gap-2 text-sm">
          <span class="text-green-600 dark:text-green-400 font-medium">+{{ meritsStore.totalEarned.toLocaleString() }}</span> ganados
          <span class="text-gray-400">|</span>
          <span class="text-red-600 dark:text-red-400 font-medium">-{{ meritsStore.totalSpent.toLocaleString() }}</span> gastados
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Órdenes Pendientes</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-white mt-1">{{ meritsStore.pendingOrders.length }}</p>
          </div>
          <div class="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center">
            <span class="text-2xl">📦</span>
          </div>
        </div>
        <router-link to="/selecting-front" class="mt-4 text-sm text-indigo-600 dark:text-indigo-400 hover:underline">Ver catálogo</router-link>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Vuelos Próximos</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-white mt-1">{{ airportStore.activeClearances.length }}</p>
          </div>
          <div class="w-12 h-12 bg-indigo-100 dark:bg-indigo-900/30 rounded-xl flex items-center justify-center">
            <span class="text-2xl">✈️</span>
          </div>
        </div>
        <div v-if="airportStore.nextFlight" class="mt-4 text-sm text-gray-600 dark:text-gray-400">
          {{ airportStore.nextFlight.flight_number }} · {{ airportStore.nextFlight.airport_code }}
          <br>{{ new Date(airportStore.nextFlight.departure_time).toLocaleDateString('es-DO') }}
        </div>
        <router-link v-else to="/airport" class="mt-4 text-sm text-indigo-600 dark:text-indigo-400 hover:underline">Solicitar Easy Pass</router-link>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Nivel de Identidad</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-white mt-1">{{ authStore.identityLevel }}/5</p>
          </div>
          <div class="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center">
            <span class="text-2xl">{{ identityIcons[authStore.identityLevel] }}</span>
          </div>
        </div>
        <div class="mt-4 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div class="h-full bg-indigo-600 transition-all duration-500" :style="{ width: `${(authStore.identityLevel / 5) * 100}%` }"></div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div>
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Acciones Rápidas</h2>
        <router-link to="/merits" class="text-sm text-indigo-600 dark:text-indigo-400 hover:underline">Ver todas</router-link>
      </div>
      <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
        <router-link
          v-for="action in quickActions"
          :key="action.label"
          :to="action.to"
          class="group p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-700 transition-colors text-center"
        >
          <div class="text-3xl mb-2" aria-hidden="true">{{ action.icon }}</div>
          <div class="text-sm font-medium text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">{{ action.label }}</div>
        </router-link>
      </div>
    </div>

    <!-- Next Flight Details -->
    <div v-if="airportStore.nextFlight" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div class="p-6 bg-gradient-to-r from-indigo-600 to-blue-600 text-white">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-semibold">Próximo Vuelo - Easy Pass Activo</h3>
            <p class="text-white/80 text-sm">{{ airportStore.nextFlight.airport_name }}</p>
          </div>
          <span class="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-sm font-medium">
            {{ airportStore.nextFlight.label }}
          </span>
        </div>
      </div>
      <div class="p-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Vuelo</p>
          <p class="font-semibold text-gray-900 dark:text-white">{{ airportStore.nextFlight.flight_number }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Destino</p>
          <p class="font-semibold text-gray-900 dark:text-white">{{ airportStore.nextFlight.destination }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Salida</p>
          <p class="font-semibold text-gray-900 dark:text-white">{{ new Date(airportStore.nextFlight.departure_time).toLocaleString('es-DO') }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Tiempo Estimado</p>
          <p class="font-semibold text-gray-900 dark:text-white">{{ airportStore.nextFlight.estimated_time }}</p>
        </div>
      </div>
      <div class="px-6 py-4 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-200 dark:border-gray-600 flex flex-wrap gap-3">
        <router-link :to="`/airport/clearance/${airportStore.nextFlight.id}`" class="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors">Ver Detalles</router-link>
        <router-link :to="`/airport/clearance/${airportStore.nextFlight.id}`" class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors">QR Code</router-link>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div class="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Actividad Reciente</h3>
        <router-link to="/merits" class="text-sm text-indigo-600 dark:text-indigo-400 hover:underline">Ver todo</router-link>
      </div>
      <div class="divide-y divide-gray-200 dark:divide-gray-700">
        <div v-for="tx in meritsStore.transactions.slice(0, 5)" :key="tx.id" class="p-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700/50">
          <div class="flex items-center gap-3">
            <div :class="['w-10 h-10 rounded-full flex items-center justify-center', tx.type === 'earn' ? 'bg-green-100 dark:bg-green-900/30' : 'bg-amber-100 dark:bg-amber-900/30']">
              <span class="text-lg">{{ tx.type === 'earn' ? '+' : '-' }}</span>
            </div>
            <div>
              <p class="font-medium text-gray-900 dark:text-white">{{ tx.reason }}</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">{{ new Date(tx.created_at).toLocaleDateString('es-DO') }}</p>
            </div>
          </div>
          <div class="text-right">
            <p :class="['font-semibold', tx.type === 'earn' ? 'text-green-600 dark:text-green-400' : 'text-amber-600 dark:text-amber-400']">
              {{ tx.type === 'earn' ? '+' : '-' }}{{ tx.amount.toLocaleString() }}
            </p>
            <p class="text-sm text-gray-500 dark:text-gray-400">Saldo: {{ tx.balance_after.toLocaleString() }}</p>
          </div>
        </div>
        <div v-if="meritsStore.transactions.length === 0" class="p-8 text-center text-gray-500 dark:text-gray-400">
          No hay actividad reciente. ¡Empieza participando en un Quest o reportando una Veeduría!
        </div>
      </div>
    </div>
  </div>
</template>