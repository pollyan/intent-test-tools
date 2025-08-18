"""
数据库配置管理器
支持SQLite数据库 (优化Vercel部署) 和PostgreSQL数据库
"""

import os
from urllib.parse import urlparse
from sqlalchemy import create_engine, text
from pathlib import Path


def is_postgres_available() -> bool:
    """检查PostgreSQL是否可用"""
    try:
        import psycopg2
        return True
    except ImportError:
        return False


class DatabaseConfig:
    """数据库配置管理器"""
    
    def __init__(self):
        self.database_url = self._get_database_url()
        self.is_production = self._is_production()
        self.is_sqlite = self.database_url.startswith('sqlite:///')
        
        # 如果是PostgreSQL，确保驱动可用
        if self.database_url.startswith(('postgresql://', 'postgres://')):
            if not is_postgres_available():
                raise ImportError(
                    "❌ PostgreSQL驱动未安装！\n"
                    "请安装PostgreSQL驱动：pip install psycopg2-binary\n"
                    "或者：pip install psycopg2"
                )
        
        # SQLite数据库文件路径初始化
        if self.is_sqlite:
            self._ensure_sqlite_directory()
    
    def _get_database_url(self) -> str:
        """获取数据库URL - 支持SQLite和PostgreSQL"""
        # 优先使用环境变量
        database_url = os.getenv('DATABASE_URL')

        if database_url:
            # 处理Heroku/Railway等平台的postgres://前缀
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)

            # 处理SQLite相对路径，转换为基于项目根目录的绝对路径
            if database_url.startswith('sqlite:///') and not database_url.startswith('sqlite:////'):
                # 提取相对路径部分
                relative_path = database_url[10:]  # 去掉 'sqlite:///' 前缀
                if not relative_path.startswith('/'):  # 确保是相对路径
                    # 计算项目根目录（database_config.py的父目录的父目录）
                    project_root = Path(__file__).parent.parent
                    absolute_path = project_root / relative_path
                    database_url = f"sqlite:///{absolute_path.absolute()}"

            # 为Serverless环境添加连接参数
            if os.getenv('VERCEL') == '1' and 'supabase.co' in database_url:
                # 添加Supabase Serverless优化参数
                if '?' not in database_url:
                    database_url += '?'
                else:
                    database_url += '&'
                database_url += 'sslmode=require&connect_timeout=10&application_name=vercel-intent-test'

            return database_url

        # Vercel环境优先使用SQLite
        if os.getenv('VERCEL') == '1':
            # Vercel环境中的SQLite数据库路径
            return "sqlite:////tmp/intent_test.db"

        # 本地开发环境使用SQLite
        if os.getenv('FLASK_ENV') == 'development' or not os.getenv('DATABASE_URL'):
            # 本地SQLite数据库路径
            db_path = Path(__file__).parent.parent / "data" / "intent_test.db"
            return f"sqlite:///{db_path.absolute()}"

        # Supabase特定配置（用于需要PostgreSQL的场景）
        supabase_url = os.getenv('SUPABASE_DATABASE_URL')
        if supabase_url:
            return supabase_url

        # 备用PostgreSQL配置
        return "postgresql://postgres.jzmqsuxphksbulrbhebp:Shunlian04@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres?sslmode=require&connect_timeout=15&application_name=local-dev"
    
    def _ensure_sqlite_directory(self):
        """确保SQLite数据库目录存在"""
        if self.database_url.startswith('sqlite:///'):
            # 提取SQLite文件路径
            db_path = self.database_url.replace('sqlite:///', '')
            if db_path.startswith('/tmp/'):
                # Vercel临时目录，不需要创建
                return
            
            # 本地开发环境，确保目录存在
            db_file = Path(db_path)
            db_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _is_production(self) -> bool:
        """判断是否为生产环境"""
        return os.getenv('VERCEL') == '1' or os.getenv('RAILWAY_ENVIRONMENT') == 'production'
    
    def _test_postgres_connection(self, url: str) -> bool:
        """测试PostgreSQL连接是否可用"""
        try:
            if not is_postgres_available():
                return False
            
            engine = create_engine(url, pool_pre_ping=True, connect_args={'connect_timeout': 5})
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
    
    def get_sqlalchemy_config(self) -> dict:
        """获取SQLAlchemy配置"""
        config = {
            'SQLALCHEMY_DATABASE_URI': self.database_url,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        }
        
        if self.is_sqlite:
            # SQLite特定配置
            engine_options = {
                'pool_pre_ping': True,
                'pool_recycle': -1,  # SQLite不需要连接回收
                'pool_timeout': 20,
                'echo': False,  # 生产环境关闭SQL日志
                'connect_args': {
                    'check_same_thread': False,  # SQLite多线程支持
                    'timeout': 20  # 连接超时设置
                }
            }

            # Vercel环境优化配置
            if self.is_production:
                engine_options.update({
                    'poolclass': None,  # Serverless环境禁用连接池
                    'pool_pre_ping': False,  # 减少不必要的ping
                    'connect_args': {
                        'check_same_thread': False,
                        'timeout': 10,
                        'isolation_level': None  # 自动提交模式
                    }
                })

            config.update({
                'SQLALCHEMY_ENGINE_OPTIONS': engine_options
            })
            
        elif self.database_url.startswith(('postgresql://', 'postgres://')):
            # PostgreSQL特定配置
            engine_options = {
                'pool_pre_ping': True,
                'pool_recycle': 3600,
            }

            # Serverless环境优化
            if self.is_production:
                engine_options.update({
                    'pool_size': 1,  # Serverless环境使用小连接池
                    'max_overflow': 0,  # 不允许溢出连接
                    'pool_timeout': 10,  # 快速超时
                    'connect_args': {
                        'connect_timeout': 10,
                        'sslmode': 'require',
                        'application_name': 'vercel-intent-test'
                    }
                })
            else:
                engine_options.update({
                    'pool_size': 5,
                    'pool_timeout': 60,
                    'max_overflow': 10,
                    'connect_args': {
                        'connect_timeout': 15,
                        'sslmode': 'require',
                        'application_name': 'local-dev'
                    }
                })

            config.update({
                'SQLALCHEMY_ENGINE_OPTIONS': engine_options
            })
        else:
            # 默认配置
            config.update({
                'SQLALCHEMY_ENGINE_OPTIONS': {
                    'pool_pre_ping': True,
                    'pool_recycle': 3600,
                    'pool_size': 10,
                    'pool_timeout': 30,
                    'max_overflow': 20,
                }
            })
        
        return config
    
    def get_migration_config(self) -> dict:
        """获取数据库迁移配置"""
        if self.is_sqlite:
            return {
                'source_type': 'sqlite',
                'target_type': 'sqlite',
                'batch_size': 500,  # SQLite适合较小的批次
                'enable_foreign_keys': True,
                'wal_mode': True,  # 启用WAL模式提升并发性能
            }
        else:
            return {
                'source_type': 'postgresql',
                'target_type': 'postgresql',
                'batch_size': 1000,
                'enable_foreign_keys': True,
            }
    
    def create_engine_with_config(self):
        """创建配置好的数据库引擎"""
        config = self.get_sqlalchemy_config()
        engine_options = config.get('SQLALCHEMY_ENGINE_OPTIONS', {})
        
        return create_engine(
            self.database_url,
            **engine_options
        )
    
    def get_connection_info(self) -> dict:
        """获取连接信息用于调试"""
        parsed = urlparse(self.database_url)
        
        return {
            'scheme': parsed.scheme,
            'host': parsed.hostname or ('local-file' if self.is_sqlite else 'unknown'),
            'port': parsed.port,
            'database': parsed.path.lstrip('/') if parsed.path else 'unknown',
            'is_sqlite': self.is_sqlite,
            'is_postgres': self.database_url.startswith(('postgresql://', 'postgres://')),
            'is_production': self.is_production,
            'database_type': 'SQLite' if self.is_sqlite else ('PostgreSQL' if self.database_url.startswith(('postgresql://', 'postgres://')) else 'Unknown')
        }


# 全局配置实例
db_config = DatabaseConfig()


def print_database_info():
    """打印数据库连接信息"""
    info = db_config.get_connection_info()
    
    print("🗄️  数据库配置信息:")
    print(f"   类型: {info['database_type']}")
    print(f"   环境: {'生产环境' if info['is_production'] else '开发环境'}")
    print(f"   主机: {info['host']}")
    if info['port']:
        print(f"   端口: {info['port']}")
    print(f"   数据库: {info['database']}")


def get_flask_config() -> dict:
    """获取Flask应用的数据库配置"""
    return db_config.get_sqlalchemy_config()


def validate_database_connection() -> bool:
    """验证数据库连接"""
    try:
        engine = db_config.create_engine_with_config()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        return True
    except Exception as e:
        db_type = 'SQLite' if db_config.is_sqlite else 'PostgreSQL'
        print(f"❌ {db_type}数据库连接失败: {e}")
        return False


if __name__ == '__main__':
    # 测试配置
    try:
        print_database_info()
        if db_config.is_sqlite:
            print("SQLite数据库模式")
        else:
            print(f"PostgreSQL驱动可用: {is_postgres_available()}")
        print(f"数据库连接: {'✅ 成功' if validate_database_connection() else '❌ 失败'}")
    except Exception as e:
        print(f"❌ 配置错误: {e}")
