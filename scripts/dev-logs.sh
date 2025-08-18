#!/bin/bash

# 意图测试平台 - 日志查看和调试工具
# 用于实时查看和分析服务日志

set -e

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  意图测试平台 - 日志调试工具${NC}"
echo -e "${BLUE}========================================${NC}"

# 创建日志目录
mkdir -p logs

# 实时查看所有日志
tail_all_logs() {
    echo -e "${GREEN}📋 实时查看所有服务日志 (Ctrl+C退出)${NC}"
    echo -e "${YELLOW}---${NC}"
    
    # 检查并创建日志文件
    touch logs/midscene.log logs/app.log
    
    # 使用multitail或者tail -f查看多个日志文件
    if command -v multitail >/dev/null 2>&1; then
        multitail -ci cyan logs/midscene.log -ci yellow logs/app.log
    else
        # 使用tail -f的替代方案
        tail -f logs/midscene.log logs/app.log 2>/dev/null
    fi
}

# 查看MidScene日志
show_midscene_logs() {
    echo -e "${CYAN}🤖 MidScene服务日志${NC}"
    echo -e "${YELLOW}---${NC}"
    
    if [ -f "logs/midscene.log" ]; then
        case "${1:-recent}" in
            "all")
                cat logs/midscene.log
                ;;
            "recent")
                tail -50 logs/midscene.log
                ;;
            "errors")
                grep -i "error\|exception\|failed" logs/midscene.log 2>/dev/null || echo "没有发现错误日志"
                ;;
            "follow")
                echo -e "${GREEN}实时跟踪MidScene日志 (Ctrl+C退出)${NC}"
                tail -f logs/midscene.log
                ;;
        esac
    else
        echo -e "${YELLOW}⚠️ MidScene日志文件不存在${NC}"
    fi
}

# 查看Web应用日志
show_web_logs() {
    echo -e "${GREEN}🌐 Web应用服务日志${NC}"
    echo -e "${YELLOW}---${NC}"
    
    if [ -f "logs/app.log" ]; then
        case "${1:-recent}" in
            "all")
                cat logs/app.log
                ;;
            "recent")
                tail -50 logs/app.log
                ;;
            "errors")
                grep -i "error\|exception\|failed" logs/app.log 2>/dev/null || echo "没有发现错误日志"
                ;;
            "follow")
                echo -e "${GREEN}实时跟踪Web应用日志 (Ctrl+C退出)${NC}"
                tail -f logs/app.log
                ;;
        esac
    else
        echo -e "${YELLOW}⚠️ Web应用日志文件不存在${NC}"
    fi
}

# 分析错误日志
analyze_errors() {
    echo -e "${RED}🚨 错误日志分析${NC}"
    echo -e "${YELLOW}---${NC}"
    
    local found_errors=false
    
    # MidScene错误
    if [ -f "logs/midscene.log" ]; then
        echo -e "${CYAN}MidScene服务错误:${NC}"
        if grep -i "error\|exception\|failed" logs/midscene.log >/dev/null 2>&1; then
            grep -i "error\|exception\|failed" logs/midscene.log | tail -10
            found_errors=true
        else
            echo -e "${GREEN}  ✅ 无错误${NC}"
        fi
        echo
    fi
    
    # Web应用错误
    if [ -f "logs/app.log" ]; then
        echo -e "${GREEN}Web应用错误:${NC}"
        if grep -i "error\|exception\|failed" logs/app.log >/dev/null 2>&1; then
            grep -i "error\|exception\|failed" logs/app.log | tail -10
            found_errors=true
        else
            echo -e "${GREEN}  ✅ 无错误${NC}"
        fi
        echo
    fi
    
    if [ "$found_errors" = false ]; then
        echo -e "${GREEN}✅ 未发现明显错误${NC}"
    fi
}

# 系统资源监控
monitor_resources() {
    echo -e "${PURPLE}📊 系统资源监控${NC}"
    echo -e "${YELLOW}---${NC}"
    
    # 检查进程状态
    echo -e "${BLUE}进程状态:${NC}"
    echo "  MidScene进程:"
    if pgrep -f "midscene_server.js" >/dev/null; then
        ps aux | grep midscene_server.js | grep -v grep | awk '{printf "    PID: %s, CPU: %s%%, MEM: %s%%\n", $2, $3, $4}'
    else
        echo -e "    ${YELLOW}未运行${NC}"
    fi
    
    echo "  Web应用进程:"
    if pgrep -f "app_enhanced.py" >/dev/null; then
        ps aux | grep app_enhanced.py | grep -v grep | awk '{printf "    PID: %s, CPU: %s%%, MEM: %s%%\n", $2, $3, $4}'
    else
        echo -e "    ${YELLOW}未运行${NC}"
    fi
    
    echo
    echo -e "${BLUE}端口占用情况:${NC}"
    echo "  端口3001 (MidScene):"
    if lsof -i :3001 >/dev/null 2>&1; then
        lsof -i :3001 | grep LISTEN | awk '{printf "    %s (PID: %s)\n", $1, $2}'
    else
        echo -e "    ${YELLOW}未占用${NC}"
    fi
    
    echo "  端口5001 (Web):"
    if lsof -i :5001 >/dev/null 2>&1; then
        lsof -i :5001 | grep LISTEN | awk '{printf "    %s (PID: %s)\n", $1, $2}'
    else
        echo -e "    ${YELLOW}未占用${NC}"
    fi
    
    echo
    echo -e "${BLUE}磁盘使用情况:${NC}"
    echo "  项目目录大小:"
    du -sh . 2>/dev/null | awk '{printf "    总计: %s\n", $1}'
    if [ -d "logs" ]; then
        du -sh logs 2>/dev/null | awk '{printf "    日志: %s\n", $1}'
    fi
    if [ -d "data" ]; then
        du -sh data 2>/dev/null | awk '{printf "    数据: %s\n", $1}'
    fi
    if [ -d "screenshots" ]; then
        du -sh screenshots 2>/dev/null | awk '{printf "    截图: %s\n", $1}'
    fi
}

# 清理和归档日志
manage_logs() {
    echo -e "${YELLOW}🗂️ 日志文件管理${NC}"
    echo -e "${YELLOW}---${NC}"
    
    case "${1:-status}" in
        "status")
            echo "当前日志文件状态:"
            if [ -d "logs" ]; then
                ls -lah logs/ 2>/dev/null | grep -v "^total" | while read line; do
                    echo "  $line"
                done
            else
                echo -e "${YELLOW}  日志目录不存在${NC}"
            fi
            ;;
        "rotate")
            echo "轮转日志文件..."
            timestamp=$(date +"%Y%m%d_%H%M%S")
            
            if [ -f "logs/midscene.log" ] && [ -s "logs/midscene.log" ]; then
                mv "logs/midscene.log" "logs/midscene.log.$timestamp"
                touch "logs/midscene.log"
                echo -e "${GREEN}  ✅ 已轮转 midscene.log${NC}"
            fi
            
            if [ -f "logs/app.log" ] && [ -s "logs/app.log" ]; then
                mv "logs/app.log" "logs/app.log.$timestamp"
                touch "logs/app.log"
                echo -e "${GREEN}  ✅ 已轮转 app.log${NC}"
            fi
            ;;
        "clean")
            echo -e "${YELLOW}清理旧日志文件...${NC}"
            if [ -d "logs" ]; then
                # 删除7天前的归档日志
                find logs -name "*.log.*" -mtime +7 -delete 2>/dev/null || true
                # 清空当前日志文件
                > logs/midscene.log 2>/dev/null || true
                > logs/app.log 2>/dev/null || true
                echo -e "${GREEN}  ✅ 已清理日志文件${NC}"
            fi
            ;;
        "archive")
            echo "归档日志文件..."
            timestamp=$(date +"%Y%m%d")
            archive_dir="logs/archive/$timestamp"
            mkdir -p "$archive_dir"
            
            if [ -f "logs/midscene.log" ] && [ -s "logs/midscene.log" ]; then
                cp "logs/midscene.log" "$archive_dir/"
                > logs/midscene.log
            fi
            
            if [ -f "logs/app.log" ] && [ -s "logs/app.log" ]; then
                cp "logs/app.log" "$archive_dir/"
                > logs/app.log
            fi
            
            echo -e "${GREEN}  ✅ 已归档到 $archive_dir${NC}"
            ;;
    esac
}

# 调试模式启动
debug_mode() {
    echo -e "${PURPLE}🔍 启动调试模式${NC}"
    echo -e "${YELLOW}---${NC}"
    
    # 设置调试环境变量
    export DEBUG=true
    export LOG_LEVEL=DEBUG
    export FLASK_ENV=development
    
    echo -e "${GREEN}已设置调试环境变量:${NC}"
    echo "  DEBUG=true"
    echo "  LOG_LEVEL=DEBUG"
    echo "  FLASK_ENV=development"
    echo
    echo -e "${YELLOW}提示: 重启服务以应用调试设置${NC}"
}

# 帮助信息
show_help() {
    echo "日志和调试工具使用方法: $0 [命令] [选项]"
    echo ""
    echo "可用命令:"
    echo "  all [recent|errors|follow]  - 查看所有服务日志"
    echo "  midscene [recent|all|errors|follow] - 查看MidScene日志"
    echo "  web [recent|all|errors|follow]      - 查看Web应用日志"
    echo "  errors                      - 分析错误日志"
    echo "  monitor                     - 系统资源监控"
    echo "  logs [status|rotate|clean|archive] - 日志文件管理"
    echo "  debug                       - 启动调试模式"
    echo "  tail                        - 实时跟踪所有日志"
    echo "  help                        - 显示帮助信息"
    echo ""
    echo "日志选项:"
    echo "  recent  - 显示最近50行 (默认)"
    echo "  all     - 显示全部日志"
    echo "  errors  - 只显示错误日志"
    echo "  follow  - 实时跟踪日志"
    echo ""
    echo "示例:"
    echo "  $0 tail              # 实时查看所有日志"
    echo "  $0 midscene errors   # 查看MidScene错误日志"
    echo "  $0 web follow        # 实时跟踪Web应用日志"
    echo "  $0 errors            # 分析所有错误"
    echo "  $0 monitor           # 监控系统资源"
    echo "  $0 logs clean        # 清理日志文件"
}

# 主函数
main() {
    local command="${1:-tail}"
    local option="${2:-recent}"
    
    case "$command" in
        "all")
            case "$option" in
                "follow")
                    tail_all_logs
                    ;;
                *)
                    show_midscene_logs "$option"
                    echo ""
                    show_web_logs "$option"
                    ;;
            esac
            ;;
        "midscene"|"mid")
            show_midscene_logs "$option"
            ;;
        "web"|"app")
            show_web_logs "$option"
            ;;
        "errors"|"err")
            analyze_errors
            ;;
        "monitor"|"mon")
            monitor_resources
            ;;
        "logs"|"manage")
            manage_logs "$option"
            ;;
        "debug")
            debug_mode
            ;;
        "tail")
            tail_all_logs
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo -e "${RED}❌ 未知命令: $command${NC}"
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