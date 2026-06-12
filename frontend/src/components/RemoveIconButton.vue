<template>
  <button type="button" class="remove-icon-btn" :aria-label="label" @click="$emit('click', $event)">
    <svg viewBox="0 0 24 24" aria-hidden="true">
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
  name: 'RemoveIconButton',
  props: {
    label: { type: String, default: '빼기' },
  },
  emits: ['click'],
}
</script>

<style scoped>
.remove-icon-btn {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border: 1px solid var(--glt-glass-border);
  border-radius: 50%;
  background: var(--glt-surface);
  color: var(--glt-ink-tertiary);
  cursor: pointer;
  transition:
    color var(--glt-duration),
    border-color var(--glt-duration),
    background var(--glt-duration);
}

.remove-icon-btn:hover {
  color: var(--glt-accent-hover);
  border-color: var(--glt-accent-muted);
  background: var(--glt-accent-soft);
}

.remove-icon-btn svg {
  width: 16px;
  height: 16px;
  display: block;
}
</style>
