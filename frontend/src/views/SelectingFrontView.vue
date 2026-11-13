/**
 * Selecting Front View - Merit Redemption Catalog
 */

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { useMeritsStore } from '@/stores/merits';

const meritsStore = useMeritsStore();

const selectedCategory = ref<'all' | 'utility' | 'housing' | 'appliance'>('all');
const categories = [
  { id: 'all', label: 'Todos', icon: '📦' },
  { id: 'utility', label: 'Utilidades', icon: '⚡' },
  { id: 'housing', label: 'Vivienda', icon: '🏠' },
  { id: 'appliance', label: 'Electrodomésticos', icon: '📱' },
];

const filteredItems = computed(() => {
  if (selectedCategory.value === 'all') return meritsStore.availableItems;
  return meritsStore.catalog.filter(i => i.category === selectedCategory.value && i.available);
});

onMounted(async () => {
  await meritsStore.fetchCatalog();
});

async function handleOrder(item: any) {
  const confirm = window.confirm(`¿Confirmar pedido de "${item.name}" por ${item.merit_cost.toLocaleString()} méritos?\n\nSaldo actual: ${meritsStore.balance.toLocaleString()} méritos\nSaldo restante: ${(meritsStore.balance - item.merit_cost).toLocaleString()} méritos`);
  if (!confirm) return;
  
  const result = await meritsStore.placeOrder(item.id);
  if (result.success) {
    alert('¡Pedido confirmado! Recibirás notificación cuando esté listo para entrega.');
  } else {
    alert(`Error: ${result.error}`);
  }
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Selecting Front</h1>
        <p class="text-gray-500 dark:text-gray-400">Canjea tus méritos por servicios y bienes reales</p>
      </div>
      <div class="flex items-center gap-3 px-4 py-2 bg-amber-50 dark:bg-amber-900/30 rounded-xl border border-amber-200 dark:border-amber-800">
        <span class="text-xl">🏆</span>
        <div class="text-right">
          <p class="text-xs text-amber-700 dark:text-amber-400">Tu saldo</p>
          <p class="font-bold text-amber-800 dark:text-amber-300">{{ meritsStore.balance.toLocaleString() }} méritos</p>
        </div>
      </div>
    </div>

    <!-- Category Tabs -->
    <div class="flex gap-2 overflow-x-auto pb-2">
      <button
        v-for="cat in categories"
        :key="cat.id"
        @click="selectedCategory = cat.id as any"
        :class="[
          'px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors flex items-center gap-1',
          selectedCategory === cat.id
            ? 'bg-indigo-600 text-white'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
        ]"
      >
        {{ cat.icon }} {{ cat.label }}
      </button>
    </div>

    <!-- Items Grid -->
    <div class="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <div
        v-for="item in filteredItems"
        :key="item.id"
        class="group bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-lg hover:border-indigo-300 dark:hover:border-indigo-700 transition-all"
        :class="{ 'opacity-50 pointer-events-none': !meritsStore.canAfford(item.merit_cost) }"
      >
        <div class="aspect-square bg-gray-100 dark:bg-gray-700 flex items-center justify-center text-5xl">
          {{ item.category === 'utility' ? '⚡' : item.category === 'housing' ? '🏠' : '📱' }}
        </div>
        <div class="p-4 space-y-2">
          <div class="flex items-center justify-between">
            <h3 class="font-semibold text-gray-900 dark:text-white truncate">{{ item.name }}</h3>
            <span class="px-2 py-0.5 text-xs font-medium rounded-full"
              :class="item.category === 'utility' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400' :
                       item.category === 'housing' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' :
                       'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'">
              {{ item.category }}
            </span>
          </div>
          <p class="text-sm text-gray-500 dark:text-gray-400 line-clamp-2">{{ item.description }}</p>
          <div class="flex items-center justify-between pt-2 border-t border-gray-100 dark:border-gray-700">
            <div class="flex items-center gap-1 text-amber-600 dark:text-amber-400">
              <span class="text-lg">🏆</span>
              <span class="font-bold text-lg">{{ item.merit_cost.toLocaleString() }}</span>
            </div>
            <span class="text-xs text-gray-500 dark:text-gray-400">Valor: ${{ item.estimated_value }}</span>
          </div>
          <button
            @click="handleOrder(item)"
            :disabled="!meritsStore.canAfford(item.merit_cost) || meritsStore.loading"
            class="w-full py-2 px-3 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-1"
            :class="meritsStore.canAfford(item.merit_cost)
              ? 'bg-indigo-600 text-white hover:bg-indigo-700'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed'"
          >
            <span v-if="meritsStore.loading">Procesando...</span>
            <span v-else-if="meritsStore.canAfford(item.merit_cost)">Canjear</span>
            <span v-else>Faltan {{ (item.merit_cost - meritsStore.balance).toLocaleString() }} méritos</span>
          </button>
        </div>
      </div>
    </div>

    <div v-if="filteredItems.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
      <span class="text-4xl block mb-2">📦</span>
      No hay artículos disponibles en esta categoría.
    </div>

    <!-- My Orders -->
    <div v-if="meritsStore.orders.length > 0" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
      <div class="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Mis Pedidos</h3>
        <span class="text-sm text-gray-500 dark:text-gray-400">{{ meritsStore.orders.length }} pedidos</span>
      </div>
      <div class="divide-y divide-gray-200 dark:divide-gray-700">
        <div v-for="order in meritsStore.orders.slice(0, 5)" :key="order.id" class="p-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700/50">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg flex items-center justify-center">
              <span class="text-lg">{{ order.item_name.includes('Vivienda') ? '🏠' : order.item_name.includes('Utilidad') ? '⚡' : '📱' }}</span>
            </div>
            <div>
              <p class="font-medium text-gray-900 dark:text-white">{{ order.item_name }}</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">{{ new Date(order.created_at).toLocaleDateString('es-DO') }} · {{ order.quantity }} uds</p>
            </div>
          </div>
          <div class="text-right">
            <p class="font-semibold text-amber-600 dark:text-amber-400">{{ order.total_merits.toLocaleString() }} méritos</p>
            <span class="inline-block px-2 py-0.5 text-xs rounded-full"
              :class="order.status === 'delivered' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' :
                       order.status === 'shipped' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' :
                       order.status === 'confirmed' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400' :
                       'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'">
              {{ order.status }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>