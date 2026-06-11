<template>
  <div class="app">
    <div class="app-frame">
      <div class="app-bg" aria-hidden="true">
        <div class="app-bg-warm" />
      </div>

      <header class="header">
        <div class="glt-container header-inner">
          <router-link to="/" class="brand">
            <span class="brand-mark">G</span>
            <strong class="brand-name">괴테는 모든 것을 말했다</strong>
          </router-link>
          <nav class="nav">
            <div class="nav-group">
              <router-link to="/" class="nav-link">검색</router-link>
              <router-link to="/novels" class="nav-link">작품</router-link>
              <router-link to="/quotes" class="nav-link">구절</router-link>
              <router-link to="/saved" class="nav-link">{{ COLLECT.nav }}</router-link>
              <router-link
                :to="registerNavTarget"
                class="nav-link"
                :class="{ 'nav-link-cta': $route.name !== 'quote-detail' && $route.name !== 'register' }"
              >
                + 등록
              </router-link>
            </div>
          </nav>
        </div>
      </header>

      <main class="main">
        <router-view />
      </main>

      <ChatBot />
    </div>
  </div>
</template>

<script>
import ChatBot from './components/ChatBot.vue'
import { COLLECT } from './utils/collectLabels'
import { registerRouteForQuote } from './utils/registerBook'

export default {
  name: 'App',
  components: { ChatBot },
  data() {
    return { COLLECT }
  },
  computed: {
    registerNavTarget() {
      if (this.$route.name === 'quote-detail' && this.$route.params.id) {
        return registerRouteForQuote(this.$route.params.id)
      }
      return { path: '/register' }
    },
  },
}
</script>

<style scoped>
.app {
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  justify-content: center;
  background: var(--glt-bg-outer);
}

.app-frame {
  position: relative;
  width: min(100%, var(--glt-app-width));
  max-width: 100%;
  min-height: 100vh;
  min-height: 100dvh;
  background: var(--glt-bg);
  box-shadow: var(--glt-shadow-app);
  overflow-x: clip;
  overflow-y: visible;
}

@media (min-width: 1000px) {
  .app {
    padding: 24px 16px;
  }

  .app-frame {
    width: var(--glt-app-width);
    min-height: calc(100dvh - 48px);
    border-radius: 28px;
    border: 1px solid var(--glt-glass-border);
    overflow: hidden;
  }
}

.app-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.app-bg-warm {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 90% 60% at 50% -10%, rgba(253, 238, 228, 0.9) 0%, transparent 55%),
    radial-gradient(ellipse 70% 50% at 100% 80%, rgba(232, 220, 200, 0.35) 0%, transparent 50%);
}

.header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(250, 246, 240, 0.92);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--glt-glass-border);
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--glt-space-3);
  padding-top: var(--glt-space-3);
  padding-bottom: var(--glt-space-3);
}

.brand {
  display: flex;
  align-items: center;
  gap: var(--glt-space-2);
  text-decoration: none;
  min-width: 0;
}

.brand-mark {
  width: 34px;
  height: 34px;
  flex-shrink: 0;
  display: grid;
  place-items: center;
  border-radius: 10px;
  background: var(--glt-accent);
  color: #fff;
  font-family: var(--glt-font-serif);
  font-size: 0.95rem;
  font-weight: 700;
}

.brand-name {
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--glt-ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.nav-group {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 3px;
  border-radius: var(--glt-radius-full);
  background: rgba(255, 255, 255, 0.55);
  border: 1px solid var(--glt-glass-border);
}

.nav-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 7px 10px;
  border-radius: var(--glt-radius-full);
  font-size: 0.8rem;
  font-weight: 600;
  line-height: 1;
  white-space: nowrap;
  color: var(--glt-ink-secondary);
  text-decoration: none;
  transition: all var(--glt-duration) var(--glt-ease);
}

.nav-link:hover {
  color: var(--glt-ink);
  background: var(--glt-overlay);
}

.nav-link.router-link-active {
  color: var(--glt-accent-hover);
  background: var(--glt-accent-soft);
}

.nav-link-cta.router-link-active,
.nav-link-cta {
  background: var(--glt-accent);
  color: #fff;
}

.nav-link-cta:hover {
  background: var(--glt-accent-hover);
  color: #fff;
}

.main {
  position: relative;
  z-index: 1;
  padding: var(--glt-space-4) 0 var(--glt-space-8);
}
</style>
