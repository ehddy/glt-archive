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
    <!-- Own profile header -->
    <div v-if="isOwnProfile && loggedIn" class="own-profile-header">
      <div class="profile-hero">
        <div class="profile-avatar">{{ avatarLetter }}</div>
        <span class="profile-name">{{ displayName }}</span>
      </div>
      <button type="button" class="logout-btn" @click="logout">로그아웃</button>
    </div>

    <!-- Login prompt -->
    <div v-if="isOwnProfile && !loggedIn" class="login-panel glt-card">
      <p class="login-text">로그인하면 문장을 스크랩하고 다시 볼 수 있어요</p>
      <div class="login-actions">
        <router-link :to="{ name: 'login', query: { redirect: '/saved' } }" class="glt-btn glt-btn-primary">로그인</router-link>
        <router-link :to="{ name: 'signup', query: { redirect: '/saved' } }" class="glt-btn glt-btn-ghost">회원가입</router-link>
      </div>
    </div>

    <template v-else-if="!initialLoading">
      <!-- Unified bookshelf (above tabs) -->
      <section v-if="allBooks.length" class="my-bookshelf">
        <header class="shelf-head">
          <div class="shelf-head-left">
            <h2 class="shelf-title">{{ isOwnProfile ? '내 책장' : `${displayName}님의 책장` }}</h2>
            <span class="shelf-count">{{ allBooks.length }}권</span>
          </div>
          <router-link v-if="isOwnProfile" to="/my-library" class="shelf-more">
            더보기
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M9 6l6 6-6 6" />
            </svg>
          </router-link>
        </header>
        <div class="shelf-scroll">
          <router-link v-for="book in allBooks" :key="book.id" :to="`/novels/${book.id}`" class="shelf-book">
            <div class="shelf-cover-wrap">
              <img v-if="book.cover_url" :src="book.cover_url" :alt="book.title" class="shelf-cover" />
              <div v-else class="shelf-cover shelf-cover--empty">📖</div>
              <span v-if="book.featured" class="shelf-star" aria-label="대표 책">★</span>
            </div>
            <p class="shelf-book-title">{{ book.title }}</p>
            <p v-if="book.authorName" class="shelf-book-author">{{ book.authorName }}</p>
          </router-link>
        </div>
      </section>

      <!-- Tabs -->
      <div class="tabs">
        <button class="tab-btn" :class="{ active: tab === 'scraps' }" @click="tab = 'scraps'">
          컬렉션<span v-if="scrapsTotal" class="tab-count">{{ scrapsTotal }}</span>
        </button>
        <button class="tab-btn" :class="{ active: tab === 'posts' }" @click="switchToPostsTab">
          포스트<span v-if="postsTotal" class="tab-count">{{ postsTotal }}</span>
        </button>
      </div>

      <!-- Scraps tab -->
      <template v-if="tab === 'scraps'">
        <div v-if="scrapsError" class="glt-empty">{{ scrapsError }}</div>
        <div v-else-if="!scraps.length && !scrapsLoading" class="section-empty">아직 스크랩한 문장이 없어요</div>
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

      <!-- Posts tab -->
      <template v-else>
        <div v-if="postsLoading" class="section-empty"><span class="loading-spinner" /></div>
        <div v-else-if="postsError" class="glt-empty">{{ postsError }}</div>
        <div v-else-if="!posts.length" class="section-empty">아직 포스팅한 문장이 없어요</div>
        <div v-else class="quote-feed">
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
import SavedQuoteList from '../components/SavedQuoteList.vue'
import { authState, clearSession, isLoggedIn, requireLogin } from '../utils/auth'
import { toggleLike as toggleLikeRequest } from '../utils/likeToggle'
import { toggleScrap as toggleScrapRequest } from '../utils/scrapToggle'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'

export default {
  name: 'UserProfileView',
  components: { SavedQuoteList, QuoteFeedItem },
  data() {
    return {
      userName: '',
      tab: 'scraps',
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
      ownBooks: [],
      postBooks: [],
      featuredIds: [],
      initialLoading: true,
      likedIds: new Set(),
      scrappedIds: new Set(),
      pageSize: 20,
    }
  },
  computed: {
    isOwnProfile() { return !this.$route.params.id },
    loggedIn() { return isLoggedIn() },
    userId() {
      return this.$route.params.id ? Number(this.$route.params.id) : authState.user?.id
    },
    displayName() {
      if (this.isOwnProfile) return authState.user?.name || authState.user?.email?.split('@')[0] || ''
      return this.userName || `사용자 ${this.userId}`
    },
    avatarLetter() { return (this.displayName || '?')[0].toUpperCase() },
    scrapsBooks() {
      if (this.isOwnProfile) return this.ownBooks
      const seen = new Set()
      const result = []
      for (const q of this.scraps) {
        const id = q.novel?.id || q.source?.novel_id
        if (!id || seen.has(id)) continue
        seen.add(id)
        result.push({ id, title: q.novel?.title || q.source?.title || '', cover_url: q.novel?.cover_url || q.source?.cover_url || null, authorName: q.novel?.author?.name || q.source?.author?.name || null })
      }
      return result
    },
    allBooks() {
      const normalize = b => ({ id: b.id, title: b.title, cover_url: b.cover_url, authorName: b.authorName || b.author?.name || null })
      const pool = [...this.scrapsBooks, ...this.postBooks].map(normalize)
      const seen = new Set()
      const result = []
      for (const id of this.featuredIds) {
        const book = pool.find(b => b.id === id)
        if (book && !seen.has(id)) { seen.add(id); result.push({ ...book, featured: true }) }
      }
      for (const book of pool) {
        if (!seen.has(book.id)) { seen.add(book.id); result.push({ ...book, featured: false }) }
      }
      return result
    },
  },
  watch: {
    '$route.fullPath': { immediate: true, handler() { this.init() } },
    scrapsLoading(newVal, oldVal) { if (oldVal && !newVal) this.$nextTick(() => this.setupScrapsScroll()) },
    postsLoading(newVal, oldVal) { if (oldVal && !newVal) this.$nextTick(() => this.setupPostsScroll()) },
  },
  beforeUnmount() {
    if (this.scrapsObserver) this.scrapsObserver.disconnect()
    if (this.postsObserver) this.postsObserver.disconnect()
  },
  methods: {
    async init() {
      if (!this.isOwnProfile && authState.user?.id && Number(this.$route.params.id) === authState.user.id) {
        this.$router.replace({ name: 'saved' })
        return
      }
      if (this.scrapsObserver) { this.scrapsObserver.disconnect(); this.scrapsObserver = null }
      if (this.postsObserver) { this.postsObserver.disconnect(); this.postsObserver = null }
      this.scraps = []
      this.posts = []
      this.ownBooks = []
      this.postBooks = []
      this.featuredIds = []
      this.scrapsTotal = null
      this.postsTotal = null
      this.postsLoaded = false
      this.tab = 'scraps'
      this.initialLoading = true

      if (this.isOwnProfile && !this.loggedIn) { this.initialLoading = false; return }

      const tasks = [this.loadScraps(), this.loadPostBooks()]
      if (!this.isOwnProfile) tasks.push(this.loadUser())
      if (this.isOwnProfile) tasks.push(this.loadOwnBooks(), this.loadUserState())
      await Promise.all([...tasks, this.loadFeaturedIds()])
      this.initialLoading = false
    },
    async loadFeaturedIds() {
      if (!this.userId) return
      try {
        const res = await api.getFeaturedNovels(this.userId)
        this.featuredIds = res.novel_ids || []
      } catch { this.featuredIds = [] }
    },
    async loadUser() {
      try { const u = await api.getUser(this.userId); this.userName = u.name || '' } catch {}
    },
    async loadOwnBooks() {
      try { this.ownBooks = await api.listScrappedNovels() } catch {}
    },
    async loadPostBooks() {
      if (!this.userId) return
      try { this.postBooks = await api.getUserNovels(this.userId) } catch {}
    },
    async loadUserState() {
      if (!isLoggedIn()) return
      try {
        const [l, s] = await Promise.all([
          api.getLikeIds().catch(() => ({ quote_ids: [] })),
          api.getScrapIds().catch(() => ({ quote_ids: [] })),
        ])
        this.likedIds = new Set(l.quote_ids || [])
        this.scrappedIds = new Set(s.quote_ids || [])
      } catch {}
    },
    async loadScraps({ append = false } = {}) {
      if (!this.userId) return
      if (append) { this.scrapsLoadingMore = true }
      else { this.scrapsLoading = true; this.scraps = []; startPageLoading() }
      this.scrapsError = ''
      try {
        const res = await api.getUserScraps(this.userId, { skip: append ? this.scraps.length : 0, limit: this.pageSize })
        this.scrapsTotal = res.total
        this.scraps = append ? [...this.scraps, ...res.items] : res.items
      } catch (e) { this.scrapsError = e.message }
      finally { if (!append) { this.scrapsLoading = false; endPageLoading() }; this.scrapsLoadingMore = false }
    },
    async loadPosts({ append = false } = {}) {
      if (!this.userId) return
      if (append) { this.postsLoadingMore = true }
      else { this.postsLoading = true; this.posts = [] }
      this.postsError = ''
      try {
        const res = await api.getUserQuotes(this.userId, { skip: append ? this.posts.length : 0, limit: this.pageSize })
        this.postsTotal = res.total
        this.posts = append ? [...this.posts, ...res.items] : res.items
        this.postsLoaded = true
      } catch (e) { this.postsError = e.message }
      finally { this.postsLoading = false; this.postsLoadingMore = false }
    },
    switchToPostsTab() {
      this.tab = 'posts'
      if (!this.postsLoaded) this.loadPosts().then(() => this.$nextTick(() => this.setupPostsScroll()))
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
    async handleRemove(quoteId) {
      try {
        await api.removeScrap(quoteId)
        this.scraps = this.scraps.filter(q => q.id !== quoteId)
        if (this.scrapsTotal !== null) this.scrapsTotal--
        this.ownBooks = await api.listScrappedNovels()
      } catch {}
    },
    async handleToggleLike(quoteId) {
      if (!requireLogin(this.$router, this.$route.fullPath)) return
      try {
        const { likedIds, likeCount } = await toggleLikeRequest(api, this.likedIds, quoteId)
        this.likedIds = likedIds
        const idx = this.posts.findIndex(q => q.id === quoteId)
        if (idx !== -1) this.posts.splice(idx, 1, { ...this.posts[idx], like_count: likeCount })
      } catch {}
    },
    async handleToggleScrap(quoteId) {
      if (!requireLogin(this.$router, this.$route.fullPath)) return
      try {
        const { scrappedIds, scrapCount } = await toggleScrapRequest(api, this.scrappedIds, quoteId)
        this.scrappedIds = scrappedIds
        const idx = this.posts.findIndex(q => q.id === quoteId)
        if (idx !== -1) this.posts.splice(idx, 1, { ...this.posts[idx], scrap_count: scrapCount })
      } catch {}
    },
    logout() {
      clearSession()
      this.$router.push('/')
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

.back-btn:hover { background: var(--glt-bg-subtle); color: var(--glt-ink); }

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

.own-profile-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 4px 0 16px;
}

.own-profile-header .profile-avatar {
  width: 44px;
  height: 44px;
  font-size: 1.15rem;
}

.own-profile-header .profile-name {
  font-size: 1.05rem;
}

.logout-btn {
  flex-shrink: 0;
  border: 1px solid var(--glt-glass-border);
  background: transparent;
  color: var(--glt-ink-tertiary);
  font-size: 0.78rem;
  padding: 5px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: color var(--glt-duration), border-color var(--glt-duration);
}

.logout-btn:hover {
  color: var(--glt-ink);
  border-color: var(--glt-ink-tertiary);
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

.shelf-cover-wrap {
  position: relative;
  width: 90px;
  height: 124px;
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

.shelf-book:hover .shelf-cover { transform: translateY(-2px); box-shadow: var(--glt-shadow-md); }

.shelf-cover--empty {
  display: grid;
  place-items: center;
  background: var(--glt-bg-subtle);
  font-size: 1.4rem;
  border-radius: 6px;
}

.shelf-star {
  position: absolute;
  top: 5px;
  right: 5px;
  font-size: 0.9rem;
  color: #f5c842;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
  line-height: 1;
  pointer-events: none;
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

.tabs {
  display: flex;
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
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  transition: color var(--glt-duration);
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

.section-empty {
  padding: var(--glt-space-8) 0;
  text-align: center;
  font-size: 0.86rem;
  color: var(--glt-ink-tertiary);
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

.loading-spinner {
  display: block;
  width: 22px;
  height: 22px;
  border: 2px solid var(--glt-glass-border);
  border-top-color: var(--glt-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
