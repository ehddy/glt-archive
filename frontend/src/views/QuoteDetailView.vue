<template>
  <section v-if="error && !loading" class="glt-empty">{{ error }}</section>
  <section v-else-if="quote && !loading" class="detail glt-container">
    <BackLink use-history fallback-to="/" label="뒤로" />

    <header class="detail-header">
      <h1 class="glt-title">한 줄</h1>
      <router-link
        v-if="hasLinkedNovel"
        :to="registerRoute"
        class="add-quote-link"
      >
        문장 추가
      </router-link>
    </header>

    <div class="detail-graph glt-card">
      <div class="detail-source">
        <component
          :is="novelLinkId ? 'router-link' : 'div'"
          v-if="novelTitle"
          v-bind="novelLinkId ? { to: `/novels/${novelLinkId}` } : {}"
          class="detail-book-link"
          :class="{ 'detail-book-link--static': !novelLinkId }"
        >
          <BookNode
            :title="novelTitle"
            :author="authorName"
            :cover-url="coverUrl"
            :color-index="bookColorIndex"
          />
        </component>
        <div v-else-if="authorName" class="detail-source-fallback">
          <p class="fallback-author">{{ authorName }}</p>
        </div>
        <div class="detail-connector" />
      </div>
      <article class="detail-quote glt-card-raised">
        <p class="glt-quote glt-quote-lg">{{ quote.text }}</p>
        <div class="detail-like">
          <LikeButton
            :liked="isLiked"
            :count="quote.like_count || 0"
            @click="toggleLike"
          />
        </div>
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

      <p v-if="likeMessage" class="like-message" :class="{ 'is-error': likeIsError }">
        {{ likeMessage }}
      </p>
    </section>
  </section>
</template>

<script>
import { api } from '../api'
import BackLink from '../components/BackLink.vue'
import BookNode from '../components/BookNode.vue'
import LikeButton from '../components/LikeButton.vue'
import { requireLogin } from '../utils/auth'
import { toggleLike as toggleLikeRequest } from '../utils/likeToggle'
import { quoteAuthorName, quoteCoverUrl, quoteNovelId, quoteSourceTitle } from '../utils/quoteDisplay'
import { registerRouteForNovel, registerRouteForQuote } from '../utils/registerBook'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'

export default {
  name: 'QuoteDetailView',
  components: { BackLink, BookNode, LikeButton },
  data() {
    return {
      quote: null,
      loading: true,
      error: '',
      likeMessage: '',
      likeIsError: false,
      isLiked: false,
      likedIds: new Set(),
    }
  },
  computed: {
    authorName() {
      return quoteAuthorName(this.quote)
    },
    novelTitle() {
      return quoteSourceTitle(this.quote)
    },
    coverUrl() {
      return quoteCoverUrl(this.quote) || ''
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
      startPageLoading()
      this.error = ''
      this.likeMessage = ''
      try {
        const id = this.$route.params.id
        const [quote, likedRes] = await Promise.all([
          api.getQuote(id),
          api.getLikeIds().catch(() => ({ quote_ids: [] })),
        ])
        this.quote = quote
        this.likedIds = new Set(likedRes.quote_ids || [])
        this.isLiked = this.likedIds.has(quote.id)
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
        endPageLoading()
      }
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
  },
}
</script>

<style scoped>
.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: var(--glt-space-3);
}

.detail-header .glt-title {
  margin: 0;
}

.add-quote-link {
  flex-shrink: 0;
  padding: 6px 12px;
  border-radius: var(--glt-radius-full);
  background: var(--glt-accent);
  color: #fff;
  font-size: 0.76rem;
  font-weight: 600;
  text-decoration: none;
  box-shadow: 0 2px 8px rgba(196, 105, 58, 0.22);
}

.add-quote-link:hover {
  background: var(--glt-accent-hover);
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
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

.detail-book-link {
  text-decoration: none;
  color: inherit;
  cursor: pointer;
}

.detail-book-link--static {
  cursor: default;
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
  line-height: 1.45;
  color: var(--glt-ink);
  word-break: keep-all;
  overflow-wrap: anywhere;
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

.detail-like {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--glt-space-3);
}

.like-message {
  margin-top: var(--glt-space-3);
  color: var(--glt-accent);
  font-size: 0.875rem;
  text-align: center;
}

.like-message.is-error {
  color: var(--glt-accent-hover);
}
</style>
