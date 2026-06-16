<template>
  <section class="home glt-container">
    <header class="home-header">
      <div class="search-row">
        <input
          v-model="query"
          type="text"
          enterkeyhint="search"
          class="search-input"
          placeholder="들어본 것 같은 문장 검색해 보세요"
          @keyup.enter="handleSearch"
        />
        <ClearIconButton v-if="query" @click="clearSearch" />
        <SearchIconButton @click="handleSearch" />
      </div>
    </header>

    <div v-if="error && !loading && !loadingMore" class="error-panel glt-card">
      <p class="error-title">잠시 문제가 생겼어요</p>
      <p class="error-desc">{{ error }}</p>
      <button class="glt-btn glt-btn-primary" @click="loadFeed">다시 시도</button>
    </div>

    <template v-else-if="searched">
      <SourceSearchResults
        v-if="searchResults.length"
        :results="searchResults"
        :liked-ids="likedIds"
        :scrapped-ids="scrappedIds"
        @toggle-like="toggleLike"
        @toggle-scrap="toggleScrap"
      />
      <div v-else-if="!loading" class="state-panel">
        <p class="state-title">아직 없어요</p>
        <router-link :to="registerRoute" class="glt-btn glt-btn-primary">
          직접 포스팅하기
        </router-link>
      </div>
    </template>

    <template v-else>
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
import SourceSearchResults from '../components/SourceSearchResults.vue'
import { isLoggedIn, requireLogin } from '../utils/auth'
import {
  clearHomeSearchState,
  loadHomeSearchState,
  saveHomeSearchState,
} from '../utils/homeSearchState'
import {
  applyLikePatchesToSearchResults,
  mergeLikedIds,
} from '../utils/likeSync'
import { patchQuoteLikeCount, toggleLike as toggleLikeRequest } from '../utils/likeToggle'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'
import { registerRouteForSearchQuery } from '../utils/registerBook'
import { toggleScrap as toggleScrapRequest } from '../utils/scrapToggle'

export default {
  name: 'HomeView',
  components: { ClearIconButton, QuoteFeedItem, SearchIconButton, SourceSearchResults },
  data() {
    return {
      query: '',
      searchResults: [],
      quotes: [],
      total: null,
      pageSize: 20,
      likedIds: new Set(),
      scrappedIds: new Set(),
      loading: true,
      loadingMore: false,
      error: '',
      searched: false,
      observer: null,
    }
  },
  computed: {
    registerRoute() {
      return registerRouteForSearchQuery(this.query)
    },
  },
  watch: {
    loading(newVal, oldVal) {
      if (oldVal && !newVal && !this.observer && !this.searched) {
        this.$nextTick(this.setupInfiniteScroll)
      }
    },
  },
  mounted() {
    const saved = this.restoreSearchState()
    if (!saved) this.loadFeed()
    this.loadUserState()
  },
  beforeUnmount() {
    saveHomeSearchState({
      query: this.query,
      searchResults: this.searchResults,
      searched: this.searched,
    })
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
      if (!anchor) return
      const root = document.querySelector('.app-frame') || null
      this.observer = new IntersectionObserver(
        (entries) => { if (entries[0].isIntersecting) this.loadMore() },
        { root, rootMargin: '300px' },
      )
      this.observer.observe(anchor)
    },
    async loadFeed({ append = false } = {}) {
      if (append) {
        this.loadingMore = true
      } else {
        this.loading = true
        this.quotes = []
        startPageLoading()
      }
      this.error = ''
      try {
        const res = await api.browseQuotes({ skip: append ? this.quotes.length : 0, limit: this.pageSize })
        this.total = res.total
        this.quotes = append ? [...this.quotes, ...res.items] : res.items
      } catch (e) {
        this.error = e.message || '잠시 문제가 생겼어요.'
      } finally {
        if (!append) { this.loading = false; endPageLoading() }
        this.loadingMore = false
      }
    },
    loadMore() {
      if (this.loadingMore || this.searched || this.loading) return
      if (this.total !== null && this.quotes.length >= this.total) return
      this.loadFeed({ append: true })
    },
    restoreSearchState() {
      const saved = loadHomeSearchState()
      if (!saved?.searched) return false
      this.query = saved.query || ''
      this.searched = true
      this.loading = false
      this.searchResults = applyLikePatchesToSearchResults(
        Array.isArray(saved.searchResults) ? saved.searchResults : []
      )
      this.likedIds = mergeLikedIds(this.likedIds)
      return true
    },
    async handleSearch() {
      const q = this.query.trim()
      if (!q) { this.clearSearch(); return }
      this.loading = true
      startPageLoading()
      this.error = ''
      this.searched = true
      try {
        this.searchResults = await api.searchQuotes(q)
      } catch (e) {
        this.error = e.message
        this.searchResults = []
      } finally {
        this.loading = false
        endPageLoading()
      }
    },
    clearSearch() {
      this.query = ''
      this.searchResults = []
      this.searched = false
      clearHomeSearchState()
      if (!this.quotes.length) this.loadFeed()
      else this.$nextTick(this.setupInfiniteScroll)
    },
    async toggleLike(quoteId) {
      if (!requireLogin(this.$router, this.$route.fullPath)) return
      try {
        const { likedIds, likeCount } = await toggleLikeRequest(api, this.likedIds, quoteId)
        this.likedIds = likedIds
        this.searchResults = patchQuoteLikeCount(this.searchResults, quoteId, likeCount, { nested: true })
      } catch (e) {
        this.error = e.message
      }
    },
    async toggleScrap(quoteId) {
      if (!requireLogin(this.$router, this.$route.fullPath)) return
      try {
        const { scrappedIds, scrapCount } = await toggleScrapRequest(api, this.scrappedIds, quoteId)
        this.scrappedIds = scrappedIds
        this.searchResults = this.searchResults.map(item =>
          item.quote?.id === quoteId
            ? { ...item, quote: { ...item.quote, scrap_count: scrapCount } }
            : item
        )
      } catch {}
    },
  },
}
</script>

<style scoped>
.home-header {
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

.error-panel {
  padding: var(--glt-space-4);
  text-align: center;
}

.error-title {
  margin: 0 0 8px;
  font-weight: 600;
}

.error-desc {
  margin: 0 0 var(--glt-space-3);
  color: var(--glt-ink-secondary);
  font-size: 0.9rem;
}

.state-panel {
  padding: var(--glt-space-10) var(--glt-space-4);
  text-align: center;
}

.state-title {
  margin: 0 0 var(--glt-space-3);
  color: var(--glt-ink-secondary);
}
</style>
