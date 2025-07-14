from .law_agent import LawAgent
from .contract_agent import ContractAgent
from .faq_agent import FAQAgent
import logging

logger = logging.getLogger(__name__)

class AgentDispatcher:
    def __init__(self):
        try:
            self.law_agent = LawAgent()
            print("✅ LawAgent 初始化成功", flush=True)
            print("LawAgent 初始化成功", flush=True)
        except Exception as e:
            logger.error(f"❌ LawAgent 初始化失败: {str(e)}")
            self.law_agent = None
            
        try:
            self.contract_agent = ContractAgent()
            print("✅ ContractAgent 初始化成功", flush=True)
            print("ContractAgent 初始化成功", flush=True)
        except Exception as e:
            logger.error(f"❌ ContractAgent 初始化失败: {str(e)}")
            self.contract_agent = None
            
        try:
            self.faq_agent = FAQAgent()
            print("✅ FAQAgent 初始化成功", flush=True)
            print("FAQAgent 初始化成功", flush=True)
        except Exception as e:
            logger.error(f"❌ FAQAgent 初始化失败: {str(e)}")
            self.faq_agent = None

    def determine_question_type(self, question: str) -> str:
        """判断问题类型，返回 'chat' 或 'write'"""
        # 合同生成相关关键词
        contract_creation_keywords = ["制作", "起草", "拟定", "编写", "撰写", "合同模板", "合同范本", "生成", "创建"]
        contract_types = ["租赁合同", "买卖合同", "借款合同", "劳动合同", "服务合同"]

        # 检查是否为合同生成请求
        if any(keyword in question for keyword in contract_creation_keywords):
            return "write"

        if any(contract_type in question for contract_type in contract_types) and any(keyword in question for keyword in ["生成", "制作", "起草", "拟定"]):
            return "write"

        # 默认为聊天咨询
        return "chat"

    def route_question(self, question: str, history_id: int, model: str) -> dict:
        try:
            # 判断问题类型
            question_type = self.determine_question_type(question)
            # print(question_type)
            # 优先检查FAQ
            from .main import conversation_histories
            if self.faq_agent and any(k in question for k in self.faq_agent.FAQS):
                result = self.faq_agent.answer(question)
                result["history_id"] = history_id
                result["model_used"] = model
                result["type"] = "chat"  # FAQ 默认为 chat 类型
                return result

            # 根据类型调用相应的agent
            if question_type == "write":
                if self.contract_agent:
                    result = self.contract_agent.answer(question)
                    result["history_id"] = history_id
                    result["model_used"] = model
                    result["type"] = "write"
                    return result
                else:
                    return {
                        "answer": "抱歉，合同生成功能暂时不可用，请稍后再试。",
                        "reference": "系统错误",
                        "type": "write",
                        "history_id": history_id,
                        "model_used": model
                    }
            else:
                # chat 类型调用 law_agent
                if self.law_agent:
                    result = self.law_agent.answer(question, model=model)
                    result["history_id"] = history_id
                    result["model_used"] = model
                    result["type"] = "chat"
                    return result
                else:
                    return {
                        "answer": "抱歉，法律咨询功能暂时不可用，请稍后再试。",
                        "reference": "系统错误",
                        "type": "chat",
                        "history_id": history_id,
                        "model_used": model
                    }
                    
        except Exception as e:
            logger.error(f"route_question 出现异常: {str(e)}", exc_info=True)
            return {
                "answer": f"抱歉，处理您的问题时出现系统错误: {str(e)}",
                "reference": "系统错误",
                "type": "chat",
                "history_id": history_id,
                "model_used": model
            }
