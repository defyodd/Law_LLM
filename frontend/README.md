# 律智AI - 法律AI助手前端项目

一个基于Vue 3的现代化法律AI助手平台，提供法律咨询、文书撰写、法规检索等功能。

## 📋 项目简介

律智AI是一个智能化的法律服务平台，集成了以下核心功能：
- 🤖 **AI法律咨询** - 智能回答法律问题
- 📝 **AI文书撰写** - 自动生成各类法律文书
- 📚 **法律文库** - 全面的法律法规检索系统

## 🛠️ 技术栈

- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **UI组件**: Element Plus
- **路由**: Vue Router 4
- **状态管理**: Pinia
- **样式**: SCSS + CSS3
- **图标**: Font Awesome
- **文档处理**: marked, DOMPurify
- **HTTP客户端**: Axios
- **工具库**: VueUse

## 📦 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── assets/            # 静态资源文件
│   │   ├── main.scss      # 全局样式
│   │   └── the-legal.jpg  # 背景图片
│   ├── components/        # 可复用组件
│   │   └── ChatMessage.vue # 聊天消息组件
│   ├── router/           # 路由配置
│   │   └── index.js      # 路由定义
│   ├── services/         # API服务
│   │   ├── api.js        # 聊天API
│   │   ├── law.js        # 法律法规API
│   │   └── user.js       # 用户相关API
│   ├── stores/           # Pinia状态管理
│   │   ├── chatId.js     # 聊天ID状态
│   │   ├── token.js      # 用户Token状态
│   │   └── user.js       # 用户信息状态
│   ├── utils/            # 工具函数
│   │   └── request.js    # HTTP请求封装
│   ├── views/            # 页面组件
│   │   ├── ChatPage.vue  # AI法律咨询页面
│   │   ├── Contracts.vue # 合同模板页面
│   │   ├── DocWriter.vue # AI文书撰写页面
│   │   ├── LawDetail.vue # 法律详情页面
│   │   ├── Library.vue   # 法律文库页面
│   │   ├── Login.vue     # 登录页面
│   │   └── NotFound.vue  # 404页面
│   ├── App.vue           # 根组件
│   └── main.js           # 应用入口
├── package.json          # 项目依赖
├── vite.config.js        # Vite配置
└── README.md            # 项目说明
```

## ⚡ 快速开始

### 环境要求

- Node.js >= 16.0.0
- npm >= 8.0.0

### 安装依赖

```sh
npm install
```

### 开发环境运行

```sh
npm run dev
```

访问 http://localhost:3100 查看应用

### 生产环境构建

```sh
npm run build
```

### 预览生产构建

```sh
npm run preview
```

## 🔧 配置说明

### 环境配置

项目支持通过 `vite.config.js` 配置开发服务器：

```javascript
server: {
  port: 3100,           // 开发服务器端口
  host: '0.0.0.0',      // 允许外部访问
  open: '/login',       // 自动打开登录页
  proxy: {
    '/api': {
      target: 'http://172.20.10.4:8000',  // 后端API地址
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

### API代理配置

开发环境下，所有以 `/api` 开头的请求会被代理到后端服务器。可根据实际后端地址修改 `target` 配置。

## 🎨 主要功能

### 1. 用户认证
- 用户注册/登录
- Token持久化存储
- 自动登录状态检测

### 2. AI法律咨询
- 实时对话界面
- 流式响应显示
- 聊天历史管理
- 多模型切换支持

### 3. AI文书撰写
- 智能文书生成
- 多种导出格式（PDF、Word、TXT）
- 文档历史管理
- 模板快速选择

### 4. 法律文库
- 法律法规浏览
- 全文搜索功能
- 章节目录导航
- 法规详情查看

### 5. 合同模板
- 分类模板展示
- 模板预览下载
- 搜索过滤功能

## 🎯 核心特性

### 响应式设计
- 完全自适应移动端
- 触摸友好的交互体验
- 优化的移动端导航

### 现代化UI
- Material Design风格
- 流畅的动画效果
- 暗色模式支持
- 无障碍访问支持

### 性能优化
- 代码分割和懒加载
- 组件级别的缓存
- 图片和资源优化
- 渐进式Web应用特性

## 🔍 开发指南

### 添加新页面

1. 在 `src/views/` 创建页面组件
2. 在 `src/router/index.js` 添加路由配置
3. 在主导航中添加菜单项

### 状态管理

使用Pinia进行状态管理，各个store职责：
- `userStore`: 用户信息管理
- `tokenStore`: 认证Token管理
- `chatIdStore`: 聊天会话管理

### API调用

所有API调用都通过 `src/services/` 中的服务模块：
- 统一的错误处理
- 自动Token注入
- 请求/响应拦截

### 样式规范

- 使用SCSS预处理器
- CSS变量定义主题色彩
- 响应式断点统一管理
- 组件样式采用scoped模式


### 静态服务器部署

构建完成后，将 `dist/` 目录内容部署到任意静态服务器即可。

## 🐛 问题解决

### 常见问题

1. **开发服务器启动失败**
   ```bash
   # 清除node_modules重新安装
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **API请求失败**
   - 检查 `vite.config.js` 中的代理配置
   - 确认后端服务是否正常运行

3. **样式加载异常**
   - 检查SCSS预处理器是否正确安装
   - 确认CSS变量定义是否完整

### 调试技巧

- 使用Vue DevTools进行组件调试
- 利用浏览器开发者工具检查网络请求
- 查看控制台错误信息定位问题


**律智AI** - 让法律服务更智能、更便捷 ⚖️🤖
