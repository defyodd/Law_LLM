import json

def create_final_restructured_civil_code():
    """
    创建最终的重构版本，只包含有实际条文内容的部分
    """
    
    input_file = r"D:\Law_LLM\crawled data\civil\civil_code_clean.json"
    output_file = r"D:\Law_LLM\crawled data\civil\civil_code_final_restructured.json"
    
    with open(input_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    # 提取有内容的章节
    chapters_with_content = []
    for part in original_data["parts"]:
        for chapter in part["chapters"]:
            if chapter["articles"]:
                chapters_with_content.append(chapter)
    
    print(f"找到有内容的章节数: {len(chapters_with_content)}")
    
    restructured_data = {
        "title": "中华人民共和国民法典",
        "note": "本文件只包含有具体条文内容的编。后续编（人格权、婚姻家庭、继承、侵权责任）的条文内容在原文件中为空。",
        "parts": []
    }
    
    # 第一编：总则 (前8章，缺少第四章非法人组织、第十章期间计算)
    part1_chapters = []
    part1_titles = ["基本规定", "自然人", "法人", "民事权利", "民事法律行为", "代理", "民事责任", "诉讼时效"]
    
    for chapter in chapters_with_content:
        title = chapter["chapter_title"]
        if any(keyword in title for keyword in part1_titles):
            part1_chapters.append(chapter)
    
    # 第二编：物权 (从"物权的设立"开始到"占有"结束)
    part2_chapters = []
    part2_keywords = ["物权", "所有权", "建筑物", "相邻", "共有", "土地承包", "建设用地", "宅基地", "居住权", "地役权", "抵押权", "质权", "留置权", "占有"]
    
    for chapter in chapters_with_content:
        title = chapter["chapter_title"]
        if any(keyword in title for keyword in part2_keywords) and chapter not in part1_chapters:
            part2_chapters.append(chapter)
    
    # 第三编：合同 (剩余的章节)
    part3_chapters = []
    for chapter in chapters_with_content:
        if chapter not in part1_chapters and chapter not in part2_chapters:
            part3_chapters.append(chapter)
    
    # 添加各编
    restructured_data["parts"].append({
        "part_title": "第一编　总则",
        "chapters": part1_chapters
    })
    
    restructured_data["parts"].append({
        "part_title": "第二编　物权", 
        "chapters": part2_chapters
    })
    
    restructured_data["parts"].append({
        "part_title": "第三编　合同",
        "chapters": part3_chapters
    })
    
    # 添加空的编（仅结构，无条文）
    empty_parts = [
        ("第四编　人格权", ["一般规定", "生命权、身体权和健康权", "姓名权和名称权", "肖像权", "名誉权和荣誉权", "隐私权和个人信息保护"]),
        ("第五编　婚姻家庭", ["一般规定", "结婚", "家庭关系", "离婚", "收养"]),
        ("第六编　继承", ["一般规定", "法定继承", "遗嘱继承和遗赠", "遗产的处理"]),
        ("第七编　侵权责任", ["一般规定", "损害赔偿", "责任主体的特殊规定", "产品责任", "机动车交通事故责任", "医疗损害责任", "环境污染和生态破坏责任", "高度危险责任", "饲养动物损害责任", "建筑物和物件损害责任"])
    ]
    
    for part_title, chapter_titles in empty_parts:
        chapters = []
        for i, chapter_title in enumerate(chapter_titles, 1):
            chapters.append({
                "chapter_title": f"第{['一', '二', '三', '四', '五', '六', '七', '八', '九', '十'][i-1]}章　{chapter_title}",
                "articles": [],
                "note": "本章条文内容在原文件中为空"
            })
        
        restructured_data["parts"].append({
            "part_title": part_title,
            "chapters": chapters,
            "note": "本编条文内容在原文件中为空，仅保留结构"
        })
    
    # 保存结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(restructured_data, f, ensure_ascii=False, indent=2)
    
    # 统计信息
    print(f"\n重构完成！新文件：{output_file}")
    print(f"\n统计信息:")
    print(f"总编数: {len(restructured_data['parts'])}")
    
    total_chapters_with_content = 0
    total_articles = 0
    
    for part in restructured_data["parts"]:
        chapter_count = len(part["chapters"])
        article_count = sum(len(chapter["articles"]) for chapter in part["chapters"])
        total_chapters_with_content += len([ch for ch in part["chapters"] if ch["articles"]])
        total_articles += article_count
        
        content_status = "有内容" if article_count > 0 else "结构框架"
        print(f"{part['part_title']}: {chapter_count}章, {article_count}条 ({content_status})")
    
    print(f"\n有内容的章节总数: {total_chapters_with_content}")
    print(f"条文总数: {total_articles}")

if __name__ == "__main__":
    create_final_restructured_civil_code()
