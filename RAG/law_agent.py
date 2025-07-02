#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能法律助手Agent - 基于RAG的问答系统
"""

from search_faiss_index import LawFAISSSearcher
from build_faiss_index import LawFAISSIndexBuilder
import os
import re
from typing import List, Dict, Any, Optional

class LawAgent:
    """智能法律助手Agent"""
    
    def __init__(self, index_dir: str = "./indexes"):
        """
        初始化法律Agent
        
        Args:
            index_dir: 索引文件目录
        """
        self.index_dir = index_dir
        self.searcher = None
        self.conversation_history = []
        self._initialize()
    
    def _initialize(self):
        """初始化Agent"""
        try:
            if self._check_index():
                print("🤖 法律助手正在启动...")
                self.searcher = LawFAISSSearcher(self.index_dir)
                print("✅ 法律助手已就绪")
            else:
                self._build_index()
        except Exception as e:
            print(f"❌ Agent初始化失败: {e}")
            raise
    
    def _check_index(self) -> bool:
        """检查索引是否存在"""
        return os.path.exists(os.path.join(self.index_dir, 'law_faiss_index.bin'))
    
    def _build_index(self):
        """构建索引"""
        print("🔨 正在构建法律知识库...")
        json_file = r"e:\WorkBench\VSCode\Law_LLM\Law_LLM\crawled data\中华人民共和国民法典-北大法宝V6官网(1).json"
        
        builder = LawFAISSIndexBuilder()
        builder.build_index_from_json(json_file, self.index_dir)
        
        self.searcher = LawFAISSSearcher(self.index_dir)
        print("✅ 知识库构建完成")
    
    def _extract_keywords(self, query: str) -> List[str]:
        """从查询中提取关键词"""
        # 简单的关键词提取
        keywords = []
        
        # 常见法律关键词
        legal_keywords = [
            '合同', '违约', '赔偿', '责任', '权利', '义务', '婚姻', '离婚', 
            '继承', '财产', '侵权', '损害', '物权', '债权', '担保', '抵押',
            '租赁', '买卖', '借贷', '劳动', '工伤', '保险', '诉讼', '仲裁'
        ]
        
        for keyword in legal_keywords:
            if keyword in query:
                keywords.append(keyword)
        
        return keywords
    
    def _analyze_query_type(self, query: str) -> str:
        """分析查询类型"""
        if any(word in query for word in ['什么', '如何', '怎么', '怎样']):
            return "定义咨询"
        elif any(word in query for word in ['能否', '可以', '是否', '能不能']):
            return "可行性咨询"
        elif any(word in query for word in ['责任', '赔偿', '处罚', '后果']):
            return "责任咨询"
        elif any(word in query for word in ['流程', '程序', '步骤', '手续']):
            return "程序咨询"
        else:
            return "一般咨询"
    
    def answer(self, question: str, max_results: int = 5) -> Dict[str, Any]:
        """
        回答用户问题
        
        Args:
            question: 用户问题
            max_results: 最大检索结果数
            
        Returns:
            回答结果字典
        """
        # 1. 分析问题
        query_type = self._analyze_query_type(question)
        keywords = self._extract_keywords(question)
        
        # 2. 检索相关法条
        search_results = self.searcher.search(question, top_k=max_results)
        
        # 3. 生成回答
        answer_text = self._generate_answer(question, search_results, query_type)
        
        # 4. 构建响应
        response = {
            'question': question,
            'query_type': query_type,
            'keywords': keywords,
            'answer': answer_text,
            'relevant_articles': search_results,
            'confidence': self._calculate_confidence(search_results),
            'suggestions': self._generate_suggestions(search_results, query_type)
        }
        
        # 5. 记录对话历史
        self.conversation_history.append({
            'question': question,
            'response': response,
            'timestamp': self._get_timestamp()
        })
        
        return response
    
    def _generate_answer(self, question: str, results: List[Dict], query_type: str) -> str:
        """生成回答文本"""
        if not results:
            return "抱歉，我在现有的法律条文中没有找到直接相关的内容。建议您：\n1. 尝试使用更具体的关键词\n2. 咨询专业律师获得更准确的建议"
        
        answer_parts = []
        
        # 根据查询类型生成不同的回答
        if query_type == "定义咨询":
            answer_parts.append("根据相关法律条文，")
        elif query_type == "可行性咨询":
            answer_parts.append("根据法律规定，")
        elif query_type == "责任咨询":
            answer_parts.append("关于责任问题，法律条文规定：")
        else:
            answer_parts.append("根据相关法律条文：")
        
        # 添加最相关的法条内容
        best_result = results[0]
        if best_result['score'] > 0.7:  # 高相关度
            answer_parts.append(f"\n\n📖 {best_result['article_no']}规定：\n{best_result['article_content']}")
        
        # 如果有多个相关法条
        if len(results) > 1 and results[1]['score'] > 0.6:
            answer_parts.append(f"\n\n此外，{results[1]['article_no']}也规定：\n{results[1]['article_content']}")
        
        # 添加法条出处
        answer_parts.append(f"\n\n📂 相关章节：{best_result['part_title']} > {best_result['chapter_title']}")
        
        return "".join(answer_parts)
    
    def _calculate_confidence(self, results: List[Dict]) -> float:
        """计算回答的置信度"""
        if not results:
            return 0.0
        
        # 基于最高相似度分数
        max_score = results[0]['score']
        
        if max_score > 0.8:
            return 0.9
        elif max_score > 0.6:
            return 0.7
        elif max_score > 0.4:
            return 0.5
        else:
            return 0.3
    
    def _generate_suggestions(self, results: List[Dict], query_type: str) -> List[str]:
        """生成建议"""
        suggestions = []
        
        if not results:
            suggestions.append("建议重新描述问题或使用更具体的法律术语")
            return suggestions
        
        confidence = self._calculate_confidence(results)
        
        if confidence >= 0.8:
            suggestions.append("找到了高度相关的法条，建议仔细阅读")
        elif confidence >= 0.6:
            suggestions.append("找到了相关的法条，建议结合具体情况分析")
        else:
            suggestions.append("相关度一般，建议咨询专业律师")
        
        # 根据查询类型提供建议
        if query_type == "程序咨询":
            suggestions.append("对于具体程序问题，建议咨询当地相关部门")
        elif query_type == "责任咨询":
            suggestions.append("具体责任认定需要结合实际案件情况")
        
        return suggestions
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def print_answer(self, response: Dict[str, Any]):
        """美化打印回答"""
        print("\n" + "="*60)
        print(f"🤖 法律助手回答")
        print("="*60)
        
        print(f"❓ 问题类型：{response['query_type']}")
        
        if response['keywords']:
            print(f"🔑 关键词：{', '.join(response['keywords'])}")
        
        print(f"📝 回答：")
        print(response['answer'])
        
        print(f"\n📊 置信度：{response['confidence']:.1%}")
        
        if response['suggestions']:
            print(f"\n💡 建议：")
            for i, suggestion in enumerate(response['suggestions'], 1):
                print(f"   {i}. {suggestion}")
        
        print("\n📚 参考法条：")
        for i, article in enumerate(response['relevant_articles'][:3], 1):
            print(f"   {i}. {article['article_no']} (相关度: {article['score']:.3f})")

def interactive_agent():
    """交互式Agent测试"""
    print("🤖 智能法律助手 Agent 启动")
    print("="*50)
    print("💡 我可以帮您：")
    print("   • 查找相关法律条文")
    print("   • 解答法律问题")
    print("   • 提供法律建议")
    print("\n输入 'quit' 退出，'help' 查看示例")
    
    try:
        agent = LawAgent()
        
        while True:
            print("\n" + "-"*50)
            question = input("🗣️  请描述您的法律问题：").strip()
            
            if question.lower() in ['quit', 'exit', '退出']:
                print("👋 感谢咨询，再见！")
                break
            
            if question.lower() == 'help':
                print("\n📝 示例问题：")
                examples = [
                    "合同违约怎么办？",
                    "离婚财产如何分割？",
                    "房屋买卖合同有什么要求？",
                    "交通事故责任如何认定？",
                    "劳动合同可以随时解除吗？"
                ]
                for i, ex in enumerate(examples, 1):
                    print(f"   {i}. {ex}")
                continue
            
            if not question:
                print("请输入有效问题")
                continue
            
            # 获取回答
            response = agent.answer(question)
            
            # 打印回答
            agent.print_answer(response)
    
    except KeyboardInterrupt:
        print("\n\n👋 助手已关闭")
    except Exception as e:
        print(f"❌ 系统错误：{e}")

if __name__ == "__main__":
    interactive_agent()
