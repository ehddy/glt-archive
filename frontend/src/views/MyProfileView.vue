<template>
  <section class="my-profile glt-container">
    <h1 class="glt-title">프로필</h1>

    <div v-if="!loggedIn" class="login-panel glt-card">
      <p class="login-text">로그인하면 내 프로필을 볼 수 있어요</p>
      <div class="login-actions">
        <router-link :to="{ name: 'login', query: { redirect: '/my-profile' } }" class="glt-btn glt-btn-primary">
          로그인
        </router-link>
        <router-link :to="{ name: 'signup', query: { redirect: '/my-profile' } }" class="glt-btn glt-btn-ghost">
          회원가입
        </router-link>
      </div>
    </div>

    <template v-else>
      <!-- Profile hero -->
      <div class="profile-hero">
        <div class="profile-avatar">{{ avatarLetter }}</div>
        <div class="profile-body">
          <h2 class="profile-name">{{ userName }}</h2>
          <p class="profile-email">{{ userEmail }}</p>
        </div>
        <button type="button" class="logout-btn" @click="logout">로그아웃</button>
      </div>

      <!-- Stats -->
      <div class="profile-stats">
        <div class="stat-item">
          <span class="stat-num">{{ postsTotal !== null ? postsTotal : '—' }}</span>
          <span class="stat-label">등록</span>
        </div>
      </div>

      <!-- Posts feed -->
      <div class="section-label">등록한 문장</div>

      <div v-if="loading" class="page-state">
        <span class="loading-spinner" />
      </div>
      <div v-else-if="error" class="page-state">{{ error }}</div>
      <div v-else-if="!posts.length" class="page-state glt-empty glt-card">아직 등록한 문장이 없어요</div>
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
        <div ref="scrollAnchor" class="scroll-anchor">
          <span v-if="loadingMore" class="loading-spinner" aria-hidden="true" />
        </div>
      </template>
    </template>
  </section>
</template>

<script>
import { api } from '../api'
import QuoteFeedItem from '../components/QuoteFeedItem.vue'
import { authState, clearSession, isLoggedIn, requireLogin } from '../utils/auth'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'
import { toggleLike as toggleLikeRequest } from '../utils/likeToggle'
import { toggleScrap as toggleScrapRequest } from '../utils/scrapToggle'

export default {
  name: 'MyProfileView',
  components: { QuoteFeedItem },
  data() {
    return {
      posts: [],
      postsTotal: null,
      loading: false,
      loadingMore: false,
      error: '',
      likedIds: new Set(),
      scrappedIds: new Set(),
      observer: null,
      pageSize: 20,
    }
  },
  computed: {
    loggedIn() {
      return isLoggedIn()
    },
    userName() {
      return authState.user?.name || authState.user?.email?.split('@')[0] || ''
    },
    userEmail() {
      return authState.user?.email || ''
    },
    avatarLetter() {
      return (this.userName || '?')[0].toUpperCase()
    },
  },
  mounted() {
    if (this.loggedIn) this.init()
  },
  beforeUnmount() {
    if (this.observer) this.observer.disconnect()
  },
  methods: {
    async init() {
      await Promise.all([this.loadPosts(), this.loadUserState()])
    },
    async loadUserState() {
      try {
        const [likedRes, scrappedRes] = await Promise.all([
          api.getLikeIds().catch(() => ({ quote_ids: [] })),
          api.getScrapIds().catch(() => ({ quote_ids: [] })),
        ])
        this.likedIds = new Set(likedRes.quote_ids || [])
        this.scrappedIds = new Set(scrappedRes.quote_ids || [])
      } catch {}
    },
    async loadPosts({ append = false } = {}) {
      if (!authState.user?.id) return
      if (append) {
        this.loadingMore = true
      } else {
        this.loading = true
        this.posts = []
        startPageLoading()
      }
      this.error = ''
      try {
        const res = await api.getUserQuotes(authState.user.id, {
          skip: append ? this.posts.length : 0,
          limit: this.pageSize,
        })
        this.postsTotal = res.total
        this.posts = append ? [...this.posts, ...res.items] : res.items
        if (!append) this.$nextTick(this.setupScroll)
      } catch (e) {
        this.error = e.message
      } finally {
        if (!append) { this.loading = false; endPageLoading() }
        this.loadingMore = false
      }
    },
    loadMore() {
      if (this.loadingMore || this.loading) return
      if (this.postsTotal !== null && this.posts.length >= this.postsTotal) return
      this.loadPosts({ append: true })
    },
    setupScroll() {
      const anchor = this.$refs.scrollAnchor
      if (!anchor || this.observer) return
      this.observer = new IntersectionObserver(
        (entries) => { if (entries[0].isIntersecting) this.loadMore() },
        { rootMargin: '300px' },
      )
      this.observer.observe(anchor)
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
      this.posts = []
      this.$router.push('/')
    },
  },
}
</script>

<style scoped>
.my-profile .glt-title {
  margin-bottom: var(--glt-space-3);
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

.profile-hero {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 4px 0 20px;
}

.profile-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--glt-accent-soft) 0%, rgba(74, 142, 132, 0.2) 100%);
  display: grid;
  place-items: center;
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--glt-accent-hover);
  flex-shrink: 0;
}

.profile-body {
  flex: 1;
  min-width: 0;
}

.profile-name {
  margin: 0 0 2px;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--glt-ink);
}

.profile-email {
  margin: 0;
  font-size: 0.78rem;
  color: var(--glt-ink-tertiary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

.profile-stats {
  display: flex;
  align-items: center;
  gap: 0;
  padding: 12px 16px;
  background: var(--glt-bg-subtle);
  border-radius: 14px;
  margin-bottom: var(--glt-space-5);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 0 12px 0 0;
}

.stat-num {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--glt-ink);
  line-height: 1;
}

.stat-label {
  font-size: 0.74rem;
  color: var(--glt-ink-tertiary);
}

.section-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--glt-ink-tertiary);
  margin-bottom: var(--glt-space-3);
  letter-spacing: 0.02em;
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
