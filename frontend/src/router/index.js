import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import NovelDetailView from '../views/NovelDetailView.vue'
import NovelsView from '../views/NovelsView.vue'
import QuoteDetailView from '../views/QuoteDetailView.vue'
import QuotesBrowseView from '../views/QuotesBrowseView.vue'
import RegisterView from '../views/RegisterView.vue'
import SavedView from '../views/SavedView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/saved', name: 'saved', component: SavedView },
    { path: '/novels', name: 'novels', component: NovelsView },
    { path: '/novels/:id', name: 'novel-detail', component: NovelDetailView },
    { path: '/quotes', name: 'quotes-browse', component: QuotesBrowseView },
    { path: '/quotes/:id', name: 'quote-detail', component: QuoteDetailView },
    { path: '/register', name: 'register', component: RegisterView },
  ],
})

export default router
