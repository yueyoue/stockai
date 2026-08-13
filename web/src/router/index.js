import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { guest: true },
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('../views/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../views/MarketDashboard.vue'),
      },
      {
        path: '/reports',
        name: 'Reports',
        component: () => import('../views/Reports.vue'),
      },
      {
        path: '/news',
        name: 'News',
        component: () => import('../views/News.vue'),
      },
      {
        path: '/watchlist',
        name: 'Watchlist',
        component: () => import('../views/Watchlist.vue'),
      },
      {
        path: '/stock/:code',
        name: 'StockDetail',
        component: () => import('../views/StockDetail.vue'),
      },
      {
        path: '/push',
        name: 'PushSettings',
        component: () => import('../views/PushSettings.vue'),
      },
      {
        path: '/admin',
        name: 'Admin',
        component: () => import('../views/Admin.vue'),
        meta: { admin: true },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next('/login')
  } else if (to.meta.guest && authStore.isLoggedIn) {
    next('/')
  } else if (to.meta.admin && !authStore.isAdmin) {
    next('/')
  } else {
    next()
  }
})

export default router
