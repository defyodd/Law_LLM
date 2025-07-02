#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速RAG测试 - 简化版本
"""

from search_faiss_index import LawFAISSSearcher
from build_faiss_index import LawFAISSIndexBuilder
import os

def quick_rag_test():
    """快速RAG测试"""
    print("🚀 快速RAG测试启动")
    
    # 检查索引是否存在
    index_dir = "./indexes"
    index_file = os.path.join(index_dir, 'law_faiss_index.bin')
    
    if not os.path.exists(index_file):
        print("⚠️ 索引不存在，正在构建...")
        # 构建索引
        json_file = r"e:\WorkBench\VSCode\Law_LLM\Law_LLM\crawled data\中华人民共和国民法典-北大法宝V6官网(1).json"
        builder = LawFAISSIndexBuilder()
        builder.build_index_from_json(json_file, index_dir)
        print("✅ 索引构建完成")
    
    # 初始化搜索器
    print("📚 正在加载法律知识库...")
    searcher = LawFAISSSearcher(index_dir)
    
    # 简单的查询测试
    while True:
        print("\n" + "="*50)
        user_input = input("💭 请输入您的法律问题 (输入'q'退出): ").strip()
        
        if user_input.lower() in ['q', 'quit', '退出']:
            print("👋 再见！")
            break
            
        if not user_input:
            continue
        
        print(f"\n🔍 正在搜索: {user_input}")
        
        # 执行检索
        results = searcher.search(user_input, top_k=3)
        
        if results:
            print(f"\n📋 找到 {len(results)} 个相关法条:")
            print("-" * 50)
            
            for i, result in enumerate(results, 1):
                print(f"\n【结果 {i}】相似度: {result['score']:.3f}")
                print(f"📖 {result['article_no']}")
                print(f"📂 {result['part_title']} > {result['chapter_title']}")
                print(f"📝 {result['article_content']}")
                
                if i < len(results):
                    print("-" * 30)
        else:
            print("❌ 未找到相关法条，请尝试其他关键词")

if __name__ == "__main__":
    try:
        quick_rag_test()
    except KeyboardInterrupt:
        print("\n👋 程序已中断")
    except Exception as e:
        print(f"❌ 错误: {e}")
        print("请确保已安装所需依赖: pip install faiss-cpu sentence-transformers")
