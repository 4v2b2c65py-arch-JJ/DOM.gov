import {
  clearPendingEmail,
  getPendingEmail,
  setSession,
  userFromEmail,
} from '../_auth.js'

export default function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' })
    return
  }

  const email = getPendingEmail(req)
  if (!email) {
    res.status(400).json({ error: 'No pending login. Request a code first.' })
    return
  }

  const { token } = req.body || {}
  if (String(token) !== '123456') {
    res.status(400).json({ error: 'Invalid code' })
    return
  }

  clearPendingEmail(res)
  setSession(res, email)
  res.status(200).json(userFromEmail(email))
}