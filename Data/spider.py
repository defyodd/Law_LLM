from selenium import webdriver
from bs4 import BeautifulSoup
import json
import time

def get_rendered_html(url, wait_time=8):
    """用 Selenium 加载 JS，并返回渲染后的 HTML"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('blink-settings=imagesEnabled=false')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0")

    driver = webdriver.Chrome(options=options)
    # 绕过 navigator.webdriver 检测
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    try:
        driver.get(url)
        print(f"[浏览器] 开始渲染：{url}")
        time.sleep(wait_time)
        html = driver.page_source
        print(f"[浏览器] 渲染完成，HTML 长度：{len(html)}")
        return html
    finally:
        driver.quit()

def parse_law_articles(html):
    soup = BeautifulSoup(html, 'html.parser')
    title_tag = soup.find('title')
    law_title = title_tag.text.strip().split('_')[0] if title_tag else "未知法律"

    articles = []
    spans = soup.find_all('span', class_='navtiao')
    
    for span in spans:
        article_number = span.get_text(strip=True).replace('\u3000', '').replace('\xa0', '')
        tiao_wrap = span.find_parent("div", class_="tiao-wrap")
        if not tiao_wrap:
            continue

        content_lines = []
        for kuan in tiao_wrap.find_all("div", class_="kuan-wrap"):
            kuan_content = kuan.find("div", class_="kuan-content")
            if kuan_content:
                kuan_text = kuan_content.get_text(strip=True)
                if article_number in kuan_text:
                    kuan_text = kuan_text.replace(article_number, '', 1).strip()
                content_lines.append(kuan_text)

            for xiang in kuan.find_all("div", class_="xiang-content"):
                xiang_text = xiang.get_text(strip=True)
                if xiang_text:
                    content_lines.append(xiang_text)

        article_content = '\n'.join(content_lines).strip()
        if article_content:
            articles.append({
                "law_title": law_title,
                "article_number": article_number,
                "article_content": article_content
            })

    return articles


def save_to_json(articles, filename="law_articles.json"):
    """将所有法条写入 JSON 文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    print(f"[保存] 共保存 {len(articles)} 条法条 到 {filename}")

if __name__ == "__main__":
    print("[开始] 抓取所有法律")
    urls = [
        "https://www.pkulaw.com/chl/aa00daaeb5a4fe4ebdfb.html",
        "https://www.pkulaw.com/chl/3b70bb09d2971662bdfb.html",
        "https://www.pkulaw.com/chl/6393f2e43412bddbbdfb.html",
        "https://www.pkulaw.com/chl/7c7e81f43957c58bbdfb.html",
        "https://www.pkulaw.com/chl/6da217477d512dabbdfb.html",
        "https://www.pkulaw.com/chl/1095cd22312af2f3bdfb.html"
        # 添加更多……
    ]

    all_articles = []
    for url in urls:
        html = get_rendered_html(url)
        if not html:
            print(f"[错误] 无法获取页面：{url}")
            continue
        arts = parse_law_articles(html)
        print(f"[解析] 从 {url} 提取到 {len(arts)} 条")
        all_articles.extend(arts)

    # 去重（根据 law_title+article_number）
    unique = {}
    for art in all_articles:
        key = f"{art['law_title']}|{art['article_number']}"
        unique[key] = art
    deduped_articles = list(unique.values())

    # 最终保存
    save_to_json(deduped_articles)

