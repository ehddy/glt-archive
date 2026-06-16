const STORAGE_KEY = 'ai-search-state'
const TTL_MS = 5 * 60 * 1000 // 5분

export function saveAiSearchState({ query, result, searched }) {
  if (!result) {
    sessionStorage.removeItem(STORAGE_KEY)
    return
  }

  sessionStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({ query, result, searched, savedAt: Date.now() }),
  )
}

export function loadAiSearchState() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const state = JSON.parse(raw)
    if (Date.now() - (state.savedAt ?? 0) > TTL_MS) {
      sessionStorage.removeItem(STORAGE_KEY)
      return null
    }
    return state
  } catch {
    return null
  }
}
