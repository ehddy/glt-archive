import { quoteNovelId } from './quoteDisplay'

export function routeAfterQuoteCreated(quote) {
  const novelId = quoteNovelId(quote)
  if (novelId) {
    return { path: `/novels/${novelId}` }
  }
  if (quote?.id) {
    return { path: `/quotes/${quote.id}` }
  }
  return { path: '/' }
}

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
    state: { prefillBook: book, sourceMode: 'aladin' },
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

export function registerRouteForAiArticle(article) {
  const text = (article?.quote || '').trim()
  const title = (article?.source_title || '').trim()
  const author = (article?.author || '').trim()

  const baseState = { fromAiSearch: true }

  if (title) {
    return {
      path: '/register',
      state: {
        ...baseState,
        prefillText: text,
        sourceMode: 'custom',
        prefillCustomSource: { title, author },
      },
    }
  }

  return {
    path: '/register',
    state: {
      ...baseState,
      prefillText: text,
      sourceMode: 'custom',
      prefillCustomSource: { title: '', author },
    },
  }
}
