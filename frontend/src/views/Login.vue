<script setup>
import { User, Lock, Phone, Postcard , Message} from '@element-plus/icons-vue'
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useDark } from '@vueuse/core'

// 控制注册与登录表单的显示， 默认显示注册
const isRegister = ref(false)

const isDark = useDark()

// 定义数据模型
const userRegisterData = ref({
    username: '',
    email: '',
    password: '',
    repassword: ''
})

// 校验密码的函数
const checkRePassword = (rule, value, callback) => {
    if (value === '') {
        callback(new Error('请再次确认密码'))
    } else if (value !== userRegisterData.value.password) {
        callback(new Error('两次输入密码不一致'))
    } else {
        callback()
    }
}

// 定义表单校验规则
const rules = {
    username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 16, message: '长度在 3 到 16 个字符', trigger: 'blur' }
    ],
    email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
    ],
    password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 5, max: 16, message: '长度在 5 到 16 个字符', trigger: 'blur' }
    ],
    repassword: [
        {validator: checkRePassword, trigger: 'blur'},
        { required: true, message: '请再次确认密码', trigger: 'blur' }
    ]
}

// 注册全局校验
const formRefRegister = ref(null);

const handleRegister = () => {
    formRefRegister.value.validate((valid) => {
        if (valid) {
            register(); // 调用注册函数
        } else {
            console.log('请完善表单信息');
            return false;
        }
    });
};

// 添加加载状态
const isLoading = ref(false)
const isRegistering = ref(false)

// 添加页面加载状态
const pageLoading = ref(true)

// 调用后台接口完成注册
import { userRegisterService, userLoginService } from '@/services/user.js'
const register = async () => {
    isRegistering.value = true
    try {
        let result = await userRegisterService(userRegisterData.value);
        if (result.code === 0) {
            ElMessage.success('注册成功');
            // 保存用户名以便登录
            const username = userRegisterData.value.username;
            // 清空表单
            clearRegisterData();
            // 设置用户名（使注册用户无需重新输入用户名）
            userRegisterData.value.username = username;
            // 切换到登录页面
            isRegister.value = false;
        } else {
            ElMessage.error('注册失败，请检查信息是否正确');
        }
    } catch (error) {
        ElMessage.error('注册失败，请稍后重试');
    } finally {
        isRegistering.value = false
    }
}

// 登录全局校验
const formRefLogin = ref(null);

const handleLogin = () => {
    formRefLogin.value.validate((valid) => {
        if (valid) {
            login(); // 调用登录函数
        } else {
            console.log('表单校验失败');
            return false;
        }
    });
};

import { userInfoService } from '@/services/user.js'
import useUserInfoStore from '@/stores/user'
const userInfoStore = useUserInfoStore()
// 调用函数，获取用户详细信息
const getUserInfo = async () => {
    // 调用接口
    let result = await userInfoService();
    // 数据存储到pinia中
    userInfoStore.setUserInfo(result.data);
};

// 绑定数据，复用注册表单的数据模型
// 表单数据校验
// 登录函数
import {useTokenStore} from '@/stores/token.js'
import { useRouter } from 'vue-router'
const router = useRouter();
const tokenStore = useTokenStore();
const login = async () => {
    isLoading.value = true
    try {
        let result = await userLoginService(userRegisterData.value);
        if (result.code === 0) {
            ElMessage.success('登录成功');
            // 将token存储到pinia
            tokenStore.setToken(result.data);
            await getUserInfo();
            
            setTimeout(() => {
                router.push('/library'); 
            }, 500);
        } else {
            ElMessage.error('用户名或密码错误！');
        }
    } catch (error) {
        ElMessage.error('登录失败，请稍后重试');
    } finally {
        // 延迟关闭加载状态
        setTimeout(() => {
            isLoading.value = false
        }, 300);
    }
};

// 定义函数，清空数据模型的数据
const clearRegisterData = () => {
    userRegisterData.value = {
        username: '',
        email: '',
        password: '',
        repassword: ''
    }
}

// 页面加载完成后执行
onMounted(() => {
  setTimeout(() => {
    pageLoading.value = false
  }, 800)
  
  initParticleSystem()
})

// 粒子系统
const initParticleSystem = () => {
  const canvas = document.getElementById('particle-canvas')
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  let particles = []
  
  // 设置canvas尺寸
  const resizeCanvas = () => {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
  }
  resizeCanvas()
  window.addEventListener('resize', resizeCanvas)
  
  // 粒子类
  class Particle {
    constructor() {
      this.x = Math.random() * canvas.width
      this.y = Math.random() * canvas.height
      this.vx = (Math.random() - 0.5) * 0.5
      this.vy = (Math.random() - 0.5) * 0.5
      this.size = Math.random() * 2 + 1
      this.opacity = Math.random() * 0.5 + 0.2
      this.pulseSpeed = Math.random() * 0.02 + 0.01
      this.pulse = 0
    }
    
    update() {
      this.x += this.vx
      this.y += this.vy
      this.pulse += this.pulseSpeed
      
      // 边界检测
      if (this.x < 0 || this.x > canvas.width) this.vx *= -1
      if (this.y < 0 || this.y > canvas.height) this.vy *= -1
      
      // 保持在画布内
      this.x = Math.max(0, Math.min(canvas.width, this.x))
      this.y = Math.max(0, Math.min(canvas.height, this.y))
    }
    
    draw() {
      const pulseSizeBonus = Math.sin(this.pulse) * 0.5
      const currentSize = this.size + pulseSizeBonus
      const currentOpacity = this.opacity + Math.sin(this.pulse) * 0.1
      
      ctx.beginPath()
      ctx.arc(this.x, this.y, currentSize, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(74, 134, 232, ${currentOpacity})`
      ctx.fill()
      
      // 添加光晕效果
      ctx.beginPath()
      ctx.arc(this.x, this.y, currentSize * 2, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(74, 134, 232, ${currentOpacity * 0.1})`
      ctx.fill()
    }
  }
  
  // 创建粒子
  for (let i = 0; i < 100; i++) {
    particles.push(new Particle())
  }
  
  // 绘制连线
  const drawConnections = () => {
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x
        const dy = particles[i].y - particles[j].y
        const distance = Math.sqrt(dx * dx + dy * dy)
        
        if (distance < 120) {
          const opacity = (120 - distance) / 120 * 0.2
          ctx.beginPath()
          ctx.moveTo(particles[i].x, particles[i].y)
          ctx.lineTo(particles[j].x, particles[j].y)
          ctx.strokeStyle = `rgba(74, 134, 232, ${opacity})`
          ctx.lineWidth = 0.5
          ctx.stroke()
        }
      }
    }
  }
  
  // 动画循环
  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    particles.forEach(particle => {
      particle.update()
      particle.draw()
    })
    
    drawConnections()
    requestAnimationFrame(animate)
  }
  
  animate()
}
</script>

<template>
    <div class="login-page" :class="{ 'dark': isDark }">
      <!-- 粒子画布背景 -->
      <canvas id="particle-canvas" class="particle-canvas"></canvas>
      
      <!-- 几何装饰元素 -->
      <div class="geometric-decorations">
        <div class="geo-shape geo-circle-1"></div>
        <div class="geo-shape geo-circle-2"></div>
        <div class="geo-shape geo-triangle-1"></div>
        <div class="geo-shape geo-triangle-2"></div>
        <div class="geo-shape geo-diamond-1"></div>
        <div class="geo-shape geo-diamond-2"></div>
      </div>
      
      <!-- 光线效果 -->
      <div class="light-rays">
        <div class="light-ray light-ray-1"></div>
        <div class="light-ray light-ray-2"></div>
        <div class="light-ray light-ray-3"></div>
      </div>
      
      <!-- 页面初始加载遮罩 -->
      <div class="page-loading-overlay" :class="{ active: pageLoading }">
        <div class="page-loading-content">
          <div class="logo-loading">
            <i class="fas fa-balance-scale"></i>
            <div class="logo-glow"></div>
          </div>
          <div class="loading-spinner-small">
            <div class="spinner-dot"></div>
            <div class="spinner-dot"></div>
            <div class="spinner-dot"></div>
          </div>
          <div class="page-loading-text">律智AI</div>
          <div class="tech-lines">
            <div class="tech-line"></div>
            <div class="tech-line"></div>
          </div>
        </div>
      </div>
      
      <!-- 登录加载遮罩 -->
      <div class="loading-overlay" :class="{ active: isLoading }">
        <div class="loading-content">
          <div class="loading-spinner">
            <div class="spinner-ring"></div>
            <div class="spinner-ring"></div>
            <div class="spinner-ring"></div>
          </div>
          <div class="loading-text">正在登录...</div>
          <div class="scan-line"></div>
        </div>
      </div>
      
      <div class="background-overlay"></div>
      <div class="form" :class="{ 'dark': isDark, 'loading': isLoading || isRegistering, 'page-loading': pageLoading }">
        <!-- 注册表单 -->
        <el-form ref="formRefRegister" size="large" autocomplete="off" v-if="isRegister" :model="userRegisterData" :rules="rules">
          <el-form-item>
            <h1>注册</h1>
          </el-form-item>
          <el-form-item prop="username">
            <el-input :prefix-icon="User" placeholder="请输入用户名（3~16位）" v-model="userRegisterData.username" :disabled="isRegistering"></el-input>
          </el-form-item>
          <el-form-item prop="email">
            <el-input :prefix-icon="Message" placeholder="请输入邮箱" v-model="userRegisterData.email" :disabled="isRegistering"></el-input>
          </el-form-item>
          <el-form-item prop="password">
            <el-input :prefix-icon="Lock" type="password" placeholder="请输入密码（5~16位）" v-model="userRegisterData.password" :disabled="isRegistering"></el-input>
          </el-form-item>
          <el-form-item prop="repassword">
            <el-input :prefix-icon="Lock" type="password" placeholder="请输入再次密码（5~16位）" v-model="userRegisterData.repassword" :disabled="isRegistering"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button 
              class="button" 
              type="primary" 
              auto-insert-space 
              @click="handleRegister"
              :loading="isRegistering"
              :disabled="isRegistering"
            >
              <span v-if="!isRegistering">注册</span>
              <span v-else>注册中...</span>
            </el-button>
          </el-form-item>
          <el-form-item class="flex">
            <el-link type="info" :underline="false" @click="isRegister = false;clearRegisterData()" :disabled="isRegistering">← 返回</el-link>
          </el-form-item>
        </el-form>
  
        <!-- 登录表单 -->
        <el-form ref="formRefLogin" size="large" autocomplete="off" v-else :model="userRegisterData" :rules="rules">
          <el-form-item>
            <h1>登录</h1>
          </el-form-item>
          <el-form-item prop="username">
            <el-input :prefix-icon="User" placeholder="请输入用户名" v-model="userRegisterData.username" :disabled="isLoading"></el-input>
          </el-form-item>
          <el-form-item prop="password">
            <el-input name="password" :prefix-icon="Lock" type="password" placeholder="请输入密码" v-model="userRegisterData.password" :disabled="isLoading"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button 
              class="button" 
              type="primary" 
              auto-insert-space 
              @click="handleLogin"
              :loading="isLoading"
              :disabled="isLoading"
            >
              <span v-if="!isLoading">登录</span>
              <span v-else>登录中...</span>
            </el-button>
          </el-form-item>
          <el-form-item class="flex">
            <el-link type="info" :underline="false" @click="isRegister = true;clearRegisterData()" :disabled="isLoading">注册 →</el-link>
          </el-form-item>
        </el-form>
      </div>
    </div>
</template>

<style lang="scss" scoped>
/* 粒子画布样式 */
.particle-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
}

/* 几何装饰元素 */
.geometric-decorations {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
  overflow: hidden;
}

.geo-shape {
  position: absolute;
  opacity: 0.1;
  animation-fill-mode: both;
}

.geo-circle-1 {
  width: 200px;
  height: 200px;
  border: 2px solid #4a86e8;
  border-radius: 50%;
  top: 10%;
  left: 10%;
  animation: float 8s ease-in-out infinite, pulse 4s ease-in-out infinite;
}

.geo-circle-2 {
  width: 150px;
  height: 150px;
  border: 1px solid #00dfd8;
  border-radius: 50%;
  top: 60%;
  right: 15%;
  animation: float 6s ease-in-out infinite reverse, pulse 3s ease-in-out infinite 1s;
}

.geo-triangle-1 {
  width: 0;
  height: 0;
  border-left: 50px solid transparent;
  border-right: 50px solid transparent;
  border-bottom: 87px solid rgba(74, 134, 232, 0.2);
  top: 20%;
  right: 20%;
  animation: rotate 12s linear infinite, float 5s ease-in-out infinite;
}

.geo-triangle-2 {
  width: 0;
  height: 0;
  border-left: 30px solid transparent;
  border-right: 30px solid transparent;
  border-bottom: 52px solid rgba(0, 223, 216, 0.2);
  bottom: 30%;
  left: 20%;
  animation: rotate 15s linear infinite reverse, float 7s ease-in-out infinite 2s;
}

.geo-diamond-1 {
  width: 60px;
  height: 60px;
  background: linear-gradient(45deg, rgba(74, 134, 232, 0.1), rgba(0, 223, 216, 0.1));
  transform: rotate(45deg);
  top: 40%;
  left: 5%;
  animation: rotate 10s linear infinite, pulse 3s ease-in-out infinite;
}

.geo-diamond-2 {
  width: 40px;
  height: 40px;
  background: linear-gradient(45deg, rgba(0, 223, 216, 0.1), rgba(74, 134, 232, 0.1));
  transform: rotate(45deg);
  top: 70%;
  right: 5%;
  animation: rotate 8s linear infinite reverse, pulse 2s ease-in-out infinite 1.5s;
}

/* 光线效果 */
.light-rays {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
  overflow: hidden;
}

.light-ray {
  position: absolute;
  background: linear-gradient(90deg, transparent, rgba(74, 134, 232, 0.1), transparent);
  opacity: 0;
}

.light-ray-1 {
  width: 2px;
  height: 100%;
  left: 20%;
  animation: lightSweep 8s ease-in-out infinite;
}

.light-ray-2 {
  width: 100%;
  height: 2px;
  top: 30%;
  animation: lightSweepHorizontal 10s ease-in-out infinite 2s;
}

.light-ray-3 {
  width: 2px;
  height: 100%;
  right: 25%;
  animation: lightSweep 12s ease-in-out infinite 4s;
}

/* 样式 */
.login-page {
  height: 100vh;
  width: 100vw;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  background-image: url('@/assets/the-legal.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1;
    background: radial-gradient(ellipse at center, rgba(26, 58, 108, 0.1) 0%, rgba(26, 58, 108, 0.4) 100%);
  }

  &.dark {
    &::before {
      background: radial-gradient(ellipse at center, rgba(0, 0, 0, 0.3) 0%, rgba(0, 0, 0, 0.7) 100%);
    }
    
    .form {
      background: rgba(40, 40, 40, 0.85);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
      backdrop-filter: blur(15px);
      border: 1px solid rgba(255, 255, 255, 0.1);
    }
  }
}

.background-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: inherit;
  filter: blur(2px);
  z-index: 0;
}

.form {
  width: 420px;
  max-width: 90vw;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(15px);
  padding: 2.5rem;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  position: relative;
  z-index: 2;
  transition: all 0.3s ease;

  &::before {
    content: '';
    position: absolute;
    top: -1px;
    left: -1px;
    right: -1px;
    bottom: -1px;
    background: linear-gradient(45deg, 
      rgba(74, 134, 232, 0.5) 0%, 
      transparent 25%, 
      transparent 75%, 
      rgba(0, 223, 216, 0.5) 100%);
    border-radius: 16px;
    z-index: -1;
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  &:hover::before {
    opacity: 1;
  }
  
  /* 科技感光晕 */
  &::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 120%;
    height: 120%;
    background: radial-gradient(circle, rgba(74, 134, 232, 0.05) 0%, transparent 70%);
    transform: translate(-50%, -50%);
    z-index: -2;
    animation: formGlow 4s ease-in-out infinite;
  }

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25);
  }

  .title {
    margin: 0 auto;
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--text-color);
  }

  h1 {
    text-align: center;
    color: #333;
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 1rem;
  }

  .button {
    width: 100%;
    background: linear-gradient(45deg, var(--primary, #1a3a6c), var(--accent, #4a86e8));
    color: #fff;
    border: none;
    transition: all 0.3s ease;
    font-size: 1rem;
    font-weight: 600;
    padding: 12px;
    border-radius: 8px;

    &:hover {
      background: linear-gradient(45deg, var(--secondary, #2c5aa0), #3a76d8);
      transform: translateY(-2px);
      box-shadow: 0 4px 15px rgba(26, 58, 108, 0.4);
    }
  }

  .flex {
    width: 100%;
    display: flex;
    justify-content: space-between;
    margin-top: 1rem;

    .el-link {
      color: #666;
      font-weight: 600;
      transition: all 0.3s ease;

      &:hover {
        transform: scale(1.05);
        color: #007CF0;
      }
    }
  }

  :deep(.el-input) {
    --el-input-bg-color: rgba(255, 255, 255, 0.9);
    --el-input-text-color: #333;
    --el-input-border-color: rgba(220, 223, 230, 0.8);
    --el-input-hover-border-color: rgba(192, 196, 204, 0.9);
    --el-input-focus-border-color: #409eff;

    .el-input__wrapper {
      background-color: var(--el-input-bg-color);
      box-shadow: 0 0 0 1px var(--el-input-border-color) inset;
      backdrop-filter: blur(5px);
      border-radius: 8px;

      &:hover {
        box-shadow: 0 0 0 1px var(--el-input-hover-border-color) inset;
      }

      &.is-focus {
        box-shadow: 0 0 0 1px var(--el-input-focus-border-color) inset;
      }
    }

    input {
      color: var(--el-input-text-color);
      font-weight: 500;

      &::placeholder {
        color: #999;
      }
    }

    .el-input__prefix {
      color: #606266;
    }
  }

  &.dark {
    h1 {
      color: #e0e0e0;
    }

    .flex .el-link {
      color: #ccc;

      &:hover {
        color: #00DFD8;
      }
    }

    :deep(.el-input) {
      --el-input-bg-color: rgba(40, 40, 40, 0.9);
      --el-input-text-color: #e0e0e0;
      --el-input-border-color: rgba(76, 76, 76, 0.8);
      --el-input-hover-border-color: rgba(106, 106, 106, 0.9);
      --el-input-focus-border-color: #409eff;

      .el-input__wrapper {
        background-color: var(--el-input-bg-color);
        box-shadow: 0 0 0 1px var(--el-input-border-color) inset;

        &:hover {
          box-shadow: 0 0 0 1px var(--el-input-hover-border-color) inset;
        }
      }

      input {
        color: var(--el-input-text-color);

        &::placeholder {
          color: #888;
        }
      }

      .el-input__prefix {
        color: #bbb;
      }
    }
  }
}

/* 登录加载遮罩样式 */
.loading-overlay {
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

.loading-overlay.active {
  opacity: 1;
  visibility: visible;
}

.loading-content {
  text-align: center;
  color: white;
  transform: translateY(20px) scale(0.9);
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.2s;
}

.loading-overlay.active .loading-content {
  transform: translateY(0) scale(1);
}

.loading-spinner {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
}

.spinner-ring {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 3px solid transparent;
  border-top: 3px solid rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  animation: spin 1.5s linear infinite;
}

.spinner-ring:nth-child(1) {
  animation-delay: 0s;
  border-top-color: rgba(255, 255, 255, 0.9);
}

.spinner-ring:nth-child(2) {
  animation-delay: -0.5s;
  border-top-color: rgba(74, 134, 232, 0.8);
  width: 60px;
  height: 60px;
  top: 10px;
  left: 10px;
}

.spinner-ring:nth-child(3) {
  animation-delay: -1s;
  border-top-color: rgba(255, 255, 255, 0.6);
  width: 40px;
  height: 40px;
  top: 20px;
  left: 20px;
}

.loading-text {
  font-size: 18px;
  font-weight: 500;
  opacity: 0;
  animation: fadeInUp 0.5s ease-out 0.3s forwards;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
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

.form {
  /* ...existing code... */
  
  /* 加载状态下的表单样式 */
  &.loading {
    pointer-events: none;
    opacity: 0.7;
    transform: scale(0.98);
    transition: all 0.3s ease;
  }

  /* 页面加载状态下的表单样式 */
  &.page-loading {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
    pointer-events: none;
  }
  
  /* 表单进入动画 */
  &:not(.page-loading) {
    animation: formSlideIn 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards;
  }

  .button {
    // ...existing code...
    
    /* 加载状态按钮样式 */
    &.is-loading {
      position: relative;
      
      .el-icon {
        margin-right: 8px;
      }
    }
    
    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none !important;
    }
  }

  .flex .el-link {
    // ...existing code...
    
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      pointer-events: none;
    }
  }

  /* 禁用状态下的输入框样式 */
  :deep(.el-input.is-disabled) {
    .el-input__wrapper {
      background-color: rgba(240, 240, 240, 0.6);
      cursor: not-allowed;
    }
  }

  &.dark :deep(.el-input.is-disabled) {
    .el-input__wrapper {
      background-color: rgba(60, 60, 60, 0.6);
    }
  }
}

@keyframes formSlideIn {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 页面初始加载动画样式 */
.page-loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(26, 58, 108, 0.98), rgba(44, 90, 160, 0.98));
  backdrop-filter: blur(5px);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 1;
  visibility: visible;
  transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-loading-overlay:not(.active) {
  opacity: 0;
  visibility: hidden;
  transform: scale(1.1);
}

.page-loading-content {
  text-align: center;
  color: white;
  transform: translateY(0) scale(1);
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-loading-overlay:not(.active) .page-loading-content {
  transform: translateY(-30px) scale(0.9);
}

.logo-loading {
  width: 100px;
  height: 100px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 30px;
  font-size: 40px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  animation: logoFloat 2s ease-in-out infinite;
  backdrop-filter: blur(10px);
}

.loading-spinner-small {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 25px;
}

.spinner-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.8);
  animation: dotBounce 1.4s ease-in-out infinite both;
}

.spinner-dot:nth-child(1) { animation-delay: -0.32s; }
.spinner-dot:nth-child(2) { animation-delay: -0.16s; }
.spinner-dot:nth-child(3) { animation-delay: 0s; }

.page-loading-text {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 2px;
  opacity: 0;
  animation: fadeInUp 0.8s ease-out 0.5s forwards;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
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

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(5deg);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.1;
    transform: scale(1);
  }
  50% {
    opacity: 0.3;
    transform: scale(1.05);
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes lightSweep {
  0%, 100% {
    opacity: 0;
    transform: translateX(-100px);
  }
  50% {
    opacity: 1;
    transform: translateX(100px);
  }
}

@keyframes lightSweepHorizontal {
  0%, 100% {
    opacity: 0;
    transform: translateY(-100px);
  }
  50% {
    opacity: 1;
    transform: translateY(100px);
  }
}

@keyframes formGlow {
  0%, 100% {
    opacity: 0.3;
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    opacity: 0.6;
    transform: translate(-50%, -50%) scale(1.1);
  }
}

@keyframes logoGlowPulse {
  0%, 100% {
    opacity: 0.3;
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    opacity: 0.6;
    transform: translate(-50%, -50%) scale(1.2);
  }
}

@keyframes techLineFlow {
  0% {
    opacity: 0;
    transform: translateX(-100%);
  }
  50% {
    opacity: 1;
    transform: translateX(0);
  }
  100% {
    opacity: 0;
    transform: translateX(100%);
  }
}

@keyframes scanLineMove {
  0% {
    top: 0;
    opacity: 1;
  }
  100% {
    top: 100%;
    opacity: 0;
  }
}

/* 移动端优化 */
@media (max-width: 768px) {
  .geometric-decorations {
    .geo-shape {
      opacity: 0.05;
    }
  }
  
  .light-rays {
    opacity: 0.5;
  }
  
  .particle-canvas {
    opacity: 0.7;
  }
}

/* 减少动画设置下的兼容性 */
@media (prefers-reduced-motion: reduce) {
  .geo-shape,
  .light-ray,
  .logo-glow,
  .tech-line,
  .scan-line,
  .form::after {
    animation: none !important;
  }
  
  .particle-canvas {
    display: none;
  }
}
</style>

<style lang="scss">

html.dark {
  .el-form-item__label {
    color: #e0e0e0 !important;
  }
  
  .el-form-item__error {
    color: #ff6b6b !important;
  }
}

.el-message {
  z-index: 9999 !important;
  position: fixed !important;
}

.el-message__group {
  z-index: 9999 !important;
}
</style>





