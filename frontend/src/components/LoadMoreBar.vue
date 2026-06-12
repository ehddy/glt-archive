<template>
  <div v-if="hasMore" class="load-more">
    <button
      type="button"
      class="glt-btn glt-btn-ghost load-more-btn"
      :disabled="loading"
      @click="$emit('load-more')"
    >
      <span v-if="loading" class="load-more-spinner" aria-hidden="true" />
      <template v-if="!loading">
        더 보기
        <span class="load-more-count">{{ shown }} / {{ total }}</span>
      </template>
    </button>
  </div>
</template>

<script>
export default {
  name: 'LoadMoreBar',
  props: {
    shown: { type: Number, required: true },
    total: { type: Number, required: true },
    pageSize: { type: Number, required: true },
    loading: { type: Boolean, default: false },
  },
  emits: ['load-more'],
  computed: {
    hasMore() {
      return this.shown < this.total
    },
  },
}
</script>

<style scoped>
.load-more {
  display: flex;
  justify-content: center;
  margin-top: var(--glt-space-5);
  padding-bottom: var(--glt-space-2);
}

.load-more-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-width: 9.5rem;
  padding: 10px 18px;
  font-size: 0.84rem;
  font-weight: 600;
}

.load-more-btn:disabled {
  opacity: 0.72;
  cursor: wait;
}

.load-more-count {
  font-size: 0.76rem;
  font-weight: 500;
  color: var(--glt-ink-tertiary);
}

.load-more-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid var(--glt-glass-border);
  border-top-color: var(--glt-accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
