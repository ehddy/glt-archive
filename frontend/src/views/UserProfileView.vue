<template>
  <section class="user-profile glt-container">
    <!-- Header -->
    <header class="page-header">
      <button type="button" class="back-btn" @click="$router.back()" aria-label="뒤로">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" aria-hidden="true">
          <path d="M15 6l-6 6 6 6" />
        </svg>
      </button>
    </header>

    <!-- Profile hero -->
    <div class="profile-hero">
      <div class="profile-avatar">{{ avatarLetter }}</div>
      <div class="profile-info">
        <h1 class="profile-name">{{ displayName }}</h1>
      </div>
    </div>

    <!-- Tabs -->
    <div class="profile-tabs" role="tablist">
      <button
        role="tab"
        class="tab-btn"
        :class="{ active: activeTab === 'scraps' }"
        @click="switchTab('scraps')"
      >
        스크랩<span v-if="scrapsTotal !== null" class="tab-count">{{ scrapsTotal }}</span>
      </button>
      <button
        role="tab"
        class="tab-btn"
        :class="{ active: activeTab === 'posts' }"
        @click="switchTab('posts')"
      >
        게시글<span v-if="postsTotal !== null" class="tab-count">{{ postsTotal }}</span>
      </button>
    </div>

    <!-- Scraps tab -->
    <template v-if="activeTab === 'scraps'">
      <section v-if="scrappedBooks.length" class="mini-shelf">
        <header class="shelf-head">
          <h2 class="shelf-title">{{ displayName }}님의 책장</h2>
          <span class="shelf-count">{{ scrappedBooks.length }}권</span>
        </header>
        <div class="shelf-scroll">
          <router-link
            v-for="book in scrappedBooks"
            :key="book.id"
            :to="`/novels/${book.id}`"
            class="shelf-book"
          >
            <img v-if="book.cover_url" :src="book.cover_url" :alt="book.title" class="shelf-cover" />
            <div v-else class="shelf-cover shelf-cover--empty">📖</div>
            <p class="shelf-book-title">{{ book.title }}</p>
            <p v-if="book.authorName" class="shelf-book-author">{{ book.authorName }}</p>
          </router-link>
        </div>
      </section>

      <div v-if="scrapsLoading" class="page-state">
        <span class="loading-spinner" />
      </div>
      <div v-else-if="scrapsError" class="page-state">{{ scrapsError }}</div>
      <div v-else-if="!scraps.length" class="page-state">아직 스크랩한 문장이 없어요</div>
      <template v-else>
        <div class="quote-feed">
          <QuoteFeedItem
            v-for="q in scraps"
            :key="q.id"
            :quote="q"
            :liked="likedIds.has(q.id)"
            :scrapped="scrappedIds.has(q.id)"
            @toggle-like="handleToggleLike(q.id)"
            @toggle-scrap="handleToggleScrap(q.id)"
          />
        </div>
        <div ref="scrapsAnchor" class="scroll-anchor">
          <span v-if="scrapsLoadingMore" class="loading-spinner" aria-hidden="true" />
        </div>
      </template>
    </template>

    <!-- Posts tab -->
    <template v-else>
      <div v-if="postsLoading" class="page-state">
        <span class="loading-spinner" />
      </div>
      <div v-else-if="postsError" class="page-state">{{ postsError }}</div>
      <div v-else-if="!posts.length" class="page-state">아직 등록한 문장이 없어요</div>
      <template v-else>
        <div class="quote-feed">
          <QuoteFeedItem
            v-for="q in posts"
            :key="q.id"
            :quote="q"
            :liked="likedIds.has(q.id)"
            :scrapped="scrappedIds.has(q.id)"
            @toggle-like="handleToggleLike(q.id)"
            @toggle-scrap="handleToggleScrap(q.id)"
          />
        </div>
        <div ref="postsAnchor" class="scroll-anchor">
          <span v-if="postsLoadingMore" class="loading-spinner" aria-hidden="true" />
        </div>
      </template>
    </template>
  </section>
</template>

<script>
import { api } from '../api'
import QuoteFeedItem from '../components/QuoteFeedItem.vue'
import { isLoggedIn, requireLogin } from '../utils/auth'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'
import { toggleLike as toggleLikeRequest } from '../utils/likeToggle'
import { toggleScrap as toggleScrapRequest } from '../utils/scrapToggle'

export default {
  name: 'UserProfileView',
  components: { QuoteFeedItem },
  data() {
    return {
      userName: '',
      activeTab: 'scraps',

      scraps: [],
      scrapsTotal: null,
      scrapsLoading: true,
      scrapsLoadingMore: false,
      scrapsError: '',
      scrapsObserver: null,

      posts: [],
      postsTotal: null,
      postsLoading: false,
      postsLoadingMore: false,
      postsError: '',
      postsObserver: null,
      postsLoaded: false,

      likedIds: new Set(),
      scrappedIds: new Set(),
      pageSize: 20,
    }
  },
  computed: {
    userId() { return this.$route.params.id },
    displayName() {
      return this.userName || `사용자 ${this.userId}`
    },
    avatarLetter() {
      return (this.displayName || '?')[0].toUpperCase()
    },
    scrappedBooks() {
      const seen = new Set()
      const books = []
      for (const q of this.scraps) {
        const novelId = q.novel?.id || q.source?.novel_id
        if (!novelId || seen.has(novelId)) continue
        seen.add(novelId)
        books.push({
          id: novelId,
          title: q.novel?.title || q.source?.title || '',
          cover_url: q.novel?.cover_url || q.source?.cover_url || null,
          authorName: q.novel?.author?.name || q.source?.author?.name || null,
        })
      }
      return books
    },
  },
  watch: {
    '$route.params.id': {
      immediate: true,
      handler() { this.init() },
    },
    scrapsLoading(newVal, oldVal) {
      if (oldVal && !newVal) this.$nextTick(() => this.setupScrapsScroll())
    },
    postsLoading(newVal, oldVal) {
      if (oldVal && !newVal) this.$nextTick(() => this.setupPostsScroll())
    },
  },
  beforeUnmount() {
    if (this.scrapsObserver) this.scrapsObserver.disconnect()
    if (this.postsObserver) this.postsObserver.disconnect()
  },
  methods: {
    async init() {
      if (this.scrapsObserver) { this.scrapsObserver.disconnect(); this.scrapsObserver = null }
      if (this.postsObserver) { this.postsObserver.disconnect(); this.postsObserver = null }
      this.scraps = []
      this.posts = []
      this.postsLoaded = false
      this.activeTab = 'scraps'
      await Promise.all([this.loadUser(), this.loadScraps(), this.loadUserState()])
    },
    async loadUser() {
      try {
        const user = await api.getUser(this.userId)
        this.userName = user.name || ''
      } catch {}
    },
    async loadUserState() {
      if (!isLoggedIn()) return
      try {
        const [likedRes, scrappedRes] = await Promise.all([
          api.getLikeIds().catch(() => ({ quote_ids: [] })),
          api.getScrapIds().catch(() => ({ quote_ids: [] })),
        ])
        this.likedIds = new Set(likedRes.quote_ids || [])
        this.scrappedIds = new Set(scrappedRes.quote_ids || [])
      } catch {}
    },
    async loadScraps({ append = false } = {}) {
      if (append) {
        this.scrapsLoadingMore = true
      } else {
        this.scrapsLoading = true
        this.scraps = []
        startPageLoading()
      }
      this.scrapsError = ''
      try {
        const res = await api.getUserScraps(this.userId, {
          skip: append ? this.scraps.length : 0,
          limit: this.pageSize,
        })
        this.scrapsTotal = res.total
        this.scraps = append ? [...this.scraps, ...res.items] : res.items
      } catch (e) {
        this.scrapsError = e.message
      } finally {
        if (!append) { this.scrapsLoading = false; endPageLoading() }
        this.scrapsLoadingMore = false
      }
    },
    async loadPosts({ append = false } = {}) {
      if (append) {
        this.postsLoadingMore = true
      } else {
        this.postsLoading = true
        this.posts = []
      }
      this.postsError = ''
      try {
        const res = await api.getUserQuotes(this.userId, {
          skip: append ? this.posts.length : 0,
          limit: this.pageSize,
        })
        this.postsTotal = res.total
        this.posts = append ? [...this.posts, ...res.items] : res.items
        this.postsLoaded = true
      } catch (e) {
        this.postsError = e.message
      } finally {
        this.postsLoading = false
        this.postsLoadingMore = false
      }
    },
    switchTab(tab) {
      this.activeTab = tab
      if (tab === 'posts' && !this.postsLoaded) {
        this.loadPosts().then(() => this.$nextTick(() => this.setupPostsScroll()))
      }
    },
    loadMoreScraps() {
      if (this.scrapsLoadingMore || this.scrapsLoading) return
      if (this.scrapsTotal !== null && this.scraps.length >= this.scrapsTotal) return
      this.loadScraps({ append: true })
    },
    loadMorePosts() {
      if (this.postsLoadingMore || this.postsLoading) return
      if (this.postsTotal !== null && this.posts.length >= this.postsTotal) return
      this.loadPosts({ append: true })
    },
    setupScrapsScroll() {
      const anchor = this.$refs.scrapsAnchor
      if (!anchor || this.scrapsObserver) return
      this.scrapsObserver = new IntersectionObserver(
        (entries) => { if (entries[0].isIntersecting) this.loadMoreScraps() },
        { rootMargin: '300px' },
      )
      this.scrapsObserver.observe(anchor)
    },
    setupPostsScroll() {
      const anchor = this.$refs.postsAnchor
      if (!anchor || this.postsObserver) return
      this.postsObserver = new IntersectionObserver(
        (entries) => { if (entries[0].isIntersecting) this.loadMorePosts() },
        { rootMargin: '300px' },
      )
      this.postsObserver.observe(anchor)
    },
    async handleToggleLike(quoteId) {
      if (!requireLogin(this.$router, this.$route.fullPath)) return
      try {
        const { likedIds, likeCount } = await toggleLikeRequest(api, this.likedIds, quoteId)
        this.likedIds = likedIds
        this.updateQuoteCount(quoteId, 'like_count', likeCount)
      } catch {}
    },
    async handleToggleScrap(quoteId) {
      if (!requireLogin(this.$router, this.$route.fullPath)) return
      try {
        const { scrappedIds, scrapCount } = await toggleScrapRequest(api, this.scrappedIds, quoteId)
        this.scrappedIds = scrappedIds
        this.updateQuoteCount(quoteId, 'scrap_count', scrapCount)
      } catch {}
    },
    updateQuoteCount(quoteId, field, value) {
      const updateList = (list) => {
        const idx = list.findIndex(q => q.id === quoteId)
        if (idx !== -1) list.splice(idx, 1, { ...list[idx], [field]: value })
      }
      updateList(this.scraps)
      updateList(this.posts)
    },
  },
}
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  padding: 0 4px 8px;
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  color: var(--glt-ink-secondary);
  cursor: pointer;
  border-radius: 10px;
  transition: background var(--glt-duration), color var(--glt-duration);
}

.back-btn:hover {
  background: var(--glt-bg-subtle);
  color: var(--glt-ink);
}

.profile-hero {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 4px 20px;
}

.profile-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--glt-accent-soft) 0%, rgba(74, 142, 132, 0.2) 100%);
  display: grid;
  place-items: center;
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--glt-accent-hover);
  flex-shrink: 0;
}

.profile-name {
  margin: 0;
  font-size: 1.12rem;
  font-weight: 700;
  color: var(--glt-ink);
}

.profile-tabs {
  display: flex;
  gap: 0;
  border-bottom: 1px solid var(--glt-glass-border);
  margin-bottom: var(--glt-space-4);
}

.tab-btn {
  flex: 1;
  padding: 10px 12px;
  border: none;
  background: transparent;
  font-size: 0.88rem;
  font-weight: 500;
  color: var(--glt-ink-tertiary);
  cursor: pointer;
  position: relative;
  transition: color var(--glt-duration);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.tab-btn.active {
  color: var(--glt-ink);
  font-weight: 700;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 16%;
  right: 16%;
  height: 2px;
  background: var(--glt-accent);
  border-radius: 999px;
}

.tab-count {
  font-size: 0.76rem;
  font-weight: 400;
  color: var(--glt-ink-tertiary);
}

.mini-shelf {
  margin-bottom: var(--glt-space-5);
}

.shelf-head {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-bottom: var(--glt-space-3);
}

.shelf-title {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--glt-ink);
}

.shelf-count {
  font-size: 0.76rem;
  color: var(--glt-ink-tertiary);
}

.shelf-scroll {
  display: flex;
  gap: 14px;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 4px 2px 12px;
  scrollbar-width: none;
  scroll-snap-type: x proximity;
  -webkit-overflow-scrolling: touch;
  touch-action: pan-x;
  overscroll-behavior-x: contain;
  user-select: none;
}

.shelf-scroll::-webkit-scrollbar { display: none; }

.shelf-book {
  flex: 0 0 86px;
  width: 86px;
  display: flex;
  flex-direction: column;
  gap: 5px;
  text-decoration: none;
  color: inherit;
  scroll-snap-align: start;
}

.shelf-cover {
  width: 86px;
  height: 118px;
  object-fit: cover;
  border-radius: 6px;
  box-shadow: var(--glt-shadow-sm);
  display: block;
  transition: transform 0.2s var(--glt-ease);
}

.shelf-book:hover .shelf-cover { transform: translateY(-2px); }

.shelf-cover--empty {
  display: grid;
  place-items: center;
  background: var(--glt-bg-subtle);
  font-size: 1.3rem;
}

.shelf-book-title {
  margin: 0;
  font-size: 0.74rem;
  font-weight: 600;
  color: var(--glt-ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.shelf-book-author {
  margin: 0;
  font-size: 0.68rem;
  color: var(--glt-ink-tertiary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.quote-feed {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.scroll-anchor {
  display: flex;
  justify-content: center;
  padding: 16px 0 8px;
  min-height: 40px;
}

.page-state {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 48px 16px;
  font-size: 0.88rem;
  color: var(--glt-ink-tertiary);
}

.loading-spinner {
  display: block;
  width: 22px;
  height: 22px;
  border: 2px solid var(--glt-glass-border);
  border-top-color: var(--glt-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
