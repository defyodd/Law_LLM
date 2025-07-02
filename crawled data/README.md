# 法律条文爬虫项目

## 项目简介
本项目旨在从北大法宝网站爬取各类法律条文，包括民法典、刑法、治安管理处罚法等，并将其保存为JSON格式文件。

## 环境要求
- Python 3.x
- Selenium
- BeautifulSoup
- Microsoft Edge 浏览器（用于Selenium）
- msedgedriver.exe（与Edge浏览器版本匹配）

## 依赖安装
1. 安装Selenium：`pip install selenium`
2. 安装BeautifulSoup：`pip install beautifulsoup4`
3. 确保已安装Microsoft Edge浏览器，并下载对应版本的[msedgedriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)。

## 代码结构说明
- **utils.py**：包含使用Selenium抓取网页HTML的函数。
- **law_parser.py**：解析HTML中的法律条文，并将其转换为结构化数据。
- **spider.py**：主程序，负责读取URL、调用解析器并保存结果。
- **urls/**：存放各类法律条文页面的URL。
- **data/**：存放爬取并解析后的法律条文JSON文件。

## 使用步骤
1. 配置urls目录下的.txt文件，确保其中的URL正确无误。
2. 运行spider.py：`python spider.py`
3. 爬取的数据将保存在data目录下的相应子目录中。

## 数据处理流程

### 输入
- **URL文件**：位于urls目录下的.txt文件，每行包含一个法律条文页面的URL。

### 处理流程
1. **抓取网页**：使用Selenium从指定URL抓取网页HTML内容。
2. **解析HTML**：利用BeautifulSoup解析HTML，提取法律标题和条文内容。
3. **保存JSON**：将解析后的数据以JSON格式保存至data目录下的相应子目录中。

### 输出
- **data文件夹**：存放爬取并解析后的法律条文JSON文件。
- **JSON文件**：每个法律条文对应一个JSON文件，包含标题和条文内容。
- **JSON格式**：
```json
{
  "title": "中华人民共和国民法典",
  "parts": [
    {
      "part_title": "第一编　总则",
      "subparts": [],
      "chapters": [
        {
          "chapter_title": "第一章　基本规定",
          "articles": [
            {
              "article_no": "第一条",
              "article_content": "为了保护民事主体的合法权益，调整民事关系，维护社会和经济秩序，适应中国特色社会主义发展要求，弘扬社会主义核心价值观，根据宪法，制定本法。"
            }
            ]
            }   
        ]
    }
}              
```

## 注意事项
1. 确保网络连接正常，部分页面可能需要较长时间加载。
2. 如果遇到反爬机制，可以尝试调整fetch_html_with_selenium函数中的等待时间。
3. 在使用前请确认msedgedriver.exe路径是否正确。
4. 如需爬取其他法律条文，请添加相应的URL到urls目录下。