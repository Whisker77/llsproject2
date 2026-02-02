import json
import os
import sys
from dotenv import load_dotenv

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
#D:\1120\pycharmproject\aiagent

from app.adapter.bi_client import EchartsClient
import logging

logger = logging.getLogger("workflow_client")

def execute_workflow(params: str):
    """修复的工作流测试"""
    load_dotenv()

    logger.info("=== Text2Echarts 工作流测试（修复版）===")

    # 检查环境变量
    api_key = os.getenv("DIFY_API_KEY_TEXT2ECHARTS")
    # api_key = "app-IJVbQMi7UZvewmGNVDGBftWP"
    base_url = os.getenv("DIFY_BASE_URL")

    if not api_key:
        logger.info("❌ 请设置 DIFY_API_KEY 环境变量")
        return

    logger.info(f"API 密钥: {api_key[:10]}...")
    logger.info(f"基础 URL: {base_url}")

    try:
        # 初始化客户端
        client = EchartsClient(api_key=api_key, base_url=base_url)
        result = client.run_workflow(params, f"test-user")
        if result["success"]:
            logger.info("✅ 查询成功")
            logger.info(f"💡 回答: {result['answer']}")

            if result.get("result"):
                logger.info(f"📊 提取结果: {result['result']}")
                return result['result']['data']

            if result.get("auto_switched"):
                logger.info("🔄 注意: 自动从工作流切换到聊天模式")

        else:
            logger.info(f"❌ 查询失败: {result.get('error')}")
            if result.get("detail"):
                logger.info(f"详细信息: {result.get('detail')}")



        logger.info(f"\n=== 测试完成 ===")

    except Exception as e:
        logger.info(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

