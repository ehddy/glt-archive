<template>
  <section class="source-results">
    <header class="results-head">
      <h2 class="results-title">{{ results.length }}건</h2>
    </header>

    <ul class="source-list">
      <li v-for="item in results" :key="item.quote.id" class="result-card glt-card">
        <router-link :to="`/quotes/${item.quote.id}`" class="result-quote-link">
          <blockquote class="result-quote">{{ item.quote.text }}</blockquote>
        </router-link>

        <component
          :is="sourceNovelId(item) ? 'router-link' : 'div'"
          v-bind="sourceNovelId(item) ? { to: `/novels/${sourceNovelId(item)}` } : {}"
          class="result-source"
          :class="{ 'result-source--static': !sourceNovelId(item) }"
        >
          <img
            v-if="sourceCover(item)"
            :src="sourceCover(item)"
            :alt="sourceTitle(item)"
            class="result-cover"
          />
          <div v-else class="result-cover result-cover--empty" aria-hidden="true">📖</div>
          <div class="result-source-meta">
            <span class="result-source-label">출처</span>
            <span class="result-source-title">{{ sourceTitle(item) }}</span>
            <span v-if="sourceAuthor(item)" class="result-source-author">{{ sourceAuthor(item) }}</span>
          </div>
        </component>

        <div class="result-actions">
          <DetailIconLink :to="`/quotes/${item.quote.id}`" />
          <BookmarkIconButton
            :saved="bookmarkIds.has(item.quote.id)"
            :action-label="COLLECT.action"
            :saved-label="COLLECT.done"
            @click="$emit('toggle-bookmark', item.quote.id)"
          />
        </div>
      </li>
    </ul>
  </section>
</template>

<script>
import BookmarkIconButton from './BookmarkIconButton.vue'
import DetailIconLink from './DetailIconLink.vue'
import { COLLECT } from '../utils/collectLabels'
import {
  quoteAuthorName,
  quoteCoverUrl,
  quoteNovelId,
  quoteSourceTitle,
} from '../utils/quoteDisplay'

export default {
  name: 'SourceSearchResults',
  components: { BookmarkIconButton, DetailIconLink },
  props: {
    results: { type: Array, required: true },
    bookmarkIds: { type: Set, required: true },
  },
  emits: ['toggle-bookmark'],
  data() {
    return { COLLECT }
  },
  methods: {
    sourceTitle(item) {
      return quoteSourceTitle(item.quote) || '미분류'
    },
    sourceAuthor(item) {
      return quoteAuthorName(item.quote)
    },
    sourceCover(item) {
      return quoteCoverUrl(item.quote)
    },
    sourceNovelId(item) {
      return quoteNovelId(item.quote)
    },
  },
}
</script>

<style scoped>
.source-results {
  margin-top: var(--glt-space-4);
}

.results-head {
  margin-bottom: var(--glt-space-3);
}

.results-title {
  margin: 0;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--glt-ink-secondary);
}

.source-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--glt-space-3);
}

.result-card {
  padding: var(--glt-space-4);
  display: flex;
  flex-direction: column;
  gap: var(--glt-space-3);
}

.result-quote-link {
  text-decoration: none;
  color: inherit;
}

.result-quote {
  margin: 0;
  padding: 0;
  border: none;
  font-family: var(--glt-font-serif);
  font-size: 0.94rem;
  font-weight: 400;
  line-height: 1.72;
  letter-spacing: -0.01em;
  color: var(--glt-ink);
  word-break: keep-all;
}

.result-source {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 10px 12px;
  border-radius: var(--glt-radius-md);
  background: var(--glt-bg-subtle);
  border: 1px solid rgba(212, 195, 170, 0.35);
  text-decoration: none;
  color: inherit;
  transition: border-color var(--glt-duration), box-shadow var(--glt-duration);
}

.result-source:not(.result-source--static):hover {
  border-color: var(--glt-accent-muted);
  box-shadow: var(--glt-shadow-sm);
}

.result-source--static {
  cursor: default;
}

.result-cover {
  width: 40px;
  height: 56px;
  object-fit: cover;
  border-radius: 4px;
  flex-shrink: 0;
}

.result-cover--empty {
  display: grid;
  place-items: center;
  background: var(--glt-surface);
  font-size: 1rem;
}

.result-source-meta {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.result-source-label {
  font-size: 0.66rem;
  font-weight: 600;
  color: var(--glt-accent);
  letter-spacing: 0.04em;
}

.result-source-title {
  font-size: 0.8rem;
  font-weight: 600;
  line-height: 1.4;
  color: var(--glt-ink);
  word-break: keep-all;
  overflow-wrap: anywhere;
}

.result-source-author {
  font-size: 0.72rem;
  color: var(--glt-ink-tertiary);
}

.result-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
