# websocket_client_fixed_protocol.py
import asyncio
import websockets
import json
import logging
from typing import Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("websocket-client")


class MCPWebSocketClient:
    def __init__(self, uri="ws://localhost:8765"):
        self.uri = uri
        self.websocket = None
        self.request_id = 0

    async def connect(self):
        """连接到服务器"""
        try:
            self.websocket = await websockets.connect(self.uri)
            logger.info(f"✅ 已连接到服务器: {self.uri}")

            # 发送初始化请求（MCP协议要求）
            await self._initialize()
            return True

        except Exception as e:
            logger.error(f"❌ 连接失败: {e}")
            return False

    async def _initialize(self):
        """发送MCP初始化请求"""
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "tools": {"listChanged": True}
                },
                "clientInfo": {
                    "name": "Health-MCP-Client",
                    "version": "1.0.0"
                }
            },
            "id": self._next_id()
        }

        response = await self._send_request(init_request)
        if response and "result" in response:
            logger.info("✅ 初始化成功")
        else:
            logger.error("❌ 初始化失败")

    async def list_tools(self):
        """列出可用工具（MCP协议）"""
        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": self._next_id()
        }
        return await self._send_request(request)

    async def query_health_data(self, user_id: str, metric: str = "all"):
        """查询健康数据（MCP协议）"""
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "query_health_data",
                "arguments": {
                    "user_id": user_id,
                    "metric": metric
                }
            },
            "id": self._next_id()
        }
        return await self._send_request(request)

    async def analyze_health_risk(self, age: int, bmi: float, conditions: list = None):
        """分析健康风险（MCP协议）"""
        if conditions is None:
            conditions = []

        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "analyze_health_risk",
                "arguments": {
                    "age": age,
                    "bmi": bmi,
                    "conditions": conditions
                }
            },
            "id": self._next_id()
        }
        return await self._send_request(request)

    async def _send_request(self, request: Dict) -> Dict:
        """发送请求并等待响应"""
        if not self.websocket:
            raise Exception("未连接到服务器")

        try:
            # 发送请求
            await self.websocket.send(json.dumps(request))
            logger.debug(f"发送请求: {request['method']}")

            # 等待响应（设置超时）
            response = await asyncio.wait_for(self.websocket.recv(), timeout=30.0)
            response_data = json.loads(response)

            # 检查是否是通知消息（没有id的消息）
            if "id" not in response_data:
                logger.info(f"收到通知: {response_data.get('method', 'unknown')}")
                # 继续等待实际响应
                response = await asyncio.wait_for(self.websocket.recv(), timeout=30.0)
                response_data = json.loads(response)

            return response_data

        except asyncio.TimeoutError:
            raise Exception("请求超时")
        except Exception as e:
            raise Exception(f"请求失败: {str(e)}")

    def _next_id(self) -> int:
        """生成下一个请求ID"""
        self.request_id += 1
        return self.request_id

    async def close(self):
        """关闭连接"""
        if self.websocket:
            await self.websocket.close()
            logger.info("连接已关闭")


async def interactive_mode():
    """交互式模式（使用MCP协议）"""
    client = MCPWebSocketClient()

    if not await client.connect():
        return

    try:
        while True:
            print("\n" + "=" * 50)
            print("MCP协议客户端 - 交互模式")
            print("1. 列出可用工具")
            print("2. 查询健康数据")
            print("3. 分析健康风险")
            print("4. 退出")

            choice = input("请选择操作 (1-4): ").strip()

            if choice == "1":
                print("🛠️  获取工具列表...")
                response = await client.list_tools()

                if "result" in response:
                    tools = response["result"].get("tools", [])
                    print("可用工具:")
                    for tool in tools:
                        print(f"  - {tool['name']}: {tool['description']}")
                        if "parameters" in tool:
                            params = tool["parameters"].get("properties", {})
                            print(f"    参数: {', '.join(params.keys())}")
                else:
                    print("❌ 获取工具列表失败:", response.get("error", "未知错误"))

            elif choice == "2":
                user_id = input("用户ID: ").strip() or "test_user"
                metric = input("指标 (默认all): ").strip() or "all"

                print(f"🔍 查询健康数据 - 用户: {user_id}, 指标: {metric}")
                response = await client.query_health_data(user_id, metric)

                if "result" in response:
                    content = response["result"].get("content", [])
                    if content and content[0].get("type") == "text":
                        try:
                            data = json.loads(content[0]["text"])
                            print("✅ 健康数据结果:")
                            print(json.dumps(data, indent=2, ensure_ascii=False))
                        except:
                            print("📄 响应内容:", content[0]["text"])
                else:
                    print("❌ 查询失败:", response.get("error", "未知错误"))

            elif choice == "3":
                try:
                    age = int(input("年龄: ").strip())
                    bmi = float(input("BMI: ").strip())
                    conditions_input = input("健康状况 (逗号分隔): ").strip()
                    conditions = [c.strip() for c in conditions_input.split(",")] if conditions_input else []

                    print(f"📊 分析健康风险 - 年龄: {age}, BMI: {bmi}, 状况: {conditions}")
                    response = await client.analyze_health_risk(age, bmi, conditions)

                    if "result" in response:
                        content = response["result"].get("content", [])
                        if content and content[0].get("type") == "text":
                            try:
                                data = json.loads(content[0]["text"])
                                print("✅ 风险分析结果:")
                                print(json.dumps(data, indent=2, ensure_ascii=False))
                            except:
                                print("📄 响应内容:", content[0]["text"])
                    else:
                        print("❌ 分析失败:", response.get("error", "未知错误"))

                except ValueError:
                    print("❌ 输入格式错误，请确保年龄和BMI是数字")

            elif choice == "4":
                break
            else:
                print("❌ 无效选择")

    except KeyboardInterrupt:
        print("\n退出交互模式")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
    finally:
        await client.close()


async def demo_mode():
    """演示模式"""
    client = MCPWebSocketClient()

    if not await client.connect():
        return

    try:
        print("🚀 开始MCP协议演示")

        # 1. 列出工具
        print("\n1. 获取工具列表...")
        tools_response = await client.list_tools()
        if "result" in tools_response:
            tools = tools_response["result"].get("tools", [])
            print("✅ 可用工具:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
        else:
            print("❌ 获取工具列表失败")
            return

        # 2. 查询健康数据
        print("\n2. 查询健康数据...")
        health_response = await client.query_health_data("demo_user", "bmi")
        if "result" in health_response:
            content = health_response["result"].get("content", [])
            if content:
                print("✅ 健康数据查询成功")
                try:
                    data = json.loads(content[0]["text"])
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                except:
                    print("响应:", content[0]["text"])
        else:
            print("❌ 健康数据查询失败")

        # 3. 分析健康风险
        print("\n3. 分析健康风险...")
        risk_response = await client.analyze_health_risk(65, 19.2, ["diabetes"])
        if "result" in risk_response:
            content = risk_response["result"].get("content", [])
            if content:
                print("✅ 风险分析成功")
                try:
                    data = json.loads(content[0]["text"])
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                except:
                    print("响应:", content[0]["text"])
        else:
            print("❌ 风险分析失败")

        print("\n🎉 演示完成")

    except Exception as e:
        print(f"❌ 演示过程中发生错误: {str(e)}")
    finally:
        await client.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "demo": #python main.py demo
        asyncio.run(demo_mode())
    else:
        print("🚀 启动MCP协议客户端 - 交互模式")
        asyncio.run(interactive_mode())