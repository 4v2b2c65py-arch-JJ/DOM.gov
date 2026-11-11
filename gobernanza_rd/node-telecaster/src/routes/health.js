/**
 * Health Check Routes
 * 
 * Health and readiness endpoints for monitoring.
 */

import express from 'express';
import os from 'os';

const router = express.Router();

// Liveness probe - basic health
router.get('/live', (req, res) => {
  res.json({ 
    status: 'alive', 
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// Readiness probe - check dependencies
router.get('/ready', async (req, res) => {
  const checks = {
    redis: false,
    queues: false,
    services: false,
    pythonBackend: false
  };
  
  try {
    // Check Redis
    await req.services.redis.ping();
    checks.redis = true;
    
    // Check queues
    const queueHealth = await Promise.all([
      req.services.broadcast.broadcastQueue.isReady(),
      req.services.alert.alertQueue.isReady(),
      req.services.notification.notificationQueue.isReady()
    ]);
    checks.queues = queueHealth.every(h => h);
    
    // Check services initialized
    checks.services = req.services.websocket && 
                      req.services.broadcast && 
                      req.services.alert && 
                      req.services.notification;
    
    // Check Python backend
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 5000);
      const response = await fetch(`${req.config.pythonBackend.url}/health/live`, { signal: controller.signal });
      clearTimeout(timeout);
      checks.pythonBackend = response.ok;
    } catch {
      checks.pythonBackend = false;
    }
    
    const allHealthy = Object.values(checks).every(v => v);
    
    res.status(allHealthy ? 200 : 503).json({
      status: allHealthy ? 'ready' : 'not ready',
      checks,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(503).json({
      status: 'not ready',
      checks,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// Detailed health info
router.get('/', async (req, res) => {
  const memUsage = process.memoryUsage();
  const cpuUsage = process.cpuUsage();
  
  // Redis info
  let redisInfo = {};
  try {
    const info = await req.services.redis.info('memory');
    const lines = info.split('\r\n');
    for (const line of lines) {
      if (line.startsWith('used_memory_human:')) {
        redisInfo.memory = line.split(':')[1];
      }
    }
  } catch {}
  
  // Queue stats
  const queueStats = {
    broadcast: {
      waiting: await req.services.broadcast.broadcastQueue.getWaitingCount(),
      active: await req.services.broadcast.broadcastQueue.getActiveCount(),
      completed: await req.services.broadcast.broadcastQueue.getCompletedCount(),
      failed: await req.services.broadcast.broadcastQueue.getFailedCount()
    },
    alert: {
      waiting: await req.services.alert.alertQueue.getWaitingCount(),
      active: await req.services.alert.alertQueue.getActiveCount(),
      completed: await req.services.alert.alertQueue.getCompletedCount(),
      failed: await req.services.alert.alertQueue.getFailedCount()
    },
    notification: {
      waiting: await req.services.notification.notificationQueue.getWaitingCount(),
      active: await req.services.notification.notificationQueue.getActiveCount(),
      completed: await req.services.notification.notificationQueue.getCompletedCount(),
      failed: await req.services.notification.notificationQueue.getFailedCount()
    }
  };
  
  // Service states
  const serviceStates = {
    broadcast: req.services.broadcast.getState(),
    alert: req.services.alert.getState(),
    notification: req.services.notification.getState(),
    websocket: req.services.websocket.getState(),
    airport: req.services.airport.getState()
  };
  
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    version: req.config.app.version,
    environment: req.config.app.env,
    system: {
      platform: os.platform(),
      arch: os.arch(),
      nodeVersion: process.version,
      cpus: os.cpus().length,
      totalMemory: os.totalmem(),
      freeMemory: os.freemem(),
      loadAverage: os.loadavg()
    },
    process: {
      pid: process.pid,
      memory: {
        rss: `${Math.round(memUsage.rss / 1024 / 1024)} MB`,
        heapTotal: `${Math.round(memUsage.heapTotal / 1024 / 1024)} MB`,
        heapUsed: `${Math.round(memUsage.heapUsed / 1024 / 1024)} MB`,
        external: `${Math.round(memUsage.external / 1024 / 1024)} MB`
      },
      cpu: {
        user: cpuUsage.user,
        system: cpuUsage.system
      }
    },
    redis: redisInfo,
    queues: queueStats,
    services: serviceStates
  });
});

// Metrics endpoint (Prometheus format)
router.get('/metrics', async (req, res) => {
  const memUsage = process.memoryUsage();
  
  let metrics = '';
  
  // Process metrics
  metrics += `# HELP process_uptime_seconds Process uptime in seconds\n`;
  metrics += `# TYPE process_uptime_seconds gauge\n`;
  metrics += `process_uptime_seconds ${process.uptime()}\n\n`;
  
  metrics += `# HELP process_memory_bytes Process memory usage in bytes\n`;
  metrics += `# TYPE process_memory_bytes gauge\n`;
  metrics += `process_memory_bytes{type="rss"} ${memUsage.rss}\n`;
  metrics += `process_memory_bytes{type="heapTotal"} ${memUsage.heapTotal}\n`;
  metrics += `process_memory_bytes{type="heapUsed"} ${memUsage.heapUsed}\n`;
  metrics += `process_memory_bytes{type="external"} ${memUsage.external}\n\n`;
  
  // Queue metrics
  for (const [name, queue] of Object.entries({
    broadcast: req.services.broadcast.broadcastQueue,
    alert: req.services.alert.alertQueue,
    notification: req.services.notification.notificationQueue
  })) {
    const waiting = await queue.getWaitingCount();
    const active = await queue.getActiveCount();
    const completed = await queue.getCompletedCount();
    const failed = await queue.getFailedCount();
    
    metrics += `# HELP queue_jobs_total Total jobs in queue\n`;
    metrics += `# TYPE queue_jobs_total gauge\n`;
    metrics += `queue_jobs_total{queue="${name}",status="waiting"} ${waiting}\n`;
    metrics += `queue_jobs_total{queue="${name}",status="active"} ${active}\n`;
    metrics += `queue_jobs_total{queue="${name}",status="completed"} ${completed}\n`;
    metrics += `queue_jobs_total{queue="${name}",status="failed"} ${failed}\n\n`;
  }
  
  // Service metrics
  const broadcastMetrics = req.services.broadcast.getMetrics();
  metrics += `# HELP broadcast_messages_total Total broadcast messages\n`;
  metrics += `# TYPE broadcast_messages_total counter\n`;
  metrics += `broadcast_messages_total{sent} ${broadcastMetrics.totalSent}\n`;
  metrics += `broadcast_messages_total{delivered} ${broadcastMetrics.totalDelivered}\n`;
  metrics += `broadcast_messages_total{failed} ${broadcastMetrics.totalFailed}\n\n`;
  
  const wsState = req.services.websocket.getState();
  metrics += `# HELP websocket_connections_active Active WebSocket connections\n`;
  metrics += `# TYPE websocket_connections_active gauge\n`;
  metrics += `websocket_connections_active ${wsState.connections}\n\n`;
  
  metrics += `# HELP websocket_users_connected Connected users\n`;
  metrics += `# TYPE websocket_users_connected gauge\n`;
  metrics += `websocket_users_connected ${wsState.users}\n\n`;
  
  res.set('Content-Type', 'text/plain; version=0.0.4; charset=utf-8');
  res.send(metrics);
});

export default router;