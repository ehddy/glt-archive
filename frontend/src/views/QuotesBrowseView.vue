<template>
  <section class="quotes-browse glt-container">
    <header class="page-head">
      <h1 class="glt-title page-title">명문장</h1>
      <p class="page-lead">기억 속 문장의 출처를 찾아보세요.</p>
    </header>

    <div class="browse-toolbar glt-card">
      <div class="glt-search browse-search">
        <input
          v-model="query"
          type="search"
          placeholder="문장, 도서명, 작가명"
          @keyup.enter="applySearch"
        />
        <button v-if="query" class="glt-btn glt-btn-ghost" @click="clearSearch">지우기</button>
        <button class="glt-btn glt-btn-primary" @click="applySearch">검색</button>
      </div>
      <p v-if="!initialLoading && total !== null" class="result-count">
        <span class="result-count-num">{{ total }}</span>문장
        <span v-if="activeQuery" class="result-query">{{ activeQuery }}</span>
      </p>
    </div>

    <div v-if="error && !initialLoading" class="state-panel state-panel--error">{{ error }}</div>

    <div v-else-if="!initialLoading && !quotes.length" class="state-panel state-panel--empty">
      <p class="state-title">아직 문장이 없습니다</p>
      <p class="state-desc">첫 문장을 등록해 보세요.</p>
      <router-link :to="registerRoute" class="glt-btn glt-btn-primary">문장 등록</router-link>
    </div>

    <template v-else-if="!initialLoading">
      <div class="quote-feed">
        <QuoteBrowseItem
          v-for="quote in quotes"
          :key="quote.id"
          :quote="quote"
        />
      </div>

      <LoadMoreBar
        :shown="quotes.length"
        :total="total"
        :page-size="pageSize"
        :loading="loadingMore"
        @load-more="loadMore"
      />
    </template>
  </section>
</template>

<script>
import { api } from '../api'
import LoadMoreBar from '../components/LoadMoreBar.vue'
import QuoteBrowseItem from '../components/QuoteBrowseItem.vue'
import { registerRouteForSearchQuery } from '../utils/registerBook'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'

export default {
  name: 'QuotesBrowseView',
  components: { LoadMoreBar, QuoteBrowseItem },
  data() {
    return {
      quotes: [],
      total: null,
      query: '',
      activeQuery: '',
      pageSize: 20,
      initialLoading: true,
      loadingMore: false,
      error: '',
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
        this.loadQuotes()
      },
    },
  },
  methods: {
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
        const skip = append ? this.quotes.length : 0
        const res = await api.browseQuotes({
          q: this.activeQuery || undefined,
          skip,
          limit: this.pageSize,
        })
        this.total = res.total
        if (append) {
          this.quotes = [...this.quotes, ...res.items]
        } else {
          this.quotes = res.items
        }
      } catch (e) {
        this.error = e.message
        if (!append) this.quotes = []
      } finally {
        if (!append) {
          this.initialLoading = false
          endPageLoading()
        }
        this.loadingMore = false
      }
    },
    loadMore() {
      if (this.loadingMore || this.quotes.length >= this.total) return
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
.browse-toolbar {
  padding: var(--glt-space-4);
  margin-bottom: var(--glt-space-5);
}

.browse-search {
  width: 100%;
}

.result-count {
  margin: var(--glt-space-3) 0 0;
  font-size: 0.8rem;
  color: var(--glt-ink-tertiary);
}

.result-count-num {
  font-weight: 600;
  color: var(--glt-ink-secondary);
}

.result-query::before {
  content: '·';
  margin: 0 6px;
  color: var(--glt-ink-faint);
}

.result-query {
  color: var(--glt-ink-secondary);
}

.quote-feed {
  margin-bottom: var(--glt-space-2);
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

.state-panel--empty .state-title {
  margin: 0 0 var(--glt-space-2);
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--glt-ink);
}

.state-panel--empty .state-desc {
  margin: 0 0 var(--glt-space-4);
  font-size: 0.86rem;
  color: var(--glt-ink-secondary);
}

.state-spinner {
  display: block;
  width: 24px;
  height: 24px;
  margin: 0 auto var(--glt-space-3);
  border: 2px solid var(--glt-glass-border);
  border-top-color: var(--glt-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
