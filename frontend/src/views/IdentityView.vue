/**
 * Identity View - Progressive Identity Levels
 */

<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { cedulaValidationError, formatCedula, normalizeCedula } from '@/utils/cedula';

const authStore = useAuthStore();

const cedulaForm = reactive({ cedula: '' });
const verifying = ref(false);
const cedulaMessage = ref('');

const cedulaError = computed(() => cedulaValidationError(cedulaForm.cedula));

function onCedulaInput(event: Event) {
  cedulaForm.cedula = formatCedula((event.target as HTMLInputElement).value);
}

async function verifyCedula() {
  cedulaMessage.value = '';
  if (cedulaError.value) {
    cedulaMessage.value = cedulaError.value;
    return;
  }
  verifying.value = true;
  try {
    const result = await authStore.verifyCedula(normalizeCedula(cedulaForm.cedula));
    cedulaMessage.value = result.success
      ? 'Cédula verificada correctamente.'
      : result.error || 'No se pudo verificar la cédula.';
  } finally {
    verifying.value = false;
  }
}

const levels = [
  { level: 0, label: 'Anónimo', icon: '👤', capabilities: ['Navegación anónima', 'Información pública'] },
  { level: 1, label: 'Email Verificado', icon: '✉️', capabilities: ['Notificaciones básicas', 'Pre-check aeropuerto', 'Email verificado', 'Enlace mágico'] },
  { level: 2, label: 'Méritos Vinculados', icon: '🏆', capabilities: ['Acumular méritos', 'Selecting Front', 'Quests', 'Veeduría', 'Viajero confiable', 'Trusted lanes aeropuerto'] },
  { level: 3, label: 'Biométrico', icon: '🔐', capabilities: ['Autenticación biométrica', 'eGate aeropuerto', 'Votación gobernanza', 'Consenso multi-IA', 'Puertas automáticas'] },
  { level: 4, label: 'Confiable', icon: '⭐', capabilities: ['VIP aeropuerto', 'Oficial dedicado', 'Supervisión FGA', 'Propuesta políticas', 'Asignación presupuesto', 'Carril diplomático'] },
  { level: 5, label: 'Autorizado/Soeberano', icon: '👑', capabilities: ['Protocolo estado', 'Inmunidad procesal', 'Acción constitucional', 'Avión gubernamental', 'Escolta', 'Carril soberano'] },
];

const currentLevel = computed(() => authStore.identityLevel);

function getProgressPercent(level: number) {
  return ((level) / 5) * 100;
}
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Identidad Progresiva</h1>
      <p class="text-gray-500 dark:text-gray-400">6 niveles - Anónimo → Soberano. Cada nivel desbloquea capacidades reales</p>
    </div>

    <!-- Progress Bar -->
    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
      <div class="mb-4">
        <div class="flex items-center justify-between mb-2">
          <span class="font-medium text-gray-900 dark:text-white">Tu Progreso</span>
          <span class="text-sm text-gray-500 dark:text-gray-400">Nivel {{ currentLevel }}/5</span>
        </div>
        <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div class="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-blue-500 rounded-full transition-all duration-500" :style="{ width: `${getProgressPercent(currentLevel)}%` }"></div>
        </div>
        <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
          <span>0 Anónimo</span>
          <span>1 Email</span>
          <span>2 Méritos</span>
          <span>3 Bio</span>
          <span>4 Confiable</span>
          <span>5 Soberano</span>
        </div>
      </div>

      <div class="flex items-center gap-4 p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
        <span class="text-4xl">{{ levels[currentLevel].icon }}</span>
        <div>
          <h3 class="font-semibold text-gray-900 dark:text-white">Nivel {{ currentLevel }}: {{ levels[currentLevel].label }}</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">{{ levels[currentLevel].capabilities.length }} capacidades desbloqueadas</p>
        </div>
      </div>
    </div>

    <!-- Cédula verification -->
    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
      <div class="flex items-center gap-2 mb-4">
        <span class="text-2xl">🪪</span>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Verificación de Cédula</h2>
        <span
          v-if="authStore.cedulaVerified"
          class="ml-auto px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full text-xs"
        >Verificada</span>
      </div>
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
        La cédula (11 a 12 dígitos) habilita el nivel 2 y permite vincular cuentas bancarias para recibir pagos y subsidios.
      </p>
      <div class="flex flex-col sm:flex-row gap-3">
        <input
          v-model="cedulaForm.cedula"
          type="text"
          inputmode="numeric"
          maxlength="14"
          @input="onCedulaInput"
          :disabled="verifying"
          class="flex-1 px-4 py-3 rounded-lg border bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-indigo-500"
          :class="cedulaForm.cedula && cedulaError ? 'border-red-400' : 'border-gray-300 dark:border-gray-600'"
          placeholder="001-1234567-8"
        />
        <button
          @click="verifyCedula"
          :disabled="verifying || !cedulaForm.cedula"
          class="py-3 px-6 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-semibold rounded-lg transition-colors"
        >
          {{ verifying ? 'Verificando...' : 'Verificar cédula' }}
        </button>
      </div>
      <p v-if="cedulaForm.cedula && cedulaError" class="mt-2 text-sm text-red-600 dark:text-red-400">{{ cedulaError }}</p>
      <p v-if="cedulaMessage" class="mt-2 text-sm text-gray-600 dark:text-gray-300">{{ cedulaMessage }}</p>
    </div>

    <!-- All Levels -->
    <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="lvl in levels"
        :key="lvl.level"
        :class="[
          'p-5 rounded-xl border transition-all',
          lvl.level === currentLevel
            ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20 ring-2 ring-indigo-500/20'
            : lvl.level < currentLevel
              ? 'border-green-300 dark:border-green-700 bg-green-50 dark:bg-green-900/20'
              : 'border-gray-200 dark:border-gray-700'
        ]"
      >
        <div class="flex items-center gap-3 mb-3">
          <div :class="['w-12 h-12 rounded-xl flex items-center justify-center text-2xl', lvl.level === currentLevel ? 'bg-indigo-100 dark:bg-indigo-900/30' : lvl.level < currentLevel ? 'bg-green-100 dark:bg-green-900/30' : 'bg-gray-100 dark:bg-gray-700']">
            {{ lvl.icon }}
          </div>
          <div>
            <h3 class="font-semibold text-gray-900 dark:text-white">Nivel {{ lvl.level }}</h3>
            <p class="text-sm text-gray-500 dark:text-gray-400">{{ lvl.label }}</p>
          </div>
        </div>
        <div class="space-y-1">
          <div v-for="cap in lvl.capabilities" :key="cap" class="flex items-center gap-2 text-sm"
            :class="lvl.level <= currentLevel ? 'text-gray-700 dark:text-gray-300' : 'text-gray-400 dark:text-gray-500'">
            <span :class="lvl.level <= currentLevel ? 'text-green-500' : 'text-gray-300 dark:text-gray-600'">✓</span>
            {{ cap }}
          </div>
        </div>
        <div v-if="lvl.level > currentLevel" class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <span class="text-xs text-gray-500 dark:text-gray-400">Requiere: </span>
          <span class="text-xs font-medium text-indigo-600 dark:text-indigo-400">
            {{ lvl.level === 1 ? 'Verificar email' :
               lvl.level === 2 ? 'Acumular méritos + participar' :
               lvl.level === 3 ? 'Registro biométrico' :
               lvl.level === 4 ? 'Invitación FGA + méritos altos' :
               'Designación oficial' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>