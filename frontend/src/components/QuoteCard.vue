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
      return this.quote.author?.name || this.quote.novel?.author?.name || ''
    },
    novelTitle() {
      return this.quote.novel?.title || ''
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
