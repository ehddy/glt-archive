export function getAladinPurchaseUrl(novel) {
  if (!novel) return null

  const link = (novel.aladin_link || '').trim()
  if (link.startsWith('http')) {
    return link
  }

  const itemId = novel.aladin_item_id
  if (itemId) {
    return `https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=${itemId}`
  }

  return null
}
