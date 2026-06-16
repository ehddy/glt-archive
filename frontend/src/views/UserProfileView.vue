<template>
  <section class="scraps-view glt-container">
    <!-- Other user profile header -->
    <div v-if="!isOwnProfile" class="profile-header">
      <button type="button" class="back-btn" @click="$router.back()" aria-label="뒤로">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M15 6l-6 6 6 6" /></svg>
      </button>
      <div class="profile-avatar-wrap">
        <div class="profile-avatar-circle">
          <img v-if="currentAvatarUrl" :src="currentAvatarUrl" class="profile-avatar-img" :alt="displayName" />
          <span v-else class="profile-avatar-letter">{{ avatarLetter }}</span>
        </div>
      </div>
      <div class="profile-info">
        <p class="profile-name">{{ displayName }}</p>
      </div>
    </div>

    <!-- Own profile header -->
    <div v-if="isOwnProfile && loggedIn" class="profile-header profile-header--own">
      <div class="profile-avatar-wrap" @click="triggerAvatarUpload">
        <div class="profile-avatar-circle" :class="{ 'profile-avatar-circle--uploading': avatarUploading }">
          <img v-if="currentAvatarUrl && !avatarUploading" :src="currentAvatarUrl" class="profile-avatar-img" :alt="displayName" />
          <span v-else-if="!avatarUploading" class="profile-avatar-letter">{{ avatarLetter }}</span>
          <span v-else class="profile-avatar-spinner" />
        </div>
        <div class="profile-avatar-edit" aria-label="프로필 사진 변경">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
            <circle cx="12" cy="13" r="4"/>
          </svg>
        </div>
        <input ref="avatarInput" type="file" accept="image/*" class="avatar-file-input" @change="handleAvatarChange" />
      </div>
      <div class="profile-info">
        <p class="profile-name">{{ displayName }}</p>
        <p class="profile-sub">{{ authState.user?.email || '' }}</p>
      </div>
      <button type="button" class="logout-btn" @click="logout">로그아웃</button>
    </div>

    <!-- Avatar crop modal -->
    <Teleport to="body">
      <div v-if="cropSrc" class="crop-overlay" @click.self="cancelCrop">
        <div class="crop-modal">
          <p class="crop-modal-title">프로필 사진 조정</p>
          <div
            class="crop-viewport"
            ref="cropViewport"
            @mousedown.prevent="onCropMouseDown"
            @mousemove.prevent="onCropMouseMove"
            @mouseup="onCropMouseUp"
            @mouseleave="onCropMouseUp"
            @wheel.prevent="onCropWheel"
            @touchstart.prevent="onCropTouchStart"
            @touchmove.prevent="onCropTouchMove"
            @touchend="onCropTouchEnd"
          >
            <img
              ref="cropImg"
              :src="cropSrc"
              class="crop-img"
              :style="cropImgStyle"
              draggable="false"
              @load="onCropImageLoad"
            />
          </div>
          <p class="crop-hint">드래그로 위치 조정 · 핀치로 확대/축소</p>
          <div class="crop-actions">
            <button type="button" class="glt-btn glt-btn-ghost" @click="cancelCrop">취소</button>
            <button type="button" class="glt-btn glt-btn-primary" :disabled="avatarUploading" @click="confirmCrop">
              <span v-if="avatarUploading" class="btn-spinner" />
              <span v-else>저장</span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Login prompt -->
    <div v-if="isOwnProfile && !loggedIn" class="login-panel glt-card">
      <p class="login-title">로그인하면 나만의 공간이 생겨요</p>
      <p class="login-desc">마음에 드는 문장을 담고, 내 책장을 채워보세요</p>
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
import BackLink from '../components/BackLink.vue'
import QuoteFeedItem from '../components/QuoteFeedItem.vue'
import SavedQuoteList from '../components/SavedQuoteList.vue'
import { authState, clearSession, isLoggedIn, requireLogin } from '../utils/auth'
import { toggleLike as toggleLikeRequest } from '../utils/likeToggle'
import { toggleScrap as toggleScrapRequest } from '../utils/scrapToggle'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'

export default {
  name: 'UserProfileView',
  components: { BackLink, SavedQuoteList, QuoteFeedItem },
  data() {
    return {
      userName: '',
      userAvatarUrl: '',
      avatarUploading: false,
      cropSrc: null,
      cropImageNW: 0,
      cropImageNH: 0,
      cropX: 0,
      cropY: 0,
      cropScale: 1,
      cropDragging: false,
      cropDragStartX: 0,
      cropDragStartY: 0,
      cropDragOriginX: 0,
      cropDragOriginY: 0,
      pinchDist: null,
      pinchScaleStart: 1,
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
    currentAvatarUrl() {
      if (this.isOwnProfile) return authState.user?.avatar_url || ''
      return this.userAvatarUrl
    },
    authState() { return authState },
    cropImgStyle() {
      return {
        position: 'absolute',
        left: '0',
        top: '0',
        transformOrigin: '0 0',
        transform: `translate(${this.cropX}px, ${this.cropY}px) scale(${this.cropScale})`,
        userSelect: 'none',
        pointerEvents: 'none',
        maxWidth: 'none',
      }
    },
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

      startPageLoading()
      try {
        const tasks = [this.loadScraps(), this.loadPostBooks()]
        if (!this.isOwnProfile) tasks.push(this.loadUser())
        if (this.isOwnProfile) tasks.push(this.loadOwnBooks(), this.loadUserState())
        await Promise.all([...tasks, this.loadFeaturedIds()])
      } finally {
        this.initialLoading = false
        endPageLoading()
      }
    },
    async loadFeaturedIds() {
      if (!this.userId) return
      try {
        const res = await api.getFeaturedNovels(this.userId)
        this.featuredIds = res.novel_ids || []
      } catch { this.featuredIds = [] }
    },
    async loadUser() {
      try {
        const u = await api.getUser(this.userId)
        this.userName = u.name || ''
        this.userAvatarUrl = u.avatar_url || ''
      } catch {}
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
      else { this.scrapsLoading = true; this.scraps = [] }
      this.scrapsError = ''
      try {
        const res = await api.getUserScraps(this.userId, { skip: append ? this.scraps.length : 0, limit: this.pageSize })
        this.scrapsTotal = res.total
        this.scraps = append ? [...this.scraps, ...res.items] : res.items
      } catch (e) { this.scrapsError = e.message }
      finally { if (!append) { this.scrapsLoading = false }; this.scrapsLoadingMore = false }
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
    triggerAvatarUpload() {
      this.$refs.avatarInput?.click()
    },
    async handleAvatarChange(e) {
      const file = e.target.files?.[0]
      if (!file || !file.type.startsWith('image/')) return
      e.target.value = ''
      this.openCropModal(file)
    },
    openCropModal(file) {
      if (this.cropSrc) URL.revokeObjectURL(this.cropSrc)
      this.cropSrc = URL.createObjectURL(file)
      this.cropX = 0
      this.cropY = 0
      this.cropScale = 1
      this.cropImageNW = 0
      this.cropImageNH = 0
    },
    onCropImageLoad() {
      const img = this.$refs.cropImg
      if (!img) return
      const VP = 280
      this.cropImageNW = img.naturalWidth
      this.cropImageNH = img.naturalHeight
      const minDim = Math.min(img.naturalWidth, img.naturalHeight)
      this.cropScale = VP / minDim
      const imgW = img.naturalWidth * this.cropScale
      const imgH = img.naturalHeight * this.cropScale
      this.cropX = (VP - imgW) / 2
      this.cropY = (VP - imgH) / 2
    },
    _clampCrop() {
      const VP = 280
      const imgW = this.cropImageNW * this.cropScale
      const imgH = this.cropImageNH * this.cropScale
      this.cropX = Math.min(0, Math.max(VP - imgW, this.cropX))
      this.cropY = Math.min(0, Math.max(VP - imgH, this.cropY))
    },
    onCropMouseDown(e) {
      this.cropDragging = true
      this.cropDragStartX = e.clientX
      this.cropDragStartY = e.clientY
      this.cropDragOriginX = this.cropX
      this.cropDragOriginY = this.cropY
    },
    onCropMouseMove(e) {
      if (!this.cropDragging) return
      this.cropX = this.cropDragOriginX + (e.clientX - this.cropDragStartX)
      this.cropY = this.cropDragOriginY + (e.clientY - this.cropDragStartY)
      this._clampCrop()
    },
    onCropMouseUp() { this.cropDragging = false },
    onCropWheel(e) {
      const VP = 280
      const center = VP / 2
      const factor = e.deltaY < 0 ? 1.12 : 0.88
      const minScale = VP / Math.min(this.cropImageNW, this.cropImageNH)
      const newScale = Math.max(minScale, Math.min(6, this.cropScale * factor))
      const sf = newScale / this.cropScale
      this.cropX = center + (this.cropX - center) * sf
      this.cropY = center + (this.cropY - center) * sf
      this.cropScale = newScale
      this._clampCrop()
    },
    onCropTouchStart(e) {
      if (e.touches.length === 1) {
        this.cropDragging = true
        this.cropDragStartX = e.touches[0].clientX
        this.cropDragStartY = e.touches[0].clientY
        this.cropDragOriginX = this.cropX
        this.cropDragOriginY = this.cropY
        this.pinchDist = null
      } else if (e.touches.length === 2) {
        this.cropDragging = false
        this.pinchDist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY,
        )
        this.pinchScaleStart = this.cropScale
      }
    },
    onCropTouchMove(e) {
      if (e.touches.length === 1 && this.cropDragging) {
        this.cropX = this.cropDragOriginX + (e.touches[0].clientX - this.cropDragStartX)
        this.cropY = this.cropDragOriginY + (e.touches[0].clientY - this.cropDragStartY)
        this._clampCrop()
      } else if (e.touches.length === 2 && this.pinchDist) {
        const VP = 280
        const center = VP / 2
        const dist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY,
        )
        const minScale = VP / Math.min(this.cropImageNW, this.cropImageNH)
        const newScale = Math.max(minScale, Math.min(6, this.pinchScaleStart * (dist / this.pinchDist)))
        const sf = newScale / this.cropScale
        this.cropX = center + (this.cropX - center) * sf
        this.cropY = center + (this.cropY - center) * sf
        this.cropScale = newScale
        this._clampCrop()
      }
    },
    onCropTouchEnd() { this.cropDragging = false; this.pinchDist = null },
    cancelCrop() {
      if (this.cropSrc) { URL.revokeObjectURL(this.cropSrc); this.cropSrc = null }
    },
    async confirmCrop() {
      const img = this.$refs.cropImg
      if (!img || !this.cropImageNW) return
      const VP = 280
      const OUTPUT = 480
      const center = VP / 2
      const imgCenterX = (center - this.cropX) / this.cropScale
      const imgCenterY = (center - this.cropY) / this.cropScale
      const half = (VP / 2) / this.cropScale
      const sx = imgCenterX - half
      const sy = imgCenterY - half
      const sw = VP / this.cropScale

      const canvas = document.createElement('canvas')
      canvas.width = OUTPUT
      canvas.height = OUTPUT
      canvas.getContext('2d').drawImage(img, sx, sy, sw, sw, 0, 0, OUTPUT, OUTPUT)

      canvas.toBlob(async (blob) => {
        URL.revokeObjectURL(this.cropSrc)
        this.cropSrc = null
        this.avatarUploading = true
        try {
          const res = await api.updateAvatar(this.userId, blob)
          if (authState.user) authState.user.avatar_url = res.avatar_url + '?v=' + Date.now()
        } catch {}
        finally { this.avatarUploading = false }
      }, 'image/jpeg', 0.85)
    },
    logout() {
      clearSession()
      this.$router.push('/')
    },
  },
}

</script>

<style scoped>
/* 공통 프로필 헤더 */
.profile-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 4px 0 20px;
}

.profile-header--own {
  padding-bottom: 20px;
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--glt-ink-tertiary);
  cursor: pointer;
  border-radius: 8px;
  flex-shrink: 0;
  transition: color var(--glt-duration);
}

.back-btn:hover { color: var(--glt-ink); }

/* 아바타 */
.profile-avatar-wrap {
  position: relative;
  flex-shrink: 0;
  cursor: pointer;
}

.profile-header:not(.profile-header--own) .profile-avatar-wrap {
  cursor: default;
}

.profile-avatar-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--glt-accent-soft) 0%, rgba(74, 142, 132, 0.2) 100%);
  border: 2px solid var(--glt-glass-border);
  display: grid;
  place-items: center;
  overflow: hidden;
  transition: opacity 0.15s;
}

.profile-header--own .profile-avatar-wrap:hover .profile-avatar-circle {
  opacity: 0.85;
}

.profile-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.profile-avatar-letter {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--glt-accent-hover);
  line-height: 1;
}

.profile-avatar-spinner {
  display: block;
  width: 22px;
  height: 22px;
  border: 2px solid var(--glt-glass-border);
  border-top-color: var(--glt-accent);
  border-radius: 50%;
  animation: spin 0.75s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.profile-avatar-edit {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--glt-surface);
  border: 1.5px solid var(--glt-glass-border);
  display: grid;
  place-items: center;
  color: var(--glt-ink-secondary);
  pointer-events: none;
}

.avatar-file-input {
  display: none;
}

/* 프로필 정보 */
.profile-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.profile-name {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--glt-ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.profile-sub {
  margin: 0;
  font-size: 0.72rem;
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
  font-size: 0.75rem;
  padding: 5px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: color var(--glt-duration), border-color var(--glt-duration);
  align-self: flex-start;
}

.logout-btn:hover {
  color: var(--glt-ink);
  border-color: var(--glt-ink-tertiary);
}

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

.my-bookshelf {
  margin-bottom: var(--glt-space-3);
}

.shelf-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--glt-space-3);
  margin-bottom: var(--glt-space-2);
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
  padding: 4px 2px 6px;
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

/* ── Crop modal ─────────────────────────────────────── */
.crop-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.72);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 16px;
}

.crop-modal {
  background: var(--glt-surface);
  border-radius: 18px;
  padding: 22px 20px 18px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  width: 100%;
  max-width: 330px;
}

.crop-modal-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--glt-ink);
  align-self: flex-start;
}

.crop-viewport {
  width: 280px;
  height: 280px;
  border-radius: 50%;
  overflow: hidden;
  position: relative;
  cursor: grab;
  user-select: none;
  -webkit-user-select: none;
  touch-action: none;
  background: var(--glt-bg-subtle);
  box-shadow: 0 0 0 3px var(--glt-glass-border), 0 4px 24px rgba(0,0,0,0.18);
  flex-shrink: 0;
}

.crop-viewport:active { cursor: grabbing; }

.crop-img {
  position: absolute;
  top: 0;
  left: 0;
  transform-origin: 0 0;
  user-select: none;
  -webkit-user-select: none;
  pointer-events: none;
  max-width: none;
  display: block;
}

.crop-hint {
  margin: 0;
  font-size: 0.76rem;
  color: var(--glt-ink-tertiary);
  text-align: center;
}

.crop-actions {
  display: flex;
  gap: 10px;
  width: 100%;
}

.crop-actions .glt-btn { flex: 1; }

.btn-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  vertical-align: middle;
}
</style>
