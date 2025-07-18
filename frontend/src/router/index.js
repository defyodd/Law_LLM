import { createRouter, createWebHistory } from 'vue-router'
import { useTokenStore } from '@/stores/token'
import { ElMessage } from 'element-plus'

const routes = [
  {
    path: '/',
    redirect: '/library' 
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Login.vue'),
    meta: { hideLayout: true }
  },
  {
    path: '/library',
    name: 'library',
    component: () => import('@/views/Library.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/chat',
    name: 'chat',
    component: () => import('@/views/ChatPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/writer',
    name: 'writer',
    component: () => import('@/views/DocWriter.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/law/:id',
    name: 'LawDetail',
    component: () => import('@/views/LawDetail.vue')
  },
  // 404页面路由
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { hideLayout: true, requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫，确保身份验证
router.beforeEach((to, from, next) => {
  const tokenStore = useTokenStore()
  
  // 如果路由需要身份验证
  if (to.meta.requiresAuth) {
    // 检查是否有token
    if (!tokenStore.token) {
      ElMessage.warning('请先登录')
      next('/login')
      return
    }
  }
  
  // 如果已登录用户访问登录页，重定向
  if (to.path === '/login' && tokenStore.token) {
    next('/library')
    return
  }
  
  next()
})

export default router

