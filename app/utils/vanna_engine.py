import logging
import os
import time
from pathlib import Path
from vanna.ollama.ollama import Ollama
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
import pymysql
from app.config import settings

logger = logging.getLogger(__name__)


class HealthRiskVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        if config is None:
            config = {}

        # 使用绝对路径避免相对路径问题
        base_dir = Path(__file__).parent.parent
        chroma_path = config.get('chroma_db_path', str(base_dir / 'chromadb'))

        # 确保路径是绝对路径
        chroma_path = os.path.abspath(chroma_path)
        os.makedirs(chroma_path, exist_ok=True)
        config['chroma_db_path'] = chroma_path

        logger.info(f"初始化 ChromaDB，路径: {chroma_path}")

        # 添加超时机制
        max_retries = 1
        for attempt in range(max_retries):
            try:
                ChromaDB_VectorStore.__init__(self, config=config)
                Ollama.__init__(self, config=config)
                logger.info("ChromaDB 初始化成功")
                break
            except Exception as e:
                logger.warning(f"ChromaDB 初始化尝试 {attempt + 1} 失败: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error("ChromaDB 初始化完全失败，使用内存模式")
                    # 使用内存模式作为备选
                    config['chroma_db_path'] = None
                    ChromaDB_VectorStore.__init__(self, config=config)
                    Ollama.__init__(self, config=config)
                else:
                    time.sleep(2)  # 等待2秒后重试

        self.db_config = {
            'host': settings.MYSQL_HOST,
            'port': int(settings.MYSQL_PORT),
            'user': settings.MYSQL_USER,
            'password': settings.MYSQL_PASSWORD,
            'database': settings.MYSQL_DB,
            'charset': 'utf8mb4'
        }

        # 延迟连接数据库，避免启动时阻塞
        self.connection = None

    def connect_to_mysql(self):
        """连接MySQL数据库"""
        try:
            if self.connection is None or not self.connection.open:
                self.connection = pymysql.connect(**self.db_config)
                logger.info("成功连接到MySQL数据库")
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            return False

    def execute_sql(self, sql: str):
        """执行SQL查询"""
        try:
            # 确保连接存在
            if self.connection is None or not self.connection.open:
                self.connect_to_mysql()

            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
        except Exception as e:
            logger.error(f"SQL执行失败: {str(e)}")
            # 重新连接并重试一次
            try:
                self.connect_to_mysql()
                with self.connection.cursor(pymysql.cursors.DictCursor) as cursor: #连接对象
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    return result
            except Exception as retry_error:
                logger.error(f"SQL重试执行失败: {str(retry_error)}")
                raise retry_error

    def train_health_risk_tables(self):
        """训练健康风险表结构 - 异步执行避免阻塞"""
        try:
            # 用户健康风险测评记录表的DDL
            import vanna_train_examples
            ddl = vanna_train_examples.ddl

            # 训练DDL
            self.train(ddl=ddl)  #父类的方法
            # 训练业务文档
            documentation = vanna_train_examples.documentation
            self.train(documentation=documentation) #让模型“知道字段在业务里是什么意思
            from vanna_train_examples import example_sqls as train_sql
            # 训练示例SQL查询  #让模型“知道你希望它怎么写 SQL
            example_sqls = vanna_train_examples.example_sqls

            for sql in example_sqls:
                self.train(sql=sql)  #作为向量放进ChromaDB

            logger.info("健康风险表结构训练完成")
        except Exception as e:
            logger.error(f"训练过程出现错误: {str(e)}")
            # 不抛出异常，避免影响服务启动


# 初始化Vanna实例 - 使用绝对路径
base_dir = Path(__file__).parent
chroma_db_path = base_dir / 'chromadb'

vanna_config = {
    'model': settings.LLM_MODEL,
    'ollama_host': settings.OLLAMA_BASE_URL,
    'chroma_db_path': str(chroma_db_path)
}

vn = HealthRiskVanna(config=vanna_config)
