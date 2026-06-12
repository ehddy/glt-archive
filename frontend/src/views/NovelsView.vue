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

    <p v-if="!initialLoading && total !== null" class="result-count">
      {{ total }}권
      <span v-if="activeQuery"> · 「{{ activeQuery }}」</span>
    </p>

    <div v-if="initialLoading" class="glt-empty">불러오는 중…</div>
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

      <LoadMoreBar
        :shown="novels.length"
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

export default {
  name: 'NovelsView',
  components: { LoadMoreBar },
  data() {
    return {
      novels: [],
      total: null,
      query: '',
      activeQuery: '',
      pageSize: 20,
      initialLoading: true,
      loadingMore: false,
      error: '',
    }
  },
  watch: {
    '$route.query': {
      immediate: true,
      handler(query) {
        this.query = query.q || ''
        this.activeQuery = query.q || ''
        this.loadNovels()
      },
    },
  },
  methods: {
    async loadNovels({ append = false } = {}) {
      if (append) {
        this.loadingMore = true
      } else {
        this.initialLoading = true
        this.novels = []
      }
      this.error = ''
      try {
        const skip = append ? this.novels.length : 0
        const res = await api.browseNovels({
          q: this.activeQuery || undefined,
          skip,
          limit: this.pageSize,
        })
        this.total = res.total
        if (append) {
          this.novels = [...this.novels, ...res.items]
        } else {
          this.novels = res.items
        }
      } catch (e) {
        this.error = e.message
        if (!append) this.novels = []
      } finally {
        this.initialLoading = false
        this.loadingMore = false
      }
    },
    loadMore() {
      if (this.loadingMore || this.novels.length >= this.total) return
      this.loadNovels({ append: true })
    },
    applySearch() {
      const q = this.query.trim()
      const next = { ...this.$route.query }
      if (q) next.q = q
      else delete next.q
      this.$router.push({ path: '/novels', query: next })
    },
    clearSearch() {
      this.query = ''
      this.$router.push({ path: '/novels' })
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
