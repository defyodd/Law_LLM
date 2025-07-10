import os
import json
import pymysql

#  修改连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',   # ← 替换成你的密码
    'database': 'lawdb',
    'charset': 'utf8mb4'
}

JSON_DIR = r"D:\Law_LLM\crawled data\cleaned_data"

def insert_article(cursor, article, source_file, vector_idx):
    sql = """
    INSERT INTO articles (
        law_title, part_title, subpart_title, chapter_title,
        article_no, content, source_file, vector_idx
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        article.get("file_title", ""),
        article.get("part_title", ""),
        article.get("subpart_title", ""),
        article.get("chapter_title", ""),
        article.get("article_no", ""),
        article.get("article_content", ""),
        source_file,
        vector_idx
    ))

def process_json():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    vector_idx = 0

    for filename in os.listdir(JSON_DIR):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(JSON_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        law_title = data.get("title", "")
        for part in data.get("parts", []):
            part_title = part.get("part_title", "")

            for chapter in part.get("chapters", []):
                chapter_title = chapter.get("chapter_title", "")
                for article in chapter.get("articles", []):
                    insert_article(cursor, {
                        "file_title": law_title,
                        "part_title": part_title,
                        "subpart_title": "",
                        "chapter_title": chapter_title,
                        "article_no": article.get("article_no", ""),
                        "article_content": article.get("article_content", "")
                    }, filename, vector_idx)
                    vector_idx += 1

            for subpart in part.get("subparts", []):
                subpart_title = subpart.get("subpart_title", "")
                for chapter in subpart.get("chapters", []):
                    chapter_title = chapter.get("chapter_title", "")
                    for article in chapter.get("articles", []):
                        insert_article(cursor, {
                            "file_title": law_title,
                            "part_title": part_title,
                            "subpart_title": subpart_title,
                            "chapter_title": chapter_title,
                            "article_no": article.get("article_no", ""),
                            "article_content": article.get("article_content", "")
                        }, filename, vector_idx)
                        vector_idx += 1

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ 插入完成，共计向量数：{vector_idx}")

if __name__ == "__main__":
    process_json()
