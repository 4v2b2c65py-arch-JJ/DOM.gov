/**
 * NotFound View - 404 Page
 */

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();
</script>

<template>
  <div class="min-h-[70vh] flex items-center justify-center text-center px-4">
    <div class="max-w-md">
      <span class="text-7xl block mb-4 animate-bounce">🏝️</span>
      <h1 class="text-5xl font-bold text-gray-900 dark:text-white mb-3">404</h1>
      <h2 class="text-2xl font-semibold text-gray-700 dark:text-gray-300 mb-4">Página No Encontrada</h2>
      <p class="text-gray-500 dark:text-gray-400 mb-8 leading-relaxed">
        La página que buscas no existe o ha sido movida. 
        Puede que necesites un nivel de identidad más alto para acceder.
      </p>
      <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
        <router-link to="/" class="px-6 py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors shadow-lg">
          🏠 Volver al Inicio
        </router-link>
        <router-link v-if="!isAuthenticated" to="/login" class="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-xl font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors">
          🔐 Iniciar Sesión
        </router-link>
        <router-link v-else to="/dashboard" class="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-xl font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors">
          📊 Mi Dashboard
        </router-link>
      </div>
      
      <div class="mt-12 pt-8 border-t border-gray-200 dark:border-gray-700">
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">¿Necesitas ayuda?</p>
        <div class="flex items-center justify-center gap-4 text-sm">
          <a href="https://github.com/4v2b2c65py-arch-JJ/DOM.gov/issues" target="_blank" rel="noopener noreferrer" class="text-indigo-600 dark:text-indigo-400 hover:underline">Reportar en GitHub</a>
          <span class="text-gray-400">|</span>
          <a href="mailto:soporte@dom.gov" class="text-indigo-600 dark:text-indigo-400 hover:underline">Email Soporte</a>
          <span class="text-gray-400">|</span>
          <a href="#" class="text-indigo-600 dark:text-indigo-400 hover:underline">Documentación</a>
        </div>
      </div>
    </div>
  </div>
</template>