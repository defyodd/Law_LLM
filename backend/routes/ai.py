from fastapi import APIRouter, Depends, Form, Query
from fastapi.responses import StreamingResponse
import pymysql
from routes.database.database import get_db
from routes.database.models import User, History, Chat
from routes.database.dao import HistoryDAO, ChatDAO
from routes.database.schemas import Result, HistoryItem, ChatItem
from routes.database.auth import get_current_user
from typing import List
import sys
import os
import time
import logging
logger = logging.getLogger(__name__)
 

from routes.RAG.dispatcher import AgentDispatcher

try:
    dispatcher = AgentDispatcher()
    print("✅ RAG模块加载成功", flush=True)
except Exception as e:
    logger.error(f"❌ RAG模块加载失败: {str(e)}")
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
            def error_generate():
                yield "AI服务暂时不可用，请稍后再试。RAG模块可能未正确加载。"
            return StreamingResponse(
                error_generate(),
                media_type="text/plain",
                headers={"Cache-Control": "no-cache"}
            )
        
        # 记录输入参数
        print(f"收到聊天请求 - prompt: {prompt[:100]}..., historyId: {historyId}, model: {model}", flush=True)
        
        # 获取最近的对话记录用于上下文记忆
        context_chats = []
        try:
            context_chats = ChatDAO.get_recent_chats_by_history_id(historyId, limit=5)
            print(f"获取到 {len(context_chats)} 条历史对话记录用于上下文记忆", flush=True)
        except Exception as context_error:
            logger.warning(f"获取上下文记录失败: {str(context_error)}")
            context_chats = []
        
        # 调用RAG模块进行问答
        try:
            result = dispatcher.route_question(prompt, historyId, model, context_chats)
            print(result, flush=True)
            print(f"RAG模块返回结果类型: {type(result)}", flush=True)
            if isinstance(result, dict):
                print(f"RAG模块返回结果键: {list(result.keys())}", flush=True)
        except KeyError as ke:
            logger.error(f"RAG模块KeyError: {str(ke)}")
            def error_generate():
                yield f"RAG模块处理失败: 缺少必要的字段 '{str(ke)}'。这通常是因为AI模型API响应格式异常，请检查网络连接或稍后重试。"
            return StreamingResponse(
                error_generate(),
                media_type="text/plain",
                headers={"Cache-Control": "no-cache"}
            )
        except Exception as rag_error:
            logger.error(f"RAG模块异常: {str(rag_error)}", exc_info=True)
            def error_generate():
                yield f"RAG模块处理失败: {str(rag_error)}"
            return StreamingResponse(
                error_generate(),
                media_type="text/plain",
                headers={"Cache-Control": "no-cache"}
            )
        
        # 解析结果
        if isinstance(result, dict):
            # 检查必要的键是否存在
            if 'answer' not in result:
                logger.warning("RAG返回结果中缺少 'answer' 字段")
                answer = '抱歉，未能获取到回答。'
            else:
                answer = result.get('answer', '抱歉，未能获取到回答。')
            
            reference = result.get('reference', '本次回答由AI生成')
            
            # 如果是合同生成类型，添加特殊标识
            if result.get('type') == 'write':
                reference = f"合同生成 | {reference}"
            
            # 添加参考法条信息
            relevant_articles = result.get('relevant_articles', [])
            if relevant_articles:
                reference += "\n\n📚 参考法条："
                for i, article in enumerate(relevant_articles[:3], 1):
                    try:
                        if isinstance(article, dict):
                            # 获取法条的详细信息
                            article_no = article.get('article_no', '未知条文')
                            article_content = article.get('article_content', article.get('content', '内容缺失'))
                            law_title = article.get('law_title', article.get('title', ''))
                            part_title = article.get('part_title', '')
                            chapter_title = article.get('chapter_title', '')
                            score = article.get('score', 0)
                            
                            # 构建法条信息
                            article_info = f"\n\n【{i}】{article_no}"
                            
                            # 添加法律名称和章节信息
                            if law_title:
                                article_info += f"\n📖 法律：{law_title}"
                            if part_title or chapter_title:
                                section_info = " - ".join(filter(None, [part_title, chapter_title]))
                                if section_info:
                                    article_info += f"\n📑 章节：{section_info}"
                            
                            # 添加条文内容
                            if article_content and article_content != '内容缺失':
                                # 如果内容过长，进行适当截取
                                if len(article_content) > 200:
                                    article_content = article_content[:200] + "..."
                                article_info += f"\n📄 内容：{article_content}"
                            
                            # 添加相关度
                            article_info += f"\n🎯 相关度：{score:.3f}"
                            
                        else:
                            article_info = f"\n\n【{i}】{str(article)}"
                        
                        reference += article_info
                        
                    except Exception as article_error:
                        logger.warning(f"处理参考法条时出错: {str(article_error)}")
                        reference += f"\n\n【{i}】法条信息处理失败：{str(article_error)}"
        else:
            answer = str(result) if result else '抱歉，未能获取到回答。'
            reference = '本次回答由AI生成'
        
        # 确保answer不为空
        if not answer or answer.strip() == '':
            answer = '抱歉，未能生成有效回答，请重新提问。'
        
        # 保存到数据库
        try:
            chat_id = ChatDAO.create_chat(historyId, prompt, answer, reference)
            print(f"对话记录保存成功，chat_id: {chat_id}", flush=True)
        except Exception as db_error:
            logger.error(f"数据库保存失败: {str(db_error)}")
            chat_id = None
        
        if not chat_id:
            def error_generate():
                yield "对话记录保存失败，但已为您生成回答。\n\n"
                yield answer
            return StreamingResponse(
                error_generate(),
                media_type="text/plain",
                headers={"Cache-Control": "no-cache"}
            )
        
        # 构造流式响应
        def generate():
            # 模拟打字机效果，逐字符返回答案
            for i, char in enumerate(answer):
                yield char
                # 每10个字符或标点符号后短暂停顿
                if i % 10 == 0 or char in '。！？，；：':
                    time.sleep(0.05)
            
            # 最后返回参考信息
            yield f"\n\n<!-- REFERENCE_DATA:{reference} -->"
        
        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/plain; charset=utf-8"
            }
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        error_msg = str(e)
        def error_generate():
            yield f"问答生成失败: {error_msg}"
        return StreamingResponse(
            error_generate(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache"}
        )
