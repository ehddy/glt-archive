<template>
  <!-- Header: only for other user -->
  <header v-if="!isOwnProfile" class="page-header">
    <button type="button" class="back-btn" @click="$router.back()" aria-label="뒤로">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" aria-hidden="true">
        <path d="M15 6l-6 6 6 6" />
      </svg>
    </button>
    <div class="profile-hero">
      <div class="profile-avatar">{{ avatarLetter }}</div>
      <span class="profile-name">{{ displayName }}</span>
    </div>
  </header>

  <section class="scraps-view glt-container">
    <!-- Login prompt (own profile, not logged in) -->
    <div v-if="isOwnProfile && !loggedIn" class="login-panel glt-card">
      <p class="login-text">로그인하면 문장을 스크랩하고 다시 볼 수 있어요</p>
      <div class="login-actions">
        <router-link :to="{ name: 'login', query: { redirect: '/saved' } }" class="glt-btn glt-btn-primary">로그인</router-link>
        <router-link :to="{ name: 'signup', query: { redirect: '/saved' } }" class="glt-btn glt-btn-ghost">회원가입</router-link>
      </div>
    </div>

    <template v-else-if="!initialLoading">
      <!-- Bookshelf -->
      <section v-if="books.length" class="my-bookshelf">
        <header class="shelf-head">
          <div class="shelf-head-left">
            <h2 class="shelf-title">{{ isOwnProfile ? '내 책장' : '책장' }}</h2>
            <span class="shelf-count">{{ books.length }}권</span>
          </div>
          <router-link v-if="isOwnProfile" to="/my-library" class="shelf-more">
            더보기
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M9 6l6 6-6 6" />
            </svg>
          </router-link>
        </header>
        <div class="shelf-scroll">
          <router-link
            v-for="book in books"
            :key="book.id"
            :to="`/novels/${book.id}`"
            class="shelf-book"
          >
            <img v-if="book.cover_url" :src="book.cover_url" :alt="book.title" class="shelf-cover" />
            <div v-else class="shelf-cover shelf-cover--empty">📖</div>
            <p class="shelf-book-title">{{ book.title }}</p>
            <p v-if="book.author?.name || book.authorName" class="shelf-book-author">{{ book.author?.name || book.authorName }}</p>
          </router-link>
        </div>
      </section>

      <!-- Scraps -->
      <div v-if="scrapsError" class="glt-empty">{{ scrapsError }}</div>
      <div v-else-if="!scraps.length && !scrapsLoading" class="glt-empty glt-card">아직 스크랩한 문장이 없어요</div>
      <SavedQuoteList
        v-else-if="scraps.length"
        :quotes="scraps"
        :removable="isOwnProfile"
        @remove="handleRemove"
      />

      <div ref="scrapsAnchor" class="scroll-anchor">
        <span v-if="scrapsLoadingMore" class="loading-spinner" aria-hidden="true" />
      </div>
    </template>
  </section>
</template>

<script>
import { api } from '../api'
import SavedQuoteList from '../components/SavedQuoteList.vue'
import { authState, isLoggedIn } from '../utils/auth'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'

export default {
  name: 'UserProfileView',
  components: { SavedQuoteList },
  data() {
    return {
      userName: '',
      scraps: [],
      scrapsTotal: null,
      scrapsLoading: true,
      scrapsLoadingMore: false,
      scrapsError: '',
      scrapsObserver: null,
      ownBooks: [],
      initialLoading: true,
      pageSize: 20,
    }
  },
  computed: {
    isOwnProfile() {
      return !this.$route.params.id
    },
    loggedIn() {
      return isLoggedIn()
    },
    userId() {
      return this.$route.params.id ? Number(this.$route.params.id) : authState.user?.id
    },
    displayName() {
      if (this.isOwnProfile) return authState.user?.name || authState.user?.email?.split('@')[0] || ''
      return this.userName || `사용자 ${this.userId}`
    },
    avatarLetter() {
      return (this.displayName || '?')[0].toUpperCase()
    },
    books() {
      if (this.isOwnProfile) return this.ownBooks
      const seen = new Set()
      const result = []
      for (const q of this.scraps) {
        const novelId = q.novel?.id || q.source?.novel_id
        if (!novelId || seen.has(novelId)) continue
        seen.add(novelId)
        result.push({
          id: novelId,
          title: q.novel?.title || q.source?.title || '',
          cover_url: q.novel?.cover_url || q.source?.cover_url || null,
          authorName: q.novel?.author?.name || q.source?.author?.name || null,
        })
      }
      return result
    },
  },
  watch: {
    '$route.fullPath': {
      immediate: true,
      handler() { this.init() },
    },
    scrapsLoading(newVal, oldVal) {
      if (oldVal && !newVal) this.$nextTick(() => this.setupScroll())
    },
  },
  beforeUnmount() {
    if (this.scrapsObserver) this.scrapsObserver.disconnect()
  },
  methods: {
    async init() {
      if (this.scrapsObserver) { this.scrapsObserver.disconnect(); this.scrapsObserver = null }
      this.scraps = []
      this.ownBooks = []
      this.scrapsTotal = null
      this.initialLoading = true

      if (this.isOwnProfile && !this.loggedIn) {
        this.initialLoading = false
        return
      }

      const tasks = [this.loadScraps()]
      if (!this.isOwnProfile) tasks.push(this.loadUser())
      if (this.isOwnProfile) tasks.push(this.loadOwnBooks())
      await Promise.all(tasks)
      this.initialLoading = false
    },
    async loadUser() {
      try {
        const user = await api.getUser(this.userId)
        this.userName = user.name || ''
      } catch {}
    },
    async loadOwnBooks() {
      try {
        this.ownBooks = await api.listScrappedNovels()
      } catch {}
    },
    async loadScraps({ append = false } = {}) {
      if (!this.userId) return
      if (append) {
        this.scrapsLoadingMore = true
      } else {
        this.scrapsLoading = true
        this.scraps = []
        if (!append) startPageLoading()
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
    loadMoreScraps() {
      if (this.scrapsLoadingMore || this.scrapsLoading) return
      if (this.scrapsTotal !== null && this.scraps.length >= this.scrapsTotal) return
      this.loadScraps({ append: true })
    },
    setupScroll() {
      const anchor = this.$refs.scrapsAnchor
      if (!anchor || this.scrapsObserver) return
      this.scrapsObserver = new IntersectionObserver(
        (entries) => { if (entries[0].isIntersecting) this.loadMoreScraps() },
        { rootMargin: '300px' },
      )
      this.scrapsObserver.observe(anchor)
    },
    async handleRemove(quoteId) {
      try {
        await api.removeScrap(quoteId)
        this.scraps = this.scraps.filter(q => q.id !== quoteId)
        if (this.scrapsTotal !== null) this.scrapsTotal--
        this.ownBooks = await api.listScrappedNovels()
      } catch {}
    },
  },
}
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 16px 4px;
  background: var(--glt-surface);
  border-bottom: 1px solid var(--glt-glass-border);
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
  flex-shrink: 0;
  transition: background var(--glt-duration), color var(--glt-duration);
}

.back-btn:hover {
  background: var(--glt-bg-subtle);
  color: var(--glt-ink);
}

.profile-hero {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.profile-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--glt-accent-soft) 0%, rgba(74, 142, 132, 0.2) 100%);
  display: grid;
  place-items: center;
  font-size: 1rem;
  font-weight: 700;
  color: var(--glt-accent-hover);
  flex-shrink: 0;
}

.profile-name {
  font-size: 1rem;
  font-weight: 700;
  color: var(--glt-ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.login-panel {
  padding: var(--glt-space-5) var(--glt-space-4);
  text-align: center;
}

.login-text {
  margin: 0 0 var(--glt-space-3);
  color: var(--glt-ink-secondary);
  line-height: 1.6;
}

.login-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.my-bookshelf {
  margin-bottom: var(--glt-space-5);
}

.shelf-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--glt-space-3);
  margin-bottom: var(--glt-space-3);
}

.shelf-head-left {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.shelf-title {
  margin: 0;
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--glt-ink);
}

.shelf-count {
  font-size: 0.78rem;
  color: var(--glt-ink-tertiary);
}

.shelf-more {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--glt-ink-tertiary);
  text-decoration: none;
  flex-shrink: 0;
}

.shelf-more:hover { color: var(--glt-accent-hover); }

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
  -webkit-user-select: none;
}

.shelf-scroll::-webkit-scrollbar { display: none; }

.shelf-book {
  flex: 0 0 90px;
  width: 90px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  text-decoration: none;
  color: inherit;
  scroll-snap-align: start;
}

.shelf-cover {
  width: 90px;
  height: 124px;
  object-fit: cover;
  border-radius: 6px;
  box-shadow: var(--glt-shadow-sm);
  transition: transform 0.2s var(--glt-ease), box-shadow 0.2s var(--glt-ease);
  display: block;
}

.shelf-book:hover .shelf-cover {
  transform: translateY(-2px);
  box-shadow: var(--glt-shadow-md);
}

.shelf-cover--empty {
  display: grid;
  place-items: center;
  background: var(--glt-bg-subtle);
  font-size: 1.4rem;
}

.shelf-book-title {
  margin: 0;
  font-size: 0.76rem;
  font-weight: 600;
  line-height: 1.3;
  color: var(--glt-ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.shelf-book-author {
  margin: 0;
  font-size: 0.7rem;
  color: var(--glt-ink-tertiary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.scroll-anchor {
  display: flex;
  justify-content: center;
  padding: 16px 0 8px;
  min-height: 40px;
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
