/**
 * Notification Service
 * 
 * Handles citizen notifications, merit updates, quest reminders,
 * payment confirmations, and routine governance communications.
 */

import { EventEmitter } from 'events';
import crypto from 'crypto';

export class NotificationService extends EventEmitter {
  constructor(config, logger, redisClient, notificationQueue, broadcastService) {
    super();
    this.config = config;
    this.logger = logger;
    this.redis = redisClient;
    this.notificationQueue = notificationQueue;
    this.broadcastService = broadcastService;
    
    // Notification templates
    this.templates = {
      // Merit notifications
      merit_earned: {
        title: '🏆 Méritos Ganados',
        body: 'Ganaste {amount} méritos por {reason}. Total: {total}',
        channels: ['whatsapp', 'push']
      },
      merit_threshold: {
        title: '🎉 ¡Nuevo Beneficio Desbloqueado!',
        body: 'Alcanzaste {merits} méritos. Ahora calificas para: {benefit}. Ver: {url}',
        channels: ['whatsapp', 'push', 'sms']
      },
      merit_spent: {
        title: '💎 Méritos Utilizados',
        body: 'Gastaste {amount} méritos en {item}. Te quedan {remaining}.',
        channels: ['whatsapp', 'push']
      },
      
      // Payment notifications
      payment_initiated: {
        title: '💳 Pago Iniciado',
        body: 'Tu pago de {amount} por {type} está siendo procesado. Trace: {traceId}',
        channels: ['whatsapp', 'push']
      },
      payment_confirmed: {
        title: '✅ Pago Confirmado',
        body: 'Pago de {amount} por {type} completado. Trace: {traceId}. Méritos: +{merits}',
        channels: ['whatsapp', 'push', 'sms']
      },
      payment_failed: {
        title: '❌ Pago Fallido',
        body: 'Tu pago de {amount} por {type} no se pudo procesar. Razón: {reason}. Intenta de nuevo.',
        channels: ['whatsapp', 'sms', 'push']
      },
      payment_refunded: {
        title: '🔄 Reembolso Procesado',
        body: 'Se reembolsaron {amount} por {type}. Trace: {traceId}',
        channels: ['whatsapp', 'push']
      },
      
      // Selecting Front
      selecting_front_order: {
        title: '📦 Pedido Confirmado',
        body: 'Tu pedido de {item} (costo: {merits} méritos) está confirmado. Entrega: {deliveryDate}',
        channels: ['whatsapp', 'push', 'sms']
      },
      selecting_front_shipped: {
        title: '🚚 En Camino',
        body: 'Tu {item} está en camino. Courier: {courier}. Entrega estimada: {eta}',
        channels: ['whatsapp', 'push']
      },
      selecting_front_delivered: {
        title: '📬 Entregado',
        body: 'Tu {item} fue entregado. ¡Disfrútalo! Méritos ganados: +{merits}',
        channels: ['whatsapp', 'push', 'sms']
      },
      
      // Quest notifications
      quest_assigned: {
        title: '🚶 Quest Asignado',
        body: 'Fuiste asignado al Quest en {territory}. Inicio: {startDate}. Bono diario: {stipend}',
        channels: ['whatsapp', 'sms', 'push']
      },
      quest_reminder: {
        title: '⏰ Recordatorio Quest',
        body: 'Mañana tienes visita en {sector}. Hogar: {home}. Confirma: {url}',
        channels: ['whatsapp', 'sms', 'push']
      },
      quest_completed: {
        title: '✅ Quest Completado',
        body: 'Completaste el Quest en {territory}. Visitas: {visits}. Méritos: +{merits}. Stipend: {stipend}',
        channels: ['whatsapp', 'push', 'sms']
      },
      quest_pre_verification: {
        title: '🔍 Pre-verificación Requerida',
        body: 'Necesitas pre-verificar entrega para {recipient} en {address}. Fecha: {date}',
        channels: ['whatsapp', 'sms']
      },
      
      // Veeduría
      veeduria_filed: {
        title: '📋 Veeduría Registrada',
        body: 'Tu reporte #{id} sobre {category} en {location} fue registrado. Estado: pendiente',
        channels: ['whatsapp', 'push']
      },
      veeduria_validated: {
        title: '✅ Veeduría Validada',
        body: 'Tu reporte #{id} fue validado. Méritos: +{merits}. Acciones: {actions}',
        channels: ['whatsapp', 'push', 'sms']
      },
      veeduria_escalated: {
        title: '⚠️ Veeduría Escalada',
        body: 'Tu reporte #{id} fue escalado a {authority}. Seguimiento: {url}',
        channels: ['whatsapp', 'push', 'sms']
      },
      veeduria_nearby: {
        title: '📍 Veeduría Cerca',
        body: 'Nueva veeduría #{id} en {location} ({type}). ¿Deseas apoyar? {url}',
        channels: ['whatsapp', 'push']
      },
      
      // Delivery notifications
      delivery_scheduled: {
        title: '📅 Entrega Programada',
        body: 'Entrega de {item} programada para {date} entre {window}. Ref: {deliveryId}',
        channels: ['whatsapp', 'sms', 'push']
      },
      delivery_en_route: {
        title: '🚛 En Ruta',
        body: 'Tu entrega de {item} está en camino. Courier: {courier}. ETA: {eta}',
        channels: ['whatsapp', 'push']
      },
      delivery_completed: {
        title: '✅ Entrega Completada',
        body: 'Tu {item} fue entregado a {recipient}. Foto: {photoUrl}. Firma: {signatureUrl}',
        channels: ['whatsapp', 'push', 'sms']
      },
      delivery_failed: {
        title: '❌ Entrega Fallida',
        body: 'No se pudo entregar {item}. Razón: {reason}. Reprogramando...',
        channels: ['whatsapp', 'sms', 'push']
      },
      delivery_neighbor: {
        title: '🤝 Entregado a Vecino',
        body: 'Tu {item} fue entregado a tu vecino {neighbor}. Recogerás: {instructions}',
        channels: ['whatsapp', 'push', 'sms']
      },
      delivery_pickup: {
        title: '📦 Listo para Recoger',
        body: 'Tu {item} está en {pickupPoint}. Horario: {hours}. Código: {code}',
        channels: ['whatsapp', 'sms', 'push']
      },
      
      // Mutual Aid
      mutual_aid_request: {
        title: '🤝 Ayuda Solicitada',
        body: '{requester} necesita ayuda con {category}: {description}. ¿Puedes ayudar? {url}',
        channels: ['whatsapp', 'push']
      },
      mutual_aid_matched: {
        title: '🤝 Ayuda Encontrada',
        body: '{helper} te ayudará con {category}. Contacto: {contact}',
        channels: ['whatsapp', 'push', 'sms']
      },
      mutual_aid_completed: {
        title: '✅ Ayuda Completada',
        body: 'La ayuda mutua con {partner} fue completada. Méritos: +{merits}',
        channels: ['whatsapp', 'push']
      },
      
      // Convivencia Limpia
      convivencia_license: {
        title: '📜 Licencia Convivencia',
        body: 'Obtuviste licencia {type} nivel {level}. Válida hasta: {expiry}',
        channels: ['whatsapp', 'push']
      },
      convivencia_interaction: {
        title: '💚 Interacción Registrada',
        body: 'Tu interacción con {person} generó bondad: +{kindness}. Confianza: {trust}',
        channels: ['push']
      },
      
      // Governance
      consensus_announcement: {
        title: '⚖️ Decisión Gobernanza',
        body: 'Consenso {decision} para {proposal}. Score: {score}%. Trace: {traceId}',
        channels: ['whatsapp', 'push', 'discord']
      },
      fga_action: {
        title: '🏛️ Acción FGA',
        body: 'FGA {action} sobre {target}. Votos: {for}/{against}. Ver: {url}',
        channels: ['whatsapp', 'push', 'discord']
      },
      
      // Identity
      identity_escalated: {
        title: '🔐 Nivel de Identidad',
        body: 'Tu nivel subió a {level}. Nuevas capacidades: {capabilities}',
        channels: ['whatsapp', 'push', 'sms']
      },
      identity_verification_required: {
        title: '📋 Verificación Requerida',
        body: 'Para acceder a {feature} necesitas verificar tu identidad. Inicia: {url}',
        channels: ['whatsapp', 'sms', 'push']
      },
      
      // System
      maintenance_notice: {
        title: '🔧 Mantenimiento Programado',
        body: 'Mantenimiento el {date} de {start} a {end}. Servicios afectados: {services}',
        channels: ['whatsapp', 'push', 'discord']
      },
      security_alert: {
        title: '🔒 Alerta de Seguridad',
        body: 'Detectamos actividad inusual en tu cuenta. Revisa: {url}',
        channels: ['whatsapp', 'sms', 'push', 'email']
      }
    };
    
    // User preferences cache
    this.userPreferences = new Map();
    this.notificationHistory = [];
  }

  async initialize() {
    this.logger.info('📬 Initializing Notification Service...');
    
    // Load user preferences
    await this.loadUserPreferences();
    
    // Start processing
    this.startProcessing();
    
    this.logger.info('✨ Notification Service initialized');
    this.emit('ready');
  }

  async loadUserPreferences() {
    try {
      const prefs = await this.redis.hGetAll('notification:preferences');
      for (const [userId, data] of Object.entries(prefs)) {
        this.userPreferences.set(userId, JSON.parse(data));
      }
    } catch (error) {
      this.logger.warn('Failed to load notification preferences', { error: error.message });
    }
  }

  startProcessing() {
    // Process notification queue
    setInterval(() => this.processQueue(), 2000);
    
    // Batch notifications every 30 seconds
    setInterval(() => this.processBatchedNotifications(), 30000);
    
    // Digest notifications daily
    setInterval(() => this.sendDailyDigests(), 86400000);
  }

  // ==================== NOTIFICATION CREATION ====================

  async notify(userId, templateKey, params = {}, options = {}) {
    const template = this.templates[templateKey];
    if (!template) {
      throw new Error(`Unknown notification template: ${templateKey}`);
    }
    
    // Get user preferences
    const preferences = this.userPreferences.get(userId) || this.getDefaultPreferences();
    
    // Check if user wants this notification type
    const category = this.getTemplateCategory(templateKey);
    if (!preferences.categories[category]) {
      this.logger.debug('Notification skipped - user disabled category', { userId, category });
      return { skipped: true, reason: 'category_disabled' };
    }
    
    // Check channel preferences
    const channels = template.channels.filter(c => preferences.channels[c]);
    if (channels.length === 0) {
      return { skipped: true, reason: 'no_channels_enabled' };
    }
    
    // Check quiet hours
    if (this.isQuietHours(preferences.quietHours)) {
      if (!options.bypassQuietHours) {
        return await this.scheduleForLater(userId, templateKey, params, preferences);
      }
    }
    
    // Render template
    const rendered = this.renderNotification(template, params);
    
    // Create notification
    const notification = {
      id: crypto.randomUUID(),
      userId,
      templateKey,
      category,
      title: rendered.title,
      body: rendered.body,
      channels,
      priority: options.priority || 'normal',
      metadata: { params, templateKey },
      createdAt: Date.now(),
      status: 'pending'
    };
    
    // Queue for delivery
    await this.queueNotification(notification);
    
    return { notificationId: notification.id, status: 'queued' };
  }

  async notifyBulk(userIds, templateKey, params = {}, options = {}) {
    const results = [];
    for (const userId of userIds) {
      try {
        const result = await this.notify(userId, templateKey, params, options);
        results.push({ userId, ...result });
      } catch (error) {
        results.push({ userId, success: false, error: error.message });
      }
    }
    return results;
  }

  async notifyGroup(groupId, templateKey, params = {}, options = {}) {
    // Get group members
    const members = await this.getGroupMembers(groupId);
    return await this.notifyBulk(members, templateKey, params, options);
  }

  // ==================== TEMPLATE RENDERING ====================

  renderNotification(template, params) {
    const render = (str) => str.replace(/\{(\w+)\}/g, (match, key) => params[key] ?? match);
    return {
      title: render(template.title),
      body: render(template.body)
    };
  }

  getTemplateCategory(templateKey) {
    if (templateKey.startsWith('merit_')) return 'merits';
    if (templateKey.startsWith('payment_')) return 'payments';
    if (templateKey.startsWith('selecting_front_')) return 'selecting_front';
    if (templateKey.startsWith('quest_')) return 'quest';
    if (templateKey.startsWith('veeduria_')) return 'veeduria';
    if (templateKey.startsWith('delivery_')) return 'delivery';
    if (templateKey.startsWith('mutual_aid_')) return 'mutual_aid';
    if (templateKey.startsWith('convivencia_')) return 'convivencia';
    if (templateKey.startsWith('consensus_') || templateKey.startsWith('fga_')) return 'governance';
    if (templateKey.startsWith('identity_')) return 'identity';
    return 'system';
  }

  getDefaultPreferences() {
    return {
      channels: {
        whatsapp: true,
        sms: true,
        push: true,
        ussd: false,
        email: false
      },
      categories: {
        merits: true,
        payments: true,
        selecting_front: true,
        quest: true,
        veeduria: true,
        delivery: true,
        mutual_aid: true,
        convivencia: true,
        governance: true,
        identity: true,
        system: true
      },
      quietHours: { start: '22:00', end: '07:00', timezone: 'America/Santo_Domingo' },
      language: 'es',
      digestEnabled: true,
      digestTime: '08:00'
    };
  }

  isQuietHours(quietHours) {
    if (!quietHours) return false;
    
    const now = new Date();
    const currentTime = now.getHours() * 60 + now.getMinutes();
    
    const [startH, startM] = quietHours.start.split(':').map(Number);
    const [endH, endM] = quietHours.end.split(':').map(Number);
    
    const startMinutes = startH * 60 + startM;
    const endMinutes = endH * 60 + endM;
    
    if (startMinutes <= endMinutes) {
      return currentTime >= startMinutes && currentTime <= endMinutes;
    } else {
      // Crosses midnight
      return currentTime >= startMinutes || currentTime <= endMinutes;
    }
  }

  async scheduleForLater(userId, templateKey, params, preferences) {
    // Calculate next allowed time
    const [endH, endM] = preferences.quietHours.end.split(':').map(Number);
    const nextAllowed = new Date();
    nextAllowed.setHours(endH, endM, 0, 0);
    
    if (nextAllowed <= new Date()) {
      nextAllowed.setDate(nextAllowed.getDate() + 1);
    }
    
    // Store for later delivery
    const key = `notification:scheduled:${userId}:${templateKey}:${Date.now()}`;
    await this.redis.set(key, JSON.stringify({ templateKey, params }), {
      EX: Math.ceil((nextAllowed - Date.now()) / 1000)
    });
    
    return { scheduled: true, deliverAt: nextAllowed.toISOString() };
  }

  // ==================== QUEUE PROCESSING ====================

  async queueNotification(notification) {
    await this.notificationQueue.add('notification', notification, {
      priority: this.getPriorityValue(notification.priority),
      attempts: 3,
      backoff: { type: 'exponential', delay: 5000 },
      removeOnComplete: 100,
      removeOnFail: 50
    });
  }

  getPriorityValue(priority) {
    const values = { emergency: 100, high: 50, normal: 10, low: 1 };
    return values[priority] || 10;
  }

  async processQueue() {
    // BullMQ workers handle actual processing
    const waiting = await this.notificationQueue.getWaitingCount();
    const active = await this.notificationQueue.getActiveCount();
    
    if (waiting > 10000) {
      this.logger.warn('Notification queue backlog', { waiting, active });
    }
  }

  async processBatchedNotifications() {
    // Batch similar notifications to same user
    // Would group by userId and send digest
  }

  async sendDailyDigests() {
    this.logger.info('Sending daily digests...');
    // Send daily digest to users with digestEnabled
  }

  // ==================== JOB PROCESSING ====================

  async processJob(jobData) {
    const notification = jobData;
    
    try {
      // Deliver via broadcast service
      const results = [];
      for (const channel of notification.channels) {
        try {
          const result = await this.broadcastService.deliverViaChannel(notification, channel);
          results.push({ channel, success: true, result });
        } catch (error) {
          results.push({ channel, success: false, error: error.message });
        }
      }
      
      notification.status = results.every(r => r.success) ? 'delivered' : 'partial';
      notification.deliveredAt = Date.now();
      notification.results = results;
      
      // Record in history
      this.notificationHistory.push({ ...notification });
      if (this.notificationHistory.length > 50000) {
        this.notificationHistory.shift();
      }
      
      // Update user preferences (last notification time)
      await this.updateUserPreference(notification.userId, 'lastNotification', Date.now());
      
      this.emit('notificationDelivered', notification);
      
    } catch (error) {
      notification.status = 'failed';
      notification.error = error.message;
      this.emit('notificationFailed', { notification, error });
    }
  }

  // ==================== USER PREFERENCES ====================

  async updateUserPreference(userId, key, value) {
    let prefs = this.userPreferences.get(userId) || this.getDefaultPreferences();
    
    if (key.includes('.')) {
      // Nested key like "channels.whatsapp"
      const parts = key.split('.');
      let obj = prefs;
      for (let i = 0; i < parts.length - 1; i++) {
        obj = obj[parts[i]];
      }
      obj[parts[parts.length - 1]] = value;
    } else {
      prefs[key] = value;
    }
    
    this.userPreferences.set(userId, prefs);
    await this.redis.hSet('notification:preferences', userId, JSON.stringify(prefs));
  }

  async getUserPreferences(userId) {
    return this.userPreferences.get(userId) || this.getDefaultPreferences();
  }

  async setUserPreferences(userId, preferences) {
    this.userPreferences.set(userId, preferences);
    await this.redis.hSet('notification:preferences', userId, JSON.stringify(preferences));
  }

  // ==================== HELPER METHODS ====================

  async getGroupMembers(groupId) {
    // Would query group membership
    return [];
  }

  async updateUserPreference(userId, key, value) {
    // Already implemented above
  }

  // ==================== PUBLIC API ====================

  getNotificationHistory(userId, limit = 50) {
    if (userId) {
      return this.notificationHistory
        .filter(n => n.userId === userId)
        .slice(-limit);
    }
    return this.notificationHistory.slice(-limit);
  }

  getTemplates() {
    return Object.keys(this.templates).map(key => ({
      key,
      title: this.templates[key].title,
      channels: this.templates[key].channels,
      category: this.getTemplateCategory(key)
    }));
  }

  getState() {
    return {
      templates: this.templates.length,
      userPreferencesCached: this.userPreferences.size,
      historyCount: this.notificationHistory.length
    };
  }
}