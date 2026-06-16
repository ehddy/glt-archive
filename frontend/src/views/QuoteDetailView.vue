<template>
  <section class="quote-detail glt-container">
    <BackLink use-history fallback-to="/" label="뒤로" />

    <div v-if="!quote" class="detail-loading">
      <span class="loading-spinner" aria-hidden="true" />
    </div>

    <template v-else>
      <!-- Quote text -->
      <div class="quote-hero glt-card">
        <blockquote class="quote-text">{{ quote.text }}</blockquote>

        <!-- Book info -->
        <component
          :is="novelId ? 'router-link' : 'div'"
          v-bind="novelId ? { to: `/novels/${novelId}` } : {}"
          class="book-strip"
          :class="{ 'book-strip--static': !novelId }"
        >
          <img v-if="coverUrl" :src="coverUrl" :alt="novelTitle" class="book-cover" />
          <div v-else class="book-cover book-cover--empty">📖</div>
          <div class="book-info">
            <span class="book-title">{{ novelTitle }}</span>
            <span v-if="authorName" class="book-author">{{ authorName }}</span>
          </div>
        </component>

        <!-- Meta + actions -->
        <div class="quote-footer">
          <div class="quote-meta">
            <router-link
              v-if="registeredById"
              :to="`/users/${registeredById}`"
              class="meta-name"
            >{{ registeredByName }}</router-link>
            <span v-else-if="registeredByName" class="meta-name meta-name--static">{{ registeredByName }}</span>
            <span v-if="timeAgo" class="meta-time">{{ timeAgo }}</span>
          </div>
          <div class="quote-actions">
            <button
              type="button"
              class="action-btn action-btn--like"
              :class="{ 'is-active': liked }"
              @click="handleToggleLike"
            >
              <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
                <path
                  d="M12 21l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.18L12 21z"
                  :fill="liked ? 'currentColor' : 'none'"
                  stroke="currentColor"
                  stroke-width="1.75"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
              <span v-if="likeCount > 0">{{ likeCount }}</span>
            </button>
            <button
              type="button"
              class="action-btn action-btn--scrap"
              :class="{ 'is-active': scrapped }"
              @click="handleToggleScrap"
            >
              <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
                <path
                  d="M5 3h14a1 1 0 0 1 1 1v17l-8-4-8 4V4a1 1 0 0 1 1-1z"
                  :fill="scrapped ? 'currentColor' : 'none'"
                  stroke="currentColor"
                  stroke-width="1.75"
                  stroke-linejoin="round"
                />
              </svg>
              <span v-if="scrapCount > 0">{{ scrapCount }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Other quotes from same book -->
      <section v-if="otherQuotes.length" class="other-quotes">
        <h2 class="other-title">이 책의 다른 문장</h2>
        <ul class="other-list">
          <li v-for="q in otherQuotes" :key="q.id">
            <router-link :to="`/quotes/${q.id}`" class="other-item glt-card">
              <p class="other-text">{{ q.text }}</p>
              <div v-if="q.like_count > 0 || q.scrap_count > 0" class="other-counts">
                <span v-if="q.like_count > 0" class="other-count">
                  <svg viewBox="0 0 24 24" width="12" height="12" aria-hidden="true">
                    <path d="M12 21l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.18L12 21z" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  {{ q.like_count }}
                </span>
                <span v-if="q.scrap_count > 0" class="other-count">
                  <svg viewBox="0 0 24 24" width="12" height="12" aria-hidden="true">
                    <path d="M5 3h14a1 1 0 0 1 1 1v17l-8-4-8 4V4a1 1 0 0 1 1-1z" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linejoin="round"/>
                  </svg>
                  {{ q.scrap_count }}
                </span>
              </div>
            </router-link>
          </li>
        </ul>
      </section>
    </template>
  </section>
</template>

<script>
import { api } from '../api'
import BackLink from '../components/BackLink.vue'
import { isLoggedIn, requireLogin } from '../utils/auth'
import { toggleLike as toggleLikeRequest } from '../utils/likeToggle'
import { toggleScrap as toggleScrapRequest } from '../utils/scrapToggle'
import { quoteAuthorName, quoteCoverUrl, quoteSourceTitle } from '../utils/quoteDisplay'
import { formatRelativeTime } from '../utils/formatters'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'

export default {
  name: 'QuoteDetailView',
  components: { BackLink },
  data() {
    return {
      quote: null,
      novel: null,
      liked: false,
      scrapped: false,
      likedIds: new Set(),
      scrappedIds: new Set(),
    }
  },
  computed: {
    novelTitle() { return quoteSourceTitle(this.quote) },
    authorName() { return quoteAuthorName(this.quote) },
    coverUrl() { return quoteCoverUrl(this.quote) },
    novelId() { return this.quote?.novel?.id || this.quote?.source?.novel_id || null },
    likeCount() { return Number(this.quote?.like_count) || 0 },
    scrapCount() { return Number(this.quote?.scrap_count) || 0 },
    registeredById() { return this.quote?.registered_by?.id || null },
    registeredByName() { return this.quote?.registered_by?.name || '' },
    timeAgo() { return formatRelativeTime(this.quote?.created_at) },
    otherQuotes() {
      if (!this.novel?.quotes) return []
      return this.novel.quotes.filter(q => q.id !== this.quote?.id).slice(0, 5)
    },
  },
  watch: {
    '$route.params.id': { immediate: true, handler() { this.load() } },
  },
  methods: {
    async load() {
      startPageLoading()
      this.quote = null
      this.novel = null
      const id = Number(this.$route.params.id)
      if (!id) { endPageLoading(); return }
      try {
        const [quote, likedRes, scrappedRes] = await Promise.all([
          api.getQuote(id),
          isLoggedIn() ? api.getLikeIds().catch(() => ({ quote_ids: [] })) : { quote_ids: [] },
          isLoggedIn() ? api.getScrapIds().catch(() => ({ quote_ids: [] })) : { quote_ids: [] },
        ])
        this.quote = quote
        this.likedIds = new Set(likedRes.quote_ids || [])
        this.scrappedIds = new Set(scrappedRes.quote_ids || [])
        this.liked = this.likedIds.has(id)
        this.scrapped = this.scrappedIds.has(id)

        const novelId = quote?.novel?.id || quote?.source?.novel_id
        if (novelId) this.novel = await api.getNovel(novelId).catch(() => null)
      } catch {}
      finally { endPageLoading() }
    },
    async handleToggleLike() {
      if (!requireLogin(this.$router, this.$route.fullPath)) return
      try {
        const { likedIds, likeCount } = await toggleLikeRequest(api, this.likedIds, this.quote.id)
        this.likedIds = likedIds
        this.liked = likedIds.has(this.quote.id)
        this.quote = { ...this.quote, like_count: likeCount }
      } catch {}
    },
    async handleToggleScrap() {
      if (!requireLogin(this.$router, this.$route.fullPath)) return
      try {
        const { scrappedIds, scrapCount } = await toggleScrapRequest(api, this.scrappedIds, this.quote.id)
        this.scrappedIds = scrappedIds
        this.scrapped = scrappedIds.has(this.quote.id)
        this.quote = { ...this.quote, scrap_count: scrapCount }
      } catch {}
    },
  },
}
</script>

<style scoped>
.quote-hero {
  padding: var(--glt-space-5);
  display: flex;
  flex-direction: column;
  gap: var(--glt-space-4);
  margin-bottom: var(--glt-space-5);
}

.quote-text {
  margin: 0;
  padding: 0;
  border: none;
  font-family: var(--glt-font-serif);
  font-size: 1.12rem;
  font-weight: 400;
  line-height: 1.85;
  letter-spacing: -0.015em;
  color: var(--glt-ink);
  word-break: keep-all;
}

.book-strip {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 12px;
  background: linear-gradient(120deg, #d6ede5 0%, #eaf5f0 100%);
  text-decoration: none;
  color: inherit;
  transition: opacity 0.15s var(--glt-ease);
}

.book-strip:not(.book-strip--static):hover { opacity: 0.82; }
.book-strip--static { pointer-events: none; }

.book-cover {
  width: 40px;
  height: 56px;
  object-fit: cover;
  border-radius: 4px;
  flex-shrink: 0;
  box-shadow: 0 1px 6px rgba(40, 80, 60, 0.18);
}

.book-cover--empty {
  display: grid;
  place-items: center;
  background: rgba(74, 142, 132, 0.12);
  font-size: 1rem;
}

.book-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.book-title {
  font-size: 0.86rem;
  font-weight: 600;
  color: #1e3d32;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-author {
  font-size: 0.76rem;
  color: #4a7a6a;
}

.quote-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding-top: var(--glt-space-3);
  border-top: 1px solid var(--glt-glass-border);
}

.quote-meta {
  display: flex;
  align-items: baseline;
  gap: 6px;
  min-width: 0;
  overflow: hidden;
}

.meta-name {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--glt-ink-secondary);
  text-decoration: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.meta-name:not(.meta-name--static):hover {
  color: var(--glt-accent-hover);
  text-decoration: underline;
}

.meta-time {
  font-size: 0.74rem;
  color: var(--glt-ink-tertiary);
  white-space: nowrap;
  flex-shrink: 0;
}

.quote-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 7px 12px;
  border: none;
  border-radius: 999px;
  background: transparent;
  font-size: 0.84rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  cursor: pointer;
  transition: background 0.15s var(--glt-ease), color 0.15s var(--glt-ease);
  color: var(--glt-ink-tertiary);
}

.action-btn:hover { background: rgba(212, 195, 170, 0.22); }
.action-btn--like.is-active { color: #c18a8a; }
.action-btn--scrap.is-active { color: #4a8e84; }
.action-btn--like:hover { color: #c18a8a; }
.action-btn--scrap:hover { color: #4a8e84; }

.other-title {
  margin: 0 0 var(--glt-space-3);
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--glt-ink-secondary);
}

.other-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.other-item {
  display: block;
  padding: var(--glt-space-4);
  text-decoration: none;
  color: inherit;
  transition: box-shadow 0.2s var(--glt-ease);
}

.other-item:hover { box-shadow: var(--glt-shadow-md); }

.other-text {
  margin: 0;
  font-family: var(--glt-font-serif);
  font-size: 0.9rem;
  line-height: 1.7;
  color: var(--glt-ink);
  word-break: keep-all;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.other-counts {
  display: flex;
  gap: 10px;
  margin-top: 8px;
}

.detail-loading {
  display: flex;
  justify-content: center;
  padding: 60px 0;
}

.loading-spinner {
  display: block;
  width: 28px;
  height: 28px;
  border: 2px solid var(--glt-glass-border);
  border-top-color: var(--glt-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.other-count {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 0.74rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: var(--glt-ink-tertiary);
}
</style>
