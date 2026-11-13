import crypto from 'node:crypto'

const SECRET = process.env.AUTH_SECRET || 'dom-gov-local-demo-secret-change-me'
const SESSION_COOKIE = 'dom_session'
const PENDING_COOKIE = 'dom_pending'
const MAX_AGE = 60 * 60 * 24 * 30

function sign(payload) {
  const body = Buffer.from(JSON.stringify(payload)).toString('base64url')
  const signature = crypto.createHmac('sha256', SECRET).update(body).digest('base64url')
  return `${body}.${signature}`
}

function verify(token) {
  if (!token || !token.includes('.')) return null
  const [body, signature] = token.split('.')
  const expected = crypto.createHmac('sha256', SECRET).update(body).digest('base64url')
  const a = Buffer.from(signature)
  const b = Buffer.from(expected)
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null
  try {
    return JSON.parse(Buffer.from(body, 'base64url').toString('utf8'))
  } catch {
    return null
  }
}

function readCookie(req, name) {
  const header = req.headers.cookie || ''
  const match = header
    .split(';')
    .map((part) => part.trim())
    .find((part) => part.startsWith(`${name}=`))
  return match ? match.slice(name.length + 1) : null
}

export function setPendingEmail(res, email) {
  const token = sign({ email, iat: Date.now() })
  res.setHeader(
    'Set-Cookie',
    `${PENDING_COOKIE}=${token}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=600`
  )
}

export function getPendingEmail(req) {
  const token = readCookie(req, PENDING_COOKIE)
  const payload = token ? verify(token) : null
  return payload?.email || null
}

export function clearPendingEmail(res) {
  res.setHeader(
    'Set-Cookie',
    `${PENDING_COOKIE}=; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=0`
  )
}

export function setSession(res, email) {
  const token = sign({ email, iat: Date.now() })
  res.setHeader(
    'Set-Cookie',
    `${SESSION_COOKIE}=${token}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=${MAX_AGE}`
  )
}

export function getSessionEmail(req) {
  const token = readCookie(req, SESSION_COOKIE)
  const payload = token ? verify(token) : null
  return payload?.email || null
}

export function clearSession(res) {
  res.setHeader(
    'Set-Cookie',
    `${SESSION_COOKIE}=; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=0`
  )
}

export function userFromEmail(email) {
  return {
    id: `local-${Buffer.from(email).toString('base64url').slice(0, 12)}`,
    email,
    identity_level: 1,
    merit_balance: 0,
    veeduria_score: 0,
    trust_score: 0,
    biometric_verified: false,
    created_at: new Date().toISOString(),
    capabilities: ['view_public', 'vote_proposals', 'report_issues'],
  }
}