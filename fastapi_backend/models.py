"""
数据库模型定义 - 使用 PyMySQL
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
import json


class User:
    """用户模型"""
    
    def __init__(self, user_id: Optional[int] = None, username: str = "", 
                 password: str = "", email: str = "", 
                 create_time: Optional[datetime] = None):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.create_time = create_time or datetime.now()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """从字典创建用户对象"""
        return cls(
            user_id=data.get('user_id'),
            username=data.get('username', ''),
            password=data.get('password', ''),
            email=data.get('email', ''),
            create_time=data.get('create_time')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'create_time': self.create_time
        }


class History:
    """历史记录模型"""
    
    def __init__(self, history_id: Optional[int] = None, user_id: int = 0,
                 title: Optional[str] = None, type: str = "",
                 create_time: Optional[datetime] = None):
        self.history_id = history_id
        self.user_id = user_id
        self.title = title
        self.type = type
        self.create_time = create_time or datetime.now()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'History':
        """从字典创建历史记录对象"""
        return cls(
            history_id=data.get('history_id'),
            user_id=data.get('user_id', 0),
            title=data.get('title'),
            type=data.get('type', ''),
            create_time=data.get('create_time')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'history_id': self.history_id,
            'user_id': self.user_id,
            'title': self.title,
            'type': self.type,
            'create_time': self.create_time
        }


class Chat:
    """对话记录模型"""
    
    def __init__(self, chat_id: Optional[int] = None, history_id: int = 0,
                 prompt: Optional[str] = None, answer: Optional[str] = None,
                 reference: Optional[str] = None, 
                 create_time: Optional[datetime] = None):
        self.chat_id = chat_id
        self.history_id = history_id
        self.prompt = prompt
        self.answer = answer
        self.reference = reference
        self.create_time = create_time or datetime.now()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Chat':
        """从字典创建对话记录对象"""
        return cls(
            chat_id=data.get('chat_id'),
            history_id=data.get('history_id', 0),
            prompt=data.get('prompt'),
            answer=data.get('answer'),
            reference=data.get('reference'),
            create_time=data.get('create_time')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'chat_id': self.chat_id,
            'history_id': self.history_id,
            'prompt': self.prompt,
            'answer': self.answer,
            'reference': self.reference,
            'create_time': self.create_time
        }


class Law:
    """法律模型"""
    
    def __init__(self, law_id: Optional[int] = None, title: str = "",
                 parts: Optional[Dict[str, Any]] = None,
                 create_time: Optional[datetime] = None):
        self.law_id = law_id
        self.title = title
        self.parts = parts or {}
        self.create_time = create_time or datetime.now()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Law':
        """从字典创建法律对象"""
        parts = data.get('parts')
        if isinstance(parts, str):
            try:
                parts = json.loads(parts)
            except (json.JSONDecodeError, TypeError):
                parts = {}
        
        return cls(
            law_id=data.get('law_id'),
            title=data.get('title', ''),
            parts=parts,
            create_time=data.get('create_time')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'law_id': self.law_id,
            'title': self.title,
            'parts': self.parts,
            'create_time': self.create_time
        }
