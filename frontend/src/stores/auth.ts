/**
 * Auth Store - User authentication and identity state
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from '@/api/client';

interface User {
  id: string;
  email: string;
  identity_level: number;
  merit_balance: number;
  veeduria_score: number;
  trust_score: number;
  passport_number?: string;
  biometric_verified: boolean;
  created_at: string;
  capabilities: string[];
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const isAuthenticated = computed(() => !!user.value);
  const identityLevel = computed(() => user.value?.identity_level || 0);
  const capabilities = computed(() => user.value?.capabilities || []);
  const meritBalance = computed(() => user.value?.merit_balance || 0);

  const hasCapability = (cap: string) => capabilities.value.includes(cap);
  const canAccessLevel = (level: number) => identityLevel.value >= level;

  async function fetchUser() {
    loading.value = true;
    error.value = null;
    try {
      user.value = await api.getMe();
    } catch (e: any) {
      error.value = e.message;
      user.value = null;
    } finally {
      loading.value = false;
    }
  }

  async function loginWithMagicLink(email: string) {
    loading.value = true;
    error.value = null;
    try {
      await api.requestMagicLink(email);
      return { success: true };
    } catch (e: any) {
      error.value = e.message;
      return { success: false, error: e.message };
    } finally {
      loading.value = false;
    }
  }

  async function verifyMagicLink(token: string) {
    loading.value = true;
    error.value = null;
    try {
      const userData = await api.verifyMagicLink(token);
      user.value = userData;
      return { success: true, user: userData };
    } catch (e: any) {
      error.value = e.message;
      return { success: false, error: e.message };
    } finally {
      loading.value = false;
    }
  }

  async function logout() {
    await api.logout();
    user.value = null;
  }

  async function refreshMeritBalance() {
    try {
      const data = await api.getMeritBalance();
      if (user.value) {
        user.value.merit_balance = data.balance;
      }
    } catch (e) {
      console.error('Failed to refresh merit balance', e);
    }
  }

  async function escalateIdentity(targetLevel: number, data: any) {
    loading.value = true;
    try {
      const result = await api.escalateIdentity(targetLevel, data);
      if (user.value) {
        user.value.identity_level = result.identity_level;
        user.value.capabilities = result.capabilities;
        user.value.biometric_verified = result.biometric_verified || false;
      }
      return { success: true };
    } catch (e: any) {
      error.value = e.message;
      return { success: false, error: e.message };
    } finally {
      loading.value = false;
    }
  }

  return {
    user,
    loading,
    error,
    isAuthenticated,
    identityLevel,
    capabilities,
    meritBalance,
    hasCapability,
    canAccessLevel,
    fetchUser,
    loginWithMagicLink,
    verifyMagicLink,
    logout,
    refreshMeritBalance,
    escalateIdentity,
  };
});