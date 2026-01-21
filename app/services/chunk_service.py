import logging
import os
import tempfile
from typing import Any, Dict, List, Optional

import requests
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredFileLoader,
)

from app.designer.strategy.chunk.jieba_chunking_strategy import JiebaChunkingStrategy
from app.designer.strategy.chunk.minio_metadata_strategy import MinIOMetadataStrategy
from app.exceptions.rag_exception import RAGException

logger = logging.getLogger(__name__)


class ChunkService:
    """文档分片服务：下载MinIO文件并生成带元数据的分片。"""

    def __init__(
        self,
        chunking_strategy: Optional[JiebaChunkingStrategy] = None,
        metadata_strategy: Optional[MinIOMetadataStrategy] = None,
    ):
        self.chunking_strategy = chunking_strategy or JiebaChunkingStrategy(
            chunk_size=800, chunk_overlap=100
        )
        self.metadata_strategy = metadata_strategy or MinIOMetadataStrategy()

    def process_minio_document(self, minio_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """下载MinIO文件并分片，返回分片结果。"""
        file_id = minio_metadata.get("file_id")
        file_name = minio_metadata.get("file_name")
        minio_path = minio_metadata.get("minio_path")

        if not file_id or not file_name or not minio_path:
            raise RAGException(400, "file_id、file_name、minio_path 均为必填字段")

        response = self._download_file(minio_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        if not file_ext:
            raise RAGException(400, f"无法识别文件类型：{file_name}")

        temp_path = self._write_temp_file(response.content, file_ext)
        try:
            docs = self._load_documents(temp_path, file_ext)
            if not docs:
                raise RAGException(500, f"解析失败：{file_name}")

            chunks = self.chunking_strategy.split_document(docs, temp_path)
            processed_chunks = self.metadata_strategy.process_metadata(
                chunks, minio_metadata
            )

            return {
                "file_id": file_id,
                "file_name": file_name,
                "chunk_count": len(processed_chunks),
                "chunks": [
                    {
                        "page_content": chunk.page_content,
                        "metadata": chunk.metadata,
                    }
                    for chunk in processed_chunks
                ],
            }
        finally:
            self._cleanup_temp_file(temp_path)

    def _download_file(self, url: str) -> requests.Response:
        try:
            response = requests.get(url, timeout=30)
        except requests.RequestException as exc:
            raise RAGException(500, f"下载文件失败：{exc}") from exc

        if response.status_code != 200:
            raise RAGException(
                response.status_code, f"下载文件失败：HTTP {response.status_code}"
            )
        return response

    def _write_temp_file(self, content: bytes, suffix: str) -> str:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        try:
            temp_file.write(content)
            temp_file.flush()
            return temp_file.name
        finally:
            temp_file.close()

    def _load_documents(self, file_path: str, file_ext: str) -> List[Document]:
        if file_ext in {".txt", ".md", ".json", ".csv", ".sql"}:
            return TextLoader(file_path, encoding="utf-8").load()
        if file_ext == ".pdf":
            return PyPDFLoader(file_path).load()
        if file_ext in {".doc", ".docx"}:
            return Docx2txtLoader(file_path).load()
        return UnstructuredFileLoader(file_path).load()

    def _cleanup_temp_file(self, file_path: str) -> None:
        try:
            os.remove(file_path)
        except OSError:
            logger.warning("清理临时文件失败：%s", file_path)
