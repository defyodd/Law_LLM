# 法律条文爬虫使用说明

## 项目简介
本项目是一个基于Selenium的法律条文爬虫，主要用于从北大法宝网站爬取法律条文数据。爬虫使用Edge浏览器的调试接口，能够绕过一些反爬虫机制。

## 环境要求
- Python 3.7+
- Microsoft Edge浏览器
- Selenium WebDriver

## 依赖安装
```bash
pip install selenium
```

## 使用步骤

### 1. 准备Edge驱动器
- 下载与您系统架构和Edge浏览器版本匹配的Edge WebDriver
- 将`msedgedriver.exe`放在项目目录下（已包含在项目中）

### 2. 启动Edge浏览器调试模式
**重要：** 在运行爬虫之前，必须先关闭所有已打开的Edge浏览器实例。

在PowerShell中运行以下命令：
```powershell
start msedge.exe --remote-debugging-port=9222 --user-data-dir="C:\edge_data"
```

这将启动Edge浏览器的调试模式，并创建一个专用的用户数据目录。

### 3. 登录北大法宝
在打开的Edge浏览器中：
1. 访问北大法宝网站
2. 完成登录（如果需要）
3. 保持浏览器开启状态

### 4. 运行爬虫
```bash
python law_text_crawler.py
```

## 代码结构说明

### 主要功能
- **浏览器复用**：使用`debuggerAddress`参数接管已打开的Edge浏览器
- **智能等待**：使用`WebDriverWait`等待页面元素加载完成
- **数据提取**：定位并提取页面中的法律条文内容
- **数据保存**：将爬取的数据保存为JSON格式文件

### 核心代码解析
```python
# 配置Edge复用选项
options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

# 等待页面元素加载
wait = WebDriverWait(driver, 20)
content = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "content")))
```

## 自定义爬取

### 修改目标网址
要爬取不同的法律条文页面，只需修改`law_text_crawler.py`中的`url`变量：

```python
# 示例：爬取刑法条文
url = "https://www.pkulaw.com/chl/其他法律条文URL"
```

### 修改输出文件名
相应地修改保存的JSON文件名：
```python
with open("law_criminal.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
```

## 输出格式
爬取的数据将保存为JSON格式，包含以下字段：
- `链接`：爬取的网页URL
- `正文`：提取的法律条文内容

示例输出：
```json
{
  "链接": "https://www.pkulaw.com/chl/...",
  "正文": "第一条 为了保护民事主体的合法权益..."
}
```

## 注意事项
1. **浏览器状态**：确保在运行爬虫前Edge浏览器处于调试模式
2. **网络连接**：确保网络连接稳定，避免爬取过程中断
3. **法律合规**：请遵守网站的robots.txt协议和使用条款
4. **频率控制**：建议在爬取间隔中添加适当的延时，避免对服务器造成过大压力

## 故障排除

### 常见问题
1. **连接失败**：检查Edge浏览器是否正确启动调试模式
2. **元素定位失败**：检查目标网页结构是否发生变化
3. **编码问题**：确保使用UTF-8编码保存文件

### 错误处理
代码中包含了基本的异常处理机制，如果爬取失败，会在JSON文件中记录错误信息。

## 扩展功能建议
- 添加多线程支持以提高爬取效率
- 实现自动重试机制
- 添加数据验证和清洗功能
- 支持批量URL爬取
