<template>
  <article
    class="shelf-book"
    :class="{
      'is-expanded': isExpanded,
      'is-search': searchMode,
      'is-active': isActiveInRow,
    }"
    :style="bookStyle"
    @mouseenter="onEnter"
    @mouseleave="onLeave"
  >
    <div
      v-if="book.quotes.length"
      class="quote-spread"
      :aria-hidden="!isExpanded"
      @mouseenter="onEnter"
      @mouseleave="onLeave"
      @click.stop
    >
      <div class="quote-spread-inner">
        <QuoteBranch
          v-for="(quote, i) in book.quotes"
          :key="quote.id"
          :quote="quote"
          variant="spread"
          :highlighted="searchMode"
          :style="{ '--quote-i': i }"
        />
      </div>
    </div>

    <div class="book-open-wrap" :class="{ 'is-open': isExpanded }">
      <span class="book-flap book-flap--left" aria-hidden="true" />
      <BookNode
        :class="{ 'is-pulled': isExpanded }"
        :title="book.title"
        :author="authorName"
        :quote-count="book.quotes.length"
        :color-index="colorIndex"
        variant="spine"
        show-count
        @click="onBookClick"
      />
      <span class="book-flap book-flap--right" aria-hidden="true" />
    </div>

    <div class="shelf-slot" :class="{ 'is-open': isExpanded }" aria-hidden="true" />
  </article>
</template>

<script>
import BookNode from './BookNode.vue'
import QuoteBranch from './QuoteBranch.vue'

const HUB_COLORS = [
  '#c4693a', '#7d8f6a', '#c97b84', '#c9a227',
  '#6b8f9c', '#a67c6d', '#8b7d6b', '#b5836e',
]

const SPREAD_STEP = 32

export default {
  name: 'BookHub',
  components: { BookNode, QuoteBranch },
  props: {
    book: { type: Object, required: true },
    colorIndex: { type: Number, default: 0 },
    bookIndexInRow: { type: Number, default: 0 },
    activeIndexInRow: { type: Number, default: null },
    pullOffset: { type: Number, default: 0 },
    forceExpanded: { type: Boolean, default: false },
    searchMode: { type: Boolean, default: false },
  },
  emits: ['show-detail', 'activate', 'deactivate'],
  data() {
    return {
      isHovered: false,
      leaveTimer: null,
    }
  },
  computed: {
    authorName() {
      return this.book.author?.name || ''
    },
    hubColor() {
      return HUB_COLORS[this.colorIndex % HUB_COLORS.length]
    },
    isActiveInRow() {
      return this.activeIndexInRow === this.bookIndexInRow
    },
    spreadX() {
      if (this.forceExpanded || this.activeIndexInRow === null) return 0
      const active = this.activeIndexInRow
      const idx = this.bookIndexInRow
      if (idx === active) return 0
      if (idx < active) return -SPREAD_STEP * (active - idx)
      return SPREAD_STEP * (idx - active)
    },
    bookStyle() {
      return {
        '--hub-color': this.hubColor,
        '--pull-shift': `${this.pullOffset * 0.35}px`,
        '--spread-x': `${this.spreadX}px`,
        '--quote-count': this.book.quotes.length,
      }
    },
    isExpanded() {
      return this.forceExpanded || this.isHovered
    },
  },
  watch: {
    isHovered(val) {
      if (this.forceExpanded) return
      if (val) {
        this.$emit('activate', this.bookIndexInRow)
      }
    },
  },
  beforeUnmount() {
    clearTimeout(this.leaveTimer)
    if (this.isHovered) {
      this.$emit('deactivate', this.bookIndexInRow)
    }
  },
  methods: {
    onEnter() {
      clearTimeout(this.leaveTimer)
      this.isHovered = true
      if (!this.forceExpanded) {
        this.$emit('activate', this.bookIndexInRow)
      }
    },
    onLeave() {
      this.leaveTimer = setTimeout(() => {
        this.isHovered = false
        if (!this.forceExpanded) {
          this.$emit('deactivate', this.bookIndexInRow)
        }
      }, 200)
    },
    onBookClick(event) {
      if (event.target.closest('.quote-bubble')) return
      if (typeof this.book.id === 'number') {
        this.$emit('show-detail', this.book.id)
      }
    },
  },
}
</script>

<style scoped>
.shelf-book {
  position: relative;
  width: 100%;
  max-width: var(--glt-spine-width);
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 1;
  transform: translateX(var(--spread-x, 0));
  transition:
    transform 0.4s var(--glt-ease),
    z-index 0s;
}

.shelf-book.is-active {
  z-index: 60;
}

.shelf-book.is-expanded:not(.is-active) {
  z-index: 10;
}

.shelf-book :deep(.book-node) {
  cursor: pointer;
}

.book-open-wrap {
  position: relative;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  transform-origin: center bottom;
  transition: transform 0.38s var(--glt-ease);
}

.book-open-wrap.is-open {
  transform: translateY(calc(-10px - var(--pull-shift))) scale(1.04);
}

.book-flap {
  position: absolute;
  bottom: 0;
  width: 10px;
  height: calc(var(--glt-spine-height) - 8px);
  background: color-mix(in srgb, var(--hub-color) 88%, #fff);
  border: 1px solid color-mix(in srgb, var(--hub-color) 55%, #5c4a38);
  border-radius: 3px;
  opacity: 0;
  transition:
    opacity 0.32s var(--glt-ease),
    transform 0.38s var(--glt-ease);
  pointer-events: none;
  z-index: 0;
}

.book-flap--left {
  left: -6px;
  transform-origin: right bottom;
}

.book-flap--right {
  right: -6px;
  transform-origin: left bottom;
}

.book-open-wrap.is-open .book-flap {
  opacity: 0.92;
}

.book-open-wrap.is-open .book-flap--left {
  transform: rotateY(-28deg) translateX(-4px);
}

.book-open-wrap.is-open .book-flap--right {
  transform: rotateY(28deg) translateX(4px);
}

.quote-spread {
  position: absolute;
  left: 50%;
  bottom: calc(100% + 12px);
  transform: translateX(-50%);
  width: max(var(--glt-spine-width), 240px);
  max-width: min(300px, 42vw);
  z-index: 80;
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  transition:
    opacity 0.28s var(--glt-ease),
    visibility 0.28s,
    transform 0.35s var(--glt-ease);
}

.shelf-book.is-expanded .quote-spread {
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
  transform: translateX(-50%) translateY(-4px);
}

.quote-spread-inner {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: min(calc(36px + var(--quote-count) * 88px), 50vh);
  overflow-y: auto;
  padding: 4px 2px;
  scrollbar-width: thin;
}

.quote-spread-inner :deep(.quote-bubble) {
  animation: quote-rise 0.32s var(--glt-ease) both;
  animation-delay: calc(var(--quote-i, 0) * 0.05s);
}

@keyframes quote-rise {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.shelf-slot {
  width: calc(var(--glt-spine-width) + 6px);
  height: 8px;
  margin-top: -4px;
  border-radius: 2px 2px 0 0;
  background: color-mix(in srgb, var(--hub-color) 25%, #3d3429);
  opacity: 0.35;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.15);
  transition: width 0.35s var(--glt-ease);
}

.shelf-slot.is-open {
  width: calc(var(--glt-spine-width) + 22px);
  opacity: 0.5;
}
</style>
