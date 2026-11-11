/**
 * Settings View
 */

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const notificationCategories = [
  'méritos', 'pagos', 'selecting_front', 'quests', 'veeduría', 
  'entregas', 'ayuda_mutua', 'convivencia', 'gobernanza', 'identidad', 'sistema'
];

const enabledCategories = ref(notificationCategories);

function toggleCategory(cat: string) {
  const idx = enabledCategories.value.indexOf(cat);
  if (idx >= 0) enabledCategories.value.splice(idx, 1);
  else enabledCategories.value.push(cat);
}

async function handleLogout() {
  await authStore.logout();
  router.push('/');
}
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Configuración</h1>
      <p class="text-gray-500 dark:text-gray-400">Cuenta, notificaciones, privacidad, seguridad</p>
    </div>

    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 space-y-8">
      <!-- Account -->
      <div>
        <h3 class="font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <span class="text-xl">👤</span> Cuenta
        </h3>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <div>
              <p class="font-medium text-gray-900 dark:text-white">Email</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">{{ authStore.user?.email || 'No disponible' }}</p>
            </div>
            <span class="px-2 py-1 text-xs bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 rounded">Verificado</span>
          </div>
          <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <div>
              <p class="font-medium text-gray-900 dark:text-white">Nivel de Identidad</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">Nivel {{ authStore.identityLevel }} de 5</p>
            </div>
            <router-link to="/identity" class="px-3 py-1 text-sm bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400 rounded hover:bg-indigo-200 dark:hover:bg-indigo-900/50 transition-colors">Gestionar Nivel</router-link>
          </div>
          <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <div>
              <p class="font-medium text-gray-900 dark:text-white">Méritos</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">{{ authStore.meritBalance?.toLocaleString() || 0 }} disponibles</p>
            </div>
            <router-link to="/merits" class="px-3 py-1 text-sm bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 rounded hover:bg-amber-200 dark:hover:bg-amber-900/50 transition-colors">Ver Detalles</router-link>
          </div>
        </div>
      </div>

      <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
        <h3 class="font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <span class="text-xl">🔔</span> Preferencias de Notificaciones
        </h3>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">Activa/desactiva categorías. Las notificaciones de emergencia y seguridad no se pueden desactivar.</p>
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
          <label v-for="cat in notificationCategories" :key="cat" class="flex items-center gap-2 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
            <input type="checkbox" :checked="enabledCategories.includes(cat)" @change="toggleCategory(cat)" class="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500" />
            <span class="text-sm text-gray-700 dark:text-gray-300 capitalize">{{ cat.replace('_', ' ') }}</span>
          </label>
        </div>
      </div>

      <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
        <h3 class="font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <span class="text-xl">🌙</span> Apariencia
        </h3>
        <div class="flex items-center gap-4">
          <label class="flex items-center gap-2 cursor-pointer">
            <input type="radio" name="theme" value="light" class="w-4 h-4 text-indigo-600" />
            <span class="text-sm text-gray-700 dark:text-gray-300">Claro</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input type="radio" name="theme" value="dark" class="w-4 h-4 text-indigo-600" />
            <span class="text-sm text-gray-700 dark:text-gray-300">Oscuro</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input type="radio" name="theme" value="system" checked class="w-4 h-4 text-indigo-600" />
            <span class="text-sm text-gray-700 dark:text-gray-300">Sistema</span>
          </label>
        </div>
      </div>

      <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
        <h3 class="font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <span class="text-xl">🔒</span> Privacidad y Seguridad
        </h3>
        <div class="space-y-3">
          <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <div>
              <p class="font-medium text-gray-900 dark:text-white">Autenticación de dos factores</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">Añade una capa extra de seguridad</p>
            </div>
            <button class="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors">Configurar</button>
          </div>
          <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <div>
              <p class="font-medium text-gray-900 dark:text-white">Sesiones activas</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">Ver y revocar dispositivos</p>
            </div>
            <button class="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors">Ver</button>
          </div>
          <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <div>
              <p class="font-medium text-gray-900 dark:text-white">Datos personales</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">Exportar o eliminar tus datos</p>
            </div>
            <button class="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors">Gestionar</button>
          </div>
        </div>
      </div>

      <!-- Danger Zone -->
      <div class="border-t border-red-200 dark:border-red-800 pt-6 bg-red-50 dark:bg-red-900/20 rounded-lg p-6">
        <h3 class="font-semibold text-red-700 dark:text-red-400 mb-4 flex items-center gap-2">
          <span class="text-xl">⚠️</span> Zona de Peligro
        </h3>
        <p class="text-sm text-red-600 dark:text-red-400 mb-4">Estas acciones son irreversibles.</p>
        <div class="flex flex-wrap gap-3">
          <button class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">Eliminar Cuenta</button>
          <button class="px-4 py-2 bg-red-200 dark:bg-red-800 text-red-700 dark:text-red-300 rounded-lg hover:bg-red-300 dark:hover:bg-red-700 transition-colors">Revocar Todo Acceso</button>
        </div>
      </div>

      <div class="pt-4">
        <button @click="handleLogout" class="w-full py-2 px-4 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors">Cerrar Sesión</button>
      </div>
    </div>
  </div>
</template>