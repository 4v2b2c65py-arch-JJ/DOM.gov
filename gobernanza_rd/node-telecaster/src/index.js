/**
 * Telecaster Main Entry Point
 * 
 * Multi-channel communication service for GobernanzaRD.
 * Handles WhatsApp, SMS, USSD, Push, WebSocket, and Airport Clearance.
 */

import express from 'express';
import { createServer } from 'http';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import compression from 'compression';

import { config } from './config.js';
import { logger } from './utils/logger.js';
import { redisClient, redisPublisher, redisSubscriber, broadcastQueue, alertQueue, notificationQueue } from './utils/redis.js';
import { BroadcastService } from './services/broadcast.js';
import { AlertService } from './services/alert.js';
import { NotificationService } from './services/notification.js';
import { WebSocketService } from './services/websocket.js';
import { AirportClearanceService } from './services/airport-clearance.js';
import { MagicAlgorithmService } from './services/magic-algorithm.js';
import { CourageEngineService } from './services/courage-engine.js';

// Import routes
import authRoutes from './routes/auth.js';
import broadcastRoutes from './routes/broadcast.js';
import alertRoutes from './routes/alert.js';
import notificationRoutes from './routes/notification.js';
import websocketRoutes from './routes/websocket.js';
import airportRoutes from './routes/airport.js';
import healthRoutes from './routes/health.js';

class TelecasterApp {
  constructor() {
    this.app = express();
    this.server = createServer(this.app);
    this.services = {};
    this.initialized = false;
  }

  async initialize() {
    if (this.initialized) return;
    
    logger.info('🚀 Initializing Telecaster...');
    
    // Setup Express middleware
    this.setupMiddleware();
    
    // Initialize Redis connections
    await this.initRedis();
    
    // Initialize services
    await this.initServices();
    
    // Setup routes
    this.setupRoutes();
    
    // Initialize WebSocket
    await this.services.websocket.initialize(this.server);
    
    // Setup error handling
    this.setupErrorHandling();
    
    this.initialized = true;
    logger.info('✨ Telecaster initialized successfully');
  }

  setupMiddleware() {
    // Security
    this.app.use(helmet({
      contentSecurityPolicy: false, // Allow WebSocket connections
      crossOriginEmbedderPolicy: false
    }));
    
    // CORS
    this.app.use(cors({
      origin: config.cors.origin,
      credentials: true,
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
      allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
    }));
    
    // Compression
    this.app.use(compression());
    
    // Body parsing
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));
    
    // Rate limiting
    const limiter = rateLimit({
      windowMs: config.rateLimit.windowMs,
      max: config.rateLimit.maxRequests,
      message: { error: 'Too many requests, please try again later' },
      standardHeaders: true,
      legacyHeaders: false
    });
    this.app.use('/api/', limiter);
    
    // Request logging
    this.app.use((req, res, next) => {
      const start = Date.now();
      res.on('finish', () => {
        const duration = Date.now() - start;
        logger.debug('HTTP Request', {
          method: req.method,
          url: req.url,
          status: res.statusCode,
          duration: `${duration}ms`,
          ip: req.ip
        });
      });
      next();
    });
    
    // Attach services to request for route access
    this.app.use((req, res, next) => {
      req.services = this.services;
      req.config = config;
      next();
    });
  }

  async initRedis() {
    logger.info('🔌 Connecting to Redis...');
    
    // Test connections
    await redisClient.ping();
    await redisPublisher.ping();
    await redisSubscriber.ping();
    
    logger.info('✅ Redis connections established');
  }

  async initServices() {
    logger.info('⚙️ Initializing services...');
    
    // Core services
    this.services.broadcast = new BroadcastService(
      config, logger, redisClient, redisPublisher,
      broadcastQueue, alertQueue, notificationQueue
    );
    
    this.services.alert = new AlertService(
      config, logger, redisClient, alertQueue, this.services.broadcast
    );
    
    this.services.notification = new NotificationService(
      config, logger, redisClient, notificationQueue, this.services.broadcast
    );
    
    this.services.websocket = new WebSocketService(
      config, logger, redisClient, redisPublisher
    );
    
    this.services.airport = new AirportClearanceService(
      config, logger, redisClient, 
      null, // authService - would be injected
      null, // paymentService
      this.services.notification
    );
    
    // Intelligence services
    this.services.magicAlgorithm = new MagicAlgorithmService(
      config, logger, redisClient
    );
    
    this.services.courageEngine = new CourageEngineService(
      config, logger, redisClient,
      this.services.magicAlgorithm
    );
    
    // Initialize all services
    await Promise.all([
      this.services.broadcast.initialize(),
      this.services.alert.initialize(),
      this.services.notification.initialize(),
      this.services.airport.initialize(),
      this.services.magicAlgorithm.initialize(),
      this.services.courageEngine.initialize()
    ]);
    
    logger.info('✅ All services initialized');
  }

  setupRoutes() {
    // Health check (no auth)
    this.app.use('/health', healthRoutes);
    
    // API routes
    this.app.use('/api/auth', authRoutes);
    this.app.use('/api/broadcast', broadcastRoutes);
    this.app.use('/api/alerts', alertRoutes);
    this.app.use('/api/notifications', notificationRoutes);
    this.app.use('/api/websocket', websocketRoutes);
    this.app.use('/api/airport', airportRoutes);
    
    // Root endpoint
    this.app.get('/', (req, res) => {
      res.json({
        name: 'GobernanzaRD Telecaster',
        version: config.app.version,
        status: 'running',
        services: Object.keys(this.services),
        timestamp: new Date().toISOString()
      });
    });
    
    // API info
    this.app.get('/api', (req, res) => {
      res.json({
        name: 'GobernanzaRD Telecaster API',
        version: config.app.version,
        endpoints: {
          auth: '/api/auth',
          broadcast: '/api/broadcast',
          alerts: '/api/alerts',
          notifications: '/api/notifications',
          websocket: '/api/websocket',
          airport: '/api/airport',
          health: '/health'
        },
        websocket: {
          path: config.websocket.path,
          auth: 'JWT token required'
        }
      });
    });
    
    // 404 handler
    this.app.use((req, res) => {
      res.status(404).json({ error: 'Not found', path: req.path });
    });
  }

  setupErrorHandling() {
    // Global error handler
    this.app.use((err, req, res, next) => {
      logger.error('Unhandled error', {
        error: err.message,
        stack: err.stack,
        path: req.path,
        method: req.method,
        ip: req.ip
      });
      
      const status = err.status || 500;
      res.status(status).json({
        error: status === 500 ? 'Internal server error' : err.message,
        ...(config.app.env === 'development' && { stack: err.stack })
      });
    });
    
    // Unhandled promise rejections
    process.on('unhandledRejection', (reason, promise) => {
      logger.error('Unhandled Rejection', { reason: reason?.message || reason, stack: reason?.stack });
    });
    
    // Uncaught exceptions
    process.on('uncaughtException', (error) => {
      logger.error('Uncaught Exception', { error: error.message, stack: error.stack });
      this.shutdown();
    });
    
    // Graceful shutdown
    process.on('SIGTERM', () => this.shutdown('SIGTERM'));
    process.on('SIGINT', () => this.shutdown('SIGINT'));
  }

  async start() {
    await this.initialize();
    
    const port = config.app.port;
    const host = config.app.host;
    
    return new Promise((resolve) => {
      this.server.listen(port, host, () => {
        logger.info(`🚀 Telecaster running on ${host}:${port}`);
        logger.info(`📡 WebSocket: ws://${host}:${port}${config.websocket.path}`);
        logger.info(`🌍 Environment: ${config.app.env}`);
        resolve(this.server);
      });
    });
  }

  async shutdown(signal = 'SHUTDOWN') {
    logger.info(`🛑 Shutting down Telecaster (${signal})...`);
    
    // Stop accepting new connections
    this.server.close();
    
    // Shutdown services
    if (this.services.websocket) {
      await this.services.websocket.shutdown();
    }
    
    // Close Redis connections
    await redisClient.quit();
    await redisPublisher.quit();
    await redisSubscriber.quit();
    
    // Close BullMQ queues
    await broadcastQueue.close();
    await alertQueue.close();
    await notificationQueue.close();
    
    logger.info('✅ Telecaster shut down complete');
    process.exit(0);
  }

  getApp() {
    return this.app;
  }

  getServer() {
    return this.server;
  }

  getServices() {
    return this.services;
  }
}

// Start if run directly
const app = new TelecasterApp();
app.start().catch(error => {
  logger.error('Failed to start Telecaster', { error: error.message, stack: error.stack });
  process.exit(1);
});

export { TelecasterApp, app };
export default app;