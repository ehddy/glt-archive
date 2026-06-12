export function formatLikeCount(count) {
  const n = Number(count) || 0
  if (n >= 10000) return `${(n / 10000).toFixed(n >= 100000 ? 0 : 1)}만`
  if (n >= 1000) return `${(n / 1000).toFixed(n >= 10000 ? 0 : 1)}천`
  return String(n)
}
