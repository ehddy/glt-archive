<template>
  <section v-if="loading" class="glt-empty">불러오는 중...</section>
  <section v-else-if="error" class="glt-empty">{{ error }}</section>
  <section v-else-if="quote" class="detail">
    <router-link to="/" class="back-link">← 목록으로</router-link>

    <div class="detail-graph glt-card">
      <div class="detail-source">
        <BookNode
          v-if="novelTitle"
          :title="novelTitle"
          :author="authorName"
          :quote-count="1"
          :color-index="bookColorIndex"
        />
        <div v-else class="detail-source-fallback">
          <span class="glt-eyebrow">미분류</span>
          <p v-if="authorName" class="fallback-author">{{ authorName }}</p>
        </div>
        <div class="detail-connector" />
      </div>
      <article class="detail-quote glt-card-raised">
        <p class="glt-quote glt-quote-lg">{{ quote.text }}</p>
      </article>
    </div>

    <section class="edit-section glt-card">
      <h2 class="glt-section-title">내용 편집</h2>
      <p class="edit-desc">구절이나 작가·작품 정보가 틀렸다면 수정해 주세요.</p>

      <div class="glt-field">
        <label>구절</label>
        <textarea v-model="form.text" />
      </div>
      <div class="glt-field">
        <label>작가</label>
        <input v-model="form.author_name" />
      </div>
      <div class="glt-field">
        <label>작품</label>
        <input v-model="form.novel_title" />
      </div>
      <button class="glt-btn glt-btn-primary" :disabled="saving" @click="save">
        {{ saving ? '저장 중...' : '저장' }}
      </button>
      <p v-if="saveMessage" class="save-message">{{ saveMessage }}</p>
    </section>

    <section v-if="versions.length > 1" class="history glt-card">
      <h2 class="glt-section-title">수정 이력</h2>
      <div v-for="version in versions" :key="version.id" class="history-item">
        <div class="history-head">
          <strong>v{{ version.version }}</strong>
          <span>{{ formatDate(version.created_at) }}</span>
        </div>
        <p class="history-text">{{ version.text }}</p>
      </div>
    </section>
  </section>
</template>

<script>
import { api } from '../api'
import BookNode from '../components/BookNode.vue'

export default {
  name: 'QuoteDetailView',
  components: { BookNode },
  data() {
    return {
      quote: null,
      versions: [],
      loading: true,
      error: '',
      saving: false,
      saveMessage: '',
      form: {
        text: '',
        author_name: '',
        novel_title: '',
      },
    }
  },
  computed: {
    authorName() {
      return this.quote?.author?.name || this.quote?.novel?.author?.name || ''
    },
    novelTitle() {
      return this.quote?.novel?.title || ''
    },
    bookColorIndex() {
      return (this.quote?.novel?.id || 0) % 8
    },
  },
  watch: {
    '$route.params.id': {
      immediate: true,
      handler() {
        this.loadQuote()
      },
    },
  },
  methods: {
    async loadQuote() {
      this.loading = true
      this.error = ''
      try {
        const id = this.$route.params.id
        const [quote, versions] = await Promise.all([
          api.getQuote(id),
          api.getVersions(id),
        ])
        this.quote = quote
        this.versions = versions
        this.form = {
          text: quote.text,
          author_name: this.authorName,
          novel_title: this.novelTitle,
        }
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    },
    async save() {
      this.saving = true
      this.saveMessage = ''
      try {
        this.quote = await api.updateQuote(this.$route.params.id, {
          text: this.form.text,
          author_name: this.form.author_name,
          novel_title: this.form.novel_title,
        })
        this.versions = await api.getVersions(this.$route.params.id)
        this.form = {
          text: this.quote.text,
          author_name: this.authorName,
          novel_title: this.novelTitle,
        }
        this.saveMessage = '저장되었습니다.'
      } catch (e) {
        this.saveMessage = e.message
      } finally {
        this.saving = false
      }
    },
    formatDate(value) {
      return new Date(value).toLocaleString('ko-KR')
    },
  },
}
</script>

<style scoped>
.back-link {
  display: inline-block;
  margin-bottom: var(--glt-space-5);
  color: var(--glt-ink-secondary);
  font-size: 0.85rem;
}

.detail-graph {
  display: flex;
  align-items: center;
  gap: var(--glt-space-6);
  padding: var(--glt-space-6);
  margin-bottom: var(--glt-space-4);
}

.detail-source {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.detail-connector {
  width: 48px;
  height: 2px;
  background: linear-gradient(90deg, var(--glt-line-active), var(--glt-accent-muted));
  margin-left: var(--glt-space-2);
  position: relative;
}

.detail-connector::after {
  content: '';
  position: absolute;
  right: -4px;
  top: 50%;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--glt-accent-soft);
  border: 2px solid var(--glt-accent-muted);
  transform: translateY(-50%);
}

.detail-quote {
  flex: 1;
  padding: var(--glt-space-6);
}

.detail-source-fallback {
  width: var(--glt-book-width);
  padding: var(--glt-space-5);
  background: var(--glt-surface);
  border: 1px dashed var(--glt-line);
  border-radius: var(--glt-radius-md);
}

.fallback-author {
  margin: var(--glt-space-2) 0 0;
  font-size: 0.85rem;
  color: var(--glt-ink-secondary);
}

.edit-section,
.history {
  padding: var(--glt-space-6);
  margin-bottom: var(--glt-space-4);
}

.edit-desc {
  color: var(--glt-ink-secondary);
  margin: var(--glt-space-2) 0 var(--glt-space-5);
  font-size: 0.875rem;
}

.save-message {
  margin-top: var(--glt-space-3);
  color: var(--glt-accent);
  font-size: 0.875rem;
}

.history-item {
  padding: var(--glt-space-4) 0;
  border-top: 1px solid var(--glt-line);
}

.history-head {
  display: flex;
  justify-content: space-between;
  gap: var(--glt-space-3);
  color: var(--glt-ink-tertiary);
  font-size: 0.8rem;
  margin-bottom: var(--glt-space-2);
}

.history-text {
  margin: 0;
  color: var(--glt-ink-secondary);
  font-size: 0.9rem;
  line-height: 1.6;
}

@media (max-width: 720px) {
  .detail-graph {
    flex-direction: column;
    align-items: stretch;
  }

  .detail-source {
    flex-direction: column;
    align-items: center;
  }

  .detail-connector {
    width: 2px;
    height: 32px;
    margin: var(--glt-space-2) 0;
  }

  .detail-connector::after {
    right: 50%;
    top: auto;
    bottom: -4px;
    transform: translateX(50%);
  }
}
</style>
