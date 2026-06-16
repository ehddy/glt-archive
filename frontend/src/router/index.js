import { createRouter, createWebHistory } from 'vue-router'
import { isLoggedIn } from '../utils/auth'
import { isPageLoading } from '../utils/pageLoading'
import AiSearchView from '../views/AiSearchView.vue'
import HomeView from '../views/HomeView.vue'
import NovelDetailView from '../views/NovelDetailView.vue'
import NovelsView from '../views/NovelsView.vue'
import MyLibraryView from '../views/MyLibraryView.vue'
import QuotesBrowseView from '../views/QuotesBrowseView.vue'
import RegisterView from '../views/RegisterView.vue'
import LoginView from '../views/LoginView.vue'
import SignupView from '../views/SignupView.vue'
import SavedView from '../views/SavedView.vue'
import MyProfileView from '../views/MyProfileView.vue'
import UserProfileView from '../views/UserProfileView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/ai-search', name: 'ai-search', component: AiSearchView },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/signup', name: 'signup', component: SignupView },
    { path: '/saved', name: 'saved', component: SavedView },
    { path: '/my-profile', name: 'my-profile', component: MyProfileView },
    { path: '/novels', name: 'novels', component: NovelsView },
    { path: '/my-library', name: 'my-library', component: MyLibraryView },
    { path: '/novels/:id', name: 'novel-detail', component: NovelDetailView },
    { path: '/quotes', name: 'quotes-browse', component: QuotesBrowseView },
    { path: '/register', name: 'register', component: RegisterView },
    { path: '/users/:id', name: 'user-profile', component: UserProfileView },
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
