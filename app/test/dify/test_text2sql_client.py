from typing import Any, Dict

from test_universal_client import DifyUniversalClient


class Text2SQLClient:
    """Text2SQL 专用客户端"""

    def __init__(self, api_key: str = None, base_url: str = None):
        self.client = DifyUniversalClient(api_key, base_url)
        self.logger = self.client.logger

        # 测试连接
        result = self.client.test_connection()
        if result["status"] == "success":
            self.logger.info(f"✅ 连接成功，应用类型: {result.get('app_type', '未知')}")
        else:
            self.logger.warning(f"⚠️  连接测试: {result.get('message')}")

    def query_database(self,
                       natural_language_query: str,
                       user_id: str = "sql-user-001",
                       **additional_inputs) -> Dict[str, Any]: #定义式定义的参数**表示收集为字典
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
        )

        return self._process_result(result, natural_language_query)

    def _process_result(self, result: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """处理返回结果"""
        if result["status"] == "success":
            data = result["data"]

            # 提取关键信息
            answer = data.get("answer", "")
            conversation_id = data.get("conversation_id")
            message_id = data.get("message_id")

            self.logger.info("✅ 查询成功")
            self.logger.info(f"💡 AI回答: {answer}")

            # 尝试提取 SQL 语句（如果存在）
            sql_query = self._extract_sql_from_answer(answer)

            return {
                "success": True,
                "original_query": original_query,
                "answer": answer,
                "sql_query": sql_query,
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

    def _extract_sql_from_answer(self, answer: str) -> str:
        """从回答中提取 SQL 语句"""
        # 简单的 SQL 提取逻辑（可以根据实际响应格式调整）
        import re

        # 查找 SQL 代码块
        sql_patterns = [
            r"```sql\n(.*?)\n```",  # Markdown SQL 代码块
            r"```\n(.*?)\n```",  # 普通代码块
            r"SELECT.*?;",  # 直接匹配 SELECT 语句
            r"```(.*?)```"  # 其他代码块格式
        ]

        for pattern in sql_patterns:
            match = re.search(pattern, answer, re.DOTALL | re.IGNORECASE) #换行也能匹配，大小写不敏感
            if match:
                return match.group(1).strip()

        # 如果没有找到代码块，尝试查找包含 SQL 关键字的段落
        sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER"]
        for keyword in sql_keywords:
            if keyword.lower() in answer.lower():
                # 提取包含关键字的句子
                sentences = answer.split('.')
                for sentence in sentences:
                    if keyword.lower() in sentence.lower():
                        return sentence.strip()

        return ""

    def batch_query(self, queries: list, user_id: str = "batch-user-001") -> list:
        """批量查询"""
        results = []
        for i, query in enumerate(queries):
            self.logger.info(f"🔍 执行批量查询 {i + 1}/{len(queries)}: {query}")
            result = self.query_database(query, f"{user_id}-{i}")
            results.append(result)
        return results