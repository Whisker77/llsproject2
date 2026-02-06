from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
class DatabaseManager:
    """
    数据库管理类
    负责数据库连接、会话管理和表创建
    """

    def __init__(self, connection_string):
        """
        初始化数据库管理器
        Args:
            connection_string: 数据库连接字符串
        """
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        """
        创建所有表
        执行SQLAlchemy的元数据创建所有定义的表
        """
        Base.metadata.create_all(self.engine)

    def get_session(self):
        """
        获取数据库会话

        Returns:
            SQLAlchemy会话对象
        """
        return self.Session()
