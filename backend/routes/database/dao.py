"""
数据访问层 (DAO) - 使用 PyMySQL
"""
import pymysql
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import logging

from routes.database.database import db_manager
from routes.database.models import User, History, Chat, Law

logger = logging.getLogger(__name__)


class UserDAO:
    """用户数据访问对象"""
    
    @staticmethod
    def create_user(username: str, password: str, email: str) -> Optional[int]:
        """创建用户"""
        with db_manager.get_db_cursor() as cursor:
            sql = """
                INSERT INTO user (username, password, email) 
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (username, password, email))
            return cursor.lastrowid
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """根据用户名获取用户"""
        with db_manager.get_db_cursor(commit=False) as cursor:
            sql = "SELECT * FROM user WHERE username = %s"
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            return User.from_dict(result) if result else None
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        with db_manager.get_db_cursor(commit=False) as cursor:
            sql = "SELECT * FROM user WHERE email = %s"
            cursor.execute(sql, (email,))
            result = cursor.fetchone()
            return User.from_dict(result) if result else None
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """根据用户ID获取用户"""
        with db_manager.get_db_cursor(commit=False) as cursor:
            sql = "SELECT * FROM user WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            return User.from_dict(result) if result else None
    
    @staticmethod
    def update_user(user_id: int, **kwargs) -> bool:
        """更新用户信息"""
        if not kwargs:
            return False
        
        with db_manager.get_db_cursor() as cursor:
            set_clauses = []
            values = []
            
            for key, value in kwargs.items():
                if key in ['username', 'password', 'email']:
                    set_clauses.append(f"{key} = %s")
                    values.append(value)
            
            if not set_clauses:
                return False
            
            values.append(user_id)
            sql = f"UPDATE user SET {', '.join(set_clauses)} WHERE user_id = %s"
            cursor.execute(sql, values)
            return cursor.rowcount > 0
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        """删除用户"""
        with db_manager.get_db_cursor() as cursor:
            sql = "DELETE FROM user WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
            return cursor.rowcount > 0


class HistoryDAO:
    """历史记录数据访问对象"""
    
    @staticmethod
    def create_history(user_id: int, title: Optional[str], type: str) -> Optional[int]:
        """创建历史记录"""
        with db_manager.get_db_cursor() as cursor:
            sql = """
                INSERT INTO history (user_id, title, type) 
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (user_id, title, type))
            return cursor.lastrowid
    
    @staticmethod
    def get_histories_by_user_id(user_id: int, limit: int = 100, offset: int = 0) -> List[History]:
        """根据用户ID获取历史记录"""
        with db_manager.get_db_cursor(commit=False) as cursor:
            sql = """
                SELECT * FROM history 
                WHERE user_id = %s 
                ORDER BY create_time DESC 
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (user_id, limit, offset))
            results = cursor.fetchall()
            return [History.from_dict(result) for result in results]
    
    @staticmethod
    def get_history_by_id(history_id: int) -> Optional[History]:
        """根据历史记录ID获取历史记录"""
        with db_manager.get_db_cursor(commit=False) as cursor:
            sql = "SELECT * FROM history WHERE history_id = %s"
            cursor.execute(sql, (history_id,))
            result = cursor.fetchone()
            return History.from_dict(result) if result else None
    
    @staticmethod
    def update_history(history_id: int, **kwargs) -> bool:
        """更新历史记录"""
        if not kwargs:
            return False
        
        with db_manager.get_db_cursor() as cursor:
            set_clauses = []
            values = []
            
            for key, value in kwargs.items():
                if key in ['title', 'type']:
                    set_clauses.append(f"{key} = %s")
                    values.append(value)
            
            if not set_clauses:
                return False
            
            values.append(history_id)
            sql = f"UPDATE history SET {', '.join(set_clauses)} WHERE history_id = %s"
            cursor.execute(sql, values)
            return cursor.rowcount > 0
    
    @staticmethod
    def delete_history(history_id: int) -> bool:
        """删除历史记录"""
        with db_manager.get_db_cursor() as cursor:
            sql = "DELETE FROM history WHERE history_id = %s"
            cursor.execute(sql, (history_id,))
            return cursor.rowcount > 0


class ChatDAO:
    """对话记录数据访问对象"""
    
    @staticmethod
    def create_chat(history_id: int, prompt: Optional[str], answer: Optional[str], 
                   reference: Optional[str] = None) -> Optional[int]:
        """创建对话记录"""
        with db_manager.get_db_cursor() as cursor:
            sql = """
                INSERT INTO chat (history_id, prompt, answer, reference) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (history_id, prompt, answer, reference))
            return cursor.lastrowid
    
    @staticmethod
    def get_chats_by_history_id(history_id: int, limit: int = 100, offset: int = 0) -> List[Chat]:
        """根据历史记录ID获取对话记录"""
        with db_manager.get_db_cursor(commit=False) as cursor:
            sql = """
                SELECT * FROM chat 
                WHERE history_id = %s 
                ORDER BY create_time ASC 
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (history_id, limit, offset))
            results = cursor.fetchall()
            return [Chat.from_dict(result) for result in results]
    
    @staticmethod
    def get_chat_by_id(chat_id: int) -> Optional[Chat]:
        """根据对话ID获取对话记录"""
        with db_manager.get_db_cursor(commit=False) as cursor:
            sql = "SELECT * FROM chat WHERE chat_id = %s"
            cursor.execute(sql, (chat_id,))
            result = cursor.fetchone()
            return Chat.from_dict(result) if result else None
    
    @staticmethod
    def update_chat(chat_id: int, **kwargs) -> bool:
        """更新对话记录"""
        if not kwargs:
            return False
        
        with db_manager.get_db_cursor() as cursor:
            set_clauses = []
            values = []
            
            for key, value in kwargs.items():
                if key in ['prompt', 'answer', 'reference']:
                    set_clauses.append(f"{key} = %s")
                    values.append(value)
            
            if not set_clauses:
                return False
            
            values.append(chat_id)
            sql = f"UPDATE chat SET {', '.join(set_clauses)} WHERE chat_id = %s"
            cursor.execute(sql, values)
            return cursor.rowcount > 0
    
    @staticmethod
    def delete_chat(chat_id: int) -> bool:
        """删除对话记录"""
        with db_manager.get_db_cursor() as cursor:
            sql = "DELETE FROM chat WHERE chat_id = %s"
            cursor.execute(sql, (chat_id,))
            return cursor.rowcount > 0
    
    @staticmethod
    def get_recent_chats_by_history_id(history_id: int, limit: int = 5) -> List[Chat]:
        """获取指定历史记录的最近几条对话记录，用于上下文记忆"""
        with db_manager.get_db_cursor(commit=False) as cursor:
            sql = """
                SELECT * FROM chat 
                WHERE history_id = %s 
                ORDER BY create_time DESC 
                LIMIT %s
            """
            cursor.execute(sql, (history_id, limit))
            results = cursor.fetchall()
            # 返回时按时间正序排列（最老的在前）
            return [Chat.from_dict(result) for result in reversed(results)]


class LawDAO:
    """法律数据访问对象"""
    
    @staticmethod
    def create_law(title: str, parts: Dict[str, Any]) -> Optional[int]:
        """创建法律记录"""
        with db_manager.get_db_cursor() as cursor:
            sql = """
                INSERT INTO laws (title, parts) 
                VALUES (%s, %s)
            """
            cursor.execute(sql, (title, json.dumps(parts, ensure_ascii=False)))
            return cursor.lastrowid
    
    @staticmethod
    def get_law_by_id(law_id: int) -> Optional[Law]:
        """根据法律ID获取法律"""
        with db_manager.get_db_cursor(commit=False) as cursor:
            sql = "SELECT * FROM laws WHERE law_id = %s"
            cursor.execute(sql, (law_id,))
            result = cursor.fetchone()
            return Law.from_dict(result) if result else None
    
    @staticmethod
    def get_law_by_title(title: str) -> Optional[Law]:
        """根据标题获取法律"""
        with db_manager.get_db_cursor(commit=False) as cursor:
            sql = "SELECT * FROM laws WHERE title = %s"
            cursor.execute(sql, (title,))
            result = cursor.fetchone()
            return Law.from_dict(result) if result else None
    
    @staticmethod
    def search_laws(keyword: str, limit: int = 20, offset: int = 0) -> List[Law]:
        """搜索法律"""
        with db_manager.get_db_cursor(commit=False) as cursor:
            sql = """
                SELECT * FROM laws 
                WHERE title LIKE %s 
                ORDER BY create_time DESC 
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (f"%{keyword}%", limit, offset))
            results = cursor.fetchall()
            return [Law.from_dict(result) for result in results]
    
    @staticmethod
    def get_all_laws(limit: int = 100, offset: int = 0) -> List[Law]:
        """获取所有法律"""
        with db_manager.get_db_cursor(commit=False) as cursor:
            try:
                # 首先尝试带排序的查询
                sql = """
                    SELECT * FROM laws 
                    ORDER BY create_time DESC 
                    LIMIT %s OFFSET %s
                """
                cursor.execute(sql, (limit, offset))
                results = cursor.fetchall()
                return [Law.from_dict(result) for result in results]
            except pymysql.err.OperationalError as e:
                # 如果遇到内存不足错误，使用简单查询不排序
                if e.args[0] == 1038:  # Out of sort memory error
                    logger.warning(f"排序内存不足，使用备用查询方案: {e}")
                    sql = """
                        SELECT * FROM laws 
                        LIMIT %s OFFSET %s
                    """
                    cursor.execute(sql, (limit, offset))
                    results = cursor.fetchall()
                    return [Law.from_dict(result) for result in results]
                else:
                    raise
    
    @staticmethod
    def update_law(law_id: int, **kwargs) -> bool:
        """更新法律信息"""
        if not kwargs:
            return False
        
        with db_manager.get_db_cursor() as cursor:
            set_clauses = []
            values = []
            
            for key, value in kwargs.items():
                if key == 'title':
                    set_clauses.append("title = %s")
                    values.append(value)
                elif key == 'parts':
                    set_clauses.append("parts = %s")
                    values.append(json.dumps(value, ensure_ascii=False))
            
            if not set_clauses:
                return False
            
            values.append(law_id)
            sql = f"UPDATE laws SET {', '.join(set_clauses)} WHERE law_id = %s"
            cursor.execute(sql, values)
            return cursor.rowcount > 0
    
    @staticmethod
    def delete_law(law_id: int) -> bool:
        """删除法律"""
        with db_manager.get_db_cursor() as cursor:
            sql = "DELETE FROM laws WHERE law_id = %s"
            cursor.execute(sql, (law_id,))
            return cursor.rowcount > 0
    
    @staticmethod
    def get_law_titles(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """获取法律标题列表（轻量级查询，只返回 ID 和标题）"""
        with db_manager.get_db_cursor(commit=False) as cursor:
            try:
                # 只查询必要的字段，减少数据传输量
                sql = """
                    SELECT law_id, title FROM laws 
                    ORDER BY law_id DESC 
                    LIMIT %s OFFSET %s
                """
                cursor.execute(sql, (limit, offset))
                results = cursor.fetchall()
                return results
            except pymysql.err.OperationalError as e:
                # 如果遇到内存不足错误，使用简单查询不排序
                if e.args[0] == 1038:  # Out of sort memory error
                    logger.warning(f"排序内存不足，使用备用查询方案: {e}")
                    sql = """
                        SELECT law_id, title FROM laws 
                        LIMIT %s OFFSET %s
                    """
                    cursor.execute(sql, (limit, offset))
                    results = cursor.fetchall()
                    return results
                else:
                    raise
