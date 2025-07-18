# 律智AI - 基于大语言模型的智能法律问答系统

> 🎯 **项目背景**: 生产实习项目 - 基于本地大语言模型的法律法规智能问答系统构建与 Agent 任务调度实践

一个集成了**RAG检索增强生成**、**多Agent架构**和**智能法律服务**的综合性法律AI助手系统。

## ✨ 核心特性

### 🤖 智能法律问答
- **语义检索**: 基于FAISS向量数据库的高效法条检索
- **多轮对话**: 支持上下文记忆的连续对话
- **智能分析**: 自动识别问题类型并提供针对性建议
- **置信度评估**: 动态评估回答质量并给出专业建议

### 📄 智能文书生成
- **合同生成**: 租赁、买卖、劳动、借款等多类型合同模板
- **文书起草**: 基于用户需求自动生成法律文书草稿
- **规范化模板**: 符合法律格式要求的专业文档

### 🏗️ Agent架构系统
- **AgentDispatcher**: 智能路由分发器，根据问题类型分发到对应Agent
- **LawAgent**: 法律问答专家，处理法律咨询和法条检索
- **ContractAgent**: 合同生成专家，负责各类法律文书生成
- **FAQAgent**: 常见问题处理器，快速响应高频法律问题

### 🔍 RAG检索增强
- **向量化存储**: 10000+法律条文的语义向量化存储
- **智能检索**: 毫秒级语义搜索，支持模糊匹配
- **上下文增强**: 基于检索结果的智能回答生成

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面      │    │   FastAPI后端   │    │   数据存储层    │
│                 │    │                 │    │                 │
│ • 用户交互      │◄───┤ • RESTful API   │◄───┤ • MySQL数据库   │
│ • 问答界面      │    │ • 用户认证      │    │ • FAISS向量库   │
│ • 历史记录      │    │ • 会话管理      │    │ • 法条JSON数据  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Agent层       │
                       │                 │
                       │ • AgentDispatcher│
                       │ • LawAgent      │
                       │ • ContractAgent │
                       │ • FAQAgent      │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   AI服务层      │
                       │                 │
                       │ • DeepSeek LLM  │
                       │ • RAG检索系统   │
                       │ • 向量编码模型  │
                       └─────────────────┘
```

## 📁 项目结构

```
Law_LLM/
├── README.md                    # 项目总览文档
├── 接口文档.md                   # API接口详细文档
├── legal_qa_dataset.json       # 法律问答数据集
├── backend/                     # FastAPI后端服务
│   ├── main.py                 # 主应用入口
│   ├── requirements.txt        # Python依赖包
│   ├── routes/                 # API路由模块
│   │   ├── auth.py            # 用户认证API
│   │   ├── ai.py              # AI问答API  
│   │   ├── law.py             # 法律法规API
│   │   ├── database/          # 数据库配置
│   │   └── RAG/               # RAG与Agent核心模块
│   │       ├── dispatcher.py  # Agent调度器
│   │       ├── law_agent.py   # 法律问答Agent
│   │       ├── contract_agent.py # 合同生成Agent
│   │       ├── faq_agent.py   # FAQ处理Agent
│   │       └── search.py      # RAG检索系统
├── crawled data/               # 数据爬取模块
│   ├── spider.py              # 网站爬虫主程序
│   ├── law_parser.py          # 法条解析器
│   ├── clean_laws.py          # 数据清洗工具
│   ├── cleaned_data/          # 清洗后的法律数据
│   └── data/                  # 原始爬取数据
└── FAISS/                     # 向量检索模块
    ├── build_index.py         # 索引构建工具
    ├── query_index.py         # 检索查询工具
    └── indexes/               # FAISS索引文件
```

## 🚀 快速开始

### 环境要求
- Python 3.8+
- MySQL 5.7+

### 1. 安装依赖

```bash
# 克隆项目
git clone https://github.com/defyodd/Law_LLM.git
cd Law_LLM/backend

# 安装Python依赖
pip install -r requirements.txt

# 单独安装可能卡住的包
pip install -i https://mirrors.aliyun.com/pypi/simple pydantic
pip install -i https://mirrors.aliyun.com/pypi/simple pydantic_settings
```

### 2. 数据准备

```bash
# 构建FAISS向量索引
cd ../FAISS
python build_index.py

# 如需重新爬取数据（可选）
cd ../crawled\ data
python spider.py
```

### 3. 配置数据库

```sql
-- 创建数据库
CREATE DATABASE law_llm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 启动服务

```bash
# 启动后端API服务
cd backend
uvicorn main:app --reload --log-level info
```

服务将在 `http://localhost:8000` 启动

### 5. 访问文档

- **API文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc

## 🎯 核心功能演示

### 法律问答示例
```
用户: 合同违约怎么处理？
AI: 根据《民法典》相关条款，合同违约的处理方式包括：
1. 继续履行：要求违约方继续履行合同义务
2. 损害赔偿：要求违约方赔偿因违约造成的损失
3. 解除合同：在违约严重时可以解除合同
...
```

### 合同生成示例
```
用户: 帮我生成一份房屋租赁合同
AI: 已为您生成专业的租赁合同：

# 房屋租赁合同

**甲方（出租方）：** _______________
**乙方（承租方）：** _______________

## 第一条 租赁房屋
房屋地址：_____________________
...
```

## 🛠️ 技术栈

### 后端框架
- **FastAPI**: 高性能Web框架，自动生成API文档
- **PyMySQL**: MySQL数据库连接

### AI & 检索
- **DeepSeek**: 大语言模型API
- **FAISS**: 高效向量检索
- **Sentence Transformers**: 文本向量化
- **LangChain**: Agent框架和对话记忆



## 🔗 API接口

### 用户认证
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `GET /auth/getUserInfo` - 获取用户信息

### AI问答服务
- `POST /ai/chat` - 智能问答（流式响应）
- `GET /ai/getHistory` - 获取历史记录
- `POST /ai/create` - 创建新对话
- `PATCH /ai/rename` - 重命名对话
- `DELETE /ai/delete` - 删除对话

### 法律法规管理  
- `POST /law/upload` - 上传法律文档
- `GET /law/getAllLaws` - 获取法律列表
- `GET /law/search` - 搜索法律法规

详细API文档请参考：[接口文档.md](./接口文档.md)


## 📈 项目进展

### 第一周任务 ✅
- [x] 本地部署LLM
- [x] 编写代码爬取pkulaw网站数据
- [x] 数据清洗
- [x] 将数据存入FAISS向量数据库
- [x] 初步构建RAG框架
- [x] 初步构建Agent框架
- [x] 前端demo构建

### 第二周任务 ✅
- [x] 数据库设计
- [x] RAG构建
- [x] Agent总体流程搭建
- [x] 前端部分完善
- [x] 后端API部分构建


### 第三周任务 ✅
- [x] 前后端对接
- [x] 问题测试
- [x] 前端完善并上传
- [x] 个人、总体报告撰写
- [x] 答辩ppt

## 👨‍💻 开发团队

| 姓名 | 职责 |
| ---- | ---- |
| 🧭 [许楷烨](https://github.com/defyodd) | 项目组长，后端框架搭建与 RAG 实现，PPT制作,数据测试 |
| 🧰 [曹云淇](https://github.com/saynotopeerpressure) | RAG和Agent搭建，数据测试 |
| 💻 [李卓](https://github.com/EzraLi) | 前端实现，撰写接口文档和数据库设计，数据测试 |
| 📄 [周伟余](https://github.com/zwy-maker)| 爬取数据，数据测试 |
| 🧪 [孙浩臻](https://github.com/sunqy123)| 清洗数据，数据测试 |
