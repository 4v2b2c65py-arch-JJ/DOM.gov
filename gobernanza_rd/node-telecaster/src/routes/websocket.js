/**
 * WebSocket Routes
 * 
 * HTTP endpoints for WebSocket service management.
 */

import express from 'express';

const router = express.Router();

// Get WebSocket service state
router.get('/state', async (req, res) => {
  res.json(req.services.websocket.getState());
});

// Get connection count
router.get('/connections/count', async (req, res) => {
  res.json({ count: req.services.websocket.getConnectionCount() });
});

// Get user connections
router.get('/connections/user/:userId', async (req, res) => {
  const { userId } = req.params;
  
  const count = req.services.websocket.getUserConnectionCount(userId);
  const connections = req.services.websocket.getUserConnections(userId);
  
  res.json({ userId, count, connections: Array.from(connections) });
});

// Get topic subscribers
router.get('/topics/:topic/subscribers', async (req, res) => {
  const { topic } = req.params;
  
  const count = req.services.websocket.getTopicSubscribers(topic);
  
  res.json({ topic, count });
});

// Get user presence
router.get('/presence/:userId', async (req, res) => {
  const { userId } = req.params;
  
  const presence = req.services.websocket.getPresence(userId);
  
  res.json({ userId, presence });
});

// Broadcast to topic (admin only)
router.post('/broadcast/topic', async (req, res) => {
  const { topic, payload, options } = req.body;
  
  if (!topic || !payload) {
    return res.status(400).json({ error: 'topic and payload required' });
  }
  
  // Check admin permission
  const user = req.user; // Would come from auth middleware
  if (!user || (user.role !== 'admin' && user.role !== 'fga_member')) {
    return res.status(403).json({ error: 'Insufficient permissions' });
  }
  
  try {
    const sent = await req.services.websocket.broadcastToTopic(topic, payload, options || {});
    res.json({ success: true, sent });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Broadcast to user
router.post('/broadcast/user/:userId', async (req, res) => {
  const { userId } = req.params;
  const { payload } = req.body;
  
  if (!payload) {
    return res.status(400).json({ error: 'payload required' });
  }
  
  try {
    const sent = await req.services.websocket.sendToUser(userId, payload);
    res.json({ success: true, sent });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Broadcast to all
router.post('/broadcast/all', async (req, res) => {
  const { payload, options } = req.body;
  
  if (!payload) {
    return res.status(400).json({ error: 'payload required' });
  }
  
  // Check admin permission
  const user = req.user;
  if (!user || user.role !== 'admin') {
    return res.status(403).json({ error: 'Admin only' });
  }
  
  try {
    const sent = await req.services.websocket.broadcastToAll(payload, options || {});
    res.json({ success: true, sent });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Broadcast to role
router.post('/broadcast/role/:role', async (req, res) => {
  const { role } = req.params;
  const { payload } = req.body;
  
  if (!payload) {
    return res.status(400).json({ error: 'payload required' });
  }
  
  // Check admin permission
  const user = req.user;
  if (!user || user.role !== 'admin') {
    return res.status(403).json({ error: 'Admin only' });
  }
  
  try {
    const sent = await req.services.websocket.broadcastToRole(role, payload);
    res.json({ success: true, sent });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Disconnect user (admin)
router.delete('/connections/user/:userId', async (req, res) => {
  const { userId } = req.params;
  
  const user = req.user;
  if (!user || user.role !== 'admin') {
    return res.status(403).json({ error: 'Admin only' });
  }
  
  // Would implement connection termination
  res.json({ success: true, message: 'User connections terminated' });
});

export default router;