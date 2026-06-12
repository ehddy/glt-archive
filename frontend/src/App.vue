<template>

  <div class="app">

    <div class="app-frame">

      <div class="app-bg" aria-hidden="true">

        <div class="app-bg-warm" />

      </div>



      <main class="main">

        <transition name="register-backdrop">
          <button
            v-if="isRegisterOpen"
            type="button"
            class="register-backdrop"
            aria-label="등록 닫기"
            @click="closeRegister"
          />
        </transition>

        <router-view v-slot="{ Component, route }">
          <component
            v-if="route.name === 'register' && backgroundView"
            :is="backgroundView"
            :key="lastRouteFullPath"
            class="route-background"
            aria-hidden="true"
          />
          <transition :name="pageTransition">
            <component :is="Component" :key="route.fullPath" />
          </transition>
        </router-view>

      </main>



      <nav class="bottom-nav" aria-label="주 메뉴">

        <router-link :to="{ name: 'home' }" class="tab-item" aria-label="홈">

          <svg class="tab-icon" viewBox="0 0 24 24" aria-hidden="true">

            <circle cx="11" cy="11" r="6.5" fill="none" stroke="currentColor" stroke-width="1.75" />

            <path d="M16.5 16.5L20 20" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" />

          </svg>

        </router-link>

        <router-link :to="{ name: 'ai-search' }" class="tab-item" aria-label="AI">

          <svg class="tab-icon" viewBox="0 0 24 24" aria-hidden="true">

            <path
              d="M12 4.5l.9 3.1 3.1.9-3.1.9-.9 3.1-.9-3.1-3.1-.9 3.1-.9.9-3.1z"
              fill="none"
              stroke="currentColor"
              stroke-width="1.75"
              stroke-linejoin="round"
            />

            <path
              d="M18 15l.5 1.7 1.7.5-1.7.5-.5 1.7-.5-1.7-1.7-.5 1.7-.5.5-1.7z"
              fill="none"
              stroke="currentColor"
              stroke-width="1.75"
              stroke-linejoin="round"
            />

          </svg>

        </router-link>

        <router-link :to="registerNavTarget" class="tab-item tab-item--register" aria-label="등록">

          <span class="tab-register-btn">+</span>

        </router-link>

        <router-link

          :to="{ name: 'novels' }"

          class="tab-item"

          :class="{ 'is-tab-active': $route.name === 'novel-detail' }"
          aria-label="책장"

        >

          <svg class="tab-icon" viewBox="0 0 24 24" aria-hidden="true">

            <path d="M12 7v13" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" />

            <path
              d="M5 5.2A2.2 2.2 0 0 1 7.2 3H12v17H7.2A2.2 2.2 0 0 1 5 17.8V5.2z"
              fill="none"
              stroke="currentColor"
              stroke-width="1.75"
              stroke-linejoin="round"
            />

            <path
              d="M19 5.2A2.2 2.2 0 0 0 16.8 3H12v17h4.8A2.2 2.2 0 0 0 19 17.8V5.2z"
              fill="none"
              stroke="currentColor"
              stroke-width="1.75"
              stroke-linejoin="round"
            />

          </svg>

        </router-link>

        <router-link :to="{ name: 'saved' }" class="tab-item" aria-label="담은">

          <svg class="tab-icon" viewBox="0 0 24 24" aria-hidden="true">

            <path
              d="M12 20.2l-1-1C6.2 14.8 4 12.6 4 10a4 4 0 0 1 7-2.4A4 4 0 0 1 20 10c0 2.6-2.2 4.8-7 9.2l-1 1z"
              fill="none"
              stroke="currentColor"
              stroke-width="1.75"
              stroke-linecap="round"
              stroke-linejoin="round"
            />

          </svg>

        </router-link>

      </nav>



      <LoadingOverlay
        v-if="pageLoading.count > 0"
        :message="pageLoading.message"
      />

      <ChatBot v-if="$route.name !== 'register' && pageLoading.count === 0" />

    </div>

  </div>

</template>



<script>

import ChatBot from './components/ChatBot.vue'
import LoadingOverlay from './components/LoadingOverlay.vue'
import { pageLoading } from './utils/pageLoading'
import AiSearchView from './views/AiSearchView.vue'
import HomeView from './views/HomeView.vue'
import NovelDetailView from './views/NovelDetailView.vue'
import NovelsView from './views/NovelsView.vue'
import QuoteDetailView from './views/QuoteDetailView.vue'
import QuotesBrowseView from './views/QuotesBrowseView.vue'
import SavedView from './views/SavedView.vue'

import { COLLECT } from './utils/collectLabels'

import { registerRouteForQuote } from './utils/registerBook'

const ROUTE_VIEWS = {
  home: HomeView,
  'ai-search': AiSearchView,
  saved: SavedView,
  novels: NovelsView,
  'novel-detail': NovelDetailView,
  'quotes-browse': QuotesBrowseView,
  'quote-detail': QuoteDetailView,
}



export default {

  name: 'App',

  components: { ChatBot, LoadingOverlay },

  data() {

    return {
      COLLECT,
      pageLoading,
      pageTransition: 'page-fade',
      lastRouteName: null,
      lastRouteFullPath: '/',
    }

  },

  computed: {

    isRegisterOpen() {
      return this.$route.name === 'register'
    },

    backgroundView() {
      if (!this.isRegisterOpen || !this.lastRouteName) return null
      return ROUTE_VIEWS[this.lastRouteName] || null
    },

    registerNavTarget() {

      if (this.$route.name === 'quote-detail' && this.$route.params.id) {

        return registerRouteForQuote(this.$route.params.id)

      }

      return { name: 'register' }

    },

  },

  watch: {
    $route: {
      immediate: true,
      handler(to, from) {
        if (to.name === 'register') {
          if (from?.name && from.name !== 'register') {
            this.lastRouteName = from.name
            this.lastRouteFullPath = from.fullPath
          }
          this.pageTransition = 'sheet-up'
          document.body.style.overflow = 'hidden'
          return
        }

        if (from?.name === 'register') {
          this.pageTransition = 'sheet-down'
        } else {
          this.pageTransition = 'page-fade'
        }
        document.body.style.overflow = ''
      },
    },
  },

  beforeUnmount() {
    document.body.style.overflow = ''
  },

  methods: {
    closeRegister() {
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

.app {

  min-height: 100vh;

  min-height: 100dvh;

  display: flex;

  justify-content: center;

  background: var(--glt-bg-outer);

}



.app-frame {

  position: relative;

  width: 100%;

  max-width: var(--glt-app-width);

  min-height: 100vh;

  min-height: 100dvh;

  background: var(--glt-bg);

  box-shadow: var(--glt-shadow-app);

  overflow-x: clip;

  display: flex;

  flex-direction: column;

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

    radial-gradient(ellipse 90% 55% at 50% -8%, var(--glt-bg-warm-1) 0%, transparent 58%),

    radial-gradient(ellipse 65% 45% at 100% 85%, var(--glt-bg-warm-2) 0%, transparent 52%);

}



.main {

  position: relative;

  z-index: 1;

  flex: 1;

  padding: calc(var(--glt-safe-top) + var(--glt-space-3)) 0 var(--glt-page-bottom);

}



.bottom-nav {

  position: fixed;

  left: 50%;

  bottom: 0;

  transform: translateX(-50%);

  z-index: 120;

  width: 100%;

  max-width: var(--glt-app-width);

  display: grid;

  grid-template-columns: repeat(5, 1fr);

  align-items: center;

  gap: 2px;

  padding: 8px 10px calc(10px + env(safe-area-inset-bottom, 0px));

  background: var(--glt-nav-bg);

  backdrop-filter: blur(14px);

  border-top: 1px solid var(--glt-glass-border);

  box-shadow: 0 -4px 20px rgba(61, 52, 41, 0.06);

}



.tab-item {

  display: flex;

  flex-direction: column;

  align-items: center;

  justify-content: center;

  min-height: 44px;

  padding: 6px 2px;

  border-radius: 12px;

  text-decoration: none;

  color: var(--glt-ink-tertiary);

  transition: color var(--glt-duration), background var(--glt-duration);

}



.tab-icon {

  width: 24px;

  height: 24px;

  flex-shrink: 0;

  display: block;

}



.tab-item.router-link-active,

.tab-item.is-tab-active {

  color: var(--glt-accent-hover);

  background: var(--glt-accent-soft);

}



.tab-register-btn {

  width: 48px;

  height: 48px;

  display: grid;

  place-items: center;

  border-radius: 50%;

  background: var(--glt-accent);

  color: #fff;

  font-size: 1.45rem;

  font-weight: 500;

  line-height: 1;

  box-shadow: 0 4px 14px rgba(196, 105, 58, 0.35);

}



.tab-item--register.router-link-active .tab-register-btn {

  background: var(--glt-accent-hover);

}



.tab-item--register.router-link-active {

  background: transparent;

  color: var(--glt-accent-hover);

}



@media (min-width: 403px) {

  .app-frame {

    border-left: 1px solid var(--glt-glass-border);

    border-right: 1px solid var(--glt-glass-border);

  }

}



.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.22s var(--glt-ease);
}

.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
}

.route-background {
  pointer-events: none;
  user-select: none;
}

.register-backdrop {
  position: fixed;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  z-index: 140;
  width: 100%;
  max-width: var(--glt-app-width);
  height: 100dvh;
  border: none;
  padding: 0;
  background: var(--glt-backdrop);
  backdrop-filter: blur(2px);
  cursor: pointer;
}

.register-backdrop-enter-active,
.register-backdrop-leave-active {
  transition: opacity 0.3s var(--glt-ease);
}

.register-backdrop-enter-from,
.register-backdrop-leave-to {
  opacity: 0;
}

.sheet-up-enter-active,
.sheet-up-leave-active {
  transition: transform 0.36s var(--glt-ease);
}

.sheet-up-enter-from,
.sheet-up-leave-to {
  transform: translateY(100%);
}

.sheet-down-enter-active {
  transition: opacity 0.22s var(--glt-ease);
}

.sheet-down-enter-from {
  opacity: 0;
}

.sheet-down-leave-active {
  transition: transform 0.36s var(--glt-ease);
}

.sheet-down-leave-to {
  transform: translateY(100%);
}

</style>


