#!/usr/bin/env python3
"""
意图测试平台 - 数据库初始化脚本（使用SQLAlchemy）
确保数据库表结构与models.py完全一致
"""
import os
import sys
import sqlite3
from datetime import datetime, timedelta
import json

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

def init_database_with_sqlalchemy():
    """使用SQLAlchemy创建数据库，确保与models.py一致"""
    print("🚀 意图测试平台 - 数据库初始化（SQLAlchemy版本）")
    print("=" * 50)
    
    try:
        # 导入Flask应用和模型
        from web_gui.app_enhanced import create_app
        from web_gui.models import db, TestCase, ExecutionHistory, StepExecution, Template
        
        # 创建Flask应用
        app = create_app()
        
        # 检查数据库文件
        db_path = os.path.join(project_root, 'data', 'app.db')
        
        # 备份现有数据库
        if os.path.exists(db_path):
            import time
            backup_path = f"{db_path}.backup.{int(time.time())}"
            os.rename(db_path, backup_path)
            print(f"✅ 已备份现有数据库到: {backup_path}")
        
        # 在应用上下文中创建表
        with app.app_context():
            print("🔧 正在使用SQLAlchemy创建数据库表...")
            # 创建所有表
            db.create_all()
            print("✅ 数据库表创建完成")
            
            # 创建索引
            print("🔧 正在创建数据库索引...")
            try:
                from web_gui.utils.db_optimization import create_database_indexes
                create_database_indexes(db)
                print("✅ 数据库索引创建完成")
            except ImportError:
                print("⚠️ 数据库优化模块不可用，跳过索引创建")
            
            # 插入示例数据
            print("📝 正在插入示例数据...")
            create_sample_data(db)
            
        print("=" * 50)
        print("✅ 数据库初始化完成！")
        print(f"📁 数据库位置: {db_path}")
        print("🚀 现在可以运行 ./scripts/dev-start.sh 启动开发环境")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_sample_data(db):
    """创建示例数据"""
    # 导入模型类
    from web_gui.models import TestCase, ExecutionHistory, StepExecution, Template
    
    # 示例测试用例
    testcases = [
        {
            "name": "百度首页访问测试",
            "description": "测试访问百度首页的基本功能",
            "category": "基础功能",
            "priority": 1,
            "steps": json.dumps([
                {
                    "action": "navigate",
                    "params": {"url": "https://www.baidu.com"},
                    "description": "打开百度首页"
                },
                {
                    "action": "ai_assert",
                    "params": {"condition": "页面标题包含'百度'"},
                    "description": "验证页面标题"
                }
            ]),
            "created_by": "system"
        },
        {
            "name": "百度搜索功能测试", 
            "description": "测试百度搜索框的输入和搜索功能",
            "category": "搜索功能",
            "priority": 2,
            "steps": json.dumps([
                {
                    "action": "navigate",
                    "params": {"url": "https://www.baidu.com"},
                    "description": "打开百度首页"
                },
                {
                    "action": "ai_input",
                    "params": {"text": "AI自动化测试", "locate": "搜索框"},
                    "description": "在搜索框中输入关键词"
                },
                {
                    "action": "ai_tap",
                    "params": {"locate": "百度一下按钮"},
                    "description": "点击搜索按钮"
                },
                {
                    "action": "ai_assert", 
                    "params": {"condition": "搜索结果页面显示相关结果"},
                    "description": "验证搜索结果"
                }
            ]),
            "created_by": "system"
        },
        {
            "name": "GitHub登录测试",
            "description": "测试GitHub网站的登录流程",
            "category": "登录功能", 
            "priority": 3,
            "steps": json.dumps([
                {
                    "action": "navigate",
                    "params": {"url": "https://github.com/login"},
                    "description": "打开GitHub登录页"
                },
                {
                    "action": "ai_input",
                    "params": {"text": "test@example.com", "locate": "用户名输入框"},
                    "description": "输入用户名"
                },
                {
                    "action": "ai_input", 
                    "params": {"text": "password123", "locate": "密码输入框"},
                    "description": "输入密码"
                },
                {
                    "action": "ai_tap",
                    "params": {"locate": "登录按钮"},
                    "description": "点击登录"
                }
            ]),
            "created_by": "system"
        }
    ]
    
    # 插入测试用例
    for tc_data in testcases:
        testcase = TestCase(**tc_data)
        db.session.add(testcase)
    
    db.session.commit()
    print(f"✅ 已创建 {len(testcases)} 个示例测试用例")
    
    # 创建示例执行历史
    print("📊 正在创建示例执行历史...")
    
    # 获取第一个测试用例
    first_testcase = TestCase.query.first()
    if first_testcase:
        # 创建一些示例执行记录
        executions = [
            {
                "execution_id": "exec_001",
                "test_case_id": first_testcase.id,
                "status": "success",
                "mode": "headless",
                "browser": "chrome",
                "start_time": datetime.utcnow() - timedelta(hours=2),
                "end_time": datetime.utcnow() - timedelta(hours=2) + timedelta(minutes=3),
                "duration": 180,
                "steps_total": 2,
                "steps_passed": 2,
                "steps_failed": 0,
                "executed_by": "system"
            },
            {
                "execution_id": "exec_002", 
                "test_case_id": first_testcase.id,
                "status": "failed",
                "mode": "browser",
                "browser": "firefox",
                "start_time": datetime.utcnow() - timedelta(hours=1),
                "end_time": datetime.utcnow() - timedelta(hours=1) + timedelta(minutes=1),
                "duration": 60,
                "steps_total": 2,
                "steps_passed": 1,
                "steps_failed": 1,
                "error_message": "页面加载超时",
                "executed_by": "system"
            }
        ]
        
        for exec_data in executions:
            execution = ExecutionHistory(**exec_data)
            db.session.add(execution)
        
        db.session.commit()
        print("✅ 示例执行历史创建完成")
    
    # 创建示例模板
    template_data = {
        "name": "用户登录测试模板",
        "description": "通用的用户登录流程测试模板",
        "category": "认证",
        "steps_template": json.dumps([
            {
                "action": "goto",
                "params": {"url": "{{login_url}}"},
                "description": "访问登录页面"
            },
            {
                "action": "ai_input", 
                "params": {"text": "{{username}}", "locate": "用户名输入框"},
                "description": "输入用户名"
            },
            {
                "action": "ai_input",
                "params": {"text": "{{password}}", "locate": "密码输入框"}, 
                "description": "输入密码"
            },
            {
                "action": "ai_tap",
                "params": {"prompt": "登录按钮"},
                "description": "点击登录按钮"
            }
        ]),
        "parameters": json.dumps({
            "login_url": {"type": "string", "description": "登录页面URL"},
            "username": {"type": "string", "description": "用户名"},
            "password": {"type": "string", "description": "密码"}
        }),
        "created_by": "system",
        "is_public": True
    }
    
    template = Template(**template_data)
    db.session.add(template)
    db.session.commit()
    print("✅ 已创建 1 个示例模板")

if __name__ == "__main__":
    init_database_with_sqlalchemy()