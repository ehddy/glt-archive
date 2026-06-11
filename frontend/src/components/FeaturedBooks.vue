<template>
  <section v-if="books.length" class="featured">
    <header class="featured-head">
      <div class="featured-head-left">
        <h2 class="featured-title">대표 작품</h2>
        <span v-if="stats" class="featured-stats">{{ stats.total_books }}권 · {{ stats.total_quotes }}구절</span>
      </div>
      <router-link to="/novels" class="featured-more">전체 보기</router-link>
    </header>

    <div class="featured-scroll">
      <article
        v-for="book in books"
        :key="book.id"
        class="featured-card"
      >
        <router-link :to="`/novels/${book.id}`" class="featured-cover-btn">
          <img
            v-if="book.cover_url"
            :src="book.cover_url"
            :alt="book.title"
            class="featured-cover"
          />
          <div v-else class="featured-cover featured-cover--empty">📖</div>
        </router-link>

        <div class="featured-meta">
          <button
            type="button"
            class="featured-book-title"
            :class="{ 'is-expanded': expandedId === book.id }"
            :title="expandedId === book.id ? '' : book.title"
            @click="toggleTitle(book.id)"
          >
            {{ book.title }}
          </button>
          <span v-if="book.author" class="featured-author">{{ book.author.name }}</span>
        </div>
      </article>
    </div>
  </section>
</template>

<script>
export default {
  name: 'FeaturedBooks',
  props: {
    books: { type: Array, required: true },
    stats: { type: Object, default: null },
  },
  data() {
    return {
      expandedId: null,
    }
  },
  methods: {
    toggleTitle(bookId) {
      this.expandedId = this.expandedId === bookId ? null : bookId
    },
  },
}
</script>

<style scoped>
.featured {
  margin-top: var(--glt-space-6);
}

.featured-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--glt-space-3);
  margin-bottom: var(--glt-space-3);
}

.featured-head-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.featured-more {
  flex-shrink: 0;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--glt-accent-hover);
  text-decoration: none;
  padding-top: 2px;
}

.featured-more:hover {
  text-decoration: underline;
}

.featured-title {
  margin: 0;
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--glt-ink-secondary);
}

.featured-stats {
  font-size: 0.78rem;
  color: var(--glt-ink-tertiary);
}

.featured-scroll {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: thin;
  align-items: flex-start;
}

.featured-card {
  flex: 0 0 108px;
  width: 108px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.featured-cover-btn {
  display: block;
  width: 108px;
  height: 148px;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 6px;
  text-decoration: none;
}

.featured-cover {
  width: 108px;
  height: 148px;
  object-fit: cover;
  border-radius: 6px;
  box-shadow: var(--glt-shadow-sm);
  transition: transform 0.2s var(--glt-ease), box-shadow 0.2s var(--glt-ease);
  display: block;
}

.featured-cover-btn:hover .featured-cover {
  transform: translateY(-3px);
  box-shadow: var(--glt-shadow-md);
}

.featured-cover--empty {
  display: grid;
  place-items: center;
  background: var(--glt-bg-subtle);
  font-size: 1.4rem;
}

.featured-meta {
  width: 108px;
  min-height: 2.2em;
}

.featured-book-title {
  display: block;
  width: 100%;
  margin: 0;
  padding: 0;
  border: none;
  background: transparent;
  font-size: 0.78rem;
  font-weight: 600;
  line-height: 1.35;
  color: var(--glt-ink);
  text-align: left;
  cursor: pointer;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  word-break: keep-all;
}

.featured-book-title:hover {
  color: var(--glt-accent-hover);
}

.featured-book-title.is-expanded {
  white-space: normal;
  overflow: visible;
  text-overflow: unset;
  word-break: keep-all;
  overflow-wrap: anywhere;
  background: var(--glt-surface);
  border-radius: 6px;
  padding: 6px 8px;
  box-shadow: var(--glt-shadow-sm);
  border: 1px solid var(--glt-glass-border);
}

.featured-author {
  display: block;
  margin-top: 4px;
  font-size: 0.72rem;
  color: var(--glt-ink-tertiary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
