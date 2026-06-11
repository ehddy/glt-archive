<template>
  <div class="book-node" :style="spineStyle">
    <div class="book-spine" :style="{ background: color }" />
    <div class="book-cover">
      <div class="book-pages" />
      <div class="book-content">
        <span class="book-label">작품</span>
        <h3 class="book-title">{{ title }}</h3>
        <p v-if="author" class="book-author">{{ author }}</p>
        <span class="book-count">{{ quoteCount }}개 구절</span>
      </div>
    </div>
    <div class="book-node-port" />
  </div>
</template>

<script>
const BOOK_COLORS = [
  'var(--glt-book-0)',
  'var(--glt-book-1)',
  'var(--glt-book-2)',
  'var(--glt-book-3)',
  'var(--glt-book-4)',
  'var(--glt-book-5)',
  'var(--glt-book-6)',
  'var(--glt-book-7)',
]

export default {
  name: 'BookNode',
  props: {
    title: { type: String, required: true },
    author: { type: String, default: '' },
    quoteCount: { type: Number, default: 0 },
    colorIndex: { type: Number, default: 0 },
  },
  computed: {
    color() {
      return BOOK_COLORS[this.colorIndex % BOOK_COLORS.length]
    },
    spineStyle() {
      return { '--book-color': this.color }
    },
  },
}
</script>

<style scoped>
.book-node {
  position: relative;
  width: var(--glt-book-width);
  flex-shrink: 0;
}

.book-cover {
  position: relative;
  background: var(--glt-surface);
  border: 1px solid var(--glt-line);
  border-radius: var(--glt-radius-md) var(--glt-radius-lg) var(--glt-radius-lg) var(--glt-radius-md);
  box-shadow: var(--glt-shadow-book);
  overflow: hidden;
  transition: transform var(--glt-duration) var(--glt-ease), box-shadow var(--glt-duration);
}

.book-node:hover .book-cover {
  transform: translateY(-2px);
  box-shadow: var(--glt-shadow-lg);
}

.book-spine {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 10px;
  z-index: 2;
}

.book-pages {
  position: absolute;
  right: -3px;
  top: 6px;
  bottom: 6px;
  width: 6px;
  background: repeating-linear-gradient(
    to bottom,
    #f0ebe0 0px,
    #f0ebe0 2px,
    #e8e2d6 2px,
    #e8e2d6 4px
  );
  border-radius: 0 2px 2px 0;
}

.book-content {
  padding: var(--glt-space-5) var(--glt-space-4) var(--glt-space-5) var(--glt-space-6);
  min-height: 140px;
  display: flex;
  flex-direction: column;
}

.book-label {
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--glt-ink-tertiary);
  margin-bottom: var(--glt-space-2);
}

.book-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.35;
  letter-spacing: -0.02em;
  color: var(--glt-ink);
  word-break: keep-all;
}

.book-author {
  margin: var(--glt-space-2) 0 0;
  font-size: 0.8rem;
  color: var(--glt-ink-secondary);
}

.book-count {
  margin-top: auto;
  padding-top: var(--glt-space-4);
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--book-color);
}

.book-node-port {
  position: absolute;
  right: -1px;
  top: 50%;
  transform: translate(50%, -50%);
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--glt-surface-raised);
  border: 2px solid var(--glt-line-active);
  box-shadow: 0 0 0 4px var(--glt-node-glow);
  z-index: 3;
}
</style>
