/**
 * Wallet View
 */

<script setup lang="ts">
import { ref } from 'vue';
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Billetera Digital</h1>
        <p class="text-gray-500 dark:text-gray-400">Apple Pay / Google Pay + 10 bancos dominicanos</p>
      </div>
      <span class="px-3 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 rounded-full text-sm">Próximamente</span>
    </div>
    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 text-center">
      <span class="text-4xl block mb-3">💳</span>
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Funcionalidad en desarrollo</h3>
      <p class="text-gray-500 dark:text-gray-400 mb-4">
        Tokenización de tarjetas, Apple Pay / Google Pay unificado, 10 bancos DR (Popular, Banreservas, BHD, Scotiabank, BDI, Santa Cruz, Caribe, Cibao, La Nacional, La Vega Real),
        pagos auto-llenados vía APIs gubernamentales.
      </p>
    </div>
  </div>
</template>