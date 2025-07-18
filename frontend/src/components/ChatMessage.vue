<template>
  <div class="message-wrapper">
    <div class="message" :class="{ 'message-user': isUser }">
      <div class="message-info">
        <i :class="isUser ? 'fas fa-user' : 'fas fa-robot'"></i>
        <span class="message-sender">{{ isUser ? '您' : '律智AI' }}</span>
      </div>
      <div class="message-content">
        <!-- 复制按钮 -->
        <div class="message-header" v-if="!isUser && message.content">
          <button class="copy-button" @click="copyContent" :title="copyButtonTitle">
            <i v-if="!copied" class="fas fa-copy"></i>
            <i v-else class="fas fa-check copied"></i>
          </button>
        </div>
        
        <!-- 用户消息直接显示 -->
        <div v-if="isUser" class="text">
          {{ message.content }}
        </div>
        
        <!-- AI消息处理 -->
        <template v-else>
          <!-- 等待状态 -->
          <div v-if="isWaiting && !message.content" class="text loading-container">
            <div class="loading-dots">
              <div class="dot"></div>
              <div class="dot"></div>
              <div class="dot"></div>
            </div>
            <div class="waiting-text">思考中...</div>
          </div>
          
          <!-- 正常内容 -->
          <div v-else class="text markdown-content" ref="contentRef" v-html="processedContent">
          </div>
          
          <!-- 思考中动画 -->
          <div v-if="isThinking && message.content" class="thinking-indicator">
            <div class="loading-dots">
              <div class="dot"></div>
              <div class="dot"></div>
              <div class="dot"></div>
            </div>
          </div>
        </template>
      </div>
    </div>
    
    <!-- 参考信息来源  -->
    <div v-if="!isUser && message.reference && !isWaiting" class="reference-section">
      <div class="reference-header" @click="toggleReference">
        <i class="fas fa-info-circle"></i>
        <span>参考信息来源</span>
        <i class="fas fa-chevron-down" :class="{ 'expanded': showReference }"></i>
      </div>
      <div v-if="showReference" class="reference-content">
        {{ message.reference }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, nextTick, ref, watch } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'

const contentRef = ref(null)
const copied = ref(false)
const copyButtonTitle = computed(() => copied.value ? '已复制' : '复制内容')
const showReference = ref(false)

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true,
  sanitize: false
})

const props = defineProps({
  message: {
    type: Object,
    required: true
  },
  isStream: {
    type: Boolean,
    default: false
  },
  isWaiting: {
    type: Boolean,
    default: false
  },
  isThinking: {
    type: Boolean,
    default: false
  }
})

const isUser = computed(() => props.message.role === 'user')

// 处理内容
const processContent = (content) => {
  if (!content) return ''

  // ...existing code... 
  let thinkBlocks = [];
  let normalContent = '';
  let isInThinkBlock = false;
  let currentThinkBlock = '';
  let currentNormalContent = '';

  for (let i = 0; i < content.length; i++) {
    if (content.slice(i, i + 7) === '<think>') {
      isInThinkBlock = true;
      normalContent += currentNormalContent;
      currentNormalContent = '';
      currentThinkBlock = '';
      i += 6;
      continue;
    }

    if (content.slice(i, i + 8) === '</think>') {
      isInThinkBlock = false;
      thinkBlocks.push(currentThinkBlock);
      currentThinkBlock = '';
      i += 7;
      continue;
    }

    if (isInThinkBlock) {
      currentThinkBlock += content[i];
    } else {
      currentNormalContent += content[i];
    }
  }

  if (currentNormalContent) {
    normalContent += currentNormalContent;
  }
  if (isInThinkBlock && currentThinkBlock) {
    thinkBlocks.push(currentThinkBlock);
  }

  let result = '';
  
  if (normalContent.trim()) {
    result = marked.parse(normalContent);
  } else if (thinkBlocks.length > 0) {
    const lastThinkBlock = thinkBlocks[thinkBlocks.length - 1];
    result = `<div class="think-block">${marked.parse(lastThinkBlock)}</div>`;
  }

  const cleanHtml = DOMPurify.sanitize(result, {
    ADD_TAGS: ['think', 'code', 'pre', 'span'],
    ADD_ATTR: ['class', 'language']
  })
  
  return cleanHtml
}

const processedContent = computed(() => {
  if (!props.message.content) return ''
  return processContent(props.message.content)
})

// 代码高亮
const highlightCode = async () => {
  await nextTick()
  if (contentRef.value) {
    contentRef.value.querySelectorAll('pre code').forEach((block) => {
      hljs.highlightElement(block)
    })
  }
}

// 复制内容
const copyContent = async () => {
  try {
    let textToCopy = props.message.content;
    
    if (!isUser.value && contentRef.value) {
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = processedContent.value;
      textToCopy = tempDiv.textContent || tempDiv.innerText || '';
    }
    
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(textToCopy);
    } else {
      const textArea = document.createElement('textarea');
      textArea.value = textToCopy;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      textArea.style.top = '-999999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      
      const successful = document.execCommand('copy');
      if (!successful) {
        throw new Error('无法复制文本');
      }
      
      document.body.removeChild(textArea);
    }
    
    copied.value = true;
    
    setTimeout(() => {
      copied.value = false;
    }, 3000);
  } catch (err) {
    console.error('复制失败:', err);
    alert('复制失败，请手动选择并复制内容');
  }
}

// 切换参考信息显示
const toggleReference = () => {
  showReference.value = !showReference.value
}

// 监听内容变化
watch(() => props.message.content, () => {
  if (!isUser.value) {
    highlightCode()
  }
})

onMounted(() => {
  if (!isUser.value) {
    highlightCode()
  }
})
</script>

<style scoped lang="scss">
.message-wrapper {
  display: flex;
  flex-direction: column;
  width: 100%;
  margin-bottom: 1.5rem;
}

.message {
  display: flex;
  flex-direction: column;
  max-width: 80%;
  padding: 16px 20px;
  border-radius: 18px;
  line-height: 1.5;
  word-wrap: break-word;
  position: relative;

  &.message-user {
    align-self: flex-end;
    background: var(--accent);
    color: white;
    border-bottom-right-radius: 4px;
  }

  &:not(.message-user) {
    align-self: flex-start;
    background: var(--light);
    color: var(--dark);
    border-bottom-left-radius: 4px;
  }
}

.message-info {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-size: 16px; 
  font-weight: 600;
}

.message-user .message-info {
  color: rgba(255, 255, 255, 0.8);
  justify-content: flex-end;
}

.message:not(.message-user) .message-info {
  color: var(--accent);
}

.message-info i {
  margin-right: 6px;
  width: 18px; 
}

.message-sender {
  font-size: 14px; 
}

.message-content {
  position: relative;
}

.message-header {
  position: absolute;
  top: -35px;
  right: -12px;
  z-index: 10;
}

.copy-button {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(0, 0, 0, 0.1);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(4px);
  
  &:hover {
    background: rgba(255, 255, 255, 1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transform: scale(1.05);
  }
  
  i {
    width: 14px;
    height: 14px;
    color: var(--dark-gray);
    
    &.copied {
      color: #4ade80;
    }
  }
}


.message-footer {
  display: none; 
}

.text {
  font-size: 16px;
  white-space: pre-wrap;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.waiting-text {
  margin-top: 0.5rem;
  font-size: 16px;
  color: #666;
}

.loading-dots {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  
  .dot {
    width: 8px;
    height: 8px;
    background-color: #666;
    border-radius: 50%;
    opacity: 0.6;
    animation: dot-pulse 1.5s infinite ease-in-out;
    
    &:nth-child(1) {
      animation-delay: 0s;
    }
    
    &:nth-child(2) {
      animation-delay: 0.5s;
    }
    
    &:nth-child(3) {
      animation-delay: 1s;
    }
  }
}

@keyframes dot-pulse {
  0%, 100% {
    transform: scale(0.8);
    opacity: 0.6;
  }
  
  50% {
    transform: scale(1.2);
    opacity: 1;
  }
}

.thinking-indicator {
  display: inline-flex;
  align-items: center;
  margin-left: 0.5rem;
  vertical-align: middle;
  
  .loading-dots {
    display: flex;
    align-items: center;
    gap: 3px;
    
    .dot {
      width: 6px;
      height: 6px;
    }
  }
}

.markdown-content {
  :deep(p) {
    margin: 0.1rem 0;
    line-height: 1.5; 
    font-size: 16px; 

    &:first-child {
      margin-top: 0;
    }

    &:last-child {
      margin-bottom: 0;
    }
  }

  :deep(ul), :deep(ol) {
    margin: 0.1rem 0;
    padding-left: 1.5rem;
    font-size: 16px; 
  }

  :deep(li) {
    margin: 0.05rem 0;
    line-height: 1.4; 
    font-size: 16px; 
  }

  :deep(code) {
    background: rgba(0, 0, 0, 0.05);
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-size: 14px; 
    font-family: ui-monospace, monospace;
  }

  :deep(pre) {
    background: #f6f8fa;
    padding: 1rem;
    border-radius: 0.5rem;
    overflow-x: auto;
    margin: 0.3rem 0;
    border: 1px solid #e1e4e8;

    code {
      background: transparent;
      padding: 0;
      font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace;
      font-size: 14px; 
      line-height: 1.4; 
      tab-size: 2;
    }
  }

  :deep(.think-block) {
    position: relative;
    padding: 0.75rem 1rem 0.75rem 1.5rem;
    margin: 0.3rem 0;
    color: #666;
    font-style: italic;
    border-left: 4px solid #ddd;
    background-color: rgba(0, 0, 0, 0.03);
    border-radius: 0 0.5rem 0.5rem 0;
    font-size: 16px; 

    &::before {
      content: '思考';
      position: absolute;
      top: -0.75rem;
      left: 1rem;
      padding: 0 0.5rem;
      font-size: 12px; 
      background: #f5f5f5;
      border-radius: 0.25rem;
      color: #999;
      font-style: normal;
    }
  }


  :deep(br) {
    line-height: 1.2; 
  }


  :deep(p + p) {
    margin-top: 0.05rem;
  }

  // 针对单行文本的特殊处理
  :deep(p:only-child) {
    margin: 0;
    line-height: 1.4; 
    font-size: 16px;
  }

  // 处理数字列表的间距
  :deep(ol li) {
    margin: 0.03rem 0;
  }

  // 处理文本节点的间距
  :deep() {
    line-height: 1.5; 
  }

  
  :deep(*) {
    margin-block-start: 0;
    margin-block-end: 0;
  }

  // 特别处理numbered list
  :deep(ol) {
    margin: 0.05rem 0;
    padding-left: 1.2rem;
    
    li {
      margin: 0.02rem 0;
      padding: 0;
    }
  }
}

/* 参考信息样式 */
.reference-section {
  max-width: 80%;
  align-self: flex-start;
  margin-top: 8px;
  margin-left: 0;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
  background: rgba(74, 134, 232, 0.05);
  
  .reference-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    background: rgba(74, 134, 232, 0.08);
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    
    &:hover {
      background: rgba(74, 134, 232, 0.12);
    }
    
    i:first-child {
      color: var(--accent);
      font-size: 14px;
    }
    
    span {
      flex: 1;
      font-size: 14px;
      font-weight: 500;
      color: var(--dark);
    }
    
    i:last-child {
      color: var(--dark-gray);
      font-size: 12px;
      transition: transform 0.2s ease;
      
      &.expanded {
        transform: rotate(180deg);
      }
    }
  }
  
  .reference-content {
    padding: 12px;
    font-size: 14px;
    line-height: 1.5;
    color: var(--dark-gray);
    background: white;
    border-top: 1px solid rgba(0, 0, 0, 0.05);
    white-space: pre-wrap;
    word-break: break-word;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .message {
    max-width: 90%;
    padding: 12px 16px;
  }
  
  .reference-section {
    max-width: 90%;
  }
  
  // ...existing code...
}

@media (max-width: 480px) {
  .message {
    max-width: 95%;
    padding: 10px 14px;
    font-size: 14px;
  }
  
  .reference-section {
    max-width: 95%;
  }
  
  // ...existing code...
}


@media (prefers-color-scheme: dark) {
  // ...existing code...
  
  .reference-section {
    border-color: rgba(255, 255, 255, 0.1);
    background: rgba(74, 134, 232, 0.1);
    
    .reference-header {
      background: rgba(74, 134, 232, 0.15);
      border-bottom-color: rgba(255, 255, 255, 0.05);
      
      &:hover {
        background: rgba(74, 134, 232, 0.2);
      }
      
      span {
        color: #e0e0e0;
      }
      
      i:last-child {
        color: #999;
      }
    }
    
    .reference-content {
      background: #363636;
      border-top-color: rgba(255, 255, 255, 0.05);
      color: #ccc;
    }
  }
}
</style>