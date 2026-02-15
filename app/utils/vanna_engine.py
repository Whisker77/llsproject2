import logging
import os
import time
from pathlib import Path
import pymysql

from vanna.legacy.ollama.ollama import Ollama
from vanna.legacy.chromadb.chromadb_vector import ChromaDB_VectorStore

from app.config import settings

logger = logging.getLogger(__name__)


class HealthRiskVanna(ChromaDB_VectorStore, Ollama):
    """
    用 legacy 的 Ollama + legacy 的 ChromaDB_VectorStore
    这样你现在的多继承结构才成立。
    """
    def __init__(self, config=None):
        if config is None:
            config = {}

        # 1) 处理 chroma 持久化目录：绝对路径
        base_dir = Path(__file__).resolve().parent  # 当前文件目录
        chroma_path = config.get("chroma_db_path", str(base_dir / "chromadb"))
        chroma_path = os.path.abspath(chroma_path)
        os.makedirs(chroma_path, exist_ok=True)

        # legacy chroma 这里你之前用的是 chroma_db_path，我们保持一致
        config["chroma_db_path"] = chroma_path

        logger.info(f"初始化 ChromaDB，路径: {chroma_path}")

        # 2) 初始化向量库 + LLM（加一次重试）
        max_retries = int(config.get("init_retries", 1))
        last_err = None
        for attempt in range(max_retries):
            try:
                ChromaDB_VectorStore.__init__(self, config=config)
                Ollama.__init__(self, config=config)
                logger.info("Vanna 初始化成功（ChromaDB + Ollama）")
                last_err = None
                break
            except Exception as e:
                last_err = e
                logger.warning(f"初始化尝试 {attempt + 1}/{max_retries} 失败: {e}")
                time.sleep(1)

        # 兜底：仍失败就退回内存模式（不持久化）
        if last_err is not None:
            logger.error(f"初始化最终失败，退回内存模式。原因: {last_err}")
            config["chroma_db_path"] = None
            ChromaDB_VectorStore.__init__(self, config=config)
            Ollama.__init__(self, config=config)

        # 3) MySQL 连接配置
        self.db_config = {
            "host": settings.MYSQL_HOST,
            "port": int(settings.MYSQL_PORT),
            "user": settings.MYSQL_USER,
            "password": settings.MYSQL_PASSWORD,
            "database": settings.MYSQL_DB,
            "charset": "utf8mb4",
        }
        self.connection = None

    def connect_to_mysql(self) -> bool:
        """连接 MySQL 数据库"""
        try:
            if self.connection is None or not self.connection.open:
                self.connection = pymysql.connect(**self.db_config)
                logger.info("成功连接到 MySQL 数据库")
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False

    def execute_sql(self, sql: str):
        """执行 SQL 查询（只读查询推荐）"""
        if not sql or not isinstance(sql, str):
            raise ValueError("sql 必须是非空字符串")

        try:
            if self.connection is None or not self.connection.open:
                ok = self.connect_to_mysql()
                if not ok:
                    raise RuntimeError("MySQL 连接失败")

            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql)
                return cursor.fetchall()

        except Exception as e:
            logger.error(f"SQL 执行失败: {e} | SQL: {sql}")
            # 重连重试一次
            try:
                ok = self.connect_to_mysql()
                if not ok:
                    raise RuntimeError("MySQL 重连失败")

                with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute(sql)
                    return cursor.fetchall()
            except Exception as retry_error:
                logger.error(f"SQL 重试执行失败: {retry_error} | SQL: {sql}")
                raise

    def train_health_risk_tables(self):
        """训练健康风险表结构（DDL + 业务文档 + 示例 SQL）"""
        try:
            import vanna_train_examples

            ddl = vanna_train_examples.ddl
            documentation = vanna_train_examples.documentation
            example_sqls = vanna_train_examples.example_sqls

            # 训练 DDL
            self.train(ddl=ddl)

            # 训练业务文档
            self.train(documentation=documentation)

            # 训练示例 SQL
            for s in example_sqls:
                self.train(sql=s)

            logger.info("健康风险表结构训练完成")
        except Exception as e:
            logger.error(f"训练过程出现错误: {e}")


# -------------------------
# 初始化 Vanna 实例
# -------------------------
base_dir = Path(__file__).resolve().parent
chroma_db_path = base_dir / "chromadb"

vanna_config = {
    # vanna legacy 常用：model + base_url（或 host）——你别用你那个乱七八糟的 key
    "model": settings.LLM_MODEL,              # 例如 "qwen2.5"
    "base_url": settings.OLLAMA_BASE_URL,     # 例如 "http://localhost:11434"
    "chroma_db_path": str(chroma_db_path),
    "init_retries": 1,
}

vn = HealthRiskVanna(config=vanna_config)
