/**
 * Airport Easy Pass View - Clearance Management
 */

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { useAirportStore } from '@/stores/airport';
import { useAuthStore } from '@/stores/auth';

const airportStore = useAirportStore();
const authStore = useAuthStore();

const activeTab = ref<'my' | 'request' | 'verify'>('my');
const requestForm = ref({
  airport_code: '',
  flight_number: '',
  departure_time: '',
  destination: '',
  passport_number: '',
  visa_required: false,
  travel_purpose: 'turismo',
});

const submitting = ref(false);
const verifying = ref(false);
const verifyQR = ref('');

const airports = computed(() => airportStore.airports);
const nextLevel = computed(() => airportStore.getGradeForLevel(authStore.identityLevel + 1));

onMounted(async () => {
  await Promise.all([
    airportStore.fetchAirports(),
    airportStore.fetchGrades(),
    airportStore.fetchMyClearances(),
  ]);
});

function formatDateTime(date: Date): string {
  return date.toISOString().slice(0, 16);
}

async function handleRequestClearance() {
  if (!requestForm.value.airport_code || !requestForm.value.flight_number || !requestForm.value.departure_time || !requestForm.value.destination || !requestForm.value.passport_number) {
    alert('Completa todos los campos requeridos');
    return;
  }
  submitting.value = true;
  try {
    const result = await airportStore.requestClearance(requestForm.value);
    if (result.success) {
      activeTab.value = 'my';
      requestForm.value = { airport_code: '', flight_number: '', departure_time: '', destination: '', passport_number: '', visa_required: false, travel_purpose: 'turismo' };
      alert('¡Easy Pass solicitado! Recibirás notificación con el QR code.');
    } else {
      alert(`Error: ${result.error}`);
    }
  } finally {
    submitting.value = false;
  }
}

async function handleVerifyQR() {
  if (!verifyQR.value.trim()) return;
  verifying.value = true;
  try {
    const result = await airportStore.verifyQRCode(verifyQR.value.trim(), '');
    if (result.valid) {
      alert(`✅ QR Válido\n\nVuelo: ${result.clearance.flight_number}\nGrado: ${result.clearance.label}\nPuerta automática: ${result.clearance.auto_gate ? 'Sí' : 'No'}\nPuerta biométrica: ${result.clearance.biometric_gate ? 'Sí' : 'No'}`);
    } else {
      alert(`❌ QR Inválido: ${result.reason}`);
    }
  } finally {
    verifying.value = false;
  }
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Easy Pass Aeropuerto</h1>
        <p class="text-gray-500 dark:text-gray-400">Autorización rápida solo con pasaporte - 6 niveles de acceso</p>
      </div>
      <div class="flex items-center gap-3">
        <div class="px-4 py-2 bg-indigo-50 dark:bg-indigo-900/30 rounded-xl border border-indigo-200 dark:border-indigo-800">
          <p class="text-xs text-indigo-700 dark:text-indigo-400">Tu nivel actual</p>
          <p class="font-bold text-indigo-800 dark:text-indigo-300">{{ authStore.identityLevel }}/5</p>
        </div>
        <div v-if="nextLevel" class="px-4 py-2 bg-yellow-50 dark:bg-yellow-900/30 rounded-xl border border-yellow-200 dark:border-yellow-800">
          <p class="text-xs text-yellow-700 dark:text-yellow-400">Próximo nivel</p>
          <p class="font-bold text-yellow-800 dark:text-yellow-300">{{ nextLevel.label }} ({{ nextLevel.identity_level }})</p>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="flex gap-1" aria-label="Pestañas de aeropuerto">
        <button @click="activeTab = 'my'" :class="['px-4 py-3 text-sm font-medium rounded-t-lg transition-colors', activeTab === 'my' ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600' : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200']">Mis Autorizaciones</button>
        <button @click="activeTab = 'request'" :class="['px-4 py-3 text-sm font-medium rounded-t-lg transition-colors', activeTab === 'request' ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600' : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200']">Solicitar Nuevo</button>
        <button @click="activeTab = 'verify'" :class="['px-4 py-3 text-sm font-medium rounded-t-lg transition-colors', activeTab === 'verify' ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600' : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200']">Verificar QR</button>
      </nav>
    </div>

    <!-- My Clearances Tab -->
    <div v-if="activeTab === 'my'" class="space-y-4">
      <div v-if="airportStore.activeClearances.length > 0" class="space-y-4">
        <div v-for="clearance in airportStore.activeClearances" :key="clearance.id" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div class="p-4 bg-gradient-to-r from-indigo-600 to-blue-600 text-white">
            <div class="flex items-center justify-between flex-wrap gap-2">
              <div>
                <h3 class="font-semibold">{{ clearance.flight_number }} · {{ clearance.airport_code }}</h3>
                <p class="text-white/80 text-sm">{{ clearance.airport_name }} → {{ clearance.destination }}</p>
              </div>
              <span class="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-sm font-medium">{{ clearance.label }}</span>
            </div>
          </div>
          <div class="p-4 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p class="text-xs text-gray-500 dark:text-gray-400">Salida</p>
              <p class="font-medium text-gray-900 dark:text-white">{{ new Date(clearance.departure_time).toLocaleString('es-DO') }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500 dark:text-gray-400">Tiempo Estimado</p>
              <p class="font-medium text-gray-900 dark:text-white">{{ clearance.estimated_time }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500 dark:text-gray-400">Puerta Auto</p>
              <p class="font-medium text-gray-900 dark:text-white">{{ clearance.auto_gate ? '✅ Sí' : '❌ No' }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500 dark:text-gray-400">Puerta Bio</p>
              <p class="font-medium text-gray-900 dark:text-white">{{ clearance.biometric_gate ? '✅ Sí' : '❌ No' }}</p>
            </div>
          </div>
          <div class="px-4 py-3 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-200 dark:border-gray-600 flex flex-wrap gap-2">
            <router-link :to="`/airport/clearance/${clearance.id}`" class="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors">Ver QR</router-link>
            <button class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors">Check-in</button>
          </div>
        </div>
      </div>

      <div v-if="airportStore.pastClearances.length > 0" class="border-t border-gray-200 dark:border-gray-700 pt-4">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">Historial</h3>
        <div class="space-y-2 max-h-64 overflow-y-auto">
          <div v-for="clearance in airportStore.pastClearances.slice(0, 10)" :key="clearance.id" class="p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <span class="text-xl">{{ clearance.status === 'completed' ? '✅' : clearance.status === 'expired' ? '⏰' : '❌' }}</span>
              <div>
                <p class="font-medium text-gray-900 dark:text-white">{{ clearance.flight_number }} · {{ clearance.airport_code }}</p>
                <p class="text-sm text-gray-500 dark:text-gray-400">{{ new Date(clearance.departure_time).toLocaleDateString('es-DO') }}</p>
              </div>
            </div>
            <span class="px-2 py-1 text-xs rounded-full"
              :class="clearance.status === 'completed' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' :
                       clearance.status === 'expired' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400' :
                       'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'">
              {{ clearance.status }}
            </span>
          </div>
        </div>
      </div>

      <div v-if="airportStore.activeClearances.length === 0 && airportStore.pastClearances.length === 0" class="text-center py-12">
        <span class="text-4xl block mb-2">✈️</span>
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-1">No hay autorizaciones activas</h3>
        <p class="text-gray-500 dark:text-gray-400 mb-4">Solicita tu Easy Pass para el próximo vuelo</p>
        <button @click="activeTab = 'request'" class="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">Solicitar Ahora</button>
      </div>
    </div>

    <!-- Request Tab -->
    <div v-if="activeTab === 'request'" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 max-w-2xl">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Solicitar Easy Pass</h3>
      <form @submit.prevent="handleRequestClearance" class="space-y-4">
        <div class="grid sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Aeropuerto *</label>
            <select v-model="requestForm.airport_code" class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500" required>
              <option value="">Selecciona...</option>
              <option v-for="apt in airports" :key="apt.code" :value="apt.code">{{ apt.code }} - {{ apt.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Vuelo *</label>
            <input v-model="requestForm.flight_number" type="text" placeholder="ej: AA1234" class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500" required />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Fecha y Hora de Salida *</label>
          <input v-model="requestForm.departure_time" type="datetime-local" :min="formatDateTime(new Date())" class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500" required />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Destino *</label>
          <input v-model="requestForm.destination" type="text" placeholder="Ciudad, País" class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500" required />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Pasaporte *</label>
          <input v-model="requestForm.passport_number" type="text" placeholder="Número de pasaporte" class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500" required />
        </div>
        <div class="flex items-center gap-2">
          <input v-model="requestForm.visa_required" type="checkbox" id="visa" class="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500" />
          <label for="visa" class="text-sm text-gray-700 dark:text-gray-300">Requiere visa para el destino</label>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Propósito del Viaje</label>
          <select v-model="requestForm.travel_purpose" class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500">
            <option value="turismo">Turismo</option>
            <option value="negocios">Negocios</option>
            <option value="gobierno">Gobierno/Oficial</option>
            <option value="estudio">Estudio</option>
            <option value="medico">Médico</option>
            <option value="familiar">Familiar</option>
          </select>
        </div>
        <button type="submit" :disabled="submitting" class="w-full py-3 px-4 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:bg-indigo-400 transition-colors">
          {{ submitting ? 'Solicitando...' : 'Solicitar Easy Pass' }}
        </button>
      </form>
    </div>

    <!-- Verify Tab -->
    <div v-if="activeTab === 'verify'" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 max-w-xl">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Verificar QR / NFC</h3>
      <p class="text-gray-500 dark:text-gray-400 mb-6">Escanea o pega el código QR del Easy Pass para verificar su validez</p>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Código QR (formato GOB-AIR:...)</label>
          <textarea v-model="verifyQR" rows="3" class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 font-mono text-sm" placeholder="GOB-AIR:eyJjaWQiOiI..." />
        </div>
        <button @click="handleVerifyQR" :disabled="verifying || !verifyQR.trim()" class="w-full py-3 px-4 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:bg-indigo-400 transition-colors">
          {{ verifying ? 'Verificando...' : 'Verificar QR' }}
        </button>
      </div>
    </div>

    <!-- Grades Info -->
    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Niveles de Autorización (Grados)</h3>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700">
              <th class="pb-2">Nivel</th>
              <th class="pb-2">Grado</th>
              <th class="pb-2">Carriles</th>
              <th class="pb-2">Puertas</th>
              <th class="pb-2">Tiempo</th>
              <th class="pb-2">Beneficios</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="grade in airportStore.grades" :key="grade.identity_level" :class="grade.identity_level === authStore.identityLevel ? 'bg-indigo-50 dark:bg-indigo-900/20' : ''">
              <td class="py-2 font-medium">{{ grade.identity_level }}</td>
              <td class="py-2">{{ grade.label }}</td>
              <td class="py-2">{{ grade.lanes.join(', ') }}</td>
              <td class="py-2">
                <span v-if="grade.auto_gate" class="mr-2 text-green-600 dark:text-green-400">✅ Auto</span>
                <span v-if="grade.biometric_gate" class="mr-2 text-blue-600 dark:text-blue-400">🔐 Bio</span>
                <span v-if="grade.vip_lane" class="mr-2 text-purple-600 dark:text-purple-400">⭐ VIP</span>
                <span v-if="grade.sovereign_protocol" class="text-red-600 dark:text-red-400">👑 Soberano</span>
              </td>
              <td class="py-2">{{ grade.estimated_time }}</td>
              <td class="py-2 text-gray-500 dark:text-gray-400">{{ grade.benefits.slice(0, 3).join(', ') }}{{ grade.benefits.length > 3 ? '...' : '' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>