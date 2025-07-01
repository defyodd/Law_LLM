import json

def analyze_chapters():
    """分析有内容的章节标题"""
    
    input_file = r"e:\WorkBench\VSCode\Law_LLM\Law_LLM\crawled data\civil_code_clean.json"
    
    with open(input_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    chapters_with_content = []
    for i, chapter in enumerate(original_data["chapters"]):
        if chapter["articles"]:
            chapters_with_content.append((i, chapter["chapter_title"], len(chapter["articles"])))
    
    print("有内容的章节:")
    for i, (idx, title, article_count) in enumerate(chapters_with_content):
        print(f"{i+1:2d}. {title} - {article_count}条")
    
    # 输出到文件以防截断
    with open("chapter_analysis.txt", "w", encoding="utf-8") as f:
        f.write("有内容的章节:\n")
        for i, (idx, title, article_count) in enumerate(chapters_with_content):
            f.write(f"{i+1:2d}. (原索引{idx:2d}) {title} - {article_count}条\n")
    
    print(f"\n详细信息已保存到 chapter_analysis.txt")
    print(f"总共有 {len(chapters_with_content)} 个有内容的章节")

if __name__ == "__main__":
    analyze_chapters()
