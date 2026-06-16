export async function toggleScrap(api, scrappedIds, quoteId) {
  const wasScrapped = scrappedIds.has(quoteId)
  const actionRes = wasScrapped
    ? await api.removeScrap(quoteId)
    : await api.addScrap(quoteId)

  const nextScrappedIds = new Set(scrappedIds)
  if (actionRes.scrapped) nextScrappedIds.add(quoteId)
  else nextScrappedIds.delete(quoteId)

  return {
    scrappedIds: nextScrappedIds,
    quoteId,
    scrapCount: Number(actionRes.scrap_count) || 0,
    scrapped: !!actionRes.scrapped,
  }
}
