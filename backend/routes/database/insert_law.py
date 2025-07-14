import json
import pymysql
import os

def read_json_file(file_path: str) -> dict:
    """读取JSON文件并返回内容"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def connect_to_db(host: str, user: str, password: str, db: str) -> pymysql.Connection:
    """连接到MySQL数据库"""
    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=db,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def insert_law_to_db(law_data: dict, db: pymysql.Connection) -> bool:
    """将法律数据插入数据库"""
    try:
        with db.cursor() as cursor:
            sql = "INSERT INTO laws (title, parts) VALUES (%s, %s)"
            cursor.execute(sql, (law_data['title'], json.dumps(law_data['parts'])))
        db.commit()
        return True
    except Exception as e:
        print(f"插入法律数据失败: {e}", flush=True)
        db.rollback()
        return False
    
    
def main():
    # 配置数据库连接
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'db': 'law_llm'
    }

    db = connect_to_db(**db_config)
    if not db:
        print("数据库连接失败", flush=True)
        return

    for file in os.listdir("../../../crawled data/cleaned_data"):
        if file.endswith(".json"):
            law_data = read_json_file(os.path.join("../../../crawled data/cleaned_data", file))

        # 插入法律数据
        if insert_law_to_db(law_data, db):
            print("法律数据插入成功", flush=True)
        else:
            print("法律数据插入失败", flush=True)

    db.close()


if __name__ == "__main__":
    main()
