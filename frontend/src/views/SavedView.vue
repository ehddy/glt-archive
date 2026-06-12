<template>
  <section class="saved glt-container">
    <h1 class="glt-title">{{ COLLECT.pageTitle }}</h1>

    <div v-if="error && !loading" class="glt-empty">{{ error }}</div>
    <div v-else-if="!loading && !quotes.length" class="glt-empty glt-card">{{ COLLECT.empty }}</div>

    <SavedQuoteList
      v-else-if="!loading"
      :quotes="quotes"
      @remove="removeBookmark"
    />
  </section>
</template>

<script>
import { api } from '../api'
import SavedQuoteList from '../components/SavedQuoteList.vue'
import { COLLECT } from '../utils/collectLabels'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'

export default {
  name: 'SavedView',
  components: { SavedQuoteList },
  data() {
    return {
      COLLECT,
      quotes: [],
      loading: true,
      error: '',
    }
  },
  mounted() {
    this.load()
  },
  methods: {
    async load() {
      this.loading = true
      startPageLoading()
      this.error = ''
      try {
        this.quotes = await api.listBookmarks()
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
        endPageLoading()
      }
    },
    async removeBookmark(quoteId) {
      try {
        await api.removeBookmark(quoteId)
        this.quotes = this.quotes.filter((q) => q.id !== quoteId)
      } catch (e) {
        this.error = e.message
      }
    },
  },
}
</script>

<style scoped>
.saved .glt-title {
  margin-bottom: var(--glt-space-2);
}
</style>
