import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import pickle
import os
from typing import List, Dict, Any


class LawFAISSIndexBuilder:
    def __init__(self, model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2'):
        print(f"正在加载模型: {model_name}")
        self.model = SentenceTransformer(model_name)

    def load_json_data(self, json_file_path: str) -> List[Dict[str, Any]]:
        """
        加载并解析一个JSON文件，支持 part/subpart/chapter/article 结构
        并包含文件级别 title
        """
        print(f"正在加载JSON文件: {json_file_path}")
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        processed_data = []
        file_title = data.get("title", "")

        for part in data.get('parts', []):
            part_title = part.get('part_title', '')

            # 处理 part 下 chapters
            for chapter in part.get('chapters', []):
                chapter_title = chapter.get('chapter_title', '')
                for article in chapter.get('articles', []):
                    article_no = article.get('article_no', '')
                    article_content = article.get('article_content', '')
                    full_text = f"{file_title} {part_title} {chapter_title} {article_no} {article_content}"
                    processed_data.append({
                        'text': full_text,
                        'article_content': article_content,
                        'article_no': article_no,
                        'chapter_title': chapter_title,
                        'part_title': part_title,
                        'subpart_title': '',
                        'file_title': file_title
                    })

            # 处理 part 下 subparts
            for subpart in part.get('subparts', []):
                subpart_title = subpart.get('subpart_title', '')
                for chapter in subpart.get('chapters', []):
                    chapter_title = chapter.get('chapter_title', '')
                    for article in chapter.get('articles', []):
                        article_no = article.get('article_no', '')
                        article_content = article.get('article_content', '')
                        full_text = f"{file_title} {part_title} {subpart_title} {chapter_title} {article_no} {article_content}"
                        processed_data.append({
                            'text': full_text,
                            'article_content': article_content,
                            'article_no': article_no,
                            'chapter_title': chapter_title,
                            'part_title': part_title,
                            'subpart_title': subpart_title,
                            'file_title': file_title
                        })

        print(f"文件 {os.path.basename(json_file_path)} 中处理了 {len(processed_data)} 条文")
        return processed_data

    def build_embeddings(self, texts: List[str]) -> np.ndarray:
        print("正在构建文本嵌入向量...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings

    def build_faiss_index(self, embeddings: np.ndarray) -> faiss.IndexFlatIP:
        print("正在构建FAISS索引...")
        faiss.normalize_L2(embeddings)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)
        print(f"FAISS索引构建完成，包含 {index.ntotal} 个向量")
        return index

    def save_index(self, index: faiss.IndexFlatIP, texts: List[str], metadata: List[Dict], save_dir: str):
        os.makedirs(save_dir, exist_ok=True)

        faiss.write_index(index, os.path.join(save_dir, 'law_faiss_index.bin'))
        with open(os.path.join(save_dir, 'law_texts.pkl'), 'wb') as f:
            pickle.dump(texts, f)
        with open(os.path.join(save_dir, 'law_metadata.pkl'), 'wb') as f:
            pickle.dump(metadata, f)
        config = {
            'model_name': self.model._model_name if hasattr(self.model, '_model_name') else 'unknown',
            'dimension': index.d,
            'total_vectors': index.ntotal,
            'index_type': 'IndexFlatIP'
        }
        with open(os.path.join(save_dir, 'index_config.json'), 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"FAISS索引及配套文件已保存到 {save_dir}")

    def build_index_from_json_dir(self, json_dir_path: str, save_dir: str):
        all_data = []
        for file in os.listdir(json_dir_path):
            if file.endswith('.json'):
                file_path = os.path.join(json_dir_path, file)
                one_data = self.load_json_data(file_path)
                all_data.extend(one_data)

        if not all_data:
            print("没有任何可索引数据，停止。")
            return

        texts = [item['text'] for item in all_data]
        metadata = [
            {
                'article_no': item['article_no'],
                'article_content': item['article_content'],
                'chapter_title': item['chapter_title'],
                'part_title': item['part_title'],
                'subpart_title': item.get('subpart_title', ''),
                'file_title': item.get('file_title', '')
            }
            for item in all_data
        ]

        embeddings = self.build_embeddings(texts)
        index = self.build_faiss_index(embeddings)
        self.save_index(index, texts, metadata, save_dir)
        print("FAISS 索引构建完成！")


def main():
    json_dir = r"D:\Python\LLM\Law_LLM\crawled data\cleaned_data"
    save_dir = r"D:\Python\LLM\Law_LLM\FAISS\indexes"
    builder = LawFAISSIndexBuilder()
    builder.build_index_from_json_dir(json_dir, save_dir)


if __name__ == "__main__":
    main()
