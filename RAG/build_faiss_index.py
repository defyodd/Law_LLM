import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import pickle
import os
from typing import List, Dict, Any

class LawFAISSIndexBuilder:
    def __init__(self, model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2'):
        """
        初始化FAISS索引构建器
        
        Args:
            model_name: 用于文本编码的模型名称
        """
        print(f"正在加载模型: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.texts = []
        self.metadata = []
        
    def load_json_data(self, json_file_path: str) -> List[Dict[str, Any]]:
        """
        加载并解析JSON数据
        
        Args:
            json_file_path: JSON文件路径
            
        Returns:
            处理后的文本数据列表
        """
        print(f"正在加载JSON文件: {json_file_path}")
        
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        processed_data = []
        
        # 遍历所有编（parts）
        for part in data.get('parts', []):
            part_title = part.get('part_title', '')
            
            # 遍历所有章（chapters）
            for chapter in part.get('chapters', []):
                chapter_title = chapter.get('chapter_title', '')
                
                # 遍历所有条文（articles）
                for article in chapter.get('articles', []):
                    article_no = article.get('article_no', '')
                    article_content = article.get('article_content', '')
                    
                    # 构建完整的文本内容
                    full_text = f"{part_title} {chapter_title} {article_no} {article_content}"
                    
                    processed_data.append({
                        'text': full_text,
                        'article_content': article_content,
                        'article_no': article_no,
                        'chapter_title': chapter_title,
                        'part_title': part_title
                    })
        
        print(f"共处理了 {len(processed_data)} 个条文")
        return processed_data
    
    def build_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        为文本列表构建嵌入向量
        
        Args:
            texts: 文本列表
            
        Returns:
            嵌入向量数组
        """
        print("正在构建文本嵌入向量...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings
    
    def build_faiss_index(self, embeddings: np.ndarray) -> faiss.IndexFlatIP:
        """
        构建FAISS索引
        
        Args:
            embeddings: 嵌入向量数组
            
        Returns:
            FAISS索引对象
        """
        print("正在构建FAISS索引...")
        
        # 标准化向量（用于余弦相似度）
        faiss.normalize_L2(embeddings)
        
        # 创建索引 - 使用内积（对于标准化向量等同于余弦相似度）
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        
        # 添加向量到索引
        index.add(embeddings)
        
        print(f"FAISS索引构建完成，包含 {index.ntotal} 个向量")
        return index
    
    def save_index(self, index: faiss.IndexFlatIP, texts: List[str], 
                   metadata: List[Dict], save_dir: str):
        """
        保存FAISS索引和相关数据
        
        Args:
            index: FAISS索引对象
            texts: 文本列表
            metadata: 元数据列表
            save_dir: 保存目录
        """
        os.makedirs(save_dir, exist_ok=True)
        
        # 保存FAISS索引
        index_path = os.path.join(save_dir, 'law_faiss_index.bin')
        faiss.write_index(index, index_path)
        print(f"FAISS索引已保存到: {index_path}")
        
        # 保存文本数据
        texts_path = os.path.join(save_dir, 'law_texts.pkl')
        with open(texts_path, 'wb') as f:
            pickle.dump(texts, f)
        print(f"文本数据已保存到: {texts_path}")
        
        # 保存元数据
        metadata_path = os.path.join(save_dir, 'law_metadata.pkl')
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        print(f"元数据已保存到: {metadata_path}")
        
        # 保存配置信息
        config = {
            'model_name': self.model._model_name if hasattr(self.model, '_model_name') else 'unknown',
            'dimension': index.d,
            'total_vectors': index.ntotal,
            'index_type': 'IndexFlatIP'
        }
        
        config_path = os.path.join(save_dir, 'index_config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"配置信息已保存到: {config_path}")
    
    def build_index_from_json(self, json_file_path: str, save_dir: str):
        """
        从JSON文件构建完整的FAISS索引
        
        Args:
            json_file_path: JSON文件路径
            save_dir: 保存目录
        """
        # 1. 加载数据
        processed_data = self.load_json_data(json_file_path)
        
        # 2. 提取文本和元数据
        texts = [item['text'] for item in processed_data]
        metadata = [
            {
                'article_no': item['article_no'],
                'article_content': item['article_content'],
                'chapter_title': item['chapter_title'],
                'part_title': item['part_title']
            }
            for item in processed_data
        ]
        
        # 3. 构建嵌入向量
        embeddings = self.build_embeddings(texts)
        
        # 4. 构建FAISS索引
        index = self.build_faiss_index(embeddings)
        
        # 5. 保存索引和数据
        self.save_index(index, texts, metadata, save_dir)
        
        print("FAISS索引构建完成！")

def main():
    # 文件路径
    json_file_path = r"Law_LLM/crawled data/中华人民共和国民法典-北大法宝V6官网(1).json"
    save_dir = r"Law_LLM/RAG/indexes"
    
    # 构建索引
    builder = LawFAISSIndexBuilder()
    builder.build_index_from_json(json_file_path, save_dir)

if __name__ == "__main__":
    main()
