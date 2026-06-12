<template>
  <button
    type="button"
    class="edit-icon-btn"
    :aria-label="label"
    @click="$emit('click', $event)"
  >
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M5 18.5h2.8L17.5 9 14.5 6 5 15.5V18.5z"
        fill="none"
        stroke="currentColor"
        stroke-width="1.75"
        stroke-linejoin="round"
      />
      <path
        d="M13 7l3 3"
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
  name: 'EditIconButton',
  props: {
    label: { type: String, default: '변경' },
  },
  emits: ['click'],
}
</script>

<style scoped>
.edit-icon-btn {
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  border: 1px solid var(--glt-glass-border);
  border-radius: 50%;
  background: var(--glt-surface);
  color: var(--glt-ink-secondary);
  cursor: pointer;
  transition:
    color var(--glt-duration),
    border-color var(--glt-duration),
    background var(--glt-duration);
}

.edit-icon-btn:hover {
  color: var(--glt-accent-hover);
  border-color: var(--glt-accent-muted);
  background: var(--glt-accent-soft);
}

.edit-icon-btn svg {
  width: 15px;
  height: 15px;
  display: block;
}
</style>
