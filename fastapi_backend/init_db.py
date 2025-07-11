"""
数据库初始化脚本 - 使用 PyMySQL
"""
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager, create_tables

def init_database():
    """初始化数据库"""
    try:
        print("正在初始化数据库...")
        
        # 创建所有表
        # create_tables()
        # print("数据库表创建成功!")
        
        # 测试连接
        with db_manager.get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print("数据库连接测试成功!")
            
        print("数据库初始化完成!")
        
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()
