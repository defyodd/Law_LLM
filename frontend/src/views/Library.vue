<script setup>
import { ref, onMounted } from 'vue'
import { getAllLaws, uploadLawJson, searchLaws } from '@/services/law.js'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter() // 导入路由
const searchQuery = ref('')
const showCards = ref(false)
const laws = ref([]) // 存储从后端获取的法律法规
const loading = ref(false) // 加载状态
const uploading = ref(false) // 上传状态
const fileInput = ref(null) // 文件输入引用
const selectedLawId = ref(null) // 添加选中的法律ID状态

// 添加搜索状态和结果变量
const searchLoading = ref(false) // 搜索加载状态
const searchResults = ref([]) // 存储搜索结果
const showSearchResults = ref(false) // 控制是否显示搜索结果

// 法律相关图标数组
const legalIcons = [
  'fas fa-gavel',           // 锤子
  'fas fa-balance-scale',   // 天平
  'fas fa-book',            // 书籍
  'fas fa-university',      // 大楼/法院
  'fas fa-landmark',        // 地标/法院
  'fas fa-scroll',          // 卷轴
  'fas fa-file-contract',   // 合同
  'fas fa-shield-alt',      // 盾牌
  'fas fa-paragraph',       // 段落
  'fas fa-stamp'            // 印章
]

// 获取随机图标
const getRandomIcon = () => {
  const randomIndex = Math.floor(Math.random() * legalIcons.length)
  return legalIcons[randomIndex]
}

// 获取法律法规列表
const fetchLaws = async () => {
  loading.value = true
  try {
    const response = await getAllLaws()
    if (response.code === 0 && response.data) {
      // 为每个法律法规添加随机图标
      laws.value = response.data.map(law => ({
        ...law,
        icon: getRandomIcon()
      }))
    } else {
      console.error('获取法律法规列表失败:', response.message)
    }
  } catch (error) {
    console.error('获取法律法规列表出错:', error)
  } finally {
    loading.value = false
  }
}

const performSearch = async () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }
  
  searchLoading.value = true
  showSearchResults.value = true
  
  try {
    const response = await searchLaws(searchQuery.value.trim())
    if (response.code === 0 && response.data) {
      searchResults.value = response.data
      if (searchResults.value.length === 0) {
        ElMessage.info('没有找到相关法律法规')
      }
    } else {
      ElMessage.error(response.message || '搜索失败')
      searchResults.value = []
    }
  } catch (error) {
    console.error('搜索法律法规出错:', error)
    ElMessage.error('搜索过程中发生错误')
    searchResults.value = []
  } finally {
    searchLoading.value = false
  }
}

// 关闭搜索结果
const closeSearchResults = () => {
  showSearchResults.value = false
  searchResults.value = []
}

// 法律法规选择
const selectLaw = (law) => {
  console.log('选择法律法规:', law.title)
  // 记录选中的法律ID
  selectedLawId.value = law.lawId
  
  // 延迟导航，以便动画效果完成
  setTimeout(() => {
    // 导航到法律法规详情页
    router.push(`/law/${law.lawId}`)
    // 重置选中状态
    setTimeout(() => {
      selectedLawId.value = null
    }, 100)
  }, 400) // 动画持续时间
}

// 根据搜索结果跳转到法律详情
const viewLawDetail = (result) => {
  // 直接使用 lawId 跳转到法律详情页，并传递章节和条款信息用于定位
  console.log('查看法律详情:', result.title, 'lawId:', result.lawId)
  router.push({
    path: `/law/${result.lawId}`,
    query: {
      chapterTitle: result.chapterTitle,
      articleNo: result.articleNo
    }
  })
}

// 处理文件上传
const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // 检查文件类型
  if (file.type !== 'application/json' && !file.name.endsWith('.json')) {
    ElMessage.error('请上传JSON格式文件')
    return
  }
  
  uploading.value = true
  try {
    const response = await uploadLawJson(file)
    if (response.code === 0) {
      ElMessage.success('法律法规上传成功')
      // 重新获取法律法规列表
      await fetchLaws()
    } else {
      ElMessage.error(response.message || '上传失败')
    }
  } catch (error) {
    console.error('上传法律法规出错:', error)
    ElMessage.error('上传过程中发生错误')
  } finally {
    uploading.value = false
    // 清空文件输入，以便可以重复上传同一文件
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}

// 触发文件选择
const triggerFileUpload = () => {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

onMounted(() => {
  // 获取法律法规数据
  fetchLaws()
  
  // 延迟显示内容以触发动画
  setTimeout(() => {
    showCards.value = true
  }, 100)
})
</script>

<template>
  <div class="library">
    <div class="library-header list-item" :class="{ 'stagger-enter': showCards }">
      <h1>法律文库</h1>
      <p>全面的法律资源与文档检索平台</p>
    </div>

    <div class="search-section list-item" :style="{ animationDelay: '0.1s' }" :class="{ 'stagger-enter': showCards }">
      <div class="search-bar">
        <div class="search-input-wrapper">
          <i class="fas fa-search search-icon"></i>
          <input 
            type="text" 
            placeholder="搜索法律条文、案例、法规..."
            v-model="searchQuery"
            @keyup.enter="performSearch"
          >
        </div>
        <button class="search-btn" @click="performSearch" :disabled="searchLoading">
          <i class="fas" :class="searchLoading ? 'fa-spinner fa-spin' : 'fa-search'"></i>
          {{ searchLoading ? '搜索中...' : '搜索' }}
        </button>
      </div>
    </div>

    <!-- 搜索结果显示区域 -->
    <div v-if="showSearchResults" class="search-results-container">
      <div class="search-results-header">
        <h2>搜索结果: "{{ searchQuery }}"</h2>
        <button class="close-btn" @click="closeSearchResults">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div v-if="searchLoading" class="search-loading">
        <i class="fas fa-spinner fa-spin"></i>
        <p>正在搜索，请稍候...</p>
      </div>
      
      <div v-else-if="searchResults.length > 0" class="search-results-list">
        <div 
          v-for="(result, index) in searchResults" 
          :key="index"
          class="search-result-item"
        >
          <div class="result-header">
            <h3>{{ result.title }}</h3>
            <span class="chapter">{{ result.chapterTitle }}</span>
            <span class="article-no">{{ result.articleNo }}</span>
          </div>
          <p class="result-content">{{ result.articleContent }}</p>
          <div class="result-footer">
            <button class="view-btn" @click="viewLawDetail(result)">
              <i class="fas fa-eye"></i> 查看详情
            </button>
          </div>
        </div>
      </div>
      
      <div v-else-if="!searchLoading" class="no-search-results">
        <i class="fas fa-search"></i>
        <p>未找到相关法律法规</p>
      </div>
    </div>

    <div class="categories-section">
      <div class="section-header list-item" :style="{ animationDelay: '0.2s' }" :class="{ 'stagger-enter': showCards }">
        <h2 class="section-title">法律法规</h2>
        
        <!-- 添加上传按钮 -->
        <div class="upload-container">
          <input 
            type="file" 
            ref="fileInput" 
            accept=".json,application/json" 
            style="display:none" 
            @change="handleFileUpload" 
          />
          <button 
            class="upload-btn" 
            @click="triggerFileUpload" 
            :disabled="uploading"
          >
            <i class="fas" :class="uploading ? 'fa-spinner fa-spin' : 'fa-upload'"></i>
            {{ uploading ? '上传中...' : '上传法规' }}
          </button>
        </div>
      </div>
      
      <!-- 加载中显示 -->
      <div v-if="loading" class="loading-container list-item" :class="{ 'stagger-enter': showCards }">
        <i class="fas fa-spinner fa-spin"></i>
        <p>正在加载法律法规...</p>
      </div>
      
      <!-- 法律法规列表 -->
      <div class="categories-grid" v-else>
        <div 
          v-for="(law, index) in laws" 
          :key="law.lawId"
          class="category-card list-item"
          :style="{ animationDelay: `${0.3 + index * 0.1}s` }"
          :class="{ 
            'stagger-enter': showCards,
            'card-selected': selectedLawId === law.lawId 
          }"
          @click="selectLaw(law)"
        >
          <div class="category-icon">
            <i :class="law.icon"></i>
          </div>
          <h3>{{ law.title }}</h3>
        </div>
        
        <!-- 无数据显示 -->
        <div v-if="laws.length === 0" class="no-data list-item" :class="{ 'stagger-enter': showCards }">
          <i class="fas fa-exclamation-circle"></i>
          <p>暂无法律法规数据</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.library {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.library-header {
  text-align: center;
  margin-bottom: 3rem;
  
  h1 {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--dark);
    margin-bottom: 1rem;
  }
  
  p {
    font-size: 1.2rem;
    color: var(--dark-gray);
  }
}

.search-section {
  margin-bottom: 3rem;
  
  .search-bar {
    display: flex;
    gap: 1rem;
    max-width: 600px;
    margin: 0 auto;
    
    .search-input-wrapper {
      flex: 1;
      position: relative;
      
      .search-icon {
        position: absolute;
        left: 1rem;
        top: 50%;
        transform: translateY(-50%);
        color: var(--dark-gray);
        font-size: 1rem;
      }
      
      input {
        width: 100%;
        padding: 1rem 1rem 1rem 3rem;
        border: 2px solid var(--gray);
        border-radius: 1rem;
        font-size: 1rem;
        transition: border-color 0.3s ease;
        
        &:focus {
          outline: none;
          border-color: var(--accent);
        }
      }
    }
    
    .search-btn {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 1rem 2rem;
      background: var(--accent);
      color: white;
      border: none;
      border-radius: 1rem;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        background: #3a76d8;
        transform: translateY(-2px);
      }
    }
  }
}

.categories-section {
  margin-bottom: 3rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.upload-container {
  display: flex;
  align-items: center;
}

.upload-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: var(--light);
  color: var(--dark);
  border: 1px solid var(--gray);
  border-radius: 0.75rem;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover:not(:disabled) {
    background: var(--accent);
    color: white;
    transform: translateY(-2px);
  }
  
  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
  
  i {
    font-size: 1rem;
  }
}

.section-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: var(--dark);
  margin-bottom: 1.5rem;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.category-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: var(--shadow);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid var(--gray);
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    border-color: var(--accent);
  }
  
  /* 添加选中动画效果 */
  &.card-selected {
    animation: card-zoom-out 0.5s forwards;
    border-color: var(--accent);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    pointer-events: none;
  }
  
  .category-icon {
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, var(--accent), #5a9af8);
    border-radius: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1rem;
    
    i {
      font-size: 1.5rem;
      color: white;
    }
  }
  
  h3 {
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--dark);
    margin-bottom: 0.5rem;
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

/* 添加缩放动画 */
@keyframes card-zoom-out {
  0% {
    transform: scale(1) translateY(-5px);
    opacity: 1;
  }
  100% {
    transform: scale(1.08);
    opacity: 0;
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);
  }
}

/* 搜索结果样式 */
.search-results-container {
  background: white;
  border-radius: 1rem;
  box-shadow: var(--shadow);
  margin: 2rem 0;
  overflow: hidden;
  border: 1px solid var(--gray);
  animation: fade-in 0.3s ease-out;
}

.search-results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--gray);
  background: var(--light);
  
  h2 {
    font-size: 1.2rem;
    margin: 0;
    color: var(--dark);
  }
  
  .close-btn {
    background: none;
    border: none;
    font-size: 1.2rem;
    color: var(--dark-gray);
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 50%;
    transition: all 0.2s;
    
    &:hover {
      background: var(--gray);
      color: var(--dark);
    }
  }
}

.search-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3rem;
  color: var(--dark-gray);
  
  i {
    font-size: 2rem;
    margin-bottom: 1rem;
  }
  
  p {
    font-size: 1rem;
  }
}

.search-results-list {
  max-height: 600px;
  overflow-y: auto;
  padding: 1rem;
}

.search-result-item {
  padding: 1.5rem;
  border-bottom: 1px solid var(--gray);
  transition: all 0.2s;
  cursor: pointer;
  
  &:last-child {
    border-bottom: none;
  }
  
  &:hover {
    background: var(--light);
  }
  
  .result-header {
    margin-bottom: 0.8rem;
    
    h3 {
      font-size: 1.2rem;
      margin: 0 0 0.5rem 0;
      color: var(--accent);
    }
    
    .chapter, .article-no {
      display: inline-block;
      padding: 0.2rem 0.5rem;
      background: var(--light);
      border-radius: 0.3rem;
      font-size: 0.8rem;
      margin-right: 0.5rem;
    }
    
    .chapter {
      color: var(--dark);
      border: 1px solid var(--gray);
    }
    
    .article-no {
      color: var(--accent);
      border: 1px solid var(--accent-light);
      background: rgba(94, 129, 244, 0.1);
    }
  }
  
  .result-content {
    margin: 0.8rem 0;
    line-height: 1.6;
    color: var(--dark);
    font-size: 1rem;
  }
  
  .result-footer {
    display: flex;
    justify-content: flex-end;
    
    .view-btn {
      padding: 0.5rem 1rem;
      background: transparent;
      color: var(--accent);
      border: 1px solid var(--accent);
      border-radius: 0.5rem;
      font-size: 0.9rem;
      cursor: pointer;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      
      &:hover {
        background: var(--accent);
        color: white;
      }
    }
  }
}

.no-search-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3rem;
  color: var(--dark-gray);
  
  i {
    font-size: 2rem;
    margin-bottom: 1rem;
    opacity: 0.5;
  }
  
  p {
    font-size: 1.2rem;
  }
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .library {
    padding: 1rem;
  }
  
  .library-header h1 {
    font-size: 2rem;
  }
  
  .search-bar {
    flex-direction: column;
    
    .search-btn {
      align-self: center;
    }
  }
  
  .categories-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .category-card {
    padding: 1.5rem;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
    
    .upload-container {
      align-self: stretch;
      
      .upload-btn {
        flex: 1;
        justify-content: center;
      }
    }
  }
}

@media (max-width: 480px) {
  .library-header h1 {
    font-size: 1.8rem;
  }
  
  .section-title {
    font-size: 1.5rem;
  }
  
  .category-card {
    padding: 1rem;
  }
}

/* 添加加载中和无数据样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: var(--dark-gray);
  
  i {
    font-size: 2rem;
    margin-bottom: 1rem;
  }
  
  p {
    font-size: 1rem;
  }
}

.no-data {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: var(--dark-gray);
  background: white;
  border-radius: 1rem;
  box-shadow: var(--shadow);
  
  i {
    font-size: 2rem;
    margin-bottom: 1rem;
    opacity: 0.5;
  }
  
  p {
    font-size: 1.2rem;
  }
}
</style>

