/**
 * Merits View - Merit Balance, History, and Earning
 */

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { useMeritsStore } from '@/stores/merits';
import { useAuthStore } from '@/stores/auth';

const meritsStore = useMeritsStore();
const authStore = useAuthStore();

const selectedTab = ref<'balance' | 'history' | 'earn'>('balance');
const earnForm = ref({ amount: 0, reason: '', metadata: {} });
const earning = ref(false);

const tabs = [
  { id: 'balance', label: 'Saldo', icon: '🏆' },
  { id: 'history', label: 'Historial', icon: '📜' },
  { id: 'earn', label: 'Ganar Méritos', icon: '➕' },
];

onMounted(async () => {
  await Promise.all([
    meritsStore.fetchBalance(),
    meritsStore.fetchHistory(),
  ]);
});

async function handleEarn() {
  if (!earnForm.value.amount || !earnForm.value.reason) return;
  earning.value = true;
  try {
    await meritsStore.earnMerits(earnForm.value.amount, earnForm.value.reason, earnForm.value.metadata);
    earnForm.value = { amount: 0, reason: '', metadata: {} };
    selectedTab.value = 'balance';
  } finally {
    earning.value = false;
  }
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Economía de Méritos</h1>
        <p class="text-gray-500 dark:text-gray-400">Acumula, gasta y canjea méritos por servicios reales</p>
      </div>
      <div class="flex items-center gap-4 px-6 py-3 bg-amber-50 dark:bg-amber-900/30 rounded-xl border border-amber-200 dark:border-amber-800">
        <span class="text-2xl">🏆</span>
        <div>
          <p class="text-sm text-amber-700 dark:text-amber-400">Saldo Actual</p>
          <p class="text-2xl font-bold text-amber-800 dark:text-amber-300">{{ meritsStore.balance.toLocaleString() }} méritos</p>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="flex gap-1" aria-label="Pestañas de méritos">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="selectedTab = tab.id as any"
          :class="[
            'px-4 py-3 text-sm font-medium rounded-t-lg transition-colors',
            selectedTab === tab.id
              ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600'
              : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
          ]"
        >
          <span class="flex items-center gap-1">{{ tab.icon }} {{ tab.label }}</span>
        </button>
      </nav>
    </div>

    <!-- Balance Tab -->
    <div v-if="selectedTab === 'balance'" class="space-y-6">
      <div class="grid md:grid-cols-3 gap-4">
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <p class="text-sm text-gray-500 dark:text-gray-400">Total Ganados</p>
          <p class="text-3xl font-bold text-green-600 dark:text-green-400 mt-1">{{ meritsStore.totalEarned.toLocaleString() }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <p class="text-sm text-gray-500 dark:text-gray-400">Total Gastados</p>
          <p class="text-3xl font-bold text-red-600 dark:text-red-400 mt-1">{{ meritsStore.totalSpent.toLocaleString() }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <p class="text-sm text-gray-500 dark:text-gray-400">Próximo Nivel</p>
          <p class="text-3xl font-bold text-indigo-600 dark:text-indigo-400 mt-1">
            {{ meritsStore.balance >= 50000 ? 'Vivienda 🏠' : meritsStore.balance >= 5000 ? 'Electrodoméstico 📱' : meritsStore.balance >= 1000 ? 'Utilidad ⚡' : 'Sigue acumulando' }}
          </p>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Cómo ganar méritos</h3>
        </div>
        <div class="p-6 grid md:grid-cols-3 gap-4">
          <div v-for="action in [
            { icon: '🚶', title: 'Quests Territoriales', desc: '50-200 méritos/visita', level: 2 },
            { icon: '📋', title: 'Veeduría Validada', desc: '100-500 méritos/reporte', level: 2 },
            { icon: '🤝', title: 'Ayuda Mutua', desc: '50-150 méritos/ayuda', level: 2 },
            { icon: '💚', title: 'Convivencia Limpia', desc: '10-50 méritos/interacción', level: 3 },
            { icon: '⚖️', title: 'Participación Gobernanza', desc: '200-1000 méritos/voto', level: 3 },
            { icon: '👥', title: 'Referidos', desc: '100 méritos/usuario activo', level: 1 },
          ]" :key="action.title" class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
            <div class="text-2xl mb-2">{{ action.icon }}</div>
            <h4 class="font-semibold text-gray-900 dark:text-white">{{ action.title }}</h4>
            <p class="text-sm text-gray-500 dark:text-gray-400">{{ action.desc }}</p>
            <span class="inline-block mt-2 px-2 py-0.5 text-xs bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400 rounded">Nivel {{ action.level }}+</span>
          </div>
        </div>
      </div>
    </div>

    <!-- History Tab -->
    <div v-if="selectedTab === 'history'" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div class="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Historial de Transacciones</h3>
        <span class="text-sm text-gray-500 dark:text-gray-400">{{ meritsStore.transactions.length }} transacciones</span>
      </div>
      <div class="divide-y divide-gray-200 dark:divide-gray-700">
        <div v-for="tx in meritsStore.transactions" :key="tx.id" class="p-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700/50">
          <div class="flex items-center gap-3">
            <div :class="['w-10 h-10 rounded-full flex items-center justify-center', tx.type === 'earn' ? 'bg-green-100 dark:bg-green-900/30' : 'bg-amber-100 dark:bg-amber-900/30']">
              <span class="text-lg">{{ tx.type === 'earn' ? '+' : '-' }}</span>
            </div>
            <div>
              <p class="font-medium text-gray-900 dark:text-white">{{ tx.reason }}</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">{{ new Date(tx.created_at).toLocaleString('es-DO') }}</p>
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
          No hay transacciones aún. Participa en un Quest o reporta una Veeduría para empezar.
        </div>
      </div>
    </div>

    <!-- Earn Tab (Admin/Testing) -->
    <div v-if="selectedTab === 'earn'" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Registrar Méritos (Testing/Admin)</h3>
      <form @submit.prevent="handleEarn" class="space-y-4 max-w-md">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Cantidad</label>
          <input v-model.number="earnForm.amount" type="number" min="1" class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500" required />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Razón</label>
          <select v-model="earnForm.reason" class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500" required>
            <option value="">Selecciona...</option>
            <option value="Quest completado">Quest completado</option>
            <option value="Veeduría validada">Veeduría validada</option>
            <option value="Ayuda mutua">Ayuda mutua</option>
            <option value="Convivencia Limpia">Convivencia Limpia</option>
            <option value="Participación gobernanza">Participación gobernanza</option>
            <option value="Referido">Referido</option>
            <option value="Bono bienvenida">Bono bienvenida</option>
            <option value="Otro">Otro</option>
          </select>
        </div>
        <button type="submit" :disabled="earning" class="w-full py-2 px-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-indigo-400 transition-colors">
          {{ earning ? 'Registrando...' : 'Añadir Méritos' }}
        </button>
      </form>
    </div>
  </div>
</template>