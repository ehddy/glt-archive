<template>
  <section class="quotes-browse glt-container">
    <header class="browse-header">
      <div class="search-row">
        <input
          v-model="query"
          type="text"
          enterkeyhint="search"
          placeholder="문장·책·작가 검색해 보세요"
          class="search-input"
          @keyup.enter="applySearch"
        />
        <ClearIconButton v-if="query" @click="clearSearch" />
        <SearchIconButton @click="applySearch" />
      </div>
      <p v-if="!initialLoading && total !== null" class="result-count">
        <span class="result-count-num">{{ total }}</span>개 문장
        <span v-if="activeQuery" class="result-query">· {{ activeQuery }}</span>
      </p>
    </header>

    <div v-if="error && !initialLoading" class="state-panel state-panel--error">{{ error }}</div>

    <div v-else-if="!initialLoading && !quotes.length" class="state-panel">
      <p class="state-title">아직 없어요</p>
      <router-link :to="registerRoute" class="glt-btn glt-btn-primary">첫 포스팅</router-link>
    </div>

    <template v-else-if="!initialLoading">
      <div class="quote-feed">
        <QuoteFeedItem
          v-for="quote in quotes"
          :key="quote.id"
          :quote="quote"
          :liked="likedIds.has(quote.id)"
          :scrapped="scrappedIds.has(quote.id)"
          @toggle-like="handleToggleLike(quote.id)"
          @toggle-scrap="handleToggleScrap(quote.id)"
        />
      </div>
      <div ref="scrollAnchor" class="scroll-anchor">
        <span v-if="loadingMore" class="loading-spinner" aria-hidden="true" />
      </div>
    </template>
  </section>
</template>

<script>
import { api } from '../api'
import ClearIconButton from '../components/ClearIconButton.vue'
import QuoteFeedItem from '../components/QuoteFeedItem.vue'
import SearchIconButton from '../components/SearchIconButton.vue'
import { isLoggedIn, requireLogin } from '../utils/auth'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'
import { registerRouteForSearchQuery } from '../utils/registerBook'
import { toggleLike as toggleLikeRequest } from '../utils/likeToggle'
import { toggleScrap as toggleScrapRequest } from '../utils/scrapToggle'

export default {
  name: 'QuotesBrowseView',
  components: { ClearIconButton, QuoteFeedItem, SearchIconButton },
  data() {
    return {
      quotes: [],
      total: null,
      query: '',
      activeQuery: '',
      pageSize: 20,
      likedIds: new Set(),
      scrappedIds: new Set(),
      initialLoading: true,
      loadingMore: false,
      error: '',
      observer: null,
    }
  },
  computed: {
    registerRoute() {
      return registerRouteForSearchQuery(this.activeQuery)
    },
  },
  watch: {
    '$route.query': {
      immediate: true,
      handler(query) {
        this.query = query.q || ''
        this.activeQuery = query.q || ''
        if (this.observer) { this.observer.disconnect(); this.observer = null }
        this.loadQuotes()
      },
    },
    initialLoading(newVal, oldVal) {
      if (oldVal && !newVal) this.$nextTick(this.setupInfiniteScroll)
    },
  },
  mounted() {
    this.loadUserState()
  },
  beforeUnmount() {
    if (this.observer) this.observer.disconnect()
  },
  methods: {
    async loadUserState() {
      if (!isLoggedIn()) return
      try {
        const [likedRes, scrappedRes] = await Promise.all([
          api.getLikeIds().catch(() => ({ quote_ids: [] })),
          api.getScrapIds().catch(() => ({ quote_ids: [] })),
        ])
        this.likedIds = new Set(likedRes.quote_ids || [])
        this.scrappedIds = new Set(scrappedRes.quote_ids || [])
      } catch {}
    },
    async handleToggleLike(quoteId) {
      if (!requireLogin(this.$router, this.$route.fullPath)) return
      try {
        const { likedIds, likeCount } = await toggleLikeRequest(api, this.likedIds, quoteId)
        this.likedIds = likedIds
        const idx = this.quotes.findIndex(q => q.id === quoteId)
        if (idx !== -1) this.quotes.splice(idx, 1, { ...this.quotes[idx], like_count: likeCount })
      } catch {}
    },
    async handleToggleScrap(quoteId) {
      if (!requireLogin(this.$router, this.$route.fullPath)) return
      try {
        const { scrappedIds, scrapCount } = await toggleScrapRequest(api, this.scrappedIds, quoteId)
        this.scrappedIds = scrappedIds
        const idx = this.quotes.findIndex(q => q.id === quoteId)
        if (idx !== -1) this.quotes.splice(idx, 1, { ...this.quotes[idx], scrap_count: scrapCount })
      } catch {}
    },
    setupInfiniteScroll() {
      const anchor = this.$refs.scrollAnchor
      if (!anchor || this.observer) return
      const root = document.querySelector('.app-frame') || null
      this.observer = new IntersectionObserver(
        (entries) => { if (entries[0].isIntersecting) this.loadMore() },
        { root, rootMargin: '300px' },
      )
      this.observer.observe(anchor)
    },
    async loadQuotes({ append = false } = {}) {
      if (append) {
        this.loadingMore = true
      } else {
        this.initialLoading = true
        this.quotes = []
        startPageLoading()
      }
      this.error = ''
      try {
        const res = await api.browseQuotes({
          q: this.activeQuery || undefined,
          skip: append ? this.quotes.length : 0,
          limit: this.pageSize,
        })
        this.total = res.total
        this.quotes = append ? [...this.quotes, ...res.items] : res.items
      } catch (e) {
        this.error = e.message
        if (!append) this.quotes = []
      } finally {
        if (!append) { this.initialLoading = false; endPageLoading() }
        this.loadingMore = false
      }
    },
    loadMore() {
      if (this.loadingMore || this.initialLoading) return
      if (this.total !== null && this.quotes.length >= this.total) return
      this.loadQuotes({ append: true })
    },
    applySearch() {
      const q = this.query.trim()
      const next = { ...this.$route.query }
      if (q) next.q = q
      else delete next.q
      this.$router.push({ path: '/quotes', query: next })
    },
    clearSearch() {
      this.query = ''
      this.$router.push({ path: '/quotes' })
    },
  },
}
</script>

<style scoped>
.browse-header {
  margin-bottom: var(--glt-space-5);
}

.search-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 4px 4px 16px;
  border-radius: var(--glt-radius-lg);
  background: var(--glt-surface);
  border: 1px solid var(--glt-glass-border);
  box-shadow: var(--glt-shadow-sm);
}

.search-input {
  flex: 1;
  min-width: 0;
  border: none;
  background: transparent;
  font-size: 0.95rem;
  color: var(--glt-ink);
  outline: none;
}

.search-input::placeholder {
  color: var(--glt-ink-faint);
}

.result-count {
  margin: var(--glt-space-2) 0 0;
  font-size: 0.8rem;
  color: var(--glt-ink-tertiary);
}

.result-count-num {
  font-weight: 600;
  color: var(--glt-ink-secondary);
}

.result-query {
  color: var(--glt-ink-secondary);
}

.quote-feed {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.scroll-anchor {
  display: flex;
  justify-content: center;
  padding: 20px 0 8px;
  min-height: 48px;
}

.loading-spinner {
  display: block;
  width: 22px;
  height: 22px;
  border: 2px solid var(--glt-glass-border);
  border-top-color: var(--glt-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.state-panel {
  padding: var(--glt-space-10) var(--glt-space-4);
  text-align: center;
  font-size: 0.88rem;
  color: var(--glt-ink-tertiary);
}

.state-panel--error {
  color: var(--glt-accent-hover);
}

.state-title {
  margin: 0 0 var(--glt-space-2);
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--glt-ink);
}
</style>
