# dify_workflow.py
import json
import os
import sys
from dotenv import load_dotenv

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) #app

from test_text2sql_client import Text2SQLClient


def main():
    """修复的工作流测试"""
    load_dotenv()

    print("=== Text2SQL 工作流测试（修复版）===")

    # 检查环境变量
    api_key = os.getenv("DIFY_API_KEY")
    base_url = os.getenv("DIFY_BASE_URL")

    if not api_key:
        print("❌ 请设置 DIFY_API_KEY 环境变量")
        return

    print(f"API 密钥: {api_key[:10]}...")
    print(f"基础 URL: {base_url}")

    try:
        # 初始化客户端
        client = Text2SQLClient(api_key=api_key, base_url=base_url)

        # 测试查询示例
        test_queries = [
            "统计各风险等级人数",
            "查询高风险患者信息"
        ]

        print(f"\n🧪 执行 {len(test_queries)} 个测试查询...")

        for i, query in enumerate(test_queries, 1):
            print(f"\n--- 测试 {i}: {query} ---")

            result = client.query_database(query, f"test-user-{i}")

            if result["success"]:
                print("✅ 查询成功")
                print(f"💡 回答: {result['answer']}")

                if result.get("sql_query"):
                    print(f"📊 提取的SQL: {result['sql_query']}")

                if result.get("auto_switched"):
                    print("🔄 注意: 自动从工作流切换到聊天模式")

            else:
                print(f"❌ 查询失败: {result.get('error')}")
                if result.get("detail"):
                    print(f"详细信息: {result.get('detail')}")

        print(f"\n=== 测试完成 ===")

    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


def test_specific_workflow():
    """测试特定工作流（如果需要）"""
    load_dotenv()

    from test_universal_client import DifyUniversalClient

    client = DifyUniversalClient()

    # 如果您确实有工作流ID，可以这样调用
    workflow_id = "workflow-49b871f9-236a-4c7f-bec1-c552b45480f2"

    result = client.call_application(
        query="统计各风险等级人数",
        inputs={"query": "统计各风险等级人数"},
        user="teacher li",
        app_type="workflow"  # 强制使用工作流模式
    )

    print("工作流调用结果:", json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

    # 如果需要测试特定工作流，取消注释下行
    test_specific_workflow()