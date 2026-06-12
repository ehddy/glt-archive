<template>

  <section
    ref="sheetEl"
    class="register glt-container register--sheet"
    :class="{ 'is-sheet-dragging': sheetDragging }"
    :style="sheetStyle"
  >
    <div
      class="sheet-drag-zone"
      @pointerdown="onSheetDragStart"
      @pointermove="onSheetDragMove"
      @pointerup="onSheetDragEnd"
      @pointercancel="onSheetDragEnd"
    >
      <div class="sheet-handle" aria-hidden="true" />
      <h1 class="glt-title sheet-title">문장 등록</h1>
    </div>

    <form class="form-card glt-card" @submit.prevent="submit">

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
        v-if="sourceMode === 'aladin' && bookSearchOpen"
        class="glt-field book-search-field"
      >

        <div class="book-search-head">
          <label>도서 검색</label>
          <button
            v-if="selectedBook"
            type="button"
            class="search-keep-btn"
            @click="bookSearchOpen = false"
          >
            선택 유지
          </button>
        </div>

        <div class="search-wrap">

          <input
            ref="bookSearchInput"
            v-model="bookQuery"
            type="search"
            placeholder="작가 이름이나 도서명을 검색하세요"
            @input="onSearchInput"
            @keyup.enter="onSearchEnter"
            @focus="bookSearchOpen = true"
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

                <span>{{ formatBookAuthor(book.author) }}</span>

                <span v-if="book.publisher" class="result-publisher">{{ book.publisher }}</span>

              </div>

            </button>

          </li>

        </ul>

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
        v-if="sourceMode === 'aladin' && selectedBook && !bookSearchOpen"
        class="glt-field book-search-reopen"
      >
        <label>도서 검색</label>
        <button type="button" class="search-reopen" @click="openBookSearch">
          작가 이름이나 도서명을 검색하세요
        </button>
      </div>

      <div
        v-if="sourceMode === 'aladin' && selectedBook && !bookSearchOpen"
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
      </div>

      <div class="glt-field">
        <label>문장 *</label>
        <textarea
          v-model="form.text"
          required
          placeholder="문장"
          @input="clearNotice"
        />
      </div>

      <div class="submit-block submit-block--standalone">
        <button
          class="glt-btn glt-btn-primary submit-btn"
          type="submit"
          :disabled="submitting || !canSubmit"
        >
          등록
        </button>
      </div>

      <p v-if="notice" class="register-notice" role="status">{{ notice }}</p>

    </form>

  </section>

</template>



<script>

import { api } from '../api'
import { friendlyRegisterError } from '../utils/registerErrors'
import {
  novelToSelectedBook,
  pickAladinBookMatch,
  routeAfterQuoteCreated,
} from '../utils/registerBook'
import { endPageLoading, startPageLoading } from '../utils/pageLoading'

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
      searchRequestId: 0,

      form: {

        text: '',

      },

      sheetDragY: 0,
      sheetDragging: false,
      sheetDragPointerId: null,
      sheetDragStartY: 0,
      sheetDragStartOffset: 0,

      bookSearchOpen: true,

    }

  },

  computed: {

    sheetStyle() {
      if (this.sheetDragY <= 0) return null
      return { transform: `translateY(${this.sheetDragY}px)` }
    },

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

    onSheetDragStart(event) {
      const sheet = this.$refs.sheetEl
      if (!sheet || sheet.scrollTop > 0) return
      if (event.pointerType === 'mouse' && event.button !== 0) return

      this.sheetDragging = true
      this.sheetDragPointerId = event.pointerId
      this.sheetDragStartY = event.clientY
      this.sheetDragStartOffset = this.sheetDragY
      event.currentTarget.setPointerCapture(event.pointerId)
    },

    onSheetDragMove(event) {
      if (!this.sheetDragging || event.pointerId !== this.sheetDragPointerId) return

      const delta = event.clientY - this.sheetDragStartY
      this.sheetDragY = Math.max(0, this.sheetDragStartOffset + delta)
    },

    onSheetDragEnd(event) {
      if (event.pointerId !== this.sheetDragPointerId) return

      const zone = event.currentTarget
      if (zone?.hasPointerCapture?.(event.pointerId)) {
        zone.releasePointerCapture(event.pointerId)
      }

      const threshold = 96
      const shouldClose = this.sheetDragY > threshold

      this.sheetDragging = false
      this.sheetDragPointerId = null

      if (shouldClose) {
        const sheet = this.$refs.sheetEl
        this.sheetDragY = sheet?.offsetHeight || 480
        window.setTimeout(() => this.goBack(), 260)
        return
      }

      this.sheetDragY = 0
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
        this.bookSearchOpen = true
      }
    },

    async applyPrefill() {
      startPageLoading()

      try {
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

        if (history.state?.fromAiSearch && stateBookQ && typeof stateBookQ === 'string') {
          this.sourceMode = 'aladin'
          const matched = await this.prefillFromAladinQuery(
            stateBookQ,
            stateSourceTitle,
            history.state?.prefillAuthor || stateCustomSource?.author || '',
          )
          if (!matched && stateCustomSource) {
            this.sourceMode = 'custom'
            this.customSource.title = stateCustomSource.title || ''
            this.customSource.author_name = stateCustomSource.author || ''
          }
          return
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
          await this.prefillFromAladinQuery(
            stateBookQ,
            stateSourceTitle,
            history.state?.prefillAuthor || '',
          )
          return
        }

        if (!novelId && !quoteId) return

        this.sourceMode = 'aladin'

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
          const novel = await api.getNovel(novelId)
          if (novel) {
            await this.setSelectedFromNovel(novel)
          }
        }
      } catch (e) {
        this.searchError = e.message
      } finally {
        endPageLoading()
      }
    },

    async prefillFromAladinQuery(bookQ, sourceTitle = '', author = '') {
      const initialQuery = (bookQ || '').trim()
      const titleHint = (sourceTitle || initialQuery).trim()

      this.bookQuery = initialQuery
      this.prefilledFromContext = false
      this.bookSearchOpen = true

      if (!initialQuery) return false

      await this.searchBooks()

      let match = pickAladinBookMatch(this.searchResults, titleHint, author)

      if (!match && titleHint && titleHint !== initialQuery) {
        this.bookQuery = titleHint
        await this.searchBooks()
        match = pickAladinBookMatch(this.searchResults, titleHint, author)
      }

      if (match) {
        await this.selectBook(match)
        return true
      }

      return false
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

      this.bookSearchOpen = false

    },

    formatBookAuthor(author) {
      if (!author) return ''
      const names = String(author).split(',').map((n) => n.trim()).filter(Boolean)
      if (!names.length) return ''
      const first = names[0].split('(')[0].trim()
      if (names.length === 1) {
        return first.length > 36 ? `${first.slice(0, 36)}…` : first
      }
      return `${first} 외 ${names.length - 1}명`
    },

    onSearchInput() {
      clearTimeout(this.searchTimer)
      this.searchError = ''

      const q = this.bookQuery.trim()
      if (!q) {
        this.searchRequestId += 1
        this.searchResults = []
        this.searched = false
        this.searching = false
        return
      }

      this.searchResults = []
      this.searched = false
      this.searchTimer = setTimeout(this.searchBooks, 400)
    },

    onSearchEnter() {
      clearTimeout(this.searchTimer)
      this.searchError = ''
      const q = this.bookQuery.trim()
      if (!q) {
        this.searchRequestId += 1
        this.searchResults = []
        this.searched = false
        this.searching = false
        return
      }
      this.searchBooks()
    },

    async searchBooks() {
      const q = this.bookQuery.trim()
      if (!q) return

      const requestId = ++this.searchRequestId
      this.searching = true
      this.searchError = ''

      try {
        const results = await api.searchAladinBooks(q)
        if (requestId !== this.searchRequestId) return
        if (q !== this.bookQuery.trim()) return
        this.searchResults = results
        this.searched = true
      } catch (e) {
        if (requestId !== this.searchRequestId) return
        this.searchResults = []
        this.searched = true
        this.searchError = e.message
      } finally {
        if (requestId === this.searchRequestId) {
          this.searching = false
        }
      }
    },

    openBookSearch() {
      this.bookSearchOpen = true
      this.$nextTick(() => {
        this.$refs.bookSearchInput?.focus()
      })
    },

    async selectBook(book) {

      this.selectedBook = book
      this.bookSearchOpen = false

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

      this.bookSearchOpen = true

      if (this.$route.query.novel_id || this.$route.query.quote_id) {

        this.$router.replace({ path: '/register' })

      }

    },

    async submit() {
      if (!this.canSubmit) return

      this.submitting = true
      startPageLoading()
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
        endPageLoading()
      }
    },

  },

}

</script>



<style scoped>

.register--sheet {
  position: fixed;
  top: calc(var(--glt-header-height) + 6px);
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 150;
  width: 100%;
  max-width: var(--glt-app-width);
  margin: 0 auto;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  background: var(--glt-bg);
  border-radius: 20px 20px 0 0;
  box-shadow: 0 -16px 48px rgba(61, 52, 41, 0.16);
  padding: var(--glt-space-2) var(--glt-space-4) calc(var(--glt-space-6) + env(safe-area-inset-bottom, 0px));
  transition: transform 0.28s var(--glt-ease);
}

.register--sheet.is-sheet-dragging {
  transition: none;
}

.sheet-drag-zone {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 0 calc(-1 * var(--glt-space-4)) var(--glt-space-3);
  padding: 6px var(--glt-space-4) var(--glt-space-2);
  cursor: grab;
  touch-action: none;
  user-select: none;
}

.sheet-drag-zone:active {
  cursor: grabbing;
}

.sheet-handle {
  width: 40px;
  height: 5px;
  margin: 0 auto 10px;
  border-radius: var(--glt-radius-full);
  background: rgba(212, 195, 170, 0.9);
}

.sheet-title {
  margin: 0;
  font-size: 1rem;
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

.book-search-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: var(--glt-space-2);
}

.book-search-head label {
  margin: 0;
}

.search-keep-btn {
  border: none;
  background: transparent;
  padding: 0;
  font-size: 0.74rem;
  font-weight: 600;
  color: var(--glt-accent-hover);
  cursor: pointer;
}

.search-keep-btn:hover {
  text-decoration: underline;
}

.book-search-reopen {
  margin-bottom: var(--glt-space-3);
}

.search-reopen {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid var(--glt-glass-border);
  border-radius: var(--glt-radius-md);
  background: var(--glt-surface);
  color: var(--glt-ink-tertiary);
  font-size: 0.9rem;
  text-align: left;
  cursor: pointer;
  transition: border-color var(--glt-duration), color var(--glt-duration);
}

.search-reopen:hover {
  color: var(--glt-ink-secondary);
  border-color: var(--glt-accent-muted);
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
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.result-text span {
  font-size: 0.82rem;
  color: var(--glt-ink-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}



.result-publisher {

  color: var(--glt-ink-tertiary) !important;

}



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
  margin: var(--glt-space-3) 0 0;
  font-size: 0.82rem;
  line-height: 1.55;
  text-align: center;
  color: var(--glt-ink-tertiary);
  word-break: keep-all;
}



@media (max-width: 640px) {
  .selected-cover {
    width: 56px;
    height: 80px;
  }
}

</style>

