<template>
  <div class="auth-modal" role="dialog" :aria-label="title">
    <div class="auth-modal-card">
      <button type="button" class="auth-modal-close" aria-label="닫기" @click="close">
        <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
          <path
            d="M6 6l12 12M18 6L6 18"
            fill="none"
            stroke="currentColor"
            stroke-width="1.75"
            stroke-linecap="round"
          />
        </svg>
      </button>

      <header class="auth-modal-head">
        <h1 class="auth-modal-title">{{ title }}</h1>
        <p v-if="subtitle" class="auth-modal-sub">{{ subtitle }}</p>
      </header>

      <div class="auth-modal-body">
        <slot />
      </div>

      <footer v-if="$slots.footer" class="auth-modal-foot">
        <slot name="footer" />
      </footer>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AuthSheet',
  props: {
    title: { type: String, required: true },
    subtitle: { type: String, default: '' },
  },
  methods: {
    close() {
      if (window.history.length > 1) {
        this.$router.back()
      } else {
        this.$router.push('/')
      }
    },
  },
}
</script>

<style scoped>
.auth-modal {
  position: fixed;
  inset: 0;
  z-index: 160;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: max(20px, env(safe-area-inset-top, 0px)) 20px max(20px, env(safe-area-inset-bottom, 0px));
  pointer-events: none;
}

.auth-modal-card {
  position: relative;
  pointer-events: auto;
  width: 100%;
  max-width: 340px;
  max-height: calc(100dvh - 40px);
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  background: var(--glt-surface);
  border: 1px solid rgba(212, 195, 170, 0.45);
  border-radius: 20px;
  box-shadow: 0 24px 56px rgba(61, 52, 41, 0.16);
  padding: 28px 22px 22px;
}

.auth-modal-close {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  border: none;
  border-radius: 50%;
  background: transparent;
  color: var(--glt-ink-tertiary);
  cursor: pointer;
  transition: color var(--glt-duration), background var(--glt-duration);
}

.auth-modal-close:hover {
  color: var(--glt-ink-secondary);
  background: var(--glt-bg-subtle);
}

.auth-modal-head {
  text-align: center;
  padding: 0 28px 20px;
}

.auth-modal-title {
  margin: 0;
  font-size: 1.12rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--glt-ink);
}

.auth-modal-sub {
  margin: 8px 0 0;
  font-size: 0.86rem;
  line-height: 1.55;
  color: var(--glt-ink-secondary);
}

.auth-modal-body {
  display: flex;
  flex-direction: column;
  gap: var(--glt-space-3);
}

.auth-modal-foot {
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid rgba(226, 213, 196, 0.65);
  text-align: center;
  font-size: 0.86rem;
  line-height: 1.5;
  color: var(--glt-ink-secondary);
}

.auth-modal-foot :deep(a) {
  color: var(--glt-accent-hover);
  font-weight: 600;
  text-decoration: none;
  margin-left: 4px;
}
</style>
