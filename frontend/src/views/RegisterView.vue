<template>

  <section class="register glt-container">

    <header class="register-head">
      <button type="button" class="back-btn" @click="goBack">← 뒤로</button>
      <h1 class="glt-title">문장 등록</h1>
    </header>

    <form class="form-card glt-card" @submit.prevent="submit">

      <div class="glt-field">

        <label>문장 *</label>

        <textarea

          v-model="form.text"

          required

          placeholder="문장"

          @input="clearNotice"

        />

      </div>

      <div class="glt-field source-mode-field">
        <label>출처</label>
        <div class="mode-tabs" role="tablist">
          <button
            type="button"
            class="mode-tab"
            :class="{ 'is-active': sourceMode === 'aladin' }"
            @click="setSourceMode('aladin')"
          >
            도서
          </button>
          <button
            type="button"
            class="mode-tab"
            :class="{ 'is-active': sourceMode === 'custom' }"
            @click="setSourceMode('custom')"
          >
            직접 입력
          </button>
        </div>
      </div>

      <div
        v-if="sourceMode === 'aladin' && (!prefilledFromContext || !selectedBook)"
        class="glt-field book-search-field"
      >

        <label>도서 검색</label>

        <div class="search-wrap">

          <input

            v-model="bookQuery"

            type="search"

            placeholder="작가 이름이나 도서명을 검색하세요"

            @input="onSearchInput"

          />

          <span v-if="searching" class="search-status">…</span>

        </div>

        <p v-if="searchHint" class="search-hint">{{ searchHint }}</p>



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
          검색 결과가 없어요. 다른 키워드로 시도해 보세요.
        </p>

      </div>

      <div v-if="sourceMode === 'custom'" class="glt-field custom-source-fields">
        <label for="custom-source-title">출처명 *</label>
        <input
          id="custom-source-title"
          v-model="customSource.title"
          type="text"
          placeholder="예: 성경, 연설문, 수필"
          maxlength="200"
          @input="clearNotice"
        />
        <label for="custom-source-author" class="custom-author-label">작가·화자</label>
        <input
          id="custom-source-author"
          v-model="customSource.author_name"
          type="text"
          placeholder="선택 사항"
          maxlength="100"
        />
      </div>

      <div
        v-if="sourceMode === 'aladin' && selectedBook"
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

      <div
        v-if="sourceMode !== 'aladin' || !selectedBook"
        class="submit-block submit-block--standalone"
      >
        <button
          class="glt-btn glt-btn-primary submit-btn"
          type="submit"
          :disabled="submitting || !canSubmit"
        >
          {{ submitting ? '등록 중…' : '등록' }}
        </button>
      </div>

      <div v-if="notice" class="register-notice" role="status">
        <p class="register-notice-text">{{ notice }}</p>
      </div>

    </form>

  </section>

</template>



<script>

import { api } from '../api'
import { friendlyRegisterError } from '../utils/registerErrors'
import { novelToSelectedBook, routeAfterQuoteCreated } from '../utils/registerBook'

export default {

  name: 'RegisterView',

  data() {

    return {

      submitting: false,

      searching: false,

      searched: false,

      searchError: '',

      notice: '',

      bookQuery: '',

      searchResults: [],

      selectedBook: null,

      prefilledFromContext: false,

      sourceMode: 'aladin',

      customSource: {
        title: '',
        author_name: '',
      },

      searchTimer: null,

      form: {

        text: '',

      },

    }

  },

  computed: {

    searchHint() {
      return this.searchError ? friendlyRegisterError(this.searchError) : ''
    },

    canSubmit() {
      const textOk = this.form.text.trim().length >= 2
      if (!textOk) return false

      if (this.sourceMode === 'custom') {
        return this.customSource.title.trim().length >= 1
      }

      const book = this.selectedBook
      return !!book && !!(book.novel_id || book.item_id)
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

    goBack() {
      if (window.history.length > 1) {
        this.$router.back()
      } else {
        this.$router.push('/')
      }
    },

    showNotice(raw) {
      this.notice = friendlyRegisterError(raw)
    },

    clearNotice() {
      this.notice = ''
    },

    setSourceMode(mode) {
      this.sourceMode = mode
      this.clearNotice()
      if (mode !== 'aladin') {
        this.selectedBook = null
        this.prefilledFromContext = false
        this.bookQuery = ''
        this.searchResults = []
        this.searched = false
      }
    },

    async applyPrefill() {

      const { novel_id: novelId, quote_id: quoteId, text } = this.$route.query
      const stateText = history.state?.prefillText
      const stateBookQ = history.state?.prefillBookQuery
      const stateSourceTitle = history.state?.prefillSourceTitle
      const stateSourceMode = history.state?.sourceMode
      const stateCustomSource = history.state?.prefillCustomSource

      if (stateText && typeof stateText === 'string') {
        this.form.text = stateText
      } else if (text && typeof text === 'string') {
        this.form.text = text
      }

      if (stateSourceMode === 'custom' || stateCustomSource) {
        this.sourceMode = 'custom'
        if (stateCustomSource) {
          this.customSource.title = stateCustomSource.title || ''
          this.customSource.author_name = stateCustomSource.author || ''
        }
        return
      }

      if (stateBookQ && typeof stateBookQ === 'string') {
        this.sourceMode = 'aladin'
        await this.prefillFromAladinQuery(stateBookQ, stateSourceTitle)
        return
      }

      if (!novelId && !quoteId) return

      this.sourceMode = 'aladin'

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
          } else if (quote.source?.title) {
            this.sourceMode = 'custom'
            this.customSource.title = quote.source.title
            this.customSource.author_name = quote.source.author?.name || ''
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

    async prefillFromAladinQuery(bookQ, sourceTitle = '') {
      this.bookQuery = bookQ
      this.prefilledFromContext = false
      await this.searchBooks()
      if (!this.searchResults.length && sourceTitle && sourceTitle !== bookQ) {
        this.bookQuery = sourceTitle
        await this.searchBooks()
      }
      if (this.searchResults.length === 1) {
        await this.selectBook(this.searchResults[0])
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

      this.clearNotice()

      try {

        const payload = { text: this.form.text.trim() }

        if (this.sourceMode === 'aladin') {
          if (!this.selectedBook) {
            this.showNotice('어떤 도서에서 나온 문장인지 선택해 주세요.')
            return
          }
          if (this.selectedBook.novel_id) {
            payload.novel_id = this.selectedBook.novel_id
          } else if (this.selectedBook.item_id) {
            payload.aladin_item_id = this.selectedBook.item_id
          } else {
            this.showNotice('어떤 도서에서 나온 문장인지 선택해 주세요.')
            return
          }
        } else if (this.sourceMode === 'custom') {
          payload.custom_source = {
            title: this.customSource.title.trim(),
            author_name: this.customSource.author_name.trim() || null,
          }
        }

        const quote = await api.createQuote(payload)
        this.$router.push(routeAfterQuoteCreated(quote))

      } catch (e) {

        this.showNotice(e.message)

      } finally {

        this.submitting = false

      }

    },

  },

}

</script>



<style scoped>

.register-head {
  display: flex;
  align-items: center;
  gap: var(--glt-space-3);
  margin-bottom: var(--glt-space-4);
}

.register-head .glt-title {
  margin: 0;
}

.back-btn {
  flex-shrink: 0;
  border: 1px solid var(--glt-glass-border);
  border-radius: var(--glt-radius-full);
  background: var(--glt-surface);
  color: var(--glt-ink-secondary);
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  padding: 7px 12px;
}

.back-btn:hover {
  color: var(--glt-accent);
  border-color: var(--glt-accent-muted);
}

.form-card {

  padding: var(--glt-space-5);

}

.source-mode-field {
  margin-top: var(--glt-space-2);
}

.mode-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.mode-tab {
  border: 1px solid var(--glt-glass-border);
  border-radius: var(--glt-radius-full);
  background: var(--glt-surface);
  color: var(--glt-ink-secondary);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  padding: 7px 14px;
  transition: background var(--glt-duration), border-color var(--glt-duration);
}

.mode-tab.is-active {
  background: var(--glt-accent-soft);
  border-color: var(--glt-accent-muted);
  color: var(--glt-accent-hover);
}

.custom-source-fields {
  display: flex;
  flex-direction: column;
  gap: var(--glt-space-2);
}

.custom-author-label {
  margin-top: var(--glt-space-2);
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
.search-hint {
  margin: 8px 0 0;
  padding: 10px 12px;
  border-radius: var(--glt-radius-md);
  background: var(--glt-bg-subtle);
  font-size: 0.84rem;
  color: var(--glt-ink-secondary);
  line-height: 1.5;
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

.register-notice {
  margin-top: var(--glt-space-4);
  padding: 14px 16px;
  border-radius: var(--glt-radius-md);
  background: var(--glt-bg-subtle);
  border: 1px solid var(--glt-glass-border);
}

.register-notice-text {
  margin: 0;
  font-size: 0.88rem;
  line-height: 1.6;
  color: var(--glt-ink-secondary);
  text-align: center;
  word-break: keep-all;
}



@media (max-width: 640px) {
  .selected-cover {
    width: 56px;
    height: 80px;
  }
}

</style>

