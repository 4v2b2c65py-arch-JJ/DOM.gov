/**
 * Logger Utility
 * 
 * Structured logging with Pino.
 */

import pino from 'pino';
import pinoPretty from 'pino-pretty';

const isDevelopment = process.env.NODE_ENV !== 'production';

let logger;

if (isDevelopment) {
  // Pretty print for development
  const stream = pinoPretty({
    colorize: true,
    translateTime: 'SYS:standard',
    ignore: 'pid,hostname',
    singleLine: false
  });
  
  logger = pino({
    level: process.env.LOG_LEVEL || 'debug',
    base: { service: 'telecaster' }
  }, stream);
} else {
  // JSON for production
  logger = pino({
    level: process.env.LOG_LEVEL || 'info',
    base: { service: 'telecaster' },
    formatters: {
      level: (label) => ({ level: label })
    },
    timestamp: pino.stdTimeFunctions.isoTime
  });
}

// Add convenience methods
logger.debug = (msg, obj) => logger.debug(obj, msg);
logger.info = (msg, obj) => logger.info(obj, msg);
logger.warn = (msg, obj) => logger.warn(obj, msg);
logger.error = (msg, obj) => logger.error(obj, msg);

export { logger };
export default logger;