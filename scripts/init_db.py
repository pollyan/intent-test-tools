#!/usr/bin/env python3
"""
意图测试平台 - 数据库初始化脚本
用于本地开发环境的数据库创建和示例数据生成
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
import uuid

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def create_sqlite_database():
    """创建SQLite数据库和表结构"""
    db_path = os.path.join(parent_dir, 'data', 'app.db')
    
    # 确保data目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # 如果数据库已存在，先备份
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup.{int(datetime.now().timestamp())}"
        os.rename(db_path, backup_path)
        print(f"✅ 已备份现有数据库到: {backup_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔧 正在创建数据库表...")
    
    # 创建测试用例表
    cursor.execute("""
    CREATE TABLE test_cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        steps TEXT NOT NULL,
        tags VARCHAR(500),
        category VARCHAR(100),
        priority INTEGER DEFAULT 3,
        created_by VARCHAR(100),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )
    """)
    
    # 创建执行历史表
    cursor.execute("""
    CREATE TABLE execution_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        execution_id VARCHAR(36) UNIQUE NOT NULL,
        test_case_id INTEGER,
        status VARCHAR(20) DEFAULT 'pending',
        mode VARCHAR(20) DEFAULT 'headless',
        browser VARCHAR(20) DEFAULT 'chrome',
        start_time DATETIME,
        end_time DATETIME,
        duration INTEGER DEFAULT 0,
        steps_total INTEGER DEFAULT 0,
        steps_passed INTEGER DEFAULT 0,
        steps_failed INTEGER DEFAULT 0,
        error_message TEXT,
        executed_by VARCHAR(100),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (test_case_id) REFERENCES test_cases (id)
    )
    """)
    
    # 创建步骤执行表
    cursor.execute("""
    CREATE TABLE step_executions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        execution_id VARCHAR(36) NOT NULL,
        step_index INTEGER NOT NULL,
        step_description TEXT,
        status VARCHAR(20) DEFAULT 'pending',
        start_time DATETIME,
        end_time DATETIME,
        duration INTEGER DEFAULT 0,
        screenshot_path VARCHAR(500),
        error_message TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 创建模板表
    cursor.execute("""
    CREATE TABLE templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        category VARCHAR(100),
        steps_template TEXT NOT NULL,
        parameters TEXT,
        created_by VARCHAR(100),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_public BOOLEAN DEFAULT 0
    )
    """)
    
    # 创建索引
    print("🔧 正在创建数据库索引...")
    indexes = [
        "CREATE INDEX idx_testcase_active ON test_cases(is_active)",
        "CREATE INDEX idx_testcase_category ON test_cases(category, is_active)",
        "CREATE INDEX idx_testcase_created ON test_cases(created_at)",
        "CREATE INDEX idx_execution_testcase ON execution_history(test_case_id)",
        "CREATE INDEX idx_execution_status ON execution_history(status)",
        "CREATE INDEX idx_execution_created ON execution_history(created_at)",
        "CREATE INDEX idx_step_execution ON step_executions(execution_id)",
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    conn.commit()
    print("✅ 数据库表和索引创建完成")
    
    return conn, cursor

def insert_sample_data(cursor):
    """插入示例数据"""
    print("📝 正在插入示例数据...")
    
    # 示例测试用例
    sample_testcases = [
        {
            'name': '百度首页访问测试',
            'description': '测试访问百度首页的基本功能',
            'steps': json.dumps([
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
            'category': '基础功能',
            'priority': 1,
            'created_by': 'system'
        },
        {
            'name': '百度搜索功能测试',
            'description': '测试百度搜索框的输入和搜索功能',
            'steps': json.dumps([
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
            'category': '搜索功能',
            'priority': 2,
            'created_by': 'system'
        },
        {
            'name': 'GitHub登录测试',
            'description': '测试GitHub网站的登录流程',
            'steps': json.dumps([
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
            'category': '登录功能',
            'priority': 3,
            'created_by': 'system'
        }
    ]
    
    testcase_ids = []
    for tc in sample_testcases:
        cursor.execute("""
        INSERT INTO test_cases (name, description, steps, category, priority, created_by)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (tc['name'], tc['description'], tc['steps'], tc['category'], tc['priority'], tc['created_by']))
        testcase_ids.append(cursor.lastrowid)
    
    print(f"✅ 已创建 {len(sample_testcases)} 个示例测试用例")
    
    # 示例执行历史
    print("📊 正在创建示例执行历史...")
    base_time = datetime.now() - timedelta(days=7)
    
    for i, testcase_id in enumerate(testcase_ids):
        # 为每个测试用例创建几个执行记录
        for j in range(3 + i):  # 不同数量的执行记录
            execution_id = str(uuid.uuid4())
            status = ['success', 'failed', 'success', 'success'][j % 4]
            start_time = base_time + timedelta(days=j, hours=i*2)
            end_time = start_time + timedelta(minutes=2 + j)
            duration = int((end_time - start_time).total_seconds())
            
            cursor.execute("""
            INSERT INTO execution_history 
            (execution_id, test_case_id, status, mode, start_time, end_time, duration, 
             steps_total, steps_passed, steps_failed, executed_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                execution_id, testcase_id, status, 'headless', 
                start_time, end_time, duration,
                len(json.loads(sample_testcases[i]['steps'])),  # steps_total
                len(json.loads(sample_testcases[i]['steps'])) if status == 'success' else j,  # steps_passed
                0 if status == 'success' else 1,  # steps_failed
                'system'
            ))
            
            # 创建步骤执行记录
            steps = json.loads(sample_testcases[i]['steps'])
            for step_idx, step in enumerate(steps):
                step_start = start_time + timedelta(seconds=step_idx * 30)
                step_end = step_start + timedelta(seconds=20)
                step_status = 'success' if status == 'success' or step_idx < j else 'failed'
                
                cursor.execute("""
                INSERT INTO step_executions
                (execution_id, step_index, step_description, status, start_time, end_time, duration)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    execution_id, step_idx, step['description'], step_status,
                    step_start, step_end, 20
                ))
    
    print("✅ 示例执行历史创建完成")
    
    # 示例模板
    sample_templates = [
        {
            'name': '网站基础测试模板',
            'description': '通用的网站功能测试模板',
            'category': '通用',
            'steps_template': json.dumps([
                {
                    "action": "navigate",
                    "params": {"url": "{{website_url}}"},
                    "description": "访问{{website_name}}"
                },
                {
                    "action": "ai_assert",
                    "params": {"condition": "页面正常加载"},
                    "description": "验证页面加载"
                }
            ]),
            'parameters': json.dumps({
                "website_url": {"type": "string", "description": "网站URL"},
                "website_name": {"type": "string", "description": "网站名称"}
            }),
            'created_by': 'system',
            'is_public': 1
        }
    ]
    
    for tpl in sample_templates:
        cursor.execute("""
        INSERT INTO templates (name, description, category, steps_template, parameters, created_by, is_public)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (tpl['name'], tpl['description'], tpl['category'], 
              tpl['steps_template'], tpl['parameters'], tpl['created_by'], tpl['is_public']))
    
    print(f"✅ 已创建 {len(sample_templates)} 个示例模板")

def main():
    """主函数"""
    print("🚀 意图测试平台 - 数据库初始化")
    print("=" * 50)
    
    try:
        # 创建数据库
        conn, cursor = create_sqlite_database()
        
        # 插入示例数据
        insert_sample_data(cursor)
        
        # 提交并关闭连接
        conn.commit()
        conn.close()
        
        print("=" * 50)
        print("✅ 数据库初始化完成！")
        print(f"📁 数据库位置: {os.path.join(parent_dir, 'data', 'app.db')}")
        print("🚀 现在可以运行 ./scripts/dev-start.sh 启动开发环境")
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()