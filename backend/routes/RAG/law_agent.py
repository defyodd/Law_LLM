import os
import re
import datetime
from typing import List, Dict, Any

from openai import OpenAI

from .search_faiss_index import LawFAISSSearcher
from .build_index import LawFAISSIndexBuilder
from langchain.memory import ConversationBufferMemory
import logging
import sys, io

logger = logging.getLogger(__name__)

# 用 UTF-8 包装标准输入输出
sys.stdin  = io.TextIOWrapper(sys.stdin.buffer,  encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class LawAgent:
    """智能法律助手Agent"""
    def __init__(self, index_dir: str = "../FAISS/indexes"):
        """
        初始化法律Agent
        """
        self.index_dir = index_dir
        self.searcher = None
        self.conversation_history = []
        self.memory = ConversationBufferMemory(return_messages=True)
        self._initialize_index()
        self.llm = self._initialize_llm()

    def _initialize_index(self):
        """初始化或构建FAISS索引"""
        try:
            if self._check_index():
                print("🤖 法律助手正在启动，加载知识库...", flush=True)
                self.searcher = LawFAISSSearcher(self.index_dir)
                print("✅ 知识库加载完毕", flush=True)
            else:
                self._build_index()
        except Exception as e:
            logger.error(f"❌ 索引初始化失败: {e}")
            raise

    def _check_index(self) -> bool:
        """检查索引是否存在"""
        return os.path.exists(os.path.join(self.index_dir, 'law_faiss_index.bin'))

    def _build_index(self):
        """从JSON文件构建FAISS索引"""
        print("🔨 正在构建法律知识库...", flush=True)
        json_dir = "../../../crawled data/cleaned_data"
        builder = LawFAISSIndexBuilder()
        builder.build_index_from_json_dir(json_dir, self.index_dir)
        self.searcher = LawFAISSSearcher(self.index_dir)
        print("✅ 知识库构建完成", flush=True)

    def _initialize_llm(self):
        api_key = 'sk-de88dee6506d49c59ccaecb8abd91045'
        if not api_key:
            raise ValueError("1")
        llm = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        print("🤖 DeepSeek 模型已配置", flush=True)
        return llm

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
        try:
            eval_prompt = f"问题：{question}\n答案：{answer}\n回答是否充分明确？不充分则返回'重试'，否则'通过'。"
            resp = self.llm.chat.completions.create(
                model="deepseek-chat", 
                messages=[
                    {"role": "system", "content": "你是评估员。"}, 
                    {"role": "user", "content": eval_prompt}
                ],
                temperature=0.1,
                max_tokens=50
            )
            
            if not resp.choices or not hasattr(resp.choices[0].message, 'content'):
                return '通过'  # 如果评估失败，默认通过
            
            return resp.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"自评估失败: {str(e)}")
            return '通过'  # 如果评估失败，默认通过

    def _check_clarity(self, question):
        try:
            prompt = f"问题：'{question}' 是否足够清晰回答？若模糊请指出需补充的信息，否则返回'清晰'。"
            resp = self.llm.chat.completions.create(
                model="deepseek-chat", 
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=100
            )
            
            if not resp.choices or not hasattr(resp.choices[0].message, 'content'):
                return '清晰'  # 如果检查失败，默认清晰
            
            return resp.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"清晰度检查失败: {str(e)}")
            return '清晰'  # 如果检查失败，默认清晰

    # def answer(self, question: str, max_results: int = 5, model: str = "deepseek-chat") -> Dict[str, Any]:
    #     try:
    #         query_type = self._analyze_query_type(question)
    #         keywords = self._extract_keywords(question)
    #         results = self.searcher.search(question, top_k=max_results)
    #         answer_text = self._generate_answer(question, results, query_type, model)
    #         eval_result = self._self_evaluate(answer_text, question)
    #         if eval_result == '重试':
    #             answer_text += "\n\n（注意：答案可能不完全明确，建议咨询专业律师。）"
    #
    #         response = {
    #             'question': question,
    #             'query_type': query_type,
    #             'keywords': keywords,
    #             'answer': answer_text,
    #             'relevant_articles': results,
    #             'confidence': self._calculate_confidence(results),
    #             'suggestions': self._generate_suggestions(results, query_type),
    #             'agent': 'LawAgent',
    #             'type': 'chat'  # 添加类型标识
    #         }
    #
    #         self.memory.save_context({"input": question}, {"output": answer_text})
    #         self.conversation_history.append({
    #             'question': question,
    #             'response': response,
    #             'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #         })
    #
    #         return response
    #
    #     except Exception as e:
    #         logger.error(f"LawAgent.answer 出现异常: {str(e)}", exc_info=True)
    #         # 返回错误处理响应
    #         return {
    #             'question': question,
    #             'query_type': '错误处理',
    #             'keywords': [],
    #             'answer': f'抱歉，处理您的问题时出现错误: {str(e)}。请稍后重试或联系技术支持。',
    #             'relevant_articles': [],
    #             'confidence': 0.0,
    #             'suggestions': ['请重新提问或联系技术支持'],
    #             'agent': 'LawAgent',
    #             'type': 'chat'
    #         }
    def _is_legal_question_by_llm(self, question: str) -> bool:
        prompt = f"""请判断下面用户的问题是否属于法律相关问题，仅回答“是”或“否”，不要输出多余内容：

    用户问题：{question}
    """
        try:
            resp = self.llm.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=2
            )
            content = resp.choices[0].message.content.strip()
            return content.startswith('是')
        except Exception as e:
            logger.error(f"法律领域判定LLM调用失败: {e}")
            # 如果出错，默认走RAG流程
            return True
    def answer(self, question: str, max_results: int = 5, model: str = "deepseek-chat", context_chats: list = None) -> Dict[str, Any]:
        try:

            if not self._is_legal_question_by_llm(question):
                # 非法律问题，直接用LLM对话生成答案
                system_msg = "你是一位智能助手，请简洁准确地回答用户问题。如果你无法回答，请直接说明。"
                
                # 构建对话历史
                messages = [{"role": "system", "content": system_msg}]
                
                # 添加上下文对话记录
                if context_chats:
                    for chat in context_chats:
                        if chat.prompt and chat.answer:
                            messages.append({"role": "user", "content": chat.prompt})
                            messages.append({"role": "assistant", "content": chat.answer})
                
                # 添加当前问题
                messages.append({"role": "user", "content": question})
                
                try:
                    resp = self.llm.chat.completions.create(
                        model=model,
                        messages=messages,
                        stream=False,
                        temperature=0.7,
                        max_tokens=2000
                    )
                    answer_text = resp.choices[0].message.content.strip() if resp.choices else "抱歉，AI未能回答您的问题。"
                except Exception as e:
                    answer_text = f"抱歉，AI服务暂时不可用: {str(e)}"

                response = {
                    'question': question,
                    'query_type': '一般咨询',
                    'keywords': [],
                    'answer': answer_text,
                    'relevant_articles': [],
                    'confidence': 0.9,
                    'suggestions': [],
                    'agent': 'LawAgent',
                    'type': 'chat'
                }
                self.memory.save_context({"input": question}, {"output": answer_text})
                self.conversation_history.append({
                    'question': question,
                    'response': response,
                    'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                return response

            # ====== 下面是你原有的“法律问题”RAG流程 ======
            query_type = self._analyze_query_type(question)
            keywords = self._extract_keywords(question)
            results = self.searcher.search(question, top_k=max_results)
            answer_text = self._generate_answer(question, results, query_type, model, context_chats)
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
                'type': 'chat'
            }

            self.memory.save_context({"input": question}, {"output": answer_text})
            self.conversation_history.append({
                'question': question,
                'response': response,
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            return response

        except Exception as e:
            logger.error(f"LawAgent.answer 出现异常: {str(e)}", exc_info=True)
            # 返回错误处理响应
            return {
                'question': question,
                'query_type': '错误处理',
                'keywords': [],
                'answer': f'抱歉，处理您的问题时出现错误: {str(e)}。请稍后重试或联系技术支持。',
                'relevant_articles': [],
                'confidence': 0.0,
                'suggestions': ['请重新提问或联系技术支持'],
                'agent': 'LawAgent',
                'type': 'chat'
            }



    def _generate_answer(self, question: str, results: List[Dict], query_type: str,
                         model: str = "deepseek-chat", context_chats: list = None) -> str:
        # 构建检索到的法条内容
        context = ""
        if results:
            try:
                context = "\n".join([
                    f"【{art.get('article_no', '未知条文')}】{art.get('article_content', art.get('content', '内容缺失'))}"
                    for art in results[:3]
                ])
            except Exception as e:
                logger.error(f"构建法条内容时出错: {str(e)}")
                context = "法条内容处理失败"

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

        # 构建消息列表，优先使用数据库中的上下文记录
        messages = [{"role": "system", "content": system_msg}]
        
        # 添加数据库中的上下文对话记录
        if context_chats:
            for chat in context_chats:
                if chat.prompt and chat.answer:
                    messages.append({"role": "user", "content": chat.prompt})
                    messages.append({"role": "assistant", "content": chat.answer})
        
        # 如果没有数据库上下文，使用内存中的历史记录作为后备
        elif hasattr(self, 'memory'):
            history = self.memory.load_memory_variables({}).get("history", [])
            for h in history[-3:]:  # 只取最近3轮
                if hasattr(h, 'input') and hasattr(h, 'output'):
                    messages.append({"role": "user", "content": h.input})
                    messages.append({"role": "assistant", "content": h.output})
        
        # 添加当前问题
        messages.append({"role": "user", "content": user_msg})

        # 调用LLM生成回答
        try:
            resp = self.llm.chat.completions.create(
                model=model,
                messages=messages,
                stream=False,
                temperature=0.7,
                max_tokens=2000
            )
            
            # 检查响应格式
            if not resp.choices:
                return "抱歉，AI模型未返回有效回答，请稍后重试。"
            
            if not hasattr(resp.choices[0].message, 'content') or resp.choices[0].message.content is None:
                return "抱歉，AI模型响应格式异常，请稍后重试。"
            
            return resp.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LLM调用失败: {str(e)}")
            return f"抱歉，AI服务暂时不可用: {str(e)}"

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
        print("\n" + "="*60, flush=True)
        print("🤖 法律助手回答", flush=True)
        print("="*60, flush=True)
        print(f"❓ 问题类型：{rsp['query_type']}", flush=True)
        if rsp['keywords']:
            print(f"🔑 关键词：{', '.join(rsp['keywords'])}", flush=True)
        print("📝 回答：", flush=True)
        print(rsp['answer'], flush=True)
        print(f"\n📊 置信度：{rsp['confidence']:.1%}", flush=True)
        if rsp['suggestions']:
            print("\n💡 建议：", flush=True)
            for i, s in enumerate(rsp['suggestions'], 1):
                print(f"   {i}. {s}", flush=True)
        print("\n📚 参考法条：", flush=True)
        for i, art in enumerate(rsp['relevant_articles'][:3], 1):
            print(f"   {i}. {art['article_no']} (相关度: {art['score']:.3f})", flush=True)


def interactive_agent():
    """交互式Agent测试"""
    print("🤖 智能法律助手 Agent 启动", flush=True)
    print("="*50, flush=True)
    print("💡 我可以帮您：", flush=True)
    print("   • 查找相关法律条文", flush=True)
    print("   • 解答法律问题", flush=True)
    print("   • 提供法律建议", flush=True)
    print("\n输入 'quit' 退出，'help' 查看示例", flush=True)

    agent = LawAgent()
    while True:
        try:
            print("\n" + "-"*50, flush=True)
            question = input("🗣️  请描述您的法律问题：").strip()
            if question.lower() in ['quit', 'exit', '退出']:
                print("👋 感谢咨询，再见！", flush=True)
                break
            if question.lower() == 'help':
                examples = [
                    "合同违约怎么办？",
                    "离婚财产如何分割？",
                    "房屋买卖合同有什么要求？",
                    "交通事故责任如何认定？",
                    "劳动合同可以随时解除吗？"
                ]
                print("\n📝 示例问题：", flush=True)
                for ex in examples:
                    print(f"   • {ex}", flush=True)
                continue
            if not question:
                print("请输入有效问题", flush=True)
                continue
            rsp = agent.answer(question)
            if rsp.get('status') == 'clarify':
                print(f"❗ 请补充信息：{rsp['message']}", flush=True)
            else:
                agent.print_answer(rsp)
            agent.print_answer(rsp)
        except KeyboardInterrupt:
            print("\n👋 助手已关闭", flush=True)
            break
        except Exception as e:
            print(f"❌ 系统错误：{e}", flush=True)

# if __name__ == "__main__":
#     interactive_agent()