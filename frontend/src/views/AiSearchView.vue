<template>
  <section class="ai-search glt-container">
    <header class="page-head">
      <span class="ai-badge">AI</span>
      <h1 class="glt-title page-title">AI로 찾기</h1>
      <p class="page-lead">
        떠오르는 단어나 감정을 입력하면, AI가 어울리는 명문장과 출처를 골라 드려요.
      </p>
    </header>

    <form class="search-form glt-card" @submit.prevent="handleSearch">
      <div class="glt-search">
        <input
          v-model="query"
          type="search"
          placeholder="예: 사랑, 고통, 바다"
          :disabled="loading"
        />
        <button
          type="submit"
          class="glt-btn glt-btn-primary"
          :disabled="loading || !query.trim()"
        >
          {{ loading ? '검색 중…' : '검색' }}
        </button>
      </div>
    </form>

    <p v-if="error" class="error-msg">{{ error }}</p>

    <div v-if="loading" class="state-panel">
      <span class="state-spinner" aria-hidden="true" />
      AI가 명문장을 찾는 중…
    </div>

    <template v-else-if="result">
      <header class="news-head">
        <p class="news-kicker">검색 결과</p>
        <h2 class="news-summary">{{ result.summary }}</h2>
        <p class="news-meta">
          키워드 <strong>{{ result.query }}</strong> · {{ result.articles.length }}건
        </p>
      </header>

      <ul class="news-list">
        <li v-for="(article, i) in result.articles" :key="i">
          <article class="news-card">
            <blockquote class="news-quote">{{ article.quote }}</blockquote>
            <div class="news-byline">
              <div class="news-field">
                <span class="news-label">출처</span>
                <span class="news-source">{{ article.source_title }}</span>
              </div>
              <div v-if="article.author" class="news-field">
                <span class="news-label">작가</span>
                <span class="news-author">{{ article.author }}</span>
              </div>
            </div>
            <p v-if="article.context" class="news-context">
              <span class="news-label">설명</span>
              <span>{{ article.context }}</span>
            </p>
            <div class="news-actions">
              <button
                type="button"
                class="glt-btn glt-btn-primary news-register-btn"
                @click="registerArticle(article)"
              >
                이 문장 등록
              </button>
              <a
                v-if="article.source_url"
                :href="article.source_url"
                target="_blank"
                rel="noopener noreferrer"
                class="news-link"
              >
                출처 보기 →
              </a>
            </div>
          </article>
        </li>
      </ul>
    </template>

    <div v-else-if="searched" class="state-panel">
      결과가 없습니다.
    </div>
  </section>
</template>

<script>
import { api } from '../api'
import { loadAiSearchState, saveAiSearchState } from '../utils/aiSearchState'
import { registerRouteForAiArticle } from '../utils/registerBook'

export default {
  name: 'AiSearchView',
  data() {
    return {
      query: '',
      result: null,
      loading: false,
      error: '',
      searched: false,
    }
  },
  mounted() {
    this.restoreSearchState()
  },

  methods: {
    restoreSearchState() {
      const saved = loadAiSearchState()
      if (!saved?.result) return

      this.query = saved.query || ''
      this.result = saved.result
      this.searched = saved.searched ?? true
      this.error = ''
      this.loading = false
    },

    async handleSearch() {
      const q = this.query.trim()
      if (!q) return

      this.loading = true
      this.error = ''
      this.result = null
      this.searched = true

      try {
        this.result = await api.aiSearch(q)
        saveAiSearchState({
          query: this.query,
          result: this.result,
          searched: this.searched,
        })
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    },
    registerArticle(article) {
      saveAiSearchState({
        query: this.query,
        result: this.result,
        searched: this.searched,
      })
      this.$router.push(registerRouteForAiArticle(article))
    },
  },
}
</script>

<style scoped>
.page-head {
  margin-bottom: var(--glt-space-5);
}

.ai-badge {
  display: inline-block;
  margin-bottom: var(--glt-space-2);
  padding: 4px 10px;
  border-radius: var(--glt-radius-full);
  background: var(--glt-accent-soft);
  border: 1px solid var(--glt-accent-muted);
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--glt-accent-hover);
  letter-spacing: 0.02em;
}

.page-title {
  margin-top: 0;
}

.page-lead {
  margin: var(--glt-space-2) 0 0;
  font-size: 0.9rem;
  line-height: 1.65;
  color: var(--glt-ink-secondary);
}

.search-form {
  padding: var(--glt-space-4);
  margin-bottom: var(--glt-space-5);
}

.search-form .glt-search {
  width: 100%;
}

.error-msg {
  margin: 0 0 var(--glt-space-4);
  padding: 12px 14px;
  border-radius: var(--glt-radius-md);
  background: rgba(196, 105, 58, 0.08);
  border: 1px solid var(--glt-accent-muted);
  color: var(--glt-accent-hover);
  font-size: 0.86rem;
}

.news-head {
  margin-bottom: var(--glt-space-5);
  padding-bottom: var(--glt-space-4);
  border-bottom: 2px solid var(--glt-ink);
}

.news-kicker {
  margin: 0 0 var(--glt-space-2);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--glt-accent-hover);
}

.news-summary {
  margin: 0 0 var(--glt-space-2);
  font-size: 1.15rem;
  font-weight: 700;
  line-height: 1.45;
  letter-spacing: -0.02em;
  color: var(--glt-ink);
}

.news-meta {
  margin: 0;
  font-size: 0.8rem;
  color: var(--glt-ink-tertiary);
}

.news-meta strong {
  color: var(--glt-ink-secondary);
}

.news-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--glt-space-5);
}

.news-card {
  padding: 16px 18px;
  border: 1px solid rgba(212, 195, 170, 0.42);
  border-radius: var(--glt-radius-lg);
  background: var(--glt-surface);
  box-shadow: 0 2px 10px rgba(61, 52, 41, 0.04);
}

.news-quote {
  margin: 0 0 var(--glt-space-3);
  padding: 0;
  border: none;
  font-family: var(--glt-font-serif);
  font-size: 1.12rem;
  line-height: 1.75;
  color: var(--glt-ink);
  word-break: keep-all;
}

.news-byline {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 16px;
  margin-bottom: var(--glt-space-2);
}

.news-field {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 8px;
}

.news-label {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: var(--glt-accent-hover);
}

.news-source {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--glt-ink);
}

.news-author {
  font-size: 0.8rem;
  color: var(--glt-ink-secondary);
}

.news-context {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin: 0 0 var(--glt-space-3);
  font-size: 0.88rem;
  line-height: 1.65;
  color: var(--glt-ink-secondary);
}

.news-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px 16px;
}

.news-register-btn {
  padding: 8px 16px;
  font-size: 0.8rem;
}

.news-link {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--glt-ink-tertiary);
  text-decoration: none;
}

.news-link:hover {
  color: var(--glt-accent-hover);
  text-decoration: underline;
}

.state-panel {
  padding: var(--glt-space-10) var(--glt-space-4);
  text-align: center;
  font-size: 0.88rem;
  color: var(--glt-ink-tertiary);
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
