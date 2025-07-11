import os
import re
import datetime
from typing import List, Dict, Any

from openai import OpenAI

from search_faiss_index import LawFAISSSearcher
from build_index import LawFAISSIndexBuilder
from langchain.memory import ConversationBufferMemory
import logging
import sys, io

# 用 UTF-8 包装标准输入输出
sys.stdin  = io.TextIOWrapper(sys.stdin.buffer,  encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class LawAgent:
    """智能法律助手Agent"""
    def __init__(self, index_dir: str = "./indexes"):
        """
        初始化法律Agent
        """
        self.index_dir = index_dir
        self.searcher = None
        self.conversation_history = []
        self.memory = ConversationBufferMemory(return_messages=True)
        self._initialize_index()
        self._initialize_llm()

    def _initialize_index(self):
        """初始化或构建FAISS索引"""
        try:
            if self._check_index():
                print("🤖 法律助手正在启动，加载知识库...")
                self.searcher = LawFAISSSearcher(self.index_dir)
                print("✅ 知识库加载完毕")
            else:
                self._build_index()
        except Exception as e:
            print(f"❌ 索引初始化失败: {e}")
            raise

    def _check_index(self) -> bool:
        """检查索引是否存在"""
        return os.path.exists(os.path.join(self.index_dir, 'law_faiss_index.bin'))

    def _build_index(self):
        """从JSON文件构建FAISS索引"""
        print("🔨 正在构建法律知识库...")
        # json_file = r"e:/WorkBench/VSCode/Law_LLM/Law_LLM/crawled data/中华人民共和国民法典-北大法宝V6官网(1).json"
        json_dir = r"E:\Law_LLM-main\crawled data\cleaned_data"
        builder = LawFAISSIndexBuilder()
        builder.build_index_from_json_dir(json_dir, self.index_dir)
        self.searcher = LawFAISSSearcher(self.index_dir)
        print("✅ 知识库构建完成")

    def _initialize_llm(self):
        api_key = 'sk-de88dee6506d49c59ccaecb8abd91045'
        if not api_key:
            raise ValueError("1")
        self.llm = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        print("🤖 DeepSeek 模型已配置")

    def _extract_keywords(self, query: str) -> List[str]:
        """从查询中提取常见法律关键词"""
        legal_keywords = [
            '合同', '违约', '赔偿', '责任', '权利', '义务', '婚姻', '离婚',
            '继承', '财产', '侵权', '损害', '物权', '债权', '担保', '抵押',
            '租赁', '买卖', '借贷', '劳动', '工伤', '保险', '诉讼', '仲裁'
        ]
        return [kw for kw in legal_keywords if kw in query]

    def _analyze_query_type(self, query: str) -> str:
        """分析查询类型"""
        if any(w in query for w in ['什么', '如何', '怎么', '怎样']):
            return "定义咨询"
        if any(w in query for w in ['能否', '可以', '是否', '能不能']):
            return "可行性咨询"
        if any(w in query for w in ['责任', '赔偿', '处罚', '后果']):
            return "责任咨询"
        if any(w in query for w in ['流程', '程序', '步骤', '手续']):
            return "程序咨询"
        return "一般咨询"
    def _self_evaluate(self, answer, question):
        eval_prompt = f"问题：{question}\n答案：{answer}\n回答是否充分明确？不充分则返回'重试'，否则'通过'。"
        resp = self.llm.chat.completions.create(model="deepseek-chat", messages=[{"role": "system", "content": "你是评估员。"}, {"role": "user", "content": eval_prompt}])
        return resp.choices[0].message.content.strip()

    def _check_clarity(self, question):
        prompt = f"问题：'{question}' 是否足够清晰回答？若模糊请指出需补充的信息，否则返回'清晰'。"
        resp = self.llm.chat.completions.create(model="deepseek-chat", messages=[{"role": "user", "content": prompt}])

        return resp.choices[0].message.content.strip()

    def answer(self, question: str, max_results: int = 5, model: str = "deepseek-chat") -> Dict[str, Any]:
        query_type = self._analyze_query_type(question)
        keywords = self._extract_keywords(question)
        results = self.searcher.search(question, top_k=max_results)
        answer_text = self._generate_answer(question, results, query_type, model)
        eval_result = self._self_evaluate(answer_text, question)
        if eval_result == '重试':
            answer_text += "\n\n（注意：答案可能不完全明确，建议咨询专业律师。）"

        response = {
            'question': question,
            'query_type': query_type,
            'keywords': keywords,
            'answer': answer_text,
            'relevant_articles': results,
            'confidence': self._calculate_confidence(results),
            'suggestions': self._generate_suggestions(results, query_type),
            'agent': 'LawAgent',
            'type': 'chat'  # 添加类型标识
        }

        self.memory.save_context({"input": question}, {"output": answer_text})
        self.conversation_history.append({
            'question': question,
            'response': response,
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        return response

    def _generate_answer(self, question: str, results: List[Dict], query_type: str,
                         model: str = "deepseek-chat") -> str:
        # 构建检索到的法条内容
        context = ""
        if results:
            context = "\n".join([
                f"【{art['article_no']}】{art['content']}"
                for art in results[:3]
            ])

        # 系统提示词
        system_msg = """你是一位专业的法律助手，具备深厚的法律知识。请基于提供的法条内容回答用户的法律问题。

    回答要求：
    1. 准确引用相关法条
    2. 语言通俗易懂，避免过于专业的术语
    3. 结合具体情况给出实用建议
    4. 如果法条不足以完全回答问题，请诚实说明
    5. 提醒用户在具体案件中咨询专业律师"""

        # 用户消息
        user_msg = f"""用户问题：{question}

    查询类型：{query_type}

    相关法条：
    {context if context else "未找到直接相关的法条"}

    请基于上述法条内容，为用户提供准确、实用的法律解答。"""

        # 调用LLM生成回答
        resp = self.llm.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            stream=False,
        )
        return resp.choices[0].message.content

    def _calculate_confidence(self, results: List[Dict]) -> float:
        """基于最高相似度评分估算置信度"""
        if not results:
            return 0.0
        score = results[0]['score']
        if score > 0.8: return 0.9
        if score > 0.6: return 0.7
        if score > 0.4: return 0.5
        return 0.3

    def _generate_suggestions(self, results: List[Dict], query_type: str) -> List[str]:
        """根据置信度和类型生成建议"""
        if not results:
            return ["建议重新描述问题或使用更具体的法律术语"]
        conf = self._calculate_confidence(results)
        sugg = []
        if conf >= 0.8:
            sugg.append("找到了高度相关的法条，建议仔细阅读")
        elif conf >= 0.6:
            sugg.append("找到了相关的法条，建议结合具体情况分析")
        else:
            sugg.append("相关度一般，建议咨询专业律师")
        if query_type == "程序咨询":
            sugg.append("对于具体程序问题，建议咨询当地相关部门")
        if query_type == "责任咨询":
            sugg.append("具体责任认定需要结合实际案件情况")
        return sugg

    def print_answer(self, rsp: Dict[str, Any]):
        """格式化打印回答"""
        print("\n" + "="*60)
        print("🤖 法律助手回答")
        print("="*60)
        print(f"❓ 问题类型：{rsp['query_type']}")
        if rsp['keywords']:
            print(f"🔑 关键词：{', '.join(rsp['keywords'])}")
        print("📝 回答：")
        print(rsp['answer'])
        print(f"\n📊 置信度：{rsp['confidence']:.1%}")
        if rsp['suggestions']:
            print("\n💡 建议：")
            for i, s in enumerate(rsp['suggestions'], 1):
                print(f"   {i}. {s}")
        print("\n📚 参考法条：")
        for i, art in enumerate(rsp['relevant_articles'][:3], 1):
            print(f"   {i}. {art['article_no']} (相关度: {art['score']:.3f})")


def interactive_agent():
    """交互式Agent测试"""
    print("🤖 智能法律助手 Agent 启动")
    print("="*50)
    print("💡 我可以帮您：")
    print("   • 查找相关法律条文")
    print("   • 解答法律问题")
    print("   • 提供法律建议")
    print("\n输入 'quit' 退出，'help' 查看示例")

    agent = LawAgent()
    while True:
        try:
            print("\n" + "-"*50)
            question = input("🗣️  请描述您的法律问题：").strip()
            if question.lower() in ['quit', 'exit', '退出']:
                print("👋 感谢咨询，再见！")
                break
            if question.lower() == 'help':
                examples = [
                    "合同违约怎么办？",
                    "离婚财产如何分割？",
                    "房屋买卖合同有什么要求？",
                    "交通事故责任如何认定？",
                    "劳动合同可以随时解除吗？"
                ]
                print("\n📝 示例问题：")
                for ex in examples:
                    print(f"   • {ex}")
                continue
            if not question:
                print("请输入有效问题")
                continue
            rsp = agent.answer(question)
            if rsp.get('status') == 'clarify':
                print(f"❗ 请补充信息：{rsp['message']}")
            else:
                agent.print_answer(rsp)
            agent.print_answer(rsp)
        except KeyboardInterrupt:
            print("\n👋 助手已关闭")
            break
        except Exception as e:
            print(f"❌ 系统错误：{e}")

# if __name__ == "__main__":
#     interactive_agent()
