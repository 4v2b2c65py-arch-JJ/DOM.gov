/**
 * Airport Clearance Service
 * 
 * Fast-track airport/immigration clearance based on GobernanzaRD identity levels.
 * Implements "Easy Pass" with grade-based clearance for seamless travel.
 */

import { EventEmitter } from 'events';
import crypto from 'crypto';

export class AirportClearanceService extends EventEmitter {
  constructor(config, logger, redisClient, authService, paymentService, telecomService) {
    super();
    this.config = config;
    this.logger = logger;
    this.redis = redisClient;
    this.authService = authService;
    this.paymentService = paymentService;
    this.telecomService = telecomService;
    
    // Clearance grades mapping to identity levels
    this.clearanceGrades = {
      0: { // Anonymous - no clearance
        grade: 'standard',
        label: 'Línea Estándar',
        lanes: ['standard'],
        benefits: [],
        requiresManualCheck: true,
        estimatedTime: '45-60 min'
      },
      1: { // Email Verified - basic pre-check
        grade: 'precheck',
        label: 'Pre-Check Básico',
        lanes: ['standard', 'precheck'],
        benefits: ['formulario_prellenado', 'documento_digital'],
        requiresManualCheck: true,
        estimatedTime: '30-45 min'
      },
      2: { // Merit Linked - trusted traveler
        grade: 'trusted',
        label: 'Viajero Confiable',
        lanes: ['standard', 'precheck', 'trusted'],
        benefits: ['formulario_prellenado', 'documento_digital', 'fila_prioritaria', 'escaneo_rapido'],
        requiresManualCheck: false,
        estimatedTime: '15-25 min',
        autoGate: true
      },
      3: { // Biometric - biometric clearance
        grade: 'biometric',
        label: 'Autorización Biométrica',
        lanes: ['standard', 'precheck', 'trusted', 'biometric', 'egate'],
        benefits: ['formulario_prellenado', 'documento_digital', 'fila_prioritaria', 'escaneo_rapido', 'puerta_automatica', 'sin_papeles'],
        requiresManualCheck: false,
        estimatedTime: '5-10 min',
        autoGate: true,
        biometricGate: true
      },
      4: { // Trusted - diplomatic/executive
        grade: 'executive',
        label: 'Autorización Ejecutiva',
        lanes: ['all', 'vip', 'diplomatic'],
        benefits: ['formulario_prellenado', 'documento_digital', 'fila_prioritaria', 'escaneo_rapido', 'puerta_automatica', 'sin_papeles', 'sala_vip', 'chofer_espera', 'inmigracion_dedicada'],
        requiresManualCheck: false,
        estimatedTime: '2-5 min',
        autoGate: true,
        biometricGate: true,
        vipLane: true,
        dedicatedOfficer: true
      },
      5: { // Authorized - sovereign/state
        grade: 'sovereign',
        label: 'Paso Soberano',
        lanes: ['all', 'vip', 'diplomatic', 'sovereign'],
        benefits: ['all', 'protocolo_estado', 'escolta', 'avion_gubernamental', 'inmunidad_procesal'],
        requiresManualCheck: false,
        estimatedTime: 'inmediato',
        autoGate: true,
        biometricGate: true,
        vipLane: true,
        dedicatedOfficer: true,
        sovereignProtocol: true
      }
    };
    
    // Airport configurations (DR airports)
    this.airports = {
      'SDQ': { // Las Américas
        name: 'Aeropuerto Internacional Las Américas',
        code: 'SDQ',
        city: 'Santo Domingo',
        egates: 12,
        biometricKiosks: 8,
        trustedLanes: 4,
        vipLanes: 2,
        sovereignLane: 1,
        dgiiIntegration: true,
        jceIntegration: true,
        migrationIntegration: true
      },
      'PUJ': { // Punta Cana
        name: 'Aeropuerto Internacional Punta Cana',
        code: 'PUJ',
        city: 'Punta Cana',
        egates: 16,
        biometricKiosks: 12,
        trustedLanes: 6,
        vipLanes: 3,
        sovereignLane: 1,
        dgiiIntegration: true,
        jceIntegration: true,
        migrationIntegration: true
      },
      'STI': { // Cibao
        name: 'Aeropuerto Internacional del Cibao',
        code: 'STI',
        city: 'Santiago',
        egates: 8,
        biometricKiosks: 6,
        trustedLanes: 3,
        vipLanes: 2,
        sovereignLane: 1,
        dgiiIntegration: true,
        jceIntegration: true,
        migrationIntegration: true
      },
      'LRM': { // La Romana
        name: 'Aeropuerto Internacional La Romana',
        code: 'LRM',
        city: 'La Romana',
        egates: 4,
        biometricKiosks: 4,
        trustedLanes: 2,
        vipLanes: 1,
        sovereignLane: 1,
        dgiiIntegration: true,
        jceIntegration: false,
        migrationIntegration: true
      },
      'AZS': { // Samaná
        name: 'Aeropuerto Internacional Samaná El Catey',
        code: 'AZS',
        city: 'Samaná',
        egates: 3,
        biometricKiosks: 2,
        trustedLanes: 1,
        vipLanes: 1,
        sovereignLane: 0,
        dgiiIntegration: true,
        jceIntegration: false,
        migrationIntegration: true
      }
    };
    
    // Active clearances
    this.activeClearances = new Map();
    this.clearanceHistory = [];
  }

  async initialize() {
    this.logger.info('✈️ Initializing Airport Clearance Service...');
    
    // Load airport configs from Redis
    await this.loadAirportConfigs();
    
    // Start clearance expiration checker
    this.startExpirationChecker();
    
    this.logger.info('✨ Airport Clearance Service initialized');
    this.emit('ready');
  }

  async loadAirportConfigs() {
    try {
      const configs = await this.redis.hGetAll('airport:configs');
      for (const [code, data] of Object.entries(configs)) {
        this.airports[code] = { ...this.airports[code], ...JSON.parse(data) };
      }
    } catch (error) {
      this.logger.warn('Failed to load airport configs', { error: error.message });
    }
  }

  startExpirationChecker() {
    // Check every 5 minutes for expired clearances
    setInterval(() => this.checkExpiredClearances(), 300000);
  }

  // ==================== CLEARANCE REQUEST ====================

  async requestClearance(userId, travelData) {
    const { 
      airportCode, 
      flightNumber, 
      departureTime, 
      destination, 
      passportNumber,
      visaRequired,
      travelPurpose 
    } = travelData;
    
    // Get user identity level
    const userProfile = await this.authService.getUserProfile(userId);
    if (!userProfile) {
      throw new Error('User not found');
    }
    
    const identityLevel = userProfile.identityLevel || 0;
    const clearanceGrade = this.clearanceGrades[identityLevel];
    
    // Check if airport supports this grade
    const airport = this.airports[airportCode];
    if (!airport) {
      throw new Error(`Airport ${airportCode} not supported`);
    }
    
    // Verify passport matches
    if (userProfile.passportNumber !== passportNumber) {
      await this.verifyPassport(userId, passportNumber);
    }
    
    // Check visa requirements
    if (visaRequired && identityLevel < 3) {
      const visaStatus = await this.checkVisaStatus(userId, destination);
      if (!visaStatus.valid) {
        throw new Error(`Visa required for ${destination}: ${visaStatus.reason}`);
      }
    }
    
    // Check for travel restrictions
    const restrictions = await this.checkTravelRestrictions(userId);
    if (restrictions.blocked) {
      throw new Error(`Travel blocked: ${restrictions.reason}`);
    }
    
    // Create clearance
    const clearanceId = crypto.randomUUID();
    const now = Date.now();
    const departureMs = new Date(departureTime).getTime();
    const validFrom = departureMs - 4 * 3600000; // 4 hours before
    const validUntil = departureMs + 2 * 3600000; // 2 hours after
    
    const clearance = {
      id: clearanceId,
      userId,
      identityLevel,
      grade: clearanceGrade.grade,
      label: clearanceGrade.label,
      airportCode,
      airportName: airport.name,
      flightNumber,
      departureTime: departureMs,
      destination,
      passportNumber,
      travelPurpose,
      status: 'active',
      benefits: clearanceGrade.benefits,
      lanes: clearanceGrade.lanes,
      autoGate: clearanceGrade.autoGate || false,
      biometricGate: clearanceGrade.biometricGate || false,
      vipLane: clearanceGrade.vipLane || false,
      dedicatedOfficer: clearanceGrade.dedicatedOfficer || false,
      sovereignProtocol: clearanceGrade.sovereignProtocol || false,
      estimatedTime: clearanceGrade.estimatedTime,
      requiresManualCheck: clearanceGrade.requiresManualCheck,
      validFrom,
      validUntil,
      createdAt: now,
      qrCode: this.generateQRCode(clearanceId, userId, airportCode),
      nfcToken: this.generateNFCToken(clearanceId),
      checkpoints: {
        checkin: { status: 'pending', location: 'checkin', required: true },
        security: { status: 'pending', location: 'security', required: true },
        immigration: { status: 'pending', location: 'immigration', required: true },
        boarding: { status: 'pending', location: 'gate', required: true }
      },
      metadata: {
        meritBalance: userProfile.meritBalance || 0,
        veeduriaScore: userProfile.veeduriaScore || 0,
        trustScore: userProfile.trustScore || 0
      }
    };
    
    // Store clearance
    this.activeClearances.set(clearanceId, clearance);
    await this.persistClearance(clearance);
    
    // Send notification to user
    await this.notifyClearance(userId, clearance);
    
    // Notify airport systems
    await this.notifyAirportSystems(airportCode, clearance);
    
    this.emit('clearanceCreated', clearance);
    return clearance;
  }

  async verifyPassport(userId, passportNumber) {
    // Verify with JCE (Junta Central Electoral)
    const verified = await this.authService.verifyDocument(userId, 'passport', passportNumber);
    if (!verified) {
      throw new Error('Passport verification failed');
    }
    return true;
  }

  async checkVisaStatus(userId, destination) {
    // Check with Migration Directorate
    // Mock implementation
    return { valid: true, type: 'tourist', expires: Date.now() + 365 * 86400000 };
  }

  async checkTravelRestrictions(userId) {
    // Check with DGII (tax debts), Judicial (legal cases), Migration (alerts)
    const checks = await Promise.all([
      this.checkTaxDebts(userId),
      this.checkLegalCases(userId),
      this.checkMigrationAlerts(userId)
    ]);
    
    const blocked = checks.some(c => c.blocked);
    const reasons = checks.filter(c => c.blocked).map(c => c.reason);
    
    return { blocked, reasons };
  }

  async checkTaxDebts(userId) {
    // Query DGII
    return { blocked: false };
  }

  async checkLegalCases(userId) {
    // Query Judicial Power
    return { blocked: false };
  }

  async checkMigrationAlerts(userId) {
    // Query Migration Directorate
    return { blocked: false };
  }

  // ==================== QR CODE & NFC ====================

  generateQRCode(clearanceId, userId, airportCode) {
    const payload = {
      cid: clearanceId,
      uid: userId,
      apt: airportCode,
      ts: Date.now(),
      sig: crypto.createHmac('sha256', this.config.airport.qrSecret).update(clearanceId).digest('hex').substring(0, 16)
    };
    return `GOB-AIR:${Buffer.from(JSON.stringify(payload)).toString('base64')}`;
  }

  generateNFCToken(clearanceId) {
    return crypto.randomBytes(32).toString('hex');
  }

  // ==================== CHECKPOINT PROCESSING ====================

  async processCheckpoint(clearanceId, checkpoint, scanData) {
    const clearance = this.activeClearances.get(clearanceId);
    if (!clearance) {
      throw new Error('Clearance not found');
    }
    
    if (clearance.status !== 'active') {
      throw new Error(`Clearance is ${clearance.status}`);
    }
    
    const now = Date.now();
    if (now < clearance.validFrom) {
      throw new Error('Clearance not yet valid');
    }
    if (now > clearance.validUntil) {
      clearance.status = 'expired';
      await this.persistClearance(clearance);
      throw new Error('Clearance expired');
    }
    
    // Verify checkpoint
    const cp = clearance.checkpoints[checkpoint];
    if (!cp) {
      throw new Error(`Invalid checkpoint: ${checkpoint}`);
    }
    
    if (cp.status === 'completed') {
      return { success: true, alreadyProcessed: true, clearance };
    }
    
    // Biometric verification for biometric gate
    if (checkpoint === 'immigration' && clearance.biometricGate) {
      const bioVerified = await this.verifyBiometric(clearance.userId, scanData.biometric);
      if (!bioVerified) {
        throw new Error('Biometric verification failed');
      }
    }
    
    // NFC tap verification
    if (scanData.nfcToken && scanData.nfcToken !== clearance.nfcToken) {
      throw new Error('Invalid NFC token');
    }
    
    // QR code verification
    if (scanData.qrCode && scanData.qrCode !== clearance.qrCode) {
      throw new Error('Invalid QR code');
    }
    
    // Update checkpoint
    cp.status = 'completed';
    cp.completedAt = now;
    cp.scannerId = scanData.scannerId;
    cp.location = scanData.location;
    cp.method = scanData.method || 'qr'; // qr, nfc, biometric, manual
    
    // Check if all required checkpoints completed
    const requiredCheckpoints = Object.values(clearance.checkpoints).filter(c => c.required);
    const allCompleted = requiredCheckpoints.every(c => c.status === 'completed');
    
    if (allCompleted) {
      clearance.status = 'completed';
      clearance.completedAt = now;
      this.emit('clearanceCompleted', clearance);
    }
    
    await this.persistClearance(clearance);
    
    // Notify user of progress
    await this.notifyCheckpointProgress(clearance.userId, clearance, checkpoint);
    
    return { success: true, clearance, checkpoint: cp, allCompleted };
  }

  async verifyBiometric(userId, biometricData) {
    // Would integrate with biometric system
    // For now, mock success for identity level >= 3
    const profile = await this.authService.getUserProfile(userId);
    return profile.identityLevel >= 3;
  }

  // ==================== AIRPORT INTEGRATION ====================

  async notifyAirportSystems(airportCode, clearance) {
    const airport = this.airports[airportCode];
    
    // Send to airport API
    const payload = {
      clearanceId: clearance.id,
      passengerId: clearance.userId,
      flightNumber: clearance.flightNumber,
      departureTime: clearance.departureTime,
      grade: clearance.grade,
      lanes: clearance.lanes,
      autoGate: clearance.autoGate,
      biometricGate: clearance.biometricGate,
      vipLane: clearance.vipLane,
      validFrom: clearance.validFrom,
      validUntil: clearance.validUntil,
      qrCode: clearance.qrCode,
      nfcToken: clearance.nfcToken,
      checkpoints: clearance.checkpoints
    };
    
    // Store for airport polling
    await this.redis.hSet(`airport:clearances:${airportCode}`, clearance.id, JSON.stringify(payload));
    await this.redis.expire(`airport:clearances:${airportCode}`, 86400);
    
    // Push notification to airport system (webhook)
    if (airport.webhookUrl) {
      // Would POST to airport webhook
    }
  }

  async getAirportClearances(airportCode, flightNumber = null) {
    const pattern = flightNumber 
      ? `airport:clearances:${airportCode}:*${flightNumber}*`
      : `airport:clearances:${airportCode}:*`;
    
    // In production, would use SCAN
    const clearances = await this.redis.hGetAll(`airport:clearances:${airportCode}`);
    return Object.values(clearances).map(c => JSON.parse(c));
  }

  // ==================== NOTIFICATIONS ====================

  async notifyClearance(userId, clearance) {
    await this.telecomService.sendNotification(userId, 'airport_clearance', {
      clearanceId: clearance.id,
      grade: clearance.label,
      airport: clearance.airportName,
      flight: clearance.flightNumber,
      departure: new Date(clearance.departureTime).toLocaleString('es-DO'),
      estimatedTime: clearance.estimatedTime,
      lanes: clearance.lanes.join(', '),
      qrCode: clearance.qrCode,
      autoGate: clearance.autoGate ? 'Sí' : 'No',
      benefits: clearance.benefits.join(', ')
    });
  }

  async notifyCheckpointProgress(userId, clearance, checkpoint) {
    const labels = {
      checkin: 'Check-in',
      security: 'Seguridad',
      immigration: 'Inmigración',
      boarding: 'Embarque'
    };
    
    await this.telecomService.sendNotification(userId, 'checkpoint_complete', {
      clearanceId: clearance.id,
      checkpoint: labels[checkpoint] || checkpoint,
      flight: clearance.flightNumber,
      nextCheckpoint: this.getNextCheckpoint(clearance, checkpoint)
    });
  }

  getNextCheckpoint(clearance, currentCheckpoint) {
    const order = ['checkin', 'security', 'immigration', 'boarding'];
    const currentIndex = order.indexOf(currentCheckpoint);
    if (currentIndex >= 0 && currentIndex < order.length - 1) {
      const next = order[currentIndex + 1];
      const labels = { checkin: 'Check-in', security: 'Seguridad', immigration: 'Inmigración', boarding: 'Embarque' };
      return labels[next];
    }
    return 'Completado';
  }

  // ==================== CLEARANCE MANAGEMENT ====================

  async getClearance(clearanceId) {
    return this.activeClearances.get(clearanceId) || await this.loadClearance(clearanceId);
  }

  async getUserClearances(userId, status = 'active') {
    const clearances = [];
    for (const clearance of this.activeClearances.values()) {
      if (clearance.userId === userId && (status === 'all' || clearance.status === status)) {
        clearances.push(clearance);
      }
    }
    return clearances.sort((a, b) => b.createdAt - a.createdAt);
  }

  async cancelClearance(clearanceId, reason) {
    const clearance = this.activeClearances.get(clearanceId);
    if (!clearance) {
      throw new Error('Clearance not found');
    }
    
    clearance.status = 'cancelled';
    clearance.cancelledAt = Date.now();
    clearance.cancelReason = reason;
    
    await this.persistClearance(clearance);
    await this.redis.hDel(`airport:clearances:${clearance.airportCode}`, clearanceId);
    
    // Notify user
    await this.telecomService.sendNotification(clearance.userId, 'clearance_cancelled', {
      clearanceId,
      reason,
      flight: clearance.flightNumber
    });
    
    this.emit('clearanceCancelled', clearance);
    return clearance;
  }

  async checkExpiredClearances() {
    const now = Date.now();
    for (const [id, clearance] of this.activeClearances.entries()) {
      if (clearance.status === 'active' && now > clearance.validUntil) {
        clearance.status = 'expired';
        await this.persistClearance(clearance);
        this.activeClearances.delete(id);
        this.logger.debug('Clearance expired', { clearanceId: id });
      }
    }
  }

  async persistClearance(clearance) {
    await this.redis.hSet('airport:clearances:all', clearance.id, JSON.stringify(clearance));
    await this.redis.expire('airport:clearances:all', 30 * 86400);
  }

  async loadClearance(clearanceId) {
    const data = await this.redis.hGet('airport:clearances:all', clearanceId);
    if (data) {
      const clearance = JSON.parse(data);
      this.activeClearances.set(clearanceId, clearance);
      return clearance;
    }
    return null;
  }

  // ==================== AIRPORT INFO ====================

  getAirportInfo(airportCode) {
    return this.airports[airportCode];
  }

  getAllAirports() {
    return Object.values(this.airports);
  }

  getClearanceGrade(identityLevel) {
    return this.clearanceGrades[identityLevel] || this.clearanceGrades[0];
  }

  getAvailableGrades() {
    return Object.entries(this.clearanceGrades).map(([level, grade]) => ({
      identityLevel: parseInt(level),
      ...grade
    }));
  }

  // ==================== STATE ====================

  getState() {
    const byStatus = {};
    for (const clearance of this.activeClearances.values()) {
      byStatus[clearance.status] = (byStatus[clearance.status] || 0) + 1;
    }
    
    return {
      activeClearances: this.activeClearances.size,
      byStatus,
      airports: Object.keys(this.airports).length,
      grades: Object.keys(this.clearanceGrades).length
    };
  }
}