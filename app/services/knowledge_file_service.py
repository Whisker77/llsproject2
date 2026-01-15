import uuid
from typing import Dict, Any
import logging
from app.models.mysql.knowledge_file import KnowledgeFile
from app.models.mysql.database_manager import DatabaseManager
from app.dao.knowledge_file_dao import KnowledgeFileDAO
from app.config import settings
logger = logging.getLogger(__name__)

db_manager = DatabaseManager(settings.MYSQL_URI)
file_dao = KnowledgeFileDAO(db_manager)
class KnowledgeFileService:
    """知识文件服务类，封装知识文件相关的数据库操作"""
    def __init__(self):
        # 初始化服务
        pass


    def save_knowledge_file(self, model_param: Dict[str, Any]) -> KnowledgeFile:
        """保存新的知识文件"""
        logger.info("保存新知识文件")
        try:
            # 使用get方法简化字段赋值，设置合理默认值
            id = uuid.uuid4()
            # 转换为字符串
            model_param['id'] = str(id)
            knowledge_file = file_dao.create_file(model_param)
            logger.info(f"知识文件保存成功! ID: {knowledge_file.id}")
            return knowledge_file
        except Exception as e:
            logger.error(f"保存知识文件失败: {str(e)}", exc_info=True)
            raise
    def update_knowledge_file(self, id, model_param: Dict[str, Any]) -> KnowledgeFile:
        logger.info('更改知识文件')
        try:
            knowledge_file = file_dao.update_file(id, model_param)
            logger.info(f'知识文件更新成功！! ID: {knowledge_file.id}')
            return knowledge_file
        except Exception as e:
            logger.error(f'更新知识文件失败：: {str(e)}', exc_info=True)
            raise

    def delete_knowledge_file(self, id):
        logger.info('删除知识文件')
        try:
            knowledge_file_is_deleted = file_dao.delete_file(id)
            logger.info(f'知识文件删除成功！ID:{id}')
            return knowledge_file_is_deleted
        except Exception as e:
            logger.error(f'删除知识文件失败：: {str(e)}', exc_info=True)
            raise

    def get_knowledge_file(self, file_id: str) -> KnowledgeFile:
        logger.info('查询知识文件')
        try:
            knowledge_file = file_dao.get_file_by_id(file_id)
            return knowledge_file
        except Exception as e:
            logger.error(f'查询知识文件失败:{str(e)}',exc_info=True)
            raise

    def list_knowledge_files(
        self,
        filter_param: Dict[str, Any],
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        logger.info('查询知识文件列表')
        try:
            knowledge_files = file_dao.list_files(
                filters=filter_param,
                page=page,
                per_page=per_page
            )
            return knowledge_files
        except Exception as e:
            logger.error(f'查询知识文件列表失败:{str(e)}', exc_info=True)
            raise
