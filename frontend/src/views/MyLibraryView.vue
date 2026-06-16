<template>
  <section class="my-library glt-container">
    <BackLink use-history fallback-to="/saved" label="뒤로" />
    <div v-if="!loggedIn" class="login-panel glt-card">
      <p class="login-text">로그인하면 스크랩한 문장의 책들을 모아볼 수 있어요</p>
      <div class="login-actions">
        <router-link :to="{ name: 'login', query: { redirect: '/my-library' } }" class="glt-btn glt-btn-primary">
          로그인
        </router-link>
        <router-link :to="{ name: 'signup', query: { redirect: '/my-library' } }" class="glt-btn glt-btn-ghost">
          회원가입
        </router-link>
      </div>
    </div>

    <template v-else>
      <p v-if="!loading && novels.length" class="result-count">
        <span class="result-count-num">{{ novels.length }}</span>권
      </p>

      <div v-if="error && !loading" class="glt-empty glt-card">{{ error }}</div>

      <div v-else-if="!loading && !novels.length" class="empty-panel glt-card">
        <p class="empty-title">아직 수집한 책이 없어요</p>
        <p class="empty-desc">문장을 스크랩하면 여기에 책이 쌓여요</p>
        <router-link to="/" class="glt-btn glt-btn-primary">문장 둘러보기</router-link>
      </div>

      <ul v-else-if="!loading" class="novel-grid">
        <li v-for="novel in novels" :key="novel.id">
          <router-link :to="`/novels/${novel.id}`" class="novel-card glt-card">
            <img
              v-if="novel.cover_url"
              :src="novel.cover_url"
              :alt="novel.title"
              class="novel-cover"
            />
            <div v-else class="novel-cover novel-cover--empty">📖</div>
            <div class="novel-meta">
              <strong class="novel-title">{{ novel.title }}</strong>
              <span v-if="novel.author" class="novel-author">{{ novel.author.name }}</span>
            </div>
          </router-link>
        </li>
      </ul>
    </template>
  </section>
</template>

<script>
import { api } from '../api'
import BackLink from '../components/BackLink.vue'
import { isLoggedIn } from '../utils/auth'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'

export default {
  name: 'MyLibraryView',
  components: { BackLink },
  data() {
    return {
      novels: [],
      loading: true,
      error: '',
    }
  },
  computed: {
    loggedIn() {
      return isLoggedIn()
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
        this.novels = await api.listScrappedNovels()
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
        endPageLoading()
      }
    },
  },
}
</script>

<style scoped>
.result-count {
  margin: 0 0 var(--glt-space-4);
  font-size: 0.82rem;
  color: var(--glt-ink-tertiary);
}

.result-count-num {
  font-weight: 600;
  color: var(--glt-ink-secondary);
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

.novel-cover {
  width: 100%;
  aspect-ratio: 3 / 4.1;
  object-fit: cover;
  border-radius: 6px;
  box-shadow: var(--glt-shadow-sm);
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
</style>
