<template>
  <button
    type="button"
    class="scrap-btn"
    :class="{ 'is-scrapped': scrapped }"
    :aria-label="scrapped ? '스크랩 취소' : '스크랩'"
    :aria-pressed="scrapped"
    @click.stop="$emit('click', $event)"
  >
    <svg class="scrap-btn-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M5 3h14a1 1 0 0 1 1 1v17l-8-4-8 4V4a1 1 0 0 1 1-1z"
        :fill="scrapped ? 'currentColor' : 'none'"
        stroke="currentColor"
        stroke-width="1.75"
        stroke-linejoin="round"
      />
    </svg>
    <span class="scrap-btn-count">{{ displayCount }}</span>
  </button>
</template>

<script>
import { formatLikeCount } from '../utils/formatLikeCount'

export default {
  name: 'ScrapButton',
  props: {
    scrapped: { type: Boolean, default: false },
    count: { type: Number, default: 0 },
  },
  emits: ['click'],
  computed: {
    displayCount() {
      return formatLikeCount(Number(this.count) || 0)
    },
  },
}
</script>

<style scoped>
.scrap-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 2px;
  border: none;
  background: transparent;
  color: var(--glt-ink-tertiary);
  cursor: pointer;
  transition: color var(--glt-duration), transform 0.15s var(--glt-ease);
}

.scrap-btn:hover {
  color: var(--glt-ink-secondary);
}

.scrap-btn.is-scrapped {
  color: #4a8e84;
}

.scrap-btn:active {
  transform: scale(0.96);
}

.scrap-btn-icon {
  width: 18px;
  height: 18px;
  display: block;
  flex-shrink: 0;
}

.scrap-btn-count {
  min-width: 1ch;
  font-size: 0.8rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  line-height: 1;
}
</style>
