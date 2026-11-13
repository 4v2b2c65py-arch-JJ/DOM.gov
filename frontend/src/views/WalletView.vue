/**
 * Wallet / Banking View - Cédula identity + Dominican bank accounts
 */

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import api from '@/api/client';
import { useAuthStore } from '@/stores/auth';
import {
  CEDULA_MAX_DIGITS,
  cedulaValidationError,
  formatCedula,
  maskCedula,
  normalizeCedula,
} from '@/utils/cedula';

const authStore = useAuthStore();

type BankAccount = {
  id: string;
  bank_code: string;
  bank_name?: string;
  account_number: string;
  account_type?: string;
  nickname?: string;
};

const BANKS = [
  { code: 'BR', name: 'Banreservas' },
  { code: 'BP', name: 'Banco Popular Dominicano' },
  { code: 'BHD', name: 'BHD León' },
  { code: 'SC', name: 'Scotiabank' },
  { code: 'BDI', name: 'Banco BDI' },
  { code: 'BSC', name: 'Banco Santa Cruz' },
  { code: 'BC', name: 'Banco Caribe' },
  { code: 'BCI', name: 'Banco Cibao' },
  { code: 'BN', name: 'Banco La Nacional' },
  { code: 'BLVR', name: 'Banco La Vega Real' },
];

const ACCOUNT_TYPES = [
  { value: 'savings', label: 'Ahorros' },
  { value: 'checking', label: 'Corriente' },
  { value: 'payroll', label: 'Nómina' },
];

const cedulaForm = reactive({ cedula: '' });
const accountForm = reactive({
  bank_code: '',
  account_number: '',
  account_type: 'savings',
  nickname: '',
  cedula: '',
});

const accounts = ref<BankAccount[]>([]);
const loading = ref(false);
const loadingAccounts = ref(false);
const error = ref<string | null>(null);
const success = ref<string | null>(null);

type CrossCheck = {
  valid: boolean;
  maskedCedula?: string;
  checks: {
    format: boolean;
    checkDigit: { valid: boolean; expected: number | null; actual: number | null };
    barcode: boolean;
  };
};

const crossForm = reactive({ cedula: '', barcode: '' });
const crossLoading = ref(false);
const crossError = ref<string | null>(null);
const crossResult = ref<CrossCheck | null>(null);
const localAiVerdict = ref<string | null>(null);

const cedulaError = computed(() => cedulaValidationError(cedulaForm.cedula));
const accountCedulaError = computed(() =>
  accountForm.cedula ? cedulaValidationError(accountForm.cedula) : '',
);
const accountNumberValid = computed(() => accountForm.account_number.replace(/\D/g, '').length >= 8);
const canSaveAccount = computed(
  () =>
    !!accountForm.bank_code &&
    accountNumberValid.value &&
    !accountCedulaError.value,
);

function onCedulaInput(event: Event, target: 'cedula' | 'account') {
  const value = formatCedula((event.target as HTMLInputElement).value);
  if (target === 'cedula') cedulaForm.cedula = value;
  else accountForm.cedula = value;
}

function onAccountNumberInput(event: Event) {
  accountForm.account_number = (event.target as HTMLInputElement).value
    .replace(/\D/g, '')
    .slice(0, 20);
}

function bankName(code: string): string {
  return BANKS.find((b) => b.code === code)?.name || code;
}

function typeLabel(value?: string): string {
  return ACCOUNT_TYPES.find((t) => t.value === value)?.label || 'Cuenta';
}

async function loadAccounts() {
  loadingAccounts.value = true;
  try {
    const result = await api.getBankAccounts();
    accounts.value = result.accounts || [];
  } catch {
    accounts.value = [];
  } finally {
    loadingAccounts.value = false;
  }
}

async function verifyCedula() {
  error.value = null;
  success.value = null;

  if (cedulaError.value) {
    error.value = cedulaError.value;
    return;
  }

  loading.value = true;
  try {
    const result = await authStore.verifyCedula(normalizeCedula(cedulaForm.cedula));
    if (!result.success) {
      error.value = result.error || 'No se pudo verificar la cédula.';
      return;
    }
    success.value = 'Cédula verificada. Ya puedes vincular tu cuenta bancaria.';
    accountForm.cedula = cedulaForm.cedula;
  } finally {
    loading.value = false;
  }
}

async function saveAccount() {
  error.value = null;
  success.value = null;

  if (!accountForm.bank_code) {
    error.value = 'Selecciona un banco.';
    return;
  }
  if (!accountNumberValid.value) {
    error.value = 'El número de cuenta debe tener al menos 8 dígitos.';
    return;
  }
  if (accountCedulaError.value) {
    error.value = accountCedulaError.value;
    return;
  }

  loading.value = true;
  try {
    await api.addBankAccount({
      bank_code: accountForm.bank_code,
      account_number: accountForm.account_number,
      account_type: accountForm.account_type,
      nickname: accountForm.nickname || bankName(accountForm.bank_code),
      cedula: accountForm.cedula ? normalizeCedula(accountForm.cedula) : undefined,
    });
    success.value = 'Cuenta bancaria vinculada correctamente.';
    accountForm.account_number = '';
    accountForm.nickname = '';
    await loadAccounts();
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'No se pudo vincular la cuenta.';
  } finally {
    loading.value = false;
  }
}

async function removeAccount(id: string) {
  error.value = null;
  try {
    await api.removeBankAccount(id);
    accounts.value = accounts.value.filter((a) => a.id !== id);
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'No se pudo eliminar la cuenta.';
  }
}

function onBarcodeInput(event: Event) {
  crossForm.barcode = (event.target as HTMLInputElement).value.toUpperCase().replace(/[^A-Z0-9]/g, '');
}

async function runCrossVerification() {
  crossError.value = null;
  crossResult.value = null;
  localAiVerdict.value = null;
  crossLoading.value = true;

  try {
    crossResult.value = (await api.crossVerifyCedula(crossForm.cedula, crossForm.barcode)) as CrossCheck;
  } catch (e: unknown) {
    crossError.value = e instanceof Error ? e.message : 'No se pudo verificar en el servidor.';
  }

  try {
    const local = (await api.localCrossVerifyCedula(crossForm.cedula, crossForm.barcode)) as {
      local_ai?: {
        available?: boolean;
        verdict?: { valid?: boolean; reason?: string };
        error?: string;
      };
    };
    if (local.local_ai?.available && local.local_ai.verdict) {
      const verdict = local.local_ai.verdict;
      localAiVerdict.value = `${verdict.valid ? 'Válida' : 'No válida'} — ${verdict.reason || 'sin detalle'}`;
    } else if (local.local_ai?.error) {
      localAiVerdict.value = 'IA local no disponible';
    }
  } catch {
    localAiVerdict.value = 'IA local no disponible';
  } finally {
    crossLoading.value = false;
  }
}

onMounted(loadAccounts);
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Billetera y Cuenta Bancaria</h1>
      <p class="text-gray-500 dark:text-gray-400">
        Verifica tu cédula y vincula tu cuenta de un banco dominicano para recibir pagos y beneficios.
      </p>
    </div>

    <div v-if="error" class="p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">
      {{ error }}
    </div>
    <div v-if="success" class="p-3 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-lg text-green-700 dark:text-green-400 text-sm">
      {{ success }}
    </div>

    <!-- Cédula verification -->
    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
      <div class="flex items-center gap-2 mb-4">
        <span class="text-2xl">🪪</span>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Identidad con Cédula</h2>
        <span
          v-if="authStore.cedulaVerified"
          class="ml-auto px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full text-xs"
        >Verificada</span>
      </div>

      <div class="grid md:grid-cols-[1fr_auto] gap-3 items-end">
        <div>
          <label for="cedula" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Cédula de identidad
          </label>
          <input
            id="cedula"
            v-model="cedulaForm.cedula"
            type="text"
            inputmode="numeric"
            maxlength="14"
            @input="onCedulaInput($event, 'cedula')"
            :disabled="loading"
            class="w-full px-4 py-3 rounded-lg border bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            :class="cedulaForm.cedula && cedulaError ? 'border-red-400' : 'border-gray-300 dark:border-gray-600'"
            placeholder="001-1234567-8"
          />
          <p v-if="cedulaForm.cedula && cedulaError" class="mt-1 text-sm text-red-600 dark:text-red-400">{{ cedulaError }}</p>
          <p v-else class="mt-1 text-xs text-gray-500 dark:text-gray-400">Entre 11 y 12 dígitos. Los guiones son opcionales.</p>
        </div>
        <button
          @click="verifyCedula"
          :disabled="loading || !!cedulaError"
          class="py-3 px-6 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-semibold rounded-lg transition-colors"
        >
          Verificar
        </button>
      </div>

      <p v-if="authStore.cedula" class="mt-3 text-xs text-gray-500 dark:text-gray-400">
        Cédula almacenada de forma tokenizada: {{ maskCedula(authStore.cedula) }}
      </p>
    </div>

    <!-- Cross verification (server + local AI) -->
    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
      <div class="flex items-center gap-2 mb-4">
        <span class="text-2xl">🔎</span>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Verificación Cruzada</h2>
      </div>
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
        Valida la cédula contra el dígito verificador oficial (Luhn) y el código de barras.
        Si el servicio local está activo, también se consulta el modelo de IA local.
      </p>

      <div class="grid md:grid-cols-2 gap-4">
        <div>
          <label for="crossCedula" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Cédula</label>
          <input
            id="crossCedula"
            v-model="crossForm.cedula"
            type="text"
            inputmode="numeric"
            maxlength="14"
            class="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-indigo-500"
            placeholder="402-0609352-7"
          />
        </div>
        <div>
          <label for="crossBarcode" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Código de barras</label>
          <input
            id="crossBarcode"
            :value="crossForm.barcode"
            type="text"
            maxlength="10"
            @input="onBarcodeInput"
            class="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-indigo-500"
            placeholder="CV01253404"
          />
        </div>
      </div>

      <button
        @click="runCrossVerification"
        :disabled="crossLoading || !crossForm.cedula || !crossForm.barcode"
        class="mt-4 py-3 px-6 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-semibold rounded-lg transition-colors"
      >
        {{ crossLoading ? 'Verificando...' : 'Ejecutar verificación cruzada' }}
      </button>

      <div v-if="crossError" class="mt-4 p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">
        {{ crossError }}
      </div>

      <div v-if="crossResult" class="mt-4 p-4 rounded-lg border" :class="crossResult.valid ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' : 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800'">
        <p class="font-semibold" :class="crossResult.valid ? 'text-green-700 dark:text-green-400' : 'text-yellow-700 dark:text-yellow-400'">
          {{ crossResult.valid ? 'Cédula válida' : 'Cédula no válida' }}
        </p>
        <div class="mt-2 text-sm text-gray-600 dark:text-gray-300 space-y-1">
          <p>Formato (11-12 dígitos): {{ crossResult.checks.format ? 'OK' : 'Error' }}</p>
          <p>
            Dígito verificador: esperado {{ crossResult.checks.checkDigit.expected ?? '—' }},
            recibido {{ crossResult.checks.checkDigit.actual ?? '—' }}
          </p>
          <p>Código de barras: {{ crossResult.checks.barcode ? 'válido' : 'inválido' }}</p>
          <p v-if="localAiVerdict">IA local: {{ localAiVerdict }}</p>
        </div>
      </div>
    </div>

    <!-- Bank account form -->
    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
      <div class="flex items-center gap-2 mb-4">
        <span class="text-2xl">🏦</span>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Vincular Cuenta Bancaria</h2>
      </div>

      <div class="grid md:grid-cols-2 gap-4">
        <div>
          <label for="bank" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Banco</label>
          <select
            id="bank"
            v-model="accountForm.bank_code"
            class="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
          >
            <option value="" disabled>Selecciona un banco</option>
            <option v-for="bank in BANKS" :key="bank.code" :value="bank.code">{{ bank.name }}</option>
          </select>
        </div>

        <div>
          <label for="accountType" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Tipo de cuenta</label>
          <select
            id="accountType"
            v-model="accountForm.account_type"
            class="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
          >
            <option v-for="type in ACCOUNT_TYPES" :key="type.value" :value="type.value">{{ type.label }}</option>
          </select>
        </div>

        <div>
          <label for="accountNumber" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Número de cuenta</label>
          <input
            id="accountNumber"
            :value="accountForm.account_number"
            type="text"
            inputmode="numeric"
            maxlength="20"
            @input="onAccountNumberInput"
            class="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-indigo-500"
            placeholder="Ej: 9600123456"
          />
          <p v-if="accountForm.account_number && !accountNumberValid" class="mt-1 text-sm text-red-600 dark:text-red-400">
            El número de cuenta debe tener al menos 8 dígitos.
          </p>
        </div>

        <div>
          <label for="accountCedula" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Cédula del titular <span class="text-xs text-gray-400">(opcional si ya la verificaste)</span>
          </label>
          <input
            id="accountCedula"
            v-model="accountForm.cedula"
            type="text"
            inputmode="numeric"
            maxlength="14"
            @input="onCedulaInput($event, 'account')"
            class="w-full px-4 py-3 rounded-lg border bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-indigo-500"
            :class="accountForm.cedula && accountCedulaError ? 'border-red-400' : 'border-gray-300 dark:border-gray-600'"
            placeholder="001-1234567-8"
          />
          <p v-if="accountForm.cedula && accountCedulaError" class="mt-1 text-sm text-red-600 dark:text-red-400">{{ accountCedulaError }}</p>
        </div>

        <div class="md:col-span-2">
          <label for="nickname" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Alias de la cuenta <span class="text-xs text-gray-400">(opcional)</span>
          </label>
          <input
            id="nickname"
            v-model="accountForm.nickname"
            type="text"
            maxlength="100"
            class="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-indigo-500"
            placeholder="Ej: Cuenta principal"
          />
        </div>
      </div>

      <button
        @click="saveAccount"
        :disabled="loading || !canSaveAccount"
        class="mt-4 w-full md:w-auto py-3 px-6 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-semibold rounded-lg transition-colors"
      >
        {{ loading ? 'Vinculando...' : 'Vincular cuenta' }}
      </button>
    </div>

    <!-- Saved accounts -->
    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Cuentas vinculadas</h2>

      <div v-if="loadingAccounts" class="text-sm text-gray-500 dark:text-gray-400">Cargando cuentas...</div>
      <div v-else-if="accounts.length === 0" class="text-sm text-gray-500 dark:text-gray-400">
        Aún no has vinculado una cuenta bancaria.
      </div>
      <ul v-else class="divide-y divide-gray-200 dark:divide-gray-700">
        <li v-for="account in accounts" :key="account.id" class="flex items-center justify-between py-3">
          <div>
            <p class="font-medium text-gray-900 dark:text-white">{{ account.bank_name || bankName(account.bank_code) }}</p>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              {{ typeLabel(account.account_type) }} · ••••{{ account.account_number.slice(-4) }}
              <span v-if="account.nickname"> · {{ account.nickname }}</span>
            </p>
          </div>
          <button
            @click="removeAccount(account.id)"
            class="text-sm text-red-600 hover:text-red-500"
          >
            Eliminar
          </button>
        </li>
      </ul>
    </div>

    <p class="text-xs text-gray-500 dark:text-gray-400">
      Los datos bancarios se tokenizan y nunca se almacenan en texto plano. Cédula: {{ CEDULA_MAX_DIGITS }} dígitos máximo.
    </p>
  </div>
</template>