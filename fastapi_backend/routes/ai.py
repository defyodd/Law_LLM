"""
问答相关API路由 - 使用 PyMySQL
"""
from fastapi import APIRouter, Depends, Form, Query
from fastapi.responses import StreamingResponse
import pymysql
from database import get_db
from models import User, History, Chat
from dao import HistoryDAO, ChatDAO
from schemas import Result, HistoryItem, ChatItem
from auth import get_current_user
from typing import List
import sys
import os

# 添加RAG模块路径
#sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "RAG"))

try:
    from Law_LLM.RAG.dispathcer import AgentDispatcher
    dispatcher = AgentDispatcher()
except ImportError:
    dispatcher = None

router = APIRouter(prefix="/ai", tags=["AI问答"])


@router.get("/getHistory", response_model=Result)
def get_history(
    userId: int = Query(...),
    type: str = Query(...),
    db: pymysql.Connection = Depends(get_db)
):
    """获取历史记录列表"""
    histories = HistoryDAO.get_histories_by_user_id(userId)
    
    # 过滤指定类型的历史记录
    filtered_histories = [h for h in histories if h.type == type]
    
    history_list = [
        HistoryItem(historyId=h.history_id, title=h.title or "")
        for h in filtered_histories
    ]
    
    return Result.success(data=history_list)


@router.get("/getChatInfo", response_model=Result)
def get_chat_info(
    historyId: int = Query(...),
    db: pymysql.Connection = Depends(get_db)
):
    """获取历史记录详细信息"""
    chats = ChatDAO.get_chats_by_history_id(historyId)
    
    chat_list = [
        ChatItem(
            prompt=chat.prompt or "",
            answer=chat.answer or "",
            reference=chat.reference or ""
        )
        for chat in chats
    ]
    
    return Result.success(data=chat_list)


@router.post("/create", response_model=Result)
def create_history(
    userId: int = Form(...),
    title: str = Form(...),
    type: str = Form(...),
    db: pymysql.Connection = Depends(get_db)
):
    """新建对话"""
    history_id = HistoryDAO.create_history(userId, title, type)
    
    if history_id:
        return Result.success(data={"historyId": history_id})
    else:
        return Result.error("历史记录创建失败")


@router.patch("/rename", response_model=Result)
def rename_history(
    historyId: int = Form(...),
    newTitle: str = Form(...),
    db: pymysql.Connection = Depends(get_db)
):
    """重命名历史记录"""
    success = HistoryDAO.update_history(historyId, title=newTitle)
    
    if success:
        return Result.success()
    else:
        return Result.error("历史记录不存在或更新失败")


@router.delete("/delete", response_model=Result)
def delete_history(
    historyId: int = Form(...),
    db: pymysql.Connection = Depends(get_db)
):
    """删除历史记录"""
    success = HistoryDAO.delete_history(historyId)
    
    if success:
        return Result.success()
    else:
        return Result.error("历史记录不存在或删除失败")


@router.post("/chat")
def chat(
    prompt: str = Form(...),
    historyId: int = Form(...),
    model: str = Form(...),
    db: pymysql.Connection = Depends(get_db)
):
    """生成问答 - 流式响应"""
    try:
        if dispatcher is None:
            return Result.error("AI服务暂时不可用")
        
        # 调用RAG模块进行问答
        result = dispatcher.route_question(prompt, historyId, model)
        
        # 解析结果
        if isinstance(result, dict):
            answer = result.get('answer', '')
            reference = result.get('reference', '本次回答由AI生成')
        else:
            answer = str(result)
            reference = '本次回答由AI生成'
        
        # 保存到数据库
        chat_id = ChatDAO.create_chat(historyId, prompt, answer, reference)
        
        if not chat_id:
            return Result.error("对话记录保存失败")
        
        # 构造流式响应
        def generate():
            # 逐字符返回答案
            for char in answer:
                yield char
            
            # 最后返回参考信息
            yield f"\n\n<!-- REFERENCE_DATA:{reference} -->"
        
        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache"}
        )
        
    except Exception as e:
        return Result.error(f"问答生成失败: {str(e)}")
