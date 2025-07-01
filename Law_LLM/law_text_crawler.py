import json
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Edge 复用配置
options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
service = Service(executable_path="msedgedriver.exe")

# 启动 Selenium 接管 Edge
driver = webdriver.Edge(service=service, options=options)
wait = WebDriverWait(driver, 20)


# 要爬取的页面（爬取的是中华名族共和国民法典）
url = "https://www.pkulaw.com/chl/aa00daaeb5a4fe4ebdfb.html?way=listView"

# 抓取逻辑
result = {"链接": url}
try:
    driver.get(url)
    content = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "content")))
    result["正文"] = content.text.strip()
except Exception as e:
    print("抓取失败:", e)
    result["正文"] = "抓取失败"

# 保存为 JSON
with open("law_single.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("✅ 成功写入 law_single.json")
