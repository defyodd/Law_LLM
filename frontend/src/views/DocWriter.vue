<template>
  <div class="doc-writer-page">
    <div class="writer-container">
      <div 
        class="sidebar list-item"
        :style="{ animationDelay: '0.1s' }"
        :class="{ 'stagger-enter': showCards }"
      >
        <div class="history-header">
          <h2>文书记录</h2>
          <button class="new-doc" @click="startNewDocument">
            <i class="fas fa-plus"></i>
            新文书
          </button>
        </div>
        <div class="history-list">
          <div 
            v-for="doc in documentHistory" 
            :key="doc.id"
            class="history-item"
            :class="{ 'active': currentDocId === doc.id }"
            @click="loadDocument(doc.id)"
          >
            <i class="fas fa-file-alt"></i>
            <span class="title">{{ doc.title || '未命名文书' }}</span>
            <el-dropdown @command="(command) => handleDocumentCommand(doc.id, command)" @click.stop>
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
        class="writer-main list-item"
        :style="{ animationDelay: '0.2s' }"
        :class="{ 'stagger-enter': showCards }"
      >
        <div class="writer-header">
          <div class="doc-title">
            <span>AI文书撰写</span>
          </div>
          
          <div class="action-buttons">
            <el-dropdown @command="handleExport" :disabled="!hasGeneratedDocument">
              <el-button type="primary" size="default" :loading="exporting">
                <i class="fas fa-download"></i>
                导出 <i class="el-icon-arrow-down el-icon--right"></i>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="docx">Word文档 (.docx)</el-dropdown-item>
                  <el-dropdown-item command="pdf">PDF文档 (.pdf)</el-dropdown-item>
                  <el-dropdown-item command="txt">文本文档 (.txt)</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
        
        <div class="writer-content">
          <!-- 左侧撰写区域 -->
          <div class="writing-area">
            <div class="writing-header">
              <h3>撰写区</h3>
              <div class="writing-controls">
              </div>
            </div>
            
            <div class="messages-container" ref="messagesRef">
              <ChatMessage
                v-for="(message, index) in currentMessages"
                :key="index"
                :message="message"
                :is-stream="isStreaming && index === currentMessages.length - 1"
                :is-waiting="isWaiting && index === currentMessages.length - 1"
                :is-thinking="isThinking && index === currentMessages.length - 1"
              />
              
              <!-- 常见问题按钮区域 -->
              <div class="quick-questions" v-if="showQuickQuestions">
                <h3>常见需求：</h3>
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
            
            <div class="input-area">
              <div class="input-row">
                <textarea
                  v-model="currentMessage"
                  @keydown.enter.prevent="sendMessage"
                  @input="adjustTextareaHeight"
                  :placeholder="'描述您需要撰写的文书内容...'"
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
            </div>
          </div>
          
          <!-- 右侧预览区域 -->
          <div class="preview-area">
            <div class="preview-header">
              <h3>文档预览</h3>
              <div class="preview-controls">
                <button class="control-btn" @click="copyDocument" :disabled="!hasGeneratedDocument">
                  <i class="fas fa-copy"></i> 复制
                </button>
                <button class="control-btn" @click="clearContent" :disabled="!hasGeneratedDocument">
                  <i class="fas fa-eraser"></i> 清空
                </button>
              </div>
            </div>
            
            <div class="document-preview" ref="documentPreview">
              <div v-if="!hasGeneratedDocument" class="empty-preview">
                <i class="fas fa-file-alt"></i>
                <p>AI生成的文书将显示在这里</p>
                <span>描述您的需求，AI将为您撰写专业文书</span>
              </div>
              
              <div v-else class="document-content" v-html="processedDocument"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import ChatMessage from '../components/ChatMessage.vue'
import { chatAPI } from '../services/api'
import useUserInfoStore from '@/stores/user.js'
import useChatIdStore from '@/stores/chatId.js'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const userInfoStore = useUserInfoStore()
const chatIdStore = useChatIdStore()

// UI状态
const messagesRef = ref(null)
const inputRef = ref(null)
const documentPreview = ref(null)
const currentMessage = ref('')
const isStreaming = ref(false)
const isWaiting = ref(false)
const isThinking = ref(false)
const showCards = ref(false)
const exporting = ref(false) // 添加导出状态变量

// 文档状态
const currentDocId = ref(chatIdStore.chatId || '')
const currentMessages = ref([])
const documentHistory = ref([])
const currentDocument = ref(null)
const generatedDocument = ref('')
const showQuickQuestions = ref(true)

// 常见问题
const commonQuestions = [
  "请帮我起草一份租房合同，房东是张三，租客是李四，月租金3000元",
  "我需要一份商业合作协议书，双方各出资50万元",
  "请起草一份知识产权转让协议",
  "帮我写一份解除劳动合同通知书，理由是公司业务调整",
  "我需要一份欠款催收函，对方欠款5万元已逾期3个月"
]

// 计算是否有生成的文档
const hasGeneratedDocument = computed(() => {
  return generatedDocument.value.trim().length > 0
})

// 处理文档显示
const processedDocument = computed(() => {
  if (!generatedDocument.value) return ''
  
  const htmlContent = marked.parse(generatedDocument.value)
  return DOMPurify.sanitize(htmlContent)
})

// 输入框高度自适应
const adjustTextareaHeight = () => {
  const textarea = inputRef.value
  if (textarea) {
    textarea.style.height = 'auto'
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px'
  }
}

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

// 发送消息
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

  let originalChatId = currentDocId.value

  // 如果没有当前文档ID，创建新文档
  if (!currentDocId.value) {
    try {
      // 直接使用用户输入的前10个字符作为标题
      const docTitle = messageContent.substring(0, 20) + (messageContent.length > 20 ? '...' : '')
      
      // 调用后端API创建新文档，使用'writ'类型
      const data = await chatAPI.createNewChat(userInfoStore.userInfo.userId, docTitle, 'writ')
      currentDocId.value = data
      originalChatId = currentDocId.value
      chatIdStore.chatId = currentDocId.value
      
      const newDoc = {
        id: currentDocId.value,
        title: docTitle,
        content: ''
      }
      
      currentDocument.value = newDoc
      documentHistory.value = [newDoc, ...documentHistory.value]
      
    } catch (createErr) {
      console.error('创建文档失败:', createErr)
      ElMessage.error('创建文档失败，请稍后重试')
      return
    }
  }
  
  // 添加AI响应消息
  const assistantMessage = {
    role: 'assistant',
    content: '',
    timestamp: new Date()
  }
  currentMessages.value.push(assistantMessage)
  
  // 设置状态为生成中
  isStreaming.value = true
  isWaiting.value = true
  isThinking.value = false
  
  // 构建提示词 - 根据用户输入
  const prompt = `请根据以下要求，生成一份专业的法律文书:\n\n${messageContent}\n\n请确保文书格式规范，内容专业完整。`;
  
  try {
    // 调用后端API，获取AI生成的文书内容，使用'writ'类型
    const streamReader = await chatAPI.sendMessage(prompt, originalChatId, 'writ')
    
    let documentContent = ''
    
    await streamReader.read(({ content, done, referenceFound, reference }) => {
      if (originalChatId !== currentDocId.value) {
        return
      }
      
      if (isWaiting.value) {
        isWaiting.value = false
      }
      
      assistantMessage.content = content
      documentContent = content
      
      if (referenceFound && reference) {
        assistantMessage.reference = reference
      }
      
      const lastIndex = currentMessages.value.length - 1
      currentMessages.value.splice(lastIndex, 1, { ...assistantMessage })
      
      scrollToBottom()
    })
    
    // 更新生成的文档内容
    generatedDocument.value = documentContent
    
    // 如果有当前文档，更新其内容
    if (currentDocument.value) {
      currentDocument.value.content = documentContent
    }
    
  } catch (error) {
    console.error('生成文书失败:', error)
    assistantMessage.content = '抱歉，生成文书时发生错误，请稍后重试。'
    ElMessage.error('生成文书失败，请稍后重试')
    isWaiting.value = false
  } finally {
    if (originalChatId === currentDocId.value) {
      isStreaming.value = false
      isWaiting.value = false
      isThinking.value = false
      await scrollToBottom()
    }
  }
}

// 快速选择模板
const handleQuickQuestion = (question) => {
  currentMessage.value = question
  sendMessage()
}

// 新建文档
const startNewDocument = () => {
  // 检查是否已有未保存的新文档
  const hasEmptyDoc = documentHistory.value.some(doc => doc.id === '')
  
  if (hasEmptyDoc && currentDocId.value === '') {
    return
  }
  
  // 重置状态
  currentDocId.value = ''
  chatIdStore.chatId = ''
  currentDocument.value = null
  generatedDocument.value = ''
  
  // 重置消息
  currentMessages.value = [
    {
      role: 'assistant',
      content: '欢迎使用AI文书撰写工具。请描述您的需求，我将为您生成专业法律文书。',
      timestamp: new Date()
    }
  ]
  
  showQuickQuestions.value = true
  scrollToBottom()
}

// 加载文档
const loadDocument = async (docId) => {
  if (currentDocId.value === '') {
    documentHistory.value = documentHistory.value.filter(doc => doc.id !== '')
  }
  
  currentDocId.value = docId
  chatIdStore.chatId = docId
  
  try {
    // 从后端加载文档数据和消息
    const messages = await chatAPI.getChatMessages(docId)
    currentMessages.value = messages || []
    
    // 如果有消息历史，将最后一个助手回复作为文档内容
    if (messages && messages.length > 0) {
      const assistantMessages = messages.filter(m => m.role === 'assistant')
      if (assistantMessages.length > 0) {
        const lastAssistantMessage = assistantMessages[assistantMessages.length - 1]
        generatedDocument.value = lastAssistantMessage.content
        
        // 获取文档信息（标题等）
        const doc = documentHistory.value.find(d => d.id === docId)
        if (doc) {
          currentDocument.value = doc
        }
      }
    }
    
    showQuickQuestions.value = false
    await scrollToBottom()
  } catch (error) {
    console.error('加载文档失败:', error)
    ElMessage.error('加载文档失败，请稍后重试')
    currentMessages.value = [
      {
        role: 'assistant',
        content: '欢迎使用AI文书撰写工具。请描述您的需求，我将为您生成专业法律文书。',
        timestamp: new Date()
      }
    ]
  }
}

// 文档操作命令处理
const handleDocumentCommand = async (docId, command) => {
  if (command === 'rename') {
    try {
      const { value } = await ElMessageBox.prompt('请输入新的文档名称', '重命名', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /.+/,
        inputErrorMessage: '文档名称不能为空'
      })
      
      // 调用API重命名文档
      await chatAPI.renameChat(docId, value)
      
      // 更新本地文档信息
      const doc = documentHistory.value.find(item => item.id === docId)
      if (doc) {
        doc.title = value
        
        // 如果是当前文档，也更新当前文档信息
        if (currentDocument.value && currentDocument.value.id === docId) {
          currentDocument.value.title = value
        }
        
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
      await ElMessageBox.confirm('确定要删除这个文档吗？', '删除确认', {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      })
      
      // 调用API删除文档
      await chatAPI.deleteChat(docId)
      
      // 更新本地文档列表
      documentHistory.value = documentHistory.value.filter(item => item.id !== docId)
      
      // 如果删除的是当前文档，则创建新文档
      if (currentDocId.value === docId) {
        startNewDocument()
      }
      
      ElMessage.success('删除成功')
    } catch (error) {
      if (error === 'cancel') {
        // 用户取消删除，不做处理
      } else {
        console.error('删除文档失败:', error)
        ElMessage.error('删除失败，请稍后重试')
      }
    }
  }
}

// 清空内容 
const clearContent = () => {
  ElMessageBox.confirm('确定要清空文档预览内容吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    generatedDocument.value = ''
    if (currentDocument.value) {
      currentDocument.value.content = ''
    }
    ElMessage.success('文档预览内容已清空')
  }).catch(() => {})
}

// 复制文档内容
const copyDocument = async () => {
  if (!generatedDocument.value) {
    ElMessage.warning('没有可复制的内容')
    return
  }
  
  try {
    await navigator.clipboard.writeText(generatedDocument.value)
    ElMessage.success('文档内容已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败，请手动选择并复制')
  }
}

// 处理导出
const handleExport = async (format) => {
  if (!generatedDocument.value) {
    ElMessage.warning('没有可导出的文档内容')
    return
  }
  
  exporting.value = true
  
  try {
    // 从文档内容中提取实际标题
    let docTitle = currentDocument.value?.title || 'AI文书'
    const content = generatedDocument.value
    
    // 尝试从文档内容中提取标题
    const titleMatch = content.match(/^#\s+(.+)$/m) || content.match(/^(.+)$/m)
    if (titleMatch && titleMatch[1]) {
      docTitle = titleMatch[1].replace(/[#*_]/g, '').trim()
    }
    
    // 根据不同格式处理导出
    switch(format) {
      case 'docx':
        await exportToWord(docTitle, content)
        break
      case 'pdf':
        await exportToPdf(docTitle, content)
        break
      case 'txt':
        exportToText(docTitle, content)
        break
      default:
        throw new Error('不支持的导出格式')
    }
    
    ElMessage.success(`已成功导出为${format}格式`)
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败，请稍后重试')
  } finally {
    exporting.value = false
  }
}

// 导出为Word文档
const exportToWord = async (title, content) => {
  try {
    // 将Markdown内容解析为纯文本
    const plainContent = content.replace(/#+\s(.*)\n/g, '$1\n\n')
                              .replace(/\*\*(.*)\*\*/g, '$1')
                              .replace(/\*(.*)\*/g, '$1')
    
    // 因为浏览器环境中无法直接使用docx库的高级功能
    // 我们改为创建一个简单的HTML文件，可以被Word打开
    const htmlContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <title>${title}</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 40px; }
          h1 { text-align: center; font-size: 24px; margin-bottom: 20px; }
          p { margin-bottom: 10px; line-height: 1.5; }
        </style>
      </head>
      <body>
        <h1>${title}</h1>
        ${marked.parse(content)}
      </body>
      </html>
    `
    
    // 创建Blob并下载
    const blob = new Blob([htmlContent], { type: 'application/msword;charset=utf-8' })
    saveAs(blob, `${title}.doc`)  // .doc而不是.docx
  } catch (error) {
    console.error('Word导出错误:', error)
    throw error
  }
}

// 导出为PDF文档 - 使用浏览器原生打印功能
const exportToPdf = async (title, content) => {
  try {
    exporting.value = true
    ElMessage.info('正在准备PDF预览，请稍候...')
    
    // 计算窗口位置，让其在当前屏幕居中显示
    const windowWidth = 800
    const windowHeight = 900
    const screenWidth = window.screen.width
    const screenHeight = window.screen.height
    const left = Math.max(0, (screenWidth - windowWidth) / 2)
    const top = Math.max(0, (screenHeight - windowHeight) / 2)
    
    // 创建新窗口用于打印，指定位置和大小
    const windowFeatures = `width=${windowWidth},height=${windowHeight},left=${left},top=${top},scrollbars=yes,resizable=yes,menubar=no,toolbar=no,location=no,status=no`
    const printWindow = window.open('', '_blank', windowFeatures)
    
    if (!printWindow) {
      throw new Error('无法打开打印窗口，请检查浏览器弹窗设置')
    }
    
    // 创建专业的文档HTML内容 - 分离CSS和JS避免标签冲突
    const cssStyles = `
      /* 通用样式 */
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }
      
      body {
        font-family: "SimSun", "Microsoft YaHei", "PingFang SC", "Helvetica Neue", Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        background: white;
        font-size: 14px;
      }
      
      /* 页面容器 */
      .page-container {
        max-width: 21cm;
        margin: 0 auto;
        padding: 2cm;
        min-height: 29.7cm;
        background: white;
        position: relative;
      }
      
      /* 文档头部 */
      .document-header {
        text-align: center;
        margin-bottom: 30px;
        padding-bottom: 20px;
        border-bottom: 2px solid #333;
      }
      
      .document-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #000;
        letter-spacing: 1px;
      }
      
      .document-subtitle {
        font-size: 12px;
        color: #666;
        margin-top: 10px;
      }
      
      /* 文档内容 */
      .document-content {
        font-size: 14px;
        line-height: 1.8;
      }
      
      /* 标题样式 */
      h1, h2, h3, h4, h5, h6 {
        color: #000;
        margin-top: 25px;
        margin-bottom: 15px;
        font-weight: bold;
        page-break-after: avoid;
      }
      
      h1 { 
        font-size: 20px; 
        text-align: center;
        margin-top: 0;
      }
      h2 { 
        font-size: 18px;
        border-bottom: 1px solid #ddd;
        padding-bottom: 5px;
      }
      h3 { font-size: 16px; }
      h4 { font-size: 15px; }
      h5 { font-size: 14px; }
      h6 { font-size: 13px; }
      
      /* 段落样式 */
      p {
        margin-bottom: 12px;
        text-align: justify;
        text-indent: 2em;
        orphans: 2;
        widows: 2;
      }
      
      /* 列表样式 */
      ul, ol {
        margin: 15px 0;
        padding-left: 30px;
        page-break-inside: avoid;
      }
      
      li {
        margin-bottom: 8px;
        line-height: 1.6;
      }
      
      /* 表格样式 */
      table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 13px;
        page-break-inside: avoid;
      }
      
      th, td {
        border: 1px solid #333;
        padding: 8px 12px;
        text-align: left;
        vertical-align: top;
      }
      
      th {
        background-color: #f8f9fa;
        font-weight: bold;
        text-align: center;
      }
      
      /* 引用块样式 */
      blockquote {
        margin: 20px 0;
        padding: 15px 20px;
        border-left: 4px solid #ddd;
        background-color: #f9f9f9;
        font-style: italic;
      }
      
      /* 代码样式 */
      code {
        background-color: #f5f5f5;
        padding: 2px 4px;
        border-radius: 3px;
        font-family: "Courier New", monospace;
        font-size: 13px;
      }
      
      pre {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        overflow-x: auto;
        margin: 15px 0;
        border: 1px solid #e9ecef;
      }
      
      /* 强调样式 */
      strong, b {
        font-weight: bold;
        color: #000;
      }
      
      em, i {
        font-style: italic;
      }
      
      /* 分割线 */
      hr {
        border: none;
        border-top: 1px solid #ddd;
        margin: 25px 0;
        page-break-after: avoid;
      }
      
      /* 控制按钮容器 */
      .print-controls {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        background: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border: 1px solid #ddd;
        min-width: 250px;
      }
      
      .control-button {
        display: inline-block;
        margin: 0 5px 10px 0;
        padding: 10px 20px;
        background: #4a86e8;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      }
      
      .control-button:hover {
        background: #357abd;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
      }
      
      .control-button.secondary {
        background: #6c757d;
      }
      
      .control-button.secondary:hover {
        background: #545b62;
      }
      
      .print-tip {
        font-size: 12px;
        color: #666;
        margin-top: 12px;
        line-height: 1.5;
        padding: 8px;
        background: #f8f9fa;
        border-radius: 4px;
        border-left: 3px solid #4a86e8;
      }
      
      /* 打印样式 */
      @media print {
        body {
          background: white !important;
          -webkit-print-color-adjust: exact;
          print-color-adjust: exact;
        }
        
        .page-container {
          max-width: none;
          margin: 0;
          padding: 1.5cm;
          min-height: auto;
        }
        
        .print-controls {
          display: none !important;
        }
        
        .document-header {
          margin-bottom: 25px;
          padding-bottom: 15px;
        }
        
        .document-title {
          font-size: 22px;
        }
        
        /* 分页控制 */
        h1, h2, h3 {
          page-break-after: avoid;
        }
        
        p, li {
          page-break-inside: avoid;
          orphans: 2;
          widows: 2;
        }
        
        table {
          page-break-inside: avoid;
        }
        
        /* 确保表格和列表不在页面边界断开 */
        table, ul, ol, blockquote {
          page-break-inside: avoid;
        }
      }
      
      /* A4 纸张尺寸 */
      @page {
        size: A4;
        margin: 1.5cm;
      }
    `
    
    // 创建HTML文档
    const htmlContent = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title}</title>
  <style>${cssStyles}</style>
</head>
<body>
  <div class="print-controls">
    <button class="control-button" onclick="window.print()" title="Ctrl+P">
      🖨️ 打印/保存PDF
    </button>
    <button class="control-button secondary" onclick="window.close()" title="Esc">
      ❌ 关闭
    </button>
    <div class="print-tip">
      💡 <strong>操作提示：</strong><br>
      • 点击"打印/保存PDF"或按 <kbd>Ctrl+P</kbd><br>
      • 在打印对话框中选择"另存为PDF"<br>
      • 选择保存位置完成导出<br>
      • 按 <kbd>Esc</kbd> 关闭此窗口
    </div>
  </div>
  
  <div class="page-container">
    <div class="document-header">
      <div class="document-title">${title}</div>
      <div class="document-subtitle">生成时间：${new Date().toLocaleString('zh-CN')}</div>
    </div>
    
    <div class="document-content">
      ${marked.parse(content)}
    </div>
  </div>
</body>
</html>`
    
    // 写入HTML内容到新窗口
    printWindow.document.write(htmlContent)
    printWindow.document.close()
    
    // 添加JavaScript功能
    const scriptElement = printWindow.document.createElement('script')
    scriptElement.textContent = `
      // 键盘快捷键支持
      document.addEventListener('keydown', function(e) {
        // Ctrl+P 打印
        if (e.ctrlKey && e.key === 'p') {
          e.preventDefault();
          window.print();
        }
        // Esc 关闭
        if (e.key === 'Escape') {
          window.close();
        }
      });
      
      // 自动聚焦窗口以启用键盘快捷键
      window.focus();
      
      // 打印完成后的提示
      window.addEventListener('afterprint', function() {
        const result = confirm('打印完成！\\n\\n如果您选择了"另存为PDF"，文件已保存到指定位置。\\n\\n是否关闭此预览窗口？');
        if (result) {
          window.close();
        }
      });
      
      // 窗口加载完成后自动居中（备用方案）
      window.addEventListener('load', function() {
        try {
          const w = 800;
          const h = 900;
          const left = (screen.width - w) / 2;
          const top = (screen.height - h) / 2;
          window.moveTo(left, top);
        } catch (e) {
          // 某些浏览器可能不允许移动窗口，忽略错误
        }
      });
    `
    printWindow.document.head.appendChild(scriptElement)
    
    // 等待页面加载完成
    printWindow.onload = function() {
      // 延迟一下确保样式加载完成
      setTimeout(() => {
        exporting.value = false
        ElMessage.success('PDF预览窗口已打开，您可以打印或保存为PDF')
      }, 500)
    }
    
    // 处理窗口关闭
    printWindow.onbeforeunload = function() {
      exporting.value = false
    }
    
  } catch (error) {
    console.error('PDF导出错误:', error)
    ElMessage.error('PDF导出失败: ' + error.message)
    exporting.value = false
    throw error
  }
}

// 导出为文本文档
const exportToText = (title, content) => {
  // 将markdown转为纯文本
  const plainContent = content.replace(/#+\s(.*)\n/g, '$1\n\n')
                              .replace(/\*\*(.*)\*\*/g, '$1')
                              .replace(/\*(.*)\*/g, '$1')
  
  const blob = new Blob([plainContent], { type: 'text/plain;charset=utf-8' })
  saveAs(blob, `${title}.txt`)
}

// 创建文件保存函数
const saveAs = (blob, fileName) => {
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = fileName
  link.click()
  
  // 清理
  setTimeout(() => {
    URL.revokeObjectURL(link.href)
  }, 100)
}

// 加载历史文档
const loadDocumentHistory = async () => {
  try {
    // 使用chatAPI获取历史记录，类型为'writ'
    const history = await chatAPI.getChatHistory(userInfoStore.userInfo.userId, 'writ')
    documentHistory.value = history?.filter(doc => doc.id !== '') || []
  } catch (error) {
    console.error('加载文档历史失败:', error)
    documentHistory.value = []
  }
}

onMounted(async () => {
  // 加载文档历史
  await loadDocumentHistory()
  
  // 检查是否有保存的文档ID
  if (chatIdStore.chatId) {
    loadDocument(chatIdStore.chatId)
  } else {
    // 创建新文档
    startNewDocument()
  }
  
  // 调整输入框高度
  adjustTextareaHeight()
  
  // 动画效果
  setTimeout(() => {
    showCards.value = true
  }, 100)
})
</script>

<style scoped lang="scss">
.doc-writer-page {
  height: calc(100vh - 140px);
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.writer-container {
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
      font-size: 20px;
      font-weight: 600;
      color: var(--dark);
      margin: 0;
    }
    
    .new-doc {
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
      font-size: 16px;
      
      &:hover {
        background: #3a76d8;
        transform: translateY(-1px);
      }
      
      i {
        font-size: 14px;
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
        font-size: 18px;
        width: 20px;
        flex-shrink: 0;
      }
      
      .title {
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        font-size: 16px;
        color: var(--dark);
      }
      
      .el-button {
        padding: 2px;
        min-height: auto;
        
        i {
          font-size: 16px;
          color: var(--dark-gray);
        }
      }
    }
  }
}

.writer-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 16px;
  box-shadow: var(--shadow);
  overflow: hidden;
  min-height: 0;
  
  .writer-header {
    padding: 16px 24px;
    border-bottom: 1px solid var(--gray);
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: white;
    flex-shrink: 0;
    flex-wrap: wrap;
    gap: 10px;
    
    .doc-title {
      font-size: 22px;
      font-weight: 600;
      color: var(--dark);
    }
    
    .action-buttons {
      display: flex;
      gap: 12px;
      
      .el-button {
        display: flex;
        align-items: center;
        gap: 8px;
        
        i {
          font-size: 14px;
        }
      }
    }
  }
  
  .writer-content {
    display: flex;
    flex: 1;
    min-height: 0;
    
    .writing-area {
      flex: 1;
      display: flex;
      flex-direction: column;
      border-right: 1px solid var(--gray);
      min-width: 0;
      
      .writing-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 24px;
        border-bottom: 1px solid var(--gray);
        
        h3 {
          font-size: 18px;
          font-weight: 600;
          margin: 0;
          color: var(--dark);
        }
        
        .writing-controls {
          display: flex;
          gap: 12px;
          
          .control-btn {
            padding: 6px 12px;
            border: 1px solid var(--gray);
            border-radius: 4px;
            background: white;
            color: var(--dark);
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 6px;
            
            &:hover {
              background: var(--light);
              border-color: var(--accent);
            }
            
            i {
              font-size: 14px;
            }
          }
        }
      }
      
      .messages-container {
        flex: 1;
        overflow-y: auto;
        padding: 24px;
        display: flex;
        flex-direction: column;
        min-height: 0;
      }
      
      .input-area {
        flex-shrink: 0;
        padding: 16px 24px;
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
            font-size: 16px;
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
    
    .preview-area {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-width: 0;
      
      .preview-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 24px;
        border-bottom: 1px solid var(--gray);
        
        h3 {
          font-size: 18px;
          font-weight: 600;
          margin: 0;
          color: var(--dark);
        }
        
        .preview-controls {
          display: flex;
          gap: 12px;
          
          .control-btn {
            padding: 6px 12px;
            border: 1px solid var(--gray);
            border-radius: 4px;
            background: white;
            color: var(--dark);
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 6px;
            
            &:hover:not(:disabled) {
              background: var(--light);
              border-color: var(--accent);
            }
            
            &:disabled {
              opacity: 0.6;
              cursor: not-allowed;
            }
            
            i {
              font-size: 14px;
            }
          }
        }
      }
      
      .document-preview {
        flex: 1;
        overflow-y: auto;
        padding: 24px 32px;
        background: #f9f9f9;
        
        .empty-preview {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          color: var(--dark-gray);
          text-align: center;
          
          i {
            font-size: 48px;
            margin-bottom: 16px;
            opacity: 0.5;
          }
          
          p {
            font-size: 18px;
            font-weight: 500;
            margin: 0 0 8px 0;
          }
          
          span {
            font-size: 14px;
            max-width: 300px;
            line-height: 1.6;
          }
        }
        
        .document-content {
          font-size: 16px;
          line-height: 1.8;
          color: var(--dark);
          
          :deep(h1) {
            font-size: 24px;
            font-weight: 600;
            margin: 0 0 24px 0;
            text-align: center;
          }
          
          :deep(h2) {
            font-size: 20px;
            font-weight: 600;
            margin: 24px 0 16px 0;
          }
          
          :deep(h3) {
            font-size: 18px;
            font-weight: 600;
            margin: 20px 0 12px 0;
          }
          
          :deep(p) {
            margin: 0 0 16px 0;
          }
          
          :deep(ul), :deep(ol) {
            margin: 16px 0;
            padding-left: 24px;
          }
          
          :deep(li) {
            margin: 8px 0;
          }
        }
      }
    }
  }
}

.quick-questions {
  margin-top: 24px;
  padding: 20px;
  border-radius: 12px;
  background-color: var(--light);
  border: 1px solid var(--gray);
  
  h3 {
    font-size: 18px;
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
      font-size: 16px;
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

@media (max-width: 1200px) {
  .sidebar {
    width: 220px;
    min-width: 220px;
  }
  
  .writer-content {
    flex-direction: column;
    
    .writing-area, .preview-area {
      flex: none;
      height: 50%;
      border-right: none;
    }
    
    .writing-area {
      border-bottom: 1px solid var(--gray);
    }
  }
}

@media (max-width: 968px) {
  .doc-writer-page {
    padding: 16px;
  }
  
  .writer-container {
    flex-direction: column;
    gap: 16px;
  }
  
  .sidebar {
    width: 100%;
    min-width: auto;
    max-height: 200px;
  }
  
  .writer-main {
    height: calc(100% - 200px - 16px);
  }
  
  .writer-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    
    .action-buttons {
      width: 100%;
      justify-content: space-between;
    }
  }
  
  .writer-content {
    flex-direction: column;
    
    .writing-area, .preview-area {
      flex: none;
      height: 50%;
    }
  }
}

@media (max-width: 768px) {
  .doc-writer-page {
    padding: 12px;
    height: calc(100vh - 120px);
  }
  
  .writer-header .doc-title {
    font-size: 20px;
  }
  
  .writing-header h3, .preview-header h3 {
    font-size: 16px;
  }
  
  .document-preview {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .doc-writer-page {
    padding: 8px;
  }
  
  .writer-header {
    padding: 12px 16px;
  }
  
  .writer-header .doc-title {
    font-size: 18px;
  }
  
  .input-area {
    padding: 12px 16px;
    
    .input-row {
      padding: 0.5rem;
      gap: 0.5rem;
      
      textarea {
        font-size: 14px;
        padding: 0.5rem;
      }
    }
    
    .send-button {
      width: 2rem;
      height: 2rem;
      
      i {
        font-size: 1rem;
      }
    }
  }
  
  .preview-area .document-content {
    font-size: 14px;
    
    :deep(h1) {
      font-size: 20px;
    }
    
    :deep(h2) {
      font-size: 18px;
    }
    
    :deep(h3) {
      font-size: 16px;
    }
  }
}
</style>



