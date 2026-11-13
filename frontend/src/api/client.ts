/**
 * API Client for DOM.gov Frontend
 * Communicates with Python FastAPI backend and Node.js Telecaster
 */

const API_BASE = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000');
const TELECASTER_BASE = import.meta.env.VITE_TELECASTER_URL || 'http://localhost:3001';

class ApiClient {
  private token: string | null = null;
  private refreshToken: string | null = null;

  constructor() {
    // Load tokens from localStorage
    this.token = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
  }

  setTokens(access: string, refresh: string) {
    this.token = access;
    this.refreshToken = refresh;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
  }

  clearTokens() {
    this.token = null;
    this.refreshToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  private async request<T>(url: string, options: RequestInit = {}): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${API_BASE}${url}`, {
      ...options,
      headers,
      credentials: 'include',
    });

    if (response.status === 401 && this.refreshToken) {
      // Try to refresh token
      const refreshed = await this.refreshAccessToken();
      if (refreshed) {
        // Retry original request
        (headers as Record<string, string>)['Authorization'] = `Bearer ${this.token}`;
        return this.request(url, options);
      }
      // Refresh failed, redirect to login
      this.clearTokens();
      window.location.href = '/login';
      throw new Error('Session expired');
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return response.json();
  }

  private async refreshAccessToken(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE}/api/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: this.refreshToken }),
        credentials: 'include',
      });

      if (!response.ok) return false;

      const data = await response.json();
      this.setTokens(data.access_token, data.refresh_token);
      return true;
    } catch {
      return false;
    }
  }

  // ==================== AUTH ====================

  async requestMagicLink(email: string, deviceFingerprint?: string, cedula?: string) {
    return this.request('/api/auth/magic-link', {
      method: 'POST',
      body: JSON.stringify({ email, device_fingerprint: deviceFingerprint, cedula }),
    });
  }

  async verifyMagicLink(token: string) {
    const data = await this.request<{ access_token: string; refresh_token: string; user: any }>(
      '/api/auth/verify',
      { method: 'POST', body: JSON.stringify({ token }) }
    );
    this.setTokens(data.access_token, data.refresh_token);
    return data.user;
  }

  async getMe() {
    return this.request('/api/users/me');
  }

  async logout() {
    this.clearTokens();
  }

  // ==================== MERITS ====================

  async getMeritBalance() {
    return this.request<{ balance: number; total_earned: number; total_spent: number }>('/api/merits/balance');
  }

  async earnMerits(amount: number, reason: string, metadata?: any) {
    return this.request('/api/merits/earn', {
      method: 'POST',
      body: JSON.stringify({ amount, reason, metadata }),
    });
  }

  async spendMerits(amount: number, item: string, metadata?: any) {
    return this.request('/api/merits/spend', {
      method: 'POST',
      body: JSON.stringify({ amount, item, metadata }),
    });
  }

  async getMeritHistory(limit = 50, offset = 0) {
    return this.request(`/api/merits/history?limit=${limit}&offset=${offset}`);
  }

  // ==================== SELECTING FRONT ====================

  async getSelectingFrontCatalog() {
    return this.request('/api/selecting-front/catalog');
  }

  async placeOrder(itemId: string, quantity = 1) {
    return this.request('/api/selecting-front/order', {
      method: 'POST',
      body: JSON.stringify({ item_id: itemId, quantity }),
    });
  }

  async getOrders(status?: string) {
    return this.request(`/api/selecting-front/orders${status ? `?status=${status}` : ''}`);
  }

  // ==================== PAYMENTS ====================

  async initiatePayment(type: string, amount: number, metadata?: any) {
    return this.request('/api/payments/initiate', {
      method: 'POST',
      body: JSON.stringify({ type, amount, metadata }),
    });
  }

  async confirmPayment(paymentId: string, confirmationToken: string) {
    return this.request('/api/payments/confirm', {
      method: 'POST',
      body: JSON.stringify({ payment_id: paymentId, confirmation_token: confirmationToken }),
    });
  }

  async getPaymentHistory(limit = 20) {
    return this.request(`/api/payments/history?limit=${limit}`);
  }

  // ==================== WALLET ====================

  async getWalletTokens() {
    return this.request('/api/wallet/tokens');
  }

  async addWalletToken(cardData: any) {
    return this.request('/api/wallet/tokens', {
      method: 'POST',
      body: JSON.stringify(cardData),
    });
  }

  async removeWalletToken(tokenId: string) {
    return this.request(`/api/wallet/tokens/${tokenId}`, { method: 'DELETE' });
  }

  // ==================== QUESTS ====================

  async getAssignedQuests() {
    return this.request('/api/quests/assigned');
  }

  async getQuestDetails(questId: string) {
    return this.request(`/api/quests/${questId}`);
  }

  async preVerifyDelivery(questId: string, householdId: string, verificationData: any) {
    return this.request('/api/quests/pre-verify', {
      method: 'POST',
      body: JSON.stringify({ quest_id: questId, household_id: householdId, ...verificationData }),
    });
  }

  async completeVisit(visitId: string, data: any) {
    return this.request(`/api/quests/visits/${visitId}/complete`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ==================== VEEDURÍA ====================

  async fileVeeduria(report: any) {
    return this.request('/api/veeduria/file', {
      method: 'POST',
      body: JSON.stringify(report),
    });
  }

  async getMyVeedurias() {
    return this.request('/api/veeduria/mine');
  }

  async getNearbyVeedurias(lat: number, lng: number, radiusKm = 5) {
    return this.request(`/api/veeduria/nearby?lat=${lat}&lng=${lng}&radius=${radiusKm}`);
  }

  async supportVeeduria(reportId: string) {
    return this.request(`/api/veeduria/${reportId}/support`, { method: 'POST' });
  }

  // ==================== GOVERNANCE ====================

  async requestConsensus(proposal: any) {
    return this.request('/api/governance/consensus', {
      method: 'POST',
      body: JSON.stringify(proposal),
    });
  }

  async getConsensusStatus(traceId: string) {
    return this.request(`/api/governance/consensus/${traceId}`);
  }

  async getGovernanceProposals(status?: string) {
    return this.request(`/api/governance/proposals${status ? `?status=${status}` : ''}`);
  }

  // ==================== AIRPORT ====================

  async requestAirportClearance(data: any) {
    return this.request('/api/airport/clearance', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getAirportClearance(clearanceId: string) {
    return this.request(`/api/airport/clearance/${clearanceId}`);
  }

  async getMyClearances() {
    return this.request('/api/airport/clearance/user/me');
  }

  async verifyQRCode(qrCode: string, airportCode: string) {
    return this.request('/api/airport/verify/qr', {
      method: 'POST',
      body: JSON.stringify({ qr_code: qrCode, airport_code: airportCode }),
    });
  }

  // ==================== NOTIFICATIONS ====================

  async getNotifications(limit = 50) {
    const response = await fetch(`${TELECASTER_BASE}/api/notifications/user/me/history?limit=${limit}`, {
      headers: { 'Authorization': `Bearer ${this.token}` },
    });
    return response.json();
  }

  async markNotificationRead(notificationId: string) {
    return this.request(`/api/notifications/${notificationId}/read`, { method: 'POST' });
  }

  // ==================== IDENTITY ====================

  async getIdentityLevel() {
    return this.request('/api/users/identity-level');
  }

  async escalateIdentity(targetLevel: number, verificationData: any) {
    return this.request('/api/users/escalate-identity', {
      method: 'POST',
      body: JSON.stringify({ target_level: targetLevel, ...verificationData }),
    });
  }

  async verifyCedula(cedula: string, jceVerificationId?: string) {
    return this.request<{ success: boolean; cedula_verified: boolean; identity_level: number }>(
      '/api/auth/cedula/verify',
      {
        method: 'POST',
        body: JSON.stringify({ cedula, jce_verification_id: jceVerificationId }),
      }
    );
  }

  async crossVerifyCedula(cedula: string, barcode: string) {
    const response = await fetch('/api/cedula-cross-verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cedula, barcode }),
    });

    if (!response.ok) {
      throw new Error(`Cross-verification failed (HTTP ${response.status})`);
    }

    return response.json();
  }

  async localCrossVerifyCedula(cedula: string, barcode: string) {
    const base = import.meta.env.VITE_CEDULA_VERIFY_URL || 'http://localhost:8001';
    const response = await fetch(`${base}/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cedula, barcode }),
    });

    if (!response.ok) {
      throw new Error(`Local verifier failed (HTTP ${response.status})`);
    }

    return response.json();
  }

  // ==================== BANK ACCOUNTS ====================

  async getBankAccounts() {
    return this.request<{ accounts: Array<Record<string, unknown>> }>('/api/wallet/bank-accounts');
  }

  async addBankAccount(data: {
    bank_code: string;
    account_number: string;
    account_type?: string;
    nickname?: string;
    cedula?: string;
  }) {
    return this.request<{ success: boolean; account: Record<string, unknown> }>(
      '/api/wallet/bank-accounts',
      { method: 'POST', body: JSON.stringify(data) }
    );
  }

  async removeBankAccount(accountId: string) {
    return this.request<{ success: boolean }>(`/api/wallet/bank-accounts/${accountId}`, {
      method: 'DELETE',
    });
  }

  // ==================== AUDIT ====================

  async getAuditTrail(filters?: any) {
    const params = new URLSearchParams(filters).toString();
    return this.request(`/api/audit/trail?${params}`);
  }
}

export const api = new ApiClient();
export default api;