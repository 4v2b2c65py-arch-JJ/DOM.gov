/**
 * Login View - Magic Link Authentication
 */

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const isRegister = route.query.register === 'true';
const step = ref<'email' | 'verify' | 'success'>('email');
const loading = ref(false);
const error = ref<string | null>(null);
const successMessage = ref('');

const form = reactive({
  email: '',
  token: '',
});

const emailRules = [
  (v: string) => !!v || 'El email es requerido',
  (v: string) => /.+@.+\..+/.test(v) || 'Email inválido',
];

async function handleSubmit() {
  if (step.value === 'email') {
    loading.value = true;
    error.value = null;
    try {
      await authStore.loginWithMagicLink(form.email);
      step.value = 'verify';
      successMessage.value = `Enviamos un enlace mágico a ${form.email}. Revisa tu bandeja de entrada (y spam).`;
    } catch (e: any) {
      error.value = e.message;
    } finally {
      loading.value = false;
    }
  } else if (step.value === 'verify') {
    loading.value = true;
    error.value = null;
    try {
      const result = await authStore.verifyMagicLink(form.token);
      if (result.success) {
        step.value = 'success';
        successMessage.value = '¡Bienvenido! Redirigiendo al dashboard...';
        setTimeout(() => {
          const redirect = route.query.redirect as string || '/dashboard';
          router.push(redirect);
        }, 1500);
      }
    } catch (e: any) {
      error.value = e.message;
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
        <!-- Step 1: Email -->
        <div v-if="step.value === 'email'" class="space-y-6">
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
            :disabled="loading || !form.email"
            class="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-semibold rounded-lg transition-colors focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
          >
            <span v-if="loading" class="flex items-center justify-center gap-2">
              <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
              Enviando...
            </span>
            <span v-else>Enviar Enlace Mágico</span>
          </button>

          <p class="text-center text-sm text-gray-500 dark:text-gray-400">
            No tienes cuenta? <router-link to="/login?register=true" class="text-indigo-600 hover:text-indigo-500 font-medium">Regístrate</router-link>
          </p>
        </div>

        <!-- Step 2: Verify Token -->
        <div v-else-if="step.value === 'verify'" class="space-y-6">
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

          <button
            @click="resendLink"
            :disabled="loading"
            class="w-full py-2 px-4 text-indigo-600 hover:text-indigo-500 font-medium text-sm transition-colors"
          >
            Reenviar enlace
          </button>
        </div>

        <!-- Step 3: Success -->
        <div v-else-if="step.value === 'success'" class="text-center space-y-4">
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