import sqlite3
import argparse
import os

DB_PATH = "law_articles.db"

def connect():
    return sqlite3.connect(DB_PATH)

def query_by_article_no(article_nos):
    conn = connect()
    cursor = conn.cursor()
    for no in article_nos:
        cursor.execute("""
            SELECT law_title, part_title, subpart_title, chapter_title, article_no, content
            FROM articles WHERE article_no = ?
        """, (no,))
        rows = cursor.fetchall()
        if not rows:
            print(f"[未找到] 条号：{no}")
        else:
            for row in rows:
                law, part, sub, chap, no, content = row
                print(f"\n📘 {law} > {part} > {chap} > {no}\n{content}")
    conn.close()

def query_by_law(law_title):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT article_no, content FROM articles WHERE law_title LIKE ? ORDER BY id", (f"%{law_title}%",))
    rows = cursor.fetchall()
    for no, content in rows:
        print(f"{no} {content}")
    conn.close()

def query_by_law_part(law_title, part_title):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT chapter_title, article_no, content
        FROM articles
        WHERE law_title LIKE ? AND part_title LIKE ?
        ORDER BY id
    """, (f"%{law_title}%", f"%{part_title}%"))
    rows = cursor.fetchall()
    for chap, no, content in rows:
        print(f"\n{chap} > {no}\n{content}")
    conn.close()

def query_by_chapter(chapter_title, law_title=None):
    conn = connect()
    cursor = conn.cursor()
    if law_title:
        cursor.execute("""
            SELECT article_no, content FROM articles
            WHERE chapter_title LIKE ? AND law_title LIKE ?
            ORDER BY id
        """, (f"%{chapter_title}%", f"%{law_title}%"))
    else:
        cursor.execute("""
            SELECT article_no, content FROM articles
            WHERE chapter_title LIKE ?
            ORDER BY id
        """, (f"%{chapter_title}%",))
    rows = cursor.fetchall()
    for no, content in rows:
        print(f"{no} {content}")
    conn.close()

def search_by_keyword(keyword):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT law_title, part_title, chapter_title, article_no, content
        FROM articles
        WHERE content LIKE ?
        ORDER BY id
    """, (f"%{keyword}%",))
    rows = cursor.fetchall()
    print(f"🔍 共找到 {len(rows)} 条包含「{keyword}」的条文：")
    for row in rows:
        law, part, chap, no, content = row
        print(f"\n📖 {law} > {part} > {chap} > {no}\n{content}")
    conn.close()

def query_by_vector_idx(idx):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT law_title, article_no, content FROM articles WHERE vector_idx = ?", (idx,))
    row = cursor.fetchone()
    if row:
        print(f"\n[vector_idx={idx}]\n{row[0]} > {row[1]}\n{row[2]}")
    else:
        print(f"[未找到] vector_idx = {idx}")
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="SQLite 法条查询工具")
    parser.add_argument("--no", nargs='+', help="按条号查询，如：--no 第四条 第五条")
    parser.add_argument("--law", help="查询某部法律全文")
    parser.add_argument("--part", help="查询法律中的某一编")
    parser.add_argument("--chapter", help="查询法律中某一章")
    parser.add_argument("--keyword", help="按正文关键词模糊搜索")
    parser.add_argument("--vector", type=int, help="根据 FAISS vector_idx 查询条文")
    args = parser.parse_args()

    if args.no:
        query_by_article_no(args.no)
    elif args.law and args.part:
        query_by_law_part(args.law, args.part)
    elif args.chapter:
        query_by_chapter(args.chapter, args.law)
    elif args.law:
        query_by_law(args.law)
    elif args.keyword:
        search_by_keyword(args.keyword)
    elif args.vector is not None:
        query_by_vector_idx(args.vector)
    else:
        print("❗ 请提供至少一个查询参数。使用 --help 查看用法。")

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"[❌] 未找到数据库文件：{DB_PATH}")
    else:
        main()

