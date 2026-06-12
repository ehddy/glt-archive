import { setLikePatch } from './likeSync'

export async function toggleLike(api, likedIds, quoteId) {
  const wasLiked = likedIds.has(quoteId)
  const actionRes = wasLiked
    ? await api.removeLike(quoteId)
    : await api.addLike(quoteId)

  const nextLikedIds = new Set(likedIds)
  if (actionRes.liked) nextLikedIds.add(quoteId)
  else nextLikedIds.delete(quoteId)

  const likeCount = Number(actionRes.like_count) || 0
  const liked = !!actionRes.liked
  setLikePatch(quoteId, { likeCount, liked })

  return {
    likedIds: nextLikedIds,
    quoteId,
    likeCount,
    liked,
  }
}

export function patchQuoteLikeCount(items, quoteId, likeCount, { nested = false } = {}) {
  const nextCount = Number(likeCount) || 0
  if (nested) {
    return items.map((item) => (
      item.quote?.id === quoteId
        ? { ...item, quote: { ...item.quote, like_count: nextCount } }
        : item
    ))
  }
  return items.map((item) => (
    item.id === quoteId ? { ...item, like_count: nextCount } : item
  ))
}
