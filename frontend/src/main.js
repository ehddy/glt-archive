import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/style.css'
import { api } from './api'
import { loadAuthSession } from './utils/auth'
import { applyTheme } from './utils/theme'

applyTheme('mist')

loadAuthSession(api).finally(() => {
  createApp(App).use(router).mount('#app')
})
