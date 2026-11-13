import { setPendingEmail } from '../_auth.js'

const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/

export default function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' })
    return
  }

  const { email } = req.body || {}
  if (!email || !EMAIL_RE.test(email)) {
    res.status(400).json({ error: 'Invalid email' })
    return
  }

  // Demo auth: there is no email provider configured, so the code is returned
  // to the caller. Replace with a real magic-link email in production.
  setPendingEmail(res, email)
  res.status(200).json({ success: true, code: '123456', email, expires_in: 600 })
}