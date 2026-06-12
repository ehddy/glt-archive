<template>
  <AuthSheet :title="LIKE.loginTitle" :subtitle="LIKE.loginSubtitle">
    <form class="auth-form" @submit.prevent="submit">
      <label class="field">
        <span class="field-label">이메일</span>
        <input
          v-model="email"
          type="email"
          autocomplete="email"
          class="field-input"
          placeholder="you@example.com"
          required
        />
      </label>

      <label class="field">
        <span class="field-label">비밀번호</span>
        <input
          v-model="password"
          type="password"
          autocomplete="current-password"
          class="field-input"
          placeholder="8자 이상"
          required
        />
      </label>

      <p v-if="error" class="auth-error">{{ error }}</p>

      <button type="submit" class="glt-btn glt-btn-primary submit-btn" :disabled="submitting">
        {{ submitting ? '로그인 중…' : '로그인' }}
      </button>
    </form>

    <template #footer>
      아직 계정이 없어요?
      <router-link :to="signupLink">회원가입</router-link>
    </template>
  </AuthSheet>
</template>

<script>
import { api } from '../api'
import AuthSheet from '../components/AuthSheet.vue'
import { applyAuthResponse } from '../utils/auth'
import { LIKE } from '../utils/likeLabels'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'

export default {
  name: 'LoginView',
  components: { AuthSheet },
  data() {
    return {
      LIKE,
      email: '',
      password: '',
      error: '',
      submitting: false,
    }
  },
  computed: {
    signupLink() {
      const redirect = this.$route.query.redirect
      return redirect
        ? { name: 'signup', query: { redirect } }
        : { name: 'signup' }
    },
  },
  mounted() {
    endPageLoading()
  },
  methods: {
    async submit() {
      this.error = ''
      this.submitting = true
      startPageLoading()
      try {
        const res = await api.login({
          email: this.email.trim(),
          password: this.password,
        })
        applyAuthResponse(res)
        const redirect = this.$route.query.redirect || '/saved'
        this.$router.replace(String(redirect))
      } catch (e) {
        this.error = e.message
      } finally {
        this.submitting = false
        endPageLoading()
      }
    },
  },
}
</script>

<style scoped>
.auth-form {
  display: flex;
  flex-direction: column;
  gap: var(--glt-space-3);
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--glt-ink-secondary);
}

.field-input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid var(--glt-glass-border);
  border-radius: var(--glt-radius-md);
  background: var(--glt-bg-subtle);
  font-size: 0.95rem;
  color: var(--glt-ink);
}

.field-input:focus {
  outline: 2px solid var(--glt-accent-muted);
  outline-offset: 1px;
}

.auth-error {
  margin: 0;
  font-size: 0.88rem;
  color: #b42318;
}

.submit-btn {
  width: 100%;
  margin-top: 6px;
}
</style>
