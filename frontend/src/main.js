import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/style.css'
import { applyTheme } from './utils/theme'

applyTheme('mist')

createApp(App).use(router).mount('#app')
