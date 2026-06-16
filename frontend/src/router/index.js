import { createRouter, createWebHistory } from 'vue-router'
import { isLoggedIn } from '../utils/auth'
import { isPageLoading } from '../utils/pageLoading'
import AiSearchView from '../views/AiSearchView.vue'
import HomeView from '../views/HomeView.vue'
import NovelDetailView from '../views/NovelDetailView.vue'
import NovelsView from '../views/NovelsView.vue'
import QuoteDetailView from '../views/QuoteDetailView.vue'
import QuotesBrowseView from '../views/QuotesBrowseView.vue'
import RegisterView from '../views/RegisterView.vue'
import LoginView from '../views/LoginView.vue'
import SignupView from '../views/SignupView.vue'
import SavedView from '../views/SavedView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/ai-search', name: 'ai-search', component: AiSearchView },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/signup', name: 'signup', component: SignupView },
    { path: '/saved', name: 'saved', component: SavedView },
    { path: '/novels', name: 'novels', component: NovelsView },
    { path: '/novels/:id', name: 'novel-detail', component: NovelDetailView },
    { path: '/quotes', name: 'quotes-browse', component: QuotesBrowseView },
    { path: '/quotes/:id', name: 'quote-detail', component: QuoteDetailView },
    { path: '/register', name: 'register', component: RegisterView },
  ],
})

router.beforeEach((to, from, next) => {
  if (isPageLoading() && to.fullPath !== from.fullPath) {
    next(false)
    return
  }
  if (to.name === 'register' && !isLoggedIn()) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }
  next()
})

export default router
