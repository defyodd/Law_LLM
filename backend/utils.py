"""
工具函数
"""
import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from routes.database.config import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Md5Util:
    """MD5加密工具"""
    
    @staticmethod
    def encrypt(text: str) -> str:
        """MD5加密"""
        return hashlib.md5(text.encode()).hexdigest()


class JwtUtil:
    """JWT工具类"""
    
    @staticmethod
    def generate_token(claims: dict) -> str:
        """生成JWT令牌"""
        to_encode = claims.copy()
        expire = datetime.utcnow() + timedelta(hours=settings.access_token_expire_hours)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    @staticmethod
    def parse_token(token: str) -> Optional[dict]:
        """解析JWT令牌"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except jwt.PyJWTError:
            return None


class PasswordUtil:
    """密码工具类"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """加密密码"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
