import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import pickle
import os
from typing import List, Dict, Any, Tuple

class LawFAISSSearcher:
    def __init__(self, index_dir: str, model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2'):
        """
        初始化FAISS搜索器
        
        Args:
            index_dir: 索引文件目录
            model_name: 文本编码模型名称
        """
        self.index_dir = index_dir
        self.model_name = model_name
        self.model = None
        self.index = None
        self.texts = None
        self.metadata = None
        self.config = None
        
        self._load_all()
    
    def _load_all(self):
        """加载所有必要的文件"""
        # 加载配置
        config_path = os.path.join(self.index_dir, 'index_config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        
        # 加载模型
        print(f"正在加载模型: {self.model_name}", flush=True)
        self.model = SentenceTransformer(self.model_name)
        
        # 加载FAISS索引
        index_path = os.path.join(self.index_dir, 'law_faiss_index.bin')
        if os.path.exists(index_path):
            print("正在加载FAISS索引...", flush=True)
            self.index = faiss.read_index(index_path)
            print(f"索引加载完成，包含 {self.index.ntotal} 个向量", flush=True)
        else:
            raise FileNotFoundError(f"索引文件不存在: {index_path}")
        
        # 加载文本数据
        texts_path = os.path.join(self.index_dir, 'law_texts.pkl')
        if os.path.exists(texts_path):
            with open(texts_path, 'rb') as f:
                self.texts = pickle.load(f)
            print(f"文本数据加载完成，共 {len(self.texts)} 条", flush=True)
        else:
            raise FileNotFoundError(f"文本文件不存在: {texts_path}")
        
        # 加载元数据
        metadata_path = os.path.join(self.index_dir, 'law_metadata.pkl')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            print(f"元数据加载完成，共 {len(self.metadata)} 条", flush=True)
        else:
            raise FileNotFoundError(f"元数据文件不存在: {metadata_path}")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        搜索最相关的法条
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            搜索结果列表
        """
        try:
            # 对查询文本进行编码
            query_embedding = self.model.encode([query])
            faiss.normalize_L2(query_embedding)
            
            # 执行搜索
            scores, indices = self.index.search(query_embedding, top_k)
            
            # 构建结果
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx != -1:  # 有效索引
                    try:
                        result = {
                            'rank': i + 1,
                            'score': float(score),
                            'article_no': self.metadata[idx]['article_no'],
                            'article_content': self.metadata[idx]['article_content'],
                            'chapter_title': self.metadata[idx]['chapter_title'],
                            'part_title': self.metadata[idx]['part_title'],
                            'file_title': self.metadata[idx].get('file_title', ''),
                            'subpart_title': self.metadata[idx].get('subpart_title', ''),
                            'full_text': self.texts[idx]
                        }
                        results.append(result)
                    except (IndexError, KeyError) as e:
                        print(f"处理搜索结果时出错，索引 {idx}: {str(e)}", flush=True)
                        continue
            
            return results
            
        except Exception as e:
            print(f"搜索过程中出现错误: {str(e)}", flush=True)
            # 返回空结果而不是抛出异常
            return []
    
    def pretty_print_results(self, results: List[Dict[str, Any]]):
        """
        美化打印搜索结果
        
        Args:
            results: 搜索结果列表
        """
        print("\n" + "="*80, flush=True)
        print("搜索结果", flush=True)
        print("="*80, flush=True)
        
        for result in results:
            print(f"\n【排名 {result['rank']}】 相似度: {result['score']:.4f}", flush=True)
            print(f"法律: {result.get('file_title', '未知法律')}", flush=True)
            print(f"编章: {result['part_title']} - {result['chapter_title']}", flush=True)
            print(f"条文: {result['article_no']}", flush=True)
            print(f"内容: {result['article_content']}", flush=True)
            print("-" * 80, flush=True)
    
    def batch_search(self, queries: List[str], top_k: int = 5) -> List[List[Dict[str, Any]]]:
        """
        批量搜索
        
        Args:
            queries: 查询文本列表
            top_k: 每个查询返回的结果数量
            
        Returns:
            每个查询的搜索结果列表
        """
        all_results = []
        for query in queries:
            results = self.search(query, top_k)
            all_results.append(results)
        
        return all_results
    
    def get_index_info(self) -> Dict[str, Any]:
        """
        获取索引信息
        
        Returns:
            索引信息字典
        """
        info = {
            'total_vectors': self.index.ntotal if self.index else 0,
            'dimension': self.index.d if self.index else 0,
            'total_texts': len(self.texts) if self.texts else 0,
            'total_metadata': len(self.metadata) if self.metadata else 0,
            'model_name': self.model_name,
            'config': self.config
        }
        return info

def main():
    """示例用法"""
    index_dir = r"e:\WorkBench\VSCode\Law_LLM\Law_LLM\RAG\indexes"
    
    try:
        # 初始化搜索器
        searcher = LawFAISSSearcher(index_dir)
        
        # 显示索引信息
        info = searcher.get_index_info()
        print(f"索引信息: {info}", flush=True)
        
        # 示例查询
        test_queries = [
            "合同纠纷",
            "婚姻家庭",
            "财产继承",
            "侵权责任"
        ]
        
        for query in test_queries:
            print(f"\n查询: {query}", flush=True)
            results = searcher.search(query, top_k=3)
            searcher.pretty_print_results(results)
            
    except FileNotFoundError as e:
        print(f"错误: {e}", flush=True)
        print("请先运行 build_faiss_index.py 构建索引", flush=True)

if __name__ == "__main__":
    main()
