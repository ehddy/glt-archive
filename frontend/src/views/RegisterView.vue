<template>
  <section class="register">
    <span class="glt-eyebrow">New Branch</span>
    <h1 class="glt-title">구절 등록</h1>
    <p class="glt-subtitle">
      작품 노드에 연결될 구절을 등록합니다. 작가와 작품을 함께 입력해 주세요.
    </p>

    <form class="form-card glt-card" @submit.prevent="submit">
      <div class="glt-field">
        <label>구절 *</label>
        <textarea
          v-model="form.text"
          required
          placeholder="인용할 구절을 입력하세요"
        />
      </div>
      <div class="form-row">
        <div class="glt-field">
          <label>작가</label>
          <input v-model="form.author_name" placeholder="예: 한강" />
        </div>
        <div class="glt-field">
          <label>작품</label>
          <input v-model="form.novel_title" placeholder="예: 소년이 온다" />
        </div>
      </div>

      <button class="glt-btn glt-btn-primary" type="submit" :disabled="submitting">
        {{ submitting ? '등록 중...' : '등록하기' }}
      </button>
      <p v-if="message" class="message">{{ message }}</p>
    </form>
  </section>
</template>

<script>
import { api } from '../api'

export default {
  name: 'RegisterView',
  data() {
    return {
      submitting: false,
      message: '',
      form: {
        text: '',
        author_name: '',
        novel_title: '',
      },
    }
  },
  methods: {
    async submit() {
      this.submitting = true
      this.message = ''
      try {
        const quote = await api.createQuote(this.form)
        this.$router.push(`/quotes/${quote.id}`)
      } catch (e) {
        this.message = e.message
      } finally {
        this.submitting = false
      }
    },
  },
}
</script>

<style scoped>
.form-card {
  padding: var(--glt-space-6);
  max-width: 560px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--glt-space-4);
}

.form-row .glt-field {
  margin-bottom: 0;
}

@media (max-width: 520px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}

.message {
  margin-top: var(--glt-space-3);
  color: var(--glt-accent);
  font-size: 0.875rem;
}
</style>
