# http_client.py
import json

import aiohttp
import asyncio
from typing import Dict, Any


class HTTPMCPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None

    async def connect(self):
        self.session = aiohttp.ClientSession()

    async def call_tool(self, tool_name: str, arguments: Dict) -> Dict:
        async with self.session.post(f"{self.base_url}/mcp", json={
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments}
        }) as response:
            return await response.json()
    async def call_tool2(self, tool_name: str, arguments: Dict) -> Dict:
        async with self.session.post(f"{self.base_url}/api/v1/rag/systemRagQuery", json={
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments}
        }) as response:
            return await response.json()
    def call_service(self,url:str):
        self.base_url = url

    async def call_tool_common(self,url:str,params: Dict) -> Dict:
        async with self.session.post(f"{self.base_url}/{url}",json=params) as response:
            return await response.json()

    async def list_tools(self) -> Dict:
        async with self.session.post(f"{self.base_url}/mcp", json={
            "method": "tools/list",
            "params": {}
        }) as response:
            return await response.json()

    async def close(self):
        if self.session:
            await self.session.close()

# 使用示例
async def main():
    client = HTTPMCPClient("http://127.0.0.1:8019")
    await client.connect()

    try:
        # 列出可用工具
        tools = await client.list_tools()
        print("可用工具:", tools)

        # 调用工具
        result = await client.call_tool("analyze_health_risk", {
            "age": 65,
            "bmi": 19.2,
            "conditions": ["diabetes"]
        })
        # kwargs = [
        #     {'url':'api/v1/rag/systemRagQuery',
        #      'params' : {
        #     "file_id": "f63226e8-b892-4410-9886-527e51ff9a7d",
        #     "question": "胃癌术后化疗患者，68岁，BMI 18.4，近1个月体重下降8%，进食量减少60%，无其他严重疾病",
        #     "collection_name": "nrs2002_collection_v2"}
        #     }
        # ]
        # result = []
        # for _ in kwargs:
        #     url = _["url"]
        #     params = _["params"]
        #     result.append(await client.call_tool_common(url,params))
        print("分析结果:", result)

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())