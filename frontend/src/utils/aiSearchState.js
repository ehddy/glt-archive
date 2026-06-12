const STORAGE_KEY = 'ai-search-state'

export function saveAiSearchState({ query, result, searched }) {
  if (!result) {
    sessionStorage.removeItem(STORAGE_KEY)
    return
  }

  sessionStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({ query, result, searched }),
  )
}

export function loadAiSearchState() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}
