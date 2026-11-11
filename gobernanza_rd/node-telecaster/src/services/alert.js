/**
 * Alert Service
 * 
 * High-priority alerting for emergencies, governance events,
 * circuit breakers, and critical system notifications.
 */

import { EventEmitter } from 'events';
import crypto from 'crypto';

export class AlertService extends EventEmitter {
  constructor(config, logger, redisClient, alertQueue, broadcastService) {
    super();
    this.config = config;
    this.logger = logger;
    this.redis = redisClient;
    this.alertQueue = alertQueue;
    this.broadcastService = broadcastService;
    
    // Alert templates
    this.templates = {
      emergency: {
        hurricane: {
          title: '🌀 ALERTA HURACÁN',
          template: 'Huracán {name} categoría {category}. Vientos {wind} km/h. Trayectoria hacia {areas}. Refúgiese ya. Más info: {url}'
        },
        flood: {
          title: '🌊 ALERTA INUNDACIÓN',
          template: 'Inundación en {areas}. Nivel de agua: {level}m. Evacúe zonas bajas. Siga instrucciones COE. {url}'
        },
        earthquake: {
          title: '🌍 ALERTA SISMO',
          template: 'Sismo magnitud {magnitude} en {location}. Profundidad {depth}km. Revise estructuras. Mantenga calma. {url}'
        },
        tsunami: {
          title: '🌊 ALERTA TSUNAMI',
          template: 'Posible tsunami tras sismo en {location}. Aléjese de la costa inmediantemente. Suba a zona alta. {url}'
        }
      },
      governance: {
        consensus_decision: {
          title: '⚖️ DECISIÓN GOBERNANZA',
          template: 'Consenso {decision} para {proposal}. Score: {score}%. Familias: {families}/5. Trace: {traceId}'
        },
        fga_action: {
          title: '🏛️ ACCIÓN FGA',
          template: 'FGA {action} sobre {target}. Votos: {for}/{against}. Implementación: {date}. Detalles: {url}'
        },
        circuit_breaker: {
          title: '🚨 INTERRUPTOR ACTIVADO',
          template: 'Circuit breaker: {trigger}. Acción: {action}. Autoridad: {authority}. Duración: {duration}'
        },
        fairness_violation: {
          title: '⚖️ VIOLACIÓN EQUIDAD',
          template: 'Métrica {metric} = {value} (umbral: {threshold}). Nivel: {level}. Corrección automática iniciada.'
        }
      },
      citizen: {
        merit_threshold: {
          title: '🏆 NUEVO BENEFICIO',
          template: 'Alcanzaste {merits} méritos. Calificas para: {benefit}. Ver: {url}'
        },
        payment_confirmed: {
          title: '✅ PAGO CONFIRMADO',
          template: 'Pago de {amount} por {type} procesado. Trace: {traceId}. Méritos: +{merits}'
        },
        quest_reminder: {
          title: '🚶 VISITA QUEST MAÑANA',
          template: 'Mañana visitarás {sector}. Hogar: {home}. Confirma: {url}'
        },
        veeduria_alert: {
          title: '📋 VEEDURÍA EN TU ZONA',
          template: 'Reporte #{id} en {location}. Tipo: {type}. ¿Apoyas? {url}'
        },
        identity_escalation: {
          title: '🔐 NIVEL IDENTIDAD',
          template: 'Tu nivel subió a {level}. Nuevas capacidades: {capabilities}'
        }
      }
    };
    
    // Alert state
    this.activeAlerts = new Map();
    this.alertHistory = [];
    this.suppressionRules = new Map();
  }

  async initialize() {
    this.logger.info('🚨 Initializing Alert Service...');
    
    // Load suppression rules
    await this.loadSuppressionRules();
    
    // Start alert processing
    this.startProcessing();
    
    this.logger.info('✨ Alert Service initialized');
    this.emit('ready');
  }

  async loadSuppressionRules() {
    try {
      const rules = await this.redis.hGetAll('alert:suppression_rules');
      for (const [key, value] of Object.entries(rules)) {
        this.suppressionRules.set(key, JSON.parse(value));
      }
    } catch (error) {
      this.logger.warn('Failed to load suppression rules', { error: error.message });
    }
  }

  startProcessing() {
    // Process alert queue every 5 seconds
    setInterval(() => this.processAlertQueue(), 5000);
    
    // Cleanup old alerts every hour
    setInterval(() => this.cleanupOldAlerts(), 3600000);
    
    // Check escalation every minute
    setInterval(() => this.checkEscalations(), 60000);
  }

  // ==================== ALERT CREATION ====================

  async createAlert(alertData) {
    const alertId = crypto.randomUUID();
    const timestamp = Date.now();
    
    // Check suppression
    if (await this.isSuppressed(alertData)) {
      this.logger.debug('Alert suppressed', { alert: alertData.type });
      return { suppressed: true };
    }
    
    const alert = {
      id: alertId,
      ...alertData,
      createdAt: timestamp,
      status: 'pending',
      priority: alertData.priority || 'high',
      channels: alertData.channels || this.getDefaultChannels(alertData.priority),
      attempts: 0,
      maxAttempts: 3,
      metadata: alertData.metadata || {}
    };
    
    // Apply template if specified
    if (alertData.template) {
      alert.rendered = this.renderTemplate(alertData.template, alertData.params || {});
    }
    
    // Queue for processing
    await this.queueAlert(alert);
    
    // Track active alert
    this.activeAlerts.set(alertId, alert);
    
    this.emit('alertCreated', alert);
    return { alertId, status: 'queued' };
  }

  async createEmergencyAlert(type, params, areas = []) {
    const template = this.templates.emergency[type];
    if (!template) {
      throw new Error(`Unknown emergency type: ${type}`);
    }
    
    const rendered = this.renderTemplate(template.template, params);
    
    return await this.createAlert({
      type: `emergency_${type}`,
      category: 'emergency',
      priority: 'emergency',
      title: template.title,
      message: rendered,
      areas,
      params,
      channels: ['cellBroadcast', 'sms', 'whatsapp', 'push', 'discord'],
      metadata: { emergency: true, type, params }
    });
  }

  async createGovernanceAlert(type, params) {
    const template = this.templates.governance[type];
    if (!template) {
      throw new Error(`Unknown governance alert type: ${type}`);
    }
    
    const rendered = this.renderTemplate(template.template, params);
    
    return await this.createAlert({
      type: `governance_${type}`,
      category: 'governance',
      priority: 'high',
      title: template.title,
      message: rendered,
      params,
      channels: ['whatsapp', 'push', 'discord', 'webhook'],
      metadata: { governance: true, type, params }
    });
  }

  async createCitizenAlert(userId, type, params) {
    const template = this.templates.citizen[type];
    if (!template) {
      throw new Error(`Unknown citizen alert type: ${type}`);
    }
    
    const rendered = this.renderTemplate(template.template, params);
    
    return await this.createAlert({
      type: `citizen_${type}`,
      category: 'citizen',
      priority: 'normal',
      title: template.title,
      message: rendered,
      userId,
      params,
      channels: ['whatsapp', 'sms', 'push'],
      metadata: { citizen: true, type, params, userId }
    });
  }

  // ==================== TEMPLATE RENDERING ====================

  renderTemplate(template, params) {
    return template.replace(/\{(\w+)\}/g, (match, key) => {
      return params[key] !== undefined ? params[key] : match;
    });
  }

  // ==================== CHANNEL SELECTION ====================

  getDefaultChannels(priority) {
    const channels = {
      emergency: ['cellBroadcast', 'sms', 'whatsapp', 'push', 'discord'],
      high: ['whatsapp', 'sms', 'push'],
      normal: ['whatsapp', 'push'],
      low: ['push']
    };
    return channels[priority] || channels.normal;
  }

  // ==================== SUPPRESSION ====================

  async isSuppressed(alertData) {
    // Check user-level suppression
    if (alertData.userId) {
      const userSuppressions = await this.redis.sMembers(`alert:suppress:user:${alertData.userId}`);
      if (userSuppressions.includes(alertData.type)) {
        return true;
      }
    }
    
    // Check global suppression rules
    for (const [ruleId, rule] of this.suppressionRules.entries()) {
      if (this.matchesRule(alertData, rule)) {
        return true;
      }
    }
    
    // Check rate limiting per user/type
    if (alertData.userId) {
      const key = `alert:ratelimit:${alertData.userId}:${alertData.type}`;
      const count = await this.redis.incr(key);
      if (count === 1) {
        await this.redis.expire(key, 3600); // 1 hour window
      }
      if (count > 10) { // Max 10 alerts/hour per type per user
        return true;
      }
    }
    
    return false;
  }

  matchesRule(alertData, rule) {
    // Check if alert matches suppression rule conditions
    for (const [field, value] of Object.entries(rule.conditions)) {
      if (alertData[field] !== value) {
        return false;
      }
    }
    return true;
  }

  // ==================== QUEUE PROCESSING ====================

  async queueAlert(alert) {
    const priority = this.getPriorityValue(alert.priority);
    
    await this.alertQueue.add('alert', {
      alertId: alert.id,
      payload: alert
    }, {
      priority,
      attempts: alert.maxAttempts,
      backoff: { type: 'exponential', delay: 10000 },
      removeOnComplete: 50,
      removeOnFail: 20
    });
  }

  getPriorityValue(priority) {
    const values = { emergency: 100, high: 50, normal: 10, low: 1 };
    return values[priority] || 10;
  }

  async processAlertQueue() {
    // BullMQ workers handle actual processing
    // This method monitors queue health
    const waiting = await this.alertQueue.getWaitingCount();
    const active = await this.alertQueue.getActiveCount();
    const failed = await this.alertQueue.getFailedCount();
    
    if (failed > 100) {
      this.logger.warn('Alert queue has many failed jobs', { waiting, active, failed });
    }
  }

  // ==================== JOB PROCESSING ====================

  async processJob(jobData) {
    const { alertId, payload } = jobData;
    
    const alert = this.activeAlerts.get(alertId) || payload;
    if (!alert) {
      this.logger.warn('Alert not found for processing', { alertId });
      return;
    }
    
    alert.status = 'delivering';
    alert.attempts++;
    
    try {
      // Deliver via broadcast service
      const results = [];
      for (const channel of alert.channels) {
        try {
          const result = await this.broadcastService.deliverViaChannel(alert, channel);
          results.push({ channel, success: true, result });
        } catch (error) {
          results.push({ channel, success: false, error: error.message });
        }
      }
      
      const allSuccess = results.every(r => r.success);
      alert.status = allSuccess ? 'delivered' : 'partial';
      alert.deliveredAt = Date.now();
      alert.results = results;
      
      // Record in history
      this.alertHistory.push({ ...alert });
      if (this.alertHistory.length > 10000) {
        this.alertHistory.shift();
      }
      
      // Persist
      await this.persistAlert(alert);
      
      this.emit('alertProcessed', { alertId, success: allSuccess, results });
      
    } catch (error) {
      alert.status = 'failed';
      alert.error = error.message;
      
      if (alert.attempts < alert.maxAttempts) {
        // Re-queue with backoff
        await this.queueAlert(alert);
      } else {
        this.emit('alertFailed', { alertId, error: error.message });
      }
    }
  }

  async persistAlert(alert) {
    // Store in Redis with TTL
    await this.redis.hSet('alert:history', alert.id, JSON.stringify(alert));
    await this.redis.expire('alert:history', 30 * 24 * 3600); // 30 days
  }

  // ==================== ESCALATION ====================

  async checkEscalations() {
    for (const [alertId, alert] of this.activeAlerts.entries()) {
      if (alert.status === 'pending' || alert.status === 'delivering') {
        const age = Date.now() - alert.createdAt;
        
        // Escalate after 5 minutes for high priority
        if (age > 300000 && alert.priority === 'high') {
          await this.escalateAlert(alertId);
        }
        
        // Escalate after 1 minute for emergency
        if (age > 60000 && alert.priority === 'emergency') {
          await this.escalateAlert(alertId);
        }
      }
    }
  }

  async escalateAlert(alertId) {
    const alert = this.activeAlerts.get(alertId);
    if (!alert) return;
    
    this.logger.warn('Escalating alert', { alertId, currentChannels: alert.channels });
    
    // Add more channels
    const additionalChannels = this.getEscalationChannels(alert.channels);
    for (const channel of additionalChannels) {
      if (!alert.channels.includes(channel)) {
        alert.channels.push(channel);
      }
    }
    
    // Re-queue
    await this.queueAlert(alert);
    
    this.emit('alertEscalated', { alertId, newChannels: alert.channels });
  }

  getEscalationChannels(currentChannels) {
    const allChannels = ['cellBroadcast', 'sms', 'whatsapp', 'push', 'voice', 'discord', 'webhook'];
    return allChannels.filter(c => !currentChannels.includes(c));
  }

  // ==================== CLEANUP ====================

  cleanupOldAlerts() {
    const cutoff = Date.now() - 24 * 3600000; // 24 hours
    let cleaned = 0;
    
    for (const [alertId, alert] of this.activeAlerts.entries()) {
      if (alert.status === 'delivered' || alert.status === 'failed') {
        if (alert.deliveredAt && alert.deliveredAt < cutoff) {
          this.activeAlerts.delete(alertId);
          cleaned++;
        }
      }
    }
    
    if (cleaned > 0) {
      this.logger.debug('Cleaned old active alerts', { count: cleaned });
    }
  }

  // ==================== PUBLIC API ====================

  getActiveAlerts() {
    return Array.from(this.activeAlerts.values());
  }

  getAlertHistory(limit = 100) {
    return this.alertHistory.slice(-limit);
  }

  async addSuppressionRule(ruleId, rule) {
    this.suppressionRules.set(ruleId, rule);
    await this.redis.hSet('alert:suppression_rules', ruleId, JSON.stringify(rule));
  }

  async removeSuppressionRule(ruleId) {
    this.suppressionRules.delete(ruleId);
    await this.redis.hDel('alert:suppression_rules', ruleId);
  }

  getState() {
    return {
      activeCount: this.activeAlerts.size,
      historyCount: this.alertHistory.length,
      suppressionRules: this.suppressionRules.size,
      byStatus: this.getStatusCounts()
    };
  }

  getStatusCounts() {
    const counts = {};
    for (const alert of this.activeAlerts.values()) {
      counts[alert.status] = (counts[alert.status] || 0) + 1;
    }
    return counts;
  }
}