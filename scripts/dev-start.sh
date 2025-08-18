#!/bin/bash

# 意图测试平台 - 本地开发环境启动脚本
# 使用方法: ./scripts/dev-start.sh

set -e  # 遇到错误时退出

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  意图测试平台 - 本地开发环境启动${NC}"
echo -e "${BLUE}========================================${NC}"
echo

# 检查是否在项目根目录
if [ ! -f "web_gui/app_enhanced.py" ] && [ ! -f "midscene_server.js" ]; then
    echo -e "${RED}❌ 错误: 请在项目根目录运行此脚本${NC}"
    echo "当前目录: $(pwd)"
    exit 1
fi

# 创建必要的目录
mkdir -p logs
mkdir -p data
mkdir -p screenshots

echo -e "${GREEN}✅ 目录检查完成${NC}"

# 检查Python环境
echo -e "${BLUE}[1/6]${NC} 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3未找到，请先安装Python 3.8+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python版本: ${PYTHON_VERSION}${NC}"

# 检查Node.js环境
echo -e "${BLUE}[2/6]${NC} 检查Node.js环境..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js未找到，请先安装Node.js 16+${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✅ Node.js版本: ${NODE_VERSION}${NC}"

# 检查和安装Python依赖
echo -e "${BLUE}[3/6]${NC} 检查Python依赖..."
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 创建Python虚拟环境...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate
echo -e "${GREEN}✅ 已激活虚拟环境${NC}"

# 安装Python依赖
if [ ! -f "venv/.deps_installed" ] || [ "requirements.txt" -nt "venv/.deps_installed" ]; then
    echo -e "${YELLOW}📦 安装Python依赖包...${NC}"
    pip install -r requirements.txt
    pip install -r web_gui/requirements.txt
    touch venv/.deps_installed
    echo -e "${GREEN}✅ Python依赖安装完成${NC}"
else
    echo -e "${GREEN}✅ Python依赖已是最新${NC}"
fi

# 检查和安装Node.js依赖
echo -e "${BLUE}[4/6]${NC} 检查Node.js依赖..."
if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules/.deps_installed" ]; then
    echo -e "${YELLOW}📦 安装Node.js依赖包...${NC}"
    npm install
    touch node_modules/.deps_installed
    echo -e "${GREEN}✅ Node.js依赖安装完成${NC}"
else
    echo -e "${GREEN}✅ Node.js依赖已是最新${NC}"
fi

# 检查环境变量配置
echo -e "${BLUE}[5/6]${NC} 检查环境配置..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚙️ 创建环境配置文件...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️ 请编辑.env文件配置您的API密钥${NC}"
    echo -e "配置文件位置: $(pwd)/.env"
fi

# 检查API密钥配置
if grep -q "your-api-key-here" .env; then
    echo -e "${YELLOW}⚠️ 检测到默认API密钥，请配置实际的API密钥${NC}"
    echo -e "编辑命令: nano .env"
fi

echo -e "${GREEN}✅ 环境配置检查完成${NC}"

# 初始化数据库
echo -e "${BLUE}[6/6]${NC} 初始化数据库..."
if [ ! -f "data/app.db" ]; then
    echo -e "${YELLOW}📊 创建本地数据库...${NC}"
    python3 scripts/init_db.py
    echo -e "${GREEN}✅ 数据库初始化完成${NC}"
else
    echo -e "${GREEN}✅ 数据库已存在${NC}"
fi

echo
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  环境准备完成，开始启动服务${NC}"
echo -e "${GREEN}========================================${NC}"
echo

# 启动服务函数
start_services() {
    echo -e "${BLUE}🚀 启动MidScene AI服务器...${NC}"
    # 在后台启动Node.js服务器
    nohup node midscene_server.js > logs/midscene.log 2>&1 &
    MIDSCENE_PID=$!
    echo $MIDSCENE_PID > logs/midscene.pid
    echo -e "${GREEN}✅ MidScene服务器已启动 (PID: $MIDSCENE_PID)${NC}"
    
    # 等待MidScene服务启动
    sleep 3
    
    echo -e "${BLUE}🌐 启动Web应用服务器...${NC}"
    # 启动Flask应用（前台运行）
    echo -e "${YELLOW}📱 Web服务器将在前台运行，按Ctrl+C停止所有服务${NC}"
    echo
    echo -e "${GREEN}🌐 Web界面: http://localhost:5001${NC}"
    echo -e "${GREEN}🤖 AI服务: http://localhost:3001${NC}"
    echo -e "${GREEN}📊 测试用例: http://localhost:5001/testcases${NC}"
    echo -e "${GREEN}🔧 执行控制台: http://localhost:5001/execution${NC}"
    echo -e "${GREEN}📈 测试报告: http://localhost:5001/reports${NC}"
    echo
    
    # 捕获Ctrl+C信号
    trap cleanup INT
    
    # 启动Web服务器
    cd web_gui && python3 app_enhanced.py
}

# 清理函数
cleanup() {
    echo
    echo -e "${YELLOW}🛑 正在停止服务...${NC}"
    
    # 停止MidScene服务器
    if [ -f "logs/midscene.pid" ]; then
        MIDSCENE_PID=$(cat logs/midscene.pid)
        if kill -0 $MIDSCENE_PID 2>/dev/null; then
            echo -e "${BLUE}🛑 停止MidScene服务器 (PID: $MIDSCENE_PID)...${NC}"
            kill $MIDSCENE_PID
        fi
        rm -f logs/midscene.pid
    fi
    
    # 停止其他可能的后台进程
    pkill -f "midscene_server.js" 2>/dev/null || true
    pkill -f "app_enhanced.py" 2>/dev/null || true
    
    echo -e "${GREEN}✅ 所有服务已停止${NC}"
    exit 0
}

# 启动服务
start_services