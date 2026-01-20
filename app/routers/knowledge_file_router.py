from pydantic import BaseModel
from ..schemas.common import ApiResponse
from .base_router import BaseRouter
from fastapi import status,Path,Body,Query
import logging
from ..services.knowledge_file_service import KnowledgeFileService
from ..schemas.knowledge_file import (
    KnowledgeFileCreate,
    KnowledgeFileUpdate,
    KnowledgeFileResponse,
)

from ..exceptions.base_api_exception import (
    DatabaseException,
    NotFoundException,
    ValidationException,
)
logger = logging.getLogger(__name__)
knowledge_file_service = KnowledgeFileService()
class KnowledgeFileRouter(BaseRouter):
    def __init__(self):
        logger.info("Initializing FileHandleRouter")
        super().__init__()
        self.router = self._register_routes()

    def _register_routes(self):
        """注册所有路由处理方法并添加Swagger文档注解"""
        # 上传知识文件
        self.router.post(
            "/knowledgeFiles",
            response_model=ApiResponse,
            status_code=status.HTTP_201_CREATED,
            summary="新增知识文件",
            description="创建知识文件元数据记录",
            tags=["知识管理"]
        )(self.create_knowledge_file)

        self.router.put(
            "/knowledgeFiles/{file_id}",
            response_model=ApiResponse,
            status_code=status.HTTP_200_OK,
            summary="更新知识文件",
            description="更新指定知识文件信息",
            tags=["知识管理"]
        )(self.update_knowledge_file)

        self.router.delete(
            "/knowledgeFiles/{file_id}",
            response_model=ApiResponse,
            status_code=status.HTTP_200_OK,
            summary="删除知识文件",
            description="删除指定知识文件记录",
            tags=["知识管理"]
        )(self.delete_knowledge_file)

        self.router.get(
            "/knowledgeFiles/{file_id}",
            response_model=ApiResponse,
            status_code=status.HTTP_200_OK,
            summary="查询知识文件",
            description="根据ID查询知识文件详情",
            tags=["知识管理"]
        )(self.get_knowledge_file)

        self.router.get(
            "/knowledgeFiles",
            response_model=ApiResponse,
            status_code=status.HTTP_200_OK,
            summary="查询知识文件列表",
            description="分页查询知识文件列表",
            tags=["知识管理"]
        )(self.list_knowledge_files)

        return self.router
    async def create_knowledge_file(self, payload: KnowledgeFileCreate):
        """创建知识文件记录"""
        try:
            knowledge_file = knowledge_file_service.save_knowledge_file(
                payload.model_dump(exclude_unset=True)
            )
            return ApiResponse(
                status=200,
                message="Knowledge file created successfully",
                data=knowledge_file.to_dict()
            )
        except ValidationException:
            raise
        except Exception as e:
            logger.error(f"Error creating knowledge file: {str(e)}", exc_info=True)
            raise DatabaseException("Failed to create knowledge file") from e


    async def update_knowledge_file(
            self,
            file_id: str = Path(..., description="知识文件ID"),
            payload: KnowledgeFileUpdate = Body(..., description="知识文件更新信息")
    ):
        """更新知识文件记录"""
        try:
            if payload.id != file_id:
                raise ValidationException("Path ID does not match payload ID")

            update_data = payload.model_dump(exclude_unset=True, exclude={"id"})
            knowledge_file = knowledge_file_service.update_knowledge_file(
                file_id,
                update_data
            )
            if not knowledge_file:
                raise NotFoundException("Knowledge file not found")

            return ApiResponse(
                status=200,
                message="Knowledge file updated successfully",
                data=knowledge_file.to_dict()
            )
        except (ValidationException, NotFoundException):
            raise
        except Exception as e:
            logger.error(f"Error updating knowledge file: {str(e)}", exc_info=True)
            raise DatabaseException("Failed to update knowledge file") from e


    async def delete_knowledge_file(
            self,
            file_id: str = Path(..., description="知识文件ID")
    ):
        """删除知识文件记录"""
        try:
            deleted = knowledge_file_service.delete_knowledge_file(file_id)
            if not deleted:
                raise NotFoundException("Knowledge file not found")

            return ApiResponse(
                status=200,
                message="Knowledge file deleted successfully",
                data={"id": file_id}
            )
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error deleting knowledge file: {str(e)}", exc_info=True)
            raise DatabaseException("Failed to delete knowledge file") from e


    async def get_knowledge_file(
            self,
            file_id: str = Path(..., description="知识文件ID")
    ):
        """查询知识文件详情"""
        try:
            knowledge_file = knowledge_file_service.get_knowledge_file(file_id)
            if not knowledge_file:
                raise NotFoundException("Knowledge file not found")

            response_data = KnowledgeFileResponse.model_validate(
                knowledge_file
            ).model_dump()
            return ApiResponse(
                status=200,
                message="Knowledge file fetched successfully",
                data=response_data
            )
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error fetching knowledge file: {str(e)}", exc_info=True)
            raise DatabaseException("Failed to fetch knowledge file") from e


    async def list_knowledge_files(
            self,
            collection_name: str = Query(None, description="集合名称"),
            file_name: str = Query(None, description="文件名称"),
            file_type: str = Query(None, description="文件类型"),
            status_value: str = Query(None, alias="status", description="文件状态"),
            page: int = Query(1, ge=1, description="页码"),
            per_page: int = Query(20, ge=1, le=200, description="每页数量")
    ):
        """分页查询知识文件列表"""
        try:
            filters = {}
            if collection_name:
                filters["collection_name"] = collection_name
            if file_name:
                filters["file_name"] = file_name
            if file_type:
                filters["file_type"] = file_type
            if status_value:
                filters["status"] = status_value

            result = knowledge_file_service.list_knowledge_files(
                filter_param=filters,
                page=page,
                per_page=per_page
            )
            items = [item.to_dict() for item in result.get("items", [])]
            page_info = {
                "page": result.get("page", page),
                "per_page": result.get("per_page", per_page),
                "total": result.get("total", len(items)),
                "pages": result.get("pages", 0)
            }

            return ApiResponse(
                status=200,
                message="Knowledge files fetched successfully",
                data=items,
                page=page_info
            )
        except Exception as e:
            logger.error(f"Error listing knowledge files: {str(e)}", exc_info=True)
            raise DatabaseException("Failed to fetch knowledge files") from e