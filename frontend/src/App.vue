<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import useUserInfoStore from '@/stores/user'
import { useTokenStore } from '@/stores/token'

const router = useRouter()
const route = useRoute()
const userInfoStore = useUserInfoStore()
const tokenStore = useTokenStore()

// 添加路由就绪状态
const routerReady = ref(false)
const sidebarCollapsed = ref(false)
const showUserDropdown = ref(false)

// 添加退出动画状态
const isLoggingOut = ref(false)

const navItems = [
  { path: '/library', icon: 'fas fa-book', text: '法律文库' },
  { path: '/chat', icon: 'fas fa-robot', text: 'AI法律咨询' },
  { path: '/writer', icon: 'fas fa-file-signature', text: 'AI文书撰写' },
]

const navigateTo = (path) => {
  router.push(path)
}

// 获取用户信息
const userInfo = computed(() => userInfoStore.userInfo)

// 获取用户名首字母
const userInitial = computed(() => {
  return userInfo.value?.username ? userInfo.value.username.charAt(0).toUpperCase() : '用'
})

// 显示的用户名
const displayName = computed(() => {
  return userInfo.value?.username || '用户'
})

// 用户邮箱
const userEmail = computed(() => {
  return userInfo.value?.email || ''
})

// 退出登录
const logout = () => {
  // 开始退出动画
  isLoggingOut.value = true
  
  // 隐藏下拉框
  showUserDropdown.value = false
  
  // 等待动画完成后跳转
  setTimeout(() => {
    // 清除token和用户信息
    tokenStore.removeToken()
    userInfoStore.removeUserInfo()
    
    // 跳转到登录页
    router.push('/login')
    
    // 重置动画状态
    isLoggingOut.value = false
  }, 800) // 动画持续时间
}

// 点击外部关闭下拉框
const handleClickOutside = (event) => {
  const userProfile = document.querySelector('.user-profile')
  const dropdown = document.querySelector('.user-dropdown')
  
  if (userProfile && dropdown && 
      !userProfile.contains(event.target) && 
      !dropdown.contains(event.target)) {
    showUserDropdown.value = false
  }
}

onMounted(() => {
  // 等待路由系统完全初始化
  router.isReady().then(() => {
    routerReady.value = true
  })
  
  // 添加全局点击事件监听
  document.addEventListener('click', handleClickOutside)
})

// 判断是否需要隐藏布局 - 只有在路由就绪后才判断
const shouldHideLayout = computed(() => {
  if (!routerReady.value) {
    // 如果当前路径是登录页面，立即返回true
    return window.location.pathname === '/login' || window.location.pathname === '/'
  }
  return route.meta?.hideLayout === true
})

// 判断是否需要显示路由加载状态
const showRouterLoading = computed(() => {
  return !routerReady.value && !shouldHideLayout.value
})

// 添加过渡动画控制
const getTransitionName = (route) => {
  // 根据路由路径确定过渡动画类型
  const routeDepth = {
    '/library': 1,
    '/chat': 2,
    '/contracts': 3,
  }
  
  const currentDepth = routeDepth[route.path] || 1
  const previousPath = router.currentRoute.value?.path
  const previousDepth = routeDepth[previousPath] || 1
  
  // 根据导航方向选择动画
  if (currentDepth > previousDepth) {
    return 'slide-left'
  } else if (currentDepth < previousDepth) {
    return 'slide-right'
  } else {
    return 'fade'
  }
}

// 动画钩子函数
const onBeforeEnter = (el) => {
  el.style.opacity = '0'
  el.style.transform = 'translateY(20px)'
}

const onEnter = (el, done) => {
  el.offsetHeight // 强制重绘
  el.style.transition = 'all 0.4s cubic-bezier(0.55, 0, 0.1, 1)'
  el.style.opacity = '1'
  el.style.transform = 'translateY(0)'
  
  setTimeout(done, 400)
}

const onLeave = (el, done) => {
  el.style.transition = 'all 0.3s cubic-bezier(0.55, 0, 0.1, 1)'
  el.style.opacity = '0'
  el.style.transform = 'translateY(-20px)'
  
  setTimeout(done, 300)
}

// 确保路由完全就绪后再显示页面
onMounted(() => {
  // 等待路由系统完全初始化
  router.isReady().then(() => {
    routerReady.value = true
  })
})
</script>

<template>
  <div v-if="routerReady || shouldHideLayout">
    <div v-if="shouldHideLayout" class="standalone-page">
      <router-view />
    </div>
    <div v-else class="app-container" :class="{ 'logging-out': isLoggingOut }">
      <!-- 退出动画遮罩 -->
      <div class="logout-overlay" :class="{ active: isLoggingOut }">
        <div class="logout-animation">
          <div class="logout-icon">
            <i class="fas fa-sign-out-alt"></i>
          </div>
          <div class="logout-text">正在退出...</div>
        </div>
      </div>
      
      <!-- 移动端遮罩 -->
      <div 
        class="mobile-overlay" 
        :class="{ active: !sidebarCollapsed }"
        @click="sidebarCollapsed = true"
      ></div>
      
      <!-- 侧边导航栏 -->
      <div class="sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="logo">
          <div class="logo-icon">
            <i class="fas fa-balance-scale"></i>
          </div>
          <transition name="logo-text" mode="out-in">
            <div v-if="!sidebarCollapsed" class="logo-text">律智AI</div>
          </transition>
        </div>
        
        <div class="nav-links">
          <div 
            v-for="item in navItems" 
            :key="item.path"
            class="nav-item" 
            :class="{ active: route.path === item.path }"
            @click="navigateTo(item.path)"
          >
            <i :class="item.icon"></i>
            <transition name="nav-text" mode="out-in">
              <span v-if="!sidebarCollapsed" class="nav-text">{{ item.text }}</span>
            </transition>
          </div>
        </div>
      </div>
      
      <!-- 主内容区 -->
      <div class="main-content" :class="{ expanded: sidebarCollapsed }">
        <!-- 顶部导航栏 -->
        <div class="topbar">
          <div class="topbar-left">
            <button class="sidebar-toggle" @click="sidebarCollapsed = !sidebarCollapsed">
              <i class="fas fa-bars" :class="{ rotated: sidebarCollapsed }"></i>
            </button>
          </div>
          
          <div class="user-actions">
            <div class="user-profile" @click="showUserDropdown = !showUserDropdown">
              <div class="avatar">{{ userInitial }}</div>
              <span class="user-name">{{ displayName }}</span>
              <i class="fas fa-chevron-down dropdown-arrow" :class="{ rotated: showUserDropdown }"></i>
              
              <!-- 用户信息下拉框 -->
              <div class="user-dropdown" :class="{ show: showUserDropdown }" @click.stop>
                <div class="dropdown-header">
                  <div class="dropdown-avatar">{{ userInitial }}</div>
                  <div class="dropdown-info">
                    <div class="dropdown-name">{{ displayName }}</div>
                    <div class="dropdown-email">{{ userEmail }}</div>
                  </div>
                </div>
                <div class="dropdown-divider"></div>
                <div class="dropdown-actions">
                  <button class="logout-btn" @click="logout">
                    <i class="fas fa-sign-out-alt"></i>
                    <span>退出登录</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 页面内容 -->
        <div class="content">
          <router-view v-slot="{ Component, route }">
            <transition 
              :name="getTransitionName(route)" 
              mode="out-in"
              @before-enter="onBeforeEnter"
              @enter="onEnter"
              @leave="onLeave"
            >
              <component :is="Component" :key="route.path" />
            </transition>
          </router-view>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="router-loading">
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  min-height: 100vh;
  overflow-x: hidden;
  width: 100%;
}

.mobile-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 99;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s ease;
}

.mobile-overlay.active {
  opacity: 1;
  pointer-events: all;
}

.sidebar {
  width: 220px;
  background: var(--primary, #1a3a6c);
  color: white;
  padding: 20px 0;
  height: 100vh;
  position: fixed;
  overflow-x: hidden;
  overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar.collapsed {
  width: 70px;
}

.logo {
  display: flex;
  align-items: center;
  padding: 0 20px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  min-height: 80px;
  transition: padding 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar.collapsed .logo {
  justify-content: center;
  padding: 0 16px 20px;
}

.logo-icon {
  background: var(--accent, #4a86e8);
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  font-size: 20px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  transform-origin: center;
  flex-shrink: 0;
}

.sidebar.collapsed .logo-icon {
  margin-right: 0;
  transform: scale(1.1);
}

.logo-text {
  font-size: 22px;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  flex-shrink: 0;
}

.nav-links {
  padding: 20px 0;
  overflow: hidden;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  margin: 3px 10px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 15px;
  position: relative;
  border-radius: 10px;
  overflow: hidden;
  white-space: nowrap;
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  margin: 3px 12px;
  padding: 12px 16px;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(4px);
}

.sidebar.collapsed .nav-item:hover {
  transform: scale(1.05);
}

.nav-item.active {
  background: var(--secondary, #2c5aa0);
  box-shadow: 0 4px 12px rgba(44, 90, 160, 0.3);
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: var(--accent, #4a86e8);
  border-radius: 0 2px 2px 0;
}

.sidebar.collapsed .nav-item.active::before {
  display: none;
}

.nav-item i {
  margin-right: 12px;
  font-size: 18px;
  width: 24px;
  text-align: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
}

.sidebar.collapsed .nav-item i {
  margin-right: 0;
  font-size: 20px;
}

.nav-text {
  white-space: nowrap;
  overflow: hidden;
  flex-shrink: 0;
}

.main-content {
  flex: 1;
  margin-left: 220px;
  min-height: 100vh;
  overflow-x: hidden;
  max-width: calc(100vw - 220px);
  transition: margin-left 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: margin-left;
}

.main-content.expanded {
  margin-left: 70px;
  max-width: calc(100vw - 70px);
}

.sidebar-toggle {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.sidebar-toggle::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: var(--light, #f5f7fa);
  border-radius: 50%;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform: translate(-50%, -50%);
  z-index: -1;
}

.sidebar-toggle:hover::before {
  width: 40px;
  height: 40px;
}

.sidebar-toggle i {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-toggle i.rotated {
  transform: rotate(90deg);
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 32px;
  background: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 10;
}

.topbar-left {
  display: flex;
  align-items: center;
}

.user-actions {
  position: relative;
}

.user-profile {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
  position: relative;
}

.user-profile:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--secondary, #2c5aa0);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  margin-right: 10px;
  font-size: 16px;
  transition: all 0.3s ease;
}

.user-name {
  font-weight: 500;
  color: var(--dark);
  margin-right: 8px;
  font-size: 14px;
}

.dropdown-arrow {
  font-size: 12px;
  color: var(--dark-gray);
  transition: transform 0.3s ease;
}

.dropdown-arrow.rotated {
  transform: rotate(180deg);
}

/* 用户下拉框样式 */
.user-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 280px;
  max-width: 90vw;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.05);
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px) scale(0.95);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1000;
  overflow: hidden;
}

.user-dropdown.show {
  opacity: 1;
  visibility: visible;
  transform: translateY(0) scale(1);
}

.dropdown-header {
  display: flex;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
}

.dropdown-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 20px;
  margin-right: 15px;
  backdrop-filter: blur(10px);
}

.dropdown-info {
  flex: 1;
}

.dropdown-name {
  color: white;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.dropdown-email {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.dropdown-divider {
  height: 1px;
  background: rgba(0, 0, 0, 0.1);
  margin: 0 20px;
}

.dropdown-actions {
  padding: 20px;
}

.logout-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  background: var(--danger, #f44336);
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: #d32f2f;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(244, 67, 54, 0.3);
}

.logout-btn i {
  font-size: 14px;
}

/* 文字淡入淡出动画 - 修复闪烁 */
.logo-text-enter-active,
.nav-text-enter-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) 0.15s;
}

.logo-text-leave-active,
.nav-text-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.logo-text-enter-from,
.nav-text-enter-from {
  opacity: 0;
  transform: translateX(-10px);
}

.logo-text-leave-to,
.nav-text-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

/* 防止动画期间的布局抖动 */
.sidebar * {
  box-sizing: border-box;
}

/* 响应式设计增强 */
@media (max-width: 1200px) {
  .sidebar {
    transform: translateX(-100%);
  }
  
  .sidebar.collapsed {
    transform: translateX(0);
  }
  
  .main-content {
    margin-left: 0;
    max-width: 100vw;
  }
  
  .main-content.expanded {
    margin-left: 70px;
    max-width: calc(100vw - 70px);
  }
  
  .mobile-overlay {
    display: block;
  }
  
  .user-name {
    display: none;
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 260px;
  }
  
  .sidebar.collapsed {
    width: 260px;
  }
  
  .main-content.expanded {
    margin-left: 0;
    max-width: 100vw;
  }
  
  .topbar {
    padding: 10px 20px;
  }
  
  .content {
    padding: 16px;
  }
  
  .user-dropdown {
    width: 260px;
    right: -10px;
  }
}

@media (max-width: 480px) {
  .topbar {
    padding: 8px 16px;
  }
  
  .user-profile {
    margin-left: 8px;
  }
  
  .avatar {
    width: 32px;
    height: 32px;
    font-size: 14px;
  }
  
  .content {
    padding: 12px;
  }
  
  .sidebar {
    width: 100vw;
  }
  
  .sidebar.collapsed {
    width: 100vw;
  }
  
  .user-dropdown {
    width: calc(100vw - 32px);
    right: -16px;
  }
}

/* 侧边栏响应式调整 */
@media (max-width: 1200px) {
  .nav-item {
    margin: 4px 12px;
  }
  
  .nav-item:hover {
    transform: none;
  }
}

@media (max-width: 768px) {
  .logo {
    padding: 0 18px 18px;
  }
  
  .nav-item {
    padding: 14px 18px;
    font-size: 15px;
  }
  
  .nav-item i {
    font-size: 17px;
  }
}

/* 提升触摸友好性 */
@media (hover: none) and (pointer: coarse) {
  .nav-item {
    padding: 18px 20px;
  }
  
  .sidebar-toggle {
    padding: 12px;
  }
  
  .card:hover {
    transform: none;
  }
  
  .card {
    cursor: default;
  }
}

/* 页面过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.4s cubic-bezier(0.55, 0, 0.1, 1);
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.98);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-20px) scale(1.02);
}

/* 向左滑动 (前进) */
.slide-left-enter-active,
.slide-left-leave-active {
  transition: all 0.4s cubic-bezier(0.55, 0, 0.1, 1);
}

.slide-left-enter-from {
  opacity: 0;
  transform: translateX(50px) scale(0.95);
}

.slide-left-leave-to {
  opacity: 0;
  transform: translateX(-50px) scale(1.05);
}

/* 向右滑动 (后退) */
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.4s cubic-bezier(0.55, 0, 0.1, 1);
}

.slide-right-enter-from {
  opacity: 0;
  transform: translateX(-50px) scale(0.95);
}

.slide-right-leave-to {
  opacity: 0;
  transform: translateX(50px) scale(1.05);
}

/* 优化动画性能 */
.fade-enter-active,
.fade-leave-active,
.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  will-change: transform, opacity;
  backface-visibility: hidden;
  perspective: 1000px;
  overflow: hidden;
}

/* 为动画添加模糊效果 (可选) */
.slide-left-leave-to,
.slide-right-leave-to {
  filter: blur(2px);
}

.slide-left-enter-from,
.slide-right-enter-from {
  filter: blur(1px);
}

.slide-left-enter-to,
.slide-right-enter-to,
.fade-enter-to {
  filter: blur(0);
}

/* 减少动画设置下的兼容性 */
@media (prefers-reduced-motion: reduce) {
  .fade-enter-active,
  .fade-leave-active,
  .slide-left-enter-active,
  .slide-left-leave-active,
  .slide-right-enter-active,
  .slide-right-leave-active {
    transition-duration: 0.1s !important;
  }
  
  .fade-enter-from,
  .fade-leave-to,
  .slide-left-enter-from,
  .slide-left-leave-to,
  .slide-right-enter-from,
  .slide-right-leave-to {
    transform: none !important;
    filter: none !important;
  }
}

/* 移动端优化动画 */
@media (max-width: 768px) {
  .fade-enter-active,
  .fade-leave-active,
  .slide-left-enter-active,
  .slide-left-leave-active,
  .slide-right-enter-active,
  .slide-right-leave-active {
    transition-duration: 0.3s;
  }
  
  .slide-left-enter-from,
  .slide-left-leave-to,
  .slide-right-enter-from,
  .slide-right-leave-to {
    transform: translateX(20px);
  }
  
  .fade-enter-from,
  .fade-leave-to {
    transform: translateY(10px);
  }
}

/* 退出动画样式 */
.logout-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(26, 58, 108, 0.95), rgba(44, 90, 160, 0.95));
  backdrop-filter: blur(10px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  visibility: hidden;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.logout-overlay.active {
  opacity: 1;
  visibility: visible;
}

.logout-animation {
  text-align: center;
  color: white;
  transform: translateY(20px) scale(0.9);
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.2s;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) translateY(20px) scale(0.9);
}

.logout-overlay.active .logout-animation {
  transform: translate(-50%, -50%) translateY(0) scale(1);
}

/* 退出时整体容器动画 */
.app-container.logging-out {
  transform: scale(0.98);
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.app-container.logging-out .sidebar {
  transform: translateX(-20px);
  opacity: 0.8;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1) 0.1s;
}

.app-container.logging-out .main-content {
  transform: translateX(20px);
  opacity: 0.8;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1) 0.2s;
}

/* 动画关键帧 */
@keyframes logoutPulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.3);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 0 20px rgba(255, 255, 255, 0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 移动端优化 */
@media (max-width: 768px) {
  .logout-icon {
    width: 60px;
    height: 60px;
    font-size: 24px;
    margin-bottom: 15px;
  }
  
  .logout-text {
    font-size: 16px;
  }
  
  .app-container.logging-out {
    transform: scale(0.95);
  }
}

/* 减少动画设置下的兼容性 */
@media (prefers-reduced-motion: reduce) {
  .logout-overlay,
  .logout-animation,
  .app-container.logging-out,
  .app-container.logging-out .sidebar,
  .app-container.logging-out .main-content {
    transition-duration: 0.2s !important;
  }
  
  .logout-icon {
    animation: none !important;
  }
  
  .logout-text {
    animation: none !important;
    opacity: 1;
  }
}
</style>

