import { getSessionEmail, userFromEmail } from '../_auth.js'

export default function handler(req, res) {
  const email = getSessionEmail(req)
  if (!email) {
    res.status(401).json({ error: 'Not authenticated' })
    return
  }

  res.status(200).json(userFromEmail(email))
}