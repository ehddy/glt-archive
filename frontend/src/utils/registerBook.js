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

function normalizeBookText(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/\s+/g, '')
    .replace(/[^\w가-힣]/g, '')
}

function primaryAuthorName(author) {
  return String(author || '')
    .split(',')[0]
    .split('(')[0]
    .trim()
}

function bookAuthorMatches(bookAuthor, author) {
  const query = normalizeBookText(primaryAuthorName(author))
  if (!query) return false

  const segments = String(bookAuthor || '')
    .split(',')
    .map((part) => normalizeBookText(part.split('(')[0]))

  if (segments.some((segment) => segment && (segment.includes(query) || query.includes(segment)))) {
    return true
  }

  const whole = normalizeBookText(bookAuthor)
  return whole.includes(query) || query.includes(whole)
}

function titleMatchesQuery(book, titleQuery) {
  const bookTitle = normalizeBookText(book.title)
  return bookTitle.includes(titleQuery) || titleQuery.includes(bookTitle)
}

function rankTitleMatches(matches, titleQuery) {
  return [...matches].sort((a, b) => {
    const aTitle = normalizeBookText(a.title)
    const bTitle = normalizeBookText(b.title)

    const aExact = aTitle === titleQuery ? 1 : 0
    const bExact = bTitle === titleQuery ? 1 : 0
    if (aExact !== bExact) return bExact - aExact

    return aTitle.length - bTitle.length
  })
}

export function pickAladinBookMatch(results, sourceTitle, author = '') {
  if (!Array.isArray(results) || !results.length) return null

  const titleQuery = normalizeBookText(sourceTitle)
  if (!titleQuery) return null

  const orderedTitleMatches = results.filter((book) => titleMatchesQuery(book, titleQuery))
  if (!orderedTitleMatches.length) return null

  if (orderedTitleMatches.length === 1) {
    return orderedTitleMatches[0]
  }

  if (primaryAuthorName(author)) {
    const authorMatches = orderedTitleMatches.filter((book) =>
      bookAuthorMatches(book.author, author),
    )
    if (authorMatches.length) {
      return rankTitleMatches(authorMatches, titleQuery)[0]
    }
  }

  return orderedTitleMatches[0]
}

export function registerRouteForAiArticle(article) {
  const text = (article?.quote || '').trim()
  const title = (article?.source_title || '').trim()
  const author = (article?.author || '').trim()

  const baseState = {
    fromAiSearch: true,
    prefillText: text,
    prefillAuthor: author,
    prefillCustomSource: { title, author },
  }

  if (title) {
    return {
      path: '/register',
      state: {
        ...baseState,
        sourceMode: 'aladin',
        prefillBookQuery: title,
        prefillSourceTitle: title,
      },
    }
  }

  return {
    path: '/register',
    state: {
      ...baseState,
      sourceMode: 'custom',
    },
  }
}
