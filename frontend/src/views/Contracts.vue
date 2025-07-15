<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const searchQuery = ref('')
const showCards = ref(false)
const selectedCategory = ref('all')

const categories = ref([
  { id: 'all', name: '全部', icon: 'fas fa-th-large' },
  { id: 'employment', name: '劳动合同', icon: 'fas fa-handshake' },
  { id: 'sales', name: '买卖合同', icon: 'fas fa-shopping-cart' },
  { id: 'lease', name: '租赁合同', icon: 'fas fa-home' },
  { id: 'service', name: '服务合同', icon: 'fas fa-tools' },
  { id: 'partnership', name: '合作协议', icon: 'fas fa-users' },
  { id: 'intellectual', name: '知识产权', icon: 'fas fa-lightbulb' }
])

const contractTemplates = ref([
  {
    id: 1,
    title: '劳动合同模板',
    category: 'employment',
    description: '标准劳动合同模板，包含薪资、工作时间、职责等条款',
    downloads: 1250,
    difficulty: '简单',
    tags: ['劳动法', '雇佣关系', '薪资']
  },
  {
    id: 2,
    title: '房屋租赁合同',
    category: 'lease',
    description: '住宅及商业房屋租赁合同，涵盖租金、押金、维修责任等',
    downloads: 980,
    difficulty: '简单',
    tags: ['租赁', '房产', '押金']
  },
  {
    id: 3,
    title: '商品销售合同',
    category: 'sales',
    description: '适用于各类商品买卖的合同模板，包含交付、付款条件',
    downloads: 756,
    difficulty: '中等',
    tags: ['买卖', '交付', '付款']
  },
  {
    id: 4,
    title: '技术服务合同',
    category: 'service',
    description: 'IT技术服务、咨询服务等专业服务合同模板',
    downloads: 642,
    difficulty: '中等',
    tags: ['技术服务', '咨询', '验收']
  },
  {
    id: 5,
    title: '合作协议书',
    category: 'partnership',
    description: '企业间合作协议模板，明确各方权利义务和利益分配',
    downloads: 534,
    difficulty: '复杂',
    tags: ['合作', '利益分配', '风险承担']
  },
  {
    id: 6,
    title: '软件著作权转让协议',
    category: 'intellectual',
    description: '软件著作权转让的专业合同模板',
    downloads: 423,
    difficulty: '复杂',
    tags: ['著作权', '知识产权', '转让']
  },
  {
    id: 7,
    title: '保密协议',
    category: 'service',
    description: '商业保密协议模板，保护企业核心信息',
    downloads: 789,
    difficulty: '简单',
    tags: ['保密', '商业机密', '违约责任']
  },
  {
    id: 8,
    title: '股权转让协议',
    category: 'partnership',
    description: '公司股权转让的法律文件模板',
    downloads: 356,
    difficulty: '复杂',
    tags: ['股权', '转让', '公司法']
  }
])

const filteredTemplates = ref([])

const filterTemplates = () => {
  let filtered = contractTemplates.value

  // 按分类过滤
  if (selectedCategory.value !== 'all') {
    filtered = filtered.filter(template => template.category === selectedCategory.value)
  }

  // 按搜索关键词过滤
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(template => 
      template.title.toLowerCase().includes(query) ||
      template.description.toLowerCase().includes(query) ||
      template.tags.some(tag => tag.toLowerCase().includes(query))
    )
  }

  filteredTemplates.value = filtered
}

const selectCategory = (categoryId) => {
  selectedCategory.value = categoryId
  filterTemplates()
}

const downloadTemplate = (template) => {
  ElMessage.success(`正在下载：${template.title}`)
  console.log('下载模板:', template)
  // 这里添加下载逻辑
}

const previewTemplate = (template) => {
  ElMessage.info(`预览：${template.title}`)
  console.log('预览模板:', template)
  // 这里添加预览逻辑
}

const getDifficultyColor = (difficulty) => {
  switch (difficulty) {
    case '简单': return '#4caf50'
    case '中等': return '#ff9800'
    case '复杂': return '#f44336'
    default: return '#666'
  }
}

onMounted(() => {
  filterTemplates()
  setTimeout(() => {
    showCards.value = true
  }, 100)
})

// 监听搜索和分类变化
const performSearch = () => {
  filterTemplates()
}
</script>

<template>
  <div class="contracts">
    <div class="contracts-header list-item" :class="{ 'stagger-enter': showCards }">
      <h1>合同模板</h1>
      <p>专业的法律合同模板库，快速生成标准合同文档</p>
    </div>

    <div class="search-section list-item" :style="{ animationDelay: '0.1s' }" :class="{ 'stagger-enter': showCards }">
      <div class="search-bar">
        <div class="search-input-wrapper">
          <i class="fas fa-search search-icon"></i>
          <input 
            type="text" 
            placeholder="搜索合同模板..."
            v-model="searchQuery"
            @keyup.enter="performSearch"
            @input="filterTemplates"
          >
        </div>
        <button class="search-btn" @click="performSearch">
          <i class="fas fa-search"></i>
          搜索
        </button>
      </div>
    </div>

    <div class="categories-section">
      <h2 class="section-title list-item" :style="{ animationDelay: '0.2s' }" :class="{ 'stagger-enter': showCards }">
        合同分类
      </h2>
      <div class="categories-tabs">
        <button 
          v-for="(category, index) in categories" 
          :key="category.id"
          class="category-tab list-item"
          :style="{ animationDelay: `${0.3 + index * 0.05}s` }"
          :class="{ 'stagger-enter': showCards, 'active': selectedCategory === category.id }"
          @click="selectCategory(category.id)"
        >
          <i :class="category.icon"></i>
          <span>{{ category.name }}</span>
        </button>
      </div>
    </div>

    <div class="templates-section">
      <div class="templates-header list-item" :style="{ animationDelay: '0.5s' }" :class="{ 'stagger-enter': showCards }">
        <h2 class="section-title">合同模板 ({{ filteredTemplates.length }})</h2>
      </div>
      
      <div class="templates-grid">
        <div 
          v-for="(template, index) in filteredTemplates" 
          :key="template.id"
          class="template-card list-item"
          :style="{ animationDelay: `${0.6 + index * 0.1}s` }"
          :class="{ 'stagger-enter': showCards }"
        >
          <div class="template-header">
            <h3>{{ template.title }}</h3>
            <div class="template-meta">
              <span class="difficulty" :style="{ color: getDifficultyColor(template.difficulty) }">
                {{ template.difficulty }}
              </span>
              <span class="downloads">
                <i class="fas fa-download"></i>
                {{ template.downloads }}
              </span>
            </div>
          </div>
          
          <p class="template-description">{{ template.description }}</p>
          
          <div class="template-tags">
            <span v-for="tag in template.tags" :key="tag" class="tag">
              {{ tag }}
            </span>
          </div>
          
          <div class="template-actions">
            <button class="preview-btn" @click="previewTemplate(template)">
              <i class="fas fa-eye"></i>
              预览
            </button>
            <button class="download-btn" @click="downloadTemplate(template)">
              <i class="fas fa-download"></i>
              下载
            </button>
          </div>
        </div>
      </div>
      
      <div v-if="filteredTemplates.length === 0" class="no-results list-item" :style="{ animationDelay: '0.6s' }" :class="{ 'stagger-enter': showCards }">
        <i class="fas fa-search"></i>
        <h3>未找到相关模板</h3>
        <p>请尝试调整搜索关键词或选择其他分类</p>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.contracts {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.contracts-header {
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

.section-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: var(--dark);
  margin-bottom: 1.5rem;
}

.categories-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 2rem;
}

.category-tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: 2px solid var(--gray);
  background: white;
  border-radius: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 500;
  
  &:hover {
    border-color: var(--accent);
    transform: translateY(-2px);
  }
  
  &.active {
    background: var(--accent);
    border-color: var(--accent);
    color: white;
  }
  
  i {
    font-size: 0.9rem;
  }
}

.templates-section {
  margin-bottom: 2rem;
}

.templates-header {
  margin-bottom: 1.5rem;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.template-card {
  background: white;
  padding: 1.5rem;
  border-radius: 1rem;
  box-shadow: var(--shadow);
  border: 1px solid var(--gray);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    border-color: var(--accent);
  }
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  
  h3 {
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--dark);
    flex: 1;
    margin-right: 1rem;
  }
  
  .template-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.25rem;
    
    .difficulty {
      font-size: 0.8rem;
      font-weight: 600;
      padding: 0.2rem 0.5rem;
      border-radius: 0.5rem;
      background: rgba(0, 0, 0, 0.05);
    }
    
    .downloads {
      font-size: 0.8rem;
      color: var(--dark-gray);
      display: flex;
      align-items: center;
      gap: 0.25rem;
    }
  }
}

.template-description {
  color: var(--dark-gray);
  margin-bottom: 1rem;
  line-height: 1.5;
  font-size: 0.95rem;
}

.template-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  
  .tag {
    background: var(--light);
    color: var(--accent);
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    font-size: 0.8rem;
    font-weight: 500;
  }
}

.template-actions {
  display: flex;
  gap: 0.75rem;
  
  button {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    border: none;
    border-radius: 0.5rem;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .preview-btn {
    background: var(--light);
    color: var(--dark);
    border: 1px solid var(--gray);
    
    &:hover {
      background: #e8f4fd;
      border-color: var(--accent);
      transform: translateY(-1px);
    }
  }
  
  .download-btn {
    background: var(--accent);
    color: white;
    
    &:hover {
      background: #3a76d8;
      transform: translateY(-1px);
    }
  }
}

.no-results {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--dark-gray);
  
  i {
    font-size: 3rem;
    margin-bottom: 1rem;
    opacity: 0.5;
  }
  
  h3 {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
    color: var(--dark);
  }
  
  p {
    font-size: 1rem;
    line-height: 1.5;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .contracts {
    padding: 1rem;
  }
  
  .contracts-header h1 {
    font-size: 2rem;
  }
  
  .search-bar {
    flex-direction: column;
    
    .search-btn {
      align-self: center;
    }
  }
  
  .categories-tabs {
    justify-content: center;
  }
  
  .templates-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .template-card {
    padding: 1rem;
  }
  
  .template-header {
    flex-direction: column;
    align-items: flex-start;
    
    .template-meta {
      align-items: flex-start;
      flex-direction: row;
      gap: 1rem;
      margin-top: 0.5rem;
    }
  }
}

@media (max-width: 480px) {
  .contracts-header h1 {
    font-size: 1.8rem;
  }
  
  .section-title {
    font-size: 1.5rem;
  }
  
  .categories-tabs {
    gap: 0.25rem;
  }
  
  .category-tab {
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
  }
  
  .template-actions {
    flex-direction: column;
    
    button {
      flex: none;
    }
  }
}
</style>
