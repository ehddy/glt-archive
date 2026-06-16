<template>
  <section class="trends-view glt-container">
    <div v-if="loading" class="trends-loading">
      <span class="loading-spinner" />
    </div>

    <template v-else-if="data">
      <!-- 오늘의 문장 -->
      <section v-if="data.quote_of_day" class="trends-section">
        <div class="section-label">
          <span class="label-date">{{ formattedDate }}</span>
          <span class="label-dot">·</span>
          <span class="label-title">오늘의 문장</span>
        </div>
        <router-link :to="`/quotes/${data.quote_of_day.id}`" class="qod-card glt-card">
          <blockquote class="qod-text">{{ data.quote_of_day.text }}</blockquote>
          <footer class="qod-meta">
            <span v-if="qodSource(data.quote_of_day)" class="qod-source">{{ qodSource(data.quote_of_day) }}</span>
            <div class="qod-counts">
              <span v-if="data.quote_of_day.scrap_count" class="count-chip count-chip--scrap">
                <svg viewBox="0 0 24 24" width="11" height="11" aria-hidden="true"><path d="M5 3h14a1 1 0 0 1 1 1v17l-8-4-8 4V4a1 1 0 0 1 1-1z" fill="currentColor" /></svg>
                {{ data.quote_of_day.scrap_count }}
              </span>
              <span v-if="data.quote_of_day.like_count" class="count-chip count-chip--like">
                ♥ {{ data.quote_of_day.like_count }}
              </span>
            </div>
          </footer>
        </router-link>
      </section>

      <!-- 오늘 가장 많이 담긴 문장 -->
      <section v-if="data.top_today.length" class="trends-section">
        <div class="section-label">
          <span class="section-icon">📌</span>
          <span class="label-title">오늘 가장 많이 담긴 문장</span>
        </div>
        <RankList :quotes="data.top_today" count-type="scrap" />
      </section>

      <!-- 이번 주 인기 문장 -->
      <section v-if="data.top_week.length" class="trends-section">
        <div class="section-label">
          <span class="section-icon">🔥</span>
          <span class="label-title">이번 주 인기 문장</span>
        </div>
        <RankList :quotes="data.top_week" count-type="like" />
      </section>

      <!-- 역대 인기 문장 -->
      <section v-if="data.top_alltime.length" class="trends-section">
        <div class="section-label">
          <span class="section-icon">⭐</span>
          <span class="label-title">역대 인기 문장</span>
        </div>
        <RankList :quotes="data.top_alltime" count-type="like" />
      </section>

      <div v-if="!data.quote_of_day && !data.top_today.length && !data.top_week.length && !data.top_alltime.length" class="trends-empty">
        <p>아직 데이터가 쌓이는 중이에요</p>
        <p class="trends-empty-sub">문장을 스크랩하거나 좋아요를 누르면 여기에 트렌드가 생겨요</p>
      </div>
    </template>

    <div v-else-if="error" class="glt-empty">{{ error }}</div>
  </section>
</template>

<script>
import { api } from '../api'
import { quoteAuthorName, quoteSourceTitle } from '../utils/quoteDisplay'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'

const RankList = {
  name: 'RankList',
  props: {
    quotes: { type: Array, required: true },
    countType: { type: String, default: 'like' },
  },
  template: `
    <ol class="rank-list">
      <li v-for="(q, i) in quotes" :key="q.id" class="rank-item">
        <router-link :to="'/quotes/' + q.id" class="rank-link">
          <span class="rank-num" :class="'rank-num--' + (i + 1)">{{ i + 1 }}</span>
          <div class="rank-body">
            <p class="rank-text">{{ q.text }}</p>
            <p v-if="sourceName(q)" class="rank-source">{{ sourceName(q) }}</p>
          </div>
          <span class="rank-count">
            <template v-if="countType === 'scrap'">
              <svg viewBox="0 0 24 24" width="11" height="11" aria-hidden="true"><path d="M5 3h14a1 1 0 0 1 1 1v17l-8-4-8 4V4a1 1 0 0 1 1-1z" fill="currentColor"/></svg>
              {{ q.scrap_count }}
            </template>
            <template v-else>♥ {{ q.like_count }}</template>
          </span>
        </router-link>
      </li>
    </ol>
  `,
  methods: {
    sourceName(q) { return quoteSourceTitle(q) || quoteAuthorName(q) || '' },
  },
}

export default {
  name: 'TrendsView',
  components: { RankList },
  data() {
    return { data: null, loading: true, error: '' }
  },
  computed: {
    formattedDate() {
      if (!this.data) return ''
      const [y, m, d] = this.data.date.split('-')
      return `${Number(m)}월 ${Number(d)}일`
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
    qodSource(q) { return quoteSourceTitle(q) || quoteAuthorName(q) || '' },
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
  margin-bottom: var(--glt-space-6);
}

.section-label {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: var(--glt-space-3);
}

.label-date {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--glt-accent-hover);
  letter-spacing: 0.02em;
}

.label-dot {
  color: var(--glt-ink-faint);
  font-size: 0.78rem;
}

.label-title {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--glt-ink);
}

.section-icon {
  font-size: 0.9rem;
  line-height: 1;
}

/* 오늘의 문장 카드 */
.qod-card {
  display: block;
  text-decoration: none;
  color: inherit;
  padding: var(--glt-space-5);
  background: linear-gradient(135deg, rgba(74, 142, 132, 0.06) 0%, var(--glt-surface) 100%);
  border: 1px solid rgba(74, 142, 132, 0.2);
  transition: box-shadow 0.2s var(--glt-ease), transform 0.2s var(--glt-ease);
}

.qod-card:hover {
  box-shadow: var(--glt-shadow-md);
  transform: translateY(-1px);
}

.qod-text {
  margin: 0 0 var(--glt-space-4);
  padding: 0;
  border: none;
  font-family: var(--glt-font-serif);
  font-size: 1.05rem;
  font-weight: 400;
  line-height: 1.8;
  letter-spacing: -0.01em;
  color: var(--glt-ink);
  word-break: keep-all;
  display: -webkit-box;
  -webkit-line-clamp: 5;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.qod-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  flex-wrap: wrap;
}

.qod-source {
  font-size: 0.76rem;
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
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.count-chip {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 0.74rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.count-chip--scrap { color: #4a8e84; }
.count-chip--like { color: #c4693a; }

/* 랭킹 리스트 */
.rank-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rank-item {
  display: block;
}

.rank-link {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 14px;
  background: var(--glt-surface);
  border: 1px solid var(--glt-glass-border);
  border-radius: var(--glt-radius-lg);
  text-decoration: none;
  color: inherit;
  transition: box-shadow 0.15s var(--glt-ease);
}

.rank-link:hover { box-shadow: var(--glt-shadow-sm); }

.rank-num {
  font-size: 0.98rem;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  min-width: 22px;
  text-align: center;
  flex-shrink: 0;
  color: var(--glt-ink-tertiary);
  padding-top: 1px;
}

.rank-num--1 { color: #c09a20; }
.rank-num--2 { color: #8a9aa8; }
.rank-num--3 { color: #a0714f; }

.rank-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
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
  font-size: 0.72rem;
  color: var(--glt-ink-tertiary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rank-count {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--glt-ink-tertiary);
  flex-shrink: 0;
  padding-top: 2px;
}

.trends-empty {
  padding: 48px 0;
  text-align: center;
  color: var(--glt-ink-secondary);
  font-size: 0.88rem;
  line-height: 1.6;
}

.trends-empty-sub {
  margin-top: 6px;
  font-size: 0.78rem;
  color: var(--glt-ink-tertiary);
}
</style>
