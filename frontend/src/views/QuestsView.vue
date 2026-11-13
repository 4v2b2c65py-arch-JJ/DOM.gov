/**
 * Quests View
 */

<script setup lang="ts">
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Quests Territoriales</h1>
        <p class="text-gray-500 dark:text-gray-400">Visitas domiciliarias verificadas con GPS + referencias comunitarias</p>
      </div>
      <span class="px-3 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 rounded-full text-sm">Próximamente</span>
    </div>
    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 text-center">
      <span class="text-4xl block mb-3">🚶</span>
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Funcionalidad en desarrollo</h3>
      <p class="text-gray-500 dark:text-gray-400 mb-4">
        Asignación de Quests, pre-verificación Quest, visitas con GPS, referencias comunitarias (colmado, iglesia, escuela),
        cadena de vecinos, puntos de entrega comunitaria, stipend diario.
      </p>
      <div class="grid md:grid-cols-3 gap-4 text-sm text-gray-500 dark:text-gray-400">
        <div>📍 GPS + Referencias comunitarias</div>
        <div>🔍 Pre-verificación Quest</div>
        <div>🤝 Cadena de vecinos</div>
        <div>📦 Puntos de entrega</div>
        <div>💰 Stipend diario</div>
        <div>🏆 Méritos por visita</div>
      </div>
    </div>
  </div>
</template>