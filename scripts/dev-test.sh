#!/bin/bash

# 意图测试平台 - 快速测试脚本
# 用于运行各种测试和健康检查

set -e

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  意图测试平台 - 开发测试工具${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查服务状态
check_services() {
    echo -e "${BLUE}📊 检查服务状态...${NC}"
    
    # 检查Web服务
    if curl -s -f http://localhost:5001/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Web服务 (端口5001) - 正常${NC}"
    else
        echo -e "${RED}❌ Web服务 (端口5001) - 异常${NC}"
        return 1
    fi
    
    # 检查MidScene服务
    if curl -s -f http://localhost:3001/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ MidScene服务 (端口3001) - 正常${NC}"
    else
        echo -e "${YELLOW}⚠️ MidScene服务 (端口3001) - 异常或未启动${NC}"
    fi
    
    # 检查数据库
    if [ -f "data/app.db" ]; then
        echo -e "${GREEN}✅ SQLite数据库 - 存在${NC}"
    else
        echo -e "${YELLOW}⚠️ SQLite数据库 - 不存在，需要初始化${NC}"
    fi
}

# 测试API端点
test_apis() {
    echo -e "${BLUE}🔍 测试API端点...${NC}"
    
    # 测试健康检查
    echo -n "  健康检查API: "
    if curl -s -f http://localhost:5001/health >/dev/null; then
        echo -e "${GREEN}✅ 通过${NC}"
    else
        echo -e "${RED}❌ 失败${NC}"
    fi
    
    # 测试API状态
    echo -n "  API状态检查: "
    if curl -s -f http://localhost:5001/api/status >/dev/null; then
        echo -e "${GREEN}✅ 通过${NC}"
    else
        echo -e "${RED}❌ 失败${NC}"
    fi
    
    # 测试测试用例API
    echo -n "  测试用例API: "
    if curl -s -f "http://localhost:5001/api/testcases?page=1&size=5" >/dev/null; then
        echo -e "${GREEN}✅ 通过${NC}"
    else
        echo -e "${RED}❌ 失败${NC}"
    fi
    
    # 测试统计数据API
    echo -n "  统计数据API: "
    if curl -s -f "http://localhost:5001/api/stats/dashboard" >/dev/null; then
        echo -e "${GREEN}✅ 通过${NC}"
    else
        echo -e "${RED}❌ 失败${NC}"
    fi
}

# 运行Python单元测试
run_python_tests() {
    echo -e "${BLUE}🧪 运行Python单元测试...${NC}"
    
    # 激活虚拟环境
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    fi
    
    if [ -d "tests" ]; then
        python3 -m pytest tests/ -v --tb=short 2>/dev/null || {
            echo -e "${YELLOW}⚠️ Python测试运行失败或无可用测试${NC}"
        }
    else
        echo -e "${YELLOW}⚠️ 未找到tests目录${NC}"
    fi
}

# 检查代码质量
check_code_quality() {
    echo -e "${BLUE}🔍 代码质量检查...${NC}"
    
    # 激活虚拟环境
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    fi
    
    # Python语法检查
    echo -n "  Python语法检查: "
    if python3 -m py_compile web_gui/*.py api/*.py 2>/dev/null; then
        echo -e "${GREEN}✅ 通过${NC}"
    else
        echo -e "${RED}❌ 发现语法错误${NC}"
    fi
    
    # JavaScript语法检查
    echo -n "  JavaScript语法检查: "
    if node -c midscene_server.js 2>/dev/null; then
        echo -e "${GREEN}✅ 通过${NC}"
    else
        echo -e "${RED}❌ 发现语法错误${NC}"
    fi
}

# 数据库健康检查
check_database() {
    echo -e "${BLUE}🗄️ 数据库健康检查...${NC}"
    
    if [ -f "data/app.db" ]; then
        # 激活虚拟环境
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
        fi
        
        # 检查数据库表
        echo -n "  数据库连接: "
        if python3 -c "
import sqlite3
import sys
try:
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
    tables = cursor.fetchall()
    if len(tables) > 0:
        print('✅ 连接成功，包含', len(tables), '个表')
    else:
        print('⚠️ 连接成功但无表结构')
    conn.close()
except Exception as e:
    print('❌ 连接失败:', e)
    sys.exit(1)
" 2>/dev/null; then
            echo -e "${GREEN}数据库正常${NC}"
        else
            echo -e "${RED}❌ 数据库连接失败${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ 数据库文件不存在${NC}"
    fi
}

# 性能基准测试
run_benchmark() {
    echo -e "${BLUE}⚡ 简单性能测试...${NC}"
    
    echo -n "  Web服务响应时间: "
    RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:5001/health 2>/dev/null || echo "timeout")
    if [ "$RESPONSE_TIME" != "timeout" ]; then
        echo -e "${GREEN}${RESPONSE_TIME}s${NC}"
    else
        echo -e "${RED}❌ 超时${NC}"
    fi
    
    echo -n "  API响应时间: "
    API_TIME=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:5001/api/status 2>/dev/null || echo "timeout")
    if [ "$API_TIME" != "timeout" ]; then
        echo -e "${GREEN}${API_TIME}s${NC}"
    else
        echo -e "${RED}❌ 超时${NC}"
    fi
}

# 查看服务日志
show_logs() {
    echo -e "${BLUE}📋 最近的服务日志...${NC}"
    
    if [ -f "logs/midscene.log" ]; then
        echo -e "${YELLOW}=== MidScene服务日志 (最近10行) ===${NC}"
        tail -10 logs/midscene.log 2>/dev/null || echo "无法读取日志文件"
    fi
    
    if [ -f "logs/app.log" ]; then
        echo -e "${YELLOW}=== Web服务日志 (最近10行) ===${NC}"
        tail -10 logs/app.log 2>/dev/null || echo "无法读取日志文件"
    fi
}

# 清理临时文件
cleanup_temp() {
    echo -e "${BLUE}🧹 清理临时文件...${NC}"
    
    # 清理Python缓存
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # 清理旧的日志文件（保留最近的）
    if [ -d "logs" ]; then
        find logs -name "*.log.*" -mtime +7 -delete 2>/dev/null || true
    fi
    
    # 清理旧的截图文件
    if [ -d "screenshots" ]; then
        find screenshots -name "*.png" -mtime +7 -delete 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✅ 清理完成${NC}"
}

# 帮助信息
show_help() {
    echo "使用方法: $0 [命令]"
    echo ""
    echo "可用命令:"
    echo "  check     - 检查服务状态"
    echo "  api       - 测试API端点"
    echo "  test      - 运行单元测试"
    echo "  quality   - 代码质量检查"
    echo "  db        - 数据库健康检查"
    echo "  bench     - 性能基准测试"
    echo "  logs      - 查看服务日志"
    echo "  clean     - 清理临时文件"
    echo "  all       - 运行所有检查"
    echo "  help      - 显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 check   # 检查服务状态"
    echo "  $0 all     # 运行完整测试套件"
}

# 主函数
main() {
    case "${1:-all}" in
        "check")
            check_services
            ;;
        "api")
            test_apis
            ;;
        "test")
            run_python_tests
            ;;
        "quality")
            check_code_quality
            ;;
        "db")
            check_database
            ;;
        "bench")
            run_benchmark
            ;;
        "logs")
            show_logs
            ;;
        "clean")
            cleanup_temp
            ;;
        "all")
            echo -e "${GREEN}🚀 运行完整测试套件...${NC}"
            echo ""
            check_services
            echo ""
            test_apis
            echo ""
            check_code_quality
            echo ""
            check_database
            echo ""
            run_benchmark
            echo ""
            echo -e "${GREEN}========================================${NC}"
            echo -e "${GREEN}  测试套件执行完成${NC}"
            echo -e "${GREEN}========================================${NC}"
            ;;
        "help")
            show_help
            ;;
        *)
            echo -e "${RED}❌ 未知命令: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 检查是否在项目根目录
if [ ! -f "web_gui/app_enhanced.py" ] && [ ! -f "midscene_server.js" ]; then
    echo -e "${RED}❌ 错误: 请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 执行主函数
main "$@"