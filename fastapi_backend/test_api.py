"""
API测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_registration():
    """测试用户注册"""
    print("测试用户注册...")
    data = {
        "username": "testuser",
        "password": "password123",
        "repassword": "password123",
        "email": "test@example.com"
    }
    response = requests.post(f"{BASE_URL}/auth/register", data=data)
    print(f"注册结果: {response.json()}")
    return response.status_code == 200

def test_login():
    """测试用户登录"""
    print("测试用户登录...")
    data = {
        "username": "testuser",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", data=data)
    result = response.json()
    print(f"登录结果: {result}")
    
    if result.get("code") == 0:
        return result.get("data")  # 返回JWT令牌
    return None

def test_get_user_info(token):
    """测试获取用户信息"""
    print("测试获取用户信息...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/getUserInfo", headers=headers)
    print(f"用户信息: {response.json()}")
    return response.status_code == 200

def test_create_history(token):
    """测试创建历史记录"""
    print("测试创建历史记录...")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "userId": 1,
        "title": "测试对话",
        "type": "chat"
    }
    response = requests.post(f"{BASE_URL}/ai/create", data=data, headers=headers)
    result = response.json()
    print(f"创建历史记录结果: {result}")
    
    if result.get("code") == 0:
        return result.get("data", {}).get("historyId")
    return None

def test_get_laws():
    """测试获取法律列表"""
    print("测试获取法律列表...")
    response = requests.get(f"{BASE_URL}/law/getAllLaws")
    print(f"法律列表: {response.json()}")
    return response.status_code == 200

def main():
    """运行测试"""
    print("开始API测试...\n")
    
    # 测试健康检查
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"健康检查: {response.json()}\n")
    except Exception as e:
        print(f"无法连接到服务器: {e}")
        return
    
    # 测试用户注册
    test_registration()
    print()
    
    # 测试用户登录
    token = test_login()
    print()
    
    if token:
        # 测试获取用户信息
        test_get_user_info(token)
        print()
        
        # 测试创建历史记录
        history_id = test_create_history(token)
        print()
    
    # 测试获取法律列表
    test_get_laws()
    print()
    
    print("测试完成!")

if __name__ == "__main__":
    main()
