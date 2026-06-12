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
        :liked-ids="likedIds"
        @toggle-like="toggleLike"
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
import { requireLogin } from '../utils/auth'
import { registerRouteForSearchQuery } from '../utils/registerBook'
import {
  clearHomeSearchState,
  loadHomeSearchState,
  saveHomeSearchState,
} from '../utils/homeSearchState'
import {
  applyLikePatchesToQuotes,
  applyLikePatchesToSearchResults,
  mergeLikedIds,
} from '../utils/likeSync'
import { patchQuoteLikeCount, toggleLike as toggleLikeRequest } from '../utils/likeToggle'
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
      likedIds: new Set(),
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
  beforeUnmount() {
    saveHomeSearchState({
      query: this.query,
      searchResults: this.searchResults,
      searched: this.searched,
    })
  },
  methods: {
    applyLikeState() {
      this.recentQuotes = applyLikePatchesToQuotes(this.recentQuotes)
      this.searchResults = applyLikePatchesToSearchResults(this.searchResults)
      this.likedIds = mergeLikedIds(this.likedIds)
    },
    restoreSearchState() {
      const saved = loadHomeSearchState()
      if (!saved?.searched) return

      this.query = saved.query || ''
      this.searched = true
      this.searchResults = Array.isArray(saved.searchResults) ? saved.searchResults : []
      this.applyLikeState()
    },
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
        this.likedIds = new Set(home.liked_ids || [])
        this.applyLikeState()
        this.restoreSearchState()
      } catch (e) {
        this.error = e.message || '잠시 문제가 생겼어요.'
        this.likedIds = new Set()
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
      clearHomeSearchState()
    },
    async toggleLike(quoteId) {
      if (!requireLogin(this.$router, this.$route.fullPath)) return
      try {
        const { likedIds, likeCount } = await toggleLikeRequest(api, this.likedIds, quoteId)
        this.likedIds = likedIds
        this.searchResults = patchQuoteLikeCount(this.searchResults, quoteId, likeCount, { nested: true })
        this.recentQuotes = patchQuoteLikeCount(this.recentQuotes, quoteId, likeCount)
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
  margin-bottom: var(--glt-space-3);
}

.search-hero {
  margin-top: var(--glt-space-2);
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

.empty-search {
  padding: var(--glt-space-5) var(--glt-space-4);
  text-align: center;
}

.empty-title {
  margin: 0 0 var(--glt-space-3);
  color: var(--glt-ink-secondary);
}
</style>
