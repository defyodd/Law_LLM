import os
import json
import sqlite3

DB_PATH = "FAISS/law_articles.db"
JSON_DIR = "crawled data/cleaned_data"

def create_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)  # 确保目录存在
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            law_title TEXT,
            part_title TEXT,
            subpart_title TEXT,
            chapter_title TEXT,
            article_no TEXT,
            content TEXT,
            source_file TEXT,
            vector_idx INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def insert_article(conn, article, source_file, vector_idx):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO articles (
            law_title, part_title, subpart_title, chapter_title,
            article_no, content, source_file, vector_idx
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        article.get("file_title", ""),
        article.get("part_title", ""),
        article.get("subpart_title", ""),
        article.get("chapter_title", ""),
        article.get("article_no", ""),
        article.get("article_content", ""),
        source_file,
        vector_idx
    ))
    conn.commit()

def process_json():
    conn = sqlite3.connect(DB_PATH)
    vector_idx = 0  # 与 FAISS 向量顺序同步

    for filename in os.listdir(JSON_DIR):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(JSON_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        law_title = data.get("title", "")
        for part in data.get("parts", []):
            part_title = part.get("part_title", "")
            
            # 无分编
            for chapter in part.get("chapters", []):
                chapter_title = chapter.get("chapter_title", "")
                for article in chapter.get("articles", []):
                    insert_article(conn, {
                        "file_title": law_title,
                        "part_title": part_title,
                        "subpart_title": "",
                        "chapter_title": chapter_title,
                        "article_no": article.get("article_no", ""),
                        "article_content": article.get("article_content", "")
                    }, filename, vector_idx)
                    vector_idx += 1

            # 有分编
            for subpart in part.get("subparts", []):
                subpart_title = subpart.get("subpart_title", "")
                for chapter in subpart.get("chapters", []):
                    chapter_title = chapter.get("chapter_title", "")
                    for article in chapter.get("articles", []):
                        insert_article(conn, {
                            "file_title": law_title,
                            "part_title": part_title,
                            "subpart_title": subpart_title,
                            "chapter_title": chapter_title,
                            "article_no": article.get("article_no", ""),
                            "article_content": article.get("article_content", "")
                        }, filename, vector_idx)
                        vector_idx += 1

    conn.close()
    print(f"✅ 插入完成，共计向量数：{vector_idx}")

if __name__ == "__main__":
    create_db()
    process_json()
