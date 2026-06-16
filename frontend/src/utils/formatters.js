export function formatCount(n) {
  if (!n || n < 1) return ''
  if (n < 10000) return n.toLocaleString()
  return String(Math.floor(n / 1000) / 10) + '만'
}
