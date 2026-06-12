import { reactive } from 'vue'

const TOKEN_KEY = 'glt_access_token'

export const authState = reactive({
  user: null,
  ready: false,
})

export function getAccessToken() {
  try {
    return localStorage.getItem(TOKEN_KEY) || ''
  } catch {
    return ''
  }
}

export function setAccessToken(token) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token)
    else localStorage.removeItem(TOKEN_KEY)
  } catch {
    // ignore
  }
}

export function clearSession() {
  setAccessToken('')
  authState.user = null
}

export function isLoggedIn() {
  return !!getAccessToken() && !!authState.user
}

export async function loadAuthSession(api) {
  authState.ready = false
  const token = getAccessToken()
  if (!token) {
    authState.user = null
    authState.ready = true
    return null
  }

  try {
    authState.user = await api.getMe()
  } catch {
    clearSession()
  } finally {
    authState.ready = true
  }
  return authState.user
}

export function applyAuthResponse(res) {
  setAccessToken(res.access_token)
  authState.user = res.user
}

export function requireLogin(router, redirectPath) {
  if (isLoggedIn()) return true
  router.push({ name: 'login', query: { redirect: redirectPath } })
  return false
}
