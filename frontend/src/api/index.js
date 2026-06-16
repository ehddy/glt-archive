// 모든 요청은 /api 경로로 백엔드에 전달 (개발: Vite 프록시, 배포: nginx)
import { getAccessToken } from '../utils/auth'
import { dbRequestQueue } from './requestQueue'

const API_BASE = import.meta.env.VITE_API_BASE || ''

const REQUEST_TIMEOUT_MS = 30000
const CHAT_TIMEOUT_MS = 120000
const AI_SEARCH_TIMEOUT_MS = 120000

function shouldUseQueue(path, options = {}) {
  if (path.includes('/chat') || path.includes('/ai-search')) return false
  if (path.includes('/api/likes/') && (options.method || 'GET').toUpperCase() !== 'GET') {
    return false
  }
  if (path.includes('/api/scraps/') && (options.method || 'GET').toUpperCase() !== 'GET') {
    return false
  }
  if (path.includes('/api/auth/') && (options.method || 'GET').toUpperCase() !== 'GET') {
    return false
  }
  const method = (options.method || 'GET').toUpperCase()
  return method === 'GET' || method === 'HEAD'
}

async function parseJsonResponse(response) {
  const contentType = response.headers.get('content-type') || ''
  if (!contentType.includes('application/json')) {
    throw new Error(apiConnectionMessage(response.status))
  }
  return response.json()
}

function apiConnectionMessage(status) {
  if (status === 404) {
    return '서버 API를 찾을 수 없어요. 백엔드를 재시작해 주세요.'
  }
  return `서버 응답 오류 (${status})`
}

function normalizeApiError(message, status) {
  if (status === 404 && (message === 'Not Found' || message === 'not found')) {
    return '서버 API를 찾을 수 없어요. 백엔드를 재시작해 주세요.'
  }
  return message
}

function shouldBypassBrowserCache(path, options = {}) {
  const method = (options.method || 'GET').toUpperCase()
  if (method !== 'GET' && method !== 'HEAD') return false
  if (!getAccessToken()) return false
  return (
    path.startsWith('/api/home')
    || path.startsWith('/api/likes')
    || path.startsWith('/api/scraps')
    || path.startsWith('/api/quotes/search')
  )
}

async function requestRaw(path, options = {}, timeoutMs = REQUEST_TIMEOUT_MS) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)
  const token = getAccessToken()
  const bypassCache = shouldBypassBrowserCache(path, options)

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
      cache: bypassCache ? 'no-store' : 'default',
      signal: controller.signal,
      ...options,
    })

    if (!response.ok) {
      try {
        const error = await parseJsonResponse(response)
        const detail = error.detail
        const message = typeof detail === 'string'
          ? detail
          : Array.isArray(detail)
            ? detail.map((d) => d.msg).join(', ')
            : apiConnectionMessage(response.status)
        throw new Error(normalizeApiError(message, response.status))
      } catch (parseErr) {
        if (parseErr.message && !parseErr.message.startsWith('서버 응답') && !parseErr.message.startsWith('API를')) {
          throw parseErr
        }
        throw new Error(apiConnectionMessage(response.status))
      }
    }

    if (response.status === 204) return null
    return parseJsonResponse(response)
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error('응답이 늦어졌어요.')
    }
    if (err instanceof TypeError) {
      throw new Error('서버에 연결하지 못했어요.')
    }
    throw err
  } finally {
    clearTimeout(timer)
  }
}

function request(path, options = {}, timeoutMs = REQUEST_TIMEOUT_MS) {
  const exec = () => requestRaw(path, options, timeoutMs)
  if (shouldUseQueue(path, options)) {
    return dbRequestQueue.enqueue(exec)
  }
  return exec()
}

export const api = {
  register({ email, password, name }) {
    return request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    })
  },
  login({ email, password }) {
    return request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
  },
  getMe() {
    return request('/api/auth/me')
  },
  getHome({ featuredLimit = 10, quoteLimit = 12 } = {}) {
    return request(
      `/api/home?featured_limit=${featuredLimit}&quote_limit=${quoteLimit}`,
    )
  },
  getLikeIds() {
    return request('/api/likes/ids')
  },
  listLikes() {
    return request('/api/likes')
  },
  addLike(quoteId) {
    return request(`/api/likes/${quoteId}`, { method: 'POST' })
  },
  removeLike(quoteId) {
    return request(`/api/likes/${quoteId}`, { method: 'DELETE' })
  },
  getScrapIds() {
    return request('/api/scraps/ids')
  },
  listScraps() {
    return request('/api/scraps')
  },
  getUser(userId) {
    return request(`/api/users/${userId}`)
  },
  getUserQuotes(userId, { skip = 0, limit = 20 } = {}) {
    return request(`/api/users/${userId}/quotes?skip=${skip}&limit=${limit}`)
  },
  getUserNovels(userId) {
    return request(`/api/users/${userId}/novels`)
  },
  getUserScraps(userId, { skip = 0, limit = 20 } = {}) {
    return request(`/api/users/${userId}/scraps?skip=${skip}&limit=${limit}`)
  },
  listScrappedNovels() {
    return request('/api/scraps/novels')
  },
  getFeaturedNovels(userId) {
    return request(`/api/users/${userId}/featured-novels`)
  },
  setFeaturedNovels(userId, novelIds) {
    return request(`/api/users/${userId}/featured-novels`, {
      method: 'PUT',
      body: JSON.stringify({ novel_ids: novelIds }),
    })
  },
  addScrap(quoteId) {
    return request(`/api/scraps/${quoteId}`, { method: 'POST' })
  },
  removeScrap(quoteId) {
    return request(`/api/scraps/${quoteId}`, { method: 'DELETE' })
  },
  getStatsOverview() {
    return request('/api/stats/overview')
  },
  getNovel(id) {
    return request(`/api/novels/${id}`)
  },
  browseNovels({ q, skip = 0, limit = 24 } = {}) {
    const params = new URLSearchParams()
    if (q) params.set('q', q)
    params.set('skip', String(skip))
    params.set('limit', String(limit))
    return request(`/api/novels?${params}`)
  },
  browseQuotes({ q, novelId, skip = 0, limit = 20 } = {}) {
    const params = new URLSearchParams()
    if (q) params.set('q', q)
    if (novelId) params.set('novel_id', String(novelId))
    params.set('skip', String(skip))
    params.set('limit', String(limit))
    return request(`/api/quotes/browse?${params}`)
  },
  searchQuotes(q, limit = 20) {
    return request(`/api/quotes/search?q=${encodeURIComponent(q)}&limit=${limit}`)
  },
  getQuote(id) {
    return request(`/api/quotes/${id}`)
  },
  createQuote(data) {
    return request('/api/quotes', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },
  searchAladinBooks(q, limit = 20) {
    return request(`/api/aladin/search?q=${encodeURIComponent(q)}&limit=${limit}`)
  },
  getAladinBook(itemId) {
    return request(`/api/aladin/books/${itemId}`)
  },
  chat(message, history = []) {
    return request('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message, history }),
    }, CHAT_TIMEOUT_MS)
  },
  aiSearch(q) {
    return request('/api/ai-search', {
      method: 'POST',
      body: JSON.stringify({ q }),
    }, AI_SEARCH_TIMEOUT_MS)
  },
}
