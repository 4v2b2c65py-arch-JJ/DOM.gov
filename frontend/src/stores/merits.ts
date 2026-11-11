/**
 * Merits Store - Merit economy state management
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from '@/api/client';

interface MeritTransaction {
  id: string;
  type: 'earn' | 'spend';
  amount: number;
  reason: string;
  balance_after: number;
  metadata?: any;
  created_at: string;
}

interface SelectingFrontItem {
  id: string;
  name: string;
  category: 'utility' | 'housing' | 'appliance';
  description: string;
  merit_cost: number;
  estimated_value: number;
  provider: string;
  available: boolean;
  requirements?: {
    identity_level: number;
    min_merits: number;
  };
}

interface Order {
  id: string;
  item_id: string;
  item_name: string;
  quantity: number;
  total_merits: number;
  status: 'pending' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled';
  delivery_address?: any;
  created_at: string;
  delivered_at?: string;
}

export const useMeritsStore = defineStore('merits', () => {
  const balance = ref(0);
  const totalEarned = ref(0);
  const totalSpent = ref(0);
  const transactions = ref<MeritTransaction[]>([]);
  const catalog = ref<SelectingFrontItem[]>([]);
  const orders = ref<Order[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const canAfford = computed((cost: number) => balance.value >= cost);
  const utilityItems = computed(() => catalog.value.filter(i => i.category === 'utility'));
  const housingItems = computed(() => catalog.value.filter(i => i.category === 'housing'));
  const applianceItems = computed(() => catalog.value.filter(i => i.category === 'appliance'));
  const availableItems = computed(() => catalog.value.filter(i => i.available));
  const pendingOrders = computed(() => orders.value.filter(o => o.status === 'pending' || o.status === 'confirmed' || o.status === 'shipped'));

  async function fetchBalance() {
    try {
      const data = await api.getMeritBalance();
      balance.value = data.balance;
      totalEarned.value = data.total_earned;
      totalSpent.value = data.total_spent;
    } catch (e: any) {
      error.value = e.message;
    }
  }

  async function fetchHistory(limit = 50, offset = 0) {
    try {
      const data = await api.getMeritHistory(limit, offset);
      transactions.value = data.transactions || data;
    } catch (e: any) {
      error.value = e.message;
    }
  }

  async function earnMerits(amount: number, reason: string, metadata?: any) {
    try {
      const result = await api.earnMerits(amount, reason, metadata);
      balance.value += amount;
      totalEarned.value += amount;
      transactions.value.unshift({
        id: result.transaction_id,
        type: 'earn',
        amount,
        reason,
        balance_after: balance.value,
        metadata,
        created_at: new Date().toISOString(),
      });
      return { success: true };
    } catch (e: any) {
      error.value = e.message;
      return { success: false, error: e.message };
    }
  }

  async function spendMerits(amount: number, item: string, metadata?: any) {
    try {
      const result = await api.spendMerits(amount, item, metadata);
      balance.value -= amount;
      totalSpent.value += amount;
      transactions.value.unshift({
        id: result.transaction_id,
        type: 'spend',
        amount,
        reason: item,
        balance_after: balance.value,
        metadata,
        created_at: new Date().toISOString(),
      });
      return { success: true };
    } catch (e: any) {
      error.value = e.message;
      return { success: false, error: e.message };
    }
  }

  async function fetchCatalog() {
    loading.value = true;
    try {
      catalog.value = await api.getSelectingFrontCatalog();
    } catch (e: any) {
      error.value = e.message;
    } finally {
      loading.value = false;
    }
  }

  async function placeOrder(itemId: string, quantity = 1) {
    try {
      const order = await api.placeOrder(itemId, quantity);
      orders.value.unshift(order);
      return { success: true, order };
    } catch (e: any) {
      error.value = e.message;
      return { success: false, error: e.message };
    }
  }

  async function fetchOrders(status?: string) {
    try {
      orders.value = await api.getOrders(status);
    } catch (e: any) {
      error.value = e.message;
    }
  }

  function clearError() {
    error.value = null;
  }

  return {
    balance,
    totalEarned,
    totalSpent,
    transactions,
    catalog,
    orders,
    loading,
    error,
    canAfford,
    utilityItems,
    housingItems,
    applianceItems,
    availableItems,
    pendingOrders,
    fetchBalance,
    fetchHistory,
    earnMerits,
    spendMerits,
    fetchCatalog,
    placeOrder,
    fetchOrders,
    clearError,
  };
});