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

def generate_evaluation_note(prompt, answer, relevant_articles):
    """
    根据问题和回答生成评估注释
    """
    try:
        # 如果没有有效回答，返回负面评估
        if not answer or answer.strip() == '' or '抱歉' in answer or '未能' in answer:
            return "回答未能提供有效信息，需要改进。"
        
        # 根据问题类型和内容进行评估
        prompt_lower = prompt.lower()
        answer_lower = answer.lower()
        
        # 检查是否有相关法条支撑
        has_legal_support = len(relevant_articles) > 0 if relevant_articles else False
        
        # 最低工资相关问题
        if any(keyword in prompt for keyword in ['最低工资', '工资标准', '薪资标准']):
            if '地区' in answer or '省份' in answer or '各地' in answer or '不同' in answer:
                return "回答准确，正确强调了地区差异性。"
            else:
                return "回答基本准确，但未强调地区差异。"
        
        # 试用期相关问题
        elif any(keyword in prompt for keyword in ['试用期', '试用时间', '试用多久']):
            if '六个月' in answer or '6个月' in answer:
                if has_legal_support:
                    return "回答准确，符合法条规定。"
                else:
                    return "回答准确，但缺乏法条依据。"
            else:
                return "回答不够准确，未正确引用法条规定。"
        
        # 劳动合同相关问题
        elif any(keyword in prompt for keyword in ['劳动合同', '合同期限', '签订合同']):
            if has_legal_support:
                return "回答符合劳动法规定，有法条支撑。"
            else:
                return "回答基本正确，建议补充法条依据。"
        
        # 合同法相关问题
        elif any(keyword in prompt for keyword in ['合同', '协议', '违约', '解除']):
            if has_legal_support:
                return "回答准确，符合合同法规定。"
            else:
                return "回答基本正确，建议补充相关法条。"
        
        # 刑法相关问题
        elif any(keyword in prompt for keyword in ['刑法', '犯罪', '刑期', '量刑']):
            if has_legal_support:
                return "回答严谨，符合刑法条文规定。"
            else:
                return "回答需要更多法条支撑以确保准确性。"
        
        # 民法相关问题
        elif any(keyword in prompt for keyword in ['民法', '民事', '侵权', '赔偿']):
            if has_legal_support:
                return "回答准确，符合民法典规定。"
            else:
                return "回答基本正确，建议引用具体法条。"
        
        # 行政法相关问题
        elif any(keyword in prompt for keyword in ['行政', '政府', '执法', '行政处罚']):
            if has_legal_support:
                return "回答符合行政法规定，有法理依据。"
            else:
                return "回答基本正确，建议补充行政法条依据。"
        
        # 一般性法律问题
        elif any(keyword in prompt for keyword in ['法律', '法规', '条例', '规定']):
            if has_legal_support:
                return "回答准确，有充分的法条支撑。"
            else:
                return "回答基本正确，建议补充具体法条引用。"
        
        # 程序性问题（如何办理、流程等）
        elif any(keyword in prompt for keyword in ['如何', '怎么', '流程', '程序', '办理']):
            if '步骤' in answer or '流程' in answer or '程序' in answer:
                return "回答详细，程序说明清晰。"
            else:
                return "回答基本正确，建议补充具体程序步骤。"
        
        # 时间期限相关问题
        elif any(keyword in prompt for keyword in ['多久', '期限', '时间', '几天', '几个月']):
            if any(time_word in answer for time_word in ['天', '月', '年', '日', '小时']):
                return "回答准确，时间期限明确。"
            else:
                return "回答需要补充具体时间期限。"
        
        # 权利义务相关问题
        elif any(keyword in prompt for keyword in ['权利', '义务', '责任', '权益']):
            if has_legal_support:
                return "回答准确，权利义务阐述清晰。"
            else:
                return "回答基本正确，建议补充法律依据。"
        
        # 默认评估
        else:
            if has_legal_support:
                return "回答有法条支撑，内容较为准确。"
            else:
                return "回答基本合理，建议补充法律依据。"
                
    except Exception as e:
        logger.warning(f"生成评估注释时出错: {str(e)}")
        return "自动评估功能异常，请人工核实答案准确性。"

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
        
        # 生成评估注释
        evaluation_note = generate_evaluation_note(prompt, answer, relevant_articles)
        
        # 将评估注释添加到reference中
        if evaluation_note:
            reference += f"\n\n💡 评估：{evaluation_note}"
        
        # 打印测试数据用于收集（按照您提供的模板格式）
        print("=" * 60, flush=True)
        print("📊 测试数据收集:", flush=True)
        print(f'"question": "{prompt}",', flush=True)
        print(f'"expected_answer": "",  # 需要手动填写预期答案', flush=True)
        
        # 提取检索到的法条文本作为retrieved_text
        retrieved_text = ""
        if relevant_articles:
            retrieved_texts = []
            for article in relevant_articles[:2]:  # 取前2个最相关的法条
                if isinstance(article, dict):
                    article_content = article.get('article_content', article.get('content', ''))
                    law_title = article.get('law_title', article.get('title', ''))
                    article_no = article.get('article_no', '')
                    
                    if article_content and article_content != '内容缺失':
                        text = f"根据《{law_title}》{article_no}，{article_content[:100]}"
                        retrieved_texts.append(text)
            retrieved_text = "……".join(retrieved_texts)
        
        print(f'"retrieved_text": "{retrieved_text}",', flush=True)
        print(f'"model_output": "{answer[:100]}{'...' if len(answer) > 100 else ''}",', flush=True)
        print(f'"evaluation_note": "{evaluation_note}"', flush=True)
        print("=" * 60, flush=True)
        
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
