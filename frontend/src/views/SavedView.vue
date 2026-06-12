<template>
  <section class="saved glt-container">
    <h1 class="glt-title">{{ LIKE.pageTitle }}</h1>

    <div v-if="!loggedIn" class="login-panel glt-card">
      <p class="login-text">{{ LIKE.loginRequired }}</p>
      <div class="login-actions">
        <router-link :to="{ name: 'login', query: { redirect: '/saved' } }" class="glt-btn glt-btn-primary">
          {{ LIKE.loginTitle }}
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

      <div v-if="error && !loading" class="glt-empty">{{ error }}</div>
      <div v-else-if="!loading && !quotes.length" class="glt-empty glt-card">{{ LIKE.empty }}</div>

      <SavedQuoteList
        v-else-if="!loading"
        :quotes="quotes"
        @remove="removeLike"
      />
    </template>
  </section>
</template>

<script>
import { api } from '../api'
import SavedQuoteList from '../components/SavedQuoteList.vue'
import { authState, clearSession, isLoggedIn } from '../utils/auth'
import { LIKE } from '../utils/likeLabels'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'

export default {
  name: 'SavedView',
  components: { SavedQuoteList },
  data() {
    return {
      LIKE,
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
  },
  watch: {
    '$route.fullPath'() {
      if (this.loggedIn) this.load()
    },
  },
  mounted() {
    if (this.loggedIn) this.load()
    else {
      this.loading = false
    }
  },
  methods: {
    async load() {
      this.loading = true
      startPageLoading()
      this.error = ''
      try {
        this.quotes = await api.listLikes()
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
        endPageLoading()
      }
    },
    async removeLike(quoteId) {
      try {
        await api.removeLike(quoteId)
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
  margin-bottom: var(--glt-space-3);
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
</style>
