from typing import Any, Dict

from app.adapter.universal_client import DifyUniversalClient


class EchartsClient:
    """Echarts 专用客户端"""

    def __init__(self, api_key: str = None, base_url: str = None):
        self.client = DifyUniversalClient(api_key, base_url)
        self.logger = self.client.logger

        # 测试连接
        result = self.client.test_connection()
        if result["status"] == "success":
            self.logger.info(f"✅ 连接成功，应用类型: {result.get('app_type', '未知')}")
        else:
            self.logger.warning(f"⚠️  连接测试: {result.get('message')}")

    def run_workflow(self,
                     natural_language_query: str,
                     user_id: str = "sql-user-001",
                     **additional_inputs) -> Dict[str, Any]:
        """
        执行自然语言到 SQL 的查询

        Args:
            natural_language_query: 自然语言查询
            user_id: 用户标识
            **additional_inputs: 额外输入参数
        """
        self.logger.info(f"❓ 用户问题：{natural_language_query}")

        # 构建输入参数
        inputs = additional_inputs.copy()

        # 调用应用
        result = self.client.call_application(
            query=natural_language_query,
            inputs=inputs,
            user=user_id,
            response_mode="blocking",
            app_type="auto"  # 自动检测应用类型
        ) #dify的输出答案

        return self._process_result(result, natural_language_query) #返回答案

    def _process_result(self, result: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """处理返回结果"""
        if result["status"] == "success":
            data = result["data"] #data是一个字典

            # 提取关键信息
            answer = data.get("answer", "")
            conversation_id = data.get("conversation_id")
            message_id = data.get("message_id")

            self.logger.info("✅ 查询成功")
            self.logger.info(f"💡 AI回答: {answer}")

            return {
                "success": True,
                "original_query": original_query,
                "answer": answer,
                "result": result,
                "conversation_id": conversation_id,
                "message_id": message_id,
                "full_response": data,
                "auto_switched": result.get("auto_switched", False)
            }
        else:
            self.logger.error(f"❌ 查询失败: {result.get('message')}")
            return {
                "success": False,
                "original_query": original_query,
                "error": result.get("message"),
                "detail": result.get("detail")
            }

    def batch_query(self, queries: list, user_id: str = "batch-user-001") -> list:
        """批量查询"""
        results = []
        for i, query in enumerate(queries):
            self.logger.info(f"🔍 执行批量查询 {i + 1}/{len(queries)}: {query}")
            result = self.run_workflow(query, f"{user_id}-{i}")
            results.append(result)
        return results