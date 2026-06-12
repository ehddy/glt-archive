<template>
  <article class="quote-card card card-hover">
    <router-link :to="`/quotes/${quote.id}`" class="quote-link">
      <p class="quote-body">{{ quote.text }}</p>
      <div class="meta-row">
        <span v-if="authorName" class="chip">{{ authorName }}</span>
        <span v-if="novelTitle" class="chip chip-accent">{{ novelTitle }}</span>
      </div>
    </router-link>
  </article>
</template>

<script>
import { quoteAuthorName, quoteSourceTitle } from '../utils/quoteDisplay'

export default {
  name: 'QuoteCard',
  props: {
    quote: {
      type: Object,
      required: true,
    },
  },
  computed: {
    authorName() {
      return quoteAuthorName(this.quote)
    },
    novelTitle() {
      return quoteSourceTitle(this.quote)
    },
  },
}
</script>

<style scoped>
.quote-card {
  padding: 20px;
}

.quote-link {
  display: block;
}

.quote-body {
  margin-bottom: 14px;
}

.meta-row {
  gap: 6px;
}
</style>
