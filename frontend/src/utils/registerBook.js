export function novelToSelectedBook(novel) {
  if (!novel?.id) return null

  const authorName = novel.author?.name || ''
  return {
    novel_id: novel.id,
    item_id: novel.aladin_item_id || null,
    title: novel.title,
    author: authorName,
    publisher: novel.publisher || '',
    pub_date: novel.pub_date || null,
    description: novel.description || null,
    cover_url: novel.cover_url || null,
    fromLibrary: true,
  }
}

export function registerRouteForNovel(novel) {
  const book = novelToSelectedBook(novel)
  if (!book) return { path: '/register' }

  return {
    path: '/register',
    query: { novel_id: String(novel.id) },
    state: { prefillBook: book },
  }
}

export function registerRouteForQuote(quoteId) {
  return {
    path: '/register',
    query: { quote_id: String(quoteId) },
  }
}

export function registerRouteForSearchQuery(q) {
  const text = (q || '').trim()
  if (!text) return { path: '/register' }
  return {
    path: '/register',
    query: { text },
  }
}
