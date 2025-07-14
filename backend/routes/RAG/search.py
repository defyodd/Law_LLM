#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
民法典RAG检索增强测试系统
"""

import search_faiss_index
from search_faiss_index import LawFAISSSearcher
import os
from build_index import LawFAISSIndexBuilder
import json
from typing import List, Dict, Any

class LawRAGSystem:
    def __init__(self, index_dir: str = None):
        """
        初始化RAG系统
        
        Args:
            index_dir: 索引文件目录
        """
        if index_dir is None:
            index_dir = os.path.join(os.path.dirname(__file__), "indexes")
        
        self.index_dir = index_dir
        self.searcher = None
        self.builder = None
        self._initialize()
    
    def _initialize(self):
        """初始化系统组件"""
        try:
            # 检查索引是否存在
            if self._check_index_exists():
                print("✅ 检测到现有索引，正在加载...", flush=True)
                self.searcher = LawFAISSSearcher(self.index_dir)
                print("✅ RAG系统初始化完成", flush=True)
            else:
                print("❌ 索引不存在，需要先构建索引", flush=True)
                self._build_index()
        except Exception as e:
            print(f"❌ 系统初始化失败: {e}", flush=True)
            raise
    
    def _check_index_exists(self) -> bool:
        """检查索引文件是否存在"""
        index_file = os.path.join(self.index_dir, 'law_faiss_index.bin')
        return os.path.exists(index_file)
    
    def _build_index(self):
        """构建索引"""
        print("🔨 开始构建索引...", flush=True)
        json_file_path = r"e:\WorkBench\VSCode\Law_LLM\Law_LLM\crawled data\中华人民共和国民法典-北大法宝V6官网(1).json"
        
        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"数据文件不存在: {json_file_path}")
        
        # 构建索引
        self.builder = LawFAISSIndexBuilder()
        self.builder.build_index_from_json(json_file_path, self.index_dir)
        
        # 重新初始化搜索器
        self.searcher = LawFAISSSearcher(self.index_dir)
        print("✅ 索引构建完成", flush=True)
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        检索相关法条
        
        Args:
            query: 用户查询
            top_k: 返回结果数量
            
        Returns:
            检索结果列表
        """
        if not self.searcher:
            raise RuntimeError("搜索器未初始化")
        
        print(f"🔍 正在检索: '{query}'", flush=True)
        results = self.searcher.search(query, top_k)
        print(f"✅ 找到 {len(results)} 个相关结果", flush=True)
        
        return results
    
    def format_context(self, results: List[Dict[str, Any]]) -> str:
        """
        将检索结果格式化为上下文文本
        
        Args:
            results: 检索结果
            
        Returns:
            格式化的上下文文本
        """
        if not results:
            return "未找到相关法条"
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context = f"""
【法条{i}】{result['article_no']}
所属章节: {result['part_title']} - {result['chapter_title']}
内容: {result['article_content']}
相关度: {result['score']:.3f}
"""
            context_parts.append(context.strip())
        
        return "\n\n".join(context_parts)
    
    def rag_search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        执行RAG检索，返回完整的响应
        
        Args:
            query: 用户查询
            top_k: 检索结果数量
            
        Returns:
            包含查询、检索结果和格式化上下文的字典
        """
        # 1. 检索相关法条
        results = self.retrieve(query, top_k)
        
        # 2. 格式化上下文
        context = self.format_context(results)
        
        # 3. 构建响应
        response = {
            'query': query,
            'retrieved_count': len(results),
            'results': results,
            'formatted_context': context,
            'suggestions': self._generate_suggestions(results)
        }
        
        return response
    
    def _generate_suggestions(self, results: List[Dict[str, Any]]) -> List[str]:
        """
        基于检索结果生成相关建议
        
        Args:
            results: 检索结果
            
        Returns:
            建议列表
        """
        if not results:
            return ["建议重新描述问题或使用更具体的关键词"]
        
        suggestions = []
        
        # 提取相关章节
        chapters = set()
        for result in results:
            chapters.add(result['chapter_title'])
        
        if len(chapters) > 1:
            suggestions.append(f"您的问题涉及多个章节: {', '.join(list(chapters)[:3])}")
        
        # 根据相关度给出建议
        if results[0]['score'] > 0.8:
            suggestions.append("找到高度相关的法条，建议重点关注第一条结果")
        elif results[0]['score'] > 0.6:
            suggestions.append("找到相关的法条，建议结合多条法条综合理解")
        else:
            suggestions.append("相关度一般，建议尝试使用更具体的关键词搜索")
        
        return suggestions

def interactive_test():
    """交互式测试函数"""
    print("🏛️ 民法典RAG检索系统测试", flush=True)
    print("=" * 50, flush=True)
    
    try:
        # 初始化RAG系统
        rag_system = LawRAGSystem()
        
        print("\n💡 使用提示:", flush=True)
        print("- 输入法律相关问题进行搜索", flush=True)
        print("- 输入 'quit' 或 'exit' 退出", flush=True)
        print("- 输入 'help' 查看示例问题", flush=True)
        
        while True:
            print("\n" + "-" * 50, flush=True)
            user_input = input("请输入您的问题: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("👋 感谢使用，再见！", flush=True)
                break
            
            if user_input.lower() == 'help':
                print("\n📝 示例问题:", flush=True)
                examples = [
                    "合同违约怎么处理",
                    "婚姻关系的法律规定",
                    "财产继承的相关法条",
                    "侵权责任的赔偿标准",
                    "物权保护的法律条文"
                ]
                for i, example in enumerate(examples, 1):
                    print(f"   {i}. {example}", flush=True)
                continue
            
            if not user_input:
                print("❌ 请输入有效问题", flush=True)
                continue
            
            try:
                # 执行RAG检索
                response = rag_system.rag_search(user_input, top_k=3)
                
                # 显示结果
                print(f"\n📊 检索结果 (共找到 {response['retrieved_count']} 条相关法条):", flush=True)
                print("=" * 60, flush=True)
                
                print(response['formatted_context'], flush=True)
                
                print("\n💡 相关建议:", flush=True)
                for suggestion in response['suggestions']:
                    print(f"   • {suggestion}", flush=True)
                
            except Exception as e:
                print(f"❌ 检索过程中出现错误: {e}", flush=True)
    
    except KeyboardInterrupt:
        print("\n\n👋 程序已中断", flush=True)
    except Exception as e:
        print(f"❌ 系统错误: {e}", flush=True)

def batch_test():
    """批量测试函数"""
    print("🧪 批量测试RAG系统", flush=True)
    
    # 测试问题
    test_queries = [
        "合同纠纷的处理方式",
        "婚姻家庭法律规定", 
        "财产继承权利",
        "侵权损害赔偿",
        "物权保护措施"
    ]
    
    try:
        rag_system = LawRAGSystem()
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'='*20} 测试 {i}/{len(test_queries)} {'='*20}", flush=True)
            response = rag_system.rag_search(query, top_k=2)
            
            print(f"问题: {query}", flush=True)
            print(f"找到相关法条: {response['retrieved_count']} 条", flush=True)
            
            if response['results']:
                best_result = response['results'][0]
                print(f"最相关法条: {best_result['article_no']}", flush=True)
                print(f"相关度: {best_result['score']:.3f}", flush=True)
                print(f"内容摘要: {best_result['article_content'][:50]}...", flush=True)
            
    except Exception as e:
        print(f"❌ 批量测试失败: {e}", flush=True)

if __name__ == "__main__":
    print("选择测试模式:", flush=True)
    print("1. 交互式测试", flush=True)
    print("2. 批量测试", flush=True)
    
    choice = input("请选择 (1/2): ").strip()
    
    if choice == "1":
        interactive_test()
    elif choice == "2":
        batch_test()
    else:
        print("默认运行交互式测试", flush=True)
        interactive_test()
