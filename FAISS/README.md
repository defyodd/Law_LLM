# 法律条文 FAISS 索引与检索项目

## 项目简介
本目录用于将结构化法律条文（JSON 格式）批量转换为向量，利用 FAISS 构建高效的相似度检索索引，并支持基于语义的法律条文查询。

## 环境要求
- Python 3.x
- numpy
- faiss
- sentence-transformers
- sqlite3
- argparse
- os / json

## 依赖安装
```bash
pip install numpy faiss-cpu sentence-transformers
```

## 目录结构说明及其功能
- `FAISS/build_index.py`：索引构建与保存脚本
- `FAISS/query_index.py`：命令行检索脚本
- `FAISS/from_json_to_sqlite.py`：将结构化法律JSON数据写入SQLite数据库
- `FAISS/query_sqlite.py`：从SQLite中按各种维度查询法条
- `FAISS/indexes/`：保存生成的 FAISS 索引及配套文件
  - `law_faiss_index.bin`：FAISS 索引文件
  - `law_texts.pkl`：原始文本内容列表
  - `law_metadata.pkl`：每条文本的元数据信息
  - `index_config.json`：索引配置信息
  - `crawled data/cleaned_data/`：存放结构化法律条文 JSON 文件

## 数据库设计
核心表：`articles`

| 字段名             | 类型         | 说明                 |
| ------------------ | ---------- | -------------------- |
| `id`               | INTEGER PK | 主键，自增           |
| `law_title`        | TEXT       | 法律名称（如《民法典》） |
| `part_title`       | TEXT       | 编标题（如“第一编 总则”） |
| `subpart_title`    | TEXT       | 分编标题（可为空）     |
| `chapter_title`    | TEXT       | 章标题（如“第一章 基本规定”） |
| `article_no`       | TEXT       | 条号（如“第四条”）     |
| `content`          | TEXT       | 条文正文内容           |
| `source_file`      | TEXT       | 来源 JSON 文件名      |
| `vector_idx`       | INTEGER    | 向量编号，对应 FAISS 向量索引 |

## 使用步骤

### 1. 数据爬取（请参考crawled data/README.md）
1. 配置urls目录下的.txt文件，确保其中的URL正确无误。
2. 运行spider.py：`python crawled data/spider.py`
3. 爬取的数据将保存在crawled data/data目录下。

### 2. 构建索引
1. 将待索引的法律条文 JSON 文件放入 `crawled data/data/` 目录
2. 运行：`python FAISS/build_index.py`
3. 索引和元数据将保存在 `FAISS/indexes/` 目录。

### 3. 检索条文
运行检索脚本，按提示输入查询内容：
```bash
python FAISS/query_index.py
```
返回与输入语义最相近的条文及其元数据。

### 4. 结构化查询
1. 创建数据库并导入JSON：`cd Law_LLM && python FAISS/from_json_to_mysql.py`

## 代码处理流程
1. 遍历所有 `cleaned_data/*.json` 文件
2. 解析层级结构（编 → 分编 → 章 → 条）
3. 按每条法条写入数据库
4. 自动为每条记录分配 `vector_idx`（用于 FAISS 对应）

## 注意事项
1. 请确保 JSON 文件结构与示例一致，包含 `title`、`parts`、`chapters`、`articles` 等字段
2. 如需更换嵌入模型，可在 `LawFAISSIndexBuilder` 初始化时指定 `model_name`
3. 检索时仅返回相似度大于 0.6 的结果
4. 在使用前请确认msedgedriver.exe路径是否正确

## 可扩展的功能
* 接入 FastAPI 实现 Web 查询接口
* 支持模糊条号/章节匹配
* 多语言版本（中英对照）
* 支持分页、导出为 CSV/Excel