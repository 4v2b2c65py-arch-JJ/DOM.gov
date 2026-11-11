/**
 * Veeduría View
 */

<script setup lang="ts">
import { ref } from 'vue';
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Veeduría Ciudadana</h1>
        <p class="text-gray-500 dark:text-gray-400">Reporta, valida y escala problemas en tu comunidad</p>
      </div>
      <span class="px-3 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 rounded-full text-sm">Próximamente</span>
    </div>
    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 text-center">
      <span class="text-4xl block mb-3">📋</span>
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Funcionalidad en desarrollo</h3>
      <p class="text-gray-500 dark:text-gray-400 mb-4">
        Reporte geolocalizado, validación comunitaria, escalamiento automático a autoridades,
        méritos por participación, veedurías cercanas, apoyo a reportes ajenos.
      </p>
    </div>
  </div>
</template>