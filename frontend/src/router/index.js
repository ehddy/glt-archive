import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import QuoteDetailView from '../views/QuoteDetailView.vue'
import RegisterView from '../views/RegisterView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/quotes/:id', name: 'quote-detail', component: QuoteDetailView },
    { path: '/register', name: 'register', component: RegisterView },
  ],
})

export default router
