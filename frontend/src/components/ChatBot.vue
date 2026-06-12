<template>
  <div class="chatbot">
    <button
      class="chat-fab"
      type="button"
      :aria-expanded="open"
      aria-label="AI 책 추천"
      @click="toggle"
    >
      <span v-if="!open" class="chat-fab-icon">📚</span>
      <span v-else>✕</span>
    </button>

    <div v-if="open" class="chat-panel glt-card">
      <header class="chat-header">
        <h2 class="chat-title">AI 책 추천</h2>
        <p class="chat-desc">
          기분이나 좋아하는 책을 알려주세요. 등록된 도서와 AI가 아는 책을 함께 추천해 드려요.
        </p>
      </header>

      <div ref="messagesEl" class="chat-messages">
        <div v-if="showIntro" class="chat-intro">
          <div class="chat-message chat-message--assistant">
            <p class="chat-bubble">
              안녕하세요. 읽고 싶은 분위기나 떠오르는 책을 말씀해 주세요.
              우리 서비스에 등록된 도서가 있으면 함께 보여 드리고,
              그밖에 어울리는 책도 AI가 추천해 드려요.
            </p>
          </div>

          <div class="chat-suggestions">
            <p class="suggestions-label">예시를 눌러 바로 물어보기</p>
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
                <span v-if="rec.in_library" class="rec-badge rec-badge--library">등록된 도서</span>
                <span v-else class="rec-badge rec-badge--ai">AI 추천</span>
              </div>
              <p class="rec-author">{{ rec.author }}</p>
              <p class="rec-reason">{{ rec.reason }}</p>
            </article>
          </div>
        </div>

        <div v-if="loading" class="chat-message chat-message--assistant">
          <p class="chat-bubble chat-bubble--loading">추천하고 있어요…</p>
        </div>
      </div>

      <form class="chat-input" @submit.prevent="send()">
        <input
          v-model="input"
          type="text"
          placeholder="예: 차분한 밤에 읽을 책"
          :disabled="loading"
        />
        <button class="glt-btn glt-btn-primary" type="submit" :disabled="loading || !input.trim()">
          보내기
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
  '외로운 밤에 읽기 좋은 책 추천해 주세요',
  '슬플 때 위로가 되는 문장이 있는 작품이요',
  '《데미안》 같은 성장 소설 찾고 있어요',
  '짧고 감각적인 문장이 많은 책이요',
  '한국 소설 중에 잔잔한 분위기의 책이요',
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
  bottom: calc(var(--glt-bottom-nav-height) + env(safe-area-inset-bottom, 0px) + 12px);
  z-index: 200;
}

.chat-fab {
  width: 52px;
  height: 52px;
  border: none;
  border-radius: 50%;
  background: var(--glt-accent);
  color: #fff;
  font-size: 1.2rem;
  box-shadow: var(--glt-shadow-md);
  cursor: pointer;
  transition: transform var(--glt-duration) var(--glt-ease);
}

.chat-fab:hover {
  transform: scale(1.05);
}

.chat-fab-icon {
  line-height: 1;
}

.chat-panel {
  position: absolute;
  right: 0;
  bottom: 64px;
  width: min(340px, calc(var(--glt-app-width) - 24px));
  height: min(460px, calc(100dvh - var(--glt-bottom-nav-height) - env(safe-area-inset-bottom, 0px) - 100px));
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

.chat-input .glt-btn {
  padding: 10px 14px;
  font-size: 0.8rem;
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
