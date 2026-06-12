<template>
  <span v-if="count > 0" class="like-count" :class="{ 'like-count--compact': compact }">
    <svg class="like-count-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M12 20.2l-1-1C6.2 14.8 4 12.6 4 10a4 4 0 0 1 7-2.4A4 4 0 0 1 20 10c0 2.6-2.2 4.8-7 9.2l-1 1z"
        fill="currentColor"
        stroke="currentColor"
        stroke-width="1.75"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
    <span class="like-count-num">{{ displayCount }}</span>
  </span>
</template>

<script>
import { formatLikeCount } from '../utils/formatLikeCount'

export default {
  name: 'LikeCount',
  props: {
    count: { type: Number, default: 0 },
    compact: { type: Boolean, default: false },
  },
  computed: {
    displayCount() {
      return formatLikeCount(Number(this.count) || 0)
    },
  },
}
</script>

<style scoped>
.like-count {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: #e2556a;
}

.like-count--compact {
  gap: 4px;
}

.like-count-icon {
  width: 18px;
  height: 18px;
  display: block;
  flex-shrink: 0;
}

.like-count-num {
  min-width: 1ch;
  font-size: 0.8rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  line-height: 1;
}
</style>
