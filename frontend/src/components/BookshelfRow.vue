<template>
  <div class="bookshelf-row" :class="{ 'is-search-mode': searchMode }" :style="rowStyle">
    <div class="shelf-wall" aria-hidden="true" />

    <div
      class="shelf-books"
      :class="{
        'is-search': searchMode,
        'has-active': activeBookIndex !== null,
      }"
      :style="shelfBooksStyle"
    >
      <BookHub
        v-for="(book, i) in books"
        :key="book.id"
        :book="book"
        :book-index-in-row="i"
        :active-index-in-row="activeBookIndex"
        :color-index="startIndex + i"
        :pull-offset="pullOffset(i)"
        :force-expanded="forceExpanded"
        :search-mode="searchMode"
        @activate="onActivate"
        @deactivate="onDeactivate($event)"
        @show-detail="$emit('show-detail', $event)"
      />
    </div>

    <div class="shelf-plank" aria-hidden="true">
      <span class="plank-face" />
      <span class="plank-edge" />
    </div>
  </div>
</template>

<script>
import BookHub from './BookHub.vue'

const WOOD_TONES = [
  '#c4a882', '#b8956e', '#a88462', '#9a7a5c',
  '#8f7358', '#a68b6b', '#b59a78', '#9e8468',
]

export default {
  name: 'BookshelfRow',
  components: { BookHub },
  props: {
    books: { type: Array, required: true },
    startIndex: { type: Number, default: 0 },
    rowIndex: { type: Number, default: 0 },
    forceExpanded: { type: Boolean, default: false },
    searchMode: { type: Boolean, default: false },
  },
  emits: ['show-detail'],
  data() {
    return {
      activeBookIndex: null,
    }
  },
  computed: {
    rowStyle() {
      const tone = WOOD_TONES[this.rowIndex % WOOD_TONES.length]
      return {
        '--shelf-wood': tone,
        '--shelf-wood-dark': `color-mix(in srgb, ${tone} 72%, #5c4a38)`,
      }
    },
    shelfBooksStyle() {
      const count = this.books.length
      const activeQuotes = this.activeBookIndex !== null
        ? (this.books[this.activeBookIndex]?.quotes?.length || 1)
        : 0
      return {
        '--book-count': count,
        '--active-quote-count': activeQuotes,
      }
    },
  },
  watch: {
    forceExpanded(val) {
      if (!val) this.activeBookIndex = null
    },
  },
  methods: {
    pullOffset(i) {
      const pattern = [0, 8, 3, 10, 5, 7]
      return pattern[(this.startIndex + i) % pattern.length]
    },
    onActivate(index) {
      this.activeBookIndex = index
    },
    onDeactivate(index) {
      if (this.activeBookIndex === index) {
        this.activeBookIndex = null
      }
    },
  },
}
</script>

<style scoped>
.bookshelf-row {
  position: relative;
  padding: 0 4px 10px;
  overflow: visible;
}

.bookshelf-row:not(:first-child) {
  padding-top: 8px;
}

.bookshelf-row.is-search-mode {
  padding-top: 12px;
}

.shelf-wall {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 18px;
  z-index: 0;
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--shelf-wood) 8%, var(--glt-bg-subtle)) 0%,
    color-mix(in srgb, var(--shelf-wood) 14%, #ebe2d6) 100%
  );
  border-radius: 6px 6px 0 0;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.35);
}

.shelf-books {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: repeat(var(--book-count), minmax(0, 1fr));
  gap: 4px;
  padding: 12px 8px 0;
  min-height: calc(var(--glt-spine-height) + 28px);
  align-items: end;
  justify-items: center;
  overflow: visible;
  transition: padding-top 0.35s var(--glt-ease);
}

.shelf-books.has-active {
  padding-top: min(
    calc(48px + var(--active-quote-count) * 92px),
    52vh
  );
}

.shelf-books.is-search {
  padding-top: min(calc(80px + var(--book-count) * 100px), 60vh);
}

.shelf-plank {
  position: relative;
  z-index: 1;
  height: 16px;
  margin-top: -2px;
  pointer-events: none;
}

.plank-face {
  display: block;
  height: 12px;
  border-radius: 2px;
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--shelf-wood) 90%, #fff) 0%,
    var(--shelf-wood) 45%,
    var(--shelf-wood-dark) 100%
  );
  box-shadow:
    0 3px 8px rgba(61, 52, 41, 0.14),
    inset 0 1px 0 rgba(255, 255, 255, 0.45);
}

.plank-edge {
  display: block;
  height: 4px;
  border-radius: 0 0 3px 3px;
  background: var(--shelf-wood-dark);
  box-shadow: 0 4px 6px rgba(61, 52, 41, 0.12);
}
</style>
