<template>
  <section v-if="quotes.length" class="recent-quotes">
    <header class="recent-head">
      <h2 class="recent-title">명문장 둘러보기</h2>
      <router-link to="/quotes" class="recent-more">
        더 보기
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path d="M9 6l6 6-6 6" />
        </svg>
      </router-link>
    </header>

    <div class="recent-feed">
      <QuoteBrowseItem
        v-for="quote in quotes"
        :key="quote.id"
        :quote="quote"
        compact
      />
    </div>
  </section>
</template>

<script>
import QuoteBrowseItem from './QuoteBrowseItem.vue'

export default {
  name: 'RecentQuotes',
  components: { QuoteBrowseItem },
  props: {
    quotes: { type: Array, required: true },
  },
}
</script>

<style scoped>
.recent-quotes {
  margin-top: 0;
}

.recent-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--glt-space-3);
  margin-bottom: var(--glt-space-3);
}

.recent-title {
  margin: 0;
  font-size: 0.92rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--glt-ink);
}

.recent-more {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--glt-ink-tertiary);
  text-decoration: none;
  transition: color var(--glt-duration) var(--glt-ease);
}

.recent-more:hover {
  color: var(--glt-accent-hover);
}
</style>
