<template>
  <div class="book-hub" :style="{ '--hub-color': hubColor }">
    <BookNode
      :title="book.title"
      :author="authorName"
      :quote-count="book.quotes.length"
      :color-index="colorIndex"
    />

    <div ref="graphEl" class="hub-graph">
      <svg
        v-if="lines.length"
        class="hub-lines"
        :viewBox="`0 0 ${svgWidth} ${svgHeight}`"
        preserveAspectRatio="none"
      >
        <path
          v-for="(line, i) in lines"
          :key="i"
          :d="line"
          class="hub-line"
          fill="none"
        />
      </svg>

      <div ref="branchesEl" class="hub-branches">
        <div
          v-for="quote in book.quotes"
          :key="quote.id"
          class="hub-branch"
        >
          <QuoteBranch :quote="quote" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import BookNode from './BookNode.vue'
import QuoteBranch from './QuoteBranch.vue'

const BOOK_COLORS = [
  '#8b3a3a', '#2d4a3e', '#4a6741', '#6b4c35',
  '#3d4f6b', '#7a5c3e', '#5c3d5e', '#8b6914',
]

export default {
  name: 'BookHub',
  components: { BookNode, QuoteBranch },
  props: {
    book: { type: Object, required: true },
    colorIndex: { type: Number, default: 0 },
  },
  data() {
    return {
      lines: [],
      svgWidth: 300,
      svgHeight: 200,
      resizeObserver: null,
    }
  },
  computed: {
    authorName() {
      return this.book.author?.name || ''
    },
    hubColor() {
      return BOOK_COLORS[this.colorIndex % BOOK_COLORS.length]
    },
  },
  mounted() {
    this.$nextTick(() => {
      this.drawLines()
      const target = this.$refs.graphEl
      if (target && typeof ResizeObserver !== 'undefined') {
        this.resizeObserver = new ResizeObserver(() => this.drawLines())
        this.resizeObserver.observe(target)
      }
    })
    window.addEventListener('resize', this.drawLines)
  },
  beforeUnmount() {
    this.resizeObserver?.disconnect()
    window.removeEventListener('resize', this.drawLines)
  },
  methods: {
    drawLines() {
      const branches = this.$refs.branchesEl
      const graph = this.$refs.graphEl
      if (!branches || !graph) return

      const items = branches.querySelectorAll('.hub-branch')
      if (!items.length) {
        if (this.lines.length) this.lines = []
        return
      }

      const graphRect = graph.getBoundingClientRect()
      if (graphRect.width === 0 || graphRect.height === 0) return

      const startX = 0
      const startY = graphRect.height / 2
      const endX = 28

      const newWidth = Math.round(graphRect.width)
      const newHeight = Math.round(graphRect.height)
      const newLines = Array.from(items).map((item) => {
        const rect = item.getBoundingClientRect()
        const endY = rect.top - graphRect.top + rect.height / 2
        const midX = endX + (graphRect.width - endX) * 0.25
        return `M ${startX} ${startY} C ${midX} ${startY}, ${midX} ${endY}, ${endX} ${endY}`
      })

      const sameSize = newWidth === this.svgWidth && newHeight === this.svgHeight
      const sameLines = sameSize
        && newLines.length === this.lines.length
        && newLines.every((l, i) => l === this.lines[i])

      if (sameLines) return

      this.svgWidth = newWidth
      this.svgHeight = newHeight
      this.lines = newLines
    },
  },
}
</script>

<style scoped>
.book-hub {
  display: flex;
  align-items: stretch;
  gap: 0;
  padding: var(--glt-space-6) 0;
}

.hub-graph {
  position: relative;
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: stretch;
}

.hub-lines {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.hub-line {
  stroke: var(--glt-line);
  stroke-width: 1.5;
  transition: stroke var(--glt-duration);
}

.book-hub:hover .hub-line {
  stroke: var(--hub-color);
  stroke-opacity: 0.45;
}

.hub-branches {
  position: relative;
  z-index: 1;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: var(--glt-branch-gap);
  padding: var(--glt-space-2) 0 var(--glt-space-2) var(--glt-space-8);
}

.hub-branch {
  position: relative;
}

.hub-branch::before {
  content: '';
  position: absolute;
  left: -20px;
  top: 50%;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--glt-surface-raised);
  border: 2px solid var(--glt-line);
  transform: translate(-50%, -50%);
  transition: border-color var(--glt-duration), background var(--glt-duration);
  z-index: 2;
}

.book-hub:hover .hub-branch::before {
  border-color: var(--hub-color);
  background: var(--glt-accent-soft);
}

@media (max-width: 720px) {
  .book-hub {
    flex-direction: column;
    align-items: center;
    gap: var(--glt-space-4);
  }

  .hub-graph {
    width: 100%;
  }

  .hub-lines {
    display: none;
  }

  .hub-branches {
    padding-left: 0;
    border-left: 2px solid var(--glt-line);
    margin-left: var(--glt-space-4);
    padding-left: var(--glt-space-5);
  }

  .hub-branch::before {
    left: calc(-1 * var(--glt-space-5) - 1px);
  }
}
</style>
