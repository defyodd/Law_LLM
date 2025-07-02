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

## 使用步骤
1. 配置urls目录下的.txt文件，确保其中的URL正确无误。
2. 运行spider.py：`python spider.py`
3. 爬取的数据将保存在data目录下的相应子目录中。

## 代码结构说明
- **utils.py**：包含使用Selenium抓取网页HTML的函数。
- **law_parser.py**：解析HTML中的法律条文，并将其转换为结构化数据。
- **spider.py**：主程序，负责读取URL、调用解析器并保存结果。
- **urls/**：存放各类法律条文页面的URL。
- **data/**：存放爬取并解析后的法律条文JSON文件。

## 注意事项
1. 确保网络连接正常，部分页面可能需要较长时间加载。
2. 如果遇到反爬机制，可以尝试调整fetch_html_with_selenium函数中的等待时间。
3. 在使用前请确认msedgedriver.exe路径是否正确。
4. 如需爬取其他法律条文，请添加相应的URL到urls目录下。