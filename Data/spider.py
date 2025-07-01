from selenium import webdriver
from bs4 import BeautifulSoup, NavigableString, Tag
import json
import time

# 获取渲染后的 HTML
def get_rendered_html(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('blink-settings=imagesEnabled=false')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0")

    # 创建 ChromeDriver
    try:
        driver = webdriver.Chrome(options=options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        driver.get(url)
        print("等待页面渲染...")
        time.sleep(8)
        html = driver.page_source
        return html
    except Exception as e:
        print(f"获取 HTML 失败: {e}")
        return None
    finally:
        try:
            driver.quit()
        except:
            pass

# 解析法律
def parse_law_articles(html):
    if not html:
        print("没有 HTML 内容可供解析")
        return []
    print("正在解析 HTML...")
    
    # 创建 BeautifulSoup 对象
    soup = BeautifulSoup(html, 'html.parser')

    title_tag = soup.find('title')
    law_title = title_tag.text.strip().split('_')[0] if title_tag else "未知法律"
    print(f"解析法典名称: {law_title}")

    articles = []
    # 找到所有 span.navtiao 元素
    law_tiao_spans = soup.find_all('span', class_='navtiao')
    print(f"找到 {len(law_tiao_spans)} 个 span.navtiao 元素")

    # 遍历 span.navtiao 元素
    for i, span in enumerate(law_tiao_spans):
        number = span.get_text(strip=True).replace('　', '')

        # 向上寻找 tiao-wrap 容器
        tiao_wrap = span.find_parent("div", class_="tiao-wrap")
        if not tiao_wrap:
            continue

        full_content = ""
        kuan_wraps = tiao_wrap.find_all("div", class_="kuan-wrap")
        for kuan in kuan_wraps:
            # 获取 kuan-content 的文本
            kuan_content = kuan.find("div", class_="kuan-content")
            if kuan_content:
                full_content += kuan_content.get_text(strip=True) + "\n"

            # 获取所有 xiang-content 的文本
            xiang_contents = kuan.find_all("div", class_="xiang-content")
            for xiang in xiang_contents:
                full_content += xiang.get_text(strip=True) + "\n"

        if full_content.strip():
            articles.append({
                "law_title": law_title,
                "article_number": number,
                "article_content": full_content.strip()
            })
            print(f"[✓] {number} 内容提取成功")
        else:
            print(f"[×] {number} 内容为空，跳过")

    print(f"共提取 {len(articles)} 条法条")
    return articles

# 保存到 JSON 文件
def save_to_json(articles, filename="law_articles.json"):
    if not articles:
        print("没有法条可保存")
        return
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    print(f"成功保存 {len(articles)} 条法条到 {filename}")


if __name__ == "__main__":
    url = "https://www.pkulaw.com/chl/aa00daaeb5a4fe4ebdfb.html"
    html = get_rendered_html(url)

    if html:
        articles = parse_law_articles(html)
        save_to_json(articles)
    else:
        print("HTML 获取失败，终止")
