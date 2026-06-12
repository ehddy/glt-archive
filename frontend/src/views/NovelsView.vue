<template>
  <section class="novels glt-container">
    <header class="page-head">
      <h1 class="glt-title">책장</h1>
      <p class="page-lead">문장이 담긴 책을 모아두었어요. 표지를 눌러 살펴보세요.</p>
    </header>

    <div class="glt-search browse-search">
      <input
        v-model="query"
        type="search"
        placeholder="도서명 또는 작가명"
        @keyup.enter="applySearch"
      />
      <button v-if="query" class="glt-btn glt-btn-ghost" @click="clearSearch">초기화</button>
      <button class="glt-btn glt-btn-primary" @click="applySearch">검색</button>
    </div>

    <p v-if="!loading && total !== null" class="result-count">
      {{ total }}권
      <span v-if="activeQuery"> · 「{{ activeQuery }}」</span>
    </p>

    <div v-if="loading" class="glt-empty">불러오는 중…</div>
    <div v-else-if="error" class="glt-empty glt-card">{{ error }}</div>
    <div v-else-if="!novels.length" class="glt-empty glt-card">
      <p>아직 담긴 책이 없어요.</p>
      <router-link to="/register" class="glt-btn glt-btn-primary">문장 등록하기</router-link>
    </div>
    <template v-else>
      <ul class="novel-grid">
        <li v-for="novel in novels" :key="novel.id">
          <router-link :to="`/novels/${novel.id}`" class="novel-card glt-card">
            <img
              v-if="novel.cover_url"
              :src="novel.cover_url"
              :alt="novel.title"
              class="novel-cover"
            />
            <div v-else class="novel-cover novel-cover--empty">📖</div>
            <div class="novel-meta">
              <strong class="novel-title">{{ novel.title }}</strong>
              <span v-if="novel.author" class="novel-author">{{ novel.author.name }}</span>
              <span class="novel-quotes">{{ novel.quote_count }}문장</span>
            </div>
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

export default {
  name: 'NovelsView',
  components: { PaginationBar },
  data() {
    return {
      novels: [],
      total: null,
      query: '',
      activeQuery: '',
      page: 1,
      pageSize: 24,
      loading: true,
      error: '',
    }
  },
  watch: {
    '$route.query': {
      immediate: true,
      handler(query) {
        this.query = query.q || ''
        this.activeQuery = query.q || ''
        this.page = Math.max(1, Number(query.page) || 1)
        this.loadNovels()
      },
    },
  },
  methods: {
    async loadNovels() {
      this.loading = true
      this.error = ''
      try {
        const skip = (this.page - 1) * this.pageSize
        const res = await api.browseNovels({
          q: this.activeQuery || undefined,
          skip,
          limit: this.pageSize,
        })
        this.novels = res.items
        this.total = res.total
        if (this.page > 1 && !res.items.length) {
          this.goToPage(1)
        }
      } catch (e) {
        this.error = e.message
        this.novels = []
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
      this.$router.push({ path: '/novels', query: next })
    },
    clearSearch() {
      this.query = ''
      this.$router.push({ path: '/novels' })
    },
    goToPage(page) {
      const next = { ...this.$route.query, page: String(page) }
      if (page <= 1) delete next.page
      this.$router.push({ path: '/novels', query: next })
    },
  },
}
</script>

<style scoped>
.browse-search {
  width: 100%;
  margin-bottom: var(--glt-space-3);
}

.result-count {
  margin: 0 0 var(--glt-space-3);
  font-size: 0.8rem;
  color: var(--glt-ink-tertiary);
}

.novel-grid {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(108px, 1fr));
  gap: 14px;
}

.novel-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px;
  text-decoration: none;
  color: inherit;
  transition: box-shadow 0.2s var(--glt-ease), transform 0.2s var(--glt-ease);
}

.novel-card:hover {
  box-shadow: var(--glt-shadow-md);
  transform: translateY(-2px);
}

.novel-cover {
  width: 100%;
  aspect-ratio: 3 / 4.1;
  object-fit: cover;
  border-radius: 6px;
  box-shadow: var(--glt-shadow-sm);
}

.novel-cover--empty {
  display: grid;
  place-items: center;
  background: var(--glt-bg-subtle);
  font-size: 1.4rem;
}

.novel-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.novel-title {
  font-size: 0.78rem;
  line-height: 1.35;
  color: var(--glt-ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.novel-author,
.novel-quotes {
  font-size: 0.72rem;
  color: var(--glt-ink-tertiary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
