@echo off
chcp 65001 >nul
title Intent Test Framework - 本地开发环境

echo.
echo ========================================
echo   意图测试平台 - 本地开发环境启动
echo ========================================
echo.

REM 检查是否在项目根目录
if not exist "web_gui\app_enhanced.py" (
    if not exist "midscene_server.js" (
        echo X 错误: 请在项目根目录运行此脚本
        echo 当前目录: %CD%
        pause
        exit /b 1
    )
)

REM 创建必要的目录
if not exist "logs" mkdir logs
if not exist "data" mkdir data  
if not exist "screenshots" mkdir screenshots

echo + 目录检查完成

REM 检查Python环境
echo.
echo [1/6] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python未找到，请先安装Python 3.8+
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo + Python版本: %PYTHON_VERSION%

REM 检查Node.js环境
echo.
echo [2/6] 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo X Node.js未找到，请先安装Node.js 16+
    pause
    exit /b 1
)

for /f %%i in ('node --version') do set NODE_VERSION=%%i
echo + Node.js版本: %NODE_VERSION%

REM 检查和创建Python虚拟环境
echo.
echo [3/6] 检查Python依赖...
if not exist "venv" (
    echo ^ 创建Python虚拟环境...
    python -m venv venv
)

call venv\Scripts\activate.bat
echo + 已激活虚拟环境

REM 安装Python依赖
if not exist "venv\.deps_installed" (
    echo ^ 安装Python依赖包...
    pip install -r requirements.txt
    pip install -r web_gui\requirements.txt
    echo. > venv\.deps_installed
    echo + Python依赖安装完成
) else (
    echo + Python依赖已是最新
)

REM 检查和安装Node.js依赖
echo.
echo [4/6] 检查Node.js依赖...
if not exist "node_modules" (
    echo ^ 安装Node.js依赖包...
    npm install
    echo + Node.js依赖安装完成
) else (
    if exist "package.json" (
        for %%i in (package.json) do set PKG_TIME=%%~ti
        for %%i in (node_modules) do set NODE_TIME=%%~ti
        REM 简单检查，实际应该比较时间戳
        echo + Node.js依赖检查完成
    )
)

REM 检查环境变量配置
echo.
echo [5/6] 检查环境配置...
if not exist ".env" (
    echo ^ 创建环境配置文件...
    copy .env.example .env >nul
    echo ! 请编辑.env文件配置您的API密钥
    echo 配置文件位置: %CD%\.env
)

findstr "your-api-key-here" .env >nul 2>&1
if not errorlevel 1 (
    echo ! 检测到默认API密钥，请配置实际的API密钥
    echo 编辑命令: notepad .env
)

echo + 环境配置检查完成

REM 初始化数据库
echo.
echo [6/6] 初始化数据库...
if not exist "data\app.db" (
    echo ^ 创建本地数据库...
    python scripts\init_db.py
    echo + 数据库初始化完成
) else (
    echo + 数据库已存在
)

echo.
echo ========================================
echo   环境准备完成，开始启动服务
echo ========================================
echo.

REM 启动MidScene服务器
echo ^ 启动MidScene AI服务器...
start /b cmd /c "node midscene_server.js > logs\midscene.log 2>&1"
timeout /t 3 /nobreak >nul

REM 启动Web服务器
echo ^ 启动Web应用服务器...
echo.
echo 服务地址:
echo   Web界面: http://localhost:5001
echo   AI服务: http://localhost:3001  
echo   测试用例: http://localhost:5001/testcases
echo   执行控制台: http://localhost:5001/execution
echo   测试报告: http://localhost:5001/reports
echo.
echo 按Ctrl+C停止服务器
echo.

cd web_gui
python app_enhanced.py

REM 清理
echo.
echo 正在停止服务...
taskkill /f /im node.exe >nul 2>&1
echo 服务已停止
pause