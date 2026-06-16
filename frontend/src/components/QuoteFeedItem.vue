<template>
  <article class="feed-card">
    <router-link :to="`/quotes/${quote.id}`" class="feed-card-body">
      <blockquote class="feed-text">{{ quote.text }}</blockquote>
    </router-link>

    <footer v-if="novelTitle || authorName" class="feed-footer">
      <component
        :is="novelRoute ? 'router-link' : 'div'"
        v-bind="novelRoute ? { to: novelRoute } : {}"
        class="feed-source"
        :class="{ 'feed-source--static': !novelRoute }"
      >
        <img
          v-if="coverUrl"
          :src="coverUrl"
          :alt="novelTitle"
          class="feed-cover"
        />
        <div v-else class="feed-cover feed-cover--empty">📖</div>
        <div class="feed-source-info">
          <span v-if="novelTitle" class="feed-book">{{ novelTitle }}</span>
          <span v-if="authorName" class="feed-author">{{ authorName }}</span>
        </div>
      </component>
    </footer>

    <div class="feed-actions">
      <div class="feed-meta">
        <router-link
          v-if="registeredById"
          :to="`/users/${registeredById}`"
          class="feed-poster-name"
          @click.stop
        >{{ registeredByName }}</router-link>
        <span v-else-if="registeredByName" class="feed-poster-name feed-poster-name--static">{{ registeredByName }}</span>
        <span v-if="timeAgo" class="feed-time-ago">{{ timeAgo }}</span>
      </div>

      <div class="feed-btns">
        <button
          type="button"
          class="feed-action-btn feed-action-btn--like"
          :class="{ 'is-active': liked }"
          @click.stop="$emit('toggle-like')"
        >
          <svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true">
            <path
              d="M12 21l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.18L12 21z"
              :fill="liked ? 'currentColor' : 'none'"
              stroke="currentColor"
              stroke-width="1.75"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
          <span v-if="likeCount > 0">{{ formattedLikeCount }}</span>
        </button>

        <button
          type="button"
          class="feed-action-btn feed-action-btn--scrap"
          :class="{ 'is-active': scrapped }"
          @click.stop="$emit('toggle-scrap')"
        >
          <svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true">
            <path
              d="M5 3h14a1 1 0 0 1 1 1v17l-8-4-8 4V4a1 1 0 0 1 1-1z"
              :fill="scrapped ? 'currentColor' : 'none'"
              stroke="currentColor"
              stroke-width="1.75"
              stroke-linejoin="round"
            />
          </svg>
          <span v-if="scrapCount > 0">{{ formattedScrapCount }}</span>
        </button>
      </div>
    </div>
  </article>
</template>

<script>
import { quoteAuthorName, quoteCoverUrl, quoteSourceTitle } from '../utils/quoteDisplay'
import { formatCount, formatRelativeTime } from '../utils/formatters'

export default {
  name: 'QuoteFeedItem',
  props: {
    quote: { type: Object, required: true },
    liked: { type: Boolean, default: false },
    scrapped: { type: Boolean, default: false },
  },
  emits: ['toggle-like', 'toggle-scrap'],
  computed: {
    novelTitle() { return quoteSourceTitle(this.quote) },
    authorName() { return quoteAuthorName(this.quote) },
    coverUrl() { return quoteCoverUrl(this.quote) || null },
    novelId() { return this.quote.novel?.id || this.quote.source?.novel_id || null },
    novelRoute() { return this.novelId ? `/novels/${this.novelId}` : null },
    likeCount() { return Number(this.quote.like_count) || 0 },
    scrapCount() { return Number(this.quote.scrap_count) || 0 },
    formattedLikeCount() { return formatCount(this.likeCount) },
    formattedScrapCount() { return formatCount(this.scrapCount) },
    registeredById() { return this.quote.registered_by?.id || null },
    registeredByName() { return this.quote.registered_by?.name || '' },
    timeAgo() { return formatRelativeTime(this.quote.created_at) },
  },
}
</script>

<style scoped>
.feed-card {
  background: var(--glt-surface);
  border: 1px solid rgba(212, 195, 170, 0.38);
  border-radius: 18px;
  overflow: hidden;
  transition: box-shadow 0.2s var(--glt-ease);
}

.feed-card:hover {
  box-shadow: 0 4px 20px rgba(61, 52, 41, 0.09);
}

.feed-card-body {
  display: block;
  padding: 22px 20px 14px;
  text-decoration: none;
  color: inherit;
}

.feed-text {
  margin: 0;
  padding: 0;
  border: none;
  font-family: var(--glt-font-serif);
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.82;
  letter-spacing: -0.01em;
  color: var(--glt-ink);
  word-break: keep-all;
  overflow-wrap: anywhere;
}

.feed-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  padding: 0 14px 12px;
}

.feed-meta {
  display: flex;
  align-items: baseline;
  gap: 5px;
  min-width: 0;
  overflow: hidden;
}

.feed-poster-name {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--glt-ink-secondary);
  text-decoration: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
}

.feed-poster-name:not(.feed-poster-name--static):hover {
  color: var(--glt-accent-hover);
  text-decoration: underline;
}

.feed-poster-name--static {
  pointer-events: none;
}

.feed-time-ago {
  font-size: 0.72rem;
  color: var(--glt-ink-tertiary);
  white-space: nowrap;
  flex-shrink: 0;
}

.feed-btns {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.feed-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border: none;
  border-radius: 999px;
  background: transparent;
  font-size: 0.8rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  cursor: pointer;
  transition: background 0.15s var(--glt-ease), color 0.15s var(--glt-ease);
  color: var(--glt-ink-tertiary);
}

.feed-action-btn:hover {
  background: rgba(212, 195, 170, 0.22);
}

.feed-action-btn--scrap.is-active {
  color: #4a8e84;
}

.feed-action-btn--like.is-active {
  color: #c18a8a;
}

.feed-action-btn--scrap:hover {
  color: #4a8e84;
}

.feed-action-btn--like:hover {
  color: #c18a8a;
}

.feed-footer {
  padding: 0 14px 14px;
}

.feed-source {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 10px 14px;
  border-radius: 12px;
  background: linear-gradient(120deg, #d6ede5 0%, #eaf5f0 100%);
  text-decoration: none;
  color: inherit;
  transition: opacity 0.15s var(--glt-ease);
}

.feed-source:not(.feed-source--static):hover {
  opacity: 0.82;
}

.feed-source--static {
  pointer-events: none;
}

.feed-cover {
  width: 36px;
  height: 50px;
  object-fit: cover;
  border-radius: 4px;
  flex-shrink: 0;
  box-shadow: 0 1px 6px rgba(40, 80, 60, 0.18);
}

.feed-cover--empty {
  display: grid;
  place-items: center;
  background: rgba(74, 142, 132, 0.12);
  font-size: 1rem;
  border-radius: 4px;
}

.feed-source-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.feed-book {
  font-size: 0.82rem;
  font-weight: 600;
  color: #1e3d32;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.feed-author {
  font-size: 0.74rem;
  color: #4a7a6a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
