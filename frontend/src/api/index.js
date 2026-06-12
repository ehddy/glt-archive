// 모든 요청은 /api 경로로 백엔드에 전달 (개발: Vite 프록시, 배포: nginx)
import { getClientId } from '../utils/clientId'

const API_BASE = import.meta.env.VITE_API_BASE || ''

const REQUEST_TIMEOUT_MS = 8000
const CHAT_TIMEOUT_MS = 60000
const AI_SEARCH_TIMEOUT_MS = 90000

function apiConnectionMessage(status) {
  if (status === 404) {
    return 'API를 찾을 수 없습니다. 백엔드가 실행 중인지 확인해 주세요.'
  }
  return `서버 응답 오류 (${status})`
}

async function parseJsonResponse(response) {
  const contentType = response.headers.get('content-type') || ''
  if (!contentType.includes('application/json')) {
    throw new Error(apiConnectionMessage(response.status))
  }
  return response.json()
}

async function request(path, options = {}, timeoutMs = REQUEST_TIMEOUT_MS) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        'X-Client-Id': getClientId(),
        ...options.headers,
      },
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
        throw new Error(message)
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
      throw new Error('응답 시간이 초과되었습니다.')
    }
    if (err instanceof TypeError) {
      throw new Error('API 서버에 연결할 수 없습니다. 백엔드가 실행 중인지 확인해 주세요.')
    }
    throw err
  } finally {
    clearTimeout(timer)
  }
}

export const api = {
  getLibrary() {
    return request('/api/library')
  },
  getLibraryStats() {
    return request('/api/library/stats')
  },
  getFeaturedBooks(limit = 20) {
    return request(`/api/library/featured?limit=${limit}`)
  },
  getBookmarkIds() {
    return request('/api/bookmarks/ids')
  },
  listBookmarks() {
    return request('/api/bookmarks')
  },
  addBookmark(quoteId) {
    return request(`/api/bookmarks/${quoteId}`, { method: 'POST' })
  },
  removeBookmark(quoteId) {
    return request(`/api/bookmarks/${quoteId}`, { method: 'DELETE' })
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
  listQuotes(skip = 0, limit = 100) {
    return request(`/api/quotes?skip=${skip}&limit=${limit}`)
  },
  searchQuotes(q, limit = 20) {
    return request(`/api/quotes/search?q=${encodeURIComponent(q)}&limit=${limit}`)
  },
  getQuote(id) {
    return request(`/api/quotes/${id}`)
  },
  getVersions(id) {
    return request(`/api/quotes/${id}/versions`)
  },
  createQuote(data) {
    return request('/api/quotes', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },
  updateQuote(id, data) {
    return request(`/api/quotes/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  },
  listAuthors() {
    return request('/api/authors')
  },
  searchAladinBooks(q, limit = 10) {
    return request(`/api/aladin/search?q=${encodeURIComponent(q)}&limit=${limit}`)
  },
  getAladinBook(itemId) {
    return request(`/api/aladin/books/${itemId}`)
  },
  importAladinBook(itemId) {
    return request(`/api/aladin/books/${itemId}`, { method: 'POST' })
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
