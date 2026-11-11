/**
 * Telecaster Configuration
 * 
 * Centralized configuration for all telecaster services.
 */

// Load environment variables
import dotenv from 'dotenv';
dotenv.config();

export const config = {
  app: {
    name: 'gobernanza-rd-telecaster',
    version: '1.0.0',
    env: process.env.NODE_ENV || 'development',
    port: parseInt(process.env.PORT) || 3001,
    host: process.env.HOST || '0.0.0.0',
    apiPrefix: '/api'
  },

  cors: {
    origin: process.env.CORS_ORIGIN?.split(',') || ['http://localhost:3000', 'http://localhost:8000'],
    credentials: true
  },

  rateLimit: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    maxRequests: 1000
  },

  jwt: {
    secret: process.env.JWT_SECRET || 'gobernanza-rd-telecaster-secret-change-in-production',
    expiresIn: '24h',
    refreshExpiresIn: '7d',
    issuer: 'gobernanza-rd',
    audience: 'telecaster'
  },

  websocket: {
    path: '/ws',
    heartbeatInterval: 15000,
    heartbeatTimeout: 30000,
    maxConnections: 10000,
    pingInterval: 10000
  },

  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT) || 6379,
    password: process.env.REDIS_PASSWORD || undefined,
    db: parseInt(process.env.REDIS_DB) || 0,
    connectionName: 'telecaster',
    retryStrategy: (times) => Math.min(times * 50, 2000),
    maxRetriesPerRequest: 3,
    enableReadyCheck: true,
    lazyConnect: false
  },

  // BullMQ Queue Configuration
  queues: {
    broadcast: {
      name: 'telecaster:broadcast',
      defaultJobOptions: {
        removeOnComplete: 100,
        removeOnFail: 50,
        attempts: 3,
        backoff: { type: 'exponential', delay: 5000 }
      }
    },
    alert: {
      name: 'telecaster:alert',
      defaultJobOptions: {
        removeOnComplete: 50,
        removeOnFail: 20,
        attempts: 5,
        backoff: { type: 'exponential', delay: 10000 }
      }
    },
    notification: {
      name: 'telecaster:notification',
      defaultJobOptions: {
        removeOnComplete: 200,
        removeOnFail: 100,
        attempts: 3,
        backoff: { type: 'exponential', delay: 5000 }
      }
    }
  },

  // Telecom Providers
  telecom: {
    // Number Portability (INDOTEL)
    numberPortability: {
      enabled: true,
      apiUrl: process.env.NP_API_URL || 'https://np.indotel.gob.do/api',
      apiKey: process.env.NP_API_KEY,
      cacheTTL: 3600, // 1 hour
      fallbackCarriers: {
        '809': 'claro',
        '829': 'claro',
        '849': 'altice'
      }
    },

    // Carrier Direct APIs
    carriers: {
      claro: {
        enabled: true,
        apiUrl: process.env.CLARO_API_URL || 'https://api.claro.com.do',
        username: process.env.CLARO_USERNAME,
        password: process.env.CLARO_PASSWORD,
        senderId: 'GOBIERNO',
        priority: 1
      },
      altice: {
        enabled: true,
        apiUrl: process.env.ALTICE_API_URL || 'https://api.altice.com.do',
        apiKey: process.env.ALTICE_API_KEY,
        senderId: 'GOBIERNO',
        priority: 2
      },
      viva: {
        enabled: true,
        apiUrl: process.env.VIVA_API_URL || 'https://api.viva.com.do',
        apiKey: process.env.VIVA_API_KEY,
        senderId: 'GOBIERNO',
        priority: 3
      }
    },

    // SMS Aggregator (fallback)
    smsAggregator: {
      enabled: true,
      provider: process.env.SMS_PROVIDER || 'twilio', // twilio, vonage, messagebird
      twilio: {
        accountSid: process.env.TWILIO_ACCOUNT_SID,
        authToken: process.env.TWILIO_AUTH_TOKEN,
        fromNumber: process.env.TWILIO_FROM_NUMBER
      },
      vonage: {
        apiKey: process.env.VONAGE_API_KEY,
        apiSecret: process.env.VONAGE_API_SECRET,
        fromNumber: process.env.VONAGE_FROM_NUMBER
      },
      messagebird: {
        accessKey: process.env.MESSAGEBIRD_ACCESS_KEY,
        fromNumber: process.env.MESSAGEBIRD_FROM_NUMBER
      }
    },

    // WhatsApp Business API
    whatsapp: {
      enabled: true,
      provider: process.env.WHATSAPP_PROVIDER || 'twilio', // twilio, vonage, messagebird, gupshup
      twilio: {
        accountSid: process.env.TWILIO_ACCOUNT_SID,
        authToken: process.env.TWILIO_AUTH_TOKEN,
        fromNumber: process.env.TWILIO_WHATSAPP_FROM
      },
      vonage: {
        apiKey: process.env.VONAGE_API_KEY,
        apiSecret: process.env.VONAGE_API_SECRET,
        applicationId: process.env.VONAGE_APPLICATION_ID,
        privateKeyPath: process.env.VONAGE_PRIVATE_KEY_PATH
      },
      messagebird: {
        accessKey: process.env.MESSAGEBIRD_ACCESS_KEY,
        channelId: process.env.MESSAGEBIRD_WHATSAPP_CHANNEL_ID
      },
      gupshup: {
        apiKey: process.env.GUPSHUP_API_KEY,
        appName: process.env.GUPSHUP_APP_NAME,
        sourceNumber: process.env.GUPSHUP_SOURCE_NUMBER
      },
      webhookUrl: process.env.WHATSAPP_WEBHOOK_URL,
      verifyToken: process.env.WHATSAPP_VERIFY_TOKEN,
      templateNamespace: process.env.WHATSAPP_TEMPLATE_NAMESPACE
    },

    // USSD Gateway
    ussd: {
      enabled: true,
      shortCode: '*462#', // *GOB#
      provider: process.env.USSD_PROVIDER || 'africastalking', // africastalking, custom
      africastalking: {
        username: process.env.AT_USERNAME,
        apiKey: process.env.AT_API_KEY,
        shortCode: process.env.AT_SHORT_CODE || '462'
      },
      sessionTimeout: 180, // 3 minutes
      maxSessionsPerUser: 5
    },

    // Cell Broadcast (Emergency)
    cellBroadcast: {
      enabled: true,
      provider: 'indotel',
      apiUrl: process.env.CB_API_URL || 'https://cb.indotel.gob.do/api',
      apiKey: process.env.CB_API_KEY,
      defaultChannel: 50,
      maxMessageLength: 1395
    },

    // Communication Router (Channel Selection)
    router: {
      defaultChannels: ['whatsapp', 'sms', 'push'],
      priorityChannels: {
        emergency: ['cellBroadcast', 'sms', 'whatsapp', 'push', 'voice'],
        high: ['whatsapp', 'sms', 'push'],
        normal: ['whatsapp', 'push'],
        low: ['push']
      },
      fallbackOrder: ['whatsapp', 'sms', 'ussd', 'push', 'voice'],
      maxRetries: 3,
      retryDelay: 5000
    }
  },

  // Digital Wallets
  wallets: {
    applePay: {
      enabled: true,
      merchantId: process.env.APPLE_PAY_MERCHANT_ID,
      teamId: process.env.APPLE_PAY_TEAM_ID,
      keyId: process.env.APPLE_PAY_KEY_ID,
      privateKeyPath: process.env.APPLE_PAY_PRIVATE_KEY_PATH,
      certificatePath: process.env.APPLE_PAY_CERT_PATH,
      sandbox: process.env.NODE_ENV !== 'production'
    },
    googlePay: {
      enabled: true,
      merchantId: process.env.GOOGLE_PAY_MERCHANT_ID,
      merchantName: 'GobernanzaRD',
      environment: process.env.NODE_ENV === 'production' ? 'PRODUCTION' : 'TEST',
      gateway: 'example',
      gatewayMerchantId: process.env.GOOGLE_PAY_GATEWAY_MERCHANT_ID
    },
    supportedNetworks: ['visa', 'mastercard', 'amex', 'discover', 'unionpay'],
    supportedAuthMethods: ['pan_only', 'cryptogram_3ds'],
    drBanks: {
      'banco-popular': { name: 'Banco Popular', binPrefixes: ['4539', '4556', '5244'] },
      'banreservas': { name: 'Banreservas', binPrefixes: ['4567', '4917', '5278'] },
      'bhd-leon': { name: 'BHD León', binPrefixes: ['4532', '4654', '5423'] },
      'scotiabank': { name: 'Scotiabank', binPrefixes: ['4541', '4823', '5291'] },
      'banco-bdi': { name: 'Banco BDI', binPrefixes: ['4598', '4712', '5345'] },
      'banco-santa-cruz': { name: 'Banco Santa Cruz', binPrefixes: ['4612', '4789', '5412'] },
      'banco-caribe': { name: 'Banco Caribe', binPrefixes: ['4634', '4801', '5467'] },
      'asociacion-cibao': { name: 'Asociación Cibao', binPrefixes: ['4656', '4823', '5489'] },
      'asociacion-la-nacional': { name: 'La Nacional', binPrefixes: ['4678', '4845', '5501'] },
      'asociacion-la-vega': { name: 'La Vega Real', binPrefixes: ['4690', '4867', '5523'] }
    }
  },

  // Airport Clearance
  airport: {
    qrSecret: process.env.AIRPORT_QR_SECRET || 'gobernanza-rd-airport-qr-secret',
    nfcSecret: process.env.AIRPORT_NFC_SECRET || 'gobernanza-rd-airport-nfc-secret',
    defaultValidityHours: 6,
    maxClearancesPerUser: 10,
    biometricThreshold: 0.85,
    supportedAirports: ['SDQ', 'PUJ', 'STI', 'LRM', 'AZS'],
    integration: {
      dgii: { enabled: true, apiUrl: process.env.DGII_API_URL },
      jce: { enabled: true, apiUrl: process.env.JCE_API_URL },
      migration: { enabled: true, apiUrl: process.env.MIGRATION_API_URL },
      customs: { enabled: true, apiUrl: process.env.CUSTOMS_API_URL }
    }
  },

  // Python Backend Integration
  pythonBackend: {
    url: process.env.PYTHON_BACKEND_URL || 'http://localhost:8000',
    apiKey: process.env.PYTHON_BACKEND_API_KEY,
    timeout: 30000,
    endpoints: {
      auth: '/api/auth',
      users: '/api/users',
      merits: '/api/merits',
      payments: '/api/payments',
      quests: '/api/quests',
      veeduria: '/api/veeduria',
      governance: '/api/governance',
      audit: '/api/audit'
    }
  },

  // Monitoring
  monitoring: {
    prometheus: {
      enabled: true,
      port: 9090,
      path: '/metrics'
    },
    grafana: {
      enabled: true,
      url: process.env.GRAFANA_URL || 'http://localhost:3000'
    },
    logging: {
      level: process.env.LOG_LEVEL || 'info',
      format: 'json',
      destination: 'stdout'
    }
  },

  // Feature Flags
  features: {
    airportClearance: true,
    whatsappBusiness: true,
    ussdGateway: true,
    cellBroadcast: true,
    webSocket: true,
    pushNotifications: true,
    digitalWallet: true,
    magicAlgorithm: true,
    courageEngine: true,
    biometricAuth: true,
    nfcSupport: true
  }
};

export default config;