export function quoteSourceTitle(quote) {
  return quote?.source?.title || quote?.novel?.title || ''
}

export function quoteAuthorName(quote) {
  return (
    quote?.source?.author?.name
    || quote?.novel?.author?.name
    || quote?.author?.name
    || ''
  )
}

export function quoteCoverUrl(quote) {
  return quote?.source?.cover_url || quote?.novel?.cover_url || null
}

export function quoteNovelId(quote) {
  const id = quote?.source?.novel_id ?? quote?.novel?.id
  return typeof id === 'number' ? id : null
}

export function quoteHasSource(quote) {
  return !!(quoteSourceTitle(quote) || quoteAuthorName(quote))
}
