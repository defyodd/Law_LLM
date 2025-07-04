import os
import faiss
import pickle
import json
from sentence_transformers import SentenceTransformer
import numpy as np

def main():
    index_dir = r"D:\Python\LLM\Law_LLM\FAISS\indexes"

    # 加载索引
    print("正在加载FAISS索引...")
    index = faiss.read_index(os.path.join(index_dir, "law_faiss_index.bin"))

    # 加载文本
    with open(os.path.join(index_dir, "law_texts.pkl"), "rb") as f:
        texts = pickle.load(f)

    # 加载元数据
    with open(os.path.join(index_dir, "law_metadata.pkl"), "rb") as f:
        metadata = pickle.load(f)

    # 加载配置
    with open(os.path.join(index_dir, "index_config.json"), "r", encoding="utf-8") as f:
        config = json.load(f)

    model_name = config.get("model_name", "")
    if not model_name or model_name == "unknown":
        model_name = "paraphrase-multilingual-MiniLM-L12-v2"

    print(f"正在加载编码模型: {model_name}")
    model = SentenceTransformer(model_name)

    while True:
        query = input("\n请输入查询（回车退出）：").strip()
        if not query:
            print("退出查询。")
            break

        q_embed = model.encode([query])
        faiss.normalize_L2(q_embed)

        k = 5
        D, I = index.search(q_embed, k)

        print("\n=== 查询结果 (相似度大于0.6) ===")
        found = False
        for rank, idx in enumerate(I[0]):
            if idx == -1:
                continue
            distance = D[0][rank]
            if distance < 0.6:
                continue  # 过滤掉相似度小于 0.6 的
            found = True
            meta = metadata[idx]
            text_preview = texts[idx][:200].replace("\n", " ")
            title = f"{meta.get('file_title', '')} | {meta.get('part_title', '')} {meta.get('subpart_title', '')} {meta.get('chapter_title', '')} {meta.get('article_no', '')}"
            print(f"\nTop {rank+1}")
            print(f"标题: {title}")
            print(f"相似度: {distance:.4f}")
            print(f"内容预览: {text_preview}")
        if not found:
            print("没有结果超过0.6的相似度。")
        print("=================")

if __name__ == "__main__":
    main()
