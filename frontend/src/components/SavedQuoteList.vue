<template>
  <section class="saved-list">
    <p class="saved-count">{{ quotes.length }}건</p>

    <ul class="saved-items">
      <li v-for="quote in quotes" :key="quote.id" class="saved-card glt-card">
        <router-link :to="`/quotes/${quote.id}`" class="saved-quote-link">
          <blockquote class="saved-quote">{{ quote.text }}</blockquote>
        </router-link>

        <component
          :is="sourceLink(quote) ? 'router-link' : 'div'"
          v-bind="sourceLink(quote) ? { to: sourceLink(quote) } : {}"
          class="saved-source"
          :class="{ 'saved-source--static': !sourceLink(quote) }"
        >
          <img
            v-if="coverUrl(quote)"
            :src="coverUrl(quote)"
            :alt="sourceTitle(quote)"
            class="saved-cover"
          />
          <div v-else class="saved-cover saved-cover--empty" aria-hidden="true">📖</div>
          <div class="saved-source-meta">
            <span class="saved-source-label">출처</span>
            <span class="saved-source-title">{{ sourceTitle(quote) }}</span>
            <span v-if="authorName(quote)" class="saved-source-author">{{ authorName(quote) }}</span>
          </div>
        </component>

        <div class="saved-actions">
          <DetailIconLink :to="`/quotes/${quote.id}`" />
          <RemoveIconButton
            label="스크랩 취소"
            @click="$emit('remove', quote.id)"
          />
        </div>
      </li>
    </ul>
  </section>
</template>

<script>
import DetailIconLink from './DetailIconLink.vue'
import RemoveIconButton from './RemoveIconButton.vue'
import {
  quoteAuthorName,
  quoteCoverUrl,
  quoteNovelId,
  quoteSourceTitle,
} from '../utils/quoteDisplay'

export default {
  name: 'SavedQuoteList',
  components: { DetailIconLink, RemoveIconButton },
  props: {
    quotes: { type: Array, required: true },
  },
  emits: ['remove'],
  methods: {
    sourceTitle(quote) {
      return quoteSourceTitle(quote) || '미분류'
    },
    authorName(quote) {
      return quoteAuthorName(quote)
    },
    coverUrl(quote) {
      return quoteCoverUrl(quote)
    },
    sourceLink(quote) {
      const novelId = quoteNovelId(quote)
      return novelId ? `/novels/${novelId}` : null
    },
  },
}
</script>

<style scoped>
.saved-list {
  margin-top: var(--glt-space-2);
}

.saved-count {
  margin: 0 0 var(--glt-space-3);
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--glt-ink-secondary);
}

.saved-items {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--glt-space-3);
}

.saved-card {
  padding: var(--glt-space-4);
  display: flex;
  flex-direction: column;
  gap: var(--glt-space-3);
}

.saved-quote-link {
  text-decoration: none;
  color: inherit;
}

.saved-quote {
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

.saved-source {
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

.saved-source:not(.saved-source--static):hover {
  border-color: var(--glt-accent-muted);
  box-shadow: var(--glt-shadow-sm);
}

.saved-source--static {
  cursor: default;
}

.saved-cover {
  width: 40px;
  height: 56px;
  object-fit: cover;
  border-radius: 4px;
  flex-shrink: 0;
}

.saved-cover--empty {
  display: grid;
  place-items: center;
  background: var(--glt-surface);
  font-size: 1rem;
}

.saved-source-meta {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.saved-source-label {
  font-size: 0.66rem;
  font-weight: 600;
  color: var(--glt-accent);
  letter-spacing: 0.04em;
}

.saved-source-title {
  font-size: 0.8rem;
  font-weight: 600;
  line-height: 1.4;
  color: var(--glt-ink);
  word-break: keep-all;
}

.saved-source-author {
  font-size: 0.72rem;
  color: var(--glt-ink-tertiary);
}

.saved-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
