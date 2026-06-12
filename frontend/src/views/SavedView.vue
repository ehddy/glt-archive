<template>
  <section class="saved glt-container">
    <h1 class="glt-title">{{ COLLECT.pageTitle }}</h1>

    <div v-if="loading" class="glt-empty">불러오는 중…</div>
    <div v-else-if="error" class="glt-empty">{{ error }}</div>
    <div v-else-if="!quotes.length" class="glt-empty glt-card">{{ COLLECT.empty }}</div>

    <SourceSearchResults
      v-else
      :results="resultItems"
      :bookmark-ids="bookmarkIds"
      @toggle-bookmark="toggleBookmark"
    />
  </section>
</template>

<script>
import { api } from '../api'
import SourceSearchResults from '../components/SourceSearchResults.vue'
import { COLLECT } from '../utils/collectLabels'

export default {
  name: 'SavedView',
  components: { SourceSearchResults },
  data() {
    return {
      COLLECT,
      quotes: [],
      bookmarkIds: new Set(),
      loading: true,
      error: '',
    }
  },
  computed: {
    resultItems() {
      return this.quotes.map((quote) => ({
        quote,
        score: 1,
        match_type: 'bookmark',
      }))
    },
  },
  mounted() {
    this.load()
  },
  methods: {
    async load() {
      this.loading = true
      this.error = ''
      try {
        const [quotes, idsRes] = await Promise.all([
          api.listBookmarks(),
          api.getBookmarkIds(),
        ])
        this.quotes = quotes
        this.bookmarkIds = new Set(idsRes.quote_ids || [])
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    },
    async toggleBookmark(quoteId) {
      try {
        if (this.bookmarkIds.has(quoteId)) {
          await api.removeBookmark(quoteId)
          this.bookmarkIds.delete(quoteId)
          this.quotes = this.quotes.filter((q) => q.id !== quoteId)
        } else {
          await api.addBookmark(quoteId)
          this.bookmarkIds.add(quoteId)
        }
        this.bookmarkIds = new Set(this.bookmarkIds)
      } catch (e) {
        this.error = e.message
      }
    },
  },
}
</script>

<style scoped>
.saved .glt-title {
  margin-bottom: var(--glt-space-3);
}
</style>
