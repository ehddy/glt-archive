<template>
  <router-link :to="to" class="detail-icon-link" :aria-label="label">
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M10 7l5 5-5 5"
        fill="none"
        stroke="currentColor"
        stroke-width="1.75"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
  </router-link>
</template>

<script>
export default {
  name: 'DetailIconLink',
  props: {
    to: { type: [String, Object], required: true },
    label: { type: String, default: '자세히 보기' },
  },
}
</script>

<style scoped>
.detail-icon-link {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  border: 1px solid var(--glt-glass-border);
  background: var(--glt-surface);
  color: var(--glt-ink-secondary);
  text-decoration: none;
  transition:
    color var(--glt-duration),
    border-color var(--glt-duration),
    background var(--glt-duration);
}

.detail-icon-link:hover {
  color: var(--glt-ink);
  border-color: var(--glt-accent-muted);
  background: var(--glt-accent-soft);
}

.detail-icon-link svg {
  width: 18px;
  height: 18px;
  display: block;
}
</style>
