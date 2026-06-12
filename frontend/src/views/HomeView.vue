<template>
  <section class="home glt-container">
    <header class="home-hero">
      <h1 class="glt-title">이 문장, 어디서 들어봤더라?</h1>

      <div class="search-hero">
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
      </div>
    </header>

    <div v-if="error && !loading" class="error-panel glt-card">
      <p class="error-title">잠시 문제가 생겼어요</p>
      <p class="error-desc">{{ error }}</p>
      <button class="glt-btn glt-btn-primary" @click="loadHome">다시 시도</button>
    </div>

    <template v-else-if="!loading">
      <SourceSearchResults
        v-if="searched && searchResults.length"
        :results="searchResults"
        :bookmark-ids="bookmarkIds"
        @toggle-bookmark="toggleBookmark"
      />

      <div v-else-if="searched" class="empty-search glt-card">
        <p class="empty-title">아직 없어요</p>
        <router-link :to="registerRoute" class="glt-btn glt-btn-primary">
          직접 등록하기
        </router-link>
      </div>

      <div v-else class="home-feed">
        <FeaturedBooks
          :books="featuredBooks"
          :stats="libraryStats"
        />
        <RecentQuotes :quotes="recentQuotes" />
      </div>
    </template>
  </section>
</template>

<script>
import { api } from '../api'
import ClearIconButton from '../components/ClearIconButton.vue'
import FeaturedBooks from '../components/FeaturedBooks.vue'
import SearchIconButton from '../components/SearchIconButton.vue'
import RecentQuotes from '../components/RecentQuotes.vue'
import SourceSearchResults from '../components/SourceSearchResults.vue'
import { registerRouteForSearchQuery } from '../utils/registerBook'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'

export default {
  name: 'HomeView',
  components: { ClearIconButton, SourceSearchResults, FeaturedBooks, RecentQuotes, SearchIconButton },
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
  },
  mounted() {
    this.loadHome()
  },
  methods: {
    async loadHome() {
      this.loading = true
      startPageLoading()
      this.error = ''
      this.libraryStats = null
      this.featuredBooks = []
      this.recentQuotes = []

      try {
        const home = await api.getHome({ featuredLimit: 10, quoteLimit: 12 })
        this.libraryStats = home.stats
        this.featuredBooks = Array.isArray(home.featured_books) ? home.featured_books : []
        this.recentQuotes = Array.isArray(home.recent_quotes) ? home.recent_quotes : []
        this.bookmarkIds = new Set(home.bookmark_ids || [])
      } catch (e) {
        this.error = e.message || '잠시 문제가 생겼어요.'
        this.bookmarkIds = new Set()
      } finally {
        this.loading = false
        endPageLoading()
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

.home-hero .glt-title {
  margin: 0 0 var(--glt-space-5);
  font-size: 1.35rem;
  line-height: 1.4;
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

.home-feed {
  display: flex;
  flex-direction: column;
  gap: var(--glt-space-5);
}

.empty-search {
  padding: var(--glt-space-6);
  text-align: center;
}

.empty-title {
  margin: 0 0 var(--glt-space-4);
  font-weight: 600;
  color: var(--glt-ink);
}
</style>
