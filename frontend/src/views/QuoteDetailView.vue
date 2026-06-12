<template>
  <section v-if="loading" class="glt-empty">불러오는 중…</section>
  <section v-else-if="error" class="glt-empty">{{ error }}</section>
  <section v-else-if="quote" class="detail glt-container">
    <router-link to="/" class="back-link">← 목록</router-link>

    <header class="detail-header">
      <h1 class="glt-title">문장</h1>
    </header>

    <div v-if="hasLinkedNovel" class="add-quote-bar glt-card">
      <router-link :to="registerRoute" class="glt-btn glt-btn-primary add-quote-btn">
        문장 추가
      </router-link>
    </div>

    <div class="detail-graph glt-card">
      <div class="detail-source">
        <BookNode
          v-if="novelTitle"
          :title="novelTitle"
          :author="authorName"
          :quote-count="1"
          :color-index="bookColorIndex"
        />
        <div v-else-if="authorName" class="detail-source-fallback">
          <p class="fallback-author">{{ authorName }}</p>
        </div>
        <div class="detail-connector" />
      </div>
      <article class="detail-quote glt-card-raised">
        <p class="glt-quote glt-quote-lg">{{ quote.text }}</p>
      </article>
    </div>

    <section class="collect-section glt-card">
      <div v-if="novelTitle || authorName" class="book-readonly glt-card-raised">
        <router-link
          v-if="novelLinkId && novelTitle"
          :to="`/novels/${novelLinkId}`"
          class="readonly-title readonly-link"
        >
          {{ novelTitle }}
        </router-link>
        <p v-else-if="novelTitle" class="readonly-title">{{ novelTitle }}</p>
        <p v-if="authorName" class="readonly-author">{{ authorName }}</p>
      </div>

      <button
        type="button"
        class="glt-btn collect-btn"
        :class="isBookmarked ? 'glt-btn-ghost is-collected' : 'glt-btn-primary'"
        @click="toggleBookmark"
      >
        {{ isBookmarked ? COLLECT.done : COLLECT.action }}
      </button>
      <p v-if="collectMessage" class="collect-message" :class="{ 'is-error': collectIsError }">
        {{ collectMessage }}
      </p>
    </section>
  </section>
</template>

<script>
import { api } from '../api'
import BookNode from '../components/BookNode.vue'
import { COLLECT } from '../utils/collectLabels'
import { quoteAuthorName, quoteNovelId, quoteSourceTitle } from '../utils/quoteDisplay'
import { registerRouteForNovel, registerRouteForQuote } from '../utils/registerBook'

export default {
  name: 'QuoteDetailView',
  components: { BookNode },
  data() {
    return {
      quote: null,
      loading: true,
      error: '',
      collectMessage: '',
      collectIsError: false,
      isBookmarked: false,
      COLLECT,
    }
  },
  computed: {
    authorName() {
      return quoteAuthorName(this.quote)
    },
    novelTitle() {
      return quoteSourceTitle(this.quote)
    },
    novelLinkId() {
      return quoteNovelId(this.quote)
    },
    hasLinkedNovel() {
      return !!this.novelLinkId
    },
    bookColorIndex() {
      return (this.novelLinkId || 0) % 8
    },
    registerRoute() {
      if (this.quote?.novel) {
        return registerRouteForNovel(this.quote.novel)
      }
      return registerRouteForQuote(this.$route.params.id)
    },
  },
  watch: {
    '$route.params.id': {
      immediate: true,
      handler() {
        this.loadQuote()
      },
    },
  },
  methods: {
    async loadQuote() {
      this.loading = true
      this.error = ''
      this.collectMessage = ''
      try {
        const id = this.$route.params.id
        const [quote, bookmarkRes] = await Promise.all([
          api.getQuote(id),
          api.getBookmarkIds().catch(() => ({ quote_ids: [] })),
        ])
        this.quote = quote
        this.isBookmarked = (bookmarkRes.quote_ids || []).includes(quote.id)
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    },
    async toggleBookmark() {
      if (!this.quote) return
      this.collectMessage = ''
      this.collectIsError = false
      try {
        if (this.isBookmarked) {
          await api.removeBookmark(this.quote.id)
          this.isBookmarked = false
        } else {
          await api.addBookmark(this.quote.id)
          this.isBookmarked = true
        }
      } catch (e) {
        this.collectMessage = e.message
        this.collectIsError = true
      }
    },
  },
}
</script>

<style scoped>
.back-link {
  display: inline-block;
  margin-bottom: var(--glt-space-3);
  color: var(--glt-ink-secondary);
  font-size: 0.85rem;
}

.detail-header {
  margin-bottom: var(--glt-space-4);
}

.detail-header .glt-title {
  margin-top: 0;
}

.add-quote-bar {
  display: flex;
  justify-content: flex-end;
  padding: 12px 16px;
  margin-bottom: var(--glt-space-3);
}

.add-quote-btn {
  font-size: 0.82rem;
  padding: 8px 14px;
}

.detail-graph {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--glt-space-3);
  padding: var(--glt-space-4);
  margin-bottom: var(--glt-space-3);
}

.detail-source {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.detail-connector {
  width: 2px;
  height: 28px;
  background: linear-gradient(180deg, var(--glt-line-active), var(--glt-accent-muted));
  position: relative;
}

.detail-connector::after {
  content: '';
  position: absolute;
  left: 50%;
  bottom: -4px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--glt-accent-soft);
  border: 2px solid var(--glt-accent-muted);
  transform: translateX(-50%);
}

.detail-quote {
  width: 100%;
  padding: var(--glt-space-4);
}

.detail-source-fallback {
  width: var(--glt-book-width);
  padding: var(--glt-space-5);
  background: var(--glt-surface);
  border: 1px dashed var(--glt-line);
  border-radius: var(--glt-radius-md);
}

.fallback-author {
  margin: 0;
  font-size: 0.85rem;
  color: var(--glt-ink-secondary);
}

.collect-section {
  padding: var(--glt-space-4);
}

.book-readonly {
  padding: var(--glt-space-3) var(--glt-space-4);
  margin-bottom: var(--glt-space-4);
}

.readonly-title {
  margin: 0 0 4px;
  font-size: 1rem;
  font-weight: 700;
  color: var(--glt-ink);
}

.readonly-link {
  display: inline-block;
  text-decoration: none;
  color: var(--glt-accent-hover);
}

.readonly-link:hover {
  text-decoration: underline;
}

.readonly-author {
  margin: 0;
  font-size: 0.86rem;
  color: var(--glt-ink-secondary);
}

.collect-btn {
  width: 100%;
  padding: 12px 18px;
  font-size: 0.92rem;
}

.collect-btn.is-collected {
  color: var(--glt-accent-hover);
  border-color: var(--glt-accent-muted);
  background: var(--glt-accent-soft);
}

.collect-message {
  margin-top: var(--glt-space-3);
  color: var(--glt-accent);
  font-size: 0.875rem;
}

.collect-message.is-error {
  color: var(--glt-accent-hover);
}
</style>
