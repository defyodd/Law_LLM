"""
用户相关API路由 - 使用 PyMySQL
"""
from fastapi import APIRouter, Depends, HTTPException, Form
import pymysql
from .database.database import get_db
from .database.models import User
from .database.dao import UserDAO
from .database.schemas import Result, UserRegister, UserLogin, UserInfo
from utils import PasswordUtil, JwtUtil
from .database.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["用户认证"])


@router.post("/register", response_model=Result)
def register(
    username: str = Form(...),
    password: str = Form(...),
    repassword: str = Form(...),
    email: str = Form(...),
    db: pymysql.Connection = Depends(get_db)
):
    """用户注册"""
    # 验证密码一致性
    if password != repassword:
        return Result.error("两次密码不一致!")
    
    # 检查用户名是否已存在
    existing_user = UserDAO.get_user_by_username(username)
    if existing_user:
        return Result.error("用户已存在!")
    
    # 检查邮箱是否已存在
    existing_email = UserDAO.get_user_by_email(email)
    if existing_email:
        return Result.error("邮箱已被使用!")
    
    # 创建新用户
    hashed_password = PasswordUtil.hash_password(password)
    user_id = UserDAO.create_user(username, hashed_password, email)
    
    if user_id:
        return Result.success()
    else:
        return Result.error("用户创建失败!")


@router.post("/login", response_model=Result)
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: pymysql.Connection = Depends(get_db)
):
    """用户登录"""
    # 查询用户
    user = UserDAO.get_user_by_username(username)
    if not user:
        return Result.error("用户名或密码错误!")
    
    # 验证密码
    if not PasswordUtil.verify_password(password, user.password):
        return Result.error("用户名或密码错误!")
    
    # 生成JWT令牌
    claims = {
        "id": user.user_id,
        "username": user.username
    }
    token = JwtUtil.generate_token(claims)
    
    return Result.success(data=token)


@router.get("/getUserInfo", response_model=Result)
def get_user_info(current_user: User = Depends(get_current_user)):
    """获取用户信息"""
    user_info = UserInfo(
        userId=current_user.user_id,
        username=current_user.username,
        email=current_user.email
    )
    return Result.success(data=user_info)
