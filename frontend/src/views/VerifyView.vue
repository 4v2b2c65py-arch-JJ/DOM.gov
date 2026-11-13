/**
 * Verify Magic Link View
 */

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const status = ref<'verifying' | 'success' | 'error'>('verifying');
const message = ref('Verificando enlace...');

onMounted(async () => {
  const token = typeof route.query.token === 'string' ? route.query.token : '';

  if (!token) {
    status.value = 'error';
    message.value = 'Token de verificación no encontrado.';
    return;
  }

  const result = await authStore.verifyMagicLink(token);

  if (result.success) {
    status.value = 'success';
    message.value = 'Identidad verificada correctamente.';
    setTimeout(() => router.push('/dashboard'), 1500);
  } else {
    status.value = 'error';
    message.value = result.error || 'No se pudo verificar el enlace.';
  }
});
</script>

<template>
  <div class="min-h-[60vh] flex items-center justify-center px-4">
    <div class="max-w-md w-full bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 text-center">
      <div v-if="status === 'verifying'">
        <span class="text-4xl block mb-4 animate-pulse">✉️</span>
        <h1 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">Verificando enlace</h1>
        <p class="text-gray-500 dark:text-gray-400">{{ message }}</p>
      </div>

      <div v-else-if="status === 'success'">
        <span class="text-4xl block mb-4">✅</span>
        <h1 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">Verificado</h1>
        <p class="text-gray-500 dark:text-gray-400">{{ message }}</p>
      </div>

      <div v-else>
        <span class="text-4xl block mb-4">⚠️</span>
        <h1 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">Error de verificación</h1>
        <p class="text-gray-500 dark:text-gray-400 mb-6">{{ message }}</p>
        <router-link to="/login" class="inline-block px-6 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors">
          Solicitar nuevo enlace
        </router-link>
      </div>
    </div>
  </div>
</template>