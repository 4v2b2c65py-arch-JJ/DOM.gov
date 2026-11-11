/**
 * Airport Store - Easy Pass clearance management
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from '@/api/client';

interface Clearance {
  id: string;
  user_id: string;
  grade: string;
  label: string;
  airport_code: string;
  airport_name: string;
  flight_number: string;
  departure_time: number;
  destination: string;
  passport_number: string;
  status: 'active' | 'completed' | 'expired' | 'cancelled';
  benefits: string[];
  lanes: string[];
  auto_gate: boolean;
  biometric_gate: boolean;
  vip_lane: boolean;
  dedicated_officer: boolean;
  sovereign_protocol: boolean;
  estimated_time: string;
  qr_code: string;
  nfc_token: string;
  checkpoints: {
    checkin: Checkpoint;
    security: Checkpoint;
    immigration: Checkpoint;
    boarding: Checkpoint;
  };
  created_at: number;
}

interface Checkpoint {
  status: 'pending' | 'completed';
  location?: string;
  completed_at?: number;
  scanner_id?: string;
  method?: string;
}

interface Airport {
  code: string;
  name: string;
  city: string;
  egates: number;
  biometric_kiosks: number;
  trusted_lanes: number;
  vip_lanes: number;
  sovereign_lane: number;
}

interface ClearanceGrade {
  identity_level: number;
  grade: string;
  label: string;
  lanes: string[];
  benefits: string[];
  auto_gate: boolean;
  biometric_gate: boolean;
  vip_lane: boolean;
  dedicated_officer: boolean;
  sovereign_protocol: boolean;
  estimated_time: string;
}

export const useAirportStore = defineStore('airport', () => {
  const clearances = ref<Clearance[]>([]);
  const airports = ref<Airport[]>([]);
  const grades = ref<ClearanceGrade[]>([]);
  const activeClearance = ref<Clearance | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const activeClearances = computed(() => clearances.value.filter(c => c.status === 'active'));
  const pastClearances = computed(() => clearances.value.filter(c => c.status !== 'active'));
  const nextFlight = computed(() => {
    const active = activeClearances.value;
    if (!active.length) return null;
    return active.sort((a, b) => a.departure_time - b.departure_time)[0];
  });

  async function fetchAirports() {
    try {
      const data = await api.getAirports();
      airports.value = data.airports || data;
    } catch (e: any) {
      error.value = e.message;
    }
  }

  async function fetchGrades() {
    try {
      const data = await api.getGrades();
      grades.value = data.grades || data;
    } catch (e: any) {
      error.value = e.message;
    }
  }

  async function requestClearance(data: {
    airport_code: string;
    flight_number: string;
    departure_time: string;
    destination: string;
    passport_number: string;
    visa_required?: boolean;
    travel_purpose?: string;
  }) {
    loading.value = true;
    error.value = null;
    try {
      const clearance = await api.requestAirportClearance(data);
      clearances.value.unshift(clearance);
      activeClearance.value = clearance;
      return { success: true, clearance };
    } catch (e: any) {
      error.value = e.message;
      return { success: false, error: e.message };
    } finally {
      loading.value = false;
    }
  }

  async function fetchMyClearances() {
    try {
      const data = await api.getMyClearances();
      clearances.value = data.clearances || data;
      const active = clearances.value.find(c => c.status === 'active');
      if (active) activeClearance.value = active;
    } catch (e: any) {
      error.value = e.message;
    }
  }

  async function processCheckpoint(clearanceId: string, checkpoint: string, scanData: any) {
    try {
      const result = await api.processCheckpoint(clearanceId, checkpoint, scanData);
      const clearance = clearances.value.find(c => c.id === clearanceId);
      if (clearance && result.clearance) {
        Object.assign(clearance, result.clearance);
        if (clearance.id === activeClearance.value?.id) {
          activeClearance.value = clearance;
        }
      }
      return { success: true, ...result };
    } catch (e: any) {
      error.value = e.message;
      return { success: false, error: e.message };
    }
  }

  async function cancelClearance(clearanceId: string, reason: string) {
    try {
      const clearance = await api.cancelClearance(clearanceId, reason);
      const idx = clearances.value.findIndex(c => c.id === clearanceId);
      if (idx >= 0) clearances.value[idx] = clearance;
      if (activeClearance.value?.id === clearanceId) {
        activeClearance.value = null;
      }
      return { success: true };
    } catch (e: any) {
      error.value = e.message;
      return { success: false, error: e.message };
    }
  }

  async function verifyQRCode(qrCode: string, airportCode: string) {
    try {
      const result = await api.verifyQRCode(qrCode, airportCode);
      return result;
    } catch (e: any) {
      error.value = e.message;
      return { valid: false, reason: e.message };
    }
  }

  function setActiveClearance(clearance: Clearance | null) {
    activeClearance.value = clearance;
  }

  function clearError() {
    error.value = null;
  }

  function getGradeForLevel(level: number): ClearanceGrade | undefined {
    return grades.value.find(g => g.identity_level === level);
  }

  function getAirport(code: string): Airport | undefined {
    return airports.value.find(a => a.code === code);
  }

  return {
    clearances,
    airports,
    grades,
    activeClearance,
    loading,
    error,
    activeClearances,
    pastClearances,
    nextFlight,
    fetchAirports,
    fetchGrades,
    requestClearance,
    fetchMyClearances,
    processCheckpoint,
    cancelClearance,
    verifyQRCode,
    setActiveClearance,
    clearError,
    getGradeForLevel,
    getAirport,
  };
});