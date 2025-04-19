"""
File   : mcp_sse_server_math.py
Desc   : 数学运算工具（SSE, Tools, FastMCP）
Date   : 2025/04/19
Author : Tianyu Chen
"""

import numpy as np
from mcp.server.fastmcp import FastMCP
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
import uvicorn


# 初始化 FastMCP server
mcp = FastMCP("math_tools")


@mcp.tool()
def power(base: float, exponent: float) -> float:
    """指数运算：计算 base 的 exponent 次方

    Args:
        base: 底数
        exponent: 次数
    """
    result = base ** exponent
    return {
        "result": result
    }


@mcp.tool()
def logarithm(base: float, value: float) -> float:
    """对数运算：计算以 base 为底的 value 的对数

    Args:
        base: 底数
        value: 值
    """
    if base <= 0 or base == 1 or value <= 0:
        raise ValueError("Base must be greater than 0 and not equal to 1, and value must be greater than 0.")
    result = np.log(value) / np.log(base)
    return {
        "result": result
    }


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can serve the provided mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )



if __name__ == "__main__":
    mcp_server = mcp._mcp_server

    import argparse

    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to listen on')
    args = parser.parse_args()

    # Bind SSE request handling to MCP server
    starlette_app = create_starlette_app(mcp_server, debug=True)
    uvicorn.run(starlette_app, host=args.host, port=args.port)
