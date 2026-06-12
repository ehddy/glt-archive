<template>
  <section class="home glt-container">
    <header class="home-hero">
      <h1 class="glt-title">우리가 알던 문장, 어디서 왔을까요?</h1>
      <p class="hero-lead">괴테는 모든 것을 말했다고 합니다. 기억 속 문장의 출처를 찾아보세요.</p>

      <div class="search-hero">
        <div class="search-row">
          <input
            v-model="query"
            type="search"
            class="search-input"
            placeholder="문장이나 도서명"
            @keyup.enter="handleSearch"
          />
          <button type="button" class="search-submit" @click="handleSearch">검색</button>
        </div>
        <button v-if="query" type="button" class="search-clear" @click="clearSearch">
          입력 지우기
        </button>
      </div>
    </header>

    <div v-if="loading && !hasHomeContent" class="glt-empty">
      <span class="loading-orbit" />
      불러오는 중…
    </div>

    <div v-else-if="error && !hasHomeContent && !searched" class="error-panel glt-card">
      <p class="error-title">불러오기 실패</p>
      <p class="error-desc">{{ error }}</p>
      <button class="glt-btn glt-btn-primary" @click="loadHome">다시 시도</button>
    </div>

    <template v-else>
      <p v-if="error && !searched" class="load-warning" role="status">{{ error }}</p>

      <SourceSearchResults
        v-if="searched && searchResults.length"
        :results="searchResults"
        :bookmark-ids="bookmarkIds"
        @toggle-bookmark="toggleBookmark"
      />

      <div v-else-if="searched" class="empty-search glt-card">
        <p class="empty-title">검색 결과가 없습니다.</p>
        <p class="empty-hint">이 문장이 아직 등록되지 않았을 수 있어요.</p>
        <router-link :to="registerRoute" class="glt-btn glt-btn-primary">
          이 문장 등록하기
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
      searched: false,
    }
  },
  computed: {
    registerRoute() {
      return registerRouteForSearchQuery(this.query)
    },
    hasHomeContent() {
      return this.featuredBooks.length > 0 || this.recentQuotes.length > 0
    },
  },
  mounted() {
    this.loadHome()
  },
  methods: {
    async loadHome() {
      this.loading = true
      this.error = ''

      try {
        const home = await api.getHome({ featuredLimit: 20, quoteLimit: 12 })
        this.libraryStats = home.stats
        this.featuredBooks = Array.isArray(home.featured_books) ? home.featured_books : []
        this.recentQuotes = Array.isArray(home.recent_quotes) ? home.recent_quotes : []
      } catch (e) {
        this.error = e.message || '불러오기에 실패했습니다.'
        this.libraryStats = null
        this.featuredBooks = []
        this.recentQuotes = []
      }

      try {
        const bookmarkRes = await api.getBookmarkIds()
        this.bookmarkIds = new Set(bookmarkRes?.quote_ids || [])
      } catch {
        // 북마크는 홈 콘텐츠 표시에 필수가 아님
      }

      this.loading = false
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
  margin: 4px 0 var(--glt-space-4);
  font-size: 0.84rem;
  line-height: 1.55;
  color: var(--glt-ink-secondary);
}

.search-hero {
  width: 100%;
}

.search-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 5px 5px 14px;
  background: var(--glt-surface);
  border: 1px solid rgba(212, 195, 170, 0.5);
  border-radius: var(--glt-radius-full);
  box-shadow: 0 2px 10px rgba(61, 52, 41, 0.04);
}

.search-row:focus-within {
  border-color: var(--glt-accent-muted);
  box-shadow: 0 0 0 3px var(--glt-accent-soft);
}

.search-input {
  flex: 1;
  min-width: 0;
  border: none;
  outline: none;
  background: transparent;
  font-size: 0.92rem;
  color: var(--glt-ink);
  padding: 9px 0;
}

.search-input::placeholder {
  color: var(--glt-ink-tertiary);
}

.search-submit {
  flex-shrink: 0;
  border: none;
  border-radius: var(--glt-radius-full);
  background: var(--glt-accent);
  color: #fff;
  font-size: 0.78rem;
  font-weight: 600;
  padding: 8px 14px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(196, 105, 58, 0.25);
  transition: background var(--glt-duration);
}

.search-submit:hover {
  background: var(--glt-accent-hover);
}

.search-clear {
  margin-top: 8px;
  padding: 0;
  border: none;
  background: transparent;
  font-size: 0.74rem;
  font-weight: 600;
  color: var(--glt-ink-tertiary);
  cursor: pointer;
}

.search-clear:hover {
  color: var(--glt-accent-hover);
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

.load-warning {
  margin: 0 0 var(--glt-space-4);
  padding: 10px 12px;
  border-radius: var(--glt-radius-md);
  background: rgba(196, 105, 58, 0.08);
  border: 1px solid rgba(196, 105, 58, 0.18);
  color: var(--glt-accent-hover);
  font-size: 0.8rem;
  line-height: 1.5;
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
