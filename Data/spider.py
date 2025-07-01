from selenium import webdriver
from bs4 import BeautifulSoup
import json
import time

# 模拟加载页面
def get_rendered_html(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 无头模式
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('blink-settings=imagesEnabled=false')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0")
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    try:
        driver.get(url)
        time.sleep(8)  # 等待 JS 渲染
        return driver.page_source
    finally:
        driver.quit()


# 结构化解析
def parse_law_articles(html):
    soup = BeautifulSoup(html, 'html.parser')
    title_tag = soup.find('title')
    law_title = title_tag.text.strip().split('_')[0] if title_tag else "未知法律"

    result = {
        "title": law_title,
        "parts": []
    }

    current_part = None
    current_chapter = None

    all_elements = soup.find_all(['p', 'span', 'div'])

    for elem in all_elements:
        if elem.name == 'p' and 'navbian' in elem.get('class', []):
            part_title = elem.get_text(strip=True)
            current_part = {
                "part_title": part_title,
                "chapters": []
            }
            result["parts"].append(current_part)
            current_chapter = None

        elif elem.name == 'p' and 'navzhang' in elem.get('class', []):
            chapter_title = elem.get_text(strip=True)
            current_chapter = {
                "chapter_title": chapter_title,
                "articles": []
            }
            if current_part is None:
                current_part = {
                    "part_title": "未知编",
                    "chapters": []
                }
                result["parts"].append(current_part)
            current_part["chapters"].append(current_chapter)

        elif elem.name == 'span' and 'navtiao' in elem.get('class', []):
            article_no = elem.get_text(strip=True).replace('\u3000', '').replace('\xa0', '')
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
                    content_lines.append(kuan_text)

                for xiang in kuan.find_all("div", class_="xiang-content"):
                    xiang_text = xiang.get_text(strip=True)
                    content_lines.append(xiang_text)

            next_kuan = tiao_wrap.find_next_sibling("div", class_="kuan-wrap")
            while next_kuan:
                kuan_text = next_kuan.get_text(strip=True)
                if kuan_text:
                    content_lines.append(kuan_text)
                next_kuan = next_kuan.find_next_sibling("div", class_="kuan-wrap")

            article_obj = {
                "article_no": article_no,
                "article_content": '\n'.join(content_lines).strip()
            }

            if current_chapter is None:
                current_chapter = {
                    "chapter_title": "未知章节",
                    "articles": []
                }
                if current_part is None:
                    current_part = {
                        "part_title": "未知编",
                        "chapters": []
                    }
                    result["parts"].append(current_part)
                current_part["chapters"].append(current_chapter)

            current_chapter["articles"].append(article_obj)

    return result


# 保存 JSON
def save_laws_to_json(all_laws, filename="laws_combined.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_laws, f, ensure_ascii=False, indent=2)
    print(f"所有法律数据已保存至 {filename}")


# 主程序：支持批量 URL
if __name__ == "__main__":
    urls = [
        "https://www.pkulaw.com/chl/aa00daaeb5a4fe4ebdfb.html",  # 示例：民法典
        "https://www.pkulaw.com/chl/3b70bb09d2971662bdfb.html",
        "https://www.pkulaw.com/chl/6393f2e43412bddbbdfb.html",
        "https://www.pkulaw.com/chl/7c7e81f43957c58bbdfb.html",
        "https://www.pkulaw.com/chl/6da217477d512dabbdfb.html",
        "https://www.pkulaw.com/chl/1095cd22312af2f3bdfb.html"    # 继续添加
    ]

    all_laws = []

    for url in urls:
        print(f"\n处理 URL: {url}")
        html = get_rendered_html(url)
        if html:
            structured = parse_law_articles(html)
            all_laws.append(structured)
        else:
            print("无法获取该页面内容，跳过。")

    save_laws_to_json(all_laws)


