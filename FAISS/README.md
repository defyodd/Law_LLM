# 法律条文 FAISS 索引与检索项目

## 项目简介
本目录用于将结构化法律条文（JSON 格式）批量转换为向量，利用 FAISS 构建高效的相似度检索索引，并支持基于语义的法律条文查询。

## 主要功能
- 加载多层级结构的法律条文 JSON 数据
- 使用 SentenceTransformer 生成文本嵌入向量
- 构建并保存 FAISS 向量索引
- 命令行语义检索，返回最相似条文及元数据

## 环境要求
- Python 3.x
- numpy
- faiss
- sentence-transformers
- pickle

## 安装依赖
```bash
pip install numpy faiss-cpu sentence-transformers
```

## 目录结构
- `FAISS/build_index.py`：索引构建与保存脚本
- `FAISS/query_index.py`：命令行检索脚本
- `FAISS/indexes/`：保存生成的 FAISS 索引及配套文件
  - `law_faiss_index.bin`：FAISS 索引文件
  - `law_texts.pkl`：原始文本内容列表
  - `law_metadata.pkl`：每条文本的元数据信息
  - `index_config.json`：索引配置信息
  - `crawled data/cleaned_data/`：存放结构化法律条文 JSON 文件

## 使用方法

### 1. 构建索引
将待索引的法律条文 JSON 文件放入 `crawled data/cleaned_data/` 目录，运行：
```bash
python FAISS/build_index.py
```
索引和元数据将保存在 `FAISS/indexes/` 目录。

### 2. 检索条文
运行检索脚本，按提示输入查询内容：
```bash
python FAISS/query_index.py
```
返回与输入语义最相近的条文及其元数据。

## 输出文件说明
- `law_faiss_index.bin`：FAISS 索引文件
- `law_texts.pkl`：原始文本内容列表
- `law_metadata.pkl`：每条文本的元数据信息
- `index_config.json`：索引配置信息

## 示例 JSON 结构
```json
{
  "title": "中华人民共和国民法典",
  "parts": [
    {
      "part_title": "第一编 总则",
      "subparts": [],
      "chapters": [
        {
          "chapter_title": "第一章 基本规定",
          "articles": [
            {
              "article_no": "第一条",
              "article_content": "为了保护民事主体的合法权益，调整民事关系，维护社会和经济秩序，适应中国特色社会主义发展要求，弘扬社会主义核心价值观，根据宪法，制定本法。"
            }
          ]
        }
      ]
    }
  ]
}
```
## 注意事项
- 请确保 JSON 文件结构与示例一致，包含 `title`、`parts`、`chapters`、`articles` 等字段
- 如需更换嵌入模型，可在 `LawFAISSIndexBuilder` 初始化时指定 `model_name`
- 检索时仅返回相似度大于 0.6 的结果
