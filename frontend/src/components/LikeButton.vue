<template>
  <button
    type="button"
    class="like-btn"
    :class="{ 'is-liked': liked, 'like-btn--compact': compact }"
    :aria-label="liked ? '좋아요 취소' : '좋아요'"
    :aria-pressed="liked"
    @click.stop="$emit('click', $event)"
  >
    <svg class="like-btn-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M12 21l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.18L12 21z"
        :fill="liked ? 'currentColor' : 'none'"
        stroke="currentColor"
        stroke-width="1.75"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
    <span class="like-btn-count">{{ displayCount }}</span>
  </button>
</template>

<script>
import { formatLikeCount } from '../utils/formatLikeCount'

export default {
  name: 'LikeButton',
  props: {
    liked: { type: Boolean, default: false },
    count: { type: Number, default: 0 },
    compact: { type: Boolean, default: false },
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
.like-btn {
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

.like-btn:hover {
  color: var(--glt-ink-secondary);
}

.like-btn.is-liked {
  color: #e2556a;
}

.like-btn:active {
  transform: scale(0.96);
}

.like-btn-icon {
  width: 18px;
  height: 18px;
  display: block;
  flex-shrink: 0;
}

.like-btn-count {
  min-width: 1ch;
  font-size: 0.8rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  line-height: 1;
}

.like-btn--compact {
  gap: 4px;
  padding: 6px 4px;
  margin: -6px -4px;
  min-height: 36px;
}
</style>
