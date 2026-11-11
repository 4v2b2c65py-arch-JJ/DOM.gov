/**
 * Placeholder Views - Coming Soon Pages
 */

// Quests View
export default {
  name: 'QuestsView',
  template: `
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
  `
}

// Veeduria View
export default {
  name: 'VeeduriaView',
  template: `
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
  `
}

// Governance View
export default {
  name: 'GovernanceView',
  template: `
    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Gobernanza Algorítmica</h1>
          <p class="text-gray-500 dark:text-gray-400">Consenso multi-IA anti-facción con FGA entidad legal</p>
        </div>
        <span class="px-3 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 rounded-full text-sm">Próximamente</span>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 text-center">
        <span class="text-4xl block mb-3">⚖️</span>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Funcionalidad en desarrollo</h3>
        <p class="text-gray-500 dark:text-gray-400 mb-4">
          5 familias de modelos (Constitucional, Económico, Social, Seguridad, Arbitraje),
          validación adversarial, firmas umbral FROST, circuit breakers, monitor de equidad,
          auditoría inmutable anclada a Corte Suprema, UN OICT, ICC, Bitcoin, Ethereum, Polygon.
        </p>
      </div>
    </div>
  `
}

// Wallet View
export default {
  name: 'WalletView',
  template: `
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
  `
}

// Identity View
export default {
  name: 'IdentityView',
  template: `
    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Identidad Progresiva</h1>
          <p class="text-gray-500 dark:text-gray-400">6 niveles - Anónimo → Soberano. Cada nivel desbloquea capacidades</p>
        </div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="level in 6" :key="level" :class="['p-4 rounded-lg border', level-1 === authStore.identityLevel ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20' : 'border-gray-200 dark:border-gray-700']">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-2xl">{{ ['👤','✉️','🏆','🔐','⭐','👑'][level-1] }}</span>
              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white">Nivel {{ level-1 }}</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">{{ ['Anónimo','Email Verificado','Méritos Vinculados','Biométrico','Confiable','Autorizado/Soeberano'][level-1] }}</p>
              </div>
            </div>
            <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <div v-for="cap in getCapabilities(level-1)" :key="cap">✓ {{ cap }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  setup() {
    const authStore = useAuthStore()
    const getCapabilities = (level: number) => {
      const caps = {
        0: ['Navegación anónima', 'Info pública'],
        1: ['Notificaciones básicas', 'Pre-check aeropuerto', 'Email verificado'],
        2: ['Acumular méritos', 'Selecting Front', 'Quests', 'Veeduría', 'Viajero confiable'],
        3: ['Autenticación biométrica', 'eGate aeropuerto', 'Votación gobernanza', 'Consenso multi-IA'],
        4: ['VIP aeropuerto', 'Oficial dedicado', 'Supervisión FGA', 'Propuesta políticas', 'Asignación presupuesto'],
        5: ['Protocolo estado', 'Inmunidad procesal', 'Acción constitucional', 'Avión gubernamental', 'Escolta'],
      }
      return caps[level as keyof typeof caps] || []
    }
    return { authStore, getCapabilities }
  }
}

// Notifications View
export default {
  name: 'NotificationsView',
  template: `
    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Notificaciones</h1>
          <p class="text-gray-500 dark:text-gray-400">Méritos, pagos, quests, veedurías, gobernanza, identidad</p>
        </div>
        <span class="px-3 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 rounded-full text-sm">Próximamente</span>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 text-center">
        <span class="text-4xl block mb-3">🔔</span>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Funcionalidad en desarrollo</h3>
        <p class="text-gray-500 dark:text-gray-400">
          Centro de notificaciones multi-canal (WhatsApp, SMS, Push, USSD, Email),
          preferencias por categoría, horas de silencio, digest diario, tiempo real via WebSocket.
        </p>
      </div>
    </div>
  `
}

// Settings View
export default {
  name: 'SettingsView',
  template: `
    <div class="space-y-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Configuración</h1>
        <p class="text-gray-500 dark:text-gray-400">Cuenta, notificaciones, privacidad, seguridad</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 space-y-6">
        <div>
          <h3 class="font-semibold text-gray-900 dark:text-white mb-4">Cuenta</h3>
          <div class="space-y-3">
            <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <div><p class="font-medium">Email</p><p class="text-sm text-gray-500">{{ authStore.user?.email }}</p></div>
              <span class="px-2 py-1 text-xs bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 rounded">Verificado</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <div><p class="font-medium">Nivel de Identidad</p><p class="text-sm text-gray-500">Nivel {{ authStore.identityLevel }}/5</p></div>
              <router-link to="/identity" class="px-3 py-1 text-sm bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400 rounded">Subir Nivel</router-link>
            </div>
          </div>
        </div>
        <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
          <h3 class="font-semibold text-gray-900 dark:text-white mb-4">Preferencias de Notificaciones</h3>
          <div class="grid md:grid-cols-2 gap-3">
            <label v-for="cat in notificationCategories" :key="cat" class="flex items-center gap-2 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg cursor-pointer">
              <input type="checkbox" :checked="true" class="w-4 h-4 text-indigo-600 rounded" />
              <span class="text-sm text-gray-700 dark:text-gray-300 capitalize">{{ cat }}</span>
            </label>
          </div>
        </div>
        <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
          <button @click="authStore.logout" class="w-full py-2 px-4 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">Cerrar Sesión</button>
        </div>
      </div>
    </div>
  `,
  setup() {
    const authStore = useAuthStore()
    const notificationCategories = ['méritos', 'pagos', 'selecting_front', 'quests', 'veeduría', 'entregas', 'ayuda_mutua', 'convivencia', 'gobernanza', 'identidad', 'sistema']
    return { authStore, notificationCategories }
  }
}

// NotFound View
export default {
  name: 'NotFoundView',
  template: `
    <div class="min-h-[60vh] flex items-center justify-center text-center px-4">
      <div>
        <span class="text-6xl block mb-4">🏝️</span>
        <h1 class="text-4xl font-bold text-gray-900 dark:text-white mb-2">404 - No Encontrado</h1>
        <p class="text-gray-500 dark:text-gray-400 mb-8 max-w-md mx-auto">La página que buscas no existe o ha sido movida. Puede que necesites subir tu nivel de identidad para acceder.</p>
        <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
          <router-link to="/" class="px-6 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors">Ir al Inicio</router-link>
          <router-link to="/dashboard" class="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors">Dashboard</router-link>
        </div>
      </div>
    </div>
  `
}