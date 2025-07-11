#!/usr/bin/env python3
"""
启动脚本
"""
import os
import sys
import subprocess

def check_dependencies():
    """检查依赖包"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pymysql
        return True
    except ImportError as e:
        print(f"缺少依赖包: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_database():
    """检查数据库连接"""
    try:
        from database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✓ 数据库连接正常")
        return True
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        print("请检查数据库配置")
        return False

def init_database():
    """初始化数据库"""
    try:
        from database import create_tables
        create_tables()
        print("✓ 数据库表初始化完成")
        return True
    except Exception as e:
        print(f"✗ 数据库初始化失败: {e}")
        return False

def main():
    """启动FastAPI应用"""
    print("法律AI助手 FastAPI后端启动检查...")
    print("=" * 50)
    
    # 设置工作目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查数据库
    if not check_database():
        print("尝试初始化数据库...")
        if not init_database():
            sys.exit(1)
    
    print("=" * 50)
    print("正在启动法律AI助手FastAPI后端服务...")
    print("API文档地址: http://localhost:8000/docs")
    print("健康检查: http://localhost:8000/health")
    print("按 Ctrl+C 停止服务")
    print("=" * 50)
    
    try:
        import uvicorn
        
        # 启动应用
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
