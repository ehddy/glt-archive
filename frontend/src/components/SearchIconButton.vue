<template>
  <button
    class="search-icon-btn"
    :type="type"
    :disabled="disabled"
    aria-label="검색"
    @click="$emit('click', $event)"
  >
    <svg class="search-icon-btn-svg" viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="11" cy="11" r="6.5" fill="none" stroke="currentColor" stroke-width="1.75" />
      <path
        d="M16.5 16.5L20 20"
        fill="none"
        stroke="currentColor"
        stroke-width="1.75"
        stroke-linecap="round"
      />
    </svg>
  </button>
</template>

<script>
export default {
  name: 'SearchIconButton',
  props: {
    type: { type: String, default: 'button' },
    disabled: { type: Boolean, default: false },
  },
  emits: ['click'],
}
</script>

<style scoped>
.search-icon-btn {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  border: none;
  border-radius: 50%;
  background: var(--glt-accent);
  color: #fff;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(95, 143, 122, 0.22);
  transition: background var(--glt-duration), opacity var(--glt-duration);
}

.search-icon-btn:hover:not(:disabled) {
  background: var(--glt-accent-hover);
}

.search-icon-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.search-icon-btn-svg {
  width: 18px;
  height: 18px;
  display: block;
}
</style>
