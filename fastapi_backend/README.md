# 法律AI助手 - FastAPI后端

这是使用FastAPI重新实现的法律AI助手后端服务，替代原有的Java Spring Boot实现。

## 功能特性

- **用户认证系统**: 用户注册、登录、JWT令牌认证
- **AI问答服务**: 集成RAG模块，支持多种AI模型
- **法律法规管理**: 上传、查询、搜索法律文档
- **历史记录管理**: 对话历史的增删改查
- **流式响应**: 支持流式AI回答输出

## 技术栈

- **FastAPI**: 现代、快速的Web框架
- **SQLAlchemy**: ORM数据库操作
- **PyMySQL**: MySQL数据库连接
- **Pydantic**: 数据验证和序列化
- **JWT**: 用户认证和授权
- **bcrypt**: 密码加密

## 项目结构

```
fastapi_backend/
├── main.py              # 主应用入口
├── models.py            # 数据库模型定义
├── schemas.py           # Pydantic模型定义
├── database.py          # 数据库配置
├── auth.py              # 认证中间件
├── utils.py             # 工具函数
├── requirements.txt     # 依赖包列表
├── routes/              # API路由
│   ├── auth.py         # 用户认证相关API
│   ├── ai.py           # AI问答相关API
│   └── law.py          # 法律法规相关API
└── README.md           # 项目说明
```

## 安装和运行

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 配置环境变量（可选）:
```bash
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=root
export DB_PASSWORD=your_password
export DB_NAME=law_llm
```

3. 运行应用:
```bash
python main.py
```

应用将在 http://localhost:8000 启动

## API文档

启动应用后，可以访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 数据库

应用启动时会自动创建所需的数据库表：
- `user`: 用户表
- `history`: 历史记录表
- `chat`: 对话记录表
- `laws`: 法律法规表

## API接口

### 用户认证
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `GET /auth/getUserInfo` - 获取用户信息

### AI问答
- `GET /ai/getHistory` - 获取历史记录列表
- `GET /ai/getChatInfo` - 获取历史记录详细信息
- `POST /ai/create` - 新建对话
- `PATCH /ai/rename` - 重命名历史记录
- `DELETE /ai/delete` - 删除历史记录
- `POST /ai/chat` - 生成问答（流式响应）

### 法律法规
- `POST /law/upload` - 上传法律法规
- `GET /law/getAllLaws` - 获取法律法规列表
- `GET /law/getLawInfo` - 获取法律详细内容
- `GET /law/search` - 搜索法律法规

## 注意事项

1. 确保MySQL数据库已安装并运行
2. 修改 `utils.py` 中的 `SECRET_KEY` 为生产环境密钥
3. RAG模块需要正确配置才能使用AI问答功能
4. 生产环境中请设置适当的CORS策略
