<template>
  <section class="quotes-browse glt-container">
    <header class="page-head">
      <router-link to="/" class="back-link">← 검색</router-link>
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
      <p v-if="!loading && total !== null" class="result-count">
        <span class="result-count-num">{{ total }}</span>문장
        <span v-if="activeQuery" class="result-query">{{ activeQuery }}</span>
      </p>
    </div>

    <div v-if="loading" class="state-panel">
      <span class="state-spinner" aria-hidden="true" />
      불러오는 중…
    </div>

    <div v-else-if="error" class="state-panel state-panel--error">{{ error }}</div>

    <div v-else-if="!quotes.length" class="state-panel state-panel--empty">
      <p class="state-title">아직 문장이 없습니다</p>
      <p class="state-desc">첫 문장을 등록해 보세요.</p>
      <router-link :to="registerRoute" class="glt-btn glt-btn-primary">문장 등록</router-link>
    </div>

    <template v-else>
      <div class="quote-feed">
        <QuoteBrowseItem
          v-for="quote in quotes"
          :key="quote.id"
          :quote="quote"
        />
      </div>

      <PaginationBar
        :page="page"
        :total="total"
        :page-size="pageSize"
        @update:page="goToPage"
      />
    </template>
  </section>
</template>

<script>
import { api } from '../api'
import PaginationBar from '../components/PaginationBar.vue'
import QuoteBrowseItem from '../components/QuoteBrowseItem.vue'
import { registerRouteForSearchQuery } from '../utils/registerBook'

export default {
  name: 'QuotesBrowseView',
  components: { PaginationBar, QuoteBrowseItem },
  data() {
    return {
      quotes: [],
      total: null,
      query: '',
      activeQuery: '',
      page: 1,
      pageSize: 20,
      loading: true,
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
        this.page = Math.max(1, Number(query.page) || 1)
        this.loadQuotes()
      },
    },
  },
  methods: {
    async loadQuotes() {
      this.loading = true
      this.error = ''
      try {
        const skip = (this.page - 1) * this.pageSize
        const res = await api.browseQuotes({
          q: this.activeQuery || undefined,
          skip,
          limit: this.pageSize,
        })
        this.quotes = res.items
        this.total = res.total
        if (this.page > 1 && !res.items.length) {
          this.goToPage(1)
        }
      } catch (e) {
        this.error = e.message
        this.quotes = []
      } finally {
        this.loading = false
      }
    },
    applySearch() {
      const q = this.query.trim()
      const next = { ...this.$route.query }
      if (q) next.q = q
      else delete next.q
      delete next.page
      this.$router.push({ path: '/quotes', query: next })
    },
    clearSearch() {
      this.query = ''
      this.$router.push({ path: '/quotes' })
    },
    goToPage(page) {
      const next = { ...this.$route.query, page: String(page) }
      if (page <= 1) delete next.page
      this.$router.push({ path: '/quotes', query: next })
    },
  },
}
</script>

<style scoped>
.page-head {
  margin-bottom: var(--glt-space-5);
}

.page-title {
  margin-top: var(--glt-space-2);
}

.back-link {
  display: inline-block;
  font-size: 0.82rem;
  color: var(--glt-ink-tertiary);
  text-decoration: none;
}

.back-link:hover {
  color: var(--glt-accent-hover);
}

.page-lead {
  margin: var(--glt-space-2) 0 0;
  font-size: 0.9rem;
  color: var(--glt-ink-secondary);
  line-height: 1.6;
}

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
