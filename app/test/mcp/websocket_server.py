# websocket_server_fixed.py
import asyncio
import json
import websockets
from typing import Dict, Any, Set
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("websocket-mcp-server")


class WebSocketMCPServer:
    def __init__(self):
        self.connected_clients: Set[websockets.WebSocketServerProtocol] = set() #所有已连接但尚未断开的客户端连接对象集合
        self.tools = {
            "query_health_data": {
                "name": "query_health_data",
                "description": "查询健康数据",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "metric": {"type": "string"}
                    },
                    "required": ["user_id"]
                }
            },
            "analyze_health_risk": {
                "name": "analyze_health_risk",
                "description": "分析健康风险",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "age": {"type": "number"},
                        "bmi": {"type": "number"},
                        "conditions": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["age", "bmi"]
                }
            }
        }

    async def handle_client(self, websocket):
        """处理WebSocket客户端连接（新版websockets兼容版本）"""
        self.connected_clients.add(websocket)
        client_ip = websocket.remote_address[0] if websocket.remote_address else "unknown"
        logger.info(f"客户端连接: {client_ip}")

        try:
            async for message in websocket:
                try:
                    request = json.loads(message)
                    logger.info(f"收到请求: {request}")

                    # 处理请求
                    response = await self.handle_request(request)

                    # 发送响应
                    await websocket.send(json.dumps(response))
                    logger.info("响应已发送")

                except json.JSONDecodeError as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32700,
                            "message": f"JSON解析错误: {str(e)}"
                        },
                        "id": None
                    }
                    await websocket.send(json.dumps(error_response))
                except Exception as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": f"内部错误: {str(e)}"
                        },
                        "id": None
                    }
                    await websocket.send(json.dumps(error_response))

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"客户端断开连接: {client_ip}")
        except Exception as e:
            logger.error(f"处理客户端时发生错误: {str(e)}")
        finally:
            self.connected_clients.remove(websocket)
            logger.info(f"客户端清理完成: {client_ip}")

    async def handle_request(self, request: Dict) -> Dict:
        """处理MCP请求"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        if method == "initialize":
            return await self.handle_initialize(request_id)
        elif method == "tools/list":
            return await self.list_tools(request_id)
        elif method == "tools/call":
            return await self.call_tool(params, request_id)
        elif method == "notifications/cancel":
            return {"jsonrpc": "2.0", "result": None, "id": request_id}
        else:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"方法未找到: {method}"
                },
                "id": request_id
            }

    async def handle_initialize(self, request_id: Any) -> Dict:
        """处理初始化请求"""
        return {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "tools": {"listChanged": True}
                },
                "serverInfo": {
                    "name": "Health-RAG-MCP-Server",
                    "version": "1.0.0"
                }
            },
            "id": request_id
        }

    async def list_tools(self, request_id: Any) -> Dict:
        """列出可用工具"""
        return {
            "jsonrpc": "2.0",
            "result": {
                "tools": list(self.tools.values())
            },
            "id": request_id
        }

    async def call_tool(self, params: Dict, request_id: Any) -> Dict:
        """调用工具"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "query_health_data":
            return await self.handle_health_query(arguments, request_id)  #返回答案
        elif tool_name == "analyze_health_risk":
            return await self.handle_risk_analysis(arguments, request_id)
        else:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"工具未找到: {tool_name}"
                },
                "id": request_id
            }

    async def handle_health_query(self, arguments: Dict, request_id: Any) -> Dict:
        """处理健康数据查询"""
        try:
            user_id = arguments.get("user_id")
            metric = arguments.get("metric", "all")

            # 模拟健康数据查询
            health_data = {
                "user_id": user_id,
                "metrics": {
                    "bmi": 19.2,
                    "blood_pressure": "120/80",
                    "heart_rate": 72,
                    "weight": 62.5
                },
                "last_update": "2024-01-15T14:20:00Z"
            }

            if metric != "all":
                health_data["metrics"] = {metric: health_data["metrics"].get(metric, "N/A")}

            return {
                "jsonrpc": "2.0",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(health_data, indent=2, ensure_ascii=False)
                        }
                    ]
                },
                "id": request_id
            }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"健康查询失败: {str(e)}"
                },
                "id": request_id
            }

    async def handle_risk_analysis(self, arguments: Dict, request_id: Any) -> Dict:
        """处理健康风险分析"""
        try:
            age = arguments.get("age", 0)
            bmi = arguments.get("bmi", 0)
            conditions = arguments.get("conditions", [])

            # 简单的风险分析逻辑
            risk_score = (age * 0.1) + ((bmi - 18.5) * 0.5 if bmi < 18.5 else 0)

            if "diabetes" in conditions:
                risk_score += 0.3
            if "hypertension" in conditions:
                risk_score += 0.2

            risk_level = "低风险" if risk_score < 0.5 else "中风险" if risk_score < 1.0 else "高风险"

            analysis_result = {
                "risk_score": round(risk_score, 2),
                "risk_level": risk_level,
                "factors": {
                    "age_contribution": round(age * 0.1, 2),
                    "bmi_contribution": round((bmi - 18.5) * 0.5 if bmi < 18.5 else 0, 2),
                    "conditions_contribution": len(conditions) * 0.1
                },
                "recommendations": [
                    "定期监测健康指标",
                    "保持均衡饮食",
                    "适当运动"
                ]
            }

            return {
                "jsonrpc": "2.0",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(analysis_result, indent=2, ensure_ascii=False) #每层嵌套用两个空格缩进
                        }
                    ]
                },
                "id": request_id
            }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"风险分析失败: {str(e)}"
                },
                "id": request_id
            }

    async def broadcast_to_clients(self, message: Dict):
        """向所有客户端广播消息"""
        if self.connected_clients:
            await asyncio.gather(*[
                client.send(json.dumps(message))
                for client in self.connected_clients
            ], return_exceptions=True) #*的作用是每个客户端同时发


async def health_check_broadcast(server: WebSocketMCPServer):
    """定期健康检查广播"""
    while True:
        await asyncio.sleep(30)  # 每30秒广播一次
        health_status = {
            "jsonrpc": "2.0",
            "method": "notifications/serverStatus",
            "params": {
                "status": "healthy",
                "connected_clients": len(server.connected_clients)
            }
        }
        await server.broadcast_to_clients(health_status)


async def main():
    """主函数"""
    server = WebSocketMCPServer()

    # 创建处理函数包装器（兼容新旧版本websockets）
    async def handler(websocket, path=None):
        """兼容性包装器"""
        # 新版本websockets只传递websocket参数，旧版本传递websocket和path
        await server.handle_client(websocket)

    # 启动WebSocket服务器
    start_server = await websockets.serve(
        handler,  # 使用包装器函数 websocket本身自动传给handler
        "localhost",
        8765
    )

    logger.info("🚀 WebSocket MCP服务器运行在 ws://localhost:8765")
    logger.info("📡 等待客户端连接...")

    # 启动健康检查广播任务
    broadcast_task = asyncio.create_task(health_check_broadcast(server))

    try:
        # 保持服务器运行
        await asyncio.Future()  # main程序不终止，协程永久运行
    except KeyboardInterrupt:
        logger.info("接收到中断信号，正在关闭服务器...")
    finally:
        # 清理资源
        broadcast_task.cancel()
        start_server.close() #下达关闭任务
        await start_server.wait_closed() #确认关闭
        logger.info("服务器已关闭")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 服务器已关闭")
    except Exception as e:
        logger.error(f"服务器运行错误: {e}")