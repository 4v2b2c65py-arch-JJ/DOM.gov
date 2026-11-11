/**
 * Home View - Landing Page
 */

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const features = [
  {
    icon: '🏆',
    title: 'Economía de Méritos',
    description: 'Acumula méritos participando en Quests, Veedurías y ayuda mutua. Cánjealos en el Selecting Front por utilidades, vivienda y electrodomésticos.',
    level: 2,
  },
  {
    icon: '✈️',
    title: 'Easy Pass Aeropuerto',
    description: '6 niveles de autorización (Estándar → Soberano) con QR/NFC offline, eGates biométricos en SDQ, PUJ, STI. Solo pasaporte y listo.',
    level: 1,
  },
  {
    icon: '📋',
    title: 'Veeduría Ciudadana',
    description: 'Reporta problemas en tu comunidad. Validación comunitaria, escalamiento automático a autoridades, méritos por participación cívica.',
    level: 2,
  },
  {
    icon: '🚶',
    title: 'Quests Territoriales',
    description: 'Visitas domiciliarias verificadas con GPS + referencias comunitarias (colmado, iglesia, escuela). Pre-verificación Quest, entrega sin dirección.',
    level: 2,
  },
  {
    icon: '⚖️',
    title: 'Consenso Multi-IA',
    description: '5 familias de modelos (Constitucional, Económico, Social, Seguridad, Arbitraje) con validación adversarial. FGA entidad legal independiente.',
    level: 3,
  },
  {
    icon: '🔗',
    title: 'Identidad Progresiva',
    description: 'Nivel 0 Anónimo → Nivel 5 Soberano. Cada nivel desbloquea capacidades: pagos auto-llenados, votación, protocolo de estado.',
    level: 0,
  },
];

const stats = [
  { value: '5', label: 'Familias de Modelos IA' },
  { value: '6', label: 'Niveles de Identidad' },
  { value: '8', label: 'APIs Gubernamentales' },
  { value: '5', label: 'Aeropuertos DR' },
  { value: '10', label: 'Bancos Soportados' },
  { value: '3', label: 'Operadores Móviles' },
];

function navigateToLogin() {
  router.push('/login');
}

function navigateToRegister() {
  router.push('/login?register=true');
}
</script>

<template>
  <div class="min-h-screen">
    <!-- Hero Section -->
    <section class="relative bg-gradient-to-br from-blue-600 via-indigo-700 to-purple-800 text-white overflow-hidden">
      <div class="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.03"%3E%3Cpath d="M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 36v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 6V0H4v4H0v2h4v4h2V6h4V4H6z"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-50" />
      
      <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32">
        <div class="text-center max-w-3xl mx-auto">
          <div class="inline-flex items-center px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 mb-6">
            <span class="text-sm font-medium">🇩🇴 República Dominicana</span>
            <span class="mx-2 text-white/50">|</span>
            <span class="text-sm font-medium">Society 5.0 / Agile Governance</span>
          </div>
          
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6 leading-tight">
            Gobernanza que
            <span class="block text-yellow-300">funciona para ti</span>
          </h1>
          
          <p class="text-xl sm:text-2xl text-white/90 mb-8 max-w-2xl mx-auto leading-relaxed">
            Plataforma ciudadana con identidad progresiva, economía de méritos, consenso multi-IA anti-facción
            y Easy Pass aeroportuario. Tu pasaporte, tu identidad, tu voz.
          </p>
          
          <div class="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
            <button
              @click="navigateToRegister"
              class="w-full sm:w-auto px-8 py-4 text-lg font-semibold text-indigo-700 bg-white rounded-xl hover:bg-gray-100 transition-colors shadow-lg"
            >
              Crear Cuenta Gratis
            </button>
            <button
              @click="navigateToLogin"
              class="w-full sm:w-auto px-8 py-4 text-lg font-semibold text-white bg-white/10 backdrop-blur-sm border border-white/30 rounded-xl hover:bg-white/20 transition-colors"
            >
              Iniciar Sesión
            </button>
          </div>

          <!-- Trust Indicators -->
          <div class="flex flex-wrap items-center justify-center gap-6 text-sm text-white/70">
            <span class="flex items-center gap-1"><span class="text-green-300">✓</span> FGA Audited</span>
            <span class="flex items-center gap-1"><span class="text-green-300">✓</span> Anti-Facción</span>
            <span class="flex items-center gap-1"><span class="text-green-300">✓</span> Auditoría Inmutable</span>
            <span class="flex items-center gap-1"><span class="text-green-300">✓</span> 8 APIs Gov</span>
            <span class="flex items-center gap-1"><span class="text-green-300">✓</span> Modelos Locales</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Bar -->
    <section class="bg-gray-50 dark:bg-gray-900 py-12 border-b border-gray-200 dark:border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8">
          <div v-for="stat in stats" :key="stat.label" class="text-center">
            <div class="text-3xl sm:text-4xl font-bold text-indigo-600 dark:text-indigo-400">{{ stat.value }}</div>
            <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section class="py-20 bg-white dark:bg-gray-900">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Todo lo que necesitas para participar
          </h2>
          <p class="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Cada función está diseñada para la realidad dominicana: sin direcciones postales,
            con operadores locales, y gobernanza que rinde cuentas.
          </p>
        </div>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div v-for="feature in features" :key="feature.title" class="group p-6 bg-gray-50 dark:bg-gray-800/50 rounded-2xl border border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-700 transition-all duration-300 hover:shadow-xl">
            <div class="text-4xl mb-4" aria-hidden="true">{{ feature.icon }}</div>
            <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">{{ feature.title }}</h3>
            <p class="text-gray-600 dark:text-gray-400 mb-4">{{ feature.description }}</p>
            <div class="flex items-center gap-2 text-sm">
              <span class="px-2 py-1 rounded-full"
                :class="feature.level >= 3 ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400' : 
                       feature.level >= 2 ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' :
                       feature.level >= 1 ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' :
                       'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'">
                Nivel {{ feature.level }}+
              </span>
              <span class="text-gray-500 dark:text-gray-500">requerido</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section class="py-20 bg-gray-50 dark:bg-gray-900">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Cómo funciona en 3 pasos
          </h2>
        </div>

        <div class="grid md:grid-cols-3 gap-8">
          <div class="relative">
            <div class="absolute left-1/2 top-0 -translate-x-1/2 w-12 h-12 rounded-full bg-indigo-600 flex items-center justify-center text-white text-2xl font-bold z-10">1</div>
            <div class="pt-8 p-6 bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700">
              <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-3">Crea tu identidad</h3>
              <p class="text-gray-600 dark:text-gray-400">
                Magic link por email → Nivel 1 verificado. Sube a Nivel 2 vinculando méritos, Nivel 3 con biométrico.
                Cada nivel desbloquea más capacidades.
              </p>
            </div>
          </div>

          <div class="relative">
            <div class="absolute left-1/2 top-0 -translate-x-1/2 w-12 h-12 rounded-full bg-indigo-600 flex items-center justify-center text-white text-2xl font-bold z-10">2</div>
            <div class="pt-8 p-6 bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700">
              <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-3">Participa y gana</h3>
              <p class="text-gray-600 dark:text-gray-400">
                Haz Quests, presenta Veedurías, ayuda a vecinos. Gana méritos → cámbialos por electricidad, agua, electrodomésticos, vivienda.
              </p>
            </div>
          </div>

          <div class="relative">
            <div class="absolute left-1/2 top-0 -translate-x-1/2 w-12 h-12 rounded-full bg-indigo-600 flex items-center justify-center text-white text-2xl font-bold z-10">3</div>
            <div class="pt-8 p-6 bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700">
              <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-3">Gobierna y viaja</h3>
              <p class="text-gray-600 dark:text-gray-400">
                Vota en consensos multi-IA, audita decisiones en blockchain. Easy Pass: solo pasaporte en aeropuerto,
                QR/NFC offline, eGates biométricos según tu nivel.
              </p>
            </div>
          </div>
        </div>

        <!-- Connecting lines -->
        <div class="hidden md:block absolute left-1/2 top-16 w-full h-0.5 bg-gradient-to-r from-transparent via-indigo-300 to-transparent -translate-x-1/2" style="width: 66%; left: 17%;" />
      </div>
    </section>

    <!-- CTA -->
    <section class="py-20 bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 text-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 class="text-3xl sm:text-4xl font-bold mb-6">Listo para participar</h2>
        <p class="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
          Únete a miles de dominicanos construyendo una gobernanza transparente, meritocrática y tecnológica.
        </p>
        <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button
            @click="navigateToRegister"
            class="w-full sm:w-auto px-8 py-4 text-lg font-semibold text-indigo-700 bg-white rounded-xl hover:bg-gray-100 transition-colors shadow-lg"
          >
            Empezar Ahora - Gratis
          </button>
          <a href="https://github.com/4v2b2c65py-arch-JJ/DOM.gov" target="_blank" rel="noopener noreferrer"
            class="w-full sm:w-auto px-8 py-4 text-lg font-semibold text-white bg-white/10 backdrop-blur-sm border border-white/30 rounded-xl hover:bg-white/20 transition-colors"
          >
            Ver Código en GitHub
          </a>
        </div>
      </div>
    </section>
  </div>
</template>