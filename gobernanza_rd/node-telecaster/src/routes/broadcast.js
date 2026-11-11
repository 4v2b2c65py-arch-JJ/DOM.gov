/**
 * Broadcast Routes
 * 
 * API endpoints for broadcast messaging.
 */

import express from 'express';
import crypto from 'crypto';

const router = express.Router();

// Send broadcast message
router.post('/', async (req, res) => {
  const { 
    message, 
    channels, 
    priority, 
    userId, 
    groupId, 
    templateKey, 
    templateParams,
    scheduledAt 
  } = req.body;
  
  if (!message && !templateKey) {
    return res.status(400).json({ error: 'message or templateKey required' });
  }
  
  try {
    let broadcastId;
    
    if (scheduledAt) {
      // Schedule for later
      const scheduled = new Date(scheduledAt).getTime();
      if (scheduled <= Date.now()) {
        return res.status(400).json({ error: 'scheduledAt must be in the future' });
      }
      
      broadcastId = await req.services.broadcast.scheduleBroadcast({
        message,
        channels,
        priority,
        userId,
        groupId,
        templateKey,
        templateParams
      }, scheduled);
      
      return res.json({ broadcastId, status: 'scheduled', scheduledAt: scheduled });
    }
    
    if (userId) {
      // Send to specific user
      broadcastId = await req.services.broadcast.broadcastToUser(userId, {
        message,
        channels,
        priority,
        templateKey,
        templateParams
      });
    } else if (groupId) {
      // Send to group
      const results = await req.services.broadcast.broadcastToGroup(groupId, {
        message,
        channels,
        priority,
        templateKey,
        templateParams
      });
      
      return res.json({ results, count: results.length });
    } else {
      // General broadcast
      broadcastId = await req.services.broadcast.broadcast({
        message,
        channels,
        priority,
        templateKey,
        templateParams
      });
    }
    
    res.json({ broadcastId, status: 'queued' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Emergency broadcast
router.post('/emergency', async (req, res) => {
  const { message, channels, type, areas, params } = req.body;
  
  if (!message) {
    return res.status(400).json({ error: 'message required' });
  }
  
  try {
    const broadcastId = await req.services.broadcast.emergencyBroadcast({
      message,
      channels: channels || ['cellBroadcast', 'sms', 'whatsapp', 'push'],
      type: type || 'emergency',
      areas: areas || [],
      params: params || {}
    });
    
    res.json({ broadcastId, status: 'delivering', priority: 'emergency' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get broadcast status
router.get('/:broadcastId', async (req, res) => {
  const { broadcastId } = req.params;
  
  const broadcast = req.services.broadcast.activeBroadcasts.get(broadcastId);
  
  if (!broadcast) {
    // Check history
    const history = await req.services.redis.hGet('broadcast:history', broadcastId);
    if (history) {
      return res.json(JSON.parse(history));
    }
    return res.status(404).json({ error: 'Broadcast not found' });
  }
  
  res.json(broadcast);
});

// Get broadcast confirmations
router.get('/:broadcastId/confirmations', async (req, res) => {
  const { broadcastId } = req.params;
  
  const confirmations = await req.services.redis.hGetAll('broadcast:confirmations');
  const filtered = {};
  
  for (const [key, value] of Object.entries(confirmations)) {
    if (key.startsWith(`${broadcastId}:`)) {
      filtered[key] = JSON.parse(value);
    }
  }
  
  res.json({ broadcastId, confirmations: filtered });
});

// Schedule broadcast
router.post('/schedule', async (req, res) => {
  const { message, channels, priority, userId, groupId, scheduledAt, templateKey, templateParams } = req.body;
  
  if (!scheduledAt) {
    return res.status(400).json({ error: 'scheduledAt required' });
  }
  
  const scheduled = new Date(scheduledAt).getTime();
  if (scheduled <= Date.now()) {
    return res.status(400).json({ error: 'scheduledAt must be in the future' });
  }
  
  try {
    const broadcastId = await req.services.broadcast.scheduleBroadcast({
      message,
      channels,
      priority,
      userId,
      groupId,
      templateKey,
      templateParams
    }, scheduled);
    
    res.json({ broadcastId, status: 'scheduled', scheduledAt: scheduled });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Cancel scheduled broadcast
router.delete('/schedule/:broadcastId', async (req, res) => {
  const { broadcastId } = req.params;
  
  const broadcast = req.services.broadcast.scheduledBroadcasts.get(broadcastId);
  if (!broadcast) {
    return res.status(404).json({ error: 'Scheduled broadcast not found' });
  }
  
  req.services.broadcast.scheduledBroadcasts.delete(broadcastId);
  await req.services.redis.hDel('broadcast:scheduled', broadcastId);
  
  res.json({ success: true, message: 'Scheduled broadcast cancelled' });
});

// Get broadcast metrics
router.get('/metrics/overview', async (req, res) => {
  const metrics = await req.services.redis.hGetAll('broadcast:metrics');
  
  res.json({
    totalSent: parseInt(metrics.totalSent) || 0,
    totalDelivered: parseInt(metrics.totalDelivered) || 0,
    totalFailed: parseInt(metrics.totalFailed) || 0,
    byChannel: metrics.byChannel ? JSON.parse(metrics.byChannel) : {},
    byPriority: metrics.byPriority ? JSON.parse(metrics.byPriority) : {},
    activeBroadcasts: req.services.broadcast.activeBroadcasts.size,
    scheduledBroadcasts: req.services.broadcast.scheduledBroadcasts.size
  });
});

// Get active broadcasts
router.get('/', async (req, res) => {
  const { status, limit = 50, offset = 0 } = req.query;
  
  let broadcasts = Array.from(req.services.broadcast.activeBroadcasts.values());
  
  if (status) {
    broadcasts = broadcasts.filter(b => b.status === status);
  }
  
  broadcasts = broadcasts
    .sort((a, b) => b.createdAt - a.createdAt)
    .slice(parseInt(offset), parseInt(offset) + parseInt(limit));
  
  res.json({ broadcasts, total: req.services.broadcast.activeBroadcasts.size });
});

export default router;