const BARCODE_RE = /^CV\d{8}$/

function normalize(value) {
  return String(value || '').replace(/\D/g, '')
}

function luhn(cedula) {
  const digits = normalize(cedula)
  if (digits.length !== 11 && digits.length !== 12) {
    return { valid: false, expected: null, actual: null, reason: 'length' }
  }

  let total = 0
  for (let i = 0; i < 10; i++) {
    let product = Number(digits[i]) * (i % 2 === 0 ? 1 : 2)
    if (product > 9) product = Math.floor(product / 10) + (product % 10)
    total += product
  }

  const expected = (10 - (total % 10)) % 10
  const actual = Number(digits[10])
  return {
    valid: expected === actual,
    expected,
    actual,
    reason: expected === actual ? '' : 'check-digit',
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
  const valid = formatValid && checksum.valid && barcodeValid && (matchesCredential ?? true)

  res.status(200).json({
    valid,
    maskedCedula: mask(digits),
    checks: {
      format: formatValid,
      checkDigit: checksum,
      barcode: barcodeValid,
      matchesCredential,
    },
  })
}