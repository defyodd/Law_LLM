#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
民法典FAISS索引使用示例
"""

from search_faiss_index import LawFAISSSearcher
from build_faiss_index import LawFAISSIndexBuilder
import os

def demo_build_index():
    """演示如何构建索引"""
    print("=== 构建FAISS索引演示 ===")
    
    # 文件路径
    json_file_path = r"e:\WorkBench\VSCode\Law_LLM\Law_LLM\crawled data\中华人民共和国民法典-北大法宝V6官网(1).json"
    save_dir = r"e:\WorkBench\VSCode\Law_LLM\Law_LLM\RAG\indexes"
    
    # 检查JSON文件是否存在
    if not os.path.exists(json_file_path):
        print(f"错误: JSON文件不存在 - {json_file_path}")
        return False
    
    # 构建索引
    try:
        builder = LawFAISSIndexBuilder()
        builder.build_index_from_json(json_file_path, save_dir)
        print("✅ 索引构建成功！")
        return True
    except Exception as e:
        print(f"❌ 索引构建失败: {e}")
        return False

def demo_search_index():
    """演示如何使用索引进行搜索"""
    print("\n=== FAISS索引搜索演示 ===")
    
    index_dir = r"e:\WorkBench\VSCode\Law_LLM\Law_LLM\RAG\indexes"
    
    # 检查索引是否存在
    if not os.path.exists(os.path.join(index_dir, 'law_faiss_index.bin')):
        print("❌ 索引文件不存在，请先运行构建索引")
        return False
    
    try:
        # 初始化搜索器
        searcher = LawFAISSSearcher(index_dir)
        
        # 显示索引信息
        info = searcher.get_index_info()
        print(f"📊 索引信息:")
        print(f"   - 总向量数: {info['total_vectors']}")
        print(f"   - 向量维度: {info['dimension']}")
        print(f"   - 使用模型: {info['model_name']}")
        
        # 测试查询
        test_queries = [
            "合同违约责任",
            "婚姻关系",
            "财产继承权",
            "侵权损害赔偿",
            "物权保护"
        ]
        
        for query in test_queries:
            print(f"\n🔍 查询: '{query}'")
            results = searcher.search(query, top_k=3)
            
            if results:
                for i, result in enumerate(results, 1):
                    print(f"   {i}. [{result['article_no']}] (相似度: {result['score']:.3f})")
                    print(f"      {result['part_title']} - {result['chapter_title']}")
                    print(f"      {result['article_content'][:100]}...")
            else:
                print("   未找到相关结果")
        
        print("\n✅ 搜索演示完成！")
        return True
        
    except Exception as e:
        print(f"❌ 搜索演示失败: {e}")
        return False

def interactive_search():
    """交互式搜索"""
    print("\n=== 交互式搜索 ===")
    print("输入查询内容，按回车搜索，输入 'quit' 退出")
    
    index_dir = r"e:\WorkBench\VSCode\Law_LLM\Law_LLM\RAG\indexes"
    
    try:
        searcher = LawFAISSSearcher(index_dir)
        
        while True:
            query = input("\n请输入查询内容: ").strip()
            
            if query.lower() in ['quit', 'exit', '退出']:
                print("👋 再见！")
                break
            
            if not query:
                continue
            
            results = searcher.search(query, top_k=5)
            searcher.pretty_print_results(results)
            
    except KeyboardInterrupt:
        print("\n👋 搜索已中断")
    except Exception as e:
        print(f"❌ 搜索错误: {e}")

def main():
    """主函数"""
    print("🏛️ 民法典FAISS索引演示程序")
    print("=" * 50)
    
    # 检查是否需要构建索引
    index_dir = r"e:\WorkBench\VSCode\Law_LLM\Law_LLM\RAG\indexes"
    index_exists = os.path.exists(os.path.join(index_dir, 'law_faiss_index.bin'))
    
    if not index_exists:
        print("🔨 检测到索引不存在，开始构建索引...")
        if not demo_build_index():
            return
    else:
        print("✅ 检测到现有索引")
    
    # 运行搜索演示
    if demo_search_index():
        # 提供交互式搜索选项
        choice = input("\n是否进入交互式搜索模式？(y/n): ").strip().lower()
        if choice in ['y', 'yes', '是']:
            interactive_search()

if __name__ == "__main__":
    main()
