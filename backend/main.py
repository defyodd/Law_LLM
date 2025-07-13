"""
主应用入口
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

# 导入路由
from routes.auth import router as auth_router
from routes.ai import router as ai_router
from routes.law import router as law_router

# 导入数据库配置
from routes.database.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时创建数据库表
    create_tables()
    print("数据库表创建完成", flush=True)
    yield
    # 关闭时的清理工作
    print("应用关闭", flush=True)


# 创建FastAPI应用
app = FastAPI(
    title="法律AI助手 API",
    description="基于FastAPI的法律AI助手后端服务",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router)
app.include_router(ai_router)
app.include_router(law_router)


@app.get("/")
async def root():
    """根路径"""
    return {"message": "法律AI助手 API 服务正在运行"}


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
