<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-card glt-card" role="dialog" aria-modal="true">
      <button type="button" class="modal-close" aria-label="닫기" @click="$emit('close')">×</button>

      <div v-if="loading" class="modal-state">불러오는 중…</div>
      <div v-else-if="error" class="modal-state modal-error">{{ error }}</div>
      <template v-else-if="novel">
        <div class="modal-body">
          <img
            v-if="novel.cover_url"
            :src="novel.cover_url"
            :alt="`${novel.title} 표지`"
            class="modal-cover"
          />
          <div v-else class="modal-cover modal-cover--empty">📖</div>

          <div class="modal-info">
            <h2 class="modal-title">{{ novel.title }}</h2>
            <p v-if="novel.author" class="modal-author">{{ novel.author.name }}</p>

            <dl class="meta-list">
              <template v-if="novel.publisher">
                <dt>출판사</dt>
                <dd>{{ novel.publisher }}</dd>
              </template>
              <template v-if="novel.pub_date">
                <dt>출간일</dt>
                <dd>{{ novel.pub_date }}</dd>
              </template>
              <template v-if="novel.isbn13 || novel.isbn">
                <dt>ISBN</dt>
                <dd>{{ novel.isbn13 || novel.isbn }}</dd>
              </template>
              <template v-if="novel.category_name">
                <dt>분류</dt>
                <dd>{{ novel.category_name }}</dd>
              </template>
              <template v-if="novel.price_sales">
                <dt>가격</dt>
                <dd>{{ novel.price_sales.toLocaleString() }}원</dd>
              </template>
              <dt>구절</dt>
              <dd>{{ novel.quote_count }}개</dd>
            </dl>

            <p v-if="novel.description" class="modal-desc">{{ novel.description }}</p>

            <section v-if="novel.quotes?.length" class="modal-quotes">
              <h3 class="modal-quotes-title">등록된 구절</h3>
              <ul class="quote-list">
                <li v-for="quote in novel.quotes" :key="quote.id">
                  <router-link
                    :to="`/quotes/${quote.id}`"
                    class="quote-item"
                    @click="$emit('close')"
                  >
                    <p class="quote-item-text">{{ quote.text }}</p>
                  </router-link>
                </li>
              </ul>
            </section>
            <p v-else-if="novel.quote_count === 0" class="modal-no-quotes">
              아직 등록된 구절이 없습니다.
            </p>

            <div class="modal-actions">
              <router-link
                v-if="registerRoute"
                :to="registerRoute"
                class="glt-btn glt-btn-primary"
                @click="$emit('close')"
              >
                구절 추가
              </router-link>
              <a
                v-if="novel.aladin_link"
                :href="novel.aladin_link"
                target="_blank"
                rel="noopener noreferrer"
                class="glt-btn glt-btn-ghost"
              >
                알라딘
              </a>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import { api } from '../api'
import { registerRouteForNovel } from '../utils/registerBook'

export default {
  name: 'BookDetailModal',
  props: {
    novelId: { type: Number, required: true },
  },
  emits: ['close'],
  data() {
    return {
      novel: null,
      loading: true,
      error: '',
    }
  },
  computed: {
    registerRoute() {
      if (!this.novel) return null
      return registerRouteForNovel(this.novel)
    },
  },
  watch: {
    novelId: {
      immediate: true,
      handler() {
        this.loadNovel()
      },
    },
  },
  methods: {
    async loadNovel() {
      this.loading = true
      this.error = ''
      try {
        this.novel = await api.getNovel(this.novelId)
      } catch (e) {
        this.error = e.message
        this.novel = null
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: grid;
  place-items: center;
  padding: var(--glt-space-4);
  background: rgba(45, 38, 32, 0.45);
  backdrop-filter: blur(4px);
}

.modal-card {
  position: relative;
  width: min(520px, 100%);
  max-height: min(88vh, 720px);
  overflow-y: auto;
  padding: var(--glt-space-5);
}

.modal-close {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: var(--glt-radius-full);
  background: var(--glt-overlay);
  color: var(--glt-ink-secondary);
  font-size: 1.4rem;
  line-height: 1;
  cursor: pointer;
}

.modal-close:hover {
  color: var(--glt-ink);
}

.modal-state {
  padding: var(--glt-space-6) 0;
  text-align: center;
  color: var(--glt-ink-secondary);
}

.modal-error {
  color: var(--glt-accent-hover);
}

.modal-body {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: var(--glt-space-4);
  align-items: start;
}

.modal-cover {
  width: 120px;
  height: 172px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: var(--glt-shadow-md);
}

.modal-cover--empty {
  display: grid;
  place-items: center;
  background: var(--glt-bg-subtle);
  font-size: 2rem;
}

.modal-title {
  margin: var(--glt-space-2) 0 4px;
  font-size: 1.2rem;
  line-height: 1.4;
  color: var(--glt-ink);
}

.modal-author {
  margin: 0 0 var(--glt-space-3);
  font-size: 0.92rem;
  color: var(--glt-ink-secondary);
}

.meta-list {
  display: grid;
  grid-template-columns: 72px 1fr;
  gap: 6px 10px;
  margin: 0 0 var(--glt-space-3);
  font-size: 0.84rem;
}

.meta-list dt {
  color: var(--glt-ink-tertiary);
  font-weight: 600;
}

.meta-list dd {
  margin: 0;
  color: var(--glt-ink-secondary);
}

.modal-desc {
  margin: 0 0 var(--glt-space-4);
  font-size: 0.86rem;
  line-height: 1.65;
  color: var(--glt-ink-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 8;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.modal-quotes {
  margin: 0 0 var(--glt-space-4);
}

.modal-quotes-title {
  margin: 0 0 var(--glt-space-2);
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--glt-ink-secondary);
}

.quote-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quote-item {
  display: block;
  padding: 10px 12px;
  border-radius: var(--glt-radius-md);
  border: 1px solid var(--glt-glass-border);
  background: var(--glt-bg-subtle);
  text-decoration: none;
  color: inherit;
  transition: border-color 0.2s var(--glt-ease), background 0.2s var(--glt-ease);
}

.quote-item:hover {
  border-color: var(--glt-accent-muted);
  background: var(--glt-surface);
}

.quote-item-text {
  margin: 0;
  font-size: 0.84rem;
  line-height: 1.6;
  color: var(--glt-ink);
  word-break: keep-all;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.modal-no-quotes {
  margin: 0 0 var(--glt-space-4);
  font-size: 0.84rem;
  color: var(--glt-ink-tertiary);
}

.modal-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

@media (max-width: 520px) {
  .modal-body {
    grid-template-columns: 1fr;
    justify-items: center;
    text-align: center;
  }

  .meta-list {
    width: 100%;
    text-align: left;
  }
}
</style>
