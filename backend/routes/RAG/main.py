from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from Law_LLM.backend.routes.RAG.dispatcher import AgentDispatcher
import datetime

app = FastAPI(title="智能法律助手 API")

dispatcher = AgentDispatcher()


class QuestionRequest(BaseModel):
    prompt: str
    historyId: int
    model: str = "DeepSeek"


class ContractGenerateRequest(BaseModel):
    contract_type: str
    custom_fields: Optional[dict] = None


class HistoryResponse(BaseModel):
    history_id: int
    questions: List[dict]
    created_at: str


# 模拟历史记录存储
conversation_histories = {}


@app.post("/ai/chat")
def chat(q: QuestionRequest):
    """AI问答接口"""
    try:
        result = dispatcher.route_question(q.prompt, q.historyId, q.model)

        # 保存到历史记录
        if q.historyId not in conversation_histories:
            conversation_histories[q.historyId] = {
                "history_id": q.historyId,
                "questions": [],
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        conversation_histories[q.historyId]["questions"].append({
            "question": q.prompt,
            "answer": result,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model": q.model
        })

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求时发生错误: {str(e)}")


@app.post("/ai/contract/generate")
def generate_contract(request: ContractGenerateRequest):
    """专门的合同生成接口"""
    try:
        contract_agent = dispatcher.contract_agent

        # 构造问题字符串
        question = f"生成{request.contract_type}"
        result = contract_agent.answer(question)

        if request.custom_fields:
            result["custom_fields"] = request.custom_fields

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成合同时发生错误: {str(e)}")


@app.get("/ai/contract/types")
def get_contract_types():
    """获取支持的合同类型"""
    return {
        "contract_types": [
            {"type": "租赁合同", "description": "房屋租赁、设备租赁等合同"},
            {"type": "买卖合同", "description": "商品买卖、服务采购等合同"},
            {"type": "借款合同", "description": "个人借款、企业借贷等合同"},
            {"type": "劳动合同", "description": "雇佣关系、劳务合同等"},
            {"type": "服务合同", "description": "咨询服务、技术服务等合同"}
        ]
    }


@app.get("/ai/history/{history_id}")
def get_conversation_history(history_id: int):
    """获取对话历史记录"""
    if history_id not in conversation_histories:
        raise HTTPException(status_code=404, detail="历史记录不存在")

    return conversation_histories[history_id]


@app.get("/ai/history")
def get_all_histories():
    """获取所有历史记录列表"""
    return {
        "histories": [
            {
                "history_id": hist["history_id"],
                "question_count": len(hist["questions"]),
                "created_at": hist["created_at"],
                "last_question": hist["questions"][-1]["question"] if hist["questions"] else ""
            }
            for hist in conversation_histories.values()
        ]
    }


@app.delete("/ai/history/{history_id}")
def delete_conversation_history(history_id: int):
    """删除指定的对话历史"""
    if history_id not in conversation_histories:
        raise HTTPException(status_code=404, detail="历史记录不存在")

    del conversation_histories[history_id]
    return {"message": f"历史记录 {history_id} 已删除"}


@app.post("/ai/faq/search")
def search_faq(question: str):
    """搜索常见问题"""
    faq_agent = dispatcher.faq_agent
    result = faq_agent.answer(question)
    return result


@app.get("/ai/faq/list")
def get_faq_list():
    """获取所有常见问题列表"""
    faq_agent = dispatcher.faq_agent
    return {
        "faqs": [
            {"keyword": k, "answer": v[:50] + "..."}
            for k, v in faq_agent.FAQS.items()
        ]
    }


@app.get("/ai/models")
def get_available_models():
    """获取可用的AI模型列表"""
    return {
        "models": [
            {"name": "DeepSeek", "description": "DeepSeek智能模型"},
            {"name": "Qwen3", "description": "阿里通义千问3.0"},
            {"name": "GPT-4", "description": "OpenAI GPT-4模型"}
        ]
    }


@app.get("/ai/stats")
def get_statistics():
    """获取使用统计"""
    total_conversations = len(conversation_histories)
    total_questions = sum(len(hist["questions"]) for hist in conversation_histories.values())

    return {
        "total_conversations": total_conversations,
        "total_questions": total_questions,
        "avg_questions_per_conversation": total_questions / total_conversations if total_conversations > 0 else 0
    }


@app.get("/")
def root():
    return {
        "message": "欢迎使用智能法律助手 API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/ai/chat - AI问答",
            "contract": "/ai/contract/generate - 合同生成",
            "history": "/ai/history - 历史记录",
            "faq": "/ai/faq - 常见问题",
            "docs": "/docs - 接口文档"
        }
    }


@app.get("/health")
def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# uvicorn main:app --reload
# http://127.0.0.1:8000/docs