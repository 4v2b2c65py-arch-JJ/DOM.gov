/**
 * Login / Registration View - Magic Link Authentication
 */

<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { cedulaValidationError, formatCedula, normalizeCedula } from '@/utils/cedula';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const isRegister = computed(() => route.query.register === 'true');
const step = ref<'email' | 'verify' | 'success'>('email');
const loading = ref(false);
const error = ref<string | null>(null);
const successMessage = ref('');

const form = reactive({
  email: '',
  cedula: '',
  token: '',
});

const cedulaError = computed(() => {
  if (!isRegister.value || !form.cedula) return '';
  return cedulaValidationError(form.cedula);
});

const canSubmitEmail = computed(() => {
  if (!form.email) return false;
  if (isRegister.value && !form.cedula) return false;
  return true;
});

function onCedulaInput(event: Event) {
  const target = event.target as HTMLInputElement;
  form.cedula = formatCedula(target.value);
}

async function handleSubmit() {
  error.value = null;

  if (step.value === 'email') {
    if (isRegister.value && cedulaError.value) {
      error.value = cedulaError.value;
      return;
    }

    loading.value = true;
    try {
      const result = await authStore.loginWithMagicLink(
        form.email,
        isRegister.value ? normalizeCedula(form.cedula) : undefined,
      );
      if (!result.success) {
        error.value = result.error || 'No se pudo enviar el enlace.';
        return;
      }
      step.value = 'verify';
      successMessage.value = `Enviamos un enlace mágico a ${form.email}. Revisa tu bandeja de entrada (y spam).`;
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Ocurrió un error inesperado.';
    } finally {
      loading.value = false;
    }
    return;
  }

  if (step.value === 'verify') {
    loading.value = true;
    try {
      const result = await authStore.verifyMagicLink(form.token);
      if (!result.success) {
        error.value = result.error || 'Código inválido o expirado.';
        return;
      }
      step.value = 'success';
      successMessage.value = '¡Bienvenido! Redirigiendo al dashboard...';
      setTimeout(() => {
        const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/dashboard';
        router.push(redirect);
      }, 1500);
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Ocurrió un error inesperado.';
    } finally {
      loading.value = false;
    }
  }
}

function resendLink() {
  step.value = 'email';
  form.token = '';
}

function goBack() {
  if (step.value === 'verify') {
    step.value = 'email';
    form.token = '';
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4 py-12">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-8">
        <router-link to="/" class="inline-flex items-center space-x-2">
          <span class="text-3xl">🇩🇴</span>
          <span class="text-2xl font-bold text-gray-900 dark:text-white">DOM.gov</span>
        </router-link>
        <p class="text-gray-500 dark:text-gray-400 mt-2">
          {{ isRegister ? 'Crea tu cuenta' : 'Inicia sesión' }} con enlace mágico
        </p>
      </div>

      <!-- Card -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-8">
        <!-- Step 1: Email (+ cédula when registering) -->
        <div v-if="step === 'email'" class="space-y-6">
          <div v-if="isRegister">
            <label for="cedula" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Cédula de identidad
            </label>
            <input
              id="cedula"
              v-model="form.cedula"
              type="text"
              inputmode="numeric"
              autocomplete="off"
              maxlength="14"
              @input="onCedulaInput"
              :disabled="loading"
              class="w-full px-4 py-3 rounded-lg border bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
              :class="cedulaError ? 'border-red-400 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'"
              placeholder="001-1234567-8"
              required
            />
            <p v-if="cedulaError" class="mt-1 text-sm text-red-600 dark:text-red-400">{{ cedulaError }}</p>
            <p v-else class="mt-1 text-xs text-gray-500 dark:text-gray-400">Entre 11 y 12 dígitos, sin importar guiones.</p>
          </div>

          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Correo electrónico
            </label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              autocomplete="email"
              @keyup.enter="handleSubmit"
              :disabled="loading"
              class="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
              placeholder="tu@email.com"
              required
            />
          </div>

          <div v-if="error" class="p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">
            {{ error }}
          </div>

          <button
            @click="handleSubmit"
            :disabled="loading || !canSubmitEmail"
            class="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-semibold rounded-lg transition-colors focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
          >
            <span v-if="loading" class="flex items-center justify-center gap-2">
              <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
              Enviando...
            </span>
            <span v-else>Enviar Enlace Mágico</span>
          </button>

          <p class="text-center text-sm text-gray-500 dark:text-gray-400">
            <template v-if="isRegister">
              Ya tienes cuenta? <router-link to="/login" class="text-indigo-600 hover:text-indigo-500 font-medium">Inicia sesión</router-link>
            </template>
            <template v-else>
              No tienes cuenta? <router-link to="/login?register=true" class="text-indigo-600 hover:text-indigo-500 font-medium">Regístrate</router-link>
            </template>
          </p>
        </div>

        <!-- Step 2: Verify Token -->
        <div v-else-if="step === 'verify'" class="space-y-6">
          <div class="text-center">
            <div class="w-16 h-16 mx-auto mb-4 bg-indigo-100 dark:bg-indigo-900/30 rounded-full flex items-center justify-center">
              <svg class="w-8 h-8 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">Revisa tu email</h3>
            <p class="text-gray-500 dark:text-gray-400">{{ successMessage }}</p>
          </div>

          <div>
            <label for="token" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Código de verificación (6 dígitos)
            </label>
            <input
              id="token"
              v-model="form.token"
              type="text"
              inputmode="numeric"
              maxlength="6"
              @keyup.enter="handleSubmit"
              :disabled="loading"
              class="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors text-center tracking-widest text-2xl"
              placeholder="123456"
              required
            />
          </div>

          <div v-if="error" class="p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">
            {{ error }}
          </div>

          <button
            @click="handleSubmit"
            :disabled="loading || form.token.length !== 6"
            class="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-semibold rounded-lg transition-colors focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
          >
            <span v-if="loading" class="flex items-center justify-center gap-2">
              <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
              Verificando...
            </span>
            <span v-else>Verificar y Entrar</span>
          </button>

          <div class="flex items-center justify-between">
            <button
              @click="goBack"
              :disabled="loading"
              class="text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
            >
              ← Cambiar email
            </button>
            <button
              @click="resendLink"
              :disabled="loading"
              class="text-sm text-indigo-600 hover:text-indigo-500 font-medium"
            >
              Reenviar enlace
            </button>
          </div>
        </div>

        <!-- Step 3: Success -->
        <div v-else-if="step === 'success'" class="text-center space-y-4">
          <div class="w-16 h-16 mx-auto mb-4 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
          </div>
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white">¡Bienvenido a DOM.gov!</h3>
          <p class="text-green-600 dark:text-green-400">{{ successMessage }}</p>
        </div>
      </div>

      <!-- Info -->
      <div class="mt-6 text-center text-sm text-gray-500 dark:text-gray-400 space-y-1">
        <p>Sin contraseñas. Solo tu email y un clic.</p>
        <p class="text-xs">Al continuar, aceptas nuestros <a href="#" class="text-indigo-600 hover:underline">Términos</a> y <a href="#" class="text-indigo-600 hover:underline">Privacidad</a>.</p>
      </div>
    </div>
  </div>
</template>