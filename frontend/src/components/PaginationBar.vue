<template>
  <nav v-if="totalPages > 1" class="pagination" aria-label="페이지">
    <button
      type="button"
      class="glt-btn glt-btn-ghost page-btn"
      :disabled="page <= 1"
      @click="$emit('update:page', page - 1)"
    >
      이전
    </button>
    <span class="page-info">{{ page }} / {{ totalPages }}</span>
    <button
      type="button"
      class="glt-btn glt-btn-ghost page-btn"
      :disabled="page >= totalPages"
      @click="$emit('update:page', page + 1)"
    >
      다음
    </button>
  </nav>
</template>

<script>
export default {
  name: 'PaginationBar',
  props: {
    page: { type: Number, required: true },
    total: { type: Number, required: true },
    pageSize: { type: Number, required: true },
  },
  emits: ['update:page'],
  computed: {
    totalPages() {
      return Math.max(1, Math.ceil(this.total / this.pageSize))
    },
  },
}
</script>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: var(--glt-space-5);
}

.page-btn {
  font-size: 0.8rem;
  padding: 8px 14px;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.82rem;
  color: var(--glt-ink-secondary);
  min-width: 4.5rem;
  text-align: center;
}
</style>
