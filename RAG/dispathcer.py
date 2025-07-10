from law_agent import LawAgent
# from contract_agent import ContractAgent
from faq_agent import FAQAgent

class AgentDispatcher:
    def __init__(self):
        self.law_agent = LawAgent()
        # self.contract_agent = ContractAgent()
        self.faq_agent = FAQAgent()

    def route_question(self, question: str) -> dict:
        if any(k in question for k in self.faq_agent.FAQS):
            return self.faq_agent.answer(question)

        # 判断是否为合同相关
        # if any(k in question for k in ["合同", "租赁", "借款", "买卖"]):
        #     return self.contract_agent.answer(question)

        # 默认交给法条问答 Agent
        return self.law_agent.answer(question)
