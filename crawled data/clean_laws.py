import os
import json
import re

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.replace('\u3000', '').replace('\xa0', '').replace('\r', '')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def clean_article(article):
    return {
        "article_no": clean_text(article.get("article_no", "")),
        "article_content": clean_text(article.get("article_content", ""))
    }

def clean_chapters(chapters):
    cleaned_chapters = []
    for chapter in chapters:
        chapter_title = clean_text(chapter.get("chapter_title", ""))
        articles = chapter.get("articles", [])
        cleaned_articles = [clean_article(a) for a in articles if a.get("article_content", "").strip()]
        if cleaned_articles:
            cleaned_chapters.append({
                "chapter_title": chapter_title,
                "articles": cleaned_articles
            })
    return cleaned_chapters

def clean_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"[❌ JSON错误] {file_path}")
            return None

    title = data.get("title", "")
    if "加载失败" in title or "系统安全提示" in title:
        print(f"[⚠️ 错误页面] {file_path}")
        return None
    data["title"] = clean_text(title)

    cleaned_parts = []

    for part in data.get("parts", []):
        part_title = part.get("part_title", "")
        if not isinstance(part_title, str):
            part_title = "无编"
        part_title = clean_text(part_title)

        # 清洗直辖章节
        cleaned_chapters = clean_chapters(part.get("chapters", []))

        # 清洗分编及其章节
        cleaned_subparts = []
        for subpart in part.get("subparts", []):
            subpart_title = clean_text(subpart.get("subpart_title", ""))
            subpart_chapters = clean_chapters(subpart.get("chapters", []))
            if subpart_chapters:
                cleaned_subparts.append({
                    "subpart_title": subpart_title,
                    "chapters": subpart_chapters
                })

        cleaned_parts.append({
            "part_title": part_title,
            "chapters": cleaned_chapters,
            "subparts": cleaned_subparts
        })

    data["parts"] = cleaned_parts
    return data

def clean_all_jsons(data_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file_name in os.listdir(data_dir):
        if not file_name.endswith(".json"):
            continue

        file_path = os.path.join(data_dir, file_name)
        cleaned_data = clean_json_file(file_path)
        if cleaned_data is None:
            continue

        output_path = os.path.join(output_dir, file_name)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
        print(f"[✅ 清洗完成] {file_name}")

if __name__ == "__main__":
    raw_data_dir = "data"  # 原始数据路径
    cleaned_output_dir = "cleaned_data"  # 清洗输出路径
    clean_all_jsons(raw_data_dir, cleaned_output_dir)

