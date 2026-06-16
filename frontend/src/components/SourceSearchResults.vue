<template>
  <section class="source-results">
    <p class="results-count">{{ results.length }}건</p>

    <div class="quote-feed">
      <QuoteFeedItem
        v-for="item in results"
        :key="item.quote.id"
        :quote="item.quote"
        :liked="likedIds.has(item.quote.id)"
        :scrapped="scrappedIds.has(item.quote.id)"
        @toggle-like="$emit('toggle-like', item.quote.id)"
        @toggle-scrap="$emit('toggle-scrap', item.quote.id)"
      />
    </div>
  </section>
</template>

<script>
import QuoteFeedItem from './QuoteFeedItem.vue'

export default {
  name: 'SourceSearchResults',
  components: { QuoteFeedItem },
  props: {
    results: { type: Array, required: true },
    likedIds: { type: Set, required: true },
    scrappedIds: { type: Set, default: () => new Set() },
  },
  emits: ['toggle-like', 'toggle-scrap'],
}
</script>

<style scoped>
.source-results {
  margin-top: var(--glt-space-2);
}

.results-count {
  margin: 0 0 var(--glt-space-3);
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--glt-ink-secondary);
}

.quote-feed {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
