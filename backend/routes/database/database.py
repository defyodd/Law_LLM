"""
数据库配置和连接管理 - 使用 PyMySQL
"""
import pymysql
import pymysql.cursors
from contextlib import contextmanager
from typing import Generator, Dict, Any, Optional
from routes.database.config import settings
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.db_config = {
            'host': settings.db_host,
            'port': settings.db_port,
            'user': settings.db_user,
            'password': settings.db_password,
            'database': settings.db_name,
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor,
            'autocommit': False
        }
    
    def get_connection(self):
        """获取数据库连接"""
        try:
            connection = pymysql.connect(**self.db_config)
            return connection
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    @contextmanager
    def get_db_connection(self):
        """获取数据库连接的上下文管理器"""
        connection = None
        try:
            connection = self.get_connection()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            if connection:
                connection.close()
    
    @contextmanager
    def get_db_cursor(self, commit: bool = True):
        """获取数据库游标的上下文管理器"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            yield cursor
            if commit:
                connection.commit()
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


# 全局数据库管理器实例
db_manager = DatabaseManager()


def get_db() -> Generator[pymysql.Connection, None, None]:
    """获取数据库连接 - 用于FastAPI依赖注入"""
    connection = None
    try:
        connection = db_manager.get_connection()
        print("数据库连接成功", flush=True)
        yield connection
    except Exception as e:
        if connection:
            connection.rollback()
        logger.error(f"数据库连接失败: {e}")
        raise
    finally:
        if connection:
            connection.close()


def create_tables():
    """创建数据库表"""
    with db_manager.get_db_cursor() as cursor:
        # 创建用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `user` (
                `user_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '用户ID',
                `username` varchar(50) NOT NULL COMMENT '用户名',
                `password` varchar(255) NOT NULL COMMENT '密码',
                `email` varchar(100) NOT NULL COMMENT '邮箱',
                `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                PRIMARY KEY (`user_id`),
                UNIQUE KEY `username` (`username`),
                UNIQUE KEY `email` (`email`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
        """)
        
        # 创建历史记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `history` (
                `history_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键id',
                `user_id` int(11) NOT NULL COMMENT '用户id',
                `title` varchar(100) DEFAULT NULL COMMENT '历史记录名称',
                `type` varchar(50) NOT NULL COMMENT '类型',
                `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                PRIMARY KEY (`history_id`),
                KEY `fk_history_user` (`user_id`),
                CONSTRAINT `fk_history_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='历史记录列表';
        """)
        
        # 创建对话记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `chat` (
                `chat_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '对话ID',
                `history_id` int(11) NOT NULL COMMENT '历史记录序号',
                `prompt` text COMMENT '问题',
                `answer` text COMMENT 'AI回答',
                `reference` text COMMENT '参考',
                `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                PRIMARY KEY (`chat_id`),
                KEY `fk_chat_history` (`history_id`),
                CONSTRAINT `fk_chat_history` FOREIGN KEY (`history_id`) REFERENCES `history` (`history_id`) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话记录';
        """)
        
        # 创建法律表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `laws` (
                `law_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
                `title` varchar(255) NOT NULL COMMENT '法律标题',
                `parts` json NOT NULL COMMENT '法律内容',
                `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建日期',
                PRIMARY KEY (`law_id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='法律表';
        """)
        
        print("数据库表创建完成", flush=True)
