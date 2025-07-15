<template>
  <div class="not-found-page">
    <div class="not-found-container">
      <div class="error-code">404</div>
      <div class="error-message">页面未找到</div>
      <div class="error-description">
        抱歉，您访问的页面不存在或已被移除。
      </div>
      <div class="action-buttons">
        <button class="btn-primary" @click="goHome">
          <i class="fas fa-home"></i>
          返回首页
        </button>
        <button class="btn-secondary" @click="goBack">
          <i class="fas fa-arrow-left"></i>
          返回上页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useTokenStore } from '@/stores/token'

const router = useRouter()
const tokenStore = useTokenStore()

const goHome = () => {
  // 如果用户已登录，跳转到法律文库，否则跳转到登录页
  if (tokenStore.token) {
    router.push('/library')
  } else {
    router.push('/login')
  }
}

const goBack = () => {
  // 如果有历史记录，返回上一页，否则跳转到首页
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    goHome()
  }
}
</script>

<style scoped lang="scss">
.not-found-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.not-found-container {
  text-align: center;
  max-width: 500px;
  width: 100%;
}

.error-code {
  font-size: 120px;
  font-weight: 700;
  color: var(--primary, #1a3a6c);
  margin-bottom: 20px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
  animation: bounce 2s ease-in-out infinite;
}

.error-message {
  font-size: 32px;
  font-weight: 600;
  color: var(--dark, #333);
  margin-bottom: 16px;
}

.error-description {
  font-size: 16px;
  color: var(--dark-gray, #666);
  margin-bottom: 40px;
  line-height: 1.5;
}

.action-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-primary,
.btn-secondary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
}

.btn-primary {
  background: var(--accent, #4a86e8);
  color: white;
  
  &:hover {
    background: #3a76d8;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(74, 134, 232, 0.3);
  }
}

.btn-secondary {
  background: white;
  color: var(--dark, #333);
  border: 2px solid var(--gray, #e0e0e0);
  
  &:hover {
    background: var(--light, #f5f7fa);
    border-color: var(--dark-gray, #999);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-20px);
  }
  60% {
    transform: translateY(-10px);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .error-code {
    font-size: 80px;
  }
  
  .error-message {
    font-size: 24px;
  }
  
  .error-description {
    font-size: 14px;
    margin-bottom: 30px;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
    gap: 12px;
  }
  
  .btn-primary,
  .btn-secondary {
    width: 200px;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .not-found-page {
    padding: 16px;
  }
  
  .error-code {
    font-size: 60px;
    margin-bottom: 16px;
  }
  
  .error-message {
    font-size: 20px;
  }
  
  .btn-primary,
  .btn-secondary {
    width: 100%;
    padding: 14px 20px;
  }
}
</style>
