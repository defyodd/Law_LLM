@echo off
echo 法律AI助手 FastAPI后端启动脚本
echo ================================

echo 正在检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Python未安装或未添加到PATH
    pause
    exit /b 1
)

echo 正在安装依赖包...
pip install -r requirements.txt

echo 正在启动服务...
python start.py

pause
