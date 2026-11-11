/**
 * Auth Routes
 * 
 * Authentication endpoints for telecaster service.
 */

import express from 'express';
import jwt from 'jsonwebtoken';
import crypto from 'crypto';

const router = express.Router();

// Generate JWT token for WebSocket connection
router.post('/token', async (req, res) => {
  const { userId, identityLevel, role, permissions } = req.body;
  
  if (!userId) {
    return res.status(400).json({ error: 'userId required' });
  }
  
  // In production, verify user exists and get actual role/level
  const payload = {
    sub: userId,
    identityLevel: identityLevel || 0,
    role: role || 'citizen',
    permissions: permissions || ['notifications:receive'],
    iat: Math.floor(Date.now() / 1000)
  };
  
  const token = jwt.sign(payload, req.config.jwt.secret, {
    expiresIn: req.config.jwt.expiresIn,
    issuer: req.config.jwt.issuer,
    audience: req.config.jwt.audience
  });
  
  const refreshToken = crypto.randomBytes(64).toString('hex');
  
  // Store refresh token
  await req.services.redis.setEx(
    `auth:refresh:${refreshToken}`,
    7 * 24 * 3600,
    JSON.stringify({ userId, identityLevel: payload.identityLevel })
  );
  
  res.json({
    accessToken: token,
    refreshToken,
    expiresIn: req.config.jwt.expiresIn,
    tokenType: 'Bearer',
    user: {
      id: userId,
      identityLevel: payload.identityLevel,
      role: payload.role
    }
  });
});

// Refresh access token
router.post('/refresh', async (req, res) => {
  const { refreshToken } = req.body;
  
  if (!refreshToken) {
    return res.status(400).json({ error: 'refreshToken required' });
  }
  
  const stored = await req.services.redis.get(`auth:refresh:${refreshToken}`);
  if (!stored) {
    return res.status(401).json({ error: 'Invalid refresh token' });
  }
  
  const { userId, identityLevel } = JSON.parse(stored);
  
  const payload = {
    sub: userId,
    identityLevel,
    role: 'citizen',
    permissions: ['notifications:receive'],
    iat: Math.floor(Date.now() / 1000)
  };
  
  const token = jwt.sign(payload, req.config.jwt.secret, {
    expiresIn: req.config.jwt.expiresIn,
    issuer: req.config.jwt.issuer,
    audience: req.config.jwt.audience
  });
  
  const newRefreshToken = crypto.randomBytes(64).toString('hex');
  
  // Rotate refresh token
  await req.services.redis.del(`auth:refresh:${refreshToken}`);
  await req.services.redis.setEx(
    `auth:refresh:${newRefreshToken}`,
    7 * 24 * 3600,
    JSON.stringify({ userId, identityLevel })
  );
  
  res.json({
    accessToken: token,
    refreshToken: newRefreshToken,
    expiresIn: req.config.jwt.expiresIn,
    tokenType: 'Bearer'
  });
});

// Verify token
router.post('/verify', async (req, res) => {
  const { token } = req.body;
  
  if (!token) {
    return res.status(400).json({ error: 'token required' });
  }
  
  try {
    const decoded = jwt.verify(token, req.config.jwt.secret, {
      issuer: req.config.jwt.issuer,
      audience: req.config.jwt.audience
    });
    
    // Check if user is still active
    const active = await req.services.redis.get(`user:active:${decoded.sub}`);
    
    res.json({
      valid: !!active,
      user: {
        id: decoded.sub,
        identityLevel: decoded.identityLevel,
        role: decoded.role,
        permissions: decoded.permissions
      }
    });
  } catch (error) {
    res.status(401).json({ valid: false, error: error.message });
  }
});

// Revoke token (logout)
router.post('/revoke', async (req, res) => {
  const { refreshToken } = req.body;
  
  if (refreshToken) {
    await req.services.redis.del(`auth:refresh:${refreshToken}`);
  }
  
  res.json({ success: true, message: 'Token revoked' });
});

// Get user capabilities based on identity level
router.get('/capabilities/:userId', async (req, res) => {
  const { userId } = req.params;
  
  const capabilities = {
    0: ['anonymous_browsing', 'public_info'],
    1: ['anonymous_browsing', 'public_info', 'email_verified', 'basic_notifications', 'precheck_airport'],
    2: ['anonymous_browsing', 'public_info', 'email_verified', 'basic_notifications', 'precheck_airport', 'merit_accumulation', 'trusted_traveler', 'selecting_front', 'quest_participation', 'veeduria_filing'],
    3: ['anonymous_browsing', 'public_info', 'email_verified', 'basic_notifications', 'precheck_airport', 'merit_accumulation', 'trusted_traveler', 'selecting_front', 'quest_participation', 'veeduria_filing', 'biometric_auth', 'biometric_airport', 'ego_gate', 'governance_participation', 'consensus_voting'],
    4: ['all', 'vip_airport', 'dedicated_officer', 'fga_oversight', 'policy_proposal', 'budget_allocation'],
    5: ['all', 'sovereign_airport', 'state_protocol', 'immunity', 'constitutional_action']
  };
  
  // Get user identity level from auth service or cache
  const userData = await req.services.redis.get(`user:profile:${userId}`);
  const identityLevel = userData ? JSON.parse(userData).identityLevel || 0 : 0;
  
  res.json({
    userId,
    identityLevel,
    capabilities: capabilities[identityLevel] || capabilities[0],
    nextLevel: identityLevel < 5 ? identityLevel + 1 : null,
    nextLevelCapabilities: capabilities[identityLevel + 1] || null
  });
});

// WebSocket connection info
router.get('/websocket/info', (req, res) => {
  res.json({
    path: req.config.websocket.path,
    auth: 'JWT token required via query param "token" or Authorization header',
    protocols: ['json'],
    heartbeat: {
      interval: req.config.websocket.heartbeatInterval,
      timeout: req.config.websocket.heartbeatTimeout
    },
    maxConnections: req.config.websocket.maxConnections
  });
});

export default router;