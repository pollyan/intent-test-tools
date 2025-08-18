#!/bin/bash

# 意图测试平台 - 快速重启脚本
# 用于快速重启服务以应用代码更改

set -e

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  快速重启开发环境${NC}"
echo -e "${BLUE}========================================${NC}"

# 停止现有服务
echo -e "${YELLOW}🛑 停止现有服务...${NC}"

# 停止MidScene服务器
if [ -f "logs/midscene.pid" ]; then
    MIDSCENE_PID=$(cat logs/midscene.pid)
    if kill -0 $MIDSCENE_PID 2>/dev/null; then
        echo -e "${BLUE}🛑 停止MidScene服务器 (PID: $MIDSCENE_PID)${NC}"
        kill $MIDSCENE_PID
        sleep 2
    fi
    rm -f logs/midscene.pid
fi

# 强制停止所有相关进程
pkill -f "midscene_server.js" 2>/dev/null || true
pkill -f "app_enhanced.py" 2>/dev/null || true
pkill -f "flask run" 2>/dev/null || true

# 等待进程完全停止
sleep 2

echo -e "${GREEN}✅ 现有服务已停止${NC}"

# 检查端口是否被释放
check_port() {
    local port=$1
    local service=$2
    
    if lsof -i :$port >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  端口 $port ($service) 仍被占用，尝试释放...${NC}"
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
}

check_port 3001 "MidScene"
check_port 5001 "Web"

# 快速启动服务
echo -e "${BLUE}🚀 重新启动服务...${NC}"

# 激活虚拟环境
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✅ 已激活虚拟环境${NC}"
fi

# 启动MidScene服务器
echo -e "${BLUE}🤖 启动MidScene AI服务器...${NC}"
nohup node midscene_server.js > logs/midscene.log 2>&1 &
MIDSCENE_PID=$!
echo $MIDSCENE_PID > logs/midscene.pid
echo -e "${GREEN}✅ MidScene服务器已启动 (PID: $MIDSCENE_PID)${NC}"

# 等待MidScene服务启动
echo -e "${YELLOW}⏳ 等待MidScene服务器启动...${NC}"
sleep 3

# 检查MidScene服务器是否正常启动
if ! kill -0 $MIDSCENE_PID 2>/dev/null; then
    echo -e "${RED}❌ MidScene服务器启动失败${NC}"
    echo -e "${RED}查看日志: tail -f logs/midscene.log${NC}"
    exit 1
fi

# 启动Web服务器
echo -e "${BLUE}🌐 启动Web应用服务器...${NC}"
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

cleanup() {
    echo
    echo -e "${YELLOW}🛑 正在停止服务...${NC}"
    
    if [ -f "logs/midscene.pid" ]; then
        MIDSCENE_PID=$(cat logs/midscene.pid)
        if kill -0 $MIDSCENE_PID 2>/dev/null; then
            kill $MIDSCENE_PID
        fi
        rm -f logs/midscene.pid
    fi
    
    pkill -f "midscene_server.js" 2>/dev/null || true
    pkill -f "app_enhanced.py" 2>/dev/null || true
    
    echo -e "${GREEN}✅ 所有服务已停止${NC}"
    exit 0
}

# 启动Web服务器
cd web_gui && python3 app_enhanced.py