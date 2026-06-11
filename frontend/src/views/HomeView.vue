<template>
  <section class="home glt-container">
    <header class="home-hero">
      <h1 class="glt-title">이 말, 어디서 왔을까?</h1>
      <p class="hero-lead">구절을 검색하거나, 아래 작품·구절을 눌러 출처를 확인하세요.</p>

      <div class="glt-search search-hero">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="search-icon">
          <circle cx="11" cy="11" r="7" />
          <path d="M20 20l-3-3" />
        </svg>
        <input
          v-model="query"
          type="search"
          placeholder="구절이나 작품명"
          @keyup.enter="handleSearch"
        />
        <button v-if="query" class="glt-btn glt-btn-ghost search-clear" @click="clearSearch">초기화</button>
        <button class="glt-btn glt-btn-primary" @click="handleSearch">검색</button>
      </div>
    </header>

    <p v-if="flashMessage" class="flash-banner" role="status">{{ flashMessage }}</p>

    <div v-if="loading" class="glt-empty">
      <span class="loading-orbit" />
      불러오는 중…
    </div>

    <div v-else-if="error" class="error-panel glt-card">
      <p class="error-title">불러오기 실패</p>
      <p class="error-desc">{{ error }}</p>
      <button class="glt-btn glt-btn-primary" @click="loadHome">다시 시도</button>
    </div>

    <template v-else>
      <SourceSearchResults
        v-if="searched && searchResults.length"
        :results="searchResults"
        :bookmark-ids="bookmarkIds"
        @toggle-bookmark="toggleBookmark"
      />

      <div v-else-if="searched" class="empty-search glt-card">
        <p class="empty-title">검색 결과가 없습니다.</p>
        <p class="empty-hint">이 구절이 아직 등록되지 않았을 수 있어요.</p>
        <router-link :to="registerRoute" class="glt-btn glt-btn-primary">
          이 구절 등록하기
        </router-link>
      </div>

      <template v-else>
        <FeaturedBooks
          :books="featuredBooks"
          :stats="libraryStats"
        />
        <RecentQuotes :quotes="recentQuotes" />
      </template>
    </template>
  </section>
</template>

<script>
import { api } from '../api'
import FeaturedBooks from '../components/FeaturedBooks.vue'
import RecentQuotes from '../components/RecentQuotes.vue'
import SourceSearchResults from '../components/SourceSearchResults.vue'
import { COLLECT } from '../utils/collectLabels'
import { registerRouteForSearchQuery } from '../utils/registerBook'

export default {
  name: 'HomeView',
  components: { SourceSearchResults, FeaturedBooks, RecentQuotes },
  data() {
    return {
      query: '',
      searchResults: [],
      featuredBooks: [],
      recentQuotes: [],
      libraryStats: null,
      bookmarkIds: new Set(),
      loading: true,
      error: '',
      flashMessage: '',
      searched: false,
    }
  },
  computed: {
    registerRoute() {
      return registerRouteForSearchQuery(this.query)
    },
  },
  mounted() {
    this.loadHome()
    this.consumeFlash()
  },
  watch: {
    '$route.query': {
      handler() {
        this.consumeFlash()
      },
    },
  },
  methods: {
    consumeFlash() {
      const { registered, saved } = this.$route.query
      if (registered === '1') {
        this.flashMessage = '등록되었습니다.'
      } else if (saved === '1') {
        this.flashMessage = COLLECT.flash
      } else {
        return
      }
      const rest = { ...this.$route.query }
      delete rest.registered
      delete rest.saved
      this.$router.replace({ path: '/', query: rest })
      this.loadHome()
    },
    async loadHome() {
      this.loading = true
      this.error = ''
      try {
        const [library, featured, recentQuotes, bookmarkRes] = await Promise.all([
          api.getLibrary(),
          api.getFeaturedBooks(8),
          api.listQuotes(0, 12),
          api.getBookmarkIds().catch(() => ({ quote_ids: [] })),
        ])
        this.libraryStats = {
          total_books: library.total_books,
          total_quotes: library.total_quotes,
        }
        this.featuredBooks = featured
        this.recentQuotes = recentQuotes
        this.bookmarkIds = new Set(bookmarkRes.quote_ids || [])
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    },
    async handleSearch() {
      const q = this.query.trim()
      if (!q) {
        this.searchResults = []
        this.searched = false
        return
      }
      this.loading = true
      this.error = ''
      this.searched = true
      try {
        this.searchResults = await api.searchQuotes(q)
      } catch (e) {
        this.error = e.message
        this.searchResults = []
      } finally {
        this.loading = false
      }
    },
    clearSearch() {
      this.query = ''
      this.searchResults = []
      this.searched = false
    },
    async toggleBookmark(quoteId) {
      try {
        if (this.bookmarkIds.has(quoteId)) {
          await api.removeBookmark(quoteId)
          this.bookmarkIds.delete(quoteId)
        } else {
          await api.addBookmark(quoteId)
          this.bookmarkIds.add(quoteId)
        }
        this.bookmarkIds = new Set(this.bookmarkIds)
      } catch (e) {
        this.error = e.message
      }
    },
  },
}
</script>

<style scoped>
.home-hero {
  margin-bottom: var(--glt-space-4);
}

.hero-lead {
  margin: var(--glt-space-2) 0 var(--glt-space-4);
  font-size: 0.9rem;
  color: var(--glt-ink-secondary);
}

.search-hero {
  width: 100%;
}

.flash-banner {
  margin: 0 0 var(--glt-space-4);
  padding: 12px 14px;
  border-radius: var(--glt-radius-md);
  background: rgba(76, 140, 74, 0.1);
  border: 1px solid rgba(76, 140, 74, 0.25);
  color: #2f6b2e;
  font-size: 0.88rem;
}

.search-icon {
  color: var(--glt-ink-tertiary);
  flex-shrink: 0;
}

.search-clear {
  padding: 8px 12px;
  font-size: 0.8rem;
}

.loading-orbit {
  display: block;
  width: 28px;
  height: 28px;
  margin: 0 auto var(--glt-space-4);
  border: 2px solid var(--glt-glass-border);
  border-top-color: var(--glt-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-panel {
  padding: var(--glt-space-6);
  text-align: center;
}

.error-title {
  margin: 0 0 var(--glt-space-2);
  font-weight: 600;
  color: var(--glt-ink);
}

.error-desc {
  margin: 0 0 var(--glt-space-5);
  color: var(--glt-ink-secondary);
  font-size: 0.875rem;
  line-height: 1.6;
  white-space: pre-line;
}

.empty-search {
  padding: var(--glt-space-6);
  text-align: center;
}

.empty-title {
  margin: 0 0 var(--glt-space-2);
  font-weight: 600;
  color: var(--glt-ink);
}

.empty-hint {
  margin: 0 0 var(--glt-space-4);
  font-size: 0.86rem;
  color: var(--glt-ink-secondary);
}
</style>
