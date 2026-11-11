/**
 * Redis Client Setup
 * 
 * Configured Redis clients for telecaster.
 */

import { createClient } from 'redis';
import { Queue } from 'bullmq';
import { config } from '../config.js';
import { logger } from './logger.js';

// Main Redis client
export const redisClient = createClient({
  socket: {
    host: config.redis.host,
    port: config.redis.port,
    reconnectStrategy: config.redis.retryStrategy
  },
  password: config.redis.password,
  database: config.redis.db,
  name: config.redis.connectionName
});

redisClient.on('error', (err) => logger.error('Redis client error', { error: err.message }));
redisClient.on('connect', () => logger.info('Redis client connected'));
redisClient.on('ready', () => logger.info('Redis client ready'));
redisClient.on('reconnecting', () => logger.warn('Redis client reconnecting'));

// Publisher client (for pub/sub)
export const redisPublisher = createClient({
  socket: {
    host: config.redis.host,
    port: config.redis.port
  },
  password: config.redis.password,
  database: config.redis.db,
  name: 'telecaster-publisher'
});

redisPublisher.on('error', (err) => logger.error('Redis publisher error', { error: err.message }));

// Subscriber client (for pub/sub)
export const redisSubscriber = createClient({
  socket: {
    host: config.redis.host,
    port: config.redis.port
  },
  password: config.redis.password,
  database: config.redis.db,
  name: 'telecaster-subscriber'
});

redisSubscriber.on('error', (err) => logger.error('Redis subscriber error', { error: err.message }));

// BullMQ connection options
const bullmqConnection = {
  host: config.redis.host,
  port: config.redis.port,
  password: config.redis.password,
  db: config.redis.db,
  maxRetriesPerRequest: config.redis.maxRetriesPerRequest,
  enableReadyCheck: config.redis.enableReadyCheck,
  lazyConnect: config.redis.lazyConnect
};

// BullMQ Queues
export const broadcastQueue = new Queue(config.queues.broadcast.name, {
  connection: bullmqConnection,
  defaultJobOptions: config.queues.broadcast.defaultJobOptions
});

export const alertQueue = new Queue(config.queues.alert.name, {
  connection: bullmqConnection,
  defaultJobOptions: config.queues.alert.defaultJobOptions
});

export const notificationQueue = new Queue(config.queues.notification.name, {
  connection: bullmqConnection,
  defaultJobOptions: config.queues.notification.defaultJobOptions
});

// Queue event handlers
[broadcastQueue, alertQueue, notificationQueue].forEach(queue => {
  queue.on('error', (err) => logger.error(`Queue ${queue.name} error`, { error: err.message }));
  queue.on('waiting', (jobId) => logger.debug(`Job waiting`, { queue: queue.name, jobId }));
  queue.on('active', (job) => logger.debug(`Job active`, { queue: queue.name, jobId: job.id }));
  queue.on('completed', (job) => logger.debug(`Job completed`, { queue: queue.name, jobId: job.id }));
  queue.on('failed', (job, err) => logger.error(`Job failed`, { queue: queue.name, jobId: job.id, error: err.message }));
});

// Initialize connections
export async function initRedis() {
  await Promise.all([
    redisClient.connect(),
    redisPublisher.connect(),
    redisSubscriber.connect()
  ]);
  
  logger.info('All Redis connections established');
}

// Graceful shutdown
export async function closeRedis() {
  await Promise.all([
    redisClient.quit(),
    redisPublisher.quit(),
    redisSubscriber.quit(),
    broadcastQueue.close(),
    alertQueue.close(),
    notificationQueue.close()
  ]);
  
  logger.info('All Redis connections closed');
}

export default {
  redisClient,
  redisPublisher,
  redisSubscriber,
  broadcastQueue,
  alertQueue,
  notificationQueue,
  initRedis,
  closeRedis
};