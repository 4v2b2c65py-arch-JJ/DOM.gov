/**
 * Alert Routes
 * 
 * API endpoints for high-priority alerts.
 */

import express from 'express';

const router = express.Router();

// Create alert
router.post('/', async (req, res) => {
  const { type, category, priority, title, message, userId, channels, params, metadata } = req.body;
  
  if (!type || !message) {
    return res.status(400).json({ error: 'type and message required' });
  }
  
  try {
    const result = await req.services.alert.createAlert({
      type,
      category: category || 'system',
      priority: priority || 'high',
      title,
      message,
      userId,
      channels,
      params,
      metadata
    });
    
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Emergency alert
router.post('/emergency', async (req, res) => {
  const { type, params, areas } = req.body;
  
  const validTypes = ['hurricane', 'flood', 'earthquake', 'tsunami'];
  if (!validTypes.includes(type)) {
    return res.status(400).json({ error: `Invalid emergency type. Valid: ${validTypes.join(', ')}` });
  }
  
  try {
    const result = await req.services.alert.createEmergencyAlert(type, params || {}, areas || []);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Governance alert
router.post('/governance', async (req, res) => {
  const { type, params } = req.body;
  
  const validTypes = ['consensus_decision', 'fga_action', 'circuit_breaker', 'fairness_violation'];
  if (!validTypes.includes(type)) {
    return res.status(400).json({ error: `Invalid governance alert type. Valid: ${validTypes.join(', ')}` });
  }
  
  try {
    const result = await req.services.alert.createGovernanceAlert(type, params || {});
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Citizen alert
router.post('/citizen', async (req, res) => {
  const { userId, type, params } = req.body;
  
  if (!userId || !type) {
    return res.status(400).json({ error: 'userId and type required' });
  }
  
  const validTypes = [
    'merit_threshold', 'payment_confirmed', 'quest_reminder', 
    'veeduria_alert', 'identity_escalation'
  ];
  if (!validTypes.includes(type)) {
    return res.status(400).json({ error: `Invalid citizen alert type. Valid: ${validTypes.join(', ')}` });
  }
  
  try {
    const result = await req.services.alert.createCitizenAlert(userId, type, params || {});
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get active alerts
router.get('/', async (req, res) => {
  const { category, status, limit = 100 } = req.query;
  
  let alerts = req.services.alert.getActiveAlerts();
  
  if (category) {
    alerts = alerts.filter(a => a.category === category);
  }
  if (status) {
    alerts = alerts.filter(a => a.status === status);
  }
  
  alerts = alerts
    .sort((a, b) => b.createdAt - a.createdAt)
    .slice(0, parseInt(limit));
  
  res.json({ alerts, total: req.services.alert.activeAlerts.size });
});

// Get alert history
router.get('/history', async (req, res) => {
  const { limit = 100 } = req.query;
  
  const history = req.services.alert.getAlertHistory(parseInt(limit));
  
  res.json({ alerts: history, total: history.length });
});

// Get alert by ID
router.get('/:alertId', async (req, res) => {
  const { alertId } = req.params;
  
  const alert = req.services.alert.activeAlerts.get(alertId);
  if (alert) {
    return res.json(alert);
  }
  
  // Check history
  const history = req.services.alert.getAlertHistory(1000);
  const found = history.find(a => a.id === alertId);
  
  if (found) {
    return res.json(found);
  }
  
  res.status(404).json({ error: 'Alert not found' });
});

// Suppression rules
router.post('/suppression', async (req, res) => {
  const { ruleId, rule } = req.body;
  
  if (!ruleId || !rule) {
    return res.status(400).json({ error: 'ruleId and rule required' });
  }
  
  try {
    await req.services.alert.addSuppressionRule(ruleId, rule);
    res.json({ success: true, ruleId });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.delete('/suppression/:ruleId', async (req, res) => {
  const { ruleId } = req.params;
  
  try {
    await req.services.alert.removeSuppressionRule(ruleId);
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/suppression', async (req, res) => {
  // Would return all suppression rules
  res.json({ rules: [] });
});

// Alert service state
router.get('/state/overview', async (req, res) => {
  res.json(req.services.alert.getState());
});

export default router;