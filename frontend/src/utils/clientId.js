const STORAGE_KEY = 'glt_client_id'

function randomId() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  return `glt-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`
}

export function getClientId() {
  try {
    let id = localStorage.getItem(STORAGE_KEY)
    if (!id) {
      id = randomId()
      localStorage.setItem(STORAGE_KEY, id)
    }
    return id
  } catch {
    return randomId()
  }
}
