<template>
  <article class="quote-item" :class="{ 'quote-item--compact': compact }">
    <router-link :to="`/quotes/${quote.id}`" class="quote-item-link">
      <blockquote class="quote-item-text">{{ quote.text }}</blockquote>
    </router-link>

    <div v-if="(quote.like_count || 0) > 0" class="quote-item-like">
      <LikeCount compact :count="quote.like_count || 0" />
    </div>

    <footer v-if="novelTitle || authorName" class="quote-item-meta">
      <span v-if="novelTitle" class="quote-item-book">{{ novelTitle }}</span>
      <span
        v-if="authorName"
        class="quote-item-author"
        :class="{ 'quote-item-author--sep': novelTitle }"
      >{{ authorName }}</span>
    </footer>
  </article>
</template>

<script>
import LikeCount from './LikeCount.vue'
import { quoteAuthorName, quoteSourceTitle } from '../utils/quoteDisplay'

export default {
  name: 'QuoteBrowseItem',
  components: { LikeCount },
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
  background: var(--glt-surface);
  border: 1px solid rgba(212, 195, 170, 0.42);
  border-radius: var(--glt-radius-lg);
  box-shadow: 0 2px 10px rgba(61, 52, 41, 0.04);
}

.quote-item-link {
  display: block;
  padding: 16px 18px 6px;
  text-decoration: none;
  color: inherit;
}

.quote-item--compact .quote-item-link {
  padding: 15px 16px 4px;
}

.quote-item-like {
  display: flex;
  justify-content: flex-end;
  padding: 0 14px 4px;
}

.quote-item--compact .quote-item-like {
  padding: 0 12px 2px;
}

.quote-item-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 10px;
  margin: 0 18px 14px;
  padding-top: 10px;
  border-top: 1px solid rgba(226, 213, 196, 0.65);
}

.quote-item--compact .quote-item-meta {
  margin: 0 16px 12px;
  padding-top: 9px;
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
</style>
