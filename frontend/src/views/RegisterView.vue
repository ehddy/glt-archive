<template>

  <section class="register glt-container">

    <h1 class="glt-title">구절 등록</h1>

    <form class="form-card glt-card" @submit.prevent="submit">

      <div class="glt-field">

        <label>구절 *</label>

        <textarea

          v-model="form.text"

          required

          placeholder="구절"

        />

      </div>



      <div v-if="!prefilledFromContext || !selectedBook" class="glt-field book-search-field">

        <label>작품 검색 *</label>

        <div class="search-wrap">

          <input

            v-model="bookQuery"

            type="search"

            placeholder="작품 검색"

            @input="onSearchInput"

          />

          <span v-if="searching" class="search-status">…</span>

        </div>

        <p v-if="searchError" class="field-error">{{ searchError }}</p>



        <ul v-if="searchResults.length" class="search-results">

          <li v-for="book in searchResults" :key="book.item_id">

            <button

              type="button"

              class="result-item"

              :class="{ 'is-selected': selectedBook?.item_id === book.item_id }"

              @click="selectBook(book)"

            >

              <img

                v-if="book.cover_url"

                :src="book.cover_url"

                :alt="`${book.title} 표지`"

                class="result-cover"

              />

              <div v-else class="result-cover result-cover--empty">📖</div>

              <div class="result-text">

                <strong>{{ book.title }}</strong>

                <span>{{ book.author }}</span>

                <span v-if="book.publisher" class="result-publisher">{{ book.publisher }}</span>

              </div>

            </button>

          </li>

        </ul>



        <p v-else-if="bookQuery.trim() && searched && !searching" class="search-empty">
          결과 없음
        </p>

      </div>



      <div
        v-if="selectedBook"
        class="book-panel glt-card-raised"
        :class="{ 'book-panel--prefilled': prefilledFromContext }"
      >
        <div class="book-panel-head">
          <button type="button" class="clear-btn" @click="clearSelection">변경</button>
        </div>

        <div class="book-panel-body">
          <img
            v-if="selectedBook.cover_url"
            :src="selectedBook.cover_url"
            :alt="`${selectedBook.title} 표지`"
            class="selected-cover"
          />
          <div v-else class="selected-cover selected-cover--empty" aria-hidden="true">📖</div>

          <div class="selected-info">
            <h3>{{ selectedBook.title }}</h3>
            <p class="selected-author">{{ selectedBook.author }}</p>
            <p v-if="selectedBook.publisher" class="selected-meta">
              {{ selectedBook.publisher }}
              <span v-if="selectedBook.pub_date"> · {{ selectedBook.pub_date }}</span>
            </p>
            <p v-if="selectedBook.description && !prefilledFromContext" class="selected-desc">
              {{ selectedBook.description }}
            </p>
          </div>
        </div>

        <div class="submit-block" :class="{ 'submit-block--inline': prefilledFromContext }">
          <button
            class="glt-btn glt-btn-primary submit-btn"
            type="submit"
            :disabled="submitting || !canSubmit"
          >
            {{ submitting ? '등록 중…' : '등록' }}
          </button>
        </div>
      </div>

      <div v-else class="submit-block submit-block--standalone">
        <button
          class="glt-btn glt-btn-primary submit-btn"
          type="submit"
          :disabled="submitting || !canSubmit"
        >
          {{ submitting ? '등록 중…' : '등록' }}
        </button>
      </div>

      <p v-if="message" class="message">{{ message }}</p>

    </form>

  </section>

</template>



<script>

import { api } from '../api'
import { novelToSelectedBook } from '../utils/registerBook'

export default {

  name: 'RegisterView',

  data() {

    return {

      submitting: false,

      searching: false,

      searched: false,

      searchError: '',

      message: '',

      bookQuery: '',

      searchResults: [],

      selectedBook: null,

      prefilledFromContext: false,

      searchTimer: null,

      form: {

        text: '',

      },

    }

  },

  computed: {

    canSubmit() {
      const book = this.selectedBook
      return (
        this.form.text.trim().length >= 2
        && !!book
        && !!(book.novel_id || book.item_id)
      )
    },

  },

  mounted() {

    this.applyPrefill()

  },

  watch: {

    '$route.query': {

      handler() {

        this.applyPrefill()

      },

    },

  },

  beforeUnmount() {

    clearTimeout(this.searchTimer)

  },

  methods: {

    async applyPrefill() {

      const { novel_id: novelId, quote_id: quoteId, text } = this.$route.query

      if (text && typeof text === 'string') {
        this.form.text = text
      }

      if (!novelId && !quoteId) return

      try {

        const stateBook = history.state?.prefillBook

        if (
          stateBook?.novel_id
          && (!novelId || String(stateBook.novel_id) === String(novelId))
        ) {

          await this.setSelectedFromNovel({

            id: stateBook.novel_id,

            title: stateBook.title,

            author: { name: stateBook.author },

            aladin_item_id: stateBook.item_id,

            cover_url: stateBook.cover_url,

            publisher: stateBook.publisher,

            pub_date: stateBook.pub_date,

            description: stateBook.description,

          })

          return

        }

        if (quoteId) {

          const quote = await api.getQuote(quoteId)

          if (quote.novel) {

            await this.setSelectedFromNovel(quote.novel)

          }

          return

        }

        if (novelId) {

          const library = await api.getLibrary()

          const book = library.books.find((b) => String(b.id) === String(novelId))

          if (book) {

            const novel = book.quotes?.[0]?.novel || {

              id: book.id,

              title: book.title,

              author: book.author,

            }

            await this.setSelectedFromNovel(novel)

          }

        }

      } catch (e) {

        this.searchError = e.message

      }

    },

    async setSelectedFromNovel(novel) {

      const book = novelToSelectedBook(novel)

      if (!book) return

      if (book.item_id) {

        try {

          const detail = await api.getAladinBook(book.item_id)

          this.selectedBook = { ...book, ...detail, novel_id: novel.id }

        } catch {

          this.selectedBook = book

        }

      } else {

        this.selectedBook = book

      }

      this.prefilledFromContext = true

      this.bookQuery = novel.title || ''

      this.searchResults = []

      this.searched = false

      this.searchError = ''

    },

    onSearchInput() {

      clearTimeout(this.searchTimer)

      this.searchError = ''

      if (!this.bookQuery.trim()) {

        this.searchResults = []

        this.searched = false

        return

      }

      this.searchTimer = setTimeout(this.searchBooks, 400)

    },

    async searchBooks() {

      const q = this.bookQuery.trim()

      if (!q) return



      this.searching = true

      this.searchError = ''

      try {

        this.searchResults = await api.searchAladinBooks(q)

        this.searched = true

      } catch (e) {

        this.searchResults = []

        this.searched = true

        this.searchError = e.message

      } finally {

        this.searching = false

      }

    },

    async selectBook(book) {

      this.selectedBook = book

      this.searchResults = []

      this.searchError = ''

      try {

        const detail = await api.getAladinBook(book.item_id)

        this.selectedBook = { ...book, ...detail }

      } catch {

        this.selectedBook = book

      }

    },

    clearSelection() {

      this.selectedBook = null

      this.prefilledFromContext = false

      this.bookQuery = ''

      this.searchResults = []

      this.searched = false

      if (this.$route.query.novel_id || this.$route.query.quote_id) {

        this.$router.replace({ path: '/register' })

      }

    },

    async submit() {

      if (!this.canSubmit) return



      this.submitting = true

      this.message = ''

      try {

        const payload = { text: this.form.text.trim() }

        if (this.selectedBook.novel_id) {
          payload.novel_id = this.selectedBook.novel_id
        } else if (this.selectedBook.item_id) {
          payload.aladin_item_id = this.selectedBook.item_id
        } else {
          this.message = '작품을 선택해 주세요.'
          return
        }

        await api.createQuote(payload)

        this.$router.push({ path: '/', query: { registered: '1' } })

      } catch (e) {

        this.message = e.message

      } finally {

        this.submitting = false

      }

    },

  },

}

</script>



<style scoped>

.form-card {

  padding: var(--glt-space-5);

}



.book-search-field {

  position: relative;

}



.search-wrap {

  position: relative;

}



.search-status {

  position: absolute;

  right: 12px;

  top: 50%;

  transform: translateY(-50%);

  font-size: 0.8rem;

  color: var(--glt-ink-tertiary);

}



.search-results {

  list-style: none;

  margin: 10px 0 0;

  padding: 0;

  max-height: 320px;

  overflow-y: auto;

  border: 1px solid var(--glt-glass-border);

  border-radius: var(--glt-radius-md);

  background: var(--glt-surface);

}



.result-item {

  width: 100%;

  display: flex;

  gap: 12px;

  align-items: flex-start;

  padding: 12px;

  border: none;

  border-bottom: 1px solid var(--glt-glass-border);

  background: transparent;

  text-align: left;

  cursor: pointer;

  transition: background var(--glt-duration);

}



.result-item:last-child {

  border-bottom: none;

}



.result-item:hover,

.result-item.is-selected {

  background: var(--glt-accent-soft);

}



.result-cover {

  width: 48px;

  height: 68px;

  object-fit: cover;

  border-radius: 4px;

  flex-shrink: 0;

  box-shadow: var(--glt-shadow-sm);

}



.result-cover--empty {

  display: grid;

  place-items: center;

  background: var(--glt-bg-subtle);

  font-size: 1.2rem;

}



.result-text {

  min-width: 0;

  display: flex;

  flex-direction: column;

  gap: 4px;

}



.result-text strong {

  font-size: 0.92rem;

  color: var(--glt-ink);

  line-height: 1.4;

}



.result-text span {

  font-size: 0.82rem;

  color: var(--glt-ink-secondary);

}



.result-publisher {

  color: var(--glt-ink-tertiary) !important;

}



.search-empty,

.field-error {

  margin: 8px 0 0;

  font-size: 0.84rem;

}



.field-error {

  color: var(--glt-accent-hover);

}



.book-panel {
  padding: 14px;
  margin-top: var(--glt-space-2);
}

.book-panel-head {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  margin-bottom: 12px;
}

.book-panel-body {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  min-width: 0;
}

.selected-cover {
  width: 64px;
  height: 90px;
  flex-shrink: 0;
  object-fit: cover;
  border-radius: 6px;
  box-shadow: var(--glt-shadow-sm);
}

.selected-cover--empty {
  display: grid;
  place-items: center;
  background: var(--glt-bg-subtle);
  font-size: 1.4rem;
}

.selected-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--glt-accent);
  white-space: nowrap;
}

.selected-info {
  flex: 1;
  min-width: 0;
}

.selected-info h3 {
  margin: 0;
  font-size: 1rem;
  line-height: 1.45;
  color: var(--glt-ink);
  word-break: keep-all;
  overflow-wrap: anywhere;
}

.selected-author {
  margin: 4px 0 0;
  font-size: 0.86rem;
  color: var(--glt-ink-secondary);
}



.selected-meta {

  color: var(--glt-ink-tertiary) !important;

}



.selected-desc {

  margin-top: 8px !important;

  font-size: 0.82rem !important;

  line-height: 1.55;

  display: -webkit-box;

  -webkit-line-clamp: 3;

  -webkit-box-orient: vertical;

  overflow: hidden;

}



.clear-btn {
  flex-shrink: 0;
  border: 1px solid var(--glt-glass-border);
  border-radius: var(--glt-radius-full);
  background: var(--glt-surface);
  color: var(--glt-ink-secondary);
  font-size: 0.76rem;
  font-weight: 600;
  cursor: pointer;
  padding: 5px 10px;
  white-space: nowrap;
}

.clear-btn:hover {
  color: var(--glt-accent);
  border-color: var(--glt-accent-muted);
}

.book-panel--prefilled .submit-block--inline {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid var(--glt-line);
}

.submit-block {
  margin-top: var(--glt-space-2);
  padding-top: var(--glt-space-4);
  border-top: 1px solid var(--glt-line);
}

.submit-block--standalone {
  margin-top: var(--glt-space-4);
}

.submit-btn {
  width: 100%;
  padding: 12px 18px;
  font-size: 0.92rem;
}

.submit-hint {
  margin: var(--glt-space-3) 0 0;
  color: var(--glt-ink-tertiary);
  font-size: 0.8rem;
  line-height: 1.55;
  text-align: center;
}

.submit-hint strong {
  color: var(--glt-accent-hover);
}

.message {

  margin-top: var(--glt-space-3);

  color: var(--glt-accent);

  font-size: 0.875rem;

}



@media (max-width: 640px) {
  .selected-cover {
    width: 56px;
    height: 80px;
  }
}

</style>

