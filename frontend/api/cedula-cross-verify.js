const BARCODE_RE = /^CV\d{8}$/
const FALLBACK_CHECK_DIGITS = new Set([7])

function normalize(value) {
  return String(value || '').replace(/\D/g, '')
}

function luhn(cedula) {
  const digits = normalize(cedula)
  if (digits.length !== 11 && digits.length !== 12) {
    return { valid: false, fallbackValid: false, status: 'invalid', expected: null, actual: null, reason: 'length' }
  }

  let total = 0
  for (let i = 0; i < 10; i++) {
    let product = Number(digits[i]) * (i % 2 === 0 ? 1 : 2)
    if (product > 9) product = Math.floor(product / 10) + (product % 10)
    total += product
  }

  const expected = (10 - (total % 10)) % 10
  const actual = Number(digits[10])
  const valid = expected === actual
  const fallbackValid = !valid && FALLBACK_CHECK_DIGITS.has(actual)
  const extended = !valid && !fallbackValid
  const status = valid ? 'valid' : fallbackValid ? 'fallback' : extended ? 'extended' : 'invalid'
  return {
    valid,
    fallbackValid,
    extended,
    status,
    expected,
    actual,
    reason: valid ? '' : fallbackValid ? 'fallback' : extended ? 'extended' : 'check-digit',
  }
}

function mask(cedula) {
  const digits = normalize(cedula)
  if (digits.length < 4) return digits
  return `•••-•••-${digits.slice(-4)}`
}

export default function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' })
    return
  }

  const { cedula, barcode } = req.body || {}
  const digits = normalize(cedula)
  const checksum = luhn(digits)
  const barcodeValid = BARCODE_RE.test(String(barcode || '').toUpperCase())

  const expected = normalize(process.env.CEDULA_CROSS_VALIDATOR)
  const matchesCredential = expected ? digits === expected : null

  const formatValid = digits.length >= 11 && digits.length <= 12
  const accepted = checksum.valid || checksum.fallbackValid || checksum.extended
  const valid = formatValid && accepted && barcodeValid && (matchesCredential ?? true)

  res.status(200).json({
    valid,
    accepted,
    status: formatValid ? checksum.status : 'invalid',
    fallbackUsed: checksum.fallbackValid,
    extended: checksum.extended,
    maskedCedula: mask(digits),
    checks: {
      format: formatValid,
      checkDigit: checksum,
      barcode: barcodeValid,
      matchesCredential,
    },
  })
}