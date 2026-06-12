<template>
  <button
    type="button"
    class="bookmark-icon-btn"
    :class="{ 'is-saved': saved }"
    :aria-label="saved ? savedLabel : actionLabel"
    :aria-pressed="saved"
    @click="$emit('click', $event)"
  >
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M12 20.2l-1-1C6.2 14.8 4 12.6 4 10a4 4 0 0 1 7-2.4A4 4 0 0 1 20 10c0 2.6-2.2 4.8-7 9.2l-1 1z"
        :fill="saved ? 'currentColor' : 'none'"
        stroke="currentColor"
        stroke-width="1.75"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
  </button>
</template>

<script>
export default {
  name: 'BookmarkIconButton',
  props: {
    saved: { type: Boolean, default: false },
    actionLabel: { type: String, default: '담기' },
    savedLabel: { type: String, default: '담아둠' },
  },
  emits: ['click'],
}
</script>

<style scoped>
.bookmark-icon-btn {
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

.bookmark-icon-btn:hover {
  color: var(--glt-accent-hover);
  border-color: var(--glt-accent-muted);
  background: var(--glt-accent-soft);
}

.bookmark-icon-btn.is-saved {
  color: var(--glt-accent-hover);
  border-color: var(--glt-accent-muted);
  background: var(--glt-accent-soft);
}

.bookmark-icon-btn svg {
  width: 17px;
  height: 17px;
  display: block;
}
</style>
