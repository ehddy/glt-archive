export function formatCount(n) {
  if (!n || n < 1) return ''
  if (n < 10000) return n.toLocaleString()
  return String(Math.floor(n / 1000) / 10) + '만'
}

export function formatRelativeTime(dateStr) {
  if (!dateStr) return ''
  // Append 'Z' if no timezone info so JS parses as UTC, not local time
  const utc = /Z$|[+-]\d{2}:\d{2}$/.test(dateStr) ? dateStr : dateStr + 'Z'
  const diff = Math.floor((Date.now() - new Date(utc).getTime()) / 1000)
  if (diff < 60) return '방금 전'
  if (diff < 3600) return `${Math.floor(diff / 60)}분 전`
  if (diff < 86400) return `${Math.floor(diff / 3600)}시간 전`
  if (diff < 86400 * 7) return `${Math.floor(diff / 86400)}일 전`
  if (diff < 86400 * 30) return `${Math.floor(diff / (86400 * 7))}주 전`
  if (diff < 86400 * 365) return `${Math.floor(diff / (86400 * 30))}개월 전`
  const d = new Date(dateStr)
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`
}
