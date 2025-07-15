import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    port: 3100, // 启动端口
    host: '0.0.0.0', // 允许外部访问
    open: '/login', // 是否自动打开浏览器
    proxy: {
      '/api': { // 获取路径中包含了api的请求
        target: 'http://localhost:8080', // 代理的目标地址
        // target: 'http://172.20.10.4:8000', // 代理的目标地址
        // target: 'http://192.168.43.231:8000', // 代理的目标地址
        changeOrigin: true, // 修改源
        rewrite: (path) => path.replace(/^\/api/, ''), // 重写路径
      }
    }
  },
})
