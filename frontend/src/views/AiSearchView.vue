<template>
  <section class="ai-search glt-container">
    <header class="page-head">
      <h1 class="glt-title page-title">AI로 찾기</h1>

      <form class="search-hero" @submit.prevent="handleSearch">
        <div class="search-row">
          <input
            v-model="query"
            type="text"
            enterkeyhint="search"
            class="search-input"
            placeholder="느낌·키워드로 검색해 보세요"
            :disabled="loading"
          />
          <ClearIconButton v-if="query" @click="clearQuery" />
          <SearchIconButton
            type="submit"
            :disabled="loading || !query.trim()"
          />
        </div>
      </form>
    </header>

    <p v-if="error" class="error-msg">{{ error }}</p>

    <template v-if="result && !loading">
      <header class="news-head">
        <h2 class="news-summary">{{ result.summary }}</h2>
        <p class="news-meta">
          <strong>{{ result.query }}</strong> · {{ result.articles.length }}건
        </p>
      </header>

      <ul class="news-list">
        <li v-for="(article, i) in result.articles" :key="i">
          <article class="news-card">
            <blockquote class="news-quote">{{ article.quote }}</blockquote>
            <div class="news-byline">
              <div class="news-byline-fields">
                <div class="news-field">
                  <span class="news-label">출처</span>
                  <span class="news-source">{{ article.source_title }}</span>
                </div>
                <div v-if="article.author" class="news-field">
                  <span class="news-label">작가</span>
                  <span class="news-author">{{ article.author }}</span>
                </div>
              </div>
              <div class="news-byline-actions">
                <a
                  v-if="article.source_url"
                  :href="article.source_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="news-link"
                >
                  출처
                </a>
                <RegisterIconButton
                  label="등록"
                  @click="registerArticle(article)"
                />
              </div>
            </div>
            <p v-if="article.context" class="news-context">
              <span class="news-label">설명</span>
              <span>{{ article.context }}</span>
            </p>
          </article>
        </li>
      </ul>
    </template>

    <div v-else-if="searched && !loading" class="state-panel">
      아직 없어요
    </div>
  </section>
</template>

<script>
import { api } from '../api'
import ClearIconButton from '../components/ClearIconButton.vue'
import RegisterIconButton from '../components/RegisterIconButton.vue'
import SearchIconButton from '../components/SearchIconButton.vue'
import { loadAiSearchState, saveAiSearchState } from '../utils/aiSearchState'
import { registerRouteForAiArticle } from '../utils/registerBook'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'

export default {
  name: 'AiSearchView',
  components: { ClearIconButton, RegisterIconButton, SearchIconButton },
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

    clearQuery() {
      this.query = ''
      this.result = null
      this.searched = false
      this.error = ''
    },

    async handleSearch() {
      const q = this.query.trim()
      if (!q) return

      this.loading = true
      startPageLoading('AI가 찾는 중')
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
        endPageLoading()
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

.page-title {
  margin: 0 0 var(--glt-space-5);
}

.page-lead {
  margin: 4px 0 var(--glt-space-4);
  font-size: 0.8rem;
  line-height: 1.5;
  letter-spacing: -0.02em;
  word-break: keep-all;
  color: var(--glt-ink-secondary);
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

.search-input:disabled {
  opacity: 0.6;
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
  margin-bottom: var(--glt-space-4);
  padding-bottom: var(--glt-space-3);
  border-bottom: 1px solid var(--glt-glass-border);
}

.news-summary {
  margin: 0 0 6px;
  font-size: 0.88rem;
  font-weight: 600;
  line-height: 1.55;
  letter-spacing: -0.01em;
  color: var(--glt-ink-secondary);
}

.news-meta {
  margin: 0;
  font-size: 0.76rem;
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
  gap: 10px;
}

.news-card {
  padding: 14px 16px;
  border: 1px solid rgba(212, 195, 170, 0.42);
  border-radius: var(--glt-radius-lg);
  background: var(--glt-surface);
  box-shadow: 0 2px 10px rgba(61, 52, 41, 0.04);
}

.news-byline-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.news-quote {
  margin: 0;
  padding: 0;
  border: none;
  font-family: var(--glt-font-serif);
  font-size: 0.94rem;
  font-weight: 400;
  line-height: 1.72;
  letter-spacing: -0.01em;
  color: var(--glt-ink);
  word-break: keep-all;
}

.news-byline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(226, 213, 196, 0.65);
}

.news-byline-fields {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 12px;
  min-width: 0;
  flex: 1;
}

.news-field {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 5px 6px;
}

.news-label {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--glt-ink-tertiary);
}

.news-source {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--glt-ink-secondary);
}

.news-author {
  font-size: 0.78rem;
  color: var(--glt-ink-tertiary);
}

.news-context {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin: 10px 0 0;
  padding-top: 10px;
  border-top: 1px solid rgba(226, 213, 196, 0.45);
  font-size: 0.8rem;
  line-height: 1.6;
  color: var(--glt-ink-secondary);
}

.news-link {
  flex-shrink: 0;
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
