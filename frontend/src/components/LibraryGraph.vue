<template>
  <div ref="wrapEl" class="library-shelf-wrap" :class="{ 'is-search': expandAll }">
    <BookshelfRow
      v-for="(row, ri) in shelfRows"
      :key="`row-${ri}`"
      :books="row"
      :start-index="rowStartIndex(ri)"
      :row-index="ri"
      :force-expanded="expandAll"
      :search-mode="expandAll"
      @show-detail="detailNovelId = $event"
    />

    <BookDetailModal
      v-if="detailNovelId"
      :novel-id="detailNovelId"
      @close="detailNovelId = null"
    />
  </div>
</template>

<script>
import BookshelfRow from './BookshelfRow.vue'
import BookDetailModal from './BookDetailModal.vue'

const SPINE_SLOT = 100

export default {
  name: 'LibraryGraph',
  components: { BookshelfRow, BookDetailModal },
  props: {
    books: { type: Array, required: true },
    expandAll: { type: Boolean, default: false },
  },
  data() {
    return {
      detailNovelId: null,
      shelfWidth: 900,
      resizeObserver: null,
    }
  },
  computed: {
    booksPerRow() {
      const per = Math.floor((this.shelfWidth - 32) / SPINE_SLOT)
      return Math.max(3, Math.min(8, per))
    },
    shelfRows() {
      const rows = []
      const size = this.booksPerRow
      for (let i = 0; i < this.books.length; i += size) {
        rows.push(this.books.slice(i, i + size))
      }
      return rows
    },
  },
  mounted() {
    this.updateWidth()
    const target = this.$refs.wrapEl
    if (target && typeof ResizeObserver !== 'undefined') {
      this.resizeObserver = new ResizeObserver(() => this.updateWidth())
      this.resizeObserver.observe(target)
    }
    window.addEventListener('resize', this.updateWidth)
  },
  beforeUnmount() {
    this.resizeObserver?.disconnect()
    window.removeEventListener('resize', this.updateWidth)
  },
  methods: {
    updateWidth() {
      this.shelfWidth = this.$refs.wrapEl?.clientWidth || 900
    },
    rowStartIndex(rowIndex) {
      return rowIndex * this.booksPerRow
    },
  },
}
</script>

<style scoped>
.library-shelf-wrap {
  padding: var(--glt-space-4) var(--glt-space-2) var(--glt-space-6);
  overflow: visible;
}

.library-shelf-wrap.is-search {
  padding-top: var(--glt-space-2);
}
</style>
