<template>
  <section class="trends-view glt-container">
    <div v-if="loading" class="trends-loading">
      <span class="loading-spinner" />
    </div>

    <template v-else-if="data">
      <!-- 오늘의 문장 -->
      <section v-if="data.quote_of_day" class="trends-section">
        <div class="section-header">
          <span class="section-date">{{ formattedDate }}</span>
          <span class="section-sep">·</span>
          <span class="section-title">오늘의 문장</span>
        </div>
        <router-link :to="`/quotes/${data.quote_of_day.id}`" class="qod-card glt-card">
          <blockquote class="qod-text">{{ data.quote_of_day.text }}</blockquote>
          <footer class="qod-footer">
            <span v-if="sourceName(data.quote_of_day)" class="qod-source">{{ sourceName(data.quote_of_day) }}</span>
            <div class="qod-counts">
              <span v-if="data.quote_of_day.scrap_count" class="chip chip--scrap">
                <svg viewBox="0 0 24 24" width="11" height="11" aria-hidden="true"><path d="M5 3h14a1 1 0 0 1 1 1v17l-8-4-8 4V4a1 1 0 0 1 1-1z" fill="currentColor" /></svg>
                {{ data.quote_of_day.scrap_count }}
              </span>
              <span v-if="data.quote_of_day.like_count" class="chip chip--like">♥ {{ data.quote_of_day.like_count }}</span>
            </div>
          </footer>
        </router-link>
      </section>

      <!-- 오늘 가장 많이 담긴 문장 -->
      <section v-if="data.top_today.length" class="trends-section">
        <div class="section-header">
          <span class="section-icon">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M5 17H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11a2 2 0 0 1 2 2v3"/><rect x="9" y="11" width="14" height="10" rx="2"/></svg>
          </span>
          <span class="section-title">오늘 가장 많이 담긴 문장</span>
        </div>
        <ol class="rank-list">
          <li v-for="(q, i) in data.top_today" :key="q.id" class="rank-item">
            <router-link :to="`/quotes/${q.id}`" class="rank-link">
              <span class="rank-num" :class="`rank-num--${i + 1}`">{{ i + 1 }}</span>
              <div class="rank-body">
                <p class="rank-text">{{ q.text }}</p>
                <p v-if="sourceName(q)" class="rank-source">{{ sourceName(q) }}</p>
              </div>
              <span class="rank-count chip chip--scrap">
                <svg viewBox="0 0 24 24" width="10" height="10" aria-hidden="true"><path d="M5 3h14a1 1 0 0 1 1 1v17l-8-4-8 4V4a1 1 0 0 1 1-1z" fill="currentColor"/></svg>
                {{ q.scrap_count }}
              </span>
            </router-link>
          </li>
        </ol>
      </section>

      <!-- 이번 주 인기 문장 -->
      <section v-if="data.top_week.length" class="trends-section">
        <div class="section-header">
          <span class="section-icon">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
          </span>
          <span class="section-title">이번 주 인기 문장</span>
        </div>
        <ol class="rank-list">
          <li v-for="(q, i) in data.top_week" :key="q.id" class="rank-item">
            <router-link :to="`/quotes/${q.id}`" class="rank-link">
              <span class="rank-num" :class="`rank-num--${i + 1}`">{{ i + 1 }}</span>
              <div class="rank-body">
                <p class="rank-text">{{ q.text }}</p>
                <p v-if="sourceName(q)" class="rank-source">{{ sourceName(q) }}</p>
              </div>
              <span class="rank-count chip chip--like">♥ {{ q.like_count }}</span>
            </router-link>
          </li>
        </ol>
      </section>

      <!-- 역대 인기 문장 -->
      <section v-if="data.top_alltime.length" class="trends-section">
        <div class="section-header">
          <span class="section-icon">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          </span>
          <span class="section-title">역대 인기 문장</span>
        </div>
        <ol class="rank-list">
          <li v-for="(q, i) in data.top_alltime" :key="q.id" class="rank-item">
            <router-link :to="`/quotes/${q.id}`" class="rank-link">
              <span class="rank-num" :class="`rank-num--${i + 1}`">{{ i + 1 }}</span>
              <div class="rank-body">
                <p class="rank-text">{{ q.text }}</p>
                <p v-if="sourceName(q)" class="rank-source">{{ sourceName(q) }}</p>
              </div>
              <span class="rank-count chip chip--like">♥ {{ q.like_count }}</span>
            </router-link>
          </li>
        </ol>
      </section>

      <div v-if="isEmpty" class="trends-empty">
        <p>아직 데이터가 쌓이는 중이에요</p>
        <p class="trends-empty-sub">문장을 스크랩하거나 좋아요를 눌러 트렌드를 만들어보세요</p>
      </div>
    </template>

    <div v-else-if="error" class="glt-empty">{{ error }}</div>
  </section>
</template>

<script>
import { api } from '../api'
import { quoteAuthorName, quoteSourceTitle } from '../utils/quoteDisplay'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'

export default {
  name: 'TrendsView',
  data() {
    return { data: null, loading: true, error: '' }
  },
  computed: {
    formattedDate() {
      if (!this.data) return ''
      const [, m, d] = this.data.date.split('-')
      return `${Number(m)}월 ${Number(d)}일`
    },
    isEmpty() {
      if (!this.data) return true
      return !this.data.quote_of_day && !this.data.top_today.length && !this.data.top_week.length && !this.data.top_alltime.length
    },
  },
  mounted() { this.load() },
  methods: {
    async load() {
      this.loading = true
      startPageLoading()
      try {
        this.data = await api.getStatsOverview()
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
        endPageLoading()
      }
    },
    sourceName(q) {
      return quoteSourceTitle(q) || quoteAuthorName(q) || ''
    },
  },
}
</script>

<style scoped>
.trends-view {
  padding-bottom: 32px;
}

.trends-loading {
  display: flex;
  justify-content: center;
  padding: 60px 0;
}

.loading-spinner {
  display: block;
  width: 24px;
  height: 24px;
  border: 2px solid var(--glt-glass-border);
  border-top-color: var(--glt-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.trends-section {
  margin-bottom: 28px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 10px;
}

.section-date {
  font-size: 0.76rem;
  font-weight: 700;
  color: var(--glt-accent-hover);
  letter-spacing: 0.03em;
}

.section-sep {
  color: var(--glt-ink-faint);
  font-size: 0.76rem;
}

.section-icon {
  display: flex;
  align-items: center;
  color: var(--glt-ink-secondary);
}

.section-title {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--glt-ink);
  letter-spacing: -0.01em;
}

/* 오늘의 문장 */
.qod-card {
  display: block;
  text-decoration: none;
  color: inherit;
  padding: 20px;
  border-left: 3px solid var(--glt-accent);
  transition: box-shadow 0.18s var(--glt-ease);
}

.qod-card:hover { box-shadow: var(--glt-shadow-md); }

.qod-text {
  margin: 0 0 14px;
  padding: 0;
  border: none;
  font-family: var(--glt-font-serif);
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.82;
  letter-spacing: -0.01em;
  color: var(--glt-ink);
  word-break: keep-all;
  display: -webkit-box;
  -webkit-line-clamp: 5;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.qod-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.qod-source {
  font-size: 0.74rem;
  font-weight: 600;
  color: var(--glt-ink-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  min-width: 0;
}

.qod-counts {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

/* 칩 */
.chip {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 0.72rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.chip--scrap { color: var(--glt-accent-hover); }
.chip--like { color: #c4693a; }

/* 랭킹 리스트 */
.rank-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
  background: var(--glt-glass-border);
  border: 1px solid var(--glt-glass-border);
  border-radius: var(--glt-radius-lg);
  overflow: hidden;
}

.rank-item { background: var(--glt-surface); }

.rank-link {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 14px;
  text-decoration: none;
  color: inherit;
  transition: background 0.12s;
}

.rank-link:hover { background: var(--glt-bg-subtle); }

.rank-num {
  font-size: 0.88rem;
  font-weight: 800;
  min-width: 20px;
  text-align: center;
  flex-shrink: 0;
  color: var(--glt-ink-tertiary);
  padding-top: 2px;
  font-variant-numeric: tabular-nums;
}

.rank-num--1 { color: #c09a20; }
.rank-num--2 { color: #7a8fa0; }
.rank-num--3 { color: #a07050; }

.rank-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.rank-text {
  margin: 0;
  font-family: var(--glt-font-serif);
  font-size: 0.88rem;
  line-height: 1.6;
  color: var(--glt-ink);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: keep-all;
}

.rank-source {
  margin: 0;
  font-size: 0.7rem;
  color: var(--glt-ink-tertiary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rank-count {
  flex-shrink: 0;
  padding-top: 3px;
}

.trends-empty {
  padding: 48px 0;
  text-align: center;
  color: var(--glt-ink-secondary);
  font-size: 0.88rem;
}

.trends-empty-sub {
  margin-top: 6px;
  font-size: 0.76rem;
  color: var(--glt-ink-tertiary);
}
</style>
