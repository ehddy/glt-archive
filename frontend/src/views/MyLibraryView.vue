<template>
  <section class="my-library glt-container">
    <BackLink use-history fallback-to="/saved" label="뒤로" />

    <div v-if="!loggedIn" class="login-panel glt-card">
      <p class="login-text">로그인하면 내 책장을 볼 수 있어요</p>
      <div class="login-actions">
        <router-link :to="{ name: 'login', query: { redirect: $route.fullPath } }" class="glt-btn glt-btn-primary">로그인</router-link>
        <router-link :to="{ name: 'signup', query: { redirect: $route.fullPath } }" class="glt-btn glt-btn-ghost">회원가입</router-link>
      </div>
    </div>

    <template v-else>
      <div v-if="!loading && novels.length" class="library-header">
        <div class="library-header-left">
          <p class="result-count"><span class="result-count-num">{{ novels.length }}</span>권</p>
          <p class="library-hint">별 표시한 3권이 내 책장 맨 앞에 보여요</p>
        </div>
        <span v-if="saving" class="saving-label">저장 중…</span>
        <span v-else-if="savedFlash" class="saving-label saved-flash">저장됨 ✓</span>
      </div>

      <div v-if="error && !loading" class="glt-empty glt-card">{{ error }}</div>

      <div v-else-if="!loading && !novels.length" class="empty-panel glt-card">
        <p class="empty-title">아직 책이 없어요</p>
        <p class="empty-desc">문장을 스크랩하거나 포스팅하면 여기에 책이 쌓여요</p>
        <router-link to="/" class="glt-btn glt-btn-primary">문장 둘러보기</router-link>
      </div>

      <ul v-else-if="!loading" class="novel-grid">
        <li v-for="novel in novels" :key="novel.id">
          <div class="novel-card-wrap">
            <router-link :to="`/novels/${novel.id}`" class="novel-card glt-card">
              <div class="novel-cover-area">
                <img v-if="novel.cover_url" :src="novel.cover_url" :alt="novel.title" class="novel-cover" />
                <div v-else class="novel-cover novel-cover--empty">📖</div>
              </div>
              <div class="novel-meta">
                <strong class="novel-title">{{ novel.title }}</strong>
                <span v-if="novel.author" class="novel-author">{{ novel.author.name }}</span>
              </div>
            </router-link>
            <button
              type="button"
              class="star-btn"
              :class="{ 'star-btn--active': isFeatured(novel.id), 'star-btn--disabled': !isFeatured(novel.id) && featuredIds.length >= 3 }"
              :aria-label="isFeatured(novel.id) ? '대표 책 해제' : '대표 책으로 설정'"
              :disabled="!isFeatured(novel.id) && featuredIds.length >= 3"
              @click="toggleFeatured(novel.id)"
            >★</button>
          </div>
        </li>
      </ul>

      <div v-if="loading" class="section-loading">
        <span class="loading-spinner" />
      </div>
    </template>
  </section>
</template>

<script>
import { api } from '../api'
import BackLink from '../components/BackLink.vue'
import { authState, isLoggedIn } from '../utils/auth'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'

export default {
  name: 'MyLibraryView',
  components: { BackLink },
  data() {
    return {
      novels: [],
      loading: true,
      error: '',
      featuredIds: [],
      saving: false,
      savedFlash: false,
      _saveTimer: null,
      _flashTimer: null,
    }
  },
  computed: {
    loggedIn() { return isLoggedIn() },
    userId() { return authState.user?.id },
  },
  mounted() {
    if (this.loggedIn) this.load()
    else this.loading = false
  },
  beforeUnmount() {
    clearTimeout(this._saveTimer)
    clearTimeout(this._flashTimer)
  },
  methods: {
    async load() {
      this.loading = true
      startPageLoading()
      this.error = ''
      try {
        const [scraps, posts, featured] = await Promise.all([
          api.listScrappedNovels().catch(() => []),
          this.userId ? api.getUserNovels(this.userId).catch(() => []) : Promise.resolve([]),
          this.userId ? api.getFeaturedNovels(this.userId).catch(() => ({ novel_ids: [] })) : Promise.resolve({ novel_ids: [] }),
        ])
        const seen = new Set()
        const merged = []
        for (const n of [...scraps, ...posts]) {
          if (!seen.has(n.id)) { seen.add(n.id); merged.push(n) }
        }
        this.novels = merged
        this.featuredIds = featured.novel_ids || []
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
        endPageLoading()
      }
    },
    isFeatured(novelId) {
      return this.featuredIds.includes(novelId)
    },
    toggleFeatured(novelId) {
      if (this.isFeatured(novelId)) {
        this.featuredIds = this.featuredIds.filter(id => id !== novelId)
      } else {
        if (this.featuredIds.length >= 3) return
        this.featuredIds = [...this.featuredIds, novelId]
      }
      this.scheduleSave()
    },
    scheduleSave() {
      clearTimeout(this._saveTimer)
      this._saveTimer = setTimeout(() => this.saveFeatured(), 600)
    },
    async saveFeatured() {
      if (!this.userId) return
      this.saving = true
      this.savedFlash = false
      try {
        await api.setFeaturedNovels(this.userId, this.featuredIds)
        this.saving = false
        this.savedFlash = true
        clearTimeout(this._flashTimer)
        this._flashTimer = setTimeout(() => { this.savedFlash = false }, 2000)
      } catch {
        this.saving = false
      }
    },
  },
}
</script>

<style scoped>
.library-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: var(--glt-space-4);
}

.library-header-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.result-count {
  margin: 0;
  font-size: 0.82rem;
  color: var(--glt-ink-tertiary);
}

.result-count-num {
  font-weight: 600;
  color: var(--glt-ink-secondary);
}

.library-hint {
  margin: 0;
  font-size: 0.76rem;
  color: var(--glt-ink-tertiary);
}

.saving-label {
  font-size: 0.76rem;
  color: var(--glt-ink-tertiary);
  flex-shrink: 0;
}

.saved-flash {
  color: var(--glt-accent);
}

.login-panel,
.empty-panel {
  padding: var(--glt-space-6) var(--glt-space-4);
  text-align: center;
}

.login-text,
.empty-title {
  margin: 0 0 var(--glt-space-2);
  font-weight: 600;
  color: var(--glt-ink);
}

.empty-desc {
  margin: 0 0 var(--glt-space-4);
  font-size: 0.88rem;
  color: var(--glt-ink-secondary);
}

.login-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: var(--glt-space-3);
}

.novel-grid {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(108px, 1fr));
  gap: 14px;
}

.novel-card-wrap {
  position: relative;
}

.novel-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px;
  text-decoration: none;
  color: inherit;
  transition: box-shadow 0.2s var(--glt-ease), transform 0.2s var(--glt-ease);
}

.novel-card:hover {
  box-shadow: var(--glt-shadow-md);
  transform: translateY(-2px);
}

.novel-cover-area {
  position: relative;
  width: 100%;
}

.novel-cover {
  width: 100%;
  aspect-ratio: 3 / 4.1;
  object-fit: cover;
  border-radius: 6px;
  box-shadow: var(--glt-shadow-sm);
  display: block;
}

.novel-cover--empty {
  display: grid;
  place-items: center;
  background: var(--glt-bg-subtle);
  font-size: 1.4rem;
}

.novel-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.novel-title {
  font-size: 0.78rem;
  line-height: 1.35;
  color: var(--glt-ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.novel-author {
  font-size: 0.72rem;
  color: var(--glt-ink-tertiary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.star-btn {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.38);
  backdrop-filter: blur(3px);
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
  line-height: 1;
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: background 0.15s, color 0.15s, transform 0.15s;
  z-index: 2;
}

.star-btn:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.55);
  color: #f5c842;
  transform: scale(1.1);
}

.star-btn--active {
  background: rgba(0, 0, 0, 0.42) !important;
  color: #f5c842 !important;
}

.star-btn--disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.section-loading {
  display: flex;
  justify-content: center;
  padding: 40px 0;
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
