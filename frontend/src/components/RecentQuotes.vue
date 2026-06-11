<template>
  <section v-if="quotes.length" class="recent-quotes">
    <header class="recent-head">
      <div class="recent-head-left">
        <h2 class="recent-title">구절 둘러보기</h2>
        <p class="recent-hint">검색창에 구절이나 작품명을 입력해도 찾을 수 있어요.</p>
      </div>
      <router-link to="/quotes" class="recent-more">더 보기</router-link>
    </header>

    <ul class="recent-list">
      <li v-for="quote in quotes" :key="quote.id">
        <router-link :to="`/quotes/${quote.id}`" class="recent-card glt-card">
          <p class="recent-text">{{ quote.text }}</p>
          <span class="recent-source">
            {{ sourceLabel(quote) }}
          </span>
        </router-link>
      </li>
    </ul>
  </section>
</template>

<script>
export default {
  name: 'RecentQuotes',
  props: {
    quotes: { type: Array, required: true },
  },
  methods: {
    sourceLabel(quote) {
      const title = quote.novel?.title
      const author = quote.novel?.author?.name || quote.author?.name
      if (title && author) return `${title} · ${author}`
      if (title) return title
      if (author) return author
      return '출처 미상'
    },
  },
}
</script>

<style scoped>
.recent-quotes {
  margin-top: var(--glt-space-6);
}

.recent-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--glt-space-3);
  margin-bottom: var(--glt-space-3);
}

.recent-head-left {
  min-width: 0;
}

.recent-more {
  flex-shrink: 0;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--glt-accent-hover);
  text-decoration: none;
  padding-top: 2px;
}

.recent-more:hover {
  text-decoration: underline;
}

.recent-title {
  margin: 0 0 4px;
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--glt-ink-secondary);
}

.recent-hint {
  margin: 0;
  font-size: 0.78rem;
  color: var(--glt-ink-tertiary);
}

.recent-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.recent-card {
  display: block;
  padding: var(--glt-space-4);
  text-decoration: none;
  color: inherit;
  transition: box-shadow 0.2s var(--glt-ease), transform 0.2s var(--glt-ease);
}

.recent-card:hover {
  box-shadow: var(--glt-shadow-md);
  transform: translateY(-1px);
}

.recent-text {
  margin: 0 0 8px;
  font-size: 0.9rem;
  line-height: 1.65;
  color: var(--glt-ink);
  word-break: keep-all;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.recent-source {
  font-size: 0.74rem;
  color: var(--glt-ink-tertiary);
}
</style>
