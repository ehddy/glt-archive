<template>
  <div class="chatbot">
    <button
      class="chat-fab"
      type="button"
      :aria-expanded="open"
      aria-label="AI 채팅"
      @click="toggle"
    >
      <svg v-if="!open" class="chat-fab-icon" viewBox="0 0 24 24" aria-hidden="true">
        <path
          d="M6 6.5h11A2.5 2.5 0 0 1 19.5 9v6.5A2.5 2.5 0 0 1 17 18H11.5L8 20.5V18H6A2.5 2.5 0 0 1 3.5 15.5V9A2.5 2.5 0 0 1 6 6.5z"
          fill="none"
          stroke="currentColor"
          stroke-width="1.75"
          stroke-linejoin="round"
        />
        <path
          d="M8 11.5h7M8 14.5h4.5"
          fill="none"
          stroke="currentColor"
          stroke-width="1.75"
          stroke-linecap="round"
        />
        <path
          d="M17.5 4.5l.55 1.85 1.85.55-1.85.55-.55 1.85-.55-1.85-1.85-.55 1.85-.55.55-1.85z"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linejoin="round"
        />
      </svg>
      <svg v-else class="chat-fab-icon" viewBox="0 0 24 24" aria-hidden="true">
        <path
          d="M8 8l8 8M16 8l-8 8"
          fill="none"
          stroke="currentColor"
          stroke-width="1.75"
          stroke-linecap="round"
        />
      </svg>
    </button>

    <div v-if="open" class="chat-panel glt-card">
      <header class="chat-header">
        <h2 class="chat-title">뭐 읽을까</h2>
      </header>

      <div ref="messagesEl" class="chat-messages">
        <div v-if="showIntro" class="chat-intro">
          <div class="chat-message chat-message--assistant">
            <p class="chat-bubble">요즘 어떤 책이 끌려요?</p>
          </div>

          <div class="chat-suggestions">
            <p class="suggestions-label">예시</p>
            <div class="suggestions-list">
              <button
                v-for="example in examples"
                :key="example"
                type="button"
                class="suggestion-chip"
                :disabled="loading"
                @click="send(example)"
              >
                {{ example }}
              </button>
            </div>
          </div>
        </div>

        <div
          v-for="(msg, i) in messages"
          :key="i"
          class="chat-message"
          :class="`chat-message--${msg.role}`"
        >
          <p class="chat-bubble">{{ msg.content }}</p>

          <div v-if="msg.recommendations?.length" class="chat-recs">
            <article
              v-for="(rec, j) in msg.recommendations"
              :key="j"
              class="rec-card"
            >
              <div class="rec-head">
                <strong>{{ rec.title }}</strong>
                <span v-if="rec.in_library" class="rec-badge rec-badge--library">등록</span>
                <span v-else class="rec-badge rec-badge--ai">AI</span>
              </div>
              <p class="rec-author">{{ rec.author }}</p>
              <p class="rec-reason">{{ rec.reason }}</p>
            </article>
          </div>
        </div>

        <div v-if="loading" class="chat-message chat-message--assistant">
          <p class="chat-bubble chat-bubble--loading">…</p>
        </div>
      </div>

      <form class="chat-input" @submit.prevent="send()">
        <input
          v-model="input"
          type="text"
          placeholder="메시지 입력"
          :disabled="loading"
        />
        <button
          class="chat-send-btn"
          type="submit"
          :disabled="loading || !input.trim()"
          aria-label="보내기"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M5 12h12M13 8l4 4-4 4"
              fill="none"
              stroke="currentColor"
              stroke-width="1.75"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </button>
      </form>

      <p v-if="error" class="chat-error">{{ errorText }}</p>
    </div>
  </div>
</template>

<script>
import { api } from '../api'
import { friendlyRegisterError } from '../utils/registerErrors'

const EXAMPLE_PROMPTS = [
  '외로운 밤에 읽을 책',
  '위로가 되는 문장',
  '《데미안》 같은 소설',
  '짧고 감각적인 문장',
  '잔잔한 한국 소설',
]

export default {
  name: 'ChatBot',
  data() {
    return {
      open: false,
      input: '',
      loading: false,
      error: '',
      messages: [],
      examples: EXAMPLE_PROMPTS,
    }
  },
  computed: {
    showIntro() {
      return !this.messages.length && !this.loading
    },
    errorText() {
      return friendlyRegisterError(this.error)
    },
  },
  methods: {
    toggle() {
      this.open = !this.open
      this.error = ''
    },
    async send(text) {
      const messageText = (typeof text === 'string' ? text : this.input).trim()
      if (!messageText || this.loading) return

      this.input = ''
      this.error = ''
      this.messages.push({ role: 'user', content: messageText })
      this.loading = true
      this.$nextTick(this.scrollToBottom)

      try {
        const history = this.messages
          .slice(0, -1)
          .map((m) => ({ role: m.role, content: m.content }))

        const res = await api.chat(messageText, history)
        this.messages.push({
          role: 'assistant',
          content: res.reply,
          recommendations: res.recommendations || [],
        })
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
        this.$nextTick(this.scrollToBottom)
      }
    },
    scrollToBottom() {
      const el = this.$refs.messagesEl
      if (el) el.scrollTop = el.scrollHeight
    },
  },
}
</script>

<style scoped>
.chatbot {
  position: fixed;
  right: max(14px, calc((100vw - var(--glt-app-width)) / 2 + 14px));
  bottom: calc(var(--glt-bottom-nav-height) + env(safe-area-inset-bottom, 0px) + 20px);
  z-index: 200;
}

.chat-fab {
  width: 52px;
  height: 52px;
  display: grid;
  place-items: center;
  border: none;
  border-radius: 50%;
  background: var(--glt-accent);
  color: #fff;
  box-shadow: var(--glt-shadow-md);
  cursor: pointer;
  transition: transform var(--glt-duration) var(--glt-ease);
}

.chat-fab:hover {
  transform: scale(1.05);
}

.chat-fab-icon {
  width: 22px;
  height: 22px;
  display: block;
}

.chat-panel {
  position: absolute;
  right: 0;
  bottom: 64px;
  width: min(340px, calc(var(--glt-app-width) - 24px));
  height: min(460px, calc(100dvh - var(--glt-bottom-nav-height) - env(safe-area-inset-bottom, 0px) - 108px));
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  padding: 14px 16px 10px;
  border-bottom: 1px solid var(--glt-glass-border);
}

.chat-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--glt-ink);
}

.chat-desc {
  margin: 6px 0 0;
  font-size: 0.78rem;
  line-height: 1.55;
  color: var(--glt-ink-secondary);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-intro {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.chat-suggestions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.suggestions-label {
  margin: 0;
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--glt-ink-tertiary);
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.suggestion-chip {
  width: 100%;
  text-align: left;
  padding: 11px 13px;
  border: 1px solid var(--glt-glass-border);
  border-radius: 16px;
  border-bottom-left-radius: 6px;
  background: var(--glt-surface);
  color: var(--glt-ink-secondary);
  font-size: 0.82rem;
  line-height: 1.5;
  cursor: pointer;
  word-break: keep-all;
  transition: background var(--glt-duration), border-color var(--glt-duration);
}

.suggestion-chip:hover:not(:disabled) {
  background: var(--glt-accent-soft);
  border-color: var(--glt-accent-muted);
  color: var(--glt-ink);
}

.suggestion-chip:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.chat-message {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chat-message--user {
  align-items: flex-end;
}

.chat-message--assistant {
  align-items: flex-start;
}

.chat-bubble {
  margin: 0;
  max-width: 92%;
  padding: 10px 12px;
  border-radius: 14px;
  font-size: 0.84rem;
  line-height: 1.55;
  word-break: keep-all;
}

.chat-message--user .chat-bubble {
  background: var(--glt-accent);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.chat-message--assistant .chat-bubble {
  background: var(--glt-surface);
  border: 1px solid var(--glt-glass-border);
  color: var(--glt-ink);
  border-bottom-left-radius: 4px;
}

.chat-bubble--loading {
  color: var(--glt-ink-tertiary);
}

.chat-recs {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rec-card {
  padding: 10px 12px;
  border-radius: var(--glt-radius-md);
  background: var(--glt-surface);
  border: 1px solid var(--glt-glass-border);
}

.rec-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.rec-head strong {
  font-size: 0.82rem;
  color: var(--glt-ink);
}

.rec-badge {
  flex-shrink: 0;
  font-size: 0.62rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--glt-radius-full);
}

.rec-badge--library {
  background: var(--glt-accent-soft);
  color: var(--glt-accent-hover);
}

.rec-badge--ai {
  background: var(--glt-bg-subtle);
  color: var(--glt-ink-tertiary);
}

.rec-author {
  margin: 4px 0 0;
  font-size: 0.74rem;
  color: var(--glt-ink-secondary);
}

.rec-reason {
  margin: 6px 0 0;
  font-size: 0.78rem;
  line-height: 1.55;
  color: var(--glt-ink);
}

.chat-input {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--glt-glass-border);
}

.chat-input input {
  flex: 1;
  min-width: 0;
  padding: 10px 12px;
  border: 1px solid var(--glt-glass-border);
  border-radius: var(--glt-radius-full);
  background: var(--glt-surface);
  color: var(--glt-ink);
  font-size: 0.84rem;
}

.chat-input input:focus {
  outline: none;
  border-color: var(--glt-accent-muted);
  box-shadow: 0 0 0 3px var(--glt-accent-soft);
}

.chat-send-btn {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: grid;
  place-items: center;
  border: none;
  border-radius: 50%;
  background: var(--glt-accent);
  color: #fff;
  cursor: pointer;
  transition: background var(--glt-duration), opacity var(--glt-duration);
}

.chat-send-btn:hover:not(:disabled) {
  background: var(--glt-accent-hover);
}

.chat-send-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.chat-send-btn svg {
  width: 18px;
  height: 18px;
  display: block;
}

.chat-error {
  margin: 0;
  padding: 0 16px 12px;
  font-size: 0.78rem;
  color: var(--glt-ink-secondary);
  line-height: 1.5;
  text-align: center;
}
</style>
