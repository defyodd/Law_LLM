"""
用户认证和授权中间件 - 使用 PyMySQL
"""
from fastapi import HTTPException, Depends, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import pymysql
from routes.database.database import get_db
from routes.database.models import User
from routes.database.dao import UserDAO
from utils import JwtUtil
from typing import Optional

security = HTTPBearer()


def get_current_user(
    authorization: str = Header(...),
    db: pymysql.Connection = Depends(get_db)
) -> User:
    """获取当前用户"""
    # 直接从Header获取token（不使用Bearer格式）
    token = authorization
    print(f"Received token: {token}", flush=True)
    
    # 解析JWT令牌
    payload = JwtUtil.parse_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从payload中获取用户信息
    user_id = payload.get("id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 查询用户
    user = UserDAO.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: pymysql.Connection = Depends(get_db)
) -> Optional[User]:
    """获取当前用户（可选）"""
    if credentials is None:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None
