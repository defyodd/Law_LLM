from bs4 import BeautifulSoup
import re
import time

def parse_law_articles(html):
    soup = BeautifulSoup(html, 'html.parser')
    title_tag = soup.find('title')
    law_title = title_tag.text.strip().split('-')[0] if title_tag else "未知法律"
    if "系统安全" in law_title or "安全提示" in law_title:
        law_title = "网页加载失败_" + time.strftime("%Y%m%d%H%M%S")
    result = {
        "title": law_title,
        "parts": []
    }

    current_part = None
    current_subpart = None
    current_chapter = None

    all_elements = soup.find_all(['p', 'span', 'div'])

    for elem in all_elements:
        text = elem.get_text(strip=True)

        # 编
        if elem.name == 'p' and 'navbian' in elem.get('class', []):
            if re.match(r'^第[一二三四五六七八九十百零〇]+编', text):
                current_part = {
                    "part_title": text,
                    "subparts": [],
                    "chapters": []
                }
                result["parts"].append(current_part)
                current_subpart = None
                current_chapter = None
            elif re.match(r'^第[一二三四五六七八九十百零〇]+分编', text):
                if current_part is None:
                    current_part = {
                        "part_title": "未知编",
                        "subparts": [],
                        "chapters": []
                    }
                    result["parts"].append(current_part)
                current_subpart = {
                    "subpart_title": text,
                    "chapters": []
                }
                current_part["subparts"].append(current_subpart)
                current_chapter = None

        # 章
        elif elem.name == 'p' and 'navzhang' in elem.get('class', []):
            current_chapter = {
                "chapter_title": text,
                "articles": []
            }
            if current_subpart:
                current_subpart["chapters"].append(current_chapter)
            elif current_part:
                current_part["chapters"].append(current_chapter)
            else:
                if not result["parts"]:
                    current_part = {
                        "part_title": [],
                        "subparts": [],
                        "chapters": []
                    }
                    result["parts"].append(current_part)
                current_part["chapters"].append(current_chapter)

        # 条
        elif elem.name == 'span' and 'navtiao' in elem.get('class', []):
            article_no = text.replace('\u3000', '').replace('\xa0', '')
            tiao_wrap = elem.find_parent("div", class_="tiao-wrap")
            if not tiao_wrap:
                continue

            content_lines = []

            for kuan in tiao_wrap.find_all("div", class_="kuan-wrap"):
                kuan_content = kuan.find("div", class_="kuan-content")
                if kuan_content:
                    kuan_text = kuan_content.get_text(strip=True)
                    if article_no in kuan_text:
                        kuan_text = kuan_text.replace(article_no, '', 1).strip()
                    if kuan_text:
                        content_lines.append(kuan_text)

                for xiang in kuan.find_all("div", class_="xiang-content"):
                    xiang_text = xiang.get_text(strip=True)
                    if xiang_text:
                        content_lines.append(xiang_text)

            # 兜底：若没有 kuan-wrap，也尝试读取 tiao-wrap 的直接文本
            if not content_lines:
                tiao_text = tiao_wrap.get_text(strip=True).replace(article_no, '', 1).strip()
                if tiao_text:
                    content_lines.append(tiao_text)
            article_obj = {
                "article_no": article_no,
                "article_content": '\n'.join(content_lines).strip()
            }

            if current_chapter:
                current_chapter["articles"].append(article_obj)
            else:
                if not result["parts"]:
                    current_part = {
                        "part_title": [],
                        "subparts": [],
                        "chapters": []
                    }
                    result["parts"].append(current_part)
                if not current_part["chapters"]:
                    current_chapter = {
                        "chapter_title": [],
                        "articles": []
                    }
                    current_part["chapters"].append(current_chapter)
                current_chapter["articles"].append(article_obj)

    return result

