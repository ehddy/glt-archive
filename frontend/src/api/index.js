// 모든 요청은 /api 경로로 백엔드에 전달 (개발: Vite 프록시, 배포: nginx)
const API_BASE = import.meta.env.VITE_API_BASE || ''

const REQUEST_TIMEOUT_MS = 8000

async function request(path, options = {}) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      signal: controller.signal,
      ...options,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      const detail = error.detail
      const message = typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
          ? detail.map((d) => d.msg).join(', ')
          : '요청에 실패했습니다.'
      throw new Error(
        message === 'Not Found'
          ? '서버 API를 찾을 수 없습니다. 백엔드를 재시작해 주세요.'
          : message
      )
    }

    if (response.status === 204) return null
    return response.json()
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error('서버 응답 시간이 초과되었습니다. 백엔드가 실행 중인지 확인해 주세요.')
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
}
