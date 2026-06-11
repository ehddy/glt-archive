<template>
  <article
    class="book-stack"
    :class="{ 'is-expanded': isExpanded, 'is-search': searchMode }"
    :style="stackStyle"
    @mouseenter="onEnter"
    @mouseleave="onLeave"
  >
    <button
      type="button"
      class="stack-bar"
      :class="{ 'is-lifted': isExpanded }"
      @click="onBookClick"
    >
      <div class="book-spine" aria-hidden="true">
        <span class="spine-line" />
        <span class="spine-line spine-line--short" />
      </div>

      <div class="book-face">
        <img
          v-if="book.cover_url"
          :src="book.cover_url"
          :alt="`${book.title} 표지`"
          class="stack-thumb"
        />
        <div v-else class="stack-thumb stack-thumb--empty">📖</div>

        <div class="stack-text">
          <span class="stack-title">{{ book.title }}</span>
          <span v-if="authorName" class="stack-author">{{ authorName }}</span>
        </div>
      </div>

      <span v-if="book.quotes.length" class="stack-count">{{ book.quotes.length }}</span>
    </button>

    <div
      v-if="book.quotes.length"
      class="quote-bubbles"
      :aria-hidden="!isExpanded"
      @mouseenter="onEnter"
      @mouseleave="onLeave"
      @click.stop
    >
      <div
        v-for="(quote, i) in book.quotes"
        :key="quote.id"
        class="quote-bubble-wrap"
        :style="{ '--i': i }"
      >
        <QuoteBranch
          :quote="quote"
          variant="shelf"
          tail-direction="left"
          :highlighted="searchMode"
        />
      </div>
    </div>
  </article>
</template>

<script>
import QuoteBranch from './QuoteBranch.vue'

const HUB_COLORS = [
  '#e8a598', '#d4897a', '#c4693a', '#b8956e',
  '#a8b89a', '#8faf9c', '#9cb0bc', '#c9a8b8',
]

export default {
  name: 'BookStack',
  components: { QuoteBranch },
  props: {
    book: { type: Object, required: true },
    stackIndex: { type: Number, default: 0 },
    colorIndex: { type: Number, default: 0 },
    forceExpanded: { type: Boolean, default: false },
    searchMode: { type: Boolean, default: false },
  },
  emits: ['show-detail'],
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
    stackColor() {
      return HUB_COLORS[this.colorIndex % HUB_COLORS.length]
    },
    stackStyle() {
      const stagger = (this.stackIndex % 5) * 5 - 10
      const width = 94 - (this.stackIndex % 3) * 3
      return {
        '--stack-color': this.stackColor,
        '--stack-z': this.stackIndex + 1,
        '--stack-shift': `${stagger}px`,
        '--stack-width': `${width}%`,
      }
    },
    isExpanded() {
      return this.forceExpanded || this.isHovered
    },
  },
  beforeUnmount() {
    clearTimeout(this.leaveTimer)
  },
  methods: {
    onEnter() {
      clearTimeout(this.leaveTimer)
      this.isHovered = true
    },
    onLeave() {
      this.leaveTimer = setTimeout(() => {
        this.isHovered = false
      }, 200)
    },
    onBookClick() {
      if (typeof this.book.id === 'number') {
        this.$emit('show-detail', this.book.id)
      }
    },
  },
}
</script>

<style scoped>
.book-stack {
  position: relative;
  width: var(--stack-width, 96%);
  max-width: 340px;
  z-index: var(--stack-z, 1);
  margin-left: var(--stack-shift, 0);
  margin-top: -5px;
}

.book-stack:first-child {
  margin-top: 0;
}

.book-stack.is-expanded {
  z-index: 100;
}

.stack-bar {
  width: 100%;
  min-height: 48px;
  padding: 0;
  display: flex;
  align-items: stretch;
  gap: 0;
  border: none;
  border-radius: 6px 14px 14px 6px;
  cursor: pointer;
  text-align: left;
  background: color-mix(in srgb, var(--stack-color) 88%, #fff);
  border: 1px solid color-mix(in srgb, var(--stack-color) 50%, #c4b5a5);
  box-shadow:
    0 2px 6px rgba(61, 52, 41, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.45);
  transition:
    transform 0.28s var(--glt-ease),
    box-shadow 0.28s var(--glt-ease);
  overflow: hidden;
}

.stack-bar.is-lifted,
.stack-bar:hover {
  transform: translateY(-2px) scale(1.01);
  box-shadow:
    0 6px 16px rgba(61, 52, 41, 0.14),
    inset 0 1px 0 rgba(255, 255, 255, 0.5);
}

.book-spine {
  width: 12px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 4px;
  background: color-mix(in srgb, var(--stack-color) 75%, #5c4a38);
  border-right: 1px solid color-mix(in srgb, var(--stack-color) 60%, #fff);
}

.spine-line {
  width: 5px;
  height: 2px;
  border-radius: 1px;
  background: rgba(255, 255, 255, 0.35);
}

.spine-line--short {
  width: 3px;
}

.book-face {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px 8px 8px;
}

.stack-thumb {
  width: 28px;
  height: 38px;
  flex-shrink: 0;
  object-fit: cover;
  border-radius: 3px 5px 5px 3px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}

.stack-thumb--empty {
  display: grid;
  place-items: center;
  background: rgba(255, 255, 255, 0.45);
  font-size: 0.95rem;
}

.stack-text {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stack-title {
  font-size: 0.88rem;
  font-weight: 700;
  line-height: 1.35;
  color: var(--glt-ink);
  word-break: keep-all;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.stack-author {
  font-size: 0.74rem;
  color: var(--glt-ink-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stack-count {
  flex-shrink: 0;
  align-self: center;
  margin-right: 10px;
  min-width: 22px;
  height: 22px;
  padding: 0 6px;
  display: grid;
  place-items: center;
  border-radius: var(--glt-radius-full);
  font-size: 0.72rem;
  font-weight: 700;
  color: #fff;
  background: color-mix(in srgb, var(--stack-color) 75%, #5c4a38);
}

.quote-bubbles {
  position: absolute;
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  width: min(var(--glt-bubble-shelf-width), 72vw);
  max-height: min(360px, 65vh);
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  padding: 8px 4px 8px 20px;
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  transition:
    opacity 0.22s var(--glt-ease),
    transform 0.28s var(--glt-ease),
    visibility 0.22s;
}

.book-stack.is-expanded .quote-bubbles {
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
  transform: translateY(-50%) translateX(0);
}

.quote-bubble-wrap {
  animation: bubble-in 0.3s var(--glt-ease) both;
  animation-delay: calc(var(--i) * 0.05s);
}

@keyframes bubble-in {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.book-stack.is-search .quote-bubbles {
  max-height: min(400px, 70vh);
}

@media (max-width: 640px) {
  .quote-bubbles {
    width: min(200px, 58vw);
    padding-left: 14px;
  }
}
</style>
