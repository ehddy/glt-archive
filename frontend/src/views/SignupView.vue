<template>
  <AuthSheet title="회원가입" subtitle="이메일로 가입하고 좋아요한 문장을 모아볼 수 있어요.">
    <form class="auth-form" @submit.prevent="submit">
      <label class="field">
        <span class="field-label">이름 (선택)</span>
        <input
          v-model="name"
          type="text"
          autocomplete="name"
          class="field-input"
          placeholder="표시 이름"
          maxlength="100"
        />
      </label>

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
          autocomplete="new-password"
          class="field-input"
          placeholder="8자 이상"
          minlength="8"
          required
        />
      </label>

      <p v-if="error" class="auth-error">{{ error }}</p>

      <button type="submit" class="glt-btn glt-btn-primary submit-btn" :disabled="submitting">
        {{ submitting ? '가입 중…' : '가입하기' }}
      </button>
    </form>

    <template #footer>
      이미 계정이 있어요?
      <router-link :to="loginLink">로그인</router-link>
    </template>
  </AuthSheet>
</template>

<script>
import { api } from '../api'
import AuthSheet from '../components/AuthSheet.vue'
import { applyAuthResponse } from '../utils/auth'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'

export default {
  name: 'SignupView',
  components: { AuthSheet },
  data() {
    return {
      name: '',
      email: '',
      password: '',
      error: '',
      submitting: false,
    }
  },
  computed: {
    loginLink() {
      const redirect = this.$route.query.redirect
      return redirect
        ? { name: 'login', query: { redirect } }
        : { name: 'login' }
    },
  },
  mounted() {
    endPageLoading()
  },
  methods: {
    async submit() {
      this.error = ''
      if (this.password.length < 8) {
        this.error = '비밀번호는 8자 이상이어야 해요.'
        return
      }
      this.submitting = true
      startPageLoading()
      try {
        const res = await api.register({
          email: this.email.trim(),
          password: this.password,
          name: this.name.trim() || undefined,
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
