/**
 * WebSocket Service
 * 
 * Real-time bidirectional communication for telecaster.
 * Handles connections, subscriptions, presence, and message routing.
 */

import { EventEmitter } from 'events';
import { WebSocketServer, WebSocket } from 'ws';
import jwt from 'jsonwebtoken';
import crypto from 'crypto';

export class WebSocketService extends EventEmitter {
  constructor(config, logger, redisClient, redisPublisher) {
    super();
    this.config = config;
    this.logger = logger;
    this.redis = redisClient;
    this.publisher = redisPublisher;
    
    // Connection state
    this.connections = new Map(); // connectionId -> connection info
    this.userConnections = new Map(); // userId -> Set(connectionId)
    this.subscriptions = new Map(); // topic -> Set(connectionId)
    this.presence = new Map(); // userId -> presence info
    
    // Message routing
    this.messageHandlers = new Map();
    this.middleware = [];
    
    // Metrics
    this.metrics = {
      totalConnections: 0,
      activeConnections: 0,
      messagesReceived: 0,
      messagesSent: 0,
      messagesBroadcast: 0,
      errors: 0
    };
    
    // Heartbeat
    this.heartbeatInterval = null;
  }

  async initialize(server) {
    this.logger.info('🔌 Initializing WebSocket Service...');
    
    // Create WebSocket server
    this.wss = new WebSocketServer({ 
      server,
      path: this.config.websocket.path || '/ws',
      verifyClient: this.verifyClient.bind(this)
    });
    
    this.wss.on('connection', this.handleConnection.bind(this));
    this.wss.on('error', this.handleServerError.bind(this));
    
    // Setup Redis subscription for cross-instance messaging
    await this.setupRedisSubscription();
    
    // Start heartbeat
    this.startHeartbeat();
    
    // Register default handlers
    this.registerDefaultHandlers();
    
    this.logger.info('✨ WebSocket Service initialized');
    this.emit('ready');
  }

  async verifyClient(info, callback) {
    try {
      // Extract token from query or headers
      const url = new URL(info.req.url, `http://${info.req.headers.host}`);
      const token = url.searchParams.get('token') || 
                   info.req.headers['sec-websocket-protocol']?.split(',')[0]?.trim() ||
                   info.req.headers.authorization?.replace('Bearer ', '');
      
      if (!token) {
        this.logger.warn('WS connection rejected: no token');
        return callback(false, 401, 'Authentication required');
      }
      
      // Verify JWT
      const decoded = jwt.verify(token, this.config.jwt.secret);
      
      // Check if user exists and is active
      const userActive = await this.redis.get(`user:active:${decoded.sub}`);
      if (!userActive) {
        return callback(false, 403, 'User not active');
      }
      
      // Attach user info to request for later use
      info.req.user = decoded;
      callback(true);
    } catch (error) {
      this.logger.warn('WS connection rejected: invalid token', { error: error.message });
      callback(false, 401, 'Invalid token');
    }
  }

  async handleConnection(ws, req) {
    const connectionId = crypto.randomUUID();
    const user = req.user;
    
    // Create connection info
    const connection = {
      id: connectionId,
      ws,
      userId: user.sub,
      userRole: user.role,
      userLevel: user.identityLevel || 0,
      connectedAt: Date.now(),
      lastActivity: Date.now(),
      subscriptions: new Set(),
      metadata: {
        userAgent: req.headers['user-agent'],
        ip: req.socket.remoteAddress
      }
    };
    
    // Store connection
    this.connections.set(connectionId, connection);
    this.addUserConnection(user.sub, connectionId);
    
    // Update presence
    await this.updatePresence(user.sub, 'online', connectionId);
    
    // Update metrics
    this.metrics.totalConnections++;
    this.metrics.activeConnections++;
    
    this.logger.info('WS client connected', { connectionId, userId: user.sub });
    this.emit('connected', connection);
    
    // Send welcome message
    this.send(connectionId, {
      type: 'welcome',
      connectionId,
      timestamp: Date.now(),
      serverTime: Date.now(),
      features: this.getAvailableFeatures(user)
    });
    
    // Setup message handler
    ws.on('message', (data) => this.handleMessage(connectionId, data));
    
    // Setup close handler
    ws.on('close', (code, reason) => this.handleDisconnect(connectionId, code, reason));
    
    // Setup error handler
    ws.on('error', (error) => this.handleError(connectionId, error));
    
    // Setup pong handler
    ws.on('pong', () => this.handlePong(connectionId));
  }

  async handleMessage(connectionId, data) {
    const connection = this.connections.get(connectionId);
    if (!connection) return;
    
    connection.lastActivity = Date.now();
    this.metrics.messagesReceived++;
    
    try {
      const message = JSON.parse(data.toString());
      
      // Run middleware
      for (const middleware of this.middleware) {
        const result = await middleware(message, connection);
        if (result === false) return; // Middleware blocked
        if (result) message = result; // Middleware transformed
      }
      
      // Route to handler
      const handler = this.messageHandlers.get(message.type);
      if (handler) {
        await handler(message, connection);
      } else {
        this.logger.debug('Unknown message type', { type: message.type, connectionId });
        this.send(connectionId, {
          type: 'error',
          code: 'UNKNOWN_MESSAGE_TYPE',
          message: `Unknown message type: ${message.type}`,
          requestId: message.requestId
        });
      }
    } catch (error) {
      this.metrics.errors++;
      this.logger.error('WS message handling error', { connectionId, error: error.message });
      this.send(connectionId, {
        type: 'error',
        code: 'MESSAGE_PARSE_ERROR',
        message: 'Invalid message format'
      });
    }
  }

  async handleDisconnect(connectionId, code, reason) {
    const connection = this.connections.get(connectionId);
    if (!connection) return;
    
    // Clean up subscriptions
    for (const topic of connection.subscriptions) {
      this.unsubscribe(connectionId, topic);
    }
    
    // Remove user connection
    this.removeUserConnection(connection.userId, connectionId);
    
    // Update presence if no more connections
    const remaining = this.userConnections.get(connection.userId)?.size || 0;
    if (remaining === 0) {
      await this.updatePresence(connection.userId, 'offline');
    }
    
    // Clean up
    this.connections.delete(connectionId);
    this.metrics.activeConnections--;
    
    this.logger.info('WS client disconnected', { connectionId, userId: connection.userId, code });
    this.emit('disconnected', { connectionId, userId: connection.userId, code, reason });
  }

  handleError(connectionId, error) {
    this.metrics.errors++;
    this.logger.error('WS connection error', { connectionId, error: error.message });
    this.emit('error', { connectionId, error });
  }

  handlePong(connectionId) {
    const connection = this.connections.get(connectionId);
    if (connection) {
      connection.lastActivity = Date.now();
    }
  }

  handleServerError(error) {
    this.logger.error('WS server error', { error: error.message });
    this.emit('serverError', error);
  }

  // ==================== MESSAGE ROUTING ====================

  registerHandler(type, handler) {
    this.messageHandlers.set(type, handler);
  }

  registerMiddleware(middleware) {
    this.middleware.push(middleware);
  }

  registerDefaultHandlers() {
    // Ping/Pong
    this.registerHandler('ping', async (message, connection) => {
      this.send(connection.id, { type: 'pong', timestamp: Date.now(), requestId: message.requestId });
    });
    
    // Subscribe
    this.registerHandler('subscribe', async (message, connection) => {
      const { topics } = message;
      if (!Array.isArray(topics)) return;
      
      const results = [];
      for (const topic of topics) {
        if (this.canSubscribe(connection, topic)) {
          this.subscribe(connection.id, topic);
          results.push({ topic, success: true });
        } else {
          results.push({ topic, success: false, reason: 'unauthorized' });
        }
      }
      
      this.send(connection.id, {
        type: 'subscribe_result',
        results,
        requestId: message.requestId
      });
    });
    
    // Unsubscribe
    this.registerHandler('unsubscribe', async (message, connection) => {
      const { topics } = message;
      if (!Array.isArray(topics)) return;
      
      for (const topic of topics) {
        this.unsubscribe(connection.id, topic);
      }
      
      this.send(connection.id, {
        type: 'unsubscribe_result',
        topics,
        requestId: message.requestId
      });
    });
    
    // Presence
    this.registerHandler('presence', async (message, connection) => {
      const { status, metadata } = message;
      await this.updatePresence(connection.userId, status, connection.id, metadata);
      
      this.send(connection.id, {
        type: 'presence_ack',
        status,
        requestId: message.requestId
      });
    });
    
    // Get presence
    this.registerHandler('get_presence', async (message, connection) => {
      const { userIds } = message;
      const presence = {};
      
      for (const userId of userIds) {
        presence[userId] = this.presence.get(userId) || { status: 'offline' };
      }
      
      this.send(connection.id, {
        type: 'presence_result',
        presence,
        requestId: message.requestId
      });
    });
    
    // Broadcast (for authorized users)
    this.registerHandler('broadcast', async (message, connection) => {
      if (!this.canBroadcast(connection)) {
        this.send(connection.id, {
          type: 'error',
          code: 'UNAUTHORIZED',
          message: 'Insufficient permissions to broadcast',
          requestId: message.requestId
        });
        return;
      }
      
      await this.broadcastToTopic(message.topic, message.payload, {
        excludeConnection: connection.id,
        priority: message.priority
      });
      
      this.send(connection.id, {
        type: 'broadcast_ack',
        topic: message.topic,
        requestId: message.requestId
      });
    });
    
    // Direct message
    this.registerHandler('direct_message', async (message, connection) => {
      const { userId, payload } = message;
      await this.sendToUser(userId, {
        type: 'direct_message',
        from: connection.userId,
        payload,
        timestamp: Date.now()
      });
      
      this.send(connection.id, {
        type: 'direct_message_ack',
        userId,
        requestId: message.requestId
      });
    });
    
    // Typing indicator
    this.registerHandler('typing', async (message, connection) => {
      const { topic, isTyping } = message;
      this.broadcastToTopic(topic, {
        type: 'user_typing',
        userId: connection.userId,
        isTyping
      }, { excludeConnection: connection.id });
    });
    
    // Read receipt
    this.registerHandler('read_receipt', async (message, connection) => {
      const { messageId, topic } = message;
      this.broadcastToTopic(topic, {
        type: 'message_read',
        messageId,
        userId: connection.userId,
        readAt: Date.now()
      }, { excludeConnection: connection.id });
    });
  }

  // ==================== SUBSCRIPTION MANAGEMENT ====================

  canSubscribe(connection, topic) {
    // Check authorization for topic
    // Public topics: anyone can subscribe
    // Private topics: require ownership or permission
    // Governance topics: require identity level >= 3
    
    if (topic.startsWith('public.')) return true;
    if (topic.startsWith('user.')) {
      const targetUserId = topic.split('.')[1];
      return connection.userId === targetUserId || connection.userRole === 'admin';
    }
    if (topic.startsWith('governance.')) {
      return connection.userLevel >= 3 || connection.userRole === 'admin';
    }
    if (topic.startsWith('fga.')) {
      return connection.userRole === 'admin' || connection.userRole === 'fga_member';
    }
    if (topic.startsWith('alert.')) return true;
    if (topic.startsWith('notification.')) {
      const targetUserId = topic.split('.')[1];
      return connection.userId === targetUserId;
    }
    
    return false;
  }

  subscribe(connectionId, topic) {
    const connection = this.connections.get(connectionId);
    if (!connection) return;
    
    connection.subscriptions.add(topic);
    
    if (!this.subscriptions.has(topic)) {
      this.subscriptions.set(topic, new Set());
    }
    this.subscriptions.get(topic).add(connectionId);
    
    this.logger.debug('WS subscribed', { connectionId, topic });
  }

  unsubscribe(connectionId, topic) {
    const connection = this.connections.get(connectionId);
    if (!connection) return;
    
    connection.subscriptions.delete(topic);
    
    const subscribers = this.subscriptions.get(topic);
    if (subscribers) {
      subscribers.delete(connectionId);
      if (subscribers.size === 0) {
        this.subscriptions.delete(topic);
      }
    }
    
    this.logger.debug('WS unsubscribed', { connectionId, topic });
  }

  // ==================== MESSAGE SENDING ====================

  send(connectionId, message) {
    const connection = this.connections.get(connectionId);
    if (!connection || connection.ws.readyState !== WebSocket.OPEN) {
      return false;
    }
    
    try {
      connection.ws.send(JSON.stringify(message));
      this.metrics.messagesSent++;
      return true;
    } catch (error) {
      this.logger.error('WS send error', { connectionId, error: error.message });
      return false;
    }
  }

  async sendToUser(userId, message) {
    const connectionIds = this.userConnections.get(userId);
    if (!connectionIds) return 0;
    
    let sent = 0;
    for (const connectionId of connectionIds) {
      if (this.send(connectionId, message)) {
        sent++;
      }
    }
    return sent;
  }

  async broadcastToTopic(topic, message, options = {}) {
    const subscribers = this.subscriptions.get(topic);
    if (!subscribers) return 0;
    
    const exclude = options.excludeConnection;
    let sent = 0;
    
    for (const connectionId of subscribers) {
      if (connectionId !== exclude) {
        if (this.send(connectionId, message)) {
          sent++;
        }
      }
    }
    
    this.metrics.messagesBroadcast += sent;
    return sent;
  }

  async broadcastToAll(message, options = {}) {
    let sent = 0;
    for (const [connectionId, connection] of this.connections.entries()) {
      if (options.filter && !options.filter(connection)) continue;
      if (this.send(connectionId, message)) {
        sent++;
      }
    }
    this.metrics.messagesBroadcast += sent;
    return sent;
  }

  async broadcastToRole(role, message) {
    let sent = 0;
    for (const [connectionId, connection] of this.connections.entries()) {
      if (connection.userRole === role || connection.userRole === 'admin') {
        if (this.send(connectionId, message)) {
          sent++;
        }
      }
    }
    this.metrics.messagesBroadcast += sent;
    return sent;
  }

  // ==================== PRESENCE ====================

  async updatePresence(userId, status, connectionId = null, metadata = {}) {
    const now = Date.now();
    const presence = {
      userId,
      status,
      lastSeen: now,
      connections: connectionId ? 1 : (this.userConnections.get(userId)?.size || 0),
      metadata,
      updatedAt: now
    };
    
    this.presence.set(userId, presence);
    
    // Persist to Redis
    await this.redis.hSet('presence:users', userId, JSON.stringify(presence));
    await this.redis.expire('presence:users', 86400); // 24 hours
    
    // Publish to other instances
    await this.publisher.publish('presence:update', JSON.stringify(presence));
    
    // Broadcast to subscribers
    await this.broadcastToTopic(`presence.${userId}`, {
      type: 'presence_update',
      presence
    });
  }

  getPresence(userId) {
    return this.presence.get(userId) || { status: 'offline' };
  }

  // ==================== CONNECTION MANAGEMENT ====================

  addUserConnection(userId, connectionId) {
    if (!this.userConnections.has(userId)) {
      this.userConnections.set(userId, new Set());
    }
    this.userConnections.get(userId).add(connectionId);
  }

  removeUserConnection(userId, connectionId) {
    const connections = this.userConnections.get(userId);
    if (connections) {
      connections.delete(connectionId);
      if (connections.size === 0) {
        this.userConnections.delete(userId);
      }
    }
  }

  getUserConnections(userId) {
    return this.userConnections.get(userId) || new Set();
  }

  isUserOnline(userId) {
    return this.userConnections.has(userId) && this.userConnections.get(userId).size > 0;
  }

  // ==================== REDIS SUBSCRIPTION ====================

  async setupRedisSubscription() {
    // Subscribe to cross-instance messages
    const subscriber = this.redis.duplicate();
    
    await subscriber.subscribe('ws:broadcast', (message) => {
      this.handleRedisBroadcast(message);
    });
    
    await subscriber.subscribe('ws:user_message', (message) => {
      this.handleRedisUserMessage(message);
    });
    
    await subscriber.subscribe('presence:update', (message) => {
      this.handleRedisPresenceUpdate(message);
    });
    
    this.redisSubscriber = subscriber;
  }

  async handleRedisBroadcast(message) {
    try {
      const { topic, payload, options } = JSON.parse(message);
      await this.broadcastToTopic(topic, payload, options);
    } catch (error) {
      this.logger.error('Redis broadcast handling error', { error: error.message });
    }
  }

  async handleRedisUserMessage(message) {
    try {
      const { userId, payload } = JSON.parse(message);
      await this.sendToUser(userId, payload);
    } catch (error) {
      this.logger.error('Redis user message handling error', { error: error.message });
    }
  }

  async handleRedisPresenceUpdate(message) {
    try {
      const presence = JSON.parse(message);
      // Update local presence cache
      this.presence.set(presence.userId, presence);
      
      // Broadcast to local subscribers
      await this.broadcastToTopic(`presence.${presence.userId}`, {
        type: 'presence_update',
        presence
      });
    } catch (error) {
      this.logger.error('Redis presence update handling error', { error: error.message });
    }
  }

  // ==================== CROSS-INSTANCE MESSAGING ====================

  async publishBroadcast(topic, payload, options = {}) {
    await this.publisher.publish('ws:broadcast', JSON.stringify({ topic, payload, options }));
  }

  async publishUserMessage(userId, payload) {
    await this.publisher.publish('ws:user_message', JSON.stringify({ userId, payload }));
  }

  // ==================== HEARTBEAT ====================

  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      const now = Date.now();
      const timeout = this.config.websocket.heartbeatTimeout || 30000;
      
      for (const [connectionId, connection] of this.connections.entries()) {
        // Check if connection is stale
        if (now - connection.lastActivity > timeout) {
          this.logger.debug('WS connection timeout', { connectionId });
          connection.ws.terminate();
          continue;
        }
        
        // Send ping
        if (connection.ws.readyState === WebSocket.OPEN) {
          connection.ws.ping();
        }
      }
    }, this.config.websocket.heartbeatInterval || 15000);
  }

  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  // ==================== FEATURES ====================

  getAvailableFeatures(user) {
    const features = {
      realtime: true,
      presence: true,
      typing: true,
      readReceipts: true,
      directMessages: true,
      broadcasts: user.userRole === 'admin' || user.userRole === 'fga_member',
      governance: user.identityLevel >= 3,
      fga: user.userRole === 'admin' || user.userRole === 'fga_member'
    };
    return features;
  }

  canBroadcast(connection) {
    return connection.userRole === 'admin' || 
           connection.userRole === 'fga_member' ||
           (connection.userLevel >= 4 && connection.userRole === 'moderator');
  }

  // ==================== PUBLIC API ====================

  getConnectionCount() {
    return this.connections.size;
  }

  getUserConnectionCount(userId) {
    return this.userConnections.get(userId)?.size || 0;
  }

  getTopicSubscribers(topic) {
    return this.subscriptions.get(topic)?.size || 0;
  }

  getMetrics() {
    return { ...this.metrics };
  }

  getState() {
    return {
      connections: this.connections.size,
      users: this.userConnections.size,
      topics: this.subscriptions.size,
      presence: this.presence.size,
      metrics: this.getMetrics()
    };
  }

  async shutdown() {
    this.logger.info('Shutting down WebSocket Service...');
    
    this.stopHeartbeat();
    
    // Close all connections
    for (const [connectionId, connection] of this.connections.entries()) {
      connection.ws.close(1001, 'Server shutting down');
    }
    
    // Close Redis subscriber
    if (this.redisSubscriber) {
      await this.redisSubscriber.quit();
    }
    
    // Close WebSocket server
    if (this.wss) {
      await new Promise(resolve => this.wss.close(resolve));
    }
    
    this.logger.info('WebSocket Service shut down');
  }
}