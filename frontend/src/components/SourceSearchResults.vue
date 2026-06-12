<template>
  <section class="source-results">
    <header class="results-head">
      <h2 class="results-title">출처 {{ results.length }}건</h2>
    </header>

    <ul class="source-list">
      <li v-for="item in results" :key="item.quote.id" class="source-node">
        <div class="node-quote glt-card">
          <p class="quote-text">{{ item.quote.text }}</p>
          <div class="quote-actions">
            <router-link :to="`/quotes/${item.quote.id}`" class="glt-btn glt-btn-ghost quote-link">
              상세
            </router-link>
            <button
              type="button"
              class="bookmark-btn"
              :class="{ 'is-saved': bookmarkIds.has(item.quote.id) }"
              @click="$emit('toggle-bookmark', item.quote.id)"
            >
              {{ bookmarkIds.has(item.quote.id) ? COLLECT.done : COLLECT.action }}
            </button>
          </div>
        </div>

        <div class="node-connector" aria-hidden="true">
          <span class="connector-line" />
          <span class="connector-dot" />
        </div>

        <router-link
          v-if="sourceNovelId(item)"
          :to="`/novels/${sourceNovelId(item)}`"
          class="node-source glt-card"
        >
          <img
            v-if="sourceCover(item)"
            :src="sourceCover(item)"
            :alt="sourceTitle(item)"
            class="source-cover"
          />
          <div v-else class="source-cover source-cover--empty">📖</div>
          <div class="source-meta">
            <span class="source-label">출처</span>
            <strong class="source-title">{{ sourceTitle(item) }}</strong>
            <span v-if="sourceAuthor(item)" class="source-author">{{ sourceAuthor(item) }}</span>
          </div>
        </router-link>
        <div v-else class="node-source node-source--static glt-card">
          <div class="source-cover source-cover--empty">📖</div>
          <div class="source-meta">
            <span class="source-label">출처</span>
            <strong class="source-title">{{ sourceTitle(item) }}</strong>
            <span v-if="sourceAuthor(item)" class="source-author">{{ sourceAuthor(item) }}</span>
          </div>
        </div>
      </li>
    </ul>
  </section>
</template>

<script>
import { COLLECT } from '../utils/collectLabels'
import {
  quoteAuthorName,
  quoteCoverUrl,
  quoteNovelId,
  quoteSourceTitle,
} from '../utils/quoteDisplay'

export default {
  name: 'SourceSearchResults',
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
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--glt-ink-secondary);
}

.source-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--glt-space-4);
}

.source-node {
  display: grid;
  grid-template-columns: 1fr auto 200px;
  gap: var(--glt-space-3);
  align-items: stretch;
}

.node-quote {
  padding: var(--glt-space-4);
  min-width: 0;
}

.quote-text {
  margin: 0 0 var(--glt-space-3);
  font-family: var(--glt-font-sans);
  font-size: 0.95rem;
  line-height: 1.65;
  color: var(--glt-ink);
  word-break: keep-all;
}

.quote-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.quote-link {
  font-size: 0.78rem;
  padding: 6px 12px;
}

.bookmark-btn {
  border: 1px solid var(--glt-glass-border);
  border-radius: var(--glt-radius-full);
  background: var(--glt-surface);
  color: var(--glt-ink-secondary);
  font-size: 0.76rem;
  font-weight: 600;
  padding: 6px 12px;
  cursor: pointer;
}

.bookmark-btn.is-saved {
  background: var(--glt-accent-soft);
  border-color: var(--glt-accent-muted);
  color: var(--glt-accent-hover);
}

.node-connector {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 24px;
  padding: var(--glt-space-2) 0;
}

.connector-line {
  flex: 1;
  width: 2px;
  background: linear-gradient(180deg, var(--glt-line), var(--glt-accent-muted));
  border-radius: 1px;
}

.connector-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--glt-accent);
  margin-top: 4px;
}

.node-source {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 10px;
  text-align: left;
  cursor: pointer;
  border: 1px solid var(--glt-glass-border);
  background: var(--glt-surface);
  border-radius: var(--glt-radius-md);
  transition: box-shadow 0.2s var(--glt-ease);
  text-decoration: none;
  color: inherit;
}

.node-source:hover {
  box-shadow: var(--glt-shadow-md);
}

.node-source--static {
  cursor: default;
}

.source-cover {
  width: 44px;
  height: 62px;
  object-fit: cover;
  border-radius: 4px;
  flex-shrink: 0;
}

.source-cover--empty {
  display: grid;
  place-items: center;
  background: var(--glt-bg-subtle);
  font-size: 1.1rem;
}

.source-meta {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.source-label {
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--glt-accent);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.source-title {
  font-size: 0.82rem;
  line-height: 1.35;
  color: var(--glt-ink);
  word-break: keep-all;
}

.source-author {
  font-size: 0.74rem;
  color: var(--glt-ink-tertiary);
}

@media (max-width: 720px) {
  .source-node {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
  }

  .node-connector {
    flex-direction: row;
    width: auto;
    height: 20px;
    padding: 0 var(--glt-space-2);
  }

  .connector-line {
    flex: 1;
    height: 2px;
    width: auto;
  }

  .connector-dot {
    margin-top: 0;
    margin-left: 4px;
  }
}
</style>
