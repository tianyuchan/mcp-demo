"""
File   : sse_client.py
Desc   : SSE MCP 客户端
Date   : 2025/04/19
Author : Tianyu Chen
"""


import os
import sys
import asyncio
import json
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.sse import sse_client
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # 从 .env 加载环境变量


class MCPClient:
    """MCP 客户端类，用于连接到 MCP 服务器并处理查询"""
    def __init__(self):
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY 环境变量未设置")
        self.openai = OpenAI()
        self.messages = [
            {
                "role": "system",
                "content": "You are a versatile assistant capable of answering questions, completing tasks, and intelligently invoking specialized tools to deliver optimal results."
            }
        ]
        # mcp 相关成员变量
        self.exit_stack = AsyncExitStack()
        self.available_tools = []
        self.read = None
        self.write = None
        self.session = None

    async def connect_to_server(self, server_url):
        """连接到 MCP 服务器

        Args:
            server_url: MCP 服务器 URL
        """
    
        # 连接 MCP 服务器，创建通信通道
        sse_transport = await self.exit_stack.enter_async_context(sse_client(url=server_url))
        self.read, self.write = sse_transport
        # 创建 MCP 客户端会话
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.read, self.write))
        await self.session.initialize()
        # 列出可用的工具
        response = await self.session.list_tools()
        tools = response.tools
        print("\n已连接到服务器，工具包括：", [tool.name for tool in tools])

        self.available_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": tool.inputSchema['properties'],
                        "required": tool.inputSchema['required']
                    }
                }
            } for tool in tools
        ]


    async def tool_calls(self, response, messages):
        """工具调用"""
        current_response = response
        while current_response.choices[0].message.tool_calls:
            if current_response.choices[0].message.content:
                print("\n🤖 AI: tool_calls", current_response.choices[0].message)
            for tool_call in current_response.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                raw_args = tool_call.function.arguments
                tool_args = {}
                try:
                    tool_args = json.loads(raw_args)
                except json.JSONDecodeError:
                    print('⚠️ 参数解析失败，使用空对象替代')
                print(f"\n🔧 调用工具 {tool_name}")
                print(f"📝 参数: {tool_args}")
                result = await self.session.call_tool(name=tool_name, arguments=tool_args)
                print(f"💡 结果: {result.content[0].text}")
                messages.append(current_response.choices[0].message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result.content[0].text
                })
            current_response = self.openai.chat.completions.create(
                model=os.getenv("OPENAI_MODEL"),
                messages=messages,
                tools=self.available_tools
            )
        return current_response


    async def process_query(self, query):
        """使用 OpenAI API 和可用的工具处理查询"""
        self.messages.append({"role": "user", "content": query})
        response = self.openai.chat.completions.create(
            model=os.getenv("OPENAI_MODEL"),
            messages=self.messages,
            tools=self.available_tools
        )
        if response.choices[0].message.content:
            print("\n🤖 AI:", response.choices[0].message)
        if response.choices[0].message.tool_calls:
            response = await self.tool_calls(response, self.messages)
        self.messages.append(response.choices[0].message)
        return response.choices[0].message.content or ""


    async def chat_loop(self):
        """运行交互式聊天循环"""
        print("\nMCP 客户端已启动！")
        print("输入你的查询或输入 'quit' 退出。")

        while True:
            try:
                query = input("\n查询: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n回答: " + response)

            except Exception as e:
                print(f"\n错误: {str(e)}")


    async def cleanup(self):
        """清理资源"""
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_server_script>")
        return
    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
