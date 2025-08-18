"""
数据库配置管理器 - 专用于SQLite数据库
支持本地开发和Vercel无服务器部署
"""

import os
from sqlalchemy import create_engine, text
from pathlib import Path


class DatabaseConfig:
    """数据库配置管理器 - SQLite专用"""
    
    def __init__(self):
        self.database_url = self._get_database_url()
        self.is_production = self._is_production()
        self.is_sqlite = True  # 始终使用SQLite
        
        # 确保SQLite数据库目录存在
        self._ensure_sqlite_directory()
    
    def _get_database_url(self) -> str:
        """获取SQLite数据库URL"""
        # 优先使用环境变量
        database_url = os.getenv('DATABASE_URL')

        if database_url:
            # 只处理SQLite URL
            if database_url.startswith('sqlite:///'):
                # 处理SQLite相对路径，转换为基于项目根目录的绝对路径
                if not database_url.startswith('sqlite:////'):
                    # 提取相对路径部分
                    relative_path = database_url[10:]  # 去掉 'sqlite:///' 前缀
                    if not relative_path.startswith('/'):  # 确保是相对路径
                        # 计算项目根目录
                        project_root = Path(__file__).parent.parent
                        absolute_path = project_root / relative_path
                        database_url = f"sqlite:///{absolute_path.absolute()}"
                return database_url
            else:
                print(f"⚠️ 警告：环境变量中配置的数据库不是SQLite，将使用默认SQLite配置")

        # Vercel环境使用临时目录
        if os.getenv('VERCEL') == '1':
            return "sqlite:////tmp/intent_test.db"

        # 本地开发环境使用data目录
        db_path = Path(__file__).parent.parent / "data" / "app.db"
        return f"sqlite:///{db_path.absolute()}"
    
    def _ensure_sqlite_directory(self):
        """确保SQLite数据库目录存在"""
        # 提取SQLite文件路径
        db_path = self.database_url.replace('sqlite:///', '')
        if db_path.startswith('/tmp/'):
            # Vercel临时目录，不需要创建
            return
        
        # 确保目录存在
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        print(f"✅ SQLite数据库目录已确保: {db_file.parent}")
    
    def _is_production(self) -> bool:
        """检查是否为生产环境"""
        return os.getenv('VERCEL') == '1' or os.getenv('FLASK_ENV') == 'production'
    
    def _test_sqlite_connection(self, url: str) -> bool:
        """测试SQLite连接是否可用"""
        try:
            engine = create_engine(url, echo=False)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"SQLite连接测试失败: {e}")
            return False
    
    def get_flask_config(self) -> dict:
        """获取Flask应用配置"""
        config = {
            'SQLALCHEMY_DATABASE_URI': self.database_url,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ECHO': not self.is_production,  # 生产环境关闭SQL日志
        }
        
        # SQLite特定配置
        config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'connect_args': {
                'check_same_thread': False,  # SQLite线程安全配置
                'timeout': 20  # 连接超时
            }
        }
        
        return config
    
    def get_database_info(self) -> dict:
        """获取数据库连接信息"""
        return {
            'database_url': self.database_url,
            'is_production': self.is_production,
            'is_sqlite': True,
            'database_type': 'SQLite'
        }


def get_flask_config() -> dict:
    """获取Flask数据库配置的便捷函数"""
    db_config = DatabaseConfig()
    config = db_config.get_flask_config()
    
    # 打印数据库信息
    db_type = 'SQLite'
    db_file = db_config.database_url.replace('sqlite:///', '')
    
    print(f"📊 数据库类型: {db_type}")
    print(f"📁 数据库文件: {db_file}")
    print(f"🌍 运行环境: {'生产环境' if db_config.is_production else '开发环境'}")
    
    return config


def print_database_info():
    """打印数据库连接信息"""
    db_config = DatabaseConfig()
    info = db_config.get_database_info()
    
    print("\n" + "="*50)
    print("🔍 数据库连接信息")
    print("="*50)
    for key, value in info.items():
        print(f"  {key}: {value}")
    print("="*50 + "\n")


def validate_database_connection() -> bool:
    """验证数据库连接"""
    try:
        db_config = DatabaseConfig()
        return db_config._test_sqlite_connection(db_config.database_url)
    except Exception as e:
        print(f"❌ 数据库连接验证失败: {e}")
        return False


if __name__ == "__main__":
    # 测试配置
    print("🧪 数据库配置测试")
    print("=" * 50)
    
    db_config = DatabaseConfig()
    config = db_config.get_flask_config()
    info = db_config.get_database_info()
    
    print("配置信息:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\nFlask配置:")
    for key, value in config.items():
        if key == 'SQLALCHEMY_DATABASE_URI':
            # 不显示完整的数据库URL（可能包含敏感信息）
            print(f"  {key}: {value.split('/')[-1] if 'sqlite' in value else '[隐藏]'}")
        else:
            print(f"  {key}: {value}")