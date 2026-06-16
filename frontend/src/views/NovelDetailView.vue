<template>
  <section v-if="error && !loading" class="glt-empty glt-container glt-card">{{ error }}</section>
  <section v-else-if="novel && !loading" class="novel-detail glt-container">
    <BackLink use-history fallback-to="/my-library" label="뒤로" />

    <div class="detail-body glt-card">
      <div class="detail-header">
        <img
          v-if="novel.cover_url"
          :src="novel.cover_url"
          :alt="`${novel.title} 표지`"
          class="detail-cover"
        />
        <div v-else class="detail-cover detail-cover--empty">📖</div>

        <div class="detail-head">
          <h1 class="detail-title">{{ novel.title }}</h1>
          <p v-if="novel.author" class="detail-author">{{ novel.author.name }}</p>

          <dl class="meta-list">
            <template v-if="novel.publisher">
              <dt>출판사</dt>
              <dd>{{ novel.publisher }}</dd>
            </template>
            <template v-if="novel.pub_date">
              <dt>출간일</dt>
              <dd>{{ novel.pub_date }}</dd>
            </template>
            <dt>문장</dt>
            <dd>{{ novel.quote_count }}개</dd>
          </dl>
        </div>
      </div>

      <p v-if="novel.description" class="detail-desc">{{ novel.description }}</p>

      <div class="detail-actions">
        <router-link :to="registerRoute" class="glt-btn glt-btn-primary detail-action-btn">
          문장 추가
        </router-link>
        <a
          v-if="aladinPurchaseUrl"
          :href="aladinPurchaseUrl"
          target="_blank"
          rel="noopener noreferrer"
          class="glt-btn glt-btn-ghost detail-action-btn"
        >
          구매
        </a>
      </div>
    </div>

    <section class="quotes-section">
      <h2 class="section-title">이 책의 한 줄</h2>

      <div v-if="!novel.quotes?.length" class="glt-empty glt-card">
        <p>아직 없어요</p>
        <router-link :to="registerRoute" class="glt-btn glt-btn-primary">첫 문장 등록</router-link>
      </div>

      <ul v-else class="quote-list">
        <li v-for="quote in novel.quotes" :key="quote.id">
          <router-link :to="`/quotes/${quote.id}`" class="quote-item glt-card">
            <p class="quote-text">{{ quote.text }}</p>
          </router-link>
        </li>
      </ul>
    </section>
  </section>
</template>

<script>
import { api } from '../api'
import BackLink from '../components/BackLink.vue'
import { getAladinPurchaseUrl } from '../utils/aladinLink'
import { registerRouteForNovel } from '../utils/registerBook'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'

export default {
  name: 'NovelDetailView',
  components: { BackLink },
  data() {
    return {
      novel: null,
      loading: true,
      error: '',
    }
  },
  computed: {
    registerRoute() {
      if (!this.novel) return { path: '/register' }
      return registerRouteForNovel(this.novel)
    },
    aladinPurchaseUrl() {
      return getAladinPurchaseUrl(this.novel)
    },
  },
  watch: {
    '$route.params.id': {
      immediate: true,
      handler() {
        this.loadNovel()
      },
    },
  },
  methods: {
    async loadNovel() {
      const id = Number(this.$route.params.id)
      if (!id) {
        this.error = '잘못된 주소예요.'
        this.loading = false
        return
      }
      this.loading = true
      startPageLoading()
      this.error = ''
      try {
        this.novel = await api.getNovel(id)
      } catch (e) {
        this.error = e.message
        this.novel = null
      } finally {
        this.loading = false
        endPageLoading()
      }
    },
  },
}
</script>

<style scoped>
.detail-body {
  display: flex;
  flex-direction: column;
  gap: var(--glt-space-4);
  padding: var(--glt-space-5);
  margin-bottom: var(--glt-space-5);
}

.detail-header {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: var(--glt-space-4);
  align-items: start;
}

.detail-cover {
  width: 120px;
  height: 172px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: var(--glt-shadow-md);
}

.detail-cover--empty {
  display: grid;
  place-items: center;
  background: var(--glt-bg-subtle);
  font-size: 2rem;
}

.detail-title {
  margin: 0 0 4px;
  font-size: 1.25rem;
  line-height: 1.4;
  color: var(--glt-ink);
}

.detail-author {
  margin: 0 0 var(--glt-space-3);
  font-size: 0.92rem;
  color: var(--glt-ink-secondary);
}

.meta-list {
  display: grid;
  grid-template-columns: 72px 1fr;
  gap: 6px 10px;
  margin: 0 0 var(--glt-space-3);
  font-size: 0.84rem;
}

.meta-list dt {
  color: var(--glt-ink-tertiary);
  font-weight: 600;
}

.meta-list dd {
  margin: 0;
  color: var(--glt-ink-secondary);
}

.detail-desc {
  margin: 0;
  padding-top: var(--glt-space-3);
  border-top: 1px solid var(--glt-glass-border);
  font-size: 0.86rem;
  line-height: 1.65;
  color: var(--glt-ink-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 6;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.detail-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(0, 1fr));
  gap: 8px;
  padding-top: var(--glt-space-3);
  border-top: 1px solid var(--glt-glass-border);
}

.detail-action-btn {
  width: 100%;
  text-decoration: none;
}

.quotes-section {
  margin-top: var(--glt-space-2);
}

.section-title {
  margin: 0 0 var(--glt-space-3);
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--glt-ink-secondary);
}

.quote-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.quote-item {
  display: block;
  padding: var(--glt-space-4);
  text-decoration: none;
  color: inherit;
  transition: box-shadow 0.2s var(--glt-ease);
}

.quote-item:hover {
  box-shadow: var(--glt-shadow-md);
}

.quote-text {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.65;
  color: var(--glt-ink);
  word-break: keep-all;
}

@media (max-width: 520px) {
  .detail-header {
    grid-template-columns: 96px 1fr;
    gap: var(--glt-space-3);
  }

  .detail-cover {
    width: 96px;
    height: 138px;
  }
}
</style>
