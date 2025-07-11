"""
配置管理 - 简化版本
"""
import os
from typing import Optional


class Settings:
    """应用配置"""
    
    def __init__(self):
        # 数据库配置
        self.db_host: str = os.getenv("DB_HOST", "localhost")
        self.db_port: int = int(os.getenv("DB_PORT", "3306"))
        self.db_user: str = os.getenv("DB_USER", "root")
        self.db_password: str = os.getenv("DB_PASSWORD", "XKY()3.14")
        self.db_name: str = os.getenv("DB_NAME", "law_llm")
        
        # JWT配置
        self.secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
        self.algorithm: str = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_hours: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", str(24 * 7)))  # 7天
        
        # 应用配置
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level: str = os.getenv("LOG_LEVEL", "info")
        
        # RAG配置
        self.rag_module_path: Optional[str] = os.getenv("RAG_MODULE_PATH")

    @property
    def database_url(self) -> str:
        """获取数据库连接URL - 已废弃，保留用于兼容性"""
        return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"


# 全局设置实例
settings = Settings()
