<template>
  <button
    class="clear-icon-btn"
    type="button"
    :aria-label="label"
    @click="$emit('click', $event)"
  >
    <svg class="clear-icon-btn-svg" viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M8 8l8 8M16 8l-8 8"
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
  name: 'ClearIconButton',
  props: {
    label: { type: String, default: '지우기' },
  },
  emits: ['click'],
}
</script>

<style scoped>
.clear-icon-btn {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  border: none;
  border-radius: 50%;
  background: transparent;
  color: var(--glt-ink-tertiary);
  cursor: pointer;
  transition: background var(--glt-duration), color var(--glt-duration);
}

.clear-icon-btn:hover {
  background: var(--glt-overlay);
  color: var(--glt-ink-secondary);
}

.clear-icon-btn-svg {
  width: 16px;
  height: 16px;
  display: block;
}
</style>
