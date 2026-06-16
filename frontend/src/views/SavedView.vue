<template>
  <section class="saved glt-container">
    <h1 class="glt-title">스크랩</h1>

    <div v-if="!loggedIn" class="login-panel glt-card">
      <p class="login-text">로그인하면 문장을 스크랩하고 다시 볼 수 있어요</p>
      <div class="login-actions">
        <router-link :to="{ name: 'login', query: { redirect: '/saved' } }" class="glt-btn glt-btn-primary">
          로그인
        </router-link>
        <router-link :to="{ name: 'signup', query: { redirect: '/saved' } }" class="glt-btn glt-btn-ghost">
          회원가입
        </router-link>
      </div>
    </div>

    <template v-else>
      <div v-if="userName" class="user-chip glt-card">
        <span>{{ userName }}</span>
        <button type="button" class="logout-btn" @click="logout">로그아웃</button>
      </div>

      <template v-if="!loading">
        <section v-if="myBooks.length" class="my-bookshelf">
          <header class="shelf-head">
            <div class="shelf-head-left">
              <h2 class="shelf-title">내 책장</h2>
              <span class="shelf-count">{{ myBooks.length }}권</span>
            </div>
            <router-link to="/my-library" class="shelf-more">
              더보기
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <path d="M9 6l6 6-6 6"/>
              </svg>
            </router-link>
          </header>
          <div class="shelf-scroll">
            <router-link
              v-for="book in myBooks.slice(0, 10)"
              :key="book.id"
              :to="`/novels/${book.id}`"
              class="shelf-book"
            >
              <img
                v-if="book.cover_url"
                :src="book.cover_url"
                :alt="book.title"
                class="shelf-cover"
              />
              <div v-else class="shelf-cover shelf-cover--empty">📖</div>
              <p class="shelf-book-title">{{ book.title }}</p>
              <p v-if="book.authorName" class="shelf-book-author">{{ book.authorName }}</p>
            </router-link>
          </div>
        </section>

        <div v-if="error" class="glt-empty">{{ error }}</div>
        <div v-else-if="!quotes.length" class="glt-empty glt-card">아직 스크랩한 문장이 없어요</div>
        <SavedQuoteList
          v-else
          :quotes="quotes"
          @remove="removeScrap"
        />
      </template>
    </template>
  </section>
</template>

<script>
import { api } from '../api'
import SavedQuoteList from '../components/SavedQuoteList.vue'
import { authState, clearSession, isLoggedIn } from '../utils/auth'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'

export default {
  name: 'SavedView',
  components: { SavedQuoteList },
  data() {
    return {
      quotes: [],
      loading: true,
      error: '',
    }
  },
  computed: {
    loggedIn() {
      return isLoggedIn()
    },
    userName() {
      return authState.user?.name || authState.user?.email || ''
    },
    myBooks() {
      const seen = new Set()
      const books = []
      for (const q of this.quotes) {
        const novelId = q.novel?.id || q.source?.novel_id
        if (!novelId || seen.has(novelId)) continue
        seen.add(novelId)
        books.push({
          id: novelId,
          title: q.novel?.title || q.source?.title || '',
          cover_url: q.novel?.cover_url || q.source?.cover_url || null,
          authorName: q.novel?.author?.name || q.source?.author?.name || q.author?.name || null,
        })
      }
      return books
    },
  },
  watch: {
    '$route.fullPath'() {
      if (this.loggedIn) this.load()
    },
  },
  mounted() {
    if (this.loggedIn) this.load()
    else this.loading = false
  },
  methods: {
    async load() {
      this.loading = true
      startPageLoading()
      this.error = ''
      try {
        this.quotes = await api.listScraps()
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
        endPageLoading()
      }
    },
    async removeScrap(quoteId) {
      try {
        await api.removeScrap(quoteId)
        this.quotes = this.quotes.filter((q) => q.id !== quoteId)
      } catch (e) {
        this.error = e.message
      }
    },
    logout() {
      clearSession()
      this.quotes = []
      this.$router.push('/')
    },
  },
}
</script>

<style scoped>
.saved .glt-title {
  margin-bottom: var(--glt-space-2);
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

.user-chip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 14px;
  margin-bottom: var(--glt-space-4);
  font-size: 0.88rem;
  color: var(--glt-ink-secondary);
}

.logout-btn {
  border: none;
  background: transparent;
  color: var(--glt-ink-tertiary);
  font-size: 0.82rem;
  cursor: pointer;
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

.shelf-more:hover {
  color: var(--glt-accent-hover);
}

.shelf-scroll {
  display: flex;
  gap: 14px;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 4px 2px 12px;
  scrollbar-width: none;
  -ms-overflow-style: none;
  scroll-snap-type: x proximity;
  -webkit-overflow-scrolling: touch;
  touch-action: pan-x;
  overscroll-behavior-x: contain;
  user-select: none;
  -webkit-user-select: none;
}

.shelf-scroll::-webkit-scrollbar {
  display: none;
}

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
</style>
