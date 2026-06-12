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
        d="M12 20.2l-1-1C6.2 14.8 4 12.6 4 10a4 4 0 0 1 7-2.4A4 4 0 0 1 20 10c0 2.6-2.2 4.8-7 9.2l-1 1z"
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
