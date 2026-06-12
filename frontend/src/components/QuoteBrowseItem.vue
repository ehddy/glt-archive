<template>
  <router-link :to="`/quotes/${quote.id}`" class="quote-item" :class="{ 'quote-item--compact': compact }">
    <blockquote class="quote-item-text">{{ quote.text }}</blockquote>
    <footer v-if="novelTitle || authorName" class="quote-item-meta">
      <span v-if="novelTitle" class="quote-item-book">{{ novelTitle }}</span>
      <span
        v-if="authorName"
        class="quote-item-author"
        :class="{ 'quote-item-author--sep': novelTitle }"
      >{{ authorName }}</span>
    </footer>
  </router-link>
</template>

<script>
import { quoteAuthorName, quoteSourceTitle } from '../utils/quoteDisplay'

export default {
  name: 'QuoteBrowseItem',
  props: {
    quote: { type: Object, required: true },
    compact: { type: Boolean, default: false },
  },
  computed: {
    novelTitle() {
      return quoteSourceTitle(this.quote)
    },
    authorName() {
      return quoteAuthorName(this.quote)
    },
  },
}
</script>

<style scoped>
.quote-item {
  display: block;
  padding: 16px 18px;
  text-decoration: none;
  color: inherit;
  background: var(--glt-surface);
  border: 1px solid rgba(212, 195, 170, 0.42);
  border-radius: var(--glt-radius-lg);
  box-shadow: 0 2px 10px rgba(61, 52, 41, 0.04);
  transition:
    transform var(--glt-duration) var(--glt-ease),
    box-shadow var(--glt-duration) var(--glt-ease),
    border-color var(--glt-duration) var(--glt-ease);
}

.quote-item:hover {
  transform: translateY(-1px);
  border-color: rgba(196, 105, 58, 0.22);
  box-shadow: 0 6px 18px rgba(61, 52, 41, 0.07);
}

.quote-item:focus-visible {
  outline: 2px solid var(--glt-accent-muted);
  outline-offset: 2px;
}

.quote-item--compact {
  padding: 15px 16px;
}

.quote-item-text {
  margin: 0;
  padding: 0;
  border: none;
  font-family: var(--glt-font-serif);
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.78;
  letter-spacing: -0.01em;
  color: var(--glt-ink);
  word-break: keep-all;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.quote-item--compact .quote-item-text {
  font-size: 0.94rem;
  line-height: 1.72;
  -webkit-line-clamp: 3;
}

.quote-item-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 10px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(226, 213, 196, 0.65);
}

.quote-item-book {
  font-size: 0.76rem;
  font-weight: 600;
  color: var(--glt-ink-secondary);
  letter-spacing: -0.01em;
}

.quote-item-author {
  font-size: 0.74rem;
  color: var(--glt-ink-tertiary);
}

.quote-item-author--sep::before {
  content: '·';
  margin-right: 10px;
  color: var(--glt-ink-faint);
}
</style>
