# 律智AI助手 - FastAPI后端

这是使用FastAPI重新实现的法律AI助手后端服务，集成了RAG检索增强生成、多Agent架构和智能法律服务功能。

## ✨ 功能特性

- **用户认证系统**: 用户注册、登录、JWT令牌认证
- **AI问答服务**: 集成RAG模块，支持多种AI模型
- **智能Agent架构**: 多Agent协作处理不同类型的法律问题
- **法律法规管理**: 上传、查询、搜索法律文档
- **历史记录管理**: 对话历史的增删改查
- **流式响应**: 支持流式AI回答输出
- **向量检索**: 基于FAISS的高效语义检索
- **合同生成**: 智能生成各类法律文书和合同模板

## 🛠️ 技术栈

### 核心框架
- **FastAPI**: 现代、快速的Web框架
- **Uvicorn**: ASGI服务器
- **Pydantic**: 数据验证和序列化
- **Python-multipart**: 文件上传支持

### 数据库与存储
- **PyMySQL**: MySQL数据库连接
- **FAISS**: 高效向量检索
- **JSON**: 结构化数据存储

### AI与检索
- **OpenAI API**: 兼容的LLM接口（DeepSeek）
- **Sentence Transformers**: 文本向量化
- **LangChain**: Agent框架和对话记忆

### 认证与安全
- **python-jose**: JWT令牌处理
- **passlib[bcrypt]**: 密码加密
- **python-dotenv**: 环境变量管理

## 📁 项目结构

```
backend/
├── main.py                      # FastAPI应用入口
├── utils.py                     # 工具函数
├── requirements.txt             # 依赖包列表
├── .env                        # 环境变量配置
├── routes/                     # API路由模块
│   ├── __init__.py
│   ├── auth.py                 # 用户认证相关API
│   ├── ai.py                   # AI问答相关API
│   ├── law.py                  # 法律法规相关API
│   ├── database/               # 数据库层
│   │   ├── __init__.py
│   │   ├── models.py           # 数据库模型定义
│   │   ├── schemas.py          # Pydantic数据模式
│   │   ├── database.py         # 数据库连接配置
│   │   ├── config.py           # 数据库配置
│   │   ├── auth.py             # 认证相关数据操作
│   │   ├── dao.py              # 数据访问对象
│   │   ├── init_db.py          # 数据库初始化
│   │   └── insert_law.py       # 法律数据插入
│   └── RAG/                    # RAG与Agent核心模块
│       ├── __init__.py
│       ├── dispatcher.py       # 智能Agent调度器
│       ├── law_agent.py        # 法律问答Agent
│       ├── contract_agent.py   # 合同生成Agent
│       ├── faq_agent.py        # FAQ处理Agent
│       ├── search.py           # RAG检索系统
│       ├── build_index.py      # FAISS索引构建
│       ├── search_faiss_index.py # FAISS索引查询
│       ├── main.py             # RAG模块入口
│       ├── requirements.txt    # RAG模块依赖
│       ├── README.md           # RAG模块文档
│       └── Agent.md            # Agent设计文档
└── __pycache__/                # Python缓存文件
```

## 🚀 安装和运行

### 1. 环境要求
- Python 3.8+
- MySQL 5.7+

### 2. 安装依赖

```bash
# 安装基础依赖
pip install -r requirements.txt

# 单独安装可能卡住的包（使用阿里云镜像）
pip install -i https://mirrors.aliyun.com/pypi/simple pydantic
pip install -i https://mirrors.aliyun.com/pypi/simple pydantic_settings

# 安装RAG模块依赖
cd routes/RAG
pip install -r requirements.txt
cd ../..
```

### 3. 环境配置

创建 `.env` 文件（可选）:
```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=law_llm

# AI模型配置
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# JWT配置
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. 数据库初始化

```sql
-- 创建数据库
CREATE DATABASE law_llm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- 应用启动时会自动创建表结构
```

### 5. 启动服务

```bash
# 启动FastAPI应用
python main.py

# 或使用uvicorn（推荐生产环境）
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

应用将在 http://localhost:8000 启动


## 🗄️ 数据库

应用启动时会自动创建所需的数据库表：

### 主要表结构
- **`user`**: 用户表 - 存储用户基本信息和认证数据
- **`history`**: 历史记录表 - 存储对话会话信息
- **`chat`**: 对话记录表 - 存储具体的问答内容
- **`laws`**: 法律法规表 - 存储法律文档和条文数据

### 表关系
- `user` 1:N `history` (一个用户可有多个对话历史)
- `history` 1:N `chat` (一个历史记录包含多轮对话)
- `laws` 独立存储法律法规数据

## 🔌 API接口

### 用户认证模块
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `GET /auth/getUserInfo` - 获取用户信息

### AI问答模块
- `GET /ai/getHistory` - 获取历史记录列表
- `GET /ai/getChatInfo` - 获取历史记录详细信息
- `POST /ai/create` - 新建对话
- `PATCH /ai/rename` - 重命名历史记录
- `DELETE /ai/delete` - 删除历史记录
- `POST /ai/chat` - 生成问答（流式响应）

### 法律法规模块
- `POST /law/upload` - 上传法律法规
- `GET /law/getAllLaws` - 获取法律法规列表
- `GET /law/getLawInfo` - 获取法律详细内容
- `GET /law/search` - 搜索法律法规

## 🤖 Agent架构

### AgentDispatcher（智能调度器）
负责根据用户问题类型智能路由到相应的Agent：
- 分析问题意图和类型
- 选择最适合的Agent处理
- 统一返回格式化结果

### 核心Agent
1. **LawAgent** - 法律问答专家
   - 处理法律咨询问题
   - 基于FAISS检索相关法条
   - 生成专业的法律解答

2. **ContractAgent** - 合同生成专家
   - 生成各类法律合同模板
   - 支持租赁、买卖、劳动等合同类型
   - 提供规范化的法律文书

3. **FAQAgent** - 常见问题处理器
   - 快速响应高频法律问题
   - 预置常见问答库
   - 提高响应效率

## 🔍 RAG检索系统

### 核心特性
- **语义检索**: 基于Sentence Transformers的多语言模型
- **向量存储**: 使用FAISS进行高效相似度搜索
- **智能问答**: 结合检索结果和LLM生成准确回答
- **上下文记忆**: 支持多轮对话和上下文理解

### 检索流程
1. 问题预处理和关键词提取
2. 向量化查询文本
3. FAISS相似度检索
4. 结果排序和筛选
5. 上下文构建和答案生成

## ⚙️ 配置说明

### 环境变量配置
项目支持通过环境变量或 `.env` 文件进行配置：

```bash
# 数据库配置
DB_HOST=localhost              # 数据库主机
DB_PORT=3306                   # 数据库端口
DB_USER=root                   # 数据库用户名
DB_PASSWORD=your_password      # 数据库密码
DB_NAME=law_llm               # 数据库名称

# AI模型配置
DEEPSEEK_API_KEY=sk-xxx       # DeepSeek API密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com  # API基础URL

# JWT配置
SECRET_KEY=your_secret_key    # JWT签名密钥
ALGORITHM=HS256               # 加密算法
ACCESS_TOKEN_EXPIRE_MINUTES=30  # 令牌过期时间（分钟）

# 应用配置
CORS_ORIGINS=*                # 允许的跨域源
LOG_LEVEL=info               # 日志级别
```

## 🚨 注意事项

### 生产环境部署
1. **安全配置**
   - 修改 `utils.py` 中的 `SECRET_KEY` 为强密码
   - 设置适当的CORS策略，不要使用 `allow_origins=["*"]`
   - 使用HTTPS协议

2. **数据库配置**
   - 确保MySQL数据库已安装并运行
   - 创建专用数据库用户，避免使用root
   - 配置数据库连接池

3. **AI模型配置**
   - 确保DeepSeek API密钥有效
   - 监控API调用次数和费用
   - 配置合适的超时时间

4. **性能优化**
   - RAG模块需要正确配置才能使用AI问答功能
   - FAISS索引文件需要预先构建
   - 考虑使用Redis缓存频繁查询的结果

### 开发环境
1. **依赖安装**
   - 某些依赖包可能需要科学上网或使用镜像源
   - pydantic相关包可能需要单独安装
   - 确保Python版本兼容

2. **调试模式**
   - 开发时使用 `reload=True` 参数
   - 查看详细日志输出
   - 使用API文档进行接口测试

## 📊 性能指标

- **响应时间**: API平均响应时间 < 500ms
- **检索性能**: FAISS检索 < 100ms
- **内存占用**: 基础运行 ~200MB，加载RAG模块 ~500MB



