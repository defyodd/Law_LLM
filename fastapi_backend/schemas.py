"""
Pydantic模型定义，用于请求和响应数据验证
"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Any, Dict
from datetime import datetime


# 通用响应模型
class Result(BaseModel):
    code: int
    message: str = ""
    data: Optional[Any] = None

    @classmethod
    def success(cls, data: Any = None, message: str = "操作成功"):
        return cls(code=0, message=message, data=data)
    
    @classmethod
    def error(cls, message: str = "操作失败"):
        return cls(code=1, message=message, data=None)


# 用户相关模型
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    repassword: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    userId: int
    username: str
    email: str


# 问答相关模型
class ChatRequest(BaseModel):
    prompt: str
    historyId: int
    model: str = "DeepSeek"


class HistoryCreate(BaseModel):
    userId: int
    title: str
    type: str = "chat"


class HistoryRename(BaseModel):
    historyId: int
    newTitle: str


class HistoryItem(BaseModel):
    historyId: int
    title: str


class ChatItem(BaseModel):
    prompt: str
    answer: str
    reference: str


# 法律相关模型
class LawInfo(BaseModel):
    title: str
    parts: List[Dict]


class LawItem(BaseModel):
    lawId: int
    title: str


class SearchLawItem(BaseModel):
    lawId: int
    title: str
    chapterTitle: str
    articleNo: str
    articleContent: str
