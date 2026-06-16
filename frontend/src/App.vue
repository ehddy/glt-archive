<template>

  <div class="app">

    <div class="app-frame">

      <div class="app-bg" aria-hidden="true">

        <div class="app-bg-warm" />

      </div>



      <main class="main">

        <transition name="register-backdrop">
          <button
            v-if="isSheetOpen"
            type="button"
            class="register-backdrop"
            :aria-label="sheetCloseLabel"
            @click="closeSheet"
          />
        </transition>

        <router-view v-slot="{ Component, route }">
          <component
            v-if="isSheetOpen && backgroundView"
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



      <nav v-if="!isSheetOpen" class="bottom-nav" aria-label="주 메뉴">

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

        <div class="tab-item tab-item--empty" aria-hidden="true"></div>

        <router-link :to="{ name: 'saved' }" class="tab-item" aria-label="나">

          <svg class="tab-icon" viewBox="0 0 24 24" aria-hidden="true">

            <circle cx="12" cy="8.5" r="3.5" fill="none" stroke="currentColor" stroke-width="1.75" />

            <path
              d="M4 20.5c0-4.1 3.6-7 8-7s8 2.9 8 7"
              fill="none"
              stroke="currentColor"
              stroke-width="1.75"
              stroke-linecap="round"
            />

          </svg>

        </router-link>

      </nav>



      <LoadingOverlay
        v-if="pageLoading.count > 0"
        :message="pageLoading.message"
      />

      <ChatBot v-if="!isSheetOpen && pageLoading.count === 0" />

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
import MyLibraryView from './views/MyLibraryView.vue'
import MyProfileView from './views/MyProfileView.vue'
import UserProfileView from './views/UserProfileView.vue'
import NovelsView from './views/NovelsView.vue'
import QuotesBrowseView from './views/QuotesBrowseView.vue'
const SHEET_ROUTE_NAMES = new Set(['register', 'login', 'signup'])
const AUTH_MODAL_ROUTES = new Set(['login', 'signup'])

const ROUTE_VIEWS = {
  home: HomeView,
  'ai-search': AiSearchView,
  saved: UserProfileView,
  novels: NovelsView,
  'my-library': MyLibraryView,
  'my-profile': MyProfileView,
  'user-profile': UserProfileView,
  'novel-detail': NovelDetailView,
  'quotes-browse': QuotesBrowseView,
}



export default {

  name: 'App',

  components: { ChatBot, LoadingOverlay },

  data() {

    return {
      pageLoading,
      pageTransition: 'page-fade',
      lastRouteName: null,
      lastRouteFullPath: '/',
    }

  },

  computed: {

    isSheetOpen() {
      return SHEET_ROUTE_NAMES.has(this.$route.name)
    },

    sheetCloseLabel() {
      if (this.$route.name === 'register') return '등록 닫기'
      if (this.$route.name === 'signup') return '회원가입 닫기'
      return '로그인 닫기'
    },

    backgroundView() {
      if (!this.isSheetOpen || !this.lastRouteName) return null
      return ROUTE_VIEWS[this.lastRouteName] || null
    },

    registerNavTarget() {
      return { name: 'register' }
    },

  },

  watch: {
    $route: {
      immediate: true,
      handler(to, from) {
        const toSheet = SHEET_ROUTE_NAMES.has(to.name)
        const fromSheet = SHEET_ROUTE_NAMES.has(from?.name)

        if (toSheet) {
          if (from?.name && !fromSheet) {
            this.lastRouteName = from.name
            this.lastRouteFullPath = from.fullPath
          }
          if (AUTH_MODAL_ROUTES.has(to.name)) {
            this.pageTransition = AUTH_MODAL_ROUTES.has(from?.name) ? 'page-fade' : 'modal-pop'
          } else {
            this.pageTransition = fromSheet ? 'page-fade' : 'sheet-up'
          }
          document.body.style.overflow = 'hidden'
          return
        }

        if (fromSheet) {
          this.pageTransition = AUTH_MODAL_ROUTES.has(from?.name) ? 'modal-pop' : 'sheet-down'
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
    closeSheet() {
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

  height: 100dvh;

  display: flex;

  justify-content: center;

  overflow: hidden;

  background: var(--glt-bg-outer);

}



.app-frame {

  position: relative;

  width: 100%;

  max-width: var(--glt-app-width);

  height: 100dvh;

  background: var(--glt-bg);

  box-shadow: var(--glt-shadow-app);

  overflow-x: clip;

  overflow-y: scroll;

  display: flex;

  flex-direction: column;

  scrollbar-width: thin;

  scrollbar-color: rgba(170, 145, 120, 0.3) transparent;

}

.app-frame::-webkit-scrollbar {

  width: 5px;

}

.app-frame::-webkit-scrollbar-track {

  background: transparent;

}

.app-frame::-webkit-scrollbar-thumb {

  background: rgba(170, 145, 120, 0.35);

  border-radius: 999px;

}

.app-frame::-webkit-scrollbar-thumb:hover {

  background: rgba(170, 145, 120, 0.6);

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

.main:has(.register--sheet),
.main:has(.auth-modal),
.main:has(.quote-sheet) {

  z-index: 130;

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

.modal-pop-enter-active,
.modal-pop-leave-active {
  transition:
    opacity 0.28s var(--glt-ease),
    transform 0.28s var(--glt-ease);
}

.modal-pop-enter-from,
.modal-pop-leave-to {
  opacity: 0;
  transform: scale(0.96) translateY(10px);
}

</style>


