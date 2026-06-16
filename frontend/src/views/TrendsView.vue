<template>
  <section class="trends-view glt-container">

    <!-- 로그인 유도 -->
    <div v-if="!loggedIn" class="login-panel glt-card">
      <p class="login-title">로그인하면 내 활동을 분석해드려요</p>
      <p class="login-desc">스크랩·좋아요 내역을 기반으로 나만의 트렌드를 확인하세요</p>
      <div class="login-actions">
        <router-link :to="{ name: 'login', query: { redirect: '/trends' } }" class="glt-btn glt-btn-primary">로그인</router-link>
        <router-link :to="{ name: 'signup', query: { redirect: '/trends' } }" class="glt-btn glt-btn-ghost">회원가입</router-link>
      </div>
    </div>

    <div v-else-if="loading" class="trends-loading">
      <span class="loading-spinner" />
    </div>

    <template v-else-if="data">

      <!-- 전체 통계 (최상단 컴팩트 한 줄) -->
      <div class="stat-strip">
        <div class="stat-item">
          <span class="stat-value">{{ fmt(data.today_stats.scraps_today) }}</span>
          <span class="stat-label">오늘 담긴</span>
        </div>
        <div class="stat-divider" />
        <div class="stat-item">
          <span class="stat-value">{{ fmt(data.today_stats.quotes_today) }}</span>
          <span class="stat-label">오늘 등록</span>
        </div>
        <div class="stat-divider" />
        <div class="stat-item">
          <span class="stat-value">{{ fmt(data.today_stats.total_quotes) }}</span>
          <span class="stat-label">전체 문장</span>
        </div>
        <div class="stat-divider" />
        <div class="stat-item">
          <span class="stat-value">{{ fmt(data.today_stats.total_scraps) }}</span>
          <span class="stat-label">전체 스크랩</span>
        </div>
      </div>

      <!-- 오늘의 문장 -->
      <section v-if="data.quote_of_day" class="trends-section">
        <p class="section-eyebrow">Daily Pick <span class="eyebrow-date">· {{ formattedDate }}</span></p>
        <router-link :to="`/quotes/${data.quote_of_day.id}`" class="qod-card glt-card">
          <blockquote class="qod-text">{{ data.quote_of_day.text }}</blockquote>
          <footer class="qod-footer">
            <span v-if="sourceName(data.quote_of_day)" class="qod-source">{{ sourceName(data.quote_of_day) }}</span>
            <div class="qod-chips">
              <span v-if="data.quote_of_day.scrap_count" class="chip chip--scrap">
                <svg viewBox="0 0 24 24" width="10" height="10"><path d="M5 3h14a1 1 0 0 1 1 1v17l-8-4-8 4V4a1 1 0 0 1 1-1z" fill="currentColor"/></svg>{{ fmt(data.quote_of_day.scrap_count) }}
              </span>
              <span v-if="data.quote_of_day.like_count" class="chip chip--like">♥ {{ fmt(data.quote_of_day.like_count) }}</span>
            </div>
          </footer>
        </router-link>
      </section>

      <!-- 지금 많이 읽히는 책 -->
      <section v-if="data.top_books.length" class="trends-section">
        <p class="section-eyebrow">Trending</p>
        <div class="shelf-scroll">
          <router-link
            v-for="book in data.top_books"
            :key="book.id"
            :to="`/novels/${book.id}`"
            class="shelf-book"
          >
            <div class="shelf-cover-wrap">
              <img v-if="book.cover_url" :src="book.cover_url" :alt="book.title" class="shelf-cover" />
              <div v-else class="shelf-cover shelf-cover--empty">📖</div>
              <span class="shelf-badge">{{ fmt(book.quote_count) }}</span>
            </div>
            <p class="shelf-title">{{ book.title }}</p>
            <p v-if="book.author" class="shelf-author">{{ book.author.name }}</p>
          </router-link>
        </div>
      </section>

      <!-- 내 7일 활동 바 차트 -->
      <section class="trends-section">
        <p class="section-eyebrow">My Activity</p>
        <div class="bar-chart-wrap">
          <div class="bar-chart">
            <div v-for="day in data.weekly_activity" :key="day.label" class="bar-col">
              <div class="bar-track">
                <div class="bar-fill" :style="{ height: barPct(day.scraps + day.likes) + '%' }"></div>
              </div>
              <span class="bar-label">{{ day.label }}</span>
            </div>
          </div>
        </div>
        <div class="chart-footer">
          <span class="legend-dot legend-dot--accent"></span>
          <span class="legend-text">스크랩 + 좋아요</span>
          <span class="today-activity" v-if="todayActivity.scraps + todayActivity.likes > 0">
            · 오늘 {{ todayActivity.scraps + todayActivity.likes }}개 활동
          </span>
          <span class="today-activity today-activity--none" v-else>· 오늘 아직 활동이 없어요</span>
        </div>
      </section>

      <!-- 랭킹 -->
      <section class="trends-section trends-section--last">
        <!-- 담기 랭킹 -->
        <div class="rank-block">
          <div class="rank-block-header">
            <p class="rank-col-label">
              <svg viewBox="0 0 24 24" width="11" height="11" fill="currentColor"><path d="M5 3h14a1 1 0 0 1 1 1v17l-8-4-8 4V4a1 1 0 0 1 1-1z"/></svg>
              담기
            </p>
            <div class="rank-period-tabs">
              <button :class="['rank-tab', { 'rank-tab--active': scrapPeriod === 'today' }]" @click="scrapPeriod = 'today'">오늘</button>
              <button :class="['rank-tab', { 'rank-tab--active': scrapPeriod === 'week' }]" @click="scrapPeriod = 'week'">이번 주</button>
              <button :class="['rank-tab', { 'rank-tab--active': scrapPeriod === 'alltime' }]" @click="scrapPeriod = 'alltime'">역대</button>
            </div>
          </div>
          <ol class="rank-list">
            <li v-for="(q, i) in currentScraps" :key="q.id">
              <router-link :to="`/quotes/${q.id}`" class="rank-link">
                <span class="rank-num" :class="`rank-num--${i + 1}`">{{ i + 1 }}</span>
                <div class="rank-body">
                  <p class="rank-text">{{ q.text }}</p>
                  <p v-if="sourceName(q)" class="rank-source">{{ sourceName(q) }}</p>
                </div>
                <span class="chip chip--scrap">
                  <svg viewBox="0 0 24 24" width="10" height="10"><path d="M5 3h14a1 1 0 0 1 1 1v17l-8-4-8 4V4a1 1 0 0 1 1-1z" fill="currentColor"/></svg>{{ fmt(q.scrap_count) }}
                </span>
              </router-link>
            </li>
          </ol>
        </div>

        <!-- 좋아요 랭킹 -->
        <div class="rank-block">
          <div class="rank-block-header">
            <p class="rank-col-label rank-col-label--like">
              <svg viewBox="0 0 24 24" width="11" height="11" fill="currentColor"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
              좋아요
            </p>
            <div class="rank-period-tabs">
              <button :class="['rank-tab', { 'rank-tab--active': likePeriod === 'today' }]" @click="likePeriod = 'today'">오늘</button>
              <button :class="['rank-tab', { 'rank-tab--active': likePeriod === 'week' }]" @click="likePeriod = 'week'">이번 주</button>
              <button :class="['rank-tab', { 'rank-tab--active': likePeriod === 'alltime' }]" @click="likePeriod = 'alltime'">역대</button>
            </div>
          </div>
          <ol class="rank-list">
            <li v-for="(q, i) in currentLikes" :key="q.id">
              <router-link :to="`/quotes/${q.id}`" class="rank-link">
                <span class="rank-num" :class="`rank-num--${i + 1}`">{{ i + 1 }}</span>
                <div class="rank-body">
                  <p class="rank-text">{{ q.text }}</p>
                  <p v-if="sourceName(q)" class="rank-source">{{ sourceName(q) }}</p>
                </div>
                <span class="chip chip--like">♥ {{ fmt(q.like_count) }}</span>
              </router-link>
            </li>
          </ol>
        </div>
      </section>

    </template>

    <div v-else-if="error" class="glt-empty">{{ error }}</div>
  </section>
</template>

<script>
import { api } from '../api'
import { isLoggedIn } from '../utils/auth'
import { quoteAuthorName, quoteSourceTitle } from '../utils/quoteDisplay'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'

export default {
  name: 'TrendsView',
  data() {
    return { data: null, loading: false, error: '', maxActivity: 1, scrapPeriod: 'today', likePeriod: 'today' }
  },
  computed: {
    loggedIn() { return isLoggedIn() },
    formattedDate() {
      if (!this.data) return ''
      const [, m, d] = this.data.date.split('-')
      return `${Number(m)}월 ${Number(d)}일`
    },
    todayActivity() {
      if (!this.data || !this.data.weekly_activity.length) return { scraps: 0, likes: 0 }
      return this.data.weekly_activity[this.data.weekly_activity.length - 1]
    },
    currentScraps() {
      if (!this.data) return []
      if (this.scrapPeriod === 'today') return this.data.top_scraps_today
      if (this.scrapPeriod === 'week') return this.data.top_scraps_week
      return this.data.top_scraps_alltime
    },
    currentLikes() {
      if (!this.data) return []
      if (this.likePeriod === 'today') return this.data.top_likes_today
      if (this.likePeriod === 'week') return this.data.top_likes_week
      return this.data.top_likes_alltime
    },
  },
  mounted() {
    if (this.loggedIn) this.load()
  },
  methods: {
    async load() {
      this.loading = true
      startPageLoading()
      try {
        this.data = await api.getStatsOverview()
        this.maxActivity = Math.max(1, ...this.data.weekly_activity.map(d => d.scraps + d.likes))
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
        endPageLoading()
      }
    },
    barPct(val) { return Math.round((val / this.maxActivity) * 100) },
    sourceName(q) { return quoteSourceTitle(q) || quoteAuthorName(q) || '' },
    fmt(n) {
      if (n == null) return '0'
      if (n >= 100000000) return `${(n / 100000000).toFixed(1).replace(/\.0$/, '')}억`
      if (n >= 10000) return `${(n / 10000).toFixed(1).replace(/\.0$/, '')}만`
      if (n >= 1000) return `${(n / 1000).toFixed(1).replace(/\.0$/, '')}천`
      return String(n)
    },
  },
}
</script>

<style scoped>
.trends-view { padding-bottom: 32px; }

/* 로그인 패널 */
.login-panel {
  padding: 28px 20px;
  text-align: center;
  margin-top: 8px;
}

.login-title {
  margin: 0 0 6px;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--glt-ink);
}

.login-desc {
  margin: 0 0 18px;
  font-size: 0.82rem;
  color: var(--glt-ink-secondary);
  line-height: 1.6;
}

.login-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.trends-loading {
  display: flex;
  justify-content: center;
  padding: 56px 0;
}

.loading-spinner {
  display: block;
  width: 22px;
  height: 22px;
  border: 2px solid var(--glt-glass-border);
  border-top-color: var(--glt-accent);
  border-radius: 50%;
  animation: spin 0.75s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* 통계 스트립 */
.stat-strip {
  display: flex;
  align-items: center;
  background: var(--glt-surface);
  border: 1px solid var(--glt-glass-border);
  border-radius: var(--glt-radius-lg);
  padding: 10px 0;
  margin-bottom: 22px;
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.stat-divider {
  width: 1px;
  height: 28px;
  background: var(--glt-glass-border);
  flex-shrink: 0;
}

.stat-value {
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--glt-ink);
  letter-spacing: -0.03em;
  font-variant-numeric: tabular-nums;
  line-height: 1.1;
}

.stat-label { font-size: 0.62rem; color: var(--glt-ink-tertiary); font-weight: 500; }

/* 섹션 */
.trends-section { margin-bottom: 22px; }
.trends-section--last { margin-bottom: 0; }

.section-eyebrow {
  display: flex;
  align-items: center;
  gap: 5px;
  margin: 0 0 8px;
  font-size: 0.73rem;
  font-weight: 700;
  color: var(--glt-ink-secondary);
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.section-eyebrow svg { opacity: 0.65; flex-shrink: 0; }
.eyebrow-date { font-weight: 400; opacity: 0.6; }

/* 오늘의 문장 */
.qod-card {
  display: block;
  text-decoration: none;
  color: inherit;
  padding: 18px 20px 14px;
  border-left: 3px solid var(--glt-accent);
  transition: box-shadow 0.15s var(--glt-ease);
}

.qod-card:hover { box-shadow: var(--glt-shadow-md); }

.qod-text {
  margin: 0 0 12px;
  padding: 0;
  border: none;
  font-family: var(--glt-font-serif);
  font-size: 0.96rem;
  font-weight: 400;
  line-height: 1.8;
  letter-spacing: -0.01em;
  color: var(--glt-ink);
  word-break: keep-all;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.qod-footer { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.qod-source { font-size: 0.72rem; font-weight: 600; color: var(--glt-ink-secondary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; min-width: 0; }
.qod-chips { display: flex; gap: 7px; flex-shrink: 0; }

/* 바 차트 */
.bar-chart-wrap {
  padding-bottom: 18px; /* bar-label의 bottom: -14px 공간 확보 */
  overflow: hidden;     /* 가로 삐침 방지 */
}

.bar-chart {
  display: flex;
  align-items: flex-end;
  gap: 5px;
  height: 64px;
  background: var(--glt-surface);
  border: 1px solid var(--glt-glass-border);
  border-radius: var(--glt-radius-lg);
  padding: 10px 14px 20px;
  position: relative;
  margin-bottom: 8px;
}

.bar-col { flex: 1; display: flex; flex-direction: column; align-items: center; height: 100%; position: relative; }
.bar-track { flex: 1; width: 100%; display: flex; align-items: flex-end; }

.bar-fill {
  width: 100%;
  background: var(--glt-accent);
  opacity: 0.65;
  border-radius: 3px 3px 0 0;
  min-height: 2px;
  transition: height 0.45s cubic-bezier(0.4, 0, 0.2, 1);
}

.bar-label {
  position: absolute;
  bottom: -14px;
  font-size: 0.58rem;
  color: var(--glt-ink-tertiary);
  white-space: nowrap;
}

.chart-footer { display: flex; align-items: center; gap: 5px; padding-left: 2px; }
.legend-dot { display: inline-block; width: 8px; height: 8px; border-radius: 2px; }
.legend-dot--accent { background: var(--glt-accent); opacity: 0.65; }
.legend-text { font-size: 0.68rem; color: var(--glt-ink-tertiary); }
.today-activity { font-size: 0.68rem; color: var(--glt-accent-hover); font-weight: 600; }
.today-activity--none { color: var(--glt-ink-tertiary); font-weight: 400; }

/* 인기 책 책장 */
.shelf-scroll {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 4px 2px 8px;
  scrollbar-width: none;
  scroll-snap-type: x proximity;
  -webkit-overflow-scrolling: touch;
}

.shelf-scroll::-webkit-scrollbar { display: none; }

.shelf-book {
  flex: 0 0 80px;
  width: 80px;
  display: flex;
  flex-direction: column;
  gap: 5px;
  text-decoration: none;
  color: inherit;
  scroll-snap-align: start;
}

.shelf-cover-wrap { position: relative; width: 80px; height: 110px; }

.shelf-cover {
  width: 80px;
  height: 110px;
  object-fit: cover;
  border-radius: 5px;
  box-shadow: var(--glt-shadow-sm);
  display: block;
  transition: transform 0.18s var(--glt-ease);
}

.shelf-book:hover .shelf-cover { transform: translateY(-2px); }

.shelf-cover--empty {
  display: grid;
  place-items: center;
  background: var(--glt-bg-subtle);
  font-size: 1.2rem;
  border-radius: 5px;
}

.shelf-badge {
  position: absolute;
  bottom: 5px;
  right: 5px;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(4px);
  color: #fff;
  font-size: 0.62rem;
  font-weight: 700;
  padding: 2px 5px;
  border-radius: 4px;
  line-height: 1.4;
}

.shelf-title {
  margin: 0;
  font-size: 0.72rem;
  font-weight: 600;
  line-height: 1.3;
  color: var(--glt-ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.shelf-author {
  margin: 0;
  font-size: 0.66rem;
  color: var(--glt-ink-tertiary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 칩 */
.chip {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 0.7rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
}

.chip--scrap { color: var(--glt-accent-hover); }
.chip--like { color: #c4693a; }

/* 랭킹 블록 */
.rank-block {
  margin-bottom: 16px;
}

.rank-block:last-child {
  margin-bottom: 0;
}

.rank-block-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 7px;
}

.rank-period-tabs {
  display: flex;
  gap: 2px;
  background: var(--glt-surface);
  border: 1px solid var(--glt-glass-border);
  border-radius: 8px;
  padding: 2px;
}

.rank-tab {
  background: none;
  border: none;
  padding: 4px 11px;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--glt-ink-tertiary);
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.rank-tab--active {
  background: var(--glt-accent-soft);
  color: var(--glt-accent-hover);
}

.rank-cols {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.rank-col-label {
  display: flex;
  align-items: center;
  gap: 4px;
  margin: 0 0 6px;
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--glt-accent-hover);
  opacity: 0.8;
}

.rank-col-label svg { opacity: 0.75; }

.rank-col-label--like {
  color: #c4693a;
}

/* 랭킹 */
.rank-list {
  list-style: none;
  margin: 0;
  padding: 0;
  border: 1px solid var(--glt-glass-border);
  border-radius: var(--glt-radius-lg);
  overflow: hidden;
}

.rank-list li + li { border-top: 1px solid var(--glt-glass-border); }

.rank-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 13px;
  text-decoration: none;
  color: inherit;
  background: var(--glt-surface);
  transition: background 0.1s;
}

.rank-link:hover { background: var(--glt-bg-subtle); }

.rank-num {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-size: 0.72rem;
  font-weight: 800;
  flex-shrink: 0;
  color: #fff;
  background: var(--glt-ink-tertiary);
  font-variant-numeric: tabular-nums;
  line-height: 1;
  box-shadow: 0 1px 4px rgba(0,0,0,0.18);
}

.rank-num--1 {
  background: linear-gradient(145deg, #f7d060 0%, #c9900e 100%);
  box-shadow: 0 2px 6px rgba(201,144,14,0.35);
}
.rank-num--2 {
  background: linear-gradient(145deg, #d4dde5 0%, #8fa3b1 100%);
  box-shadow: 0 2px 6px rgba(100,130,150,0.3);
}
.rank-num--3 {
  background: linear-gradient(145deg, #d4956a 0%, #a0613a 100%);
  box-shadow: 0 2px 6px rgba(160,97,58,0.3);
}

.rank-body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }

.rank-text {
  margin: 0;
  font-family: var(--glt-font-serif);
  font-size: 0.84rem;
  line-height: 1.55;
  color: var(--glt-ink);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: keep-all;
}

.rank-source {
  margin: 0;
  font-size: 0.67rem;
  color: var(--glt-ink-tertiary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
