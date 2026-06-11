const STORAGE_KEY = 'glt-saved-quote-ids'

export function getSavedQuoteIds() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    const parsed = raw ? JSON.parse(raw) : []
    return Array.isArray(parsed) ? parsed.filter((id) => Number.isInteger(id)) : []
  } catch {
    return []
  }
}

export function isQuoteSaved(quoteId) {
  return getSavedQuoteIds().includes(quoteId)
}

export function toggleQuoteSaved(quoteId) {
  const ids = getSavedQuoteIds()
  const next = ids.includes(quoteId)
    ? ids.filter((id) => id !== quoteId)
    : [...ids, quoteId]
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
  return next.includes(quoteId)
}
