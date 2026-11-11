/**
 * Airport Clearance Routes
 * 
 * API endpoints for airport fast-track clearance.
 */

import express from 'express';

const router = express.Router();

// Request airport clearance
router.post('/clearance', async (req, res) => {
  const { userId, airportCode, flightNumber, departureTime, destination, passportNumber, visaRequired, travelPurpose } = req.body;
  
  if (!userId || !airportCode || !flightNumber || !departureTime || !destination || !passportNumber) {
    return res.status(400).json({ error: 'Missing required fields' });
  }
  
  try {
    const clearance = await req.services.airport.requestClearance(userId, {
      airportCode,
      flightNumber,
      departureTime,
      destination,
      passportNumber,
      visaRequired,
      travelPurpose
    });
    
    res.json(clearance);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get clearance by ID
router.get('/clearance/:clearanceId', async (req, res) => {
  const { clearanceId } = req.params;
  
  const clearance = await req.services.airport.getClearance(clearanceId);
  
  if (!clearance) {
    return res.status(404).json({ error: 'Clearance not found' });
  }
  
  res.json(clearance);
});

// Get user clearances
router.get('/clearance/user/:userId', async (req, res) => {
  const { userId } = req.params;
  const { status = 'active' } = req.query;
  
  const clearances = await req.services.airport.getUserClearances(userId, status);
  
  res.json({ clearances, total: clearances.length });
});

// Process checkpoint
router.post('/clearance/:clearanceId/checkpoint', async (req, res) => {
  const { clearanceId } = req.params;
  const { checkpoint, scanData } = req.body;
  
  if (!checkpoint || !scanData) {
    return res.status(400).json({ error: 'checkpoint and scanData required' });
  }
  
  try {
    const result = await req.services.airport.processCheckpoint(clearanceId, checkpoint, scanData);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Cancel clearance
router.delete('/clearance/:clearanceId', async (req, res) => {
  const { clearanceId } = req.params;
  const { reason } = req.body;
  
  try {
    const clearance = await req.services.airport.cancelClearance(clearanceId, reason || 'User cancelled');
    res.json(clearance);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Verify QR code
router.post('/verify/qr', async (req, res) => {
  const { qrCode, airportCode } = req.body;
  
  if (!qrCode) {
    return res.status(400).json({ error: 'qrCode required' });
  }
  
  // Parse QR code
  try {
    if (!qrCode.startsWith('GOB-AIR:')) {
      return res.json({ valid: false, reason: 'Invalid QR format' });
    }
    
    const payload = JSON.parse(Buffer.from(qrCode.replace('GOB-AIR:', ''), 'base64').toString());
    
    // Verify signature
    const crypto = await import('crypto');
    const expectedSig = crypto.createHmac('sha256', req.config.airport.qrSecret).update(payload.cid).digest('hex').substring(0, 16);
    
    if (payload.sig !== expectedSig) {
      return res.json({ valid: false, reason: 'Invalid signature' });
    }
    
    // Get clearance
    const clearance = await req.services.airport.getClearance(payload.cid);
    
    if (!clearance) {
      return res.json({ valid: false, reason: 'Clearance not found' });
    }
    
    if (clearance.status !== 'active') {
      return res.json({ valid: false, reason: `Clearance is ${clearance.status}` });
    }
    
    const now = Date.now();
    if (now < clearance.validFrom) {
      return res.json({ valid: false, reason: 'Clearance not yet valid' });
    }
    if (now > clearance.validUntil) {
      return res.json({ valid: false, reason: 'Clearance expired' });
    }
    
    if (airportCode && clearance.airportCode !== airportCode) {
      return res.json({ valid: false, reason: 'Wrong airport' });
    }
    
    res.json({ 
      valid: true, 
      clearance: {
        id: clearance.id,
        userId: clearance.userId,
        grade: clearance.grade,
        label: clearance.label,
        flightNumber: clearance.flightNumber,
        autoGate: clearance.autoGate,
        biometricGate: clearance.biometricGate,
        vipLane: clearance.vipLane,
        lanes: clearance.lanes,
        checkpoints: clearance.checkpoints
      }
    });
  } catch (error) {
    res.json({ valid: false, reason: error.message });
  }
});

// Verify NFC token
router.post('/verify/nfc', async (req, res) => {
  const { nfcToken, airportCode } = req.body;
  
  if (!nfcToken) {
    return res.status(400).json({ error: 'nfcToken required' });
  }
  
  // Would lookup clearance by NFC token
  // For now, return not found
  res.json({ valid: false, reason: 'NFC token not found' });
});

// Get airport info
router.get('/airports', async (req, res) => {
  const airports = req.services.airport.getAllAirports();
  res.json({ airports, total: airports.length });
});

router.get('/airports/:airportCode', async (req, res) => {
  const { airportCode } = req.params;
  
  const airport = req.services.airport.getAirportInfo(airportCode.toUpperCase());
  
  if (!airport) {
    return res.status(404).json({ error: 'Airport not found' });
  }
  
  res.json(airport);
});

// Get clearance grades
router.get('/grades', async (req, res) => {
  const grades = req.services.airport.getAvailableGrades();
  res.json({ grades, total: grades.length });
});

router.get('/grades/:identityLevel', async (req, res) => {
  const { identityLevel } = req.params;
  
  const grade = req.services.airport.getClearanceGrade(parseInt(identityLevel));
  
  if (!grade) {
    return res.status(404).json({ error: 'Grade not found' });
  }
  
  res.json({ identityLevel: parseInt(identityLevel), ...grade });
});

// Get airport clearances (for airport staff)
router.get('/airport/:airportCode/clearances', async (req, res) => {
  const { airportCode } = req.params;
  const { flightNumber } = req.query;
  
  // Check authorization (would be middleware)
  const user = req.user;
  if (!user || (user.role !== 'admin' && user.role !== 'airport_staff')) {
    return res.status(403).json({ error: 'Insufficient permissions' });
  }
  
  const clearances = await req.services.airport.getAirportClearances(airportCode.toUpperCase(), flightNumber);
  
  res.json({ clearances, total: clearances.length });
});

// Service state
router.get('/state/overview', async (req, res) => {
  res.json(req.services.airport.getState());
});

export default router;