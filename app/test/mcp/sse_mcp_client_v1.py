import json
import os
import logging
from typing import Dict, List, Any
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("sse-mcp-client")


class ToolConfig:
    """工具配置管理类"""

    def __init__(self, config_path: str = "config/tools_config.json"):
        self.config_path = Path(config_path)
        self.tools = []
        self.tool_mappings = {}
        self.load_config()

    def load_config(self) -> None:
        """加载工具配置"""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.tools = config.get("tools", [])
            self.tool_mappings = config.get("tool_mappings", {})

            logger.info(f"✅ 成功加载 {len(self.tools)} 个工具配置")

        except Exception as e:
            logger.error(f"❌ 加载配置文件失败: {e}")
            # 使用默认配置作为备选
            self._load_default_config()

    def _load_default_config(self) -> None:
        """加载默认配置（备选方案）"""
        self.tools = [
            {
                "name": "query_health_data",
                "description": "查询健康数据",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "用户ID"},
                        "metrics": {"type": "string", "description": "指标", "default": "all"}
                    },
                    "required": ["user_id"]
                }
            }
        ]
        self.tool_mappings = {
            "query_health_data": {
                "display_name": "查询健康数据",
                "input_prompts": {"user_id": "用户ID", "metrics": "指标 (默认all)"}
            }
        }
        logger.info("✅ 使用默认工具配置")

    def get_tool_config(self, tool_name: str) -> Dict[str, Any]:
        """获取指定工具的配置"""
        for tool in self.tools:
            if tool["name"] == tool_name:
                return tool
        return {}

    def get_tool_mapping(self, tool_name: str) -> Dict[str, Any]:
        """获取工具的显示映射配置"""
        return self.tool_mappings.get(tool_name, {})

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具列表"""
        return self.tools


class SSEMCPClient:
    """SSE MCP客户端（使用配置文件的版本）"""

    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.session_id = None
        self.tool_config = ToolConfig()

    def get_tool_display_info(self) -> Dict[str, str]:
        """获取工具显示信息"""
        display_info = {}
        for tool in self.tool_config.tools:
            tool_name = tool["name"]
            mapping = self.tool_config.get_tool_mapping(tool_name)
            display_name = mapping.get("display_name", tool_name)
            display_info[tool_name] = display_name
        return display_info

    def get_tool_input_prompts(self, tool_name: str) -> Dict[str, str]:
        """获取工具输入提示信息"""
        mapping = self.tool_config.get_tool_mapping(tool_name)
        return mapping.get("input_prompts", {})

    def get_tool_parameters(self, tool_name: str) -> Dict[str, Any]:
        """获取工具参数定义"""
        tool_config = self.tool_config.get_tool_config(tool_name)
        return tool_config.get("parameters", {})


def interactive_mode(client: SSEMCPClient):
    """交互模式（使用配置文件版本）"""

    # 获取工具显示信息
    tool_display_info = client.get_tool_display_info()

    # 构建菜单
    menu_options = {
        "1": "query_health_data",
        "2": "analyze_health_risk",
        "3": "nrs2002_assessment",
        "4": "view_session_info",
        "5": "exit"
    }

    while True:
        print("\n" + "=" * 50)
        print("SSE MCP客户端 - 交互模式（配置化版本）")

        # 动态生成菜单
        for key, tool_name in menu_options.items():
            if tool_name in ["view_session_info", "exit"]:
                continue
            display_name = tool_display_info.get(tool_name, tool_name)
            print(f"{key}. {display_name}")

        print("4. 查看会话信息")
        print("5. 退出")

        choice = input("请选择操作 (1-5): ").strip()

        if choice == "5":
            print("👋 再见！")
            break
        elif choice == "4":
            # 查看会话信息逻辑
            print("📋 会话信息功能")
            continue

        tool_name = menu_options.get(choice)
        if not tool_name or tool_name in ["view_session_info", "exit"]:
            print("❌ 无效选择")
            continue

        # 获取工具参数定义和输入提示
        parameters = client.get_tool_parameters(tool_name)
        input_prompts = client.get_tool_input_prompts(tool_name)

        if not parameters:
            print(f"❌ 未找到工具配置: {tool_name}")
            continue

        # 收集用户输入
        tool_args = {}
        required_params = parameters.get("required", [])
        properties = parameters.get("properties", {})

        print(f"🔧 正在执行: {tool_display_info.get(tool_name, tool_name)}...")

        for param_name, param_config in properties.items():
            prompt_text = input_prompts.get(param_name, param_name)
            default_value = param_config.get("default")

            if default_value:
                user_input = input(f"{prompt_text} (默认{default_value}): ").strip()
                tool_args[param_name] = user_input if user_input else default_value
            else:
                user_input = input(f"{prompt_text}: ").strip()
                if not user_input and param_name in required_params:
                    print(f"❌ 参数 {param_name} 是必填项")
                    break
                tool_args[param_name] = user_input

        else:  # 所有参数输入成功
            # 这里添加实际的工具调用逻辑
            print(f"📤 调用工具 {tool_name} 参数: {tool_args}")
            # 实际调用代码...

            # 模拟调用结果
            if tool_name == "analyze_health_risk":
                print("🎉 工具调用结果:")
                print("   工具: analyze_health_risk")
                print("   结果: 健康风险评估完成")

    print("✅ 交互模式结束")


def main():
    """主函数"""
    print("🚀 启动SSE MCP客户端 - 配置化版本")

    # 创建客户端实例
    client = SSEMCPClient("http://localhost:8000")

    try:
        # 进入交互模式
        interactive_mode(client)
    except KeyboardInterrupt:
        print("\n👋 用户中断程序")
    except Exception as e:
        logger.error(f"❌ 客户端运行错误: {e}")


if __name__ == "__main__":
    main()