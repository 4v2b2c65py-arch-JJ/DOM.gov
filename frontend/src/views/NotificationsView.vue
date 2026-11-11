/**
 * Notifications View
 */

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const notifications = ref([]);
const loading = ref(false);
const selectedCategory = ref('all');

const categories = ['all', 'méritos', 'pagos', 'selecting_front', 'quests', 'veeduría', 'entregas', 'ayuda_mutua', 'convivencia', 'gobernanza', 'identidad', 'sistema'];

onMounted(async () => {
  // Would fetch from telecaster
  notifications.value = [
    { id: '1', type: 'merit_threshold', title: '🏆 ¡Nuevo Beneficio Desbloqueado!', body: 'Alcanzaste 5,000 méritos. Ahora calificas para: Electrodoméstico certificado INFOTEP.', time: Date.now() - 3600000, read: false, category: 'méritos' },
    { id: '2', type: 'payment_confirmed', title: '✅ Pago Confirmado', body: 'Pago de $120 por electricidad (EDE) procesado. Trace: pay_abc123. Méritos: +50', time: Date.now() - 7200000, read: false, category: 'pagos' },
    { id: '3', type: 'quest_reminder', title: '⏰ Recordatorio Quest Mañana', body: 'Mañana tienes visita en Sector Norte. Hogar: Familia Pérez. Confirma: https://dom.gov/quest/confirm/123', time: Date.now() - 86400000, read: true, category: 'quests' },
    { id: '4', type: 'veeduria_nearby', title: '📍 Veeduría Cerca de Ti', body: 'Nueva veeduría #4521 en Zona Colonial (basura). ¿Deseas apoyar? https://dom.gov/veeduria/4521', time: Date.now() - 172800000, read: true, category: 'veeduría' },
    { id: '5', type: 'delivery_completed', title: '✅ Entrega Completada', body: 'Tu nevera LG fue entregada a tu vecino María. Recogerás en la bodega de la esquina.', time: Date.now() - 259200000, read: true, category: 'entregas' },
  ];
});

const filteredNotifications = computed(() => {
  if (selectedCategory.value === 'all') return notifications.value;
  return notifications.value.filter(n => n.category === selectedCategory.value);
});

function formatTime(timestamp: number) {
  const diff = Date.now() - timestamp;
  if (diff < 60000) return 'hace un momento';
  if (diff < 3600000) return `hace ${Math.floor(diff / 60000)} min`;
  if (diff < 86400000) return `hace ${Math.floor(diff / 3600000)} h`;
  return `hace ${Math.floor(diff / 86400000)} d`;
}

function markRead(id: string) {
  const n = notifications.value.find(x => x.id === id);
  if (n) n.read = true;
}

function markAllRead() {
  notifications.value.forEach(n => n.read = true);
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Notificaciones</h1>
        <p class="text-gray-500 dark:text-gray-400">Centro de notificaciones multi-canal (WhatsApp, SMS, Push, USSD, Email)</p>
      </div>
      <div class="flex items-center gap-2">
        <span class="px-3 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 rounded-full text-sm">Próximamente</span>
        <button @click="markAllRead" class="px-3 py-1 text-sm text-indigo-600 dark:text-indigo-400 hover:underline">Marcar todo como leído</button>
      </div>
    </div>

    <!-- Category Filter -->
    <div class="flex gap-2 overflow-x-auto pb-2">
      <button
        v-for="cat in categories"
        :key="cat"
        @click="selectedCategory = cat"
        :class="[
          'px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors',
          selectedCategory === cat
            ? 'bg-indigo-600 text-white'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
        ]"
      >
        {{ cat === 'all' ? 'Todas' : cat }}
      </button>
    </div>

    <!-- Notifications List -->
    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 divide-y divide-gray-200 dark:divide-gray-700">
      <div v-for="notif in filteredNotifications" :key="notif.id" class="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors" :class="{ 'bg-blue-50 dark:bg-blue-900/10': !notif.read }">
        <div class="flex items-start gap-3">
          <div class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
            :class="[
              notif.category === 'méritos' ? 'bg-amber-100 dark:bg-amber-900/30' :
              notif.category === 'pagos' ? 'bg-green-100 dark:bg-green-900/30' :
              notif.category === 'quests' ? 'bg-purple-100 dark:bg-purple-900/30' :
              notif.category === 'veeduría' ? 'bg-orange-100 dark:bg-orange-900/30' :
              notif.category === 'entregas' ? 'bg-blue-100 dark:bg-blue-900/30' :
              'bg-gray-100 dark:bg-gray-700'
            ]">
            <span class="text-lg">{{ notif.title.split(' ')[0] }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between">
              <h4 class="font-medium text-gray-900 dark:text-white truncate">{{ notif.title }}</h4>
              <span class="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap ml-2">{{ formatTime(notif.time) }}</span>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ notif.body }}</p>
            <div class="flex items-center gap-2 mt-2">
              <span class="px-2 py-0.5 text-xs rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400">{{ notif.category }}</span>
              <button v-if="!notif.read" @click="markRead(notif.id)" class="text-xs text-indigo-600 dark:text-indigo-400 hover:underline">Marcar como leída</button>
            </div>
          </div>
          <div v-if="!notif.read" class="w-2 h-2 bg-indigo-500 rounded-full mt-2 ml-12 flex-shrink-0" />
        </div>
      </div>
      <div v-if="filteredNotifications.length === 0" class="p-8 text-center text-gray-500 dark:text-gray-400">
        <span class="text-3xl block mb-2">🔔</span>
        No hay notificaciones en esta categoría.
      </div>
    </div>
  </div>
</template>