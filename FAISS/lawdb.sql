-- 创建数据库
CREATE DATABASE lawdb DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 切换数据库
USE lawdb;

-- 创建表结构
CREATE TABLE articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    law_title VARCHAR(255),
    part_title VARCHAR(255),
    subpart_title VARCHAR(255),
    chapter_title VARCHAR(255),
    article_no VARCHAR(50),
    content TEXT,
    source_file VARCHAR(255),
    vector_idx INT
);


