/**
 * Footer Component
 */

<script setup lang="ts">
import { onMounted } from 'vue';

const currentYear = new Date().getFullYear();
const version = import.meta.env.VITE_APP_VERSION || '1.0.0';

const footerLinks = {
  platform: [
    { label: 'Dashboard', to: '/dashboard' },
    { label: 'Méritos', to: '/merits' },
    { label: 'Selecting Front', to: '/selecting-front' },
    { label: 'Quests', to: '/quests' },
    { label: 'Veeduría', to: '/veeduria' },
    { label: 'Gobernanza', to: '/governance' },
  ],
  services: [
    { label: 'Easy Pass Aeropuerto', to: '/airport' },
    { label: 'Billetera Digital', to: '/wallet' },
    { label: 'Identidad Progresiva', to: '/identity' },
    { label: 'Notificaciones', to: '/notifications' },
  ],
  governance: [
    { label: 'Modelo CARACOL', to: '#', external: true },
    { label: 'Consenso Multi-IA', to: '#', external: true },
    { label: 'FGA - Fundación', to: '#', external: true },
    { label: 'Auditoría Inmutable', to: '#', external: true },
    { label: 'Anti-Facción', to: '#', external: true },
  ],
  legal: [
    { label: 'Términos de Servicio', to: '#', external: true },
    { label: 'Política de Privacidad', to: '#', external: true },
    { label: 'Cookies', to: '#', external: true },
    { label: 'Accesibilidad', to: '#', external: true },
  ],
};

const socialLinks = [
  { name: 'GitHub', href: 'https://github.com/4v2b2c65py-arch-JJ/DOM.gov', icon: '🐙' },
  { name: 'Twitter', href: '#', icon: '🐦' },
  { name: 'Transparencia', href: '#', icon: '📊' },
];
</script>

<template>
  <footer class="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-auto">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-8">
        <!-- Brand -->
        <div class="col-span-2 lg:col-span-1">
          <div class="flex items-center space-x-2 mb-4">
            <span class="text-2xl">🇩🇴</span>
            <span class="text-xl font-bold text-gray-900 dark:text-white">DOM.gov</span>
          </div>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
            Plataforma de gobernanza algorítmica para República Dominicana.
            Implementando Society 5.0 con adaptación local.
          </p>
          <div class="flex space-x-4">
            <a v-for="social in socialLinks" :key="social.name" :href="social.href" target="_blank" rel="noopener noreferrer"
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors text-sm"
              :aria-label="social.name"
            >
              {{ social.icon }}
            </a>
          </div>
        </div>

        <!-- Platform -->
        <div>
          <h3 class="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider mb-4">Plataforma</h3>
          <ul class="space-y-2">
            <li v-for="link in footerLinks.platform" :key="link.to">
              <router-link :to="link.to" class="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
                {{ link.label }}
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Services -->
        <div>
          <h3 class="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider mb-4">Servicios</h3>
          <ul class="space-y-2">
            <li v-for="link in footerLinks.services" :key="link.to">
              <router-link :to="link.to" class="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
                {{ link.label }}
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Governance -->
        <div>
          <h3 class="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider mb-4">Gobernanza</h3>
          <ul class="space-y-2">
            <li v-for="link in footerLinks.governance" :key="link.label">
              <a v-if="link.external" :href="link.to" target="_blank" rel="noopener noreferrer"
                class="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
              >
                {{ link.label }}
              </a>
              <router-link v-else :to="link.to" class="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
                {{ link.label }}
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Legal -->
        <div>
          <h3 class="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider mb-4">Legal</h3>
          <ul class="space-y-2">
            <li v-for="link in footerLinks.legal" :key="link.label">
              <a v-if="link.external" :href="link.to" target="_blank" rel="noopener noreferrer"
                class="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
              >
                {{ link.label }}
              </a>
              <router-link v-else :to="link.to" class="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
                {{ link.label }}
              </router-link>
            </li>
          </ul>
        </div>
      </div>

      <!-- Bottom Bar -->
      <div class="mt-12 pt-8 border-t border-gray-200 dark:border-gray-700">
        <div class="flex flex-col md:flex-row items-center justify-between gap-4">
          <p class="text-sm text-gray-500 dark:text-gray-400">
            © {{ currentYear }} DOM.gov - GobernanzaRD. Todos los derechos reservados.
          </p>
          <div class="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
            <span>v{{ version }}</span>
            <span class="px-2 py-0.5 bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 rounded-full text-xs">
              Society 5.0 Compliant
            </span>
            <span class="px-2 py-0.5 bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 rounded-full text-xs">
              FGA Audited
            </span>
            <span class="px-2 py-0.5 bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300 rounded-full text-xs">
              Anti-Facción
            </span>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>