const patches = new Map()

export function setLikePatch(quoteId, { likeCount, liked }) {
  patches.set(Number(quoteId), {
    likeCount: Number(likeCount) || 0,
    liked: !!liked,
  })
}

export function applyLikePatchesToQuotes(quotes) {
  if (!Array.isArray(quotes)) return []
  return quotes.map((quote) => {
    const patch = patches.get(quote.id)
    if (!patch) return quote
    return { ...quote, like_count: patch.likeCount }
  })
}

export function applyLikePatchesToSearchResults(items) {
  if (!Array.isArray(items)) return []
  return items.map((item) => {
    const quoteId = item.quote?.id
    if (!quoteId) return item
    const patch = patches.get(quoteId)
    if (!patch) return item
    return {
      ...item,
      quote: { ...item.quote, like_count: patch.likeCount },
    }
  })
}

export function mergeLikedIds(likedIds) {
  const next = new Set(likedIds)
  for (const [quoteId, patch] of patches) {
    if (patch.liked) next.add(quoteId)
    else next.delete(quoteId)
  }
  return next
}
