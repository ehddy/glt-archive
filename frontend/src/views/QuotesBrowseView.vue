<template>
  <section class="quotes-browse glt-container">
    <header class="page-head">
      <router-link to="/" class="back-link">← 검색</router-link>
      <h1 class="glt-title">구절 둘러보기</h1>
      <p class="page-lead">등록된 구절을 모아봅니다. 구절·작품·작가로 검색할 수 있어요.</p>
    </header>

    <div class="glt-search browse-search">
      <input
        v-model="query"
        type="search"
        placeholder="구절, 작품명, 작가명"
        @keyup.enter="applySearch"
      />
      <button v-if="query" class="glt-btn glt-btn-ghost" @click="clearSearch">초기화</button>
      <button class="glt-btn glt-btn-primary" @click="applySearch">검색</button>
    </div>

    <p v-if="!loading && total !== null" class="result-count">
      {{ total }}구절
      <span v-if="activeQuery"> · 「{{ activeQuery }}」</span>
    </p>

    <div v-if="loading" class="glt-empty">불러오는 중…</div>
    <div v-else-if="error" class="glt-empty glt-card">{{ error }}</div>
    <div v-else-if="!quotes.length" class="glt-empty glt-card">
      <p>구절이 없습니다.</p>
      <router-link :to="registerRoute" class="glt-btn glt-btn-primary">구절 등록하기</router-link>
    </div>
    <template v-else>
      <ul class="quote-list">
        <li v-for="quote in quotes" :key="quote.id">
          <router-link :to="`/quotes/${quote.id}`" class="quote-card glt-card">
            <p class="quote-text">{{ quote.text }}</p>
            <span class="quote-source">{{ sourceLabel(quote) }}</span>
          </router-link>
        </li>
      </ul>

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
import { registerRouteForSearchQuery } from '../utils/registerBook'

export default {
  name: 'QuotesBrowseView',
  components: { PaginationBar },
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
    sourceLabel(quote) {
      const title = quote.novel?.title
      const author = quote.novel?.author?.name || quote.author?.name
      if (title && author) return `${title} · ${author}`
      if (title) return title
      if (author) return author
      return '출처 미상'
    },
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
  margin-bottom: var(--glt-space-4);
}

.back-link {
  display: inline-block;
  margin-bottom: var(--glt-space-2);
  font-size: 0.82rem;
  color: var(--glt-ink-tertiary);
  text-decoration: none;
}

.back-link:hover {
  color: var(--glt-accent-hover);
}

.page-lead {
  margin: var(--glt-space-2) 0 0;
  font-size: 0.88rem;
  color: var(--glt-ink-secondary);
}

.browse-search {
  width: 100%;
  margin-bottom: var(--glt-space-3);
}

.result-count {
  margin: 0 0 var(--glt-space-3);
  font-size: 0.8rem;
  color: var(--glt-ink-tertiary);
}

.quote-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.quote-card {
  display: block;
  padding: var(--glt-space-4);
  text-decoration: none;
  color: inherit;
  transition: box-shadow 0.2s var(--glt-ease), transform 0.2s var(--glt-ease);
}

.quote-card:hover {
  box-shadow: var(--glt-shadow-md);
  transform: translateY(-1px);
}

.quote-text {
  margin: 0 0 8px;
  font-size: 0.9rem;
  line-height: 1.65;
  color: var(--glt-ink);
  word-break: keep-all;
}

.quote-source {
  font-size: 0.74rem;
  color: var(--glt-ink-tertiary);
}
</style>
