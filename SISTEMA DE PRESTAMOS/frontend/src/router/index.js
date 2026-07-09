import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/', name: 'home', component: () => import('../views/HomeView.vue') },
  { path: '/login', name: 'login', component: () => import('../views/LoginView.vue') },
  { path: '/registro', name: 'register', component: () => import('../views/RegisterView.vue') },
  { path: '/oauth-callback', name: 'oauth-callback', component: () => import('../views/OAuthCallbackView.vue') },
  { path: '/productos/:id', name: 'product-detail', component: () => import('../views/ProductDetailView.vue'), props: true },
  { path: '/publicar', name: 'publish-product', component: () => import('../views/PublishProductView.vue'), meta: { requiresAuth: true, role: 'rentador' } },
  { path: '/mis-reservas', name: 'reservations', component: () => import('../views/ReservationsView.vue'), meta: { requiresAuth: true } },
  { path: '/favoritos', name: 'favorites', component: () => import('../views/FavoritesView.vue'), meta: { requiresAuth: true } },
  { path: '/perfil', name: 'profile', component: () => import('../views/ProfileView.vue'), meta: { requiresAuth: true } },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('../views/NotFoundView.vue') }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  // Guarda por rol: si la ruta exige un rol que el usuario no tiene,
  // lo enviamos al perfil para que pueda activarlo (ej. ser rentador).
  if (to.meta.role && auth.isAuthenticated && !auth.hasRole(to.meta.role)) {
    return { name: 'profile', query: { needRole: to.meta.role, redirect: to.fullPath } }
  }
  return true
})

export default router
