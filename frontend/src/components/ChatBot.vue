<template>
  <div class="chatbot">
    <button
      class="chat-fab"
      type="button"
      :aria-expanded="open"
      aria-label="책 추천"
      @click="toggle"
    >
      <span v-if="!open">📚</span>
      <span v-else>✕</span>
    </button>

    <div v-if="open" class="chat-panel glt-card">
      <header class="chat-header">
        <h2 class="chat-title">책 추천</h2>
      </header>

      <div ref="messagesEl" class="chat-messages">

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
                <span v-if="rec.in_library" class="rec-badge">라이브러리</span>
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

      <form class="chat-input" @submit.prevent="send">
        <input
          v-model="input"
          type="text"
          placeholder="메시지"
          :disabled="loading"
        />
        <button class="glt-btn glt-btn-primary" type="submit" :disabled="loading || !input.trim()">
          전송
        </button>
      </form>

      <p v-if="error" class="chat-error">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import { api } from '../api'

export default {
  name: 'ChatBot',
  data() {
    return {
      open: false,
      input: '',
      loading: false,
      error: '',
      messages: [],
    }
  },
  methods: {
    toggle() {
      this.open = !this.open
      this.error = ''
    },
    async send() {
      const text = this.input.trim()
      if (!text || this.loading) return

      this.input = ''
      this.error = ''
      this.messages.push({ role: 'user', content: text })
      this.loading = true
      this.$nextTick(this.scrollToBottom)

      try {
        const history = this.messages
          .slice(0, -1)
          .map((m) => ({ role: m.role, content: m.content }))

        const res = await api.chat(text, history)
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
  right: max(16px, calc((100vw - var(--glt-app-width)) / 2 + 16px));
  bottom: 20px;
  z-index: 200;
}

@media (max-width: 999px) {
  .chatbot {
    right: 16px;
  }
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

.chat-panel {
  position: absolute;
  right: 0;
  bottom: 64px;
  width: min(360px, calc(100vw - 32px));
  height: min(520px, calc(100dvh - 120px));
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
  margin: 4px 0 0;
  font-size: 0.75rem;
  color: var(--glt-ink-tertiary);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-empty {
  font-size: 0.82rem;
  line-height: 1.6;
  color: var(--glt-ink-tertiary);
  text-align: center;
  padding: 24px 8px;
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
  background: var(--glt-accent-soft);
  color: var(--glt-accent-hover);
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
  color: var(--glt-accent-hover);
  line-height: 1.4;
}
</style>
