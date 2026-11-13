/**
 * Dominican Cédula de Identidad y Electoral helpers.
 *
 * The cédula is validated by digit count: 11 or 12 digits are accepted
 * (the standard format is 3-3-3-2, e.g. 001-1234567-8).
 */

export const CEDULA_MIN_DIGITS = 11
export const CEDULA_MAX_DIGITS = 12

/** Strip everything that is not a digit. */
export function normalizeCedula(value: string | null | undefined): string {
  return (value ?? '').replace(/\D/g, '')
}

/** True when the value contains between 11 and 12 digits. */
export function isValidCedula(value: string | null | undefined): boolean {
  const digits = normalizeCedula(value)
  return digits.length >= CEDULA_MIN_DIGITS && digits.length <= CEDULA_MAX_DIGITS
}

/** Format digits as 3-3-3-2 (or 3-3-3-3 when 12 digits are provided). */
export function formatCedula(value: string | null | undefined): string {
  const digits = normalizeCedula(value).slice(0, CEDULA_MAX_DIGITS)
  if (digits.length <= 3) return digits
  if (digits.length <= 7) return `${digits.slice(0, 3)}-${digits.slice(3)}`
  if (digits.length <= 10) return `${digits.slice(0, 3)}-${digits.slice(3, 7)}-${digits.slice(7)}`
  return `${digits.slice(0, 3)}-${digits.slice(3, 7)}-${digits.slice(7, 10)}-${digits.slice(10)}`
}

/** Mask all but the last four digits for display/logging. */
export function maskCedula(value: string | null | undefined): string {
  const digits = normalizeCedula(value)
  if (digits.length < 4) return digits
  return `•••-•••-${digits.slice(-4)}`
}

/** Human-readable validation message, or an empty string when valid. */
export function cedulaValidationError(value: string | null | undefined): string {
  const digits = normalizeCedula(value)
  if (!digits) return 'La cédula es requerida.'
  if (digits.length < CEDULA_MIN_DIGITS || digits.length > CEDULA_MAX_DIGITS) {
    return `La cédula debe tener entre ${CEDULA_MIN_DIGITS} y ${CEDULA_MAX_DIGITS} dígitos.`
  }
  return ''
}