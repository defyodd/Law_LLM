<template>
  <div class="chat-page">
    <div class="chat-container">
      <div 
        class="sidebar list-item"
        :style="{ animationDelay: '0.1s' }"
        :class="{ 'stagger-enter': showCards }"
      >
        <div class="history-header">
          <h2>聊天记录</h2>
          <button class="new-chat" @click="startNewChat">
            <i class="fas fa-plus"></i>
            新对话
          </button>
        </div>
        <div class="history-list">
          <div 
            v-for="chat in chatHistory" 
            :key="chat.id"
            class="history-item"
            :class="{ 'active': currentChatId === chat.id }"
            @click="loadChat(chat.id)"
          >
            <i class="fas fa-comment-alt"></i>
            <span class="title">{{ chat.title || '新对话' }}</span>
            <el-dropdown @command="(command) => handleSessionCommand(chat.id, command)" @click.stop>
              <template #default>
                <el-button text @click.stop>
                  <i class="fas fa-ellipsis-v"></i>
                </el-button>
              </template>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="rename">重命名</el-dropdown-item>
                  <el-dropdown-item command="delete">删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>
      
      <div 
        class="chat-main list-item"
        :style="{ animationDelay: '0.2s' }"
        :class="{ 'stagger-enter': showCards }"
      >
        <div class="chat-header">
          <div class="chat-title">AI法律咨询</div>
          <!-- 注释掉模型选择器 -->
          <!-- <div class="model-selector">
            <div class="current-model-label">当前模型：{{ getCurrentModelLabel }}</div>
            <el-select v-model="currentModel" placeholder="选择模型" size="default" @change="handleModelChange">
              <template #prefix>
                <i class="fas fa-robot model-icon"></i>
              </template>
              <el-option
                v-for="model in availableModels"
                :key="model.value"
                :label="model.label"
                :value="model.value"
              />
            </el-select>
          </div> -->
          <div class="chat-status">
            <div class="status-indicator"></div>
            <span>AI助手在线</span>
          </div>
        </div>
        
        <div class="chat-messages" ref="messagesRef">
          <ChatMessage
            v-for="(message, index) in currentMessages"
            :key="index"
            :message="message"
            :is-stream="isStreaming && index === currentMessages.length - 1"
            :is-waiting="isWaiting && index === currentMessages.length - 1"
            :is-thinking="isThinking && index === currentMessages.length - 1"
          />
          
          <!-- 常见问题按钮区域 - 保留这个 -->
          <div class="quick-questions" v-if="showQuickQuestions">
            <h3>你可能想问：</h3>
            <div class="questions-container">
              <button 
                v-for="(question, index) in commonQuestions" 
                :key="index" 
                class="question-btn"
                @click="handleQuickQuestion(question)"
              >
                {{ question }}
              </button>
            </div>
          </div>
        </div>
        
        <div class="chat-input-area">
          <div class="input-row">
            <textarea
              v-model="currentMessage"
              @keydown.enter.prevent="sendMessage"
              @input="adjustTextareaHeight"
              :placeholder="'输入您的法律问题...'"
              rows="1"
              ref="inputRef"
            ></textarea>
            <button 
              class="send-button" 
              @click="sendMessage"
              :disabled="isStreaming || !currentMessage.trim()"
            >
              <i class="fas fa-paper-plane"></i>
            </button>
          </div>
          <!-- 移除这里的快捷建议按钮 -->
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import ChatMessage from '../components/ChatMessage.vue'
import { chatAPI } from '../services/api'
import useUserInfoStore from '@/stores/user.js'
import useChatIdStore from '@/stores/chatId.js'

const chatIdStore = useChatIdStore()
const userInfoStore = useUserInfoStore()

const isDark = ref(false)
const messagesRef = ref(null)
const inputRef = ref(null)
const currentMessage = ref('')
const isStreaming = ref(false)
const isWaiting = ref(false)
const isThinking = ref(false)

// 注释掉模型相关数据
// const availableModels = [
//   { value: 'deepseek-chat', label: 'deepseek-chat' },
//   { value: 'Qwen3', label: 'Qwen3' },
//   { value: 'gpt-4', label: 'GPT-4' },
//   { value: 'claude-3', label: 'Claude 3' },
//   { value: 'ChatGLM', label: 'ChatGLM' },
// ]
// const currentModel = ref('deepseek-chat')

const currentChatId = ref(chatIdStore.chatId || null)
const currentMessages = ref([])
const chatHistory = ref([])

const commonQuestions = [
  "我想了解劳动合同的相关法律规定",
  "如何处理房屋买卖纠纷？", 
  "公司注册需要什么材料？",
  "知识产权保护有哪些方式？",
  "如何申请法律援助？"
]

const showQuickQuestions = ref(false)
const showCards = ref(false)

const adjustTextareaHeight = () => {
  const textarea = inputRef.value
  if (textarea) {
    textarea.style.height = 'auto'
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px'
  }
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (isStreaming.value || !currentMessage.value.trim()) return
  
  showQuickQuestions.value = false
  
  const messageContent = currentMessage.value.trim()
  
  // 添加用户消息
  const userMessage = {
    role: 'user',
    content: messageContent,
    timestamp: new Date()
  }
  currentMessages.value.push(userMessage)
  
  // 清空输入
  currentMessage.value = ''
  adjustTextareaHeight()
  await scrollToBottom()

  let originalChatId = currentChatId.value

  // 如果没有当前对话ID，创建新对话
  if (!currentChatId.value) {
    try {
      const chatTitle = messageContent.length > 10 ? messageContent.substring(0, 10) + '...' : messageContent
      
      const data = await chatAPI.createNewChat(userInfoStore.userInfo.userId, chatTitle, 'chat')
      currentChatId.value = data
      originalChatId = currentChatId.value
      chatIdStore.chatId = currentChatId.value
      
      const newChat = {
        id: currentChatId.value,
        title: chatTitle
      }
      chatHistory.value = [newChat, ...chatHistory.value]
    } catch (createErr) {
      console.error('创建对话失败:', createErr)
      ElMessage.error('创建对话失败，请稍后重试')
      return
    }
  }
  
  const assistantMessage = {
    role: 'assistant',
    content: '',
    timestamp: new Date()
  }
  currentMessages.value.push(assistantMessage)
  
  isStreaming.value = true
  isWaiting.value = true
  isThinking.value = false
  
  try {
    // 注释掉模型参数，使用默认模型
    // const streamReader = await chatAPI.sendMessage(messageContent, originalChatId, currentModel.value)
    const streamReader = await chatAPI.sendMessage(messageContent, originalChatId, 'deepseek-chat')
    
    await streamReader.read(({ content, done, referenceFound, reference }) => {
      if (originalChatId !== currentChatId.value) {
        return
      }
      
      if (isWaiting.value) {
        isWaiting.value = false
      }
      
      assistantMessage.content = content
      if (referenceFound && reference) {
        assistantMessage.reference = reference
      }
      
      const lastIndex = currentMessages.value.length - 1
      currentMessages.value.splice(lastIndex, 1, { ...assistantMessage })
      
      scrollToBottom()
    })
  } catch (error) {
    console.error('发送消息失败:', error)
    if (originalChatId === currentChatId.value) {
      assistantMessage.content = '抱歉，发生了错误，请稍后重试。'
      ElMessage.error('发送消息失败，请稍后重试')
      isWaiting.value = false
    }
  } finally {
    if (originalChatId === currentChatId.value) {
      isStreaming.value = false
      isWaiting.value = false
      isThinking.value = false
      await scrollToBottom()
    }
  }
}

const loadChat = async (chatId) => {
  if (currentChatId.value === '') {
    chatHistory.value = chatHistory.value.filter(chat => chat.id !== '')
  }
  
  currentChatId.value = chatId
  chatIdStore.chatId = chatId
  
  try {
    const messages = await chatAPI.getChatMessages(chatId)
    currentMessages.value = messages || []
    
    showQuickQuestions.value = false
    
    await scrollToBottom()
  } catch (error) {
    console.error('加载对话消息失败:', error)
    ElMessage.error('加载对话消息失败，请稍后重试')
    currentMessages.value = [
      {
        role: 'assistant',
        content: '您好！我是律智AI，可以为您解答法律问题、分析法律风险、提供法律建议。请问有什么可以帮您的？',
        timestamp: new Date()
      }
    ]
  }
}

const loadChatHistory = async () => {
  try {
    const history = await chatAPI.getChatHistory(userInfoStore.userInfo.userId, 'chat')
    chatHistory.value = history?.filter(chat => chat.id !== '') || []
  } catch (error) {
    console.error('加载聊天历史失败:', error)
    chatHistory.value = []
  }
}

const startNewChat = () => {
  const hasEmptyChat = chatHistory.value.some(chat => chat.id === '')
  
  if (hasEmptyChat && currentChatId.value === '') {
    return
  }
  
  const newChatId = ''
  currentChatId.value = newChatId
  chatIdStore.chatId = newChatId
  
  currentMessages.value = [
    {
      role: 'assistant',
      content: '您好！我是法律AI助手，可以为您解答法律问题、分析法律风险、提供法律建议。请问有什么可以帮您的？',
      timestamp: new Date()
    }
  ]
  
  showQuickQuestions.value = true
  scrollToBottom()
}

const handleSessionCommand = async (chatId, command) => {
  if (command === 'rename') {
    try {
      const { value } = await ElMessageBox.prompt('请输入新的对话名称', '重命名', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /.+/,
        inputErrorMessage: '对话名称不能为空'
      })
      
      await chatAPI.renameChat(chatId, value)
      
      const chat = chatHistory.value.find(item => item.id === chatId)
      if (chat) {
        chat.title = value
        ElMessage.success('重命名成功')
      }
    } catch (error) {
      if (error === 'cancel') {
        // 用户取消操作，不做处理
      } else {
        console.error('重命名失败:', error)
        ElMessage.error('重命名失败，请稍后重试')
      }
    }
  } else if (command === 'delete') {
    try {
      await ElMessageBox.confirm('确定要删除这个对话吗？', '删除确认', {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      })
      
      await chatAPI.deleteChat(chatId)
      
      chatHistory.value = chatHistory.value.filter(item => item.id !== chatId)
      
      if (currentChatId.value === chatId) {
        startNewChat()
      }
      
      ElMessage.success('删除成功')
    } catch (error) {
      if (error === 'cancel') {
        // 用户取消删除，不做处理
      } else {
        console.error('删除对话失败:', error)
        ElMessage.error('删除失败，请稍后重试')
      }
    }
  }
}

const handleQuickQuestion = (question) => {
  currentMessage.value = question
  sendMessage()
  showQuickQuestions.value = false
}

// 注释掉模型切换处理函数
// const handleModelChange = (model) => {
//   ElMessage.success(`已切换到 ${availableModels.find(m => m.value === model).label} 模型`)
//   // 这里可以添加更多逻辑，例如通知后端已切换模型
// }

// 注释掉当前模型名称的计算属性
// const getCurrentModelLabel = computed(() => {
//   const model = availableModels.find(m => m.value === currentModel.value)
//   return model ? model.label : '未选择'
// })

onMounted(async () => {
  await loadChatHistory()
  
  // 总是创建新对话，不恢复上次的对话
  startNewChat()
  
  adjustTextareaHeight()
  
  setTimeout(() => {
    showCards.value = true
  }, 100)
})
</script>

<style scoped lang="scss">
.chat-page {
  height: calc(100vh - 140px);
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.chat-container {
  display: flex;
  height: 100%;
  gap: 20px;
  max-width: 100%;
}

.sidebar {
  width: 240px;
  min-width: 240px;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 16px;
  box-shadow: var(--shadow);
  overflow: hidden;
  
  .history-header {
    flex-shrink: 0;
    padding: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--gray);
    
    h2 {
      font-size: 20px; // 从 18px 改为 20px
      font-weight: 600;
      color: var(--dark);
      margin: 0;
    }
    
    .new-chat {
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 6px 12px;
      border-radius: 6px;
      background: var(--accent);
      color: white;
      border: none;
      cursor: pointer;
      transition: all 0.3s ease;
      font-size: 16px; // 从 14px 改为 16px
      
      &:hover {
        background: #3a76d8;
        transform: translateY(-1px);
      }
      
      i {
        font-size: 14px; // 从 12px 改为 14px
      }
    }
  }
  
  .history-list {
    flex: 1;
    overflow-y: auto;
    padding: 12px 16px;
    
    .history-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      margin: 2px 0;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        background: var(--light);
      }
      
      &.active {
        background: rgba(74, 134, 232, 0.1);
        border: 1px solid var(--accent);
      }
      
      i {
        color: var(--accent);
        font-size: 18px; // 从 16px 改为 18px
        width: 20px; // 从 18px 改为 20px
        flex-shrink: 0;
      }
      
      .title {
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        font-size: 16px; // 从 14px 改为 16px
        color: var(--dark);
      }
      
      .el-button {
        padding: 2px;
        min-height: auto;
        
        i {
          font-size: 16px; // 从 14px 改为 16px
          color: var(--dark-gray);
        }
      }
    }
  }
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 16px;
  box-shadow: var(--shadow);
  overflow: hidden;
  min-height: 0;
  
  .chat-header {
    padding: 20px 24px;
    border-bottom: 1px solid var(--gray);
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: white;
    flex-shrink: 0;
    
    .chat-title {
      font-size: 22px;
      font-weight: 600;
      color: var(--dark);
    }
    
    /* 注释掉模型选择器样式 */
    /* .model-selector {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-left: auto;
      margin-right: 20px;
      
      .current-model-label {
        font-size: 16px;
        font-weight: 500;
        color: var(--dark);
        white-space: nowrap;
      }
      
      .model-icon {
        color: var(--accent);
        font-size: 16px;
        margin-right: 4px;
      }
      
      :deep(.el-input__wrapper) {
        box-shadow: 0 0 0 1px var(--gray) inset;
        background-color: var(--light);
        min-width: 120px;
        padding: 0 12px;
      }
      
      :deep(.el-input__inner) {
        color: var(--dark);
        font-size: 16px;
        font-weight: 500;
      }

      :deep(.el-select .el-input.is-focus .el-input__wrapper) {
        box-shadow: 0 0 0 1px var(--accent) inset;
      }
    } */
    
    .chat-status {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      color: var(--dark-gray);
      
      .status-indicator {
        width: 8px;
        height: 8px;
        background: var(--success);
        border-radius: 50%;
        animation: pulse 2s infinite;
      }
    }
  }
  
  .chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    min-height: 0;
  }

  .chat-input-area {
    flex-shrink: 0;
    padding: 1.5rem 2rem;
    background: rgba(255, 255, 255, 0.98);
    border-top: 1px solid var(--gray);

    .input-row {
      display: flex;
      gap: 1rem;
      align-items: flex-end;
      background: #fff;
      padding: 0.75rem;
      border-radius: 1rem;
      border: 1px solid rgba(0, 0, 0, 0.1);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
      transition: border-color 0.3s ease;
      
      &:focus-within {
        border-color: var(--accent);
      }
        
      textarea {
        flex: 1;
        resize: none;
        border: none;
        background: transparent;
        padding: 0.75rem;
        color: var(--dark);
        font-family: inherit;
        font-size: 16px; // 从 1rem 改为 16px
        line-height: 1.5;
        max-height: 150px;
        min-height: 24px;
        
        &:focus {
          outline: none;
        }
        
        &::placeholder {
          color: var(--dark-gray);
        }
      }
      
      .send-button {
        width: 2.5rem;
        height: 2.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        border: none;
        border-radius: 0.75rem;
        background: var(--accent);
        color: white;
        cursor: pointer;
        transition: all 0.2s ease;
        flex-shrink: 0;
        
        &:hover:not(:disabled) {
          background: #3a76d8;
          transform: translateY(-1px);
        }
        
        &:disabled {
          background: var(--gray);
          cursor: not-allowed;
          transform: none;
        }
        
        i {
          font-size: 1.25rem;
        }
      }
    }
  }
}

/* 添加常见问题样式 */
.quick-questions {
  margin-top: 24px;
  padding: 20px;
  border-radius: 12px;
  background-color: var(--light);
  border: 1px solid var(--gray);
  
  h3 {
    font-size: 18px; // 从 16px 改为 18px
    margin-bottom: 16px;
    color: var(--dark);
    font-weight: 600;
  }
  
  .questions-container {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    
    .question-btn {
      padding: 8px 16px;
      border-radius: 20px;
      background-color: white;
      border: 1px solid var(--gray);
      cursor: pointer;
      transition: all 0.3s ease;
      font-size: 16px; // 从 14px 改为 16px
      color: var(--dark);
      
      &:hover {
        background-color: var(--accent);
        color: white;
        border-color: var(--accent);
        transform: translateY(-1px);
      }
    }
  }
}

// 添加状态指示器动画
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .sidebar {
    width: 220px;
    min-width: 220px;
  }
}

@media (max-width: 968px) {
  .chat-page {
    padding: 16px;
  }
  
  .chat-container {
    gap: 16px;
  }
  
  .sidebar {
    width: 200px;
    min-width: 200px;
  }
}

@media (max-width: 768px) {
  .chat-page {
    padding: 12px;
    height: calc(100vh - 120px);
  }
  
  .chat-container {
    flex-direction: column;
    gap: 12px;
  }
  
  .sidebar {
    width: 100%;
    min-width: auto;
    height: 200px;
    order: 2;
    
    .history-header {
      padding: 12px;
      
      h2 {
        font-size: 18px; // 移动端适当缩小
      }
      
      .new-chat {
        padding: 4px 8px;
        font-size: 14px; // 移动端适当缩小
      }
    }
    
    .history-list {
      padding: 8px 12px;
      
      .history-item {
        padding: 6px 8px;
        
        .title {
          font-size: 14px; // 移动端适当缩小
        }
      }
    }
  }
  
  .chat-main {
    order: 1;
    flex: 1;
    min-height: 400px;
    
    .chat-header {
      padding: 16px;
      flex-direction: row;
      flex-wrap: wrap;
      gap: 8px;
      
      .chat-title {
        font-size: 20px; // 移动端适当缩小
      }
      
      /* 注释掉移动端模型选择器样式 */
      /* .model-selector {
        order: 3;
        width: 100%;
        margin: 8px 0 0 0;
        flex-wrap: wrap;
        
        .current-model-label {
          width: 100%;
          margin-bottom: 6px;
          font-size: 14px;
        }
        
        :deep(.el-select) {
          flex: 1;
          max-width: 200px;
        }
        
        :deep(.el-input__inner) {
          font-size: 16px;
          font-weight: 500;
        }
      } */
    }
    
    .chat-messages {
      padding: 16px;
      gap: 16px;
    }
    
    .chat-input-area {
      padding: 16px;
      
      .input-row {
        padding: 0.5rem;
      }
    }
  }
}

@media (max-width: 480px) {
  .chat-page {
    padding: 8px;
  }
  
  .chat-header {
    padding: 12px 16px !important;
    
    .chat-title {
      font-size: 18px;
    }
  }
  
  .chat-input-area {
    padding: 12px 16px !important;
    
    .input-row {
      padding: 0.5rem !important;
      gap: 0.5rem;
      
      textarea {
        font-size: 14px;
        padding: 0.5rem;
      }
    }
    
    .send-button {
      width: 2rem !important;
      height: 2rem !important;
      
      i {
        font-size: 1rem;
      }
    }
  }
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar,
.history-list::-webkit-scrollbar {
  width: 4px;
}

.chat-messages::-webkit-scrollbar-track,
.history-list::-webkit-scrollbar-track {
  background: var(--light);
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb,
.history-list::-webkit-scrollbar-thumb {
  background: var(--gray);
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb:hover,
.history-list::-webkit-scrollbar-thumb:hover {
  background: var(--dark-gray);
}

/* 暗黑模式适配 */
@media (prefers-color-scheme: dark) {
  .sidebar,
  .chat-main {
    background: #2c2c2c;
    
    .history-header h2,
    .history-item .title,
    .chat-header .chat-title {
      color: #e0e0e0;
    }
    
    .chat-header .chat-status {
      color: #999;
    }
    
    .history-item {
      &:hover {
        background: rgba(255, 255, 255, 0.1);
      }
      
      &.active {
        background: rgba(74, 134, 232, 0.2);
      }
    }
  }
  
  .assistant-message {
    background: #363636;
    color: #e0e0e0;
  }
  
  .user-message {
    background: #0066cc;
    color: white;
  }
  
  .quick-questions {
    background: #363636;
    border-color: #555;
    
    h3 {
      color: #e0e0e0;
    }
    
    .question-btn {
      background: #2c2c2c;
      border-color: #555;
      color: #e0e0e0;
      
      &:hover {
        background: var(--accent);
        color: white;
      }
    }
  }
  
  .suggestion-item {
    background: #363636;
    border-color: #555;
    color: #e0e0e0;
    
    &:hover {
      background: var(--accent);
      color: white;
    }
  }
  
  .chat-input-area {
    background: rgba(30, 30, 30, 0.98) !important;
    border-top: 1px solid rgba(255, 255, 255, 0.05);

    .input-row {
      background: rgba(50, 50, 50, 0.95);
      border-color: rgba(80, 80, 80, 0.2);
      
      &:focus-within {
        border-color: var(--accent);
      }

      textarea {
        color: #fff;
        
        &::placeholder {
          color: #666;
        }
      }
    }
  }
}

/* 添加进入动画 */
.list-item {
  opacity: 0;
  transform: translateY(30px);
  animation: none;
  
  &.stagger-enter {
    animation: list-item-in 0.6s ease-out forwards;
  }
}

@keyframes list-item-in {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>





