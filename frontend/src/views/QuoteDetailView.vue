<template>
  <div
    ref="sheetEl"
    class="quote-sheet"
    :class="{ 'is-dragging': sheetDragging }"
    :style="sheetStyle"
  >
    <!-- Drag handle zone -->
    <div
      class="sheet-drag-zone"
      @pointerdown="onDragStart"
      @pointermove="onDragMove"
      @pointerup="onDragEnd"
      @pointercancel="onDragEnd"
    >
      <div class="sheet-handle-pill" aria-hidden="true" />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="sheet-state">
      <span class="loading-spinner" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="sheet-state sheet-state--error">{{ error }}</div>

    <!-- Content -->
    <div v-else-if="quote" class="sheet-body">
      <blockquote class="sheet-quote">{{ quote.text }}</blockquote>

      <component
        v-if="novelTitle || authorName"
        :is="novelLinkId ? 'router-link' : 'div'"
        v-bind="novelLinkId ? { to: `/novels/${novelLinkId}` } : {}"
        class="sheet-source"
        :class="{ 'sheet-source--static': !novelLinkId }"
      >
        <img v-if="coverUrl" :src="coverUrl" :alt="novelTitle" class="sheet-cover" />
        <div v-else class="sheet-cover sheet-cover--empty">📖</div>
        <div class="sheet-source-info">
          <span v-if="novelTitle" class="sheet-book">{{ novelTitle }}</span>
          <span v-if="authorName" class="sheet-author">{{ authorName }}</span>
        </div>
      </component>

      <div class="sheet-actions">
        <LikeButton :liked="isLiked" :count="quote.like_count || 0" @click="toggleLike" />
        <ScrapButton :scrapped="isScrapped" :count="quote.scrap_count || 0" @click="toggleScrap" />
      </div>

      <router-link
        v-if="novelLinkId && novelQuoteCount > 0"
        :to="`/novels/${novelLinkId}`"
        class="sheet-novel-link"
      >
        이 책의 문장 {{ novelQuoteCount }}개 →
      </router-link>

      <div class="sheet-footer">
        <p v-if="quoteMeta" class="sheet-meta">{{ quoteMeta }}</p>
        <router-link v-if="hasLinkedNovel" :to="registerRoute" class="sheet-add-btn">
          문장 추가
        </router-link>
      </div>

      <p v-if="likeMessage" class="sheet-msg" :class="{ 'is-error': likeIsError }">
        {{ likeMessage }}
      </p>
    </div>
  </div>
</template>

<script>
import { api } from '../api'
import LikeButton from '../components/LikeButton.vue'
import ScrapButton from '../components/ScrapButton.vue'
import { requireLogin } from '../utils/auth'
import { toggleLike as toggleLikeRequest } from '../utils/likeToggle'
import { toggleScrap as toggleScrapRequest } from '../utils/scrapToggle'
import { quoteAuthorName, quoteCoverUrl, quoteNovelId, quoteSourceTitle } from '../utils/quoteDisplay'
import { registerRouteForNovel, registerRouteForQuote } from '../utils/registerBook'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'

export default {
  name: 'QuoteDetailView',
  components: { LikeButton, ScrapButton },
  data() {
    return {
      quote: null,
      loading: true,
      error: '',
      likeMessage: '',
      likeIsError: false,
      isLiked: false,
      likedIds: new Set(),
      isScrapped: false,
      scrappedIds: new Set(),
      sheetDragY: 0,
      sheetDragging: false,
      sheetDragPointerId: null,
      sheetDragStartY: 0,
      sheetDragStartOffset: 0,
    }
  },
  computed: {
    authorName() { return quoteAuthorName(this.quote) },
    novelTitle() { return quoteSourceTitle(this.quote) },
    coverUrl() { return quoteCoverUrl(this.quote) || '' },
    novelLinkId() { return quoteNovelId(this.quote) },
    hasLinkedNovel() { return !!this.novelLinkId },
    novelQuoteCount() { return Number(this.quote?.novel?.quote_count) || 0 },
    registerRoute() {
      if (this.quote?.novel) return registerRouteForNovel(this.quote.novel)
      return registerRouteForQuote(this.$route.params.id)
    },
    quoteMeta() {
      if (!this.quote) return ''
      const parts = []
      const name = this.quote.registered_by?.name
      if (name) parts.push(name)
      if (this.quote.created_at) {
        const d = new Date(this.quote.created_at)
        parts.push(`${d.getFullYear()}. ${d.getMonth() + 1}. ${d.getDate()}.`)
      }
      return parts.join('  ·  ')
    },
    sheetStyle() {
      if (this.sheetDragY <= 0) return null
      return { transform: `translateY(${this.sheetDragY}px)` }
    },
  },
  watch: {
    '$route.params.id': {
      immediate: true,
      handler() { this.loadQuote() },
    },
  },
  methods: {
    async loadQuote() {
      this.loading = true
      startPageLoading()
      this.error = ''
      this.likeMessage = ''
      try {
        const id = this.$route.params.id
        const [quote, likedRes, scrappedRes] = await Promise.all([
          api.getQuote(id),
          api.getLikeIds().catch(() => ({ quote_ids: [] })),
          api.getScrapIds().catch(() => ({ quote_ids: [] })),
        ])
        this.quote = quote
        this.likedIds = new Set(likedRes.quote_ids || [])
        this.isLiked = this.likedIds.has(quote.id)
        this.scrappedIds = new Set(scrappedRes.quote_ids || [])
        this.isScrapped = this.scrappedIds.has(quote.id)
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
        endPageLoading()
      }
    },

    onDragStart(event) {
      const sheet = this.$refs.sheetEl
      if (!sheet || sheet.scrollTop > 0) return
      if (event.pointerType === 'mouse' && event.button !== 0) return
      this.sheetDragging = true
      this.sheetDragPointerId = event.pointerId
      this.sheetDragStartY = event.clientY
      this.sheetDragStartOffset = this.sheetDragY
      event.currentTarget.setPointerCapture(event.pointerId)
    },
    onDragMove(event) {
      if (!this.sheetDragging || event.pointerId !== this.sheetDragPointerId) return
      const delta = event.clientY - this.sheetDragStartY
      this.sheetDragY = Math.max(0, this.sheetDragStartOffset + delta)
    },
    onDragEnd(event) {
      if (event.pointerId !== this.sheetDragPointerId) return
      const zone = event.currentTarget
      if (zone?.hasPointerCapture?.(event.pointerId)) zone.releasePointerCapture(event.pointerId)
      const shouldClose = this.sheetDragY > 96
      this.sheetDragging = false
      this.sheetDragPointerId = null
      if (shouldClose) {
        const sheet = this.$refs.sheetEl
        this.sheetDragY = sheet?.offsetHeight || 600
        window.setTimeout(() => this.$router.back(), 260)
        return
      }
      this.sheetDragY = 0
    },

    async toggleLike() {
      if (!this.quote) return
      if (!requireLogin(this.$router, this.$route.fullPath)) return
      this.likeMessage = ''
      this.likeIsError = false
      try {
        const { likedIds, likeCount, liked } = await toggleLikeRequest(api, this.likedIds, this.quote.id)
        this.likedIds = likedIds
        this.isLiked = liked
        this.quote = { ...this.quote, like_count: likeCount }
      } catch (e) {
        this.likeMessage = e.message
        this.likeIsError = true
      }
    },
    async toggleScrap() {
      if (!this.quote) return
      if (!requireLogin(this.$router, this.$route.fullPath)) return
      this.likeMessage = ''
      this.likeIsError = false
      try {
        const { scrappedIds, scrapCount, scrapped } = await toggleScrapRequest(api, this.scrappedIds, this.quote.id)
        this.scrappedIds = scrappedIds
        this.isScrapped = scrapped
        this.quote = { ...this.quote, scrap_count: scrapCount }
      } catch (e) {
        this.likeMessage = e.message
        this.likeIsError = true
      }
    },

    goBack() {
      if (window.history.length > 1) this.$router.back()
      else this.$router.push('/')
    },
  },
}
</script>

<style scoped>
.quote-sheet {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 150;
  width: 100%;
  max-width: var(--glt-app-width);
  max-height: calc(100dvh - var(--glt-safe-top) - 6px);
  margin: 0 auto;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  background: var(--glt-bg);
  border-radius: 20px 20px 0 0;
  box-shadow: 0 -16px 48px rgba(61, 52, 41, 0.14);
  transition: transform 0.28s var(--glt-ease);
}

.quote-sheet.is-dragging {
  transition: none;
}

.sheet-drag-zone {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 14px 20px 10px;
  cursor: grab;
  touch-action: none;
  user-select: none;
}

.sheet-drag-zone:active {
  cursor: grabbing;
}

.sheet-handle-pill {
  width: 36px;
  height: 4px;
  background: rgba(170, 145, 120, 0.35);
  border-radius: 999px;
}

.sheet-state {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 60px 20px;
  color: var(--glt-ink-tertiary);
  font-size: 0.9rem;
}

.sheet-state--error {
  color: var(--glt-accent-hover);
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

@keyframes spin {
  to { transform: rotate(360deg); }
}

.sheet-body {
  padding: 4px 20px calc(env(safe-area-inset-bottom, 0px) + 32px);
}

.sheet-quote {
  margin: 0 0 22px;
  padding: 0;
  border: none;
  font-family: var(--glt-font-serif);
  font-size: 1.18rem;
  font-weight: 400;
  line-height: 1.92;
  letter-spacing: -0.01em;
  color: var(--glt-ink);
  word-break: keep-all;
  overflow-wrap: anywhere;
}

.sheet-source {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 14px;
  background: linear-gradient(120deg, #d6ede5 0%, #eaf5f0 100%);
  text-decoration: none;
  color: inherit;
  margin-bottom: 20px;
  transition: opacity 0.15s var(--glt-ease);
}

.sheet-source:not(.sheet-source--static):hover {
  opacity: 0.82;
}

.sheet-source--static {
  pointer-events: none;
}

.sheet-cover {
  width: 44px;
  height: 60px;
  object-fit: cover;
  border-radius: 5px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(40, 80, 60, 0.2);
}

.sheet-cover--empty {
  display: grid;
  place-items: center;
  background: rgba(74, 142, 132, 0.12);
  font-size: 1.2rem;
  border-radius: 5px;
}

.sheet-source-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.sheet-book {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e3d32;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sheet-author {
  font-size: 0.8rem;
  color: #4a7a6a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sheet-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.sheet-novel-link {
  display: block;
  margin-bottom: 20px;
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--glt-accent);
  text-decoration: none;
  letter-spacing: -0.01em;
}

.sheet-novel-link:hover {
  text-decoration: underline;
}

.sheet-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-top: 4px;
  border-top: 1px solid var(--glt-glass-border);
  margin-top: 4px;
}

.sheet-meta {
  margin: 0;
  font-size: 0.76rem;
  color: var(--glt-ink-tertiary);
  letter-spacing: 0.01em;
}

.sheet-add-btn {
  flex-shrink: 0;
  padding: 7px 14px;
  border-radius: var(--glt-radius-full);
  background: transparent;
  border: 1px solid var(--glt-glass-border);
  color: var(--glt-ink-secondary);
  font-size: 0.78rem;
  font-weight: 600;
  text-decoration: none;
  transition: border-color 0.15s, color 0.15s;
}

.sheet-add-btn:hover {
  border-color: var(--glt-accent);
  color: var(--glt-accent);
}

.sheet-msg {
  margin: 14px 0 0;
  font-size: 0.82rem;
  color: var(--glt-accent);
  text-align: center;
}

.sheet-msg.is-error {
  color: var(--glt-accent-hover);
}
</style>
