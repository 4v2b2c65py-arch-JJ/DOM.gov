import { clearSession } from '../_auth.js'

export default function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' })
    return
  }

  clearSession(res)
  res.status(200).json({ success: true })
}