/**
 * Configuration for Node Telecaster
 */

// Server
export const server = {
  port: parseInt(process.env.PORT) || 3001,
  host: process.env.HOST || '0.0.0.0',
  env: process.env.NODE_ENV || 'development'
};

// Redis
export const redis = {
  host: process.env.REDIS_HOST || 'localhost',
  port: parseInt(process.env.REDIS_PORT) || 6379,
  password: process.env.REDIS_PASSWORD || undefined,
  db: parseInt(process.env.REDIS_DB) || 1
};

// Python Backend API
export const pythonApi = {
  url: process.env.PYTHON_API_URL || 'http://localhost:8000',
  key: process.env.PYTHON_API_KEY || 'internal-service-key'
};

// CORS
export const corsOrigins = (process.env.CORS_ORIGINS || 'http://localhost:3000,http://localhost:8080').split(',');

// WhatsApp
export const whatsapp = {
  bsp: process.env.WHATSAPP_BSP || 'twilio',
  twilio: {
    accountSid: process.env.TWILIO_ACCOUNT_SID,
    authToken: process.env.TWILIO_AUTH_TOKEN,
    whatsappNumber: process.env.TWILIO_WHATSAPP_NUMBER
  }
};

// SMS Providers
export const sms = {
  claro: {
    apiUrl: process.env.CLARO_SMS_API_URL || 'https://api.claro.com.do/sms/v1',
    token: process.env.CLARO_SMS_TOKEN
  },
  altice: {
    apiUrl: process.env.ALTICE_SMS_API_URL || 'https://api.altice.com.do/sms/v1',
    token: process.env.ALTICE_SMS_TOKEN
  },
  viva: {
    apiUrl: process.env.VIVA_SMS_API_URL || 'https://api.viva.com.do/sms/v1',
    token: process.env.VIVA_SMS_TOKEN
  }
};

// USSD
export const ussd = {
  gatewayUrl: process.env.USSD_GATEWAY_URL || 'http://localhost:3002',
  code: process.env.USSD_CODE || '*462#'
};

// Cell Broadcast
export const cellBroadcast = {
  enabled: process.env.CELL_BROADCAST_ENABLED === 'true',
  coeApiUrl: process.env.COE_API_URL || 'https://api.coe.gob.do',
  indotelApiUrl: process.env.INDOTEL_API_URL || 'https://api.indotel.gob.do'
};

// Push Notifications
export const push = {
  firebase: {
    projectId: process.env.FIREBASE_PROJECT_ID,
    privateKey: process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
    clientEmail: process.env.FIREBASE_CLIENT_EMAIL
  },
  apns: {
    keyId: process.env.APNS_KEY_ID,
    teamId: process.env.APNS_TEAM_ID,
    privateKey: process.env.APNS_PRIVATE_KEY?.replace(/\\n/g, '\n')
  }
};

// Discord
export const discord = {
  botToken: process.env.DISCORD_BOT_TOKEN,
  guildId: process.env.DISCORD_GUILD_ID,
  announcementChannel: process.env.DISCORD_ANNOUNCEMENT_CHANNEL
};

// Magic Algorithm Courage
export const magic = {
  enabled: process.env.TELECASTER_MAGIC_ENABLED !== 'false',
  algoType: process.env.TELECASTER_ALGO_TYPE || 'courage',
  courageLevel: process.env.TELECASTER_COURAGE_LEVEL || 'maximum',
  broadcastIntervalMs: parseInt(process.env.TELECASTER_BROADCAST_INTERVAL_MS) || 1000,
  maxConcurrentBroadcasts: parseInt(process.env.TELECASTER_MAX_CONCURRENT_BROADCASTS) || 1000
};

// Security
export const security = {
  jwtSecret: process.env.JWT_SECRET || 'telecaster-jwt-secret-change-in-production',
  jwtExpiry: process.env.JWT_EXPIRY || '24h',
  apiKey: process.env.API_KEY || 'telecaster-api-key-change-in-production'
};

// Rate Limiting
export const rateLimit = {
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 60000,
  maxRequests: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 1000
};

// Monitoring
export const monitoring = {
  logLevel: process.env.LOG_LEVEL || 'info',
  metricsEnabled: process.env.METRICS_ENABLED !== 'false',
  prometheusPort: parseInt(process.env.PROMETHEUS_PORT) || 9091
};

// Main config object
export const config = {
  server,
  redis,
  pythonApi,
  corsOrigins,
  whatsapp,
  sms,
  ussd,
  cellBroadcast,
  push,
  discord,
  magic,
  security,
  rateLimit,
  monitoring
};

export default config;