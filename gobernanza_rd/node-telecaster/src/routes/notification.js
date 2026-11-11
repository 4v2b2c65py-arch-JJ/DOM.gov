/**
 * Notification Routes
 * 
 * API endpoints for citizen notifications.
 */

import express from 'express';

const router = express.Router();

// Send notification to user
router.post('/', async (req, res) => {
  const { userId, templateKey, params, options } = req.body;
  
  if (!userId || !templateKey) {
    return res.status(400).json({ error: 'userId and templateKey required' });
  }
  
  try {
    const result = await req.services.notification.notify(userId, templateKey, params || {}, options || {});
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Bulk notification
router.post('/bulk', async (req, res) => {
  const { userIds, templateKey, params, options } = req.body;
  
  if (!userIds || !Array.isArray(userIds) || !templateKey) {
    return res.status(400).json({ error: 'userIds array and templateKey required' });
  }
  
  try {
    const results = await req.services.notification.notifyBulk(userIds, templateKey, params || {}, options || {});
    res.json({ results, total: userIds.length, successful: results.filter(r => r.success !== false).length });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Group notification
router.post('/group/:groupId', async (req, res) => {
  const { groupId } = req.params;
  const { templateKey, params, options } = req.body;
  
  if (!templateKey) {
    return res.status(400).json({ error: 'templateKey required' });
  }
  
  try {
    const results = await req.services.notification.notifyGroup(groupId, templateKey, params || {}, options || {});
    res.json({ results, total: results.length });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get user notification history
router.get('/user/:userId/history', async (req, res) => {
  const { userId } = req.params;
  const { limit = 50 } = req.query;
  
  const history = req.services.notification.getNotificationHistory(userId, parseInt(limit));
  
  res.json({ notifications: history, total: history.length });
});

// Get all notification history
router.get('/history', async (req, res) => {
  const { limit = 100 } = req.query;
  
  const history = req.services.notification.getNotificationHistory(null, parseInt(limit));
  
  res.json({ notifications: history, total: history.length });
});

// Get available templates
router.get('/templates', async (req, res) => {
  const templates = req.services.notification.getTemplates();
  
  res.json({ templates, total: templates.length });
});

// Get user preferences
router.get('/preferences/:userId', async (req, res) => {
  const { userId } = req.params;
  
  const preferences = await req.services.notification.getUserPreferences(userId);
  
  res.json({ userId, preferences });
});

// Update user preferences
router.put('/preferences/:userId', async (req, res) => {
  const { userId } = req.params;
  const { preferences } = req.body;
  
  if (!preferences) {
    return res.status(400).json({ error: 'preferences required' });
  }
  
  try {
    await req.services.notification.setUserPreferences(userId, preferences);
    res.json({ success: true, userId });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Update single preference
router.patch('/preferences/:userId/:key', async (req, res) => {
  const { userId, key } = req.params;
  const { value } = req.body;
  
  if (value === undefined) {
    return res.status(400).json({ error: 'value required' });
  }
  
  try {
    await req.services.notification.updateUserPreference(userId, key, value);
    res.json({ success: true, userId, key, value });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Notification service state
router.get('/state/overview', async (req, res) => {
  res.json(req.services.notification.getState());
});

export default router;