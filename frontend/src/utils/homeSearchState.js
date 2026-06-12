const STORAGE_KEY = 'home-search-state'

export function saveHomeSearchState({ query, searchResults, searched }) {
  if (!searched) {
    sessionStorage.removeItem(STORAGE_KEY)
    return
  }

  sessionStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({ query, searchResults, searched }),
  )
}

export function loadHomeSearchState() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function clearHomeSearchState() {
  sessionStorage.removeItem(STORAGE_KEY)
}
