/**
 * Courage Engine Service
 * 
 * Implements the "courage" principle - adaptive decision making,
 * circuit breaker management, fairness enforcement, and model governance.
 * The courage to act, the wisdom to pause, the integrity to self-correct.
 */

import { EventEmitter } from 'events';

export class CourageEngine extends EventEmitter {
  constructor(config, logger, redisClient, magicAlgorithm) {
    super();
    this.config = config;
    this.logger = logger;
    this.redis = redisClient;
    this.magic = magicAlgorithm;
    
    // Circuit breaker states
    this.circuitBreakers = new Map();
    this.circuitBreakerConfigs = {
      consensus_failure: {
        threshold: 3, // 3 failures in window
        window: 3600000, // 1 hour
        action: 'freeze',
        timeout: 72 * 3600000, // 72 hours
        authority: 'system'
      },
      fairness_collapse: {
        threshold: 0.50, // Gini > 0.50
        metric: 'gini_coefficient',
        action: 'redistribute',
        timeout: 24 * 3600000, // 24 hours
        authority: 'fga'
      },
      model_capture: {
        threshold: 0.50, // Single provider > 50%
        metric: 'provider_concentration',
        action: 'rotate',
        timeout: 48 * 3600000, // 48 hours
        authority: 'fga_veeduria'
      },
      constitutional_crisis: {
        threshold: 1, // Court challenge filed
        metric: 'court_challenges',
        action: 'stay',
        timeout: null, // Until resolved
        authority: 'constitutional_court'
      }
    };
    
    // Fairness metrics
    this.fairnessMetrics = {
      gini_coefficient: 0.35,
      merit_concentration: 0.30,
      geographic_disparity: 3.0,
      demographic_parity: 0.10,
      intergenerational_equity: 1.0
    };
    
    // Model diversity tracking
    this.modelDiversity = {
      providerWeights: {},
      modelStaleness: {},
      rotationSchedule: []
    };
    
    // Courage state
    this.courageState = {
      currentLevel: 1.0,
      lastAssessment: Date.now(),
      pendingDecisions: [],
      overriddenDecisions: 0
    };
  }

  async initialize() {
    this.logger.info('🦁 Initializing Courage Engine...');
    
    // Load circuit breaker states from Redis
    await this.loadCircuitBreakerStates();
    
    // Load fairness metrics
    await this.loadFairnessMetrics();
    
    // Load model diversity
    await this.loadModelDiversity();
    
    // Start monitoring loops
    this.startMonitoring();
    
    this.logger.info('✨ Courage Engine initialized');
    this.emit('ready');
  }

  async loadCircuitBreakerStates() {
    try {
      const states = await this.redis.hGetAll('courage:circuit_breakers');
      for (const [key, value] of Object.entries(states)) {
        this.circuitBreakers.set(key, JSON.parse(value));
      }
      this.logger.debug('Loaded circuit breaker states', { count: this.circuitBreakers.size });
    } catch (error) {
      this.logger.warn('Failed to load circuit breaker states', { error: error.message });
    }
  }

  async loadFairnessMetrics() {
    try {
      const metrics = await this.redis.hGetAll('courage:fairness_metrics');
      for (const [key, value] of Object.entries(metrics)) {
        this.fairnessMetrics[key] = parseFloat(value);
      }
    } catch (error) {
      this.logger.warn('Failed to load fairness metrics', { error: error.message });
    }
  }

  async loadModelDiversity() {
    try {
      const diversity = await this.redis.hGetAll('courage:model_diversity');
      this.modelDiversity.providerWeights = JSON.parse(diversity.provider_weights || '{}');
      this.modelDiversity.modelStaleness = JSON.parse(diversity.model_staleness || '{}');
      this.modelDiversity.rotationSchedule = JSON.parse(diversity.rotation_schedule || '[]');
    } catch (error) {
      this.logger.warn('Failed to load model diversity', { error: error.message });
    }
  }

  startMonitoring() {
    // Check circuit breakers every 30 seconds
    setInterval(() => this.checkCircuitBreakers(), 30000);
    
    // Compute fairness metrics every 5 minutes
    setInterval(() => this.computeFairnessMetrics(), 300000);
    
    // Check model rotation every hour
    setInterval(() => this.checkModelRotation(), 3600000);
    
    // Assess courage level every minute
    setInterval(() => this.assessCourageLevel(), 60000);
    
    this.logger.debug('Courage monitoring started');
  }

  // ==================== CIRCUIT BREAKER MANAGEMENT ====================

  async checkCircuitBreakers() {
    const triggered = [];
    
    for (const [name, config] of Object.entries(this.circuitBreakerConfigs)) {
      const shouldTrigger = await this.evaluateTrigger(name, config);
      
      if (shouldTrigger && !this.circuitBreakers.has(name)) {
        const event = await this.activateBreaker(name, config);
        triggered.push(event);
      } else if (!shouldTrigger && this.circuitBreakers.has(name)) {
        // Auto-resolve if configured
        if (config.autoResolve !== false) {
          await this.resolveBreaker(name, 'auto_resolved');
        }
      }
    }
    
    if (triggered.length > 0) {
      this.logger.warn('🚨 Circuit breakers triggered', { count: triggered.length, breakers: triggered.map(t => t.name) });
      this.emit('circuitBreakersTriggered', triggered);
    }
    
    return triggered;
  }

  async evaluateTrigger(name, config) {
    switch (name) {
      case 'consensus_failure':
        return await this.checkConsensusFailures(config);
      case 'fairness_collapse':
        return await this.checkFairnessCollapse(config);
      case 'model_capture':
        return await this.checkModelCapture(config);
      case 'constitutional_crisis':
        return await this.checkConstitutionalCrisis(config);
      default:
        return false;
    }
  }

  async checkConsensusFailures(config) {
    // Check recent consensus decisions for failures
    // This would query the Python backend or local cache
    const recentFailures = await this.getRecentConsensusFailures(config.window);
    return recentFailures >= config.threshold;
  }

  async checkFairnessCollapse(config) {
    const metricValue = this.fairnessMetrics[config.metric];
    return metricValue !== undefined && metricValue > config.threshold;
  }

  async checkModelCapture(config) {
    const maxWeight = Math.max(...Object.values(this.modelDiversity.providerWeights), 0);
    return maxWeight > config.threshold;
  }

  async checkConstitutionalCrisis(config) {
    // Would check for active constitutional court cases
    // For now, manual trigger only
    const challenges = await this.getActiveCourtChallenges();
    return challenges >= config.threshold;
  }

  async activateBreaker(name, config) {
    const event = {
      name,
      trigger: name,
      action: config.action,
      activatedAt: Date.now(),
      expiresAt: config.timeout ? Date.now() + config.timeout : null,
      authority: config.authority,
      status: 'active',
      metadata: {}
    };
    
    this.circuitBreakers.set(name, event);
    
    // Persist to Redis
    await this.redis.hSet('courage:circuit_breakers', name, JSON.stringify(event));
    
    // Execute action
    await this.executeBreakerAction(event);
    
    // Notify
    this.emit('breakerActivated', event);
    
    return event;
  }

  async executeBreakerAction(event) {
    switch (event.action) {
      case 'freeze':
        await this.freezeNonEmergency();
        break;
      case 'redistribute':
        await this.triggerEmergencyRedistribution();
        break;
      case 'rotate':
        await this.forceModelRotation();
        break;
      case 'stay':
        await this.stayConstitutionalDecisions();
        break;
    }
  }

  async freezeNonEmergency() {
    this.logger.warn('❄️ FREEZE: Non-emergency decisions suspended');
    await this.redis.set('courage:freeze', 'true', { EX: 72 * 3600 });
    this.emit('freezeActivated');
  }

  async triggerEmergencyRedistribution() {
    this.logger.warn('⚖️ REDISTRIBUTE: Emergency fairness redistribution triggered');
    await this.redis.set('courage:redistribute', 'true', { EX: 24 * 3600 });
    this.emit('redistributeActivated');
  }

  async forceModelRotation() {
    this.logger.warn('🔄 ROTATE: Forced model rotation triggered');
    await this.redis.set('courage:rotate', 'true', { EX: 48 * 3600 });
    this.emit('rotateActivated');
  }

  async stayConstitutionalDecisions() {
    this.logger.warn('⚖️ STAY: Constitutional decisions stayed');
    await this.redis.set('courage:stay', 'true');
    this.emit('stayActivated');
  }

  async resolveBreaker(name, resolution) {
    const event = this.circuitBreakers.get(name);
    if (!event) return false;
    
    event.resolvedAt = Date.now();
    event.resolution = resolution;
    event.status = 'resolved';
    
    // Reverse action
    await this.reverseBreakerAction(event);
    
    // Persist
    await this.redis.hSet('courage:circuit_breakers', name, JSON.stringify(event));
    this.circuitBreakers.delete(name);
    
    this.emit('breakerResolved', { name, resolution });
    return true;
  }

  async reverseBreakerAction(event) {
    switch (event.action) {
      case 'freeze':
        await this.redis.del('courage:freeze');
        this.emit('freezeDeactivated');
        break;
      case 'redistribute':
        await this.redis.del('courage:redistribute');
        break;
      case 'rotate':
        await this.redis.del('courage:rotate');
        break;
      case 'stay':
        await this.redis.del('courage:stay');
        break;
    }
  }

  // ==================== FAIRNESS MONITORING ====================

  async computeFairnessMetrics() {
    this.logger.debug('Computing fairness metrics...');
    
    try {
      // In production, query actual data from Python backend
      // For now, simulate with realistic values
      const metrics = await this.calculateFairnessMetrics();
      
      // Update local state
      this.fairnessMetrics = { ...this.fairnessMetrics, ...metrics };
      
      // Persist to Redis
      for (const [key, value] of Object.entries(this.fairnessMetrics)) {
        await this.redis.hSet('courage:fairness_metrics', key, value.toString());
      }
      
      // Check for violations
      await this.checkFairnessViolations();
      
      this.emit('fairnessComputed', this.fairnessMetrics);
      
    } catch (error) {
      this.logger.error('Fairness computation failed', { error: error.message });
    }
  }

  async calculateFairnessMetrics() {
    // Would query actual database for:
    // - Merit score distribution (Gini)
    // - Top 10% concentration
    // - Geographic merit disparity
    // - Demographic parity
    // - Intergenerational equity
    
    // Simulated realistic values
    return {
      gini_coefficient: 0.32 + Math.random() * 0.06, // 0.32-0.38
      merit_concentration: 0.28 + Math.random() * 0.04, // 0.28-0.32
      geographic_disparity: 2.5 + Math.random() * 1.0, // 2.5-3.5
      demographic_parity: 0.08 + Math.random() * 0.04, // 0.08-0.12
      intergenerational_equity: 0.95 + Math.random() * 0.1 // 0.95-1.05
    };
  }

  async checkFairnessViolations() {
    const violations = [];
    
    const thresholds = {
      gini_coefficient: { alert: 0.40, critical: 0.50 },
      merit_concentration: { alert: 0.35, critical: 0.40 },
      geographic_disparity: { alert: 5.0, critical: 10.0 },
      demographic_parity: { alert: 0.15, critical: 0.20 },
      intergenerational_equity: { alert: { min: 0.8, max: 1.2 }, critical: { min: 0.6, max: 1.5 } }
    };
    
    for (const [metric, value] of Object.entries(this.fairnessMetrics)) {
      const threshold = thresholds[metric];
      if (!threshold) continue;
      
      if (metric === 'intergenerational_equity') {
        if (value < threshold.critical.min || value > threshold.critical.max) {
          violations.push({ metric, value, level: 'critical', threshold });
        } else if (value < threshold.alert.min || value > threshold.alert.max) {
          violations.push({ metric, value, level: 'alert', threshold });
        }
      } else {
        if (value >= threshold.critical) {
          violations.push({ metric, value, level: 'critical', threshold });
        } else if (value >= threshold.alert) {
          violations.push({ metric, value, level: 'alert', threshold });
        }
      }
    }
    
    if (violations.length > 0) {
      this.logger.warn('⚖️ Fairness violations detected', { violations });
      this.emit('fairnessViolations', violations);
      
      // Trigger circuit breaker if critical
      const criticalCount = violations.filter(v => v.level === 'critical').length;
      if (criticalCount > 0) {
        await this.checkCircuitBreakers();
      }
    }
    
    return violations;
  }

  // ==================== MODEL DIVERSITY & ROTATION ====================

  async checkModelRotation() {
    this.logger.debug('Checking model rotation schedule...');
    
    const now = Date.now();
    const dueRotations = this.modelDiversity.rotationSchedule.filter(
      r => r.scheduledAt <= now && !r.completed
    );
    
    for (const rotation of dueRotations) {
      await this.executeModelRotation(rotation);
    }
    
    // Check for staleness
    for (const [modelId, staleness] of Object.entries(this.modelDiversity.modelStaleness)) {
      if (now - staleness.lastUsed > 90 * 24 * 3600000) { // 90 days
        this.logger.warn('Model stale, scheduling rotation', { modelId });
        await this.scheduleRotation(modelId, 'staleness');
      }
    }
  }

  async executeModelRotation(rotation) {
    this.logger.info('Executing model rotation', rotation);
    
    // Would trigger actual model swap in Python backend
    // For now, mark complete
    rotation.completed = true;
    rotation.completedAt = Date.now();
    
    await this.redis.hSet('courage:model_diversity', 'rotation_schedule', 
      JSON.stringify(this.modelDiversity.rotationSchedule));
    
    this.emit('modelRotated', rotation);
  }

  async forceModelRotation() {
    // Find most overconcentrated provider
    const providerWeights = this.modelDiversity.providerWeights;
    const maxProvider = Object.entries(providerWeights)
      .sort((a, b) => b[1] - a[1])[0];
    
    if (maxProvider && maxProvider[1] > 0.35) {
      this.logger.warn('Forcing rotation for overconcentrated provider', { provider: maxProvider[0] });
      
      // Schedule rotations for all models from this provider
      // This would integrate with the Python consensus engine
      this.emit('forcedRotation', { provider: maxProvider[0] });
    }
  }

  async scheduleRotation(modelId, reason) {
    const rotation = {
      id: crypto.randomUUID(),
      modelId,
      reason,
      scheduledAt: Date.now() + 3600000, // 1 hour from now
      completed: false
    };
    
    this.modelDiversity.rotationSchedule.push(rotation);
    
    await this.redis.hSet('courage:model_diversity', 'rotation_schedule',
      JSON.stringify(this.modelDiversity.rotationSchedule));
  }

  // ==================== COURAGE ASSESSMENT ====================

  assessCourageLevel() {
    // Courage is a function of:
    // - System health (resonance from magic algorithm)
    // - Fairness stability
    // - Model diversity
    // - Circuit breaker status
    
    const resonance = this.magic?.getState?.().resonance || 0.5;
    const fairnessStability = this.calculateFairnessStability();
    const diversityScore = this.calculateDiversityScore();
    const breakerPenalty = this.circuitBreakers.size * 0.1;
    
    const courage = Math.min(1.0, 
      (resonance * 0.4) + 
      (fairnessStability * 0.3) + 
      (diversityScore * 0.3) - 
      breakerPenalty
    );
    
    this.courageState.currentLevel = Math.max(0.1, courage);
    this.courageState.lastAssessment = Date.now();
    
    this.emit('courageAssessed', { level: this.courageState.currentLevel });
  }

  calculateFairnessStability() {
    // Inverse of violation severity
    let stability = 1.0;
    for (const value of Object.values(this.fairnessMetrics)) {
      if (value > 0.45) stability -= 0.2;
      else if (value > 0.40) stability -= 0.1;
    }
    return Math.max(0, stability);
  }

  calculateDiversityScore() {
    const weights = Object.values(this.modelDiversity.providerWeights);
    if (weights.length === 0) return 0;
    
    // Herfindahl-Hirschman Index (lower = more diverse)
    const hhi = weights.reduce((sum, w) => sum + w * w, 0);
    return Math.max(0, 1 - hhi * 2); // Normalize
  }

  isCourageSufficient(required) {
    return this.courageState.currentLevel >= required;
  }

  // ==================== QUEUE WORKER METHODS ====================

  async processJob(jobData) {
    const { type, payload } = jobData;
    
    switch (type) {
      case 'assess_courage':
        this.assessCourageLevel();
        break;
      case 'check_breakers':
        await this.checkCircuitBreakers();
        break;
      case 'compute_fairness':
        await this.computeFairnessMetrics();
        break;
      case 'rotate_models':
        await this.checkModelRotation();
        break;
      default:
        this.logger.warn('Unknown courage job type', { type });
    }
  }

  // ==================== HELPER METHODS (Stubs) ====================

  async getRecentConsensusFailures(window) {
    // Would query Python backend
    return 0;
  }

  async getActiveCourtChallenges() {
    // Would check legal system integration
    return 0;
  }

  // ==================== STATE ACCESSORS ====================

  getState() {
    return {
      courage: this.courageState,
      circuitBreakers: Array.from(this.circuitBreakers.entries()),
      fairnessMetrics: this.fairnessMetrics,
      modelDiversity: this.modelDiversity
    };
  }

  isFrozen() {
    return this.circuitBreakers.has('consensus_failure');
  }

  isStayed() {
    return this.circuitBreakers.has('constitutional_crisis');
  }

  isRedistributing() {
    return this.circuitBreakers.has('fairness_collapse');
  }

  isRotating() {
    return this.circuitBreakers.has('model_capture');
  }
}

// Need crypto import
import crypto from 'crypto';