<template>
  <section class="home">
    <header class="home-hero">
      <span class="glt-eyebrow">Library Graph</span>
      <h1 class="glt-title">이 말, 어디서 왔을까?</h1>
      <p class="glt-subtitle">
        작품을 중심으로 구절이 가지처럼 뻗어 나갑니다. 구절·작가·작품으로 검색할 수 있습니다.
      </p>

      <div class="glt-search">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="search-icon">
          <circle cx="11" cy="11" r="7" />
          <path d="M20 20l-3-3" />
        </svg>
        <input
          v-model="query"
          type="search"
          placeholder="구절, 작가, 작품으로 검색"
          @keyup.enter="handleSearch"
        />
        <button v-if="query" class="glt-btn glt-btn-ghost search-clear" @click="clearSearch">초기화</button>
        <button class="glt-btn glt-btn-primary" @click="handleSearch">검색</button>
      </div>

      <div class="glt-stats">
        <span class="glt-stat"><strong>{{ stats.books }}</strong> 작품</span>
        <span class="glt-stat"><strong>{{ stats.quotes }}</strong> 구절</span>
      </div>
    </header>

    <div v-if="loading" class="glt-empty">불러오는 중...</div>

    <div v-else-if="error" class="error-panel glt-card">
      <p class="error-title">데이터를 불러오지 못했습니다</p>
      <p class="error-desc">{{ error }}</p>
      <button class="glt-btn glt-btn-primary" @click="loadLibrary">다시 시도</button>
    </div>

    <div v-else-if="!displayBooks.length" class="glt-empty glt-card">
      아직 등록된 구절이 없습니다. 새 구절을 등록해 보세요.
    </div>

    <div v-else class="library-graph">
      <BookHub
        v-for="(book, index) in displayBooks"
        :key="book.id"
        :book="book"
        :color-index="index"
      />
    </div>
  </section>
</template>

<script>
import { api } from '../api'
import BookHub from '../components/BookHub.vue'

export default {
  name: 'HomeView',
  components: { BookHub },
  data() {
    return {
      query: '',
      library: null,
      searchQuotes: null,
      loading: true,
      error: '',
    }
  },
  computed: {
    isSearching() {
      return this.searchQuotes !== null
    },
    displayBooks() {
      if (this.isSearching) {
        return this.groupQuotesByBook(this.searchQuotes)
      }
      if (!this.library) return []

      const books = [...(this.library.books || [])]
      if (this.library.unlinked?.length) {
        books.push({
          id: 'unlinked',
          title: '미분류',
          author: null,
          quotes: this.library.unlinked,
        })
      }
      return books.filter((b) => b.quotes && b.quotes.length > 0)
    },
    stats() {
      if (this.isSearching) {
        const quotes = this.searchQuotes || []
        return {
          books: this.displayBooks.length,
          quotes: quotes.length,
        }
      }
      return {
        books: this.library?.total_books || this.displayBooks.length,
        quotes: this.library?.total_quotes || 0,
      }
    },
  },
  mounted() {
    this.loadLibrary()
  },
  methods: {
    async loadLibrary() {
      this.loading = true
      this.error = ''
      try {
        const library = await api.getLibrary()
        if (!library || !Array.isArray(library.books)) {
          throw new Error('서버 응답 형식이 올바르지 않습니다.')
        }
        this.library = library
        this.searchQuotes = null
      } catch (e) {
        this.error = `${e.message}\n\n백엔드 실행:\ncd backend\nuvicorn app.main:app --reload --host 127.0.0.1 --port 8000`
        this.library = null
      } finally {
        this.loading = false
      }
    },
    async handleSearch() {
      if (!this.query.trim()) {
        this.searchQuotes = null
        return
      }
      this.loading = true
      this.error = ''
      try {
        const results = await api.searchQuotes(this.query.trim())
        this.searchQuotes = results.map((r) => r.quote)
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    },
    clearSearch() {
      this.query = ''
      this.searchQuotes = null
    },
    groupQuotesByBook(quotes) {
      const map = new Map()

      for (const quote of quotes) {
        const novel = quote.novel
        const key = novel?.id ?? 'unlinked'
        if (!map.has(key)) {
          map.set(key, {
            id: key,
            title: novel?.title || '미분류',
            author: novel?.author || quote.author || null,
            quotes: [],
          })
        }
        map.get(key).quotes.push(quote)
      }

      return Array.from(map.values())
    },
  },
}
</script>

<style scoped>
.home-hero {
  margin-bottom: var(--glt-space-6);
}

.search-icon {
  color: var(--glt-ink-tertiary);
  flex-shrink: 0;
}

.search-clear {
  padding: 8px 12px;
  font-size: 0.8rem;
}

.error-panel {
  padding: var(--glt-space-8);
  text-align: center;
  max-width: 480px;
  margin: 0 auto;
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
}

.library-graph {
  display: flex;
  flex-direction: column;
  gap: var(--glt-space-2);
}

.library-graph > :deep(.book-hub) {
  border-bottom: 1px solid var(--glt-line);
}

.library-graph > :deep(.book-hub:last-child) {
  border-bottom: none;
}
</style>
