"""
数据库初始化服务
支持SQLite和PostgreSQL数据库的创建和初始化
"""

import os
import logging
from pathlib import Path
from sqlalchemy import create_engine, text
from contextlib import contextmanager

try:
    from database_config import db_config
    from models import db, TestCase, ExecutionHistory, StepExecution, Template
except ImportError:
    from web_gui.database_config import db_config
    from web_gui.models import db, TestCase, ExecutionHistory, StepExecution, Template


class DatabaseInitService:
    """数据库初始化服务"""
    
    def __init__(self):
        self.db_config = db_config
        self.logger = logging.getLogger(__name__)
    
    def ensure_database_exists(self):
        """确保数据库文件存在（主要用于SQLite）"""
        if self.db_config.is_sqlite:
            db_path = self.db_config.database_url.replace('sqlite:///', '')
            
            # Vercel环境中的临时数据库不需要预创建
            if db_path.startswith('/tmp/'):
                return True
            
            # 本地环境确保数据库文件存在
            db_file = Path(db_path)
            if not db_file.exists():
                self.logger.info(f"创建SQLite数据库文件: {db_path}")
                db_file.parent.mkdir(parents=True, exist_ok=True)
                db_file.touch()
                
                # 设置WAL模式以提升并发性能
                self._enable_wal_mode(db_path)
                
        return True
    
    def _enable_wal_mode(self, db_path):
        """为SQLite启用WAL模式"""
        try:
            engine = create_engine(f"sqlite:///{db_path}")
            with engine.connect() as conn:
                conn.execute(text("PRAGMA journal_mode=WAL;"))
                conn.execute(text("PRAGMA synchronous=NORMAL;"))
                conn.execute(text("PRAGMA cache_size=10000;"))
                conn.execute(text("PRAGMA foreign_keys=ON;"))
                conn.commit()
            self.logger.info("SQLite WAL模式已启用")
        except Exception as e:
            self.logger.warning(f"启用WAL模式失败: {e}")
    
    def initialize_tables(self, app=None):
        """初始化数据库表结构"""
        try:
            if app:
                with app.app_context():
                    db.create_all()
                    self.logger.info("数据库表结构初始化完成")
            else:
                # 直接使用SQLAlchemy引擎
                engine = self.db_config.create_engine_with_config()
                from web_gui.models import db
                db.metadata.create_all(bind=engine)
                self.logger.info("数据库表结构初始化完成 (无Flask上下文)")
            return True
        except Exception as e:
            self.logger.error(f"数据库表初始化失败: {e}")
            return False
    
    def create_sample_data(self, app=None):
        """创建示例数据（可选）"""
        if not self._should_create_sample_data():
            return True
            
        try:
            if app:
                with app.app_context():
                    return self._create_sample_records()
            else:
                # 暂不支持无Flask上下文的示例数据创建
                self.logger.info("跳过示例数据创建 (无Flask上下文)")
                return True
        except Exception as e:
            self.logger.error(f"创建示例数据失败: {e}")
            return False
    
    def _should_create_sample_data(self):
        """判断是否应该创建示例数据"""
        # 只在本地开发环境创建示例数据
        return (not self.db_config.is_production and 
                os.getenv('CREATE_SAMPLE_DATA', 'false').lower() == 'true')
    
    def _create_sample_records(self):
        """创建示例记录"""
        # 检查是否已有数据
        if TestCase.query.first():
            self.logger.info("已存在测试用例，跳过示例数据创建")
            return True
        
        # 创建示例测试模板
        sample_template = Template(
            name="简单页面测试模板",
            description="用于测试基本页面导航和元素查找的模板",
            steps=[
                {
                    "action": "navigate",
                    "params": {"url": "https://example.com"},
                    "description": "导航到示例页面"
                },
                {
                    "action": "ai_assert",
                    "params": {"condition": "页面标题包含'Example'"},
                    "description": "验证页面标题"
                }
            ]
        )
        db.session.add(sample_template)
        
        # 创建示例测试用例
        sample_testcase = TestCase(
            name="示例测试用例",
            description="这是一个示例测试用例，演示基本功能",
            steps=[
                {
                    "action": "navigate",
                    "params": {"url": "https://example.com"},
                    "description": "打开示例网站"
                },
                {
                    "action": "ai_assert",
                    "params": {"condition": "页面加载完成"},
                    "description": "验证页面加载"
                }
            ]
        )
        db.session.add(sample_testcase)
        
        db.session.commit()
        self.logger.info("示例数据创建完成")
        return True
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        engine = self.db_config.create_engine_with_config()
        conn = engine.connect()
        try:
            yield conn
        finally:
            conn.close()
    
    def backup_database(self, backup_path=None):
        """备份SQLite数据库"""
        if not self.db_config.is_sqlite:
            self.logger.warning("备份功能仅支持SQLite数据库")
            return False
        
        try:
            source_path = self.db_config.database_url.replace('sqlite:///', '')
            
            if not backup_path:
                timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f"{source_path}.backup_{timestamp}"
            
            # 使用SQLite的备份API
            import sqlite3
            source_conn = sqlite3.connect(source_path)
            backup_conn = sqlite3.connect(backup_path)
            
            source_conn.backup(backup_conn)
            
            source_conn.close()
            backup_conn.close()
            
            self.logger.info(f"数据库备份完成: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"数据库备份失败: {e}")
            return False
    
    def get_database_stats(self):
        """获取数据库统计信息"""
        try:
            with self.get_connection() as conn:
                stats = {}
                
                # 获取各表的记录数
                for table_name in ['test_cases', 'execution_history', 'step_executions', 'templates']:
                    try:
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                        count = result.scalar()
                        stats[table_name] = count
                    except Exception as e:
                        stats[table_name] = f"Error: {e}"
                
                if self.db_config.is_sqlite:
                    # SQLite特有的统计信息
                    result = conn.execute(text("PRAGMA database_list"))
                    db_info = result.fetchall()
                    stats['database_file'] = db_info[0][2] if db_info else "Unknown"
                    
                    # 获取数据库大小
                    db_path = self.db_config.database_url.replace('sqlite:///', '')
                    if Path(db_path).exists():
                        stats['database_size_mb'] = round(Path(db_path).stat().st_size / 1024 / 1024, 2)
                
                return stats
        except Exception as e:
            self.logger.error(f"获取数据库统计信息失败: {e}")
            return {'error': str(e)}


# 全局实例
db_init_service = DatabaseInitService()


def init_database(app=None):
    """快捷函数：完整的数据库初始化流程"""
    service = db_init_service
    
    # 1. 确保数据库存在
    service.ensure_database_exists()
    
    # 2. 初始化表结构
    success = service.initialize_tables(app)
    
    if success:
        # 3. 创建示例数据（如果需要）
        service.create_sample_data(app)
    
    return success


if __name__ == '__main__':
    # 测试初始化服务
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    service = DatabaseInitService()
    print("数据库初始化服务测试:")
    print(f"数据库类型: {'SQLite' if service.db_config.is_sqlite else 'PostgreSQL'}")
    
    if service.ensure_database_exists():
        print("✅ 数据库文件创建成功")
        
        stats = service.get_database_stats()
        print("数据库统计信息:", stats)
    else:
        print("❌ 数据库文件创建失败")