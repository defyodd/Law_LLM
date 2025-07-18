<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getLawInfo } from '@/services/law.js'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const lawId = ref(route.params.id)
const lawDetail = ref(null)
const loading = ref(true)
const activeChapters = ref({}) // 用于追踪展开的章节
const targetChapter = ref(route.query.chapterTitle || null)
const targetArticle = ref(route.query.articleNo || null)
const highlightedArticle = ref(null)

// 获取法律法规详情
const fetchLawDetail = async () => {
  loading.value = true
  try {
    const response = await getLawInfo(lawId.value)
    if (response.code === 0 && response.data) {
      lawDetail.value = response.data
      document.title = response.data.title || '法律详情'
    } else {
      ElMessage.error(response.message || '获取法律详情失败')
    }
  } catch (error) {
    console.error('获取法律详情出错:', error)
    ElMessage.error('获取法律详情出错')
  } finally {
    loading.value = false
  }
}

// 切换章节展开/折叠状态
const toggleChapter = (partIndex, chapterIndex) => {
  const key = `${partIndex}-${chapterIndex}`
  activeChapters.value[key] = !activeChapters.value[key]
}

// 返回列表页
const goBack = () => {
  router.push('/library')
}

// 格式化章节标题，在"章"和后续文字之间添加空格
const formatChapterTitle = (title) => {
  // 查找"章"字的位置
  const index = title.indexOf('章')
  // 如果找到了"章"字，且不是最后一个字符，则在其后添加空格
  if (index !== -1 && index < title.length - 1) {
    return title.slice(0, index + 1) + ' ' + title.slice(index + 1)
  }
  // 如果没找到或是最后一个字符，则返回原始标题
  return title
}

// 自动展开包含目标条款的章节
const findAndExpandTargetChapter = async () => {
  if (!targetChapter.value || !targetArticle.value || !lawDetail.value) return
  
  // 遍历所有编和章节，寻找匹配的章节和条款
  for (let partIndex = 0; partIndex < lawDetail.value.parts.length; partIndex++) {
    const part = lawDetail.value.parts[partIndex]
    
    for (let chapterIndex = 0; chapterIndex < part.chapters.length; chapterIndex++) {
      const chapter = part.chapters[chapterIndex]
      
      // 检查是否是目标章节
      if (chapter.chapter_title === targetChapter.value) {
        // 展开该章节
        const key = `${partIndex}-${chapterIndex}`
        activeChapters.value[key] = true
        
        // 等待DOM更新
        await nextTick()
        
        // 找到目标条款并滚动到该位置
        const articleElement = document.getElementById(`article-${targetArticle.value}`)
        if (articleElement) {
          // 设置高亮
          highlightedArticle.value = targetArticle.value
          
          // 滚动到元素位置，添加一点偏移以获得更好的视觉效果
          setTimeout(() => {
            articleElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
          }, 300)
        }
        
        // 找到后退出循环
        return
      }
    }
  }
}

onMounted(() => {
  if (!lawId.value) {
    ElMessage.warning('未指定法律ID')
    router.push('/library')
    return
  }
  
  fetchLawDetail().then(() => {
    // 法律详情加载完成后，尝试定位到目标条款
    if (targetChapter.value && targetArticle.value) {
      findAndExpandTargetChapter()
    }
  })
})
</script>

<template>
  <div class="law-detail">
    <div class="law-detail-header">
      <button class="back-btn" @click="goBack">
        <i class="fas fa-arrow-left"></i> 返回
      </button>
      
      <h1 v-if="lawDetail" class="law-title">{{ lawDetail.title }}</h1>
      <div class="law-meta" v-if="lawDetail">
      </div>
    </div>
    
    <div v-if="loading" class="loading-container">
      <i class="fas fa-spinner fa-spin"></i>
      <p>正在加载法律内容...</p>
    </div>
    
    <div v-else-if="!lawDetail" class="error-container">
      <i class="fas fa-exclamation-triangle"></i>
      <p>无法加载法律内容</p>
    </div>
    
    <div v-else class="law-content">
      <!-- 遍历编/部分 -->
      <div v-for="(part, partIndex) in lawDetail.parts" :key="`part-${partIndex}`" class="law-part">
        <div v-if="part.part_title !== '无编'" class="part-title">
          {{ part.part_title }}
        </div>
        
        <!-- 遍历章 -->
        <div v-for="(chapter, chapterIndex) in part.chapters" :key="`chapter-${partIndex}-${chapterIndex}`" class="law-chapter">
          <div 
            class="chapter-header"
            @click="toggleChapter(partIndex, chapterIndex)"
            :class="{ 'active': activeChapters[`${partIndex}-${chapterIndex}`] }"
          >
            <h2 class="chapter-title">{{ formatChapterTitle(chapter.chapter_title) }}</h2>
            <i class="fas" :class="activeChapters[`${partIndex}-${chapterIndex}`] ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
          </div>
          
          <!-- 章节内容 -->
          <transition 
            name="chapter-transition" 
            @enter="el => el.style.height = el.scrollHeight + 'px'"
            @leave="el => el.style.height = '0px'"
          >
            <div 
              class="chapter-content"
              v-if="activeChapters[`${partIndex}-${chapterIndex}`]"
            >
              <!-- 遍历条款 -->
              <div 
                v-for="article in chapter.articles" 
                :key="article.article_no" 
                class="law-article"
                :id="`article-${article.article_no}`"
                :class="{ 'highlighted-article': article.article_no === highlightedArticle }"
              >
                <div class="article-number">{{ article.article_no }}</div>
                <div class="article-content">{{ article.article_content }}</div>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.law-detail {
  max-width: 1200px; 
  margin: 0 auto;
  padding: 2rem;
}

.law-detail-header {
  margin-bottom: 2.5rem;
  
  .back-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border: 1px solid var(--gray);
    background: white;
    border-radius: 0.5rem;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.3s ease;
    margin-bottom: 1.5rem;
    
    &:hover {
      background: var(--light);
      border-color: var(--accent);
      transform: translateY(-1px);
    }
    
    i {
      font-size: 0.8rem;
    }
  }
  
  .law-title {
    font-size: 2.2rem;
    font-weight: 700;
    color: var(--dark);
    margin-bottom: 1.2rem; 
    text-align: center;
  }
  
  .law-meta {
    text-align: center;
    color: var(--dark-gray);
    font-size: 0.9rem;
  }
}

.loading-container, .error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: var(--dark-gray);
  
  i {
    font-size: 2.5rem;
    margin-bottom: 1rem;
  }
  
  p {
    font-size: 1.2rem;
  }
}

.error-container {
  color: #d32f2f;
}

.law-content {
  background: white;
  border-radius: 1rem;
  box-shadow: var(--shadow);
  overflow: hidden;
  padding: 0.5rem 0; 
}

.law-part {
  margin-bottom: 1.5rem;
}

.part-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--dark);
  padding: 1.5rem;
  background: var(--light);
  border-bottom: 1px solid var(--gray);
}

.law-chapter {
  border-bottom: 1px solid var(--gray);
  
  &:last-child {
    border-bottom: none;
  }
}

.chapter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.4rem 1.8rem; 
  cursor: pointer;
  transition: background-color 0.3s ease;
  
  &:hover {
    background: rgba(0, 0, 0, 0.02);
  }
  
  &.active {
    background: var(--light);
    border-bottom: 1px solid var(--gray);
  }
  
  .chapter-title {
    font-size: 1.4rem; 
    font-weight: 600;
    color: var(--dark);
    margin: 0;
  }
  
  i {
    color: var(--dark-gray);
    transition: transform 0.3s ease;
    font-size: 1.1rem; 
    
    &.fa-chevron-up {
      transform: rotate(0);
    }
    
    &.fa-chevron-down {
      transform: rotate(0);
    }
  }
}

.chapter-content {
  padding: 0 2rem; 
  overflow: hidden;
}

.chapter-transition-enter-active,
.chapter-transition-leave-active {
  transition: all 0.6s ease-in-out; 
  overflow: hidden;
}

.chapter-transition-enter-from,
.chapter-transition-leave-to {
  opacity: 0;
  height: 0 !important;
  padding-top: 0;
  padding-bottom: 0;
}

.chapter-transition-enter-to,
.chapter-transition-leave-from {
  opacity: 1;
  height: auto;
}

.law-article {
  display: flex;
  gap: 2rem; 
  padding: 1.4rem 0; 
  border-bottom: 1px solid var(--gray);
  
  &:last-child {
    border-bottom: none;
  }
  
  .article-number {
    color: var(--accent);
    font-weight: 600;
    flex-shrink: 0;
    width: 80px; 
    font-size: 1.1rem; 
  }
  
  .article-content {
    flex: 1;
    line-height: 1.8; 
    color: var(--dark);
    font-size: 1.1rem; 
  }
}

.highlighted-article {
  background-color: rgba(94, 129, 244, 0.1);
  border-radius: 0.5rem;
  padding: 0.5rem;
  box-shadow: 0 0 0 2px rgba(94, 129, 244, 0.3);
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    left: -1rem;
    top: 0;
    bottom: 0;
    width: 4px;
    background: var(--accent);
    border-radius: 2px;
  }
  
  .article-number {
    font-weight: 700;
    color: var(--accent);
  }
  
  .article-content {
    font-weight: 500;
  }
  
  animation: highlight-pulse 2s infinite alternate;
}

@keyframes highlight-pulse {
  from {
    background-color: rgba(94, 129, 244, 0.1);
  }
  to {
    background-color: rgba(94, 129, 244, 0.2);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .law-detail {
    padding: 1.5rem;
  }
  
  .law-detail-header .law-title {
    font-size: 1.8rem; 
  }
  
  .chapter-header .chapter-title {
    font-size: 1.3rem; 
  }
  
  .law-article {
    flex-direction: column;
    gap: 0.5rem;
    
    .article-number {
      width: auto;
      font-size: 1.05rem; 
    }
    
    .article-content {
      font-size: 1.05rem; 
    }
  }
}

@media (max-width: 480px) {
  .law-detail {
    padding: 1rem;
  }
  
  .law-detail-header .law-title {
    font-size: 1.5rem;
  }
  
  .chapter-header .chapter-title {
    font-size: 1.1rem;
  }
}
</style>
