import json

def restructure_civil_code_v2():
    """
    基于实际章节内容重新组织民法典JSON文件结构
    """
    
    input_file = r"crawled data\civil_code_clean.json"
    output_file = r"crawled data\civil_code_restructured.json"
    
    with open(input_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    # 提取有内容的章节
    chapters_with_content = []
    for chapter in original_data["chapters"]:
        if chapter["articles"]:
            chapters_with_content.append(chapter)
    
    print(f"找到有内容的章节数: {len(chapters_with_content)}")
    
    # 根据分析结果手动分配章节
    restructured_data = {
        "title": "中华人民共和国民法典",
        "parts": []
    }
    
    # 第一编：总则 (索引 0-7，但缺少第四章、第十章)
    part1_chapters = chapters_with_content[0:8]  # 前8章
    restructured_data["parts"].append({
        "part_title": "第一编　总则",
        "chapters": part1_chapters
    })
    
    # 第二编：物权 (索引 8-27)
    part2_chapters = chapters_with_content[8:28]  # 第9-28章
    restructured_data["parts"].append({
        "part_title": "第二编　物权", 
        "chapters": part2_chapters
    })
    
    # 第三编：合同 (索引 28-56)
    part3_chapters = chapters_with_content[28:57]  # 第29-57章
    restructured_data["parts"].append({
        "part_title": "第三编　合同",
        "chapters": part3_chapters
    })
    
    # 第四编：人格权 - 从第58章开始查找
    # 但是从分析中看，第58章是"第一章　一般规定"，这可能是人格权编的开始
    if len(chapters_with_content) > 57:
        # 检查剩余章节
        remaining_chapters = chapters_with_content[57:]
        
        # 基于章节标题判断各编
        part4_chapters = []  # 人格权
        part5_chapters = []  # 婚姻家庭  
        part6_chapters = []  # 继承
        part7_chapters = []  # 侵权责任
        
        current_part = None
        
        for chapter in remaining_chapters:
            title = chapter["chapter_title"]
            
            # 判断编的开始
            if "生命权" in title or "身体权" in title or "健康权" in title:
                current_part = "人格权"
            elif "结婚" in title or ("家庭" in title and "关系" in title):
                current_part = "婚姻家庭"
            elif "继承" in title and ("法定" in title or "一般" in title):
                current_part = "继承"
            elif "损害赔偿" in title or ("责任" in title and "主体" in title):
                current_part = "侵权责任"
            elif "一般规定" in title and current_part is None:
                # 第一个"一般规定"可能是人格权编的开始
                current_part = "人格权"
            
            # 分配到对应的编
            if current_part == "人格权":
                part4_chapters.append(chapter)
            elif current_part == "婚姻家庭":
                part5_chapters.append(chapter)
            elif current_part == "继承":
                part6_chapters.append(chapter)
            elif current_part == "侵权责任":
                part7_chapters.append(chapter)
            else:
                # 默认分配给人格权编
                part4_chapters.append(chapter)
        
        # 添加各编
        if part4_chapters:
            restructured_data["parts"].append({
                "part_title": "第四编　人格权",
                "chapters": part4_chapters
            })
        
        if part5_chapters:
            restructured_data["parts"].append({
                "part_title": "第五编　婚姻家庭", 
                "chapters": part5_chapters
            })
        
        if part6_chapters:
            restructured_data["parts"].append({
                "part_title": "第六编　继承",
                "chapters": part6_chapters
            })
        
        if part7_chapters:
            restructured_data["parts"].append({
                "part_title": "第七编　侵权责任",
                "chapters": part7_chapters
            })
    
    # 保存结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(restructured_data, f, ensure_ascii=False, indent=2)
    
    # 统计信息
    print(f"\n重构完成！新文件：{output_file}")
    print(f"\n统计信息:")
    print(f"总编数: {len(restructured_data['parts'])}")
    
    total_chapters = 0
    total_articles = 0
    
    for part in restructured_data["parts"]:
        chapter_count = len(part["chapters"])
        article_count = sum(len(chapter["articles"]) for chapter in part["chapters"])
        total_chapters += chapter_count
        total_articles += article_count
        print(f"{part['part_title']}: {chapter_count}章, {article_count}条")
    
    print(f"\n总计: {total_chapters}章, {total_articles}条")

if __name__ == "__main__":
    restructure_civil_code_v2()
